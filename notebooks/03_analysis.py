# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 03 — Analysis (Arm A, reproduction)
#
# Recomputes sub-claims C1–C4 and C6–C9 of Sugiyama et al. (2026) from the authors'
# deposit and labels each against the tolerances in `ANALYSIS_PLAN.md`. The plan was
# committed before this code ran. Operational details added afterwards are in the
# plan's § Amendments, each dated. Paper values and their verbatim sources are in
# `nanopubs/drafts/00_paper_summary.md`.
#
# Our own Python. The MATLAB scripts in the deposit were used only for constants
# and conversions.

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

# %%
CLEAN_DIR = Path("../data/clean")
RESULTS_DIR = Path("../results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

claims: list[dict] = []


def record(claim: str, item: str, paper: str, ours: str, tolerance: str, label: str, notes: str = "",
           basis: str = "pre-registered") -> None:
    """basis: 'pre-registered' (ANALYSIS_PLAN.md as committed) or 'post hoc' (dated amendment)."""
    claims.append(dict(claim=claim, item=item, basis=basis, paper=paper, ours=ours,
                       tolerance=tolerance, label=label, notes=notes))
    print(f"[{claim}|{basis}] {item}: paper {paper} | ours {ours} | {label}")


def within(value: float, target: float, tol: float) -> bool:
    return abs(value - target) <= tol


# %% [markdown]
# ## 1. Water level and fraction of flotation
#
# Conversions from `fig3/fig3.m`. The atmospheric correction uses the code's
# constants (`ANALYSIS_PLAN.md` §1; the measured series is embargoed,
# `GAP_SOURCES.md` A6):
#
# - BH2201 (dbar): level = (p − 9.2) × 1.0197 + z_bed
# - BH2202, BH2203 (MPa): level = (p − 0.089) × 101.97 + z_bed
#
# Flotation fraction, primary (code) convention: (level − z_bed) / (551.31 × 0.91).
# That is overburden as freshwater head. The paper's Eq. 1 check uses seawater
# density: z_f = z_b + (z_s − z_b) ρ_i/ρ_s, with z_s = 115.167 m
# (`fig1/borehole_geometry220521.dat`), ρ_i = 910 and ρ_s = 1025.

# %%
Z_BED_GROUNDED = -436.1   # BH2201/02, m a.s.l.
Z_BED_BH2203 = -398.1
H_ICE = 551.31
OVERBURDEN_HEAD = H_ICE * 0.91          # m of fresh water above the bed
Z_SURFACE = 115.167
Z_FLOT_EQ1 = Z_BED_GROUNDED + (Z_SURFACE - Z_BED_GROUNDED) * 910 / 1025


def load_level(name: str) -> xr.DataArray:
    ds = xr.open_dataset(CLEAN_DIR / f"pressure_{name}.nc")
    p = ds.pressure
    if name == "BH2201":
        level = (p - 9.2) * 1.0197 + ds.z_bed_m
    else:
        level = (p - 0.089) * 101.97 + ds.z_bed_m
    level.attrs = {"units": "m a.s.l.", "long_name": f"{name} water level"}
    return level.dropna("time")


level = {b: load_level(b) for b in ["BH2201", "BH2202", "BH2203"]}


def flotation_pct(lv: xr.DataArray) -> xr.DataArray:
    return 100 * (lv - Z_BED_GROUNDED) / OVERBURDEN_HEAD


def flotation_pct_eq1(lv: xr.DataArray) -> xr.DataArray:
    return 100 * (lv - Z_BED_GROUNDED) / (Z_FLOT_EQ1 - Z_BED_GROUNDED)


print(f"flotation level, code convention: {Z_BED_GROUNDED + OVERBURDEN_HEAD:.2f} m a.s.l.; "
      f"Eq. 1 (seawater): {Z_FLOT_EQ1:.2f} m a.s.l.")
for b, lv in level.items():
    print(f"{b}: {str(lv.time.values[0])[:16]} to {str(lv.time.values[-1])[:16]}, "
          f"{float(lv.min()):.1f} to {float(lv.max()):.1f} m a.s.l.")

# %% [markdown]
# ## 2. C1: water pressure close to overburden (93–97% of flotation at BH2201/02)
#
# Min and max over each record, excluding the first 6 h after installation.

# %%
c1 = {}
for b in ["BH2201", "BH2202"]:
    lv = level[b]
    lv = lv.sel(time=slice(lv.time.values[0] + np.timedelta64(6, "h"), None))
    raw = flotation_pct(lv)
    hourly = flotation_pct(lv.resample(time="1h").mean().dropna("time"))
    c1[b] = dict(min=float(raw.min()), max=float(raw.max()),
                 hmin=float(hourly.min()), hmax=float(hourly.max()),
                 eq1_min=float(flotation_pct_eq1(lv).min()), eq1_max=float(flotation_pct_eq1(lv).max()),
                 t_max=str(raw.idxmax().values)[:16])
    print(b, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in c1[b].items()})

