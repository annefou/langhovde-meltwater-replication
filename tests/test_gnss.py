"""Tests for notebooks/gnss.py.

Synthetic tests check the maths against known answers. The regression test runs
the full generic pipeline on the authors' raw GNSS files and compares it with the
curves in their published `fig3.eps`. It downloads the deposit first if needed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "notebooks"), str(ROOT / "scripts")]
from gnss import (AUTHORS_FIG3, GnssSettings, find_segments, latlon2utm,  # noqa: E402
                  local_regression, process_track)

FIG3 = ROOT / "data/raw/mendeley/Field data from Langhovde Glacier and MATLAB code/fig3"


# ---------- local_regression ----------

def test_linear_signal_is_returned_unchanged():
    t = np.linspace(0, 10, 400)
    ti = np.linspace(1, 9, 50)
    for h in (0.05, 0.5, 5.0):
        np.testing.assert_allclose(local_regression(t, 3.0 - 0.7 * t, ti, h), 3.0 - 0.7 * ti, atol=1e-9)


def test_quadratic_bias_matches_theory():
    # For dense symmetric sampling, local linear regression with a Gaussian kernel
    # of std h estimates c·t0² as c·(t0² + h²).
    t = np.linspace(-50, 50, 200_001)
    c, h = 0.3, 0.8
    est = local_regression(t, c * t ** 2, np.array([0.0, 2.0]), h)
    np.testing.assert_allclose(est, c * (np.array([0.0, 2.0]) ** 2 + h ** 2), rtol=1e-6)


def test_nan_samples_are_ignored():
    t = np.linspace(0, 1, 101)
    x = 2 * t
    x[10:20] = np.nan
    np.testing.assert_allclose(local_regression(t, x, np.array([0.5]), 0.1), [1.0], atol=1e-9)


@pytest.mark.parametrize("bad", [dict(h=0), dict(h=-1)])
def test_rejects_bad_bandwidth(bad):
    with pytest.raises(ValueError):
        local_regression(np.arange(5.0), np.arange(5.0), np.arange(5.0), **bad)


# ---------- segments and settings ----------

def test_segments_split_only_at_long_gaps():
    hours = np.r_[np.arange(0, 10), np.arange(15, 20), np.arange(50, 55)]   # gaps of 6 h and 31 h
    time = np.datetime64("2022-01-01") + (hours * 3600).astype("timedelta64[s]")
    assert find_segments(time, 12.0) == [slice(0, 15), slice(15, 20)]
    assert find_segments(time, 5.0) == [slice(0, 10), slice(10, 15), slice(15, 20)]


def test_segments_reject_unsorted_time():
    time = np.array(["2022-01-01T01", "2022-01-01T00"], dtype="datetime64[ns]")
    with pytest.raises(ValueError):
        find_segments(time, 12.0)


def test_settings_validate():
    with pytest.raises(ValueError):
        GnssSettings(bandwidth_h=0)
    with pytest.raises(ValueError):
        GnssSettings(scheme="backward")


# ---------- process_track on a synthetic track ----------

def _synthetic_track(speed_m_per_d: float, days: float = 6.0, gap: tuple[float, float] | None = None):
    t_days = np.arange(0, days, 0.25 / 24)                      # 15-min sampling
    if gap:
        t_days = t_days[(t_days < gap[0]) | (t_days > gap[1])]
    x0, y0 = latlon2utm(np.array([-69.2146]), np.array([39.846]))
    ang = np.deg2rad(300)                                       # constant direction
    x = x0[0] + speed_m_per_d * t_days * np.cos(ang)
    y = y0[0] + speed_m_per_d * t_days * np.sin(ang)
    from pyproj import Transformer
    lon, lat = Transformer.from_crs("EPSG:32737", "EPSG:4326", always_xy=True).transform(x, y)
    time = np.datetime64("2022-01-01") + np.round(t_days * 86400).astype("timedelta64[s]")
    return time, lat, lon, 0.01 * t_days                        # 10 mm/d steady rise


@pytest.mark.parametrize("scheme", ["centred", "forward"])
def test_constant_velocity_track(scheme):
    time, lat, lon, z = _synthetic_track(0.25)
    ds = process_track(time, lat, lon, z, GnssSettings(bandwidth_h=6, scheme=scheme))
    np.testing.assert_allclose(ds.speed.dropna("time"), 0.25, rtol=1e-6)
    np.testing.assert_allclose(ds.uplift, 0.01 * (ds.time - ds.time[0]) / np.timedelta64(1, "D"), atol=1e-9)


def test_gap_produces_two_segments_and_no_output_inside():
    time, lat, lon, z = _synthetic_track(0.25, days=6, gap=(2.0, 3.5))
    ds = process_track(time, lat, lon, z, GnssSettings(bandwidth_h=6, max_gap_h=12))
    assert sorted(set(ds.segment.values)) == [0, 1]
    inside = (ds.time > np.datetime64("2022-01-03T00:30")) & (ds.time < np.datetime64("2022-01-04T11:30"))
    assert int(inside.sum()) == 0


# ---------- regression test against the authors' published figure ----------

@pytest.fixture(scope="module")
def deposit() -> Path:
    if not (FIG3 / "fig3.eps").exists():
        subprocess.run([sys.executable, "01_data_download.py"], cwd=ROOT / "notebooks", check=True)
    return FIG3


def _load(path: Path):
    df = pd.read_csv(path, header=None, skipinitialspace=True)
    return pd.to_datetime(df[0], format="%Y/%m/%d %H:%M:%S.%f").to_numpy(), df[1].to_numpy(), \
        df[2].to_numpy(), df[3].to_numpy()


def test_generic_pipeline_reproduces_published_fig3(deposit):
    from eps_curves import read_polylines
    polys = read_polylines(deposit / "fig3.eps")
    tmin = np.datetime64("2021-12-19")
    # Speed panel frame in EPS units: x 198..694 = tmin..tmin+50 d; y 912..701 = 0.15..0.35 m/d.
    curves = {"GNSS2": [25], "GNSS1": [26, 27, 30]}
    files = {"GNSS1": "LG05.dat", "GNSS2": "LG04.dat"}
    for station, idxs in curves.items():
        ds = process_track(*_load(deposit / files[station]), AUTHORS_FIG3[station], station)
        t_ours = (ds.time.values - tmin) / np.timedelta64(1, "D")
        for i in idxs:
            xy = polys[i].xy
            et = (xy[:, 0] - 198) / (694 - 198) * 50
            ev = 0.15 + (912 - xy[:, 1]) / (912 - 701) * 0.2
            seg = ds.segment.values[np.argmin(np.abs(t_ours - et.mean()))]
            m = (ds.segment.values == seg) & np.isfinite(ds.speed.values)
            rms = np.sqrt(np.mean((np.interp(et, t_ours[m], ds.speed.values[m]) - ev) ** 2))
            assert rms < 2e-4, f"{station} curve {i}: rms {rms:.2e} m/d"
