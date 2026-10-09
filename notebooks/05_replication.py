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
# # 05 — Replication (Arm B, independent data)
#
# Tests the paper's claims against data the authors did not deposit. Each test is
# pre-registered in `ANALYSIS_PLAN.md` § Arm B before its data were downloaded in full.
# Results go to `results/arm_b_table.csv`, labelled replicated / partially replicated /
# not replicated.

# %%
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

# %%
CLEAN_DIR = Path("../data/clean")
RESULTS_DIR = Path("../results")
rows: list[dict] = []


def record(test: str, item: str, paper: str, ours: str, rule: str, label: str, notes: str = "",
           basis: str = "pre-registered") -> None:
    rows.append(dict(test=test, item=item, basis=basis, paper=paper, ours=ours, rule=rule, label=label, notes=notes))
    print(f"[{test}|{basis}] {item}: paper {paper} | ours {ours} | {label}")


# %% [markdown]
# ## B-rain: rain frequency at Syowa (C9)
#
# JMA daily weather summaries (天気概況), daytime and night-time, Syowa local time.
# Definitions as pre-registered:
# - **rain day:** a summary contains 雨;
# - **sleet-only day:** みぞれ without 雨;
# - **event:** rain days at most 2 days apart;
# - **season:** July–June, labelled by its January;
# - **covered season:** December, January and February each have at least 90% of
#   days with a summary.

# %%
AUTHORS_SEASONS = [1991, 1996, 2004, 2009, 2013, 2018, 2022]      # hard-coded in fig_s3.m

jma = pd.read_parquet(CLEAN_DIR / "jma_syowa_daily.parquet")
text = jma.summary_day + " / " + jma.summary_night
jma["has_summary"] = (jma.summary_day != "") | (jma.summary_night != "")
jma["rain"] = text.str.contains("雨")
jma["sleet_only"] = text.str.contains("みぞれ") & ~jma.rain
jma["season"] = np.where(jma.date.dt.month >= 7, jma.date.dt.year + 1, jma.date.dt.year)

month_cov = jma.groupby(jma.date.dt.to_period("M")).has_summary.mean()
uncovered = month_cov[month_cov < 0.9]
print(f"months with < 90% summaries: {len(uncovered)}; first fully covered month: {month_cov[month_cov >= 0.9].index.min()}")
print("uncovered months:", ", ".join(str(p) for p in uncovered.index))


def season_covered(season: int) -> bool:
    need = [pd.Period(f"{season - 1}-12", "M"), pd.Period(f"{season}-01", "M"), pd.Period(f"{season}-02", "M")]
    return all(month_cov.get(p, 0) >= 0.9 for p in need)


all_seasons = sorted(s for s in jma.season.unique() if s <= 2026)
covered = [s for s in all_seasons if season_covered(s)]
print(f"covered seasons: {len(covered)} of {len(all_seasons)} ({covered[0]}–{covered[-1]})")


def events(flag: pd.Series) -> pd.DataFrame:
    d = jma.loc[flag, ["date", "season", "summary_day", "summary_night"]].sort_values("date")
    new = d.date.diff().dt.days.fillna(99) > 3                      # at most 2 days between rain days
    d["event"] = new.cumsum()
    return d.groupby("event").agg(start=("date", "min"), end=("date", "max"), season=("season", "first"),
                                  days=("date", "size"),
                                  summaries=("summary_day", lambda s: " | ".join(
                                      f"{a} / {b}" for a, b in zip(s, d.loc[s.index, "summary_night"]))))


# English gloss of the JMA weather summaries (天気概況). Translated term by term from a fixed
# glossary of JMA weather vocabulary; any term not in it is kept and marked [?…] rather than guessed.
# JMA grammar: "A一時B" = A, briefly B; "A時々B" = A, at times B; "A後B" = A, later B.
GLOSSARY = {
    "地ふぶき": "drifting snow", "ふぶき": "blizzard", "霧雨": "drizzle", "みぞれ": "sleet", "あられ": "snow pellets",
    "ひょう": "hail", "快晴": "fine", "薄曇": "thin cloud", "晴": "clear", "曇": "cloudy", "雨": "rain", "雪": "snow",
    "霧": "fog", "もや": "mist", "大風": "strong wind", "雷": "thunder", "一時": ", briefly", "時々": ", at times",
    "後一時": ", later briefly", "後時々": ", later at times", "後": ", later", "、": "; ", "を伴う": "",
}
_TERMS = sorted(GLOSSARY, key=len, reverse=True)


