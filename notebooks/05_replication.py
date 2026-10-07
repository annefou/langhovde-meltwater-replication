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


ev_rain = events(jma.rain)
ev_wet = events(jma.rain | jma.sleet_only)
ev_rain.to_csv(RESULTS_DIR / "jma_rain_events.csv", index=False)
print(ev_rain[["start", "end", "season", "days", "summaries"]].to_string(index=False))

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
# ## Persist results

# %%
table = pd.DataFrame(rows)
table.to_csv(RESULTS_DIR / "arm_b_table.csv", index=False)
table