lo = min(c1[b]["min"] for b in c1)
hi = max(c1[b]["max"] for b in c1)
bounds_ok = within(round(lo), 93, 1) and within(round(hi), 97, 1)
label = "reproduced" if bounds_ok else ("partially reproduced" if lo > 90 else "not reproduced")
record("C1", "range of % flotation, BH2201/02 (raw)", "93–97%", f"{lo:.1f}–{hi:.1f}%",
       "bounds ±1 percentage point", label,
       f"hourly means {min(c1[b]['hmin'] for b in c1):.1f}–{max(c1[b]['hmax'] for b in c1):.1f}%; "
       f"Eq. 1 (seawater) {min(c1[b]['eq1_min'] for b in c1):.1f}–{max(c1[b]['eq1_max'] for b in c1):.1f}%")

# %% [markdown]
# ### C1, paper-text windows (post hoc, `ANALYSIS_PLAN.md` § Amendments)
#
# The paper describes later phases separately: oscillations then "a rapid increase to
# above the flotation level" at BH2201 from 29 January, and BH2202 "rapidly rose to the
# flotation level" on 22 January. Those phases are excluded here.

# %%
windows = {"BH2201": "2022-01-28T23:59", "BH2202": "2022-01-21T23:59"}
win = {b: flotation_pct(level[b].sel(time=slice(level[b].time.values[0] + np.timedelta64(6, "h"), end)))
       for b, end in windows.items()}
wlo, whi = min(float(w.min()) for w in win.values()), max(float(w.max()) for w in win.values())
w_ok = within(round(wlo), 93, 1) and within(round(whi), 97, 1)
record("C1", "range of % flotation, before the late phases the paper describes", "93–97%",
       f"{wlo:.1f}–{whi:.1f}% (BH2201 {float(win['BH2201'].min()):.1f}–{float(win['BH2201'].max()):.1f}; "
       f"BH2202 {float(win['BH2202'].min()):.1f}–{float(win['BH2202'].max()):.1f})",
       "bounds ±1 percentage point",
       "reproduced" if w_ok else ("partially reproduced" if wlo > 90 else "not reproduced"),
       "BH2201 to 28 Jan; BH2202 to 21 Jan", basis="post hoc")
p2 = flotation_pct(level["BH2201"].sel(time=slice(level["BH2201"].time.values[0] + np.timedelta64(6, "h"),
                                                  "2022-01-06T23:59")))
record("C1", "range of % flotation, Period II only (BH2201)", "93–97%",
       f"{float(p2.min()):.1f}–{float(p2.max()):.1f}%", "bounds ±1 percentage point",
       "reproduced" if within(round(float(p2.min())), 93, 1) and within(round(float(p2.max())), 97, 1)
       else "not reproduced", "BH2202 not yet installed in Period II", basis="post hoc")

# %% [markdown]
# ## 3. C2: the Period II pressure event at BH2201
#
# Operational definitions in `ANALYSIS_PLAN.md` § Amendments (2026-10-07).

# %%
lv1 = level["BH2201"]
start = lv1.time.values[0] + np.timedelta64(6, "h")
pre = lv1.sel(time=slice(start, "2022-01-02T23:59"))
day3 = lv1.sel(time=slice("2022-01-03T00:00", "2022-01-03T23:59"))
t_peak = day3.idxmax().values
peak = float(day3.max())
at_midnight = float(lv1.sel(time="2022-01-03T00:00", method="nearest"))
after = lv1.sel(time=slice(t_peak, t_peak + np.timedelta64(60, "m")))
drop_1h = peak - float(after.min())
hourly1 = lv1.resample(time="1h").mean()
h_after = float(hourly1.sel(time=t_peak + np.timedelta64(1, "h"), method="nearest"))
h_10d = float(hourly1.sel(time=t_peak + np.timedelta64(10, "D"), method="nearest"))
decline_10d = h_after - h_10d

# The 3 Jan peak must also be the Period II maximum, otherwise "peaked" is misleading.
period2_max_time = str(lv1.sel(time=slice("2022-01-02", "2022-01-06")).idxmax().values)[:16]
print(f"pre-event {float(pre.min()):.1f}–{float(pre.max()):.1f} m; peak {peak:.1f} m at {str(t_peak)[:16]} "
      f"(Period II max at {period2_max_time}); level at 3 Jan 00:00 {at_midnight:.1f} m")

checks = {
    "pre-event range": (f"{float(pre.min()):.1f}–{float(pre.max()):.1f} m a.s.l.", "29–33 m a.s.l.", "±2 m",
                        within(float(pre.min()), 29, 2) and within(float(pre.max()), 33, 2)),
    "3 Jan peak": (f"{peak:.1f} m a.s.l. at {str(t_peak)[:16]} UTC "
                   f"({float(flotation_pct(xr.DataArray(peak))):.1f}%)", "51 m a.s.l. (97%) on 3 Jan", "±2 m",
                   within(peak, 51, 2)),
    "rise on 3 Jan": (f"{peak - at_midnight:.1f} m", "20 m", "±2 m", within(peak - at_midnight, 20, 2)),
    "drop within 1 h": (f"{drop_1h:.1f} m", "~10 m", "±3 m", within(drop_1h, 10, 3)),
    "decline over 10 days": (f"{decline_10d:.1f} m", "~30 m", "±5 m", within(decline_10d, 30, 5)),
}
for item, (ours, paper, tol, ok) in checks.items():
    record("C2", item, paper, ours, tol, "within tolerance" if ok else "outside tolerance")