def gloss(text: str) -> str:
    out, i = [], 0
    text = re.sub(r"([^、\s/|]+)を伴う", lambda m: "with " + m.group(1), text)   # "、Xを伴う" = "; with X"
    while i < len(text):
        term = next((t for t in _TERMS if text.startswith(t, i)), None)
        if term:
            out.append(GLOSSARY[term] if out or not GLOSSARY[term].startswith(",") else GLOSSARY[term][2:])
            i += len(term)
        elif text[i] in " /|" or text[i].isascii():
            out.append(text[i])
            i += 1
        else:
            out.append(f"[?{text[i]}]")
            i += 1
    g = re.sub(r"(?<=[a-z])(?=[a-z])", "", "".join(out))
    return re.sub(r"\s+", " ", re.sub(r"(\w)(clear|cloudy|rain|snow|sleet|drizzle|blizzard|fog|thin|fine)", r"\1 \2", g)).strip()


ev_rain = events(jma.rain)
ev_wet = events(jma.rain | jma.sleet_only)
ev_rain["summaries_en"] = ev_rain.summaries.map(gloss)
ev_rain.to_csv(RESULTS_DIR / "jma_rain_events.csv", index=False)
print(ev_rain[["start", "end", "season", "days", "summaries_en"]].to_string(index=False))
print("(original JMA wording in results/jma_rain_events.csv, column 'summaries')")

# %% [markdown]
# ### Tests 1–4

# %%
authors_cov = [s for s in AUTHORS_SEASONS if s in covered]


def season_tests(ev: pd.DataFrame, name: str, basis: str) -> None:
    rain_seasons = sorted(s for s in ev.season.unique() if s in covered)
    match = [s for s in authors_cov if s in rain_seasons]
    extra = [s for s in rain_seasons if s not in authors_cov]
    if rain_seasons == authors_cov:
        lab = "replicated"
    elif len(match) >= 5 or abs(len(rain_seasons) - len(authors_cov)) <= 2:
        lab = "partially replicated"
    else:
        lab = "not replicated"
    record("B-rain", f"seasons with rain ({name})", f"seven: {AUTHORS_SEASONS}",
           f"{len(rain_seasons)} covered seasons: {rain_seasons}",
           "exact match = replicated; ≥5 of the authors' seasons or count ±2 = partial", lab,
           f"authors' seasons covered by JMA: {authors_cov}; matched {match}; "
           f"missing {[s for s in authors_cov if s not in rain_seasons]}; extra {extra}", basis=basis)
    gaps = np.diff(rain_seasons)
    mean_gap = float(gaps.mean()) if len(gaps) else np.nan
    record("B-rain", f"mean interval between rain seasons ({name})", "approximately every five years",
           f"{mean_gap:.1f} years (range {gaps.min()}–{gaps.max()})" if len(gaps) else "n/a", "4–6 years",
           "replicated" if 4 <= mean_gap <= 6 else "not replicated", basis=basis)
    counts = pd.Series(0, index=covered, dtype=float)
    counts.update(ev[ev.season.isin(covered)].groupby("season").size().astype(float))
    fit = sm.GLM(counts.to_numpy(), sm.add_constant(np.array(covered, float)), family=sm.families.Poisson()).fit()
    p = float(fit.pvalues[1])
    record("B-rain", f"trend in rain events per season ({name})", "no significant trend",
           f"Poisson slope {fit.params[1]:+.3f} per year, p = {p:.2f} ({int(counts.sum())} events)", "p ≥ 0.05",
           "replicated" if p >= 0.05 else "not replicated", basis=basis)


season_tests(ev_rain, "rain, primary", "pre-registered")
season_tests(ev_wet, "rain or sleet, sensitivity", "pre-registered")

between = jma[(jma.date >= "2017-12-25") & (jma.date <= "2022-01-01") & jma.rain]
record("B-rain", "no rain between December 2017 and 2 January 2022",
       "last recorded rain at Syowa was in December 2017",
       "no rain days" if between.empty else f"{len(between)} rain days: {', '.join(between.date.dt.strftime('%Y-%m-%d'))}",
       "no rain day 25 Dec 2017 – 1 Jan 2022", "replicated" if between.empty else "not replicated")

