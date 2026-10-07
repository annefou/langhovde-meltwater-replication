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
# # 04 — Figures
#
# Figures regenerated from the CC BY 4.0 data deposit
# ([doi:10.17632/8wvtxg53ry.1](https://doi.org/10.17632/8wvtxg53ry.1)) and our own
# results. None is adapted from the CC BY-NC-ND article.
#
# - **Main result:** our analogue of the paper's Fig. 3 as stacked panels on one time
#   axis. Each panel has a single y-scale; the original combines speed and vertical
#   displacement on two y-axes in one panel.
# - **Sensitivity:** the C3 speed-up as a function of smoothing bandwidth.
#
# All times are UTC. The tide is shown in UTC: the deposit file is UTC+3
# (`03_analysis.py` § clock check).

# %%
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

# %%
RESULTS_DIR = Path("../results")
CLEAN_DIR = Path("../data/clean")
FIGURES_DIR = Path("../figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
# Validated categorical slots (dataviz reference palette, light mode): blue, orange, aqua.
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, SHADE = "#0b0b0b", "#898781", "#ecebe6"
plt.rcParams.update({"axes.edgecolor": "#c3c2b7", "grid.color": "#e1e0d9", "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 9, "lines.linewidth": 1.4})

PERIODS = {"I": ("2021-12-21", "2021-12-26"), "II": ("2022-01-02", "2022-01-07")}    # paper-text windows
PERIOD_III = ("2022-01-14", "2022-02-06")
FLOTATION = -436.1 + 551.31 * 0.91                                                    # m a.s.l., code convention

# %%
gnss = xr.open_dataset(RESULTS_DIR / "gnss_tracks.nc")
levels = xr.open_dataset(RESULTS_DIR / "water_levels.nc")
tide = xr.open_dataset(CLEAN_DIR / "tide.nc").tide
tide = tide.assign_coords(time=tide.time - np.timedelta64(3, "h")) - tide.mean()     # file is UTC+3
aws = xr.open_dataset(CLEAN_DIR / "aws.nc")


def var(name: str, min_segment: str = "48h") -> pd.Series:
    """Track with gaps as NaN; segments shorter than min_segment are hidden in the figures.

    Short segments between gaps (GNSS2 in late January) carry edge artefacts of the 12 h
    smoother. The authors' fig3.m does not plot them either. The analysis keeps them.
    """
    sr = gnss[name].to_series().dropna()
    seg = (sr.index.to_series().diff() > pd.Timedelta("2h")).cumsum()
    span = sr.index.to_series().groupby(seg).agg(lambda t: t.max() - t.min())
    sr = sr[seg.map(span >= pd.Timedelta(min_segment)).to_numpy()]
    return sr.where(sr.index.to_series().diff().fillna(pd.Timedelta(0)) < pd.Timedelta("2h"))


def shade(ax, iii: bool = False) -> None:
    for a, b in PERIODS.values():
        ax.axvspan(pd.Timestamp(a), pd.Timestamp(b), color=SHADE, zorder=0, lw=0)
    if iii:
        ax.axvspan(pd.Timestamp(PERIOD_III[0]), pd.Timestamp(PERIOD_III[1]), color=SHADE, alpha=0.5, zorder=0, lw=0)


def label(ax, x: str, y: float, text: str, color: str) -> None:
    ax.text(pd.Timestamp(x), y, text, color=INK, fontsize=8, va="center",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=1))


# %% [markdown]
# ## Main result: speed, uplift, water level, tide and weather

# %%
fig, axs = plt.subplots(6, 1, figsize=(7.5, 10.5), sharex=True,
                        gridspec_kw=dict(height_ratios=[1.3, 1.1, 1.4, 0.7, 0.8, 0.6], hspace=0.12))
a_spd, a_up, a_lvl, a_tide, a_t, a_rain = axs

# a. Horizontal speed, h = 12 h (the published processing), observed solid, spline fill dashed.
spl = gnss[["speed_GNSS1_h12_spline", "observed_GNSS1_h12_spline"]].to_dataframe().dropna()
gap = spl.where(~spl.observed_GNSS1_h12_spline.astype(bool))
a_spd.plot(gap.index, gap.speed_GNSS1_h12_spline, color=C1, lw=0.9, ls=(0, (4, 3)))
for st, c in [("GNSS1", C1), ("GNSS2", C2)]:
    sr = var(f"speed_{st}_h12")
    a_spd.plot(sr.index, sr, color=c)
a_spd.set_ylabel("Horizontal speed\n(m d$^{-1}$)")
label(a_spd, "2022-01-20", 0.335, "GNSS2 (afloat)", C2)
label(a_spd, "2022-01-29", 0.25, "GNSS1 (grounded)", C1)
a_spd.text(pd.Timestamp("2021-12-23T12"), 0.205, "dashed: spline\nthrough gaps", fontsize=7, color=MUTED)

# b. Vertical displacement, h = 12 h.
up_spl = gnss[["uplift_GNSS1_h12_spline", "observed_GNSS1_h12_spline"]].to_dataframe().dropna()
gap = up_spl.where(~up_spl.observed_GNSS1_h12_spline.astype(bool))
a_up.plot(gap.index, gap.uplift_GNSS1_h12_spline, color=C1, lw=0.9, ls=(0, (4, 3)))
for st, c in [("GNSS1", C1), ("GNSS2", C2)]:
    sr = var(f"uplift_{st}_h12")
    a_up.plot(sr.index, sr, color=c)
a_up.set_ylabel("Vertical\ndisplacement (m)")
label(a_up, "2022-01-29", 0.07, "GNSS1", C1)
label(a_up, "2021-12-27", -0.025, "GNSS2", C2)

# c. Borehole water level.
for b, c in [("BH2201", C1), ("BH2202", C2), ("BH2203", C3)]:
    lv = levels[f"level_{b}"].to_series().dropna()
    a_lvl.plot(lv.index, lv, color=c, lw=0.9)
a_lvl.axhline(FLOTATION, color=MUTED, lw=0.8, ls="--")
a_lvl.text(pd.Timestamp("2021-12-20"), FLOTATION + 4, f"flotation level, BH2201/02 ({FLOTATION:.1f} m)",
           fontsize=7, color=MUTED)
a_lvl.set_ylabel("Water level\n(m a.s.l.)")
label(a_lvl, "2022-01-07", 45, "BH2201", C1)
label(a_lvl, "2022-01-16", 40, "BH2202", C2)
label(a_lvl, "2022-01-26", -12, "BH2203", C3)
a_lvl.set_ylim(-25, 135)

# d. Tide at Syowa, UTC.
a_tide.plot(tide.time, tide, color=INK, lw=0.4)
a_tide.set_ylabel("Tide (m)")

# e. Air temperature (hourly mean) and f. daily rain, on-glacier AWS.
t_h = aws.air_temperature.to_series().resample("1h").mean()
a_t.plot(t_h.index, t_h, color=INK, lw=0.6)
a_t.axhline(0, color=MUTED, lw=0.8)
a_t.set_ylabel("Air temp.\n(°C)")
# rain_accum counts since the last 00:00 and the 00:00 record closes the previous day,
# so each record is assigned to the day it closes.
ra = aws.rain_accum.to_series()
rain = ra.groupby((ra.index - pd.Timedelta("1min")).floor("D")).max()
a_rain.bar(rain.index + pd.Timedelta("12h"), rain, width=0.8, color=C1)
a_rain.set_ylabel("Rain\n(mm d$^{-1}$)")

for ax in axs:
    shade(ax, iii=ax is a_lvl)
a_spd.text(pd.Timestamp("2021-12-21T06"), 0.355, "Period I", fontsize=8, color=INK)
a_spd.text(pd.Timestamp("2022-01-02T06"), 0.355, "Period II", fontsize=8, color=INK)
a_lvl.text(pd.Timestamp("2022-01-14T06"), 120, "Period III", fontsize=8, color=INK)
a_spd.set_ylim(0.15, 0.37)
a_rain.set_xlim(pd.Timestamp("2021-12-19"), pd.Timestamp("2022-02-07"))
a_rain.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 10, 20]))
a_rain.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
a_rain.set_xlabel("2021/22 (UTC)")
for ax, letter in zip(axs, "abcdef"):
    ax.text(-0.13, 1.0, letter, transform=ax.transAxes, fontsize=11, fontweight="bold", va="top")