decline_from_peak = peak - h_10d
record("C2", "decline over 10 days, measured from the peak", "~30 m", f"{decline_from_peak:.1f} m", "±5 m",
       "within tolerance" if within(decline_from_peak, 30, 5) else "outside tolerance",
       "alternative reading; not used for the overall C2 label", basis="post hoc")

n_ok = sum(ok for *_, ok in checks.values())
c2_label = "reproduced" if n_ok == len(checks) else "partially reproduced"
record("C2", "overall", "rise to 51 m on 3 Jan, then decline", f"{n_ok}/{len(checks)} items within tolerance",
       "all items", c2_label, "pressure recorded for Period II only (sensor installed 31 Dec)")

# %% [markdown]
# ## 4. C8: head difference BH2201 − BH2203 (9–44 m) and hydraulic gradient
#
# BH2201 is interpolated to BH2203 timestamps over their common record.

# %%
lv3 = level["BH2203"]
common = lv3.sel(time=slice(lv1.time.values[0], lv1.time.values[-1]))
lv1_on3 = lv1.interp(time=common.time)
diff = (lv1_on3 - common).dropna("time")
dmin, dmax = float(diff.min()), float(diff.max())
diff_h = diff.resample(time="1h").mean().dropna("time")
print(f"common record {str(diff.time.values[0])[:16]} to {str(diff.time.values[-1])[:16]}, n={diff.sizes['time']}")
ok_lo, ok_hi = within(dmin, 9, 2), within(dmax, 44, 2)
c8_label = "reproduced" if ok_lo and ok_hi else ("partially reproduced" if ok_lo or ok_hi else "not reproduced")
record("C8", "head difference BH2201 − BH2203", "9–44 m", f"{dmin:.1f}–{dmax:.1f} m", "bounds ±2 m", c8_label,
       f"hourly means {float(diff_h.min()):.1f}–{float(diff_h.max()):.1f} m")
record("C8", "hydraulic gradient", "0.9–4.4 × 10⁻² (1 km)",
       f"{dmin / 1000 * 100:.1f}–{dmax / 1000 * 100:.1f} × 10⁻² (1 km); "
       f"{dmin / 1500 * 100:.1f}–{dmax / 1500 * 100:.1f} × 10⁻² (1.5 km)",
       "follows from the head difference", "reported",
       "Kondo et al. 2025 give 1.5 km to the grounding line (GAP_SOURCES.md D)")

# %% [markdown]
# ### C8, paper-text window (post hoc)
#
# Common record up to the first time BH2201 exceeds 100% of flotation.

# %%
above = flotation_pct(lv1) > 100
t_above = lv1.time.values[int(np.argmax(above.values))]
dw = diff.sel(time=slice(None, t_above))
wmin, wmax = float(dw.min()), float(dw.max())
ok_lo, ok_hi = within(wmin, 9, 2), within(wmax, 44, 2)
record("C8", "head difference, before BH2201 exceeds flotation", "9–44 m", f"{wmin:.1f}–{wmax:.1f} m",
       "bounds ±2 m",
       "reproduced" if ok_lo and ok_hi else ("partially reproduced" if ok_lo or ok_hi else "not reproduced"),
       f"window ends {str(t_above)[:16]} UTC", basis="post hoc")

# %% [markdown]
# ## 5. C7: tidal signal in the boreholes
#
# Operational details are in `ANALYSIS_PLAN.md` § Amendments (C7). The authors
# computed one correlation, in `fig_s4.m`:
# - BH2203 against tide, 25 Jan – 6 Feb, on a 15-min grid;
# - tide mean removed and timestamps shifted by −2.5 h;
# - a further 15-min step for the "with lag" value.
#
# For BH2201/02 the code only plots a scatter over 13–25 Jan.

# %%
tide_ds = xr.open_dataset(CLEAN_DIR / "tide.nc")
tide = tide_ds.tide - tide_ds.tide.mean()             # mean of the whole record, as in the code
CODE_TIDE_SHIFT = np.timedelta64(-150, "m")
STEP = np.timedelta64(15, "m")


def grid(start: str, end) -> np.ndarray:
    end = np.datetime64(end, "ns")
    return np.arange(np.datetime64(start, "ns"), end + np.timedelta64(1, "s"), STEP)


def on_grid(da: xr.DataArray, g: np.ndarray, shift=np.timedelta64(0, "m")) -> np.ndarray:
    t = (da.time.values + shift).astype("datetime64[ns]").astype("int64")
    return np.interp(g.astype("int64"), t, da.values, left=np.nan, right=np.nan)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    m = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[m], b[m])[0, 1])


def highpass(v: np.ndarray, hours: float = 25.0) -> np.ndarray:
    n = int(round(hours * 4)) + 1                       # samples in a centred 25 h window
    return v - pd.Series(v).rolling(n, center=True, min_periods=n).mean().to_numpy()