# Post hoc: the pre-registered window ends on 1 Jan 2022, so it catches the onset of the
# January 2022 event itself (rain in the night of 1 Jan, local time, merged with 2 Jan).
onset = ev_rain[(ev_rain.start <= "2022-01-01") & (ev_rain.end >= "2022-01-02")]
other = between[~between.date.isin(pd.date_range(onset.start.min(), onset.end.max()))] if len(onset) else between
record("B-rain", "no rain between December 2017 and the January 2022 event",
       "last recorded rain at Syowa was in December 2017",
       "no rain days" if other.empty else f"{len(other)} rain day(s): " + "; ".join(
           f"{d:%Y-%m-%d} ({a} / {b})" for d, a, b in zip(other.date, other.summary_day, other.summary_night)),
       "no rain day outside the January 2022 event", "replicated" if other.empty else "not replicated",
       "the 1 Jan 2022 rain day is the onset of the 2 Jan event; the Hirasawa WAMC 2023 abstract also says "
       "'for the first time since December 24, 2017'", basis="post hoc")
record("B-rain", "number of rain events since December 1989", "seven",
       f"{len(ev_rain)} events in {ev_rain.season.nunique()} seasons (sleet included: {len(ev_wet)})", "—", "reported",
       "JMA summaries start in February 1990: the 1989/90 summer cannot be checked")

# Post hoc: SI Fig. 3 is captioned "Summer (December and January)". Restrict events to
# those months to test whether that explains the difference from the authors' list.
dj = ev_rain[ev_rain.start.dt.month.isin([12, 1])]
dj_seasons = sorted(dj.season.unique())
record("B-rain", "rain events in December–January only", f"seven: {AUTHORS_SEASONS}",
       f"{len(dj)} events in seasons {[int(x) for x in dj_seasons]}", "exact match of events and seasons",
       "replicated" if (len(dj) == 7 and [int(x) for x in dj_seasons] == AUTHORS_SEASONS) else "not replicated",
       "the events JMA adds outside December–January: " + "; ".join(
           f"{a:%Y-%m-%d}" for a in ev_rain[~ev_rain.start.dt.month.isin([12, 1])].start), basis="post hoc")

# %% [markdown]
# ## B-pressure: measured air pressure in the borehole correction (C1, C2)
#
# Values from `03_analysis.py` § 8 (`results/pressure_sensitivity.csv`). Arm A
# tolerances are applied to both columns; replicated if no label changes and no C2
# value moves by more than 0.5 m.

# %%
ps = pd.read_csv(RESULTS_DIR / "pressure_sensitivity.csv").set_index("metric")


def c1c2_labels(col: str) -> dict:
    v = ps[col]
    num = lambda k: float(v[k])  # noqa: E731
    lo_, hi_ = min(num("c1_min_BH2201"), num("c1_min_BH2202")), max(num("c1_max_BH2201"), num("c1_max_BH2202"))
    c1 = ("reproduced" if abs(round(lo_) - 93) <= 1 and abs(round(hi_) - 97) <= 1
          else "partially reproduced" if lo_ > 90 else "not reproduced")
    return {"C1": c1,
            "pre-event range": abs(num("pre_min") - 29) <= 2 and abs(num("pre_max") - 33) <= 2,
            "peak": abs(num("peak") - 51) <= 2, "rise": abs(num("rise") - 20) <= 2,
            "drop_1h": abs(num("drop_1h") - 10) <= 3, "decline_10d": abs(num("decline_10d") - 30) <= 5}


lab_code, lab_jma = c1c2_labels("code_constants"), c1c2_labels("jma_corrected")
c2_keys = ["pre_min", "pre_max", "peak", "rise", "drop_1h", "decline_10d"]
max_shift = max(abs(float(ps.loc[k, "jma_corrected"]) - float(ps.loc[k, "code_constants"])) for k in c2_keys)
changed = [k for k in lab_code if lab_code[k] != lab_jma[k]]
record("B-pressure", "C1/C2 with measured air pressure (JMA Syowa hourly)",
       "corrected with hourly air pressure (Methods)",
       f"labels changed: {changed or 'none'}; largest C2 shift {max_shift:.2f} m; peak "
       f"{float(ps.loc['peak', 'jma_corrected']):.1f} m at {ps.loc['peak_time', 'jma_corrected']}",
       "no label change and shifts ≤ 0.5 m",
       "replicated" if not changed and max_shift <= 0.5 else "partially replicated",
       "the code's constants act as sensor offsets; only the air-pressure anomaly is applied")

# %% [markdown]
# ## B-AR: atmospheric-river days at Syowa (reviewer question, context)
#
# Favier (2025), doi:10.5281/zenodo.17165410. Each listed date is already an AR day
# under the catalogue's own ±1-day rule. Documented span: 1980 to March 2022.

