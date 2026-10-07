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
# ## Persist results

# %%
table = pd.DataFrame(claims)
table.to_csv(RESULTS_DIR / "claims_table.csv", index=False)
xr.Dataset({f"level_{b}": lv.rename({"time": f"time_{b}"}) for b, lv in level.items()}).to_netcdf(
    RESULTS_DIR / "water_levels.nc")
table