def lag_scan(lv: np.ndarray, g: np.ndarray) -> pd.Series:
    shifts = np.arange(-6, 6.001, 0.25)
    return pd.Series([corr(lv, on_grid(tide, g, np.timedelta64(int(s * 60), "m"))) for s in shifts],
                     index=shifts, name="r")


# --- BH2203, exactly as fig_s4.m ---
g3 = grid("2022-01-25", "2022-02-06")
lev3 = on_grid(level["BH2203"], g3)
tid3 = on_grid(tide, g3, CODE_TIDE_SHIFT)
r3 = corr(tid3, lev3)
r3_lag = corr(tid3[1:], lev3[:-1])                      # tide2i(2:end) vs level3i(1:end-1)
record("C7", "r, BH2203 vs tide (code method)", "0.965", f"{r3:.3f}", "±0.02",
       "reproduced" if within(r3, 0.965, 0.02) else "not reproduced")
record("C7", "r, BH2203 vs tide with extra 0.25 h lag (code method)", "0.970", f"{r3_lag:.3f}", "±0.02",
       "reproduced" if within(r3_lag, 0.970, 0.02) else "not reproduced")
scan3 = lag_scan(lev3, g3)
print(f"BH2203 lag scan on raw tide timestamps: best shift {scan3.idxmax():+.2f} h, r = {scan3.max():.3f}")

# --- BH2201, BH2202: pre-registered Period III rule ---
c7_rows = {}
for b in ["BH2201", "BH2202"]:
    gb = grid("2022-01-14", level[b].time.values[-1])
    hp = highpass(on_grid(level[b], gb))
    tb = on_grid(tide, gb, CODE_TIDE_SHIFT)
    r = corr(hp, tb)
    m = np.isfinite(hp) & np.isfinite(tb)
    ratio = float(np.polyfit(tb[m], hp[m], 1)[0])
    daily = pd.Series(hp, index=gb).groupby(pd.Series(gb).dt.floor("D").values)
    amp = float(np.median([0.5 * (d.max() - d.min()) for _, d in daily if d.notna().sum() == 96]))
    scan = lag_scan(hp, gb)
    c7_rows[b] = dict(r=r, amp=amp, ratio=ratio, best=scan.idxmax(), r_best=scan.max())
    lab = "reproduced" if (r >= 0.5 and amp < 1) else ("partially reproduced" if r >= 0.3 else "not reproduced")
    record("C7", f"{b} filtered level vs tide, 14 Jan to end", "correlated; amplitude < 1 m",
           f"r = {r:.2f}; amplitude {amp:.2f} m; ratio {ratio:.2f} m/m", "r ≥ 0.5 and amplitude < 1 m", lab,
           f"best shift on raw tide {scan.idxmax():+.2f} h (r = {scan.max():.2f})")

# --- BH2201, BH2202: before the late phases the paper describes (post hoc; same windows as C1) ---
for b, end in windows.items():
    gb = grid("2022-01-14", end)
    hp = highpass(on_grid(level[b], gb))
    tb = on_grid(tide, gb, CODE_TIDE_SHIFT)
    m = np.isfinite(hp) & np.isfinite(tb)
    daily = pd.Series(hp, index=gb).groupby(pd.Series(gb).dt.floor("D").values)
    amp = float(np.median([0.5 * (d.max() - d.min()) for _, d in daily if d.notna().sum() == 96]))
    r, ratio, scan = corr(hp, tb), float(np.polyfit(tb[m], hp[m], 1)[0]), lag_scan(hp, gb)
    lab = "reproduced" if (r >= 0.5 and amp < 1) else ("partially reproduced" if r >= 0.3 else "not reproduced")
    record("C7", f"{b} filtered level vs tide, 14 Jan to {end[5:10]}", "correlated; amplitude < 1 m",
           f"r = {r:.2f}; amplitude {amp:.2f} m; ratio {ratio:.2f} m/m", "r ≥ 0.5 and amplitude < 1 m", lab,
           f"best shift on raw tide {scan.idxmax():+.2f} h (r = {scan.max():.2f})", basis="post hoc")

# %% [markdown]
# ### Clock of the tide file
#
# The code shifts the tide by −2.5 h ("2.5 hours lag!"), and every borehole fits best
# at −2.75 h. The IOC mirror of the same gauge has UTC timestamps
# (`01_data_download.py`). Matching the two measures the file's clock offset directly.

# %%
import json  # noqa: E402

ioc = pd.DataFrame(json.loads(Path("../data/raw/ioc_syow_20220125_20220128.json").read_text()))
ioc = ioc[(ioc.sensor == "prs") & (ioc.slevel < 20)]          # drop the 100 m fill values
s_ioc = pd.Series(ioc.slevel.to_numpy(), pd.to_datetime(ioc.stime)).sort_index()
s_ioc = s_ioc["2022-01-25 06:00":"2022-01-27 18:00"]
dep = tide_ds.tide.to_series()
offsets = np.arange(-300, 301)                                # minutes
r_off = [np.corrcoef(s_ioc.to_numpy(),
                     np.interp((s_ioc.index + pd.Timedelta(minutes=int(m))).asi8, dep.index.asi8, dep.to_numpy()))[0, 1]
         for m in offsets]