# %%
ar = pd.to_datetime(pd.read_csv(Path("../data/raw/favier2025_Syowa_ARday.csv"), header=None)[0])
ar = ar[ar <= "2022-03-31"]
ar_set = set(ar.dt.normalize())
for name, (a, b) in {"Period I": ("2021-12-21", "2021-12-25"), "Period II": ("2022-01-02", "2022-01-06")}.items():
    hits = [d.strftime("%d %b") for d in pd.date_range(a, b) if d in ar_set]
    record("B-AR", f"AR days in {name}", "not attributed in the paper (Reviewer 1: 'consistent with an AR')",
           ", ".join(hits) if hits else "none", "—", "reported")

dj_ar = pd.Series([d for d in ar if d.month in (12, 1)])
dj_season = np.where(dj_ar.dt.month == 12, dj_ar.dt.year + 1, dj_ar.dt.year)
per_season = pd.Series(0, index=range(1981, 2023))
per_season.update(pd.Series(dj_season).value_counts())
n22 = int(per_season.loc[2022])
pct = 100 * float((per_season < n22).mean() + 0.5 * (per_season == n22).mean())
record("B-AR", "December–January AR days, 2021/22 vs 1980/81–2021/22", "2021/22 'not unusual' (Syowa station data)",
       f"{n22} days; percentile {pct:.0f} (median {per_season.median():.0f}, max {per_season.max()})", "—", "reported")

rain_in_span = ev_rain[ev_rain.start <= "2022-03-31"]
def near_ar(row, pad: int) -> bool:
    return any(d in ar_set for d in pd.date_range(row.start - pd.Timedelta(days=pad), row.end + pd.Timedelta(days=pad)))
k1 = sum(near_ar(r, 1) for r in rain_in_span.itertuples())
k0 = sum(near_ar(r, 0) for r in rain_in_span.itertuples())
record("B-AR", "JMA rain events with an AR day", "—",
       f"{k1}/{len(rain_in_span)} within ±1 day (pre-registered); {k0}/{len(rain_in_span)} on the event days "
       "(catalogue's own ±1-day rule)", "—", "reported",
       "events without AR: " + ", ".join(f"{r.start:%Y-%m-%d}" for r in rain_in_span.itertuples() if not near_ar(r, 0)))

# %% [markdown]
# ## B-temp: temperature records independent of the authors' extract (C3 Period I, C9)
#
# 1. PDD from the original JMA daily record, using the authors' definition
#    (`fig_s3.m`): the sum of positive daily means, December–January.
# 2. Period I warmth: JMA Syowa and on-glacier AWS daily maxima, 19–25 Dec 2021.
# 3. ERA5 at the glacier (below, once downloaded).

# %%
import xarray as xr  # noqa: E402

dj = jma[jma.date.dt.month.isin([12, 1])].copy()
dj["season"] = np.where(dj.date.dt.month == 12, dj.date.dt.year + 1, dj.date.dt.year)
complete = dj.groupby("season").t_mean.apply(lambda v: v.notna().sum() == 62)
pdd_jma = dj[dj.season.isin(complete[complete].index)].groupby("season").t_mean.apply(lambda v: v.clip(lower=0).sum())
pdd_jma = pdd_jma.loc[1990:2026]
p22_j, mean_j = float(pdd_jma.loc[2022]), float(pdd_jma.mean())
dep = xr.open_dataset(CLEAN_DIR / "syowa_temperature.nc").to_dataframe()
dep_vs_jma = dep.set_index(dep.index.normalize()).t_mean.sub(jma.set_index("date").t_mean).dropna()
record("B-temp", "PDD from the original JMA record", "10.6 °C d (2021/22); mean 18.2 °C d (1989/90–2025/26)",
       f"{p22_j:.1f}; mean {mean_j:.2f} over {len(pdd_jma)} complete seasons ({pdd_jma.index.min() - 1}/"
       f"{pdd_jma.index.min()}–{pdd_jma.index.max() - 1}/{pdd_jma.index.max()})", "±0.5 °C d each",
       "replicated" if abs(p22_j - 10.6) <= 0.5 and abs(mean_j - 18.2) <= 0.5 else "not replicated",
       f"deposit vs JMA daily means: {int((dep_vs_jma.abs() > 0.05).sum())} of {len(dep_vs_jma)} days differ by > 0.05 °C")

