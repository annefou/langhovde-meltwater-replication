"""GNSS track processing: smoothing, horizontal speed and vertical displacement.

A generic reimplementation of the processing in the authors' `fig3/fig3.m`. It
includes the two functions missing from the Mendeley deposit (doi:10.17632/8wvtxg53ry.1):

- `local_regression`: Gaussian-kernel (σ = h) local linear regression.
- `latlon2utm`: WGS84 to UTM zone 37S.

Nothing here reads the authors' figures. The reconstruction was identified once
against the deposited `fig3.eps` (`scripts/validate_reconstruction.py`) and is
guarded by a regression test (`tests/test_gnss.py`). The analysis itself runs from
the raw positions only.

Differences from `fig3.m`, all of which reproduce its output:
- Data gaps come from the timestamps (`max_gap_h`), not hard-coded row numbers.
  Any threshold between 8.3 h and 29.1 h gives the authors' segments.
- Differencing is a parameter. The authors used forward differences at GNSS2 and
  centred differences at GNSS1; `AUTHORS_FIG3` records that.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import xarray as xr
from pyproj import Transformer

_TO_UTM37S = Transformer.from_crs("EPSG:4326", "EPSG:32737", always_xy=True)
_DAY = np.timedelta64(1, "D")


@dataclass(frozen=True)
class GnssSettings:
    bandwidth_h: float = 12.0          # Gaussian σ of the local linear regression
    max_gap_h: float = 12.0            # sampling gaps longer than this split the track
    step_h: float = 1.0                # output grid spacing, from each segment's first sample
    scheme: Literal["centred", "forward"] = "centred"

    def __post_init__(self) -> None:
        if min(self.bandwidth_h, self.max_gap_h, self.step_h) <= 0:
            raise ValueError("bandwidth_h, max_gap_h and step_h must be positive")
        if self.scheme not in ("centred", "forward"):
            raise ValueError(f"unknown scheme {self.scheme!r}")


# The authors' processing for the published Fig. 3 (validated against fig3.eps).
AUTHORS_FIG3 = {
    "GNSS1": GnssSettings(bandwidth_h=12.0, scheme="centred"),
    "GNSS2": GnssSettings(bandwidth_h=12.0, scheme="forward"),
}


def latlon2utm(lat: np.ndarray, lon: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """WGS84 lat/lon (degrees) to UTM zone 37S easting, northing (m)."""
    return _TO_UTM37S.transform(np.asarray(lon, dtype=float), np.asarray(lat, dtype=float))


def local_regression(t: np.ndarray, x: np.ndarray, ti: np.ndarray, h: float) -> np.ndarray:
    """Gaussian-kernel (σ = h) local linear regression of x(t), evaluated at ti.

    t, ti and h must share units. All finite samples contribute, including samples
    across data gaps (callers keep ti inside segments, as fig3.m does).
    """
    t, x, ti = (np.asarray(a, dtype=float) for a in (t, x, ti))
    if t.shape != x.shape:
        raise ValueError("t and x must have the same shape")
    if h <= 0:
        raise ValueError("h must be positive")
    ok = np.isfinite(t) & np.isfinite(x)
    t, x = t[ok], x[ok]
    if t.size < 2:
        raise ValueError("need at least two finite samples")
    out = np.empty(ti.size)
    for k, t0 in enumerate(ti):
        d = t - t0
        w = np.exp(-0.5 * (d / h) ** 2)
        sw, swd, swdd = w.sum(), (w * d).sum(), (w * d * d).sum()
        det = sw * swdd - swd ** 2
        # Weighted least-squares intercept of x = a + b·d at d = 0; NaN where the
        # kernel holds too little data to fit a line (far outside the samples).
        out[k] = (swdd * (w * x).sum() - swd * (w * d * x).sum()) / det if det > 1e-300 else np.nan
    return out


def find_segments(time: np.ndarray, max_gap_h: float) -> list[slice]:
    """Index slices of runs of samples with no sampling gap longer than max_gap_h."""
    time = np.asarray(time, dtype="datetime64[ns]")
    if time.size == 0:
        return []
    dt_h = np.diff(time) / np.timedelta64(1, "h")
    if np.any(dt_h <= 0):
        raise ValueError("time must be strictly increasing")
    breaks = np.flatnonzero(dt_h > max_gap_h) + 1
    edges = np.concatenate([[0], breaks, [time.size]])
    return [slice(a, b) for a, b in zip(edges[:-1], edges[1:])]


def _difference(ti: np.ndarray, v: np.ndarray, scheme: str) -> np.ndarray:
    rate = np.full(v.size, np.nan)
    if v.size < 2:
        return rate
    if scheme == "centred":
        rate[1:-1] = (v[2:] - v[:-2]) / (ti[2:] - ti[:-2])
    else:
        rate[:-1] = np.diff(v) / np.diff(ti)
    return rate


def process_track(time: np.ndarray, lat: np.ndarray, lon: np.ndarray, height: np.ndarray,
                  settings: GnssSettings = GnssSettings(), station: str = "") -> xr.Dataset:
    """Smoothed displacement, horizontal speed (m/d) and vertical displacement (m).

    Displacements are relative to the first sample. The output grid restarts at the
    first sample of each segment, with no values inside gaps. `speed` at a grid time
    uses that time's centred or forward difference (`settings.scheme`).
    """
    time = np.asarray(time, dtype="datetime64[ns]")
    lat, lon, height = (np.asarray(a, dtype=float) for a in (lat, lon, height))
    if not (time.shape == lat.shape == lon.shape == height.shape):
        raise ValueError("time, lat, lon and height must have the same shape")
    x, y = latlon2utm(lat, lon)
    dx, dy, dz = x - x[0], y - y[0], height - height[0]
    t0 = time[0]
    t = (time - t0) / _DAY
    h, step = settings.bandwidth_h / 24, settings.step_h / 24

    parts = []
    for seg_id, sl in enumerate(find_segments(time, settings.max_gap_h)):
        ti = np.arange(t[sl][0], t[sl][-1] + 1e-9, step)
        xs, ys, zs = (local_regression(t, v, ti, h) for v in (dx, dy, dz))
        u, v = _difference(ti, xs, settings.scheme), _difference(ti, ys, settings.scheme)
        parts.append(xr.Dataset(
            {"x": ("time", xs), "y": ("time", ys), "uplift": ("time", zs),
             "speed": ("time", np.hypot(u, v)),
             "segment": ("time", np.full(ti.size, seg_id))},
            coords={"time": t0 + np.round(ti * 86400e9).astype("timedelta64[ns]")},
        ))
    ds = xr.concat(parts, dim="time")
    ds["x"].attrs = {"units": "m", "long_name": "smoothed easting displacement (UTM 37S)"}
    ds["y"].attrs = {"units": "m", "long_name": "smoothed northing displacement (UTM 37S)"}
    ds["uplift"].attrs = {"units": "m", "long_name": "smoothed vertical displacement"}
    ds["speed"].attrs = {"units": "m d-1", "long_name": "horizontal speed"}
    ds.attrs = {"station": station, "bandwidth_h": settings.bandwidth_h, "max_gap_h": settings.max_gap_h,
                "step_h": settings.step_h, "difference_scheme": settings.scheme,
                "smoother": "Gaussian-kernel local linear regression (sigma = bandwidth_h)"}
    return ds


def fill_gaps_spline(track: xr.Dataset, scheme: Literal["centred", "forward"] = "centred") -> xr.Dataset:
    """Continuous track through data gaps, as in `fig_s6.m` (SI Fig. 6, dashed lines in Fig. 3).

    A not-a-knot cubic spline (MATLAB `spline`) is fitted through the smoothed hourly x,
    y and uplift of all segments. It is evaluated on one regular grid from the first to
    the last output time and then differenced. `observed` is False at grid times
    inside a gap, i.e. outside every segment's span.
    """
    from scipy.interpolate import CubicSpline

    t0 = track.time.values[0]
    t = (track.time.values - t0) / _DAY
    step = track.attrs.get("step_h", 1.0) / 24
    ti = np.arange(t[0], t[-1] + 1e-9, step)
    out = {k: CubicSpline(t, track[k].values, bc_type="not-a-knot")(ti) for k in ("x", "y", "uplift")}
    u, v = _difference(ti, out["x"], scheme), _difference(ti, out["y"], scheme)
    seg = track.segment.values
    spans = [(t[seg == s].min(), t[seg == s].max()) for s in np.unique(seg)]
    observed = np.zeros(ti.size, dtype=bool)
    for a, b in spans:
        observed |= (ti >= a - 1e-9) & (ti <= b + 1e-9)
    ds = xr.Dataset(
        {"x": ("time", out["x"]), "y": ("time", out["y"]), "uplift": ("time", out["uplift"]),
         "speed": ("time", np.hypot(u, v)), "observed": ("time", observed)},
        coords={"time": t0 + np.round(ti * 86400e9).astype("timedelta64[ns]")},
        attrs={**track.attrs, "gap_fill": "not-a-knot cubic spline through smoothed hourly positions",
               "difference_scheme": scheme},
    )
    for k in ("x", "y", "uplift", "speed"):
        ds[k].attrs = track[k].attrs
    return ds