best_off = int(offsets[int(np.argmax(r_off))])
resid = np.interp((s_ioc.index + pd.Timedelta(minutes=best_off)).asi8, dep.index.asi8, dep.to_numpy()) - s_ioc.to_numpy()
# Physical lag at 1-min resolution, once the clock offset is known.
lag_rows = []
for name, lv, g, hp in [("BH2203", lev3, g3, False),
                        ("BH2201", on_grid(level["BH2201"], grid("2022-01-14", "2022-01-28T23:45")),
                         grid("2022-01-14", "2022-01-28T23:45"), True),
                        ("BH2202", on_grid(level["BH2202"], grid("2022-01-14", "2022-01-21T23:45")),
                         grid("2022-01-14", "2022-01-21T23:45"), True)]:
    v = highpass(lv) if hp else lv
    mins = np.arange(-240, -119)
    rr = np.array([corr(v, on_grid(tide, g, np.timedelta64(int(m), "m"))) for m in mins])
    near = mins[rr >= rr.max() - 0.001]
    # tide sample at file time T is matched to the borehole at T + shift; file time = UTC + best_off
    lag_rows.append(f"{name} {best_off + mins[int(np.argmax(rr))]:+d} min (range {best_off + near.min()}"
                    f" to {best_off + near.max()})")
print("lag after the gauge, UTC:", "; ".join(lag_rows))

record("C7", "clock of the deposit tide file", "not stated (code shifts −2.5 h)",
       f"UTC{best_off / 60:+.2f} h (r = {max(r_off):.5f}, residual sd {resid.std() * 100:.2f} cm vs IOC syow); "
       f"borehole lag after gauge: {'; '.join(lag_rows)}",
       "—", "reported",
       "the best-fitting shift is 2.75 h (the code's 2.5 h plus the SI's 0.25 h) = the 3 h offset minus a real "
       "lag of ~15 min (1-min scan below); in UTC the boreholes respond after the Syowa gauge, the reverse of "
       "the SI wording; the code's 2.5 h alone is 30 min short of the clock offset", basis="post hoc")

# --- BH2201, BH2202: the code's plotted window (13–25 Jan), computed like BH2203 ---
g1 = grid("2022-01-13", "2022-01-25")
for b in ["BH2201", "BH2202"]:
    rb = corr(on_grid(tide, g1, CODE_TIDE_SHIFT), on_grid(level[b], g1))
    rb_hp = corr(on_grid(tide, g1, CODE_TIDE_SHIFT), highpass(on_grid(level[b], g1)))
    record("C7", f"{b} vs tide, 13–25 Jan (SI Fig. 4 window)", "plotted, no r given",
           f"r = {rb:.2f} unfiltered; {rb_hp:.2f} after 25 h high-pass", "—", "reported",
           "the code computes no r for the grounded boreholes", basis="post hoc")

# %% [markdown]
# ## 6. GNSS speed and uplift: C3, C4, C6
#
# Processing with `gnss.py` (reconstructed `local_regression`, validated against the
# published `fig3.eps` by `tests/test_gnss.py`). Operational details are in
# `ANALYSIS_PLAN.md` § Amendments (C3, C4, C6).

# %%
from gnss import AUTHORS_FIG3, GnssSettings, fill_gaps_spline, process_track  # noqa: E402

BANDWIDTHS = [1, 3, 6, 12]
STATIONS = ["GNSS1", "GNSS2"]
WINDOWS = {
    "paper": {"I": ("2021-12-21T00:00", "2021-12-25T23:59"), "II": ("2022-01-02T00:00", "2022-01-06T23:59")},
    "code": {"I": ("2021-12-22T00:00", "2021-12-27T00:00"), "II": ("2022-01-02T00:00", "2022-01-07T00:00")},
}
DAY = pd.Timedelta("1D")

tracks, filled = {}, {}
for st in STATIONS:
    g = xr.open_dataset(CLEAN_DIR / f"gnss_{st}.nc")
    for h in BANDWIDTHS:
        settings = AUTHORS_FIG3[st] if h == 12 else GnssSettings(bandwidth_h=h)
        tracks[st, h] = process_track(g.time.values, g.lat.values, g.lon.values, g.z.values, settings, st)
        filled[st, h] = fill_gaps_spline(tracks[st, h])
print("processed", len(tracks), "tracks")


def series(ds: xr.Dataset, var: str = "speed") -> pd.Series:
    return ds[var].to_series().dropna()


def in_window(sr: pd.Series, win: tuple[str, str]) -> pd.Series:
    return sr[(sr.index >= pd.Timestamp(win[0])) & (sr.index <= pd.Timestamp(win[1]))]


def masked(sr: pd.Series, wins: dict) -> pd.Series:
    keep = np.ones(len(sr), bool)
    for a, b in wins.values():
        keep &= ~((sr.index >= pd.Timestamp(a)) & (sr.index <= pd.Timestamp(b)))
    return sr[keep]