aws = xr.open_dataset(CLEAN_DIR / "aws.nc").air_temperature.to_series()
aws_max = aws.groupby(aws.index.floor("D")).max()
jma_i = jma.set_index("date")
days_i = pd.date_range("2021-12-19", "2021-12-25")
record("B-temp", "daily maximum temperature, 19–25 Dec 2021", "about 5 °C ('period of good weather')",
       "JMA Syowa: " + ", ".join(f"{d:%d} {jma_i.t_max.get(d, np.nan):.1f}" for d in days_i)
       + " | glacier AWS: " + ", ".join(f"{d:%d} {aws_max.get(d, np.nan):.1f}" for d in days_i), "—", "reported",
       "Syowa is on an island ~25 km away; the AWS is the deposit's on-glacier station (UTC days)")

# %% [markdown]
# ### B-temp 3: ERA5 2 m temperature at the glacier
#
# Grid cell nearest GNSS1. Daily means from hourly UTC values, then PDD over
# December–January.

# %%
from scipy import stats  # noqa: E402

GNSS1_LATLON = (-69.214612056, 39.846029576)
cell = xr.open_dataset(Path("../data/raw/era5_arco_t2m_gnss1_dec_jan_1989_2026.nc")).t2m   # ECMWF ARCO, nearest cell
t2m = (cell.to_series() - 273.15).rename_axis("time")
t2m = t2m[t2m.index.month.isin([12, 1])]
daily = t2m.groupby(t2m.index.floor("D")).mean()
season = np.where(daily.index.month == 12, daily.index.year + 1, daily.index.year)
dfe = pd.DataFrame({"t": daily.to_numpy(), "season": season}, index=daily.index)
full = dfe.groupby("season").t.count() == 62
pdd_era = dfe[dfe.season.isin(full[full].index)].groupby("season").t.apply(lambda v: v.clip(lower=0).sum())
pdd_era = pdd_era.loc[1990:2026]
p22_e = float(pdd_era.loc[2022])
pct_e = 100 * float((pdd_era < p22_e).mean())
lr = stats.linregress(pdd_era.index.to_numpy(float), pdd_era.to_numpy())
record("B-temp", "ERA5 PDD at the glacier, 2021/22 vs 1989/90–2025/26", "2021/22 below the long-term mean (Syowa)",
       f"{p22_e:.1f} °C d; percentile {pct_e:.0f}; median {pdd_era.median():.1f}; cell "
       f"{float(cell.latitude):.2f}°, {float(cell.longitude):.2f}°", "below the median",
       "replicated" if p22_e < pdd_era.median() else "not replicated",
       f"r with JMA Syowa PDD: {np.corrcoef(pdd_era, pdd_jma.reindex(pdd_era.index))[0, 1]:.2f}")
record("B-temp", "trend in ERA5 PDD at the glacier", "no significant trend",
       f"OLS slope {lr.slope * 10:+.2f} °C d per decade, p = {lr.pvalue:.2f}", "p ≥ 0.05",
       "replicated" if lr.pvalue >= 0.05 else "not replicated")
# Post hoc: ERA5's SST/sea-ice forcing changed in September 2007 (HadISST2 before, OSTIA
# after; ERA5 data documentation, ECMWF Confluence). Split the record at that change and
# compare with Syowa over the same seasons (2008 = Dec 2007 – Jan 2008, after the change).
pre_e, post_e = pdd_era.loc[:2007], pdd_era.loc[2008:]
pre_j, post_j = pdd_jma.reindex(pre_e.index), pdd_jma.reindex(post_e.index)
tr = {k: stats.linregress(v.index.to_numpy(float), v.to_numpy()) for k, v in [("pre", pre_e), ("post", post_e)]}
record("B-temp", "ERA5 PDD split at the September 2007 forcing change", "—",
       f"ERA5 mean {pre_e.mean():.1f} → {post_e.mean():.1f} °C d (Syowa {pre_j.mean():.1f} → {post_j.mean():.1f}); "
       f"ERA5 trend within segments: {tr['pre'].slope:+.2f} °C d/yr (p = {tr['pre'].pvalue:.2f}, ≤2007), "
       f"{tr['post'].slope:+.2f} °C d/yr (p = {tr['post'].pvalue:.2f}, ≥2008)",
       "—", "reported",
       "the full-record ERA5 decline comes from a step at ERA5's SST/sea-ice input change (HadISST2 → OSTIA, "
       "Sept 2007), with opposite trends either side, and has no counterpart at Syowa: ERA5 at this coastal cell "
       "is not a reliable trend indicator (likely reanalysis inhomogeneity; not proven)", basis="post hoc")