fig.align_ylabels(axs)

fig.savefig(FIGURES_DIR / "main_result.png", dpi=150, bbox_inches="tight")
fig.savefig(FIGURES_DIR / "main_result.pdf", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## C3 sensitivity: speed-up against smoothing bandwidth
#
# Observed data only, local baseline B1, paper-text windows. The band marks the
# paper's 10–20%; the pre-registered tolerance is 7–23%. The paper states a 1 h
# bandwidth, but its figures were made with 12 h (`tests/test_gnss.py`).

# %%
sens = pd.read_csv(RESULTS_DIR / "sensitivity_c3.csv").query("windows == 'paper' and gap == 'observed'")
fig, axs = plt.subplots(1, 2, figsize=(7.5, 3.2), sharey=True)
for ax, period in zip(axs, ["I", "II"]):
    ax.axhspan(7, 23, color=SHADE, lw=0)
    ax.axhspan(10, 20, color="#d9d8d1", lw=0)
    for st, c, dy in [("GNSS1", C1, 5), ("GNSS2", C2, -5)]:
        sub = sens.query("station == @st and period == @period").sort_values("h_hours")
        ax.plot(sub.h_hours, sub.speedup_B1, color=c, marker="o", ms=5, lw=1.4)
        ax.annotate(st, (12, float(sub.speedup_B1.iloc[-1])), xytext=(7, dy), textcoords="offset points",
                    fontsize=8, va="center", color=INK)
    ax.set_xticks([1, 3, 6, 12])
    ax.set_xlabel("Smoothing bandwidth h (hours)")
    ax.set_title(f"Period {period}", fontsize=9, color=INK)
    ax.axvline(1, color=MUTED, lw=0.6, ls=":")
    ax.text(1.3, 79, "paper text", fontsize=7, color=MUTED)
    ax.axvline(12, color=MUTED, lw=0.6, ls=":")
    ax.text(8.6, 79, "code / figures", fontsize=7, color=MUTED)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 83)
axs[0].set_ylabel("Peak speed-up over background (%)")
axs[0].text(0.3, 15, "paper 10–20%", fontsize=7, color=INK, va="center")
fig.tight_layout()
fig.savefig(FIGURES_DIR / "sensitivity_c3.png", dpi=150, bbox_inches="tight")
fig.savefig(FIGURES_DIR / "sensitivity_c3.pdf", bbox_inches="tight")
plt.show()