def baseline_values(obs: pd.Series, wins: dict, period: str, t_peak: pd.Timestamp) -> dict[str, float]:
    m = masked(obs, wins)
    a, b = pd.Timestamp(wins[period][0]), pd.Timestamp(wins[period][1])
    b1 = m[((m.index >= a - 3 * DAY) & (m.index < a)) | ((m.index > b) & (m.index <= b + 3 * DAY))]
    tn = (m.index - m.index[0]) / DAY
    slope, icpt = np.polyfit(tn, m.to_numpy(), 1)
    near = m[(m.index >= t_peak - 3.5 * DAY) & (m.index <= t_peak + 3.5 * DAY)]
    return {"B1": float(b1.median()) if len(b1) else np.nan,
            "B2": float(m.median()),
            "B3": float(icpt + slope * (t_peak - m.index[0]) / DAY),
            "B4": float(near.median()) if len(near) >= 24 else np.nan}


rows = []
for st in STATIONS:
    for h in BANDWIDTHS:
        obs = series(tracks[st, h])
        for gap, sr in [("observed", obs), ("spline", series(filled[st, h]))]:
            for wname, wins in WINDOWS.items():
                for period, win in wins.items():
                    w = in_window(sr, win)
                    row = dict(station=st, h_hours=h, gap=gap, windows=wname, period=period,
                               n_hours=len(w), first=str(w.index.min())[:16] if len(w) else "",
                               peak_time=pd.NaT, peak_speed=np.nan)
                    if len(w):
                        row.update(peak_time=w.idxmax(), peak_speed=float(w.max()))
                        for k, v in baseline_values(obs, wins, period, w.idxmax()).items():
                            row[k] = v
                            row[f"speedup_{k}"] = 100 * (row["peak_speed"] / v - 1)
                    rows.append(row)
sens = pd.DataFrame(rows)
sens.to_csv(RESULTS_DIR / "sensitivity_c3.csv", index=False)

prim = sens.query("h_hours == 12 and windows == 'paper'").set_index(["gap", "station", "period"])
print(prim[["first", "n_hours", "peak_time", "peak_speed", "B1", "speedup_B1", "speedup_B2",
            "speedup_B3", "speedup_B4"]].round(3).to_string())

# %% [markdown]
# ### C3 labels

# %%
def in_range(v: float) -> bool:
    return bool(np.isfinite(v) and 7 <= v <= 23)


cells = [(st, p) for st in STATIONS for p in ["I", "II"]]
obs12 = {c: prim.loc[("observed", *c)] for c in cells}
spl12 = {c: prim.loc[("spline", *c)] for c in cells}
for (st, p), r in obs12.items():
    note = "no observed data in window" if r.n_hours == 0 else f"first hour in window {r['first']}"
    record("C3", f"speed-up {st} Period {p} (h = 12 h, B1, observed)",
           "~20% (Period I GNSS2); 10–20% overall",
           "no data" if r.n_hours == 0 else f"{r.speedup_B1:.1f}% (peak {r.peak_speed:.3f} m/d at "
           f"{str(r.peak_time)[:16]}; B1 {r.B1:.3f} m/d)", "7–23%",
           "no data" if r.n_hours == 0 else ("within range" if in_range(r.speedup_B1) else "outside range"), note)

with_data = [c for c in cells if obs12[c].n_hours > 0]
primary_ok = all(in_range(obs12[c].speedup_B1) for c in with_data)
any_ok = any(in_range(v) for v in sens.query("h_hours == 12 and windows == 'paper'")
             .filter(like="speedup_").to_numpy().ravel())
spline_ok = all(in_range(spl12[c].speedup_B1) for c in cells)
if primary_ok and len(with_data) == len(cells):
    c3_label = "reproduced"
elif primary_ok or spline_ok or any_ok:
    c3_label = "partially reproduced"
else:
    c3_label = "not reproduced"
record("C3", "overall (h = 12 h, B1, paper windows)", "10–20%",
       f"{sum(in_range(obs12[c].speedup_B1) for c in with_data)}/{len(with_data)} cells with data in range "
       f"(observed); {sum(in_range(spl12[c].speedup_B1) for c in cells)}/4 (spline)",
       "all four cells 7–23%", c3_label,
       f"cells without observed data: {[f'{s} {p}' for s, p in cells if obs12[(s, p)].n_hours == 0] or 'none'}")

# %% [markdown]
# ### C3 robustness: bandwidth × baseline, and signal vs noise

# %%
rob = []
for h in BANDWIDTHS:
    for k in ["B1", "B2", "B3", "B4"]:
        for gap in ["observed", "spline"]:
            sub = sens.query("h_hours == @h and windows == 'paper' and gap == @gap")
            rob.append(dict(h_hours=h, baseline=k, gap=gap, cells_in_range=int(sum(in_range(v) for v in sub[f"speedup_{k}"])),
                            cells_with_data=int((sub.n_hours > 0).sum())))
rob = pd.DataFrame(rob)
print(rob.pivot_table(index=["h_hours"], columns=["gap", "baseline"], values="cells_in_range").to_string())
n_all4 = int(((rob.gap == "observed") & (rob.cells_in_range == rob.cells_with_data)).sum())
record("C3", "robustness: bandwidth × baseline combinations with all cells in range (observed)", "—",
       f"{n_all4}/16", "reported", "reported", "per-cell values in results/sensitivity_c3.csv")