aws_h = aws.resample("1h").mean()
e_h = t2m.reindex(aws_h.index).dropna()
record("B-temp", "ERA5 vs on-glacier AWS, field season (hourly)", "—",
       f"ERA5 − AWS {float((e_h - aws_h.reindex(e_h.index)).mean()):+.1f} °C; r = "
       f"{np.corrcoef(e_h, aws_h.reindex(e_h.index))[0, 1]:.2f} (n = {len(e_h)} h)", "—", "reported",
       "ERA5 underestimates near-surface warmth at the glacier", basis="post hoc")
tmax_e = t2m.groupby(t2m.index.floor("D")).max()
record("B-temp", "ERA5 daily maximum at the glacier, Periods I and II", "about 5 °C (Period I)",
       "PI: " + ", ".join(f"{d:%d} {tmax_e.get(d, np.nan):.1f}" for d in pd.date_range("2021-12-19", "2021-12-25"))
       + " | PII: " + ", ".join(f"{d:%d} {tmax_e.get(d, np.nan):.1f}" for d in pd.date_range("2022-01-01", "2022-01-06")),
       "—", "reported", "UTC days; a 0.25° cell")

# %% [markdown]
# ## B-melt: passive-microwave surface-melt flags
#
# Daily wet/dry status (1 = melt). The grid cell nearest GNSS1 that has data; a 25 km or
# 10 km cell mixes glacier, rock and sea ice.

# %%
AMSR_PASSES = ["snow_status_wet_dry_19H_ASC_filter", "snow_status_wet_dry_19H_DSC_filter"]


def melt_series(path: Path, var: str = "melt") -> tuple[pd.Series, str]:
    """Daily melt flag at the valid cell nearest GNSS1.

    The cell is chosen from one date, and only that cell's time series is read: the
    full AMSR grid (9000 days x 500 x 580) would not fit in a CI runner's memory.
    For AMSR, melt = 1 if either filtered pass flags it, NaN if both are missing.
    """
    ds = xr.open_dataset(path)
    flags = [var] if var in ds else AMSR_PASSES
    lat, lon = ds["lat"].values, ds["lon"].values
    day = ds[flags[0]].sel(time="2021-12-15", method="nearest")
    valid = np.any([np.isfinite(ds[f].sel(time=day.time).values) for f in flags], axis=0)
    d = np.hypot((lat - GNSS1_LATLON[0]) * 111, (lon - GNSS1_LATLON[1]) * 111 * np.cos(np.deg2rad(lat)))
    d[~valid] = np.inf
    iy, ix = np.unravel_index(np.argmin(d), d.shape)
    ydim, xdim = ds[flags[0]].dims[1], ds[flags[0]].dims[2]
    cols = [ds[f].isel({ydim: iy, xdim: ix}).load() for f in flags]
    if len(cols) == 1:
        sr = cols[0].to_series()
    else:
        a, b = cols
        sr = xr.where(a.isnull() & b.isnull(), np.nan, np.fmax(a.fillna(0), b.fillna(0))).to_series()
    return sr, f"cell centre {lat[iy, ix]:.3f}°, {lon[iy, ix]:.3f}°, {d[iy, ix]:.1f} km from GNSS1"


melt_files = {"SSM/I 25 km": Path("../data/raw/melt/CumJour-Antarctic-ssmi-1979-2025-H19.nc"),
              "AMSR 10 km": Path("../data/raw/melt/melt-AMSRJ-antarctic-10km.nc")}
detected = {}
for name, path in melt_files.items():
    sr, where = melt_series(path)
    for per, (a, b) in {"I": ("2021-12-21", "2021-12-25"), "II": ("2022-01-02", "2022-01-06")}.items():
        w = sr.loc[a:b]
        detected[name, per] = bool((w > 0).any())
        record("B-melt", f"melt flag {name}, Period {per}", "surface melt during the event",
               f"{int((w > 0).sum())}/{int(w.notna().sum())} days flagged ({', '.join(f'{d:%d %b}' for d in w[w > 0].index) or 'none'})",
               "flagged in ≥1 product", "reported", where)
    sdj = sr[sr.index.month.isin([12, 1])]
    seas = np.where(sdj.index.month == 12, sdj.index.year + 1, sdj.index.year)
    counts = pd.Series(sdj.to_numpy(), index=seas).groupby(level=0).agg(["sum", "count"])
    counts = counts[counts["count"] >= 55]["sum"]
    if 2022 in counts.index:
        record("B-melt", f"December–January melt days, {name}", "2021/22 less meltwater than usual (C9)",
               f"{counts.loc[2022]:.0f} days; median {counts.median():.0f} over {len(counts)} seasons "
               f"({counts.index.min() - 1}/{counts.index.min()}–{counts.index.max() - 1}/{counts.index.max()})",
               "below the median", "replicated" if counts.loc[2022] < counts.median() else "not replicated", where)
