"""Validate the reconstructed `local_regression` / `latlon2utm` against fig3.eps.

The authors' MATLAB output `fig3/fig3.eps` stores each plotted curve as vector
coordinates. This script recomputes those curves from the raw GNSS files, following
`fig3.m`:
- hard-coded gap indices and hourly evaluation grid;
- forward differences at GNSS2, centred differences at GNSS1;
- `plot(ti(2:end-1), vels(2:end))`.

It does this for a grid of candidate smoothers and reports the RMS misfit to the
plotted curves. Output: `results/reconstruction_validation.csv`.

Run from the repository root: `pixi run python scripts/validate_reconstruction.py`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "notebooks")]
from eps_curves import read_polylines  # noqa: E402
from gnss import find_segments, latlon2utm, local_regression  # noqa: E402

FIG3 = ROOT / "data/raw/mendeley/Field data from Langhovde Glacier and MATLAB code/fig3"
TMIN = pd.Timestamp("2021-12-19")
# Speed/uplift panel frame in EPS units: x 198..694 = tmin..tmin+50 d; y 912..701 = 0.15..0.35 m/d (left), 0..0.6 m (right).
X0, X1, Y0, Y1 = 198.0, 694.0, 912.0, 701.0
DZ_GNSS1 = 0.08   # vertical offset added in fig3.m before plotting

# fig3.eps polyline indices, identified by colour/extent (see notebook 03 § reconstruction).
EPS_SPEED = {"GNSS2": {25: 0}, "GNSS1": {26: 0, 27: 1, 30: 4}}
EPS_UPLIFT_GNSS1 = {33: 0, 34: 1, 37: 4}
MAX_GAP_H = 12.0   # reproduces fig3.m's hard-coded gap rows (any value in 8.3-29.1 h does)
FILES = {"GNSS2": "LG04.dat", "GNSS1": "LG05.dat"}


def load(station: str) -> tuple[np.ndarray, ...]:
    df = pd.read_csv(FIG3 / FILES[station], header=None, skipinitialspace=True)
    time = pd.to_datetime(df[0], format="%Y/%m/%d %H:%M:%S.%f")
    t = ((time - TMIN) / pd.Timedelta("1D")).to_numpy()
    x, y = latlon2utm(df[1].to_numpy(), df[2].to_numpy())
    z = df[3].to_numpy()
    return t, x - x[0], y - y[0], z - z[0], time.to_numpy()


def kernel_lr(t, v, ti, h, kind: str, degree: int) -> np.ndarray:
    """Generic kernel smoother used only to rule out alternative candidates."""
    if kind == "gauss" and degree == 1:
        return local_regression(t, v, ti, h)
    out = np.empty(ti.size)
    for k, t0 in enumerate(ti):
        u = (t - t0) / h
        w = {"gauss": np.exp(-0.5 * u ** 2), "tricube": np.clip(1 - np.abs(u) ** 3, 0, None) ** 3,
             "epan": np.clip(1 - u ** 2, 0, None), "box": (np.abs(u) <= 1).astype(float)}[kind]
        if degree == 0:
            out[k] = (w * v).sum() / w.sum()
        else:
            d = t - t0
            sw, swd, swdd = w.sum(), (w * d).sum(), (w * d * d).sum()
            out[k] = (swdd * (w * v).sum() - swd * (w * d * v).sum()) / (sw * swdd - swd ** 2)
    return out


def segments(t: np.ndarray, time: np.ndarray) -> list[np.ndarray]:
    return [np.arange(t[sl][0], t[sl][-1] + 1e-9, 1 / 24) for sl in find_segments(time, MAX_GAP_H)]


def misfits(polys, data, h_hours: float, kind: str, degree: int) -> dict[str, float]:
    h = h_hours / 24
    out = {}
    for station, (t, dx, dy, dz, time) in data.items():
        errs = []
        for s, ti in enumerate(segments(t, time)):
            if s not in EPS_SPEED[station].values():
                continue
            xs, ys = kernel_lr(t, dx, ti, h, kind, degree), kernel_lr(t, dy, ti, h, kind, degree)
            if station == "GNSS2":
                v, tp = np.hypot(np.diff(xs), np.diff(ys)) / np.diff(ti), ti
                tp, v = tp[1:-1], v[1:]
            else:
                v = np.hypot(xs[2:] - xs[:-2], ys[2:] - ys[:-2]) / (ti[2:] - ti[:-2])
                tp = ti[1:-1]
            for idx, seg in EPS_SPEED[station].items():
                if seg == s:
                    xy = polys[idx].xy
                    et = (xy[:, 0] - X0) / (X1 - X0) * 50
                    ev = 0.15 + (Y0 - xy[:, 1]) / (Y0 - Y1) * 0.2
                    errs.append(np.mean((np.interp(et, tp, v) - ev) ** 2))
        out[f"rms_speed_{station}_m_per_d"] = float(np.sqrt(np.mean(errs)))
    if kind == "gauss" and degree == 1:
        t, _, _, dz, time = data["GNSS1"]
        errs = []
        for s, ti in enumerate(segments(t, time)):
            for idx, seg in EPS_UPLIFT_GNSS1.items():
                if seg == s:
                    xy = polys[idx].xy
                    et = (xy[:, 0] - X0) / (X1 - X0) * 50
                    ez = (Y0 - xy[:, 1]) / (Y0 - Y1) * 0.6 - DZ_GNSS1
                    errs.append(np.mean((np.interp(et, ti, local_regression(t, dz, ti, h)) - ez) ** 2))
        out["rms_uplift_GNSS1_mm"] = float(np.sqrt(np.mean(errs)) * 1000)
    return out


@np.errstate(divide="ignore", invalid="ignore")   # compact kernels with empty windows at small h
def main() -> pd.DataFrame:
    polys = read_polylines(FIG3 / "fig3.eps")
    data = {s: load(s) for s in FILES}
    rows = []
    for kind in ["gauss", "tricube", "epan", "box"]:
        for degree in [0, 1]:
            for h_hours in [1, 3, 6, 11, 12, 13, 18, 24]:
                rows.append(dict(kernel=kind, degree=degree, h_hours=h_hours,
                                 **misfits(polys, data, h_hours, kind, degree)))
    table = pd.DataFrame(rows)
    table["rms_speed_mean"] = table.filter(like="rms_speed").mean(axis=1)
    table = table.sort_values("rms_speed_mean").reset_index(drop=True)
    (ROOT / "results").mkdir(exist_ok=True)
    table.to_csv(ROOT / "results/reconstruction_validation.csv", index=False)
    print(table.head(6).to_string())
    best = table.iloc[0]
    assert (best.kernel, best.degree, best.h_hours) == ("gauss", 1, 12), "reconstruction no longer best match"
    assert best.rms_speed_mean < 2e-4, "reconstruction misfit above EPS rounding precision"
    print("\nOK: Gaussian local linear regression, sigma = h = 12 h reproduces fig3.eps")
    return table


if __name__ == "__main__":
    main()