def b4_at(obs: pd.Series, wins: dict, t: pd.Timestamp) -> float:
    m = masked(obs, wins)
    near = m[(m.index >= t - 3.5 * DAY) & (m.index <= t + 3.5 * DAY)]
    return float(near.median()) if len(near) >= 24 else np.nan


wins = WINDOWS["paper"]
for st in STATIONS:
    for h in [12, 1]:
        obs = series(tracks[st, h])
        quiet = masked(obs, wins)
        anom = np.array([v / b4_at(obs, wins, t) - 1 for t, v in quiet.items()])
        p95 = 100 * np.nanpercentile(anom, 95)
        peaks = []
        for p in ["I", "II"]:
            w = in_window(obs, wins[p])
            peaks.append(f"P{p} {100 * (w.max() / b4_at(obs, wins, w.idxmax()) - 1):.1f}%" if len(w) else f"P{p} no data")
        record("C3", f"signal vs noise {st} (h = {h} h)", "error 7–12%",
               f"event peak anomaly {', '.join(peaks)}; 95th percentile outside events {p95:.1f}%",
               "reported", "reported", "anomaly = speed / B4 − 1")

# %% [markdown]
# ### C4: uplift

# %%
def uplift_at(sr: pd.Series, t: str) -> float:
    return float(sr.iloc[np.argmin(np.abs(sr.index - pd.Timestamp(t)))])


c4 = {}
for h in BANDWIDTHS:
    zo, zs = series(tracks["GNSS1", h], "uplift"), series(filled["GNSS1", h], "uplift")
    w1o, w1s = in_window(zo, WINDOWS["paper"]["I"]), in_window(zs, WINDOWS["paper"]["I"])
    z0 = uplift_at(zo, "2021-12-21T00:00")
    pre_gap = w1o[w1o.index < pd.Timestamp("2021-12-24")]
    w2 = in_window(zo, ("2022-01-03T00:00", "2022-01-05T23:59"))
    z2 = in_window(series(tracks["GNSS2", h], "uplift"), WINDOWS["paper"]["I"])
    c4[h] = dict(obs=1000 * (w1o.max() - z0), pre_gap=1000 * (pre_gap.max() - z0), spline=1000 * (w1s.max() - z0),
                 t_spline_max=str(w1s.idxmax())[:16], p2=1000 * (w2.max() - uplift_at(zo, "2022-01-03T00:00")),
                 gnss2=1000 * (z2.max() - z2.min()))
    print(h, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in c4[h].items()})

u = c4[12]
ok_obs, ok_spl = within(u["obs"], 120, 20), within(u["spline"], 120, 20)
ok_p2, ok_g2 = 0 <= u["p2"] <= 20, u["gnss2"] < 20
c4_label = ("reproduced" if ok_obs and ok_p2 and ok_g2 else
            "partially reproduced" if (ok_spl or ok_obs or ok_p2 or ok_g2) else "not reproduced")
record("C4", "Period I uplift GNSS1 (h = 12 h)", "120 mm (21–25 Dec)",
       f"observed {u['obs']:.0f} mm (before the 24 Dec gap {u['pre_gap']:.0f} mm); spline {u['spline']:.0f} mm "
       f"(max at {u['t_spline_max']})", "±20 mm", "within tolerance" if ok_obs else
       ("spline only" if ok_spl else "outside tolerance"))
record("C4", "Period II uplift GNSS1 (h = 12 h)", "~10 mm (3–5 Jan)", f"{u['p2']:.0f} mm", "0–20 mm",
       "within tolerance" if ok_p2 else "outside tolerance")
record("C4", "GNSS2 vertical range, Period I (h = 12 h)", "no noticeable displacement",
       f"{u['gnss2']:.0f} mm (data from 23 Dec 15:00)", "< 20 mm", "within tolerance" if ok_g2 else "outside tolerance",
       f"h = 1 h: {c4[1]['gnss2']:.0f} mm (tidal motion of floating ice not smoothed out)")
record("C4", "overall", "uplift ~0.1 m at GNSS1, none at GNSS2", "see items", "all items", c4_label,
       "; ".join(f"h={h}: obs {c4[h]['obs']:.0f}, spline {c4[h]['spline']:.0f}, PII {c4[h]['p2']:.0f}, "
                 f"GNSS2 {c4[h]['gnss2']:.0f} mm" for h in BANDWIDTHS))

# %% [markdown]
# ### C6: timing of the Period II pressure and speed peaks

# %%
t_p = pd.Timestamp(t_peak)
dts = {}
for st in STATIONS:
    for h in BANDWIDTHS:
        w = in_window(series(tracks[st, h]), WINDOWS["paper"]["II"])
        dts[st, h] = ((w.idxmax() - t_p) / pd.Timedelta("1h"), w.idxmax())