for per in ["I", "II"]:
    hit = any(detected[n, per] for n in melt_files)
    record("B-melt", f"surface melt detected in Period {per}", "melt / rain on the glacier", "yes" if hit else "no",
           "flagged in ≥1 product", "replicated" if hit else "not replicated",
           "; ".join(f"{n}: {'yes' if detected[n, per] else 'no'}" for n in melt_files))

# %% [markdown]
# ## B-velocity: ITS_LIVE image-pair velocity at the GNSS sites
#
# For each pair: GNSS mean horizontal speed over the same interval, from the h = 12 h
# track with the spline fill; the fraction of the interval that is interpolated is
# recorded. ITS_LIVE v is in m/yr and converted to m/d.

# %%
its = xr.open_dataset(Path("../data/raw/itslive_gnss_pixels_202112_202202.nc"))
gt = xr.open_dataset(RESULTS_DIR / "gnss_tracks.nc")
PI, PII = (pd.Timestamp("2021-12-21"), pd.Timestamp("2021-12-26")), (pd.Timestamp("2022-01-02"), pd.Timestamp("2022-01-07"))


def overlap_days(a: pd.Timestamp, b: pd.Timestamp, w: tuple) -> float:
    return max(0.0, (min(b, w[1]) - max(a, w[0])) / pd.Timedelta("1D"))


pairs = []
for site in ["GNSS1", "GNSS2"]:
    sp = gt[[f"speed_{site}_h12_spline", f"observed_{site}_h12_spline"]].to_dataframe().dropna()
    sp.columns = ["speed", "observed"]
    px = its.sel(site=site)
    for i in range(px.sizes["mid_date"]):
        v = float(px.v.isel(mid_date=i))
        if not np.isfinite(v):
            continue
        a = pd.Timestamp(px.acquisition_date_img1.isel(mid_date=i).values)
        b = pd.Timestamp(px.acquisition_date_img2.isel(mid_date=i).values)
        seg = sp.loc[a:b]
        if len(seg) == 0 or (seg.index[0] - a) > pd.Timedelta("1D") or (b - seg.index[-1]) > pd.Timedelta("1D"):
            continue                                                   # GNSS record does not span the pair
        pairs.append(dict(site=site, t1=a, t2=b, dt_days=(b - a) / pd.Timedelta("1D"),
                          sat=str(px.satellite_img1.isel(mid_date=i).values), v_its=v / 365.25,
                          v_err=float(px.v_error.isel(mid_date=i)) / 365.25, v_gnss=float(seg.speed.mean()),
                          interp_frac=float(1 - seg.observed.astype(bool).mean()),
                          ov_I=overlap_days(a, b, PI), ov_II=overlap_days(a, b, PII)))
pairs = pd.DataFrame(pairs)
pairs.to_csv(RESULTS_DIR / "itslive_pairs.csv", index=False)
for site, g in pairs.groupby("site"):
    d = g.v_its - g.v_gnss
    record("B-velocity", f"ITS_LIVE vs GNSS pair-mean speed, {site}", "—",
           f"n = {len(g)} pairs ({g.dt_days.min():.0f}–{g.dt_days.max():.0f} d); bias {d.mean():+.3f} m/d; "
           f"RMS {np.sqrt((d ** 2).mean()):.3f} m/d; r = {np.corrcoef(g.v_its, g.v_gnss)[0, 1]:.2f}; "
           f"GNSS mean {g.v_gnss.mean():.3f} m/d", "—", "reported",
           f"median ITS_LIVE error {g.v_err.median():.3f} m/d")
    inI = g[g.ov_I >= 3]
    quiet = g[(g.ov_I == 0) & (g.ov_II == 0)]
    if len(inI) >= 2 and len(quiet) >= 2:
        diff = inI.v_its.mean() - quiet.v_its.mean()
        se = np.sqrt(inI.v_its.var() / len(inI) + quiet.v_its.var() / len(quiet))
        gdiff = inI.v_gnss.mean() - quiet.v_gnss.mean()
        ok = diff > 2 * se and np.sign(diff) == np.sign(gdiff)
        record("B-velocity", f"Period I speed-up detectable by ITS_LIVE, {site}", "speed-up 10–20% (GNSS)",
               f"ITS_LIVE {diff:+.3f} ± {se:.3f} m/d (pairs ≥3 d in PI: {len(inI)}; quiet: {len(quiet)}); "
               f"GNSS on the same pairs {gdiff:+.3f} m/d", "difference > 2 SE, same sign as GNSS",
               "feasible" if ok else "not feasible")
    else:
        record("B-velocity", f"Period I speed-up detectable by ITS_LIVE, {site}", "speed-up 10–20% (GNSS)",
               f"too few pairs (in PI: {len(inI)}, quiet: {len(quiet)})", "difference > 2 SE", "not feasible")
n_valid = {site: int(np.isfinite(its.sel(site=site).v.values).sum()) for site in ["GNSS1", "GNSS2"]}
record("B-velocity", "ITS_LIVE pairs available", "—",
       f"{its.sizes['mid_date']} pairs per pixel in the window; valid v: GNSS1 {n_valid['GNSS1']}, GNSS2 {n_valid['GNSS2']}; "
       f"spanned by the GNSS record: GNSS1 {int((pairs.site == 'GNSS1').sum())}, GNSS2 {int((pairs.site == 'GNSS2').sum())}",
       "—", "reported", "no valid Sentinel-1 pair at either pixel; shortest valid pair 8 days")

# %% [markdown]
# ## B-optical: Sentinel-2 surface water around GNSS1
#
# Clear sky: at least 90% of the 2 km box neither cloud nor cloud shadow (SCL 3, 8, 9, 10)
# nor no-data (SCL 0, 1). NDWI = (B03 − B08) / (B03 + B08) on reflectance. The BOA offset
# (−1000) is removed for processing baseline ≥ 04.00 when not already applied upstream.

# %%
scenes = []
for path in sorted(Path("../data/raw/s2").glob("*.nc")):
    ds = xr.open_dataset(path)
    scl = ds.scl.values
    nodata, cloud = np.isin(scl, [0, 1]), np.isin(scl, [3, 8, 9, 10])
    offset = 1000 if (ds.attrs.get("processing_baseline", "0") >= "04.00"
                      and ds.attrs.get("boa_offset_applied", "") not in ("True", "true")) else 0
    g = ds.green.values.astype(float) - offset
    n = ds.nir.values.astype(float) - offset
    ok = ~nodata & ~cloud & (g + n > 0)
    ndwi = np.where(ok, (g - n) / np.where(g + n == 0, np.nan, g + n), np.nan)
    scenes.append(dict(scene=ds.attrs["item"], time=pd.Timestamp(ds.attrs["datetime"]).tz_localize(None),
                       clear=float(1 - (nodata | cloud).mean()), water_frac=float(np.nanmean(ndwi > 0.25)) if ok.any() else np.nan,
                       ndwi_median=float(np.nanmedian(ndwi)) if ok.any() else np.nan, offset=offset,
                       baseline=ds.attrs.get("processing_baseline", "")))
# The catalogue lists reprocessed duplicates of the same acquisition: keep the latest baseline.
scenes = (pd.DataFrame(scenes).assign(acq=lambda d: d.time.dt.floor("min"))
          .sort_values(["acq", "baseline"]).groupby("acq").tail(1).sort_values("time"))
scenes.to_csv(RESULTS_DIR / "s2_scenes.csv", index=False)
clear = scenes[scenes.clear >= 0.9]
print(clear[["time", "clear", "water_frac", "ndwi_median"]].round(3).to_string(index=False))
pre = clear[clear.time < pd.Timestamp("2021-12-20")]
inI = clear[(clear.time >= pd.Timestamp("2021-12-20")) & (clear.time < pd.Timestamp("2021-12-26"))]
if len(pre) and len(inI):
    ref = float(pre.iloc[-1].water_frac)
    best = inI.loc[inI.water_frac.idxmax()]
    hit = best.water_frac >= max(2 * ref, 0.01)
    lab = "replicated" if hit else "not replicated"
    ours = (f"Period I max {best.water_frac:.3f} on {best.time:%d %b} vs {ref:.3f} on "
            f"{pre.iloc[-1].time:%d %b}; clear scenes: {len(clear)} of {len(scenes)}")
else:
    lab, ours = "not testable", f"clear scenes before / in Period I: {len(pre)} / {len(inI)} (of {len(scenes)})"
record("B-optical", "surface water (NDWI > 0.25) around GNSS1 in Period I", "meltwater on the glacier surface",
       ours, "≥ 2× the clear scene before and > 1%", lab)

# %% [markdown]
# ## Persist results

# %%
table = pd.DataFrame(rows)
table.to_csv(RESULTS_DIR / "arm_b_table.csv", index=False)
table