dt12, tmax12 = dts["GNSS1", 12]
c6_ok = abs(dt12) <= 24
others = [abs(dts["GNSS1", h][0]) <= 24 for h in BANDWIDTHS]
record("C6", "GNSS1 speed peak minus BH2201 pressure peak (h = 12 h)", "broadly coincided",
       f"{dt12:+.0f} h (speed peak {str(tmax12)[:16]}, pressure peak {str(t_p)[:16]} UTC)", "|Δt| ≤ 24 h",
       "reproduced" if c6_ok and all(others) else ("partially reproduced" if c6_ok or any(others) else "not reproduced"),
       "; ".join(f"{st} h={h}: {dts[st, h][0]:+.0f} h" for st in STATIONS for h in BANDWIDTHS))

export = {f"{k}_{st}_h{h}": tracks[st, h][k].rename({"time": f"time_{st}_h{h}"})
          for st in STATIONS for h in BANDWIDTHS for k in ("speed", "uplift")}
export |= {f"{k}_{st}_h12_spline": filled[st, 12][k].rename({"time": f"time_{st}_h12_spline"})
           for st in STATIONS for k in ("speed", "uplift", "observed")}
xr.Dataset(export).to_netcdf(RESULTS_DIR / "gnss_tracks.nc")

# %% [markdown]
# ## 7. C9: summer climate context at Syowa
#
# PDD as in `figS3/fig_s3.m`: the sum of positive daily mean temperatures over
# December–January, one value per summer (season = year of the January). The seven
# rain events in SI Fig. 3 are hard-coded in `fig_s3.m` as vertical lines; the deposit
# has no rain record behind them. They are checked against JMA weather summaries in
# Arm B.

# %%
from scipy import stats  # noqa: E402

sy = xr.open_dataset(CLEAN_DIR / "syowa_temperature.nc").to_dataframe()
by = sy.groupby("season")
pdd = by.t_mean.apply(lambda v: v.clip(lower=0).sum())
tmean = by.t_mean.mean()
p22, pmean = float(pdd.loc[2022]), float(pdd.mean())
record("C9", "PDD 2021/22 (deposit)", "10.6 °C d", f"{p22:.1f} °C d", "±0.1", "reproduced" if within(p22, 10.6, 0.1)
       else "not reproduced")
record("C9", "mean PDD 1989/90–2025/26 (deposit)", "18.2 °C d", f"{pmean:.2f} °C d", "±0.1",
       "reproduced" if within(pmean, 18.2, 0.1) else "not reproduced")
record("C9", "2021/22 PDD relative to the mean", "40% smaller", f"{100 * (1 - p22 / pmean):.0f}% smaller", "—",
       "reported")

trend = {}
for name, v in [("PDD", pdd), ("Dec–Jan mean temperature", tmean)]:
    lr = stats.linregress(v.index.to_numpy(float), v.to_numpy())
    rho = stats.spearmanr(v.index, v.to_numpy())
    trend[name] = (lr.slope, lr.pvalue)
    unit = "°C d" if name == "PDD" else "°C"
    record("C9", f"trend in {name}, 1989/90–2025/26", "no significant trend",
           f"OLS slope {lr.slope * 10:+.2f} {unit} per decade, p = {lr.pvalue:.2f}", "p ≥ 0.05",
           "reproduced" if lr.pvalue >= 0.05 else "not reproduced", f"Spearman ρ = {rho.statistic:+.2f}, p = {rho.pvalue:.2f}")

# On-glacier AWS: rain_accum counts since the last 00:00; the 00:00 record closes the previous day.
ra = xr.open_dataset(CLEAN_DIR / "aws.nc").rain_accum.to_series()
rain_daily = ra.groupby((ra.index - pd.Timedelta("1min")).floor("D")).max()
r2 = float(rain_daily.loc["2022-01-02"])
record("C9", "rain on 2 January 2022 (on-glacier AWS)", "approximately 30 mm", f"{r2:.1f} mm", "±3 mm",
       "reproduced" if within(r2, 30, 3) else "not reproduced",
       f"other days > 1 mm: {', '.join(f'{d:%d %b} {v:.1f} mm' for d, v in rain_daily[rain_daily > 1].items() if d != pd.Timestamp('2022-01-02'))}",
       basis="post hoc")

RAIN_SEASONS = [1991, 1996, 2004, 2009, 2013, 2018, 2022]          # hard-coded in fig_s3.m
gaps_y = np.diff(RAIN_SEASONS)
half = int(np.median(pdd.index))
record("C9", "rain events since December 1989", "seven; about every five years",
       f"{len(RAIN_SEASONS)} lines in fig_s3.m; mean interval {gaps_y.mean():.1f} years (range {gaps_y.min()}–{gaps_y.max()}); "
       f"{sum(y <= half for y in RAIN_SEASONS)} up to {half}, {sum(y > half for y in RAIN_SEASONS)} after",
       "—", "reported", "events hard-coded in the code, no record deposited: verified in Arm B (JMA)")

# %% [markdown]
# ## Persist results

# %%
table = pd.DataFrame(claims)
table.to_csv(RESULTS_DIR / "claims_table.csv", index=False)
xr.Dataset({f"level_{b}": lv.rename({"time": f"time_{b}"}) for b, lv in level.items()}).to_netcdf(
    RESULTS_DIR / "water_levels.nc")
table
