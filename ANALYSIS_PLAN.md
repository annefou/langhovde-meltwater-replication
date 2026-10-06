# Analysis plan: Arm A (reproduction)

Written and committed on 2026-10-06, **before any analysis code was run** on the deposit. Only data inspection had been done (file formats, coverage, and the PDD check in `GAP_SOURCES.md` A2). The git history of this file is the record of what was decided before the results were known. Changes made after results are seen go in § Amendments, dated, with a reason, and never overwrite the original text.

Sources of the target numbers: `nanopubs/drafts/00_paper_summary.md` (verbatim, page-referenced). Gaps and processing choices: `GAP_SOURCES.md`.

## 1. Processing

**Borehole names.** Publication names throughout (mapping in `00_paper_summary.md`). Paper BH2203 = field BH2205.

**GNSS → speed and uplift.**
- Files: `LG05.dat` = GNSS1 (grounded), `LG04.dat` = GNSS2 (afloat). Lat/lon → UTM zone 37S (EPSG:32737) with `pyproj`.
- Smoothing: Gaussian-kernel **local linear regression** of x, y, z against time, evaluated hourly. This is the closest documented match to the missing `local_regression.m` (`GAP_SOURCES.md` A1). The bandwidth h is the kernel standard deviation.
- Bandwidths: **h = 1 h** (paper text), **h = 12 h** (deposited code), plus 3 h and 6 h for the sensitivity curve.
- Horizontal speed = magnitude of the time derivative of smoothed (x, y), in m d⁻¹.
- Gaps: GNSS1 is missing 24–25 Dec 2021, 12–19 Jan and 22–26 Jan 2022. Speeds inside a gap are computed two ways: (i) **observed only**, with gaps left empty; (ii) **gap-filled** by cubic spline through the hourly smoothed positions, as the paper does. Every number that depends on a gap is reported both ways.

**Pressure → water level → fraction of flotation.**
- Conversion as in `fig3.m`: BH2201 `(p − 9.2) × 1.0197 + z_bed`; BH2202 and BH2203 `(p − 0.089) × 101.97 + z_bed`. Beds: −436.1 m (BH2201/02) and −398.1 m (BH2203).
- Primary flotation reference, as in the code: the overburden head `z_i = 551.31 × 0.91` above the bed, i.e. ρ_i/ρ_w with ρ_w = 1000. The paper's Eq. 1 (ρ_s = 1025) is computed alongside and reported as a check, because the two conventions give different percentages.
- Atmospheric correction: the code's constants (primary, reproduction). JMA Syowa hourly station pressure is a sensitivity case: `GAP_SOURCES.md` B1, with times in UTC+3 converted to UTC.

**Tide.** `tide_211231_220206.dat`, with the code's 2.5 h shift (primary) and a lag scan from −6 h to +6 h in 0.25 h steps.

**Events.** These windows are fixed from the paper text, not from our data:
- **Period I:** 21–25 Dec 2021
- **Period II:** 2–6 Jan 2022
- **Period III:** 14 Jan 2022 to the end of the pressure record

**Background speed** (undefined in the paper, `GAP_SOURCES.md` A3). Four baselines, each computed per station and with the event windows excluded:
- **B1 local:** median speed over the 3 days before and the 3 days after each event window, using whichever days have data. GNSS2 starts on 23 Dec, so for Period I it has only the "after" side.
- **B2 campaign median.**
- **B3 campaign linear trend:** least squares on time, evaluated at the event peak.
- **B4 running median:** 7 days, centred.

Speed-up (%) = 100 × (peak speed in window / baseline − 1).

## 2. Tolerances and decision rules

Each sub-claim gets one label: **reproduced**, **partially reproduced** or **not reproduced**. Tolerances are set from the stated instrument and processing errors, not from our results.

| Claim | Paper | Reproduced if | Partially if |
|---|---|---|---|
| C1 | 93–97% of flotation at BH2201/02 | Our min and max over the record (31 Dec – 5 Feb, BH2201; 7 Jan – 5 Feb, BH2202), excluding the first 6 h after each installation, round to within ±1 percentage point of 93% and 97% | Exceeds 90% throughout (the abstract's wording) but the bounds miss by more than 1 percentage point |
| C2 | 29–33 m a.s.l. until 2 Jan; +20 m to a 51 m peak on 3 Jan; −10 m within 1 h; −30 m over 10 days | Pre-event range within ±2 m of 29–33; peak within ±2 m of 51 and dated 3 Jan (UTC); rise within ±2 m of 20; 1 h drop within ±3 m of 10; 10-day decline within ±5 m of 30 | Shape and date match, but one or more magnitudes fall outside tolerance |
| C3 | Speed-up 10–20%; Period I GNSS2 ~20%, GNSS1 similar or greater; Period II 2–6 Jan | With **h = 12 h** (the code's processing): peak speed-up in **both** periods at GNSS2, and at GNSS1 observed-only, lies within 10–20% ± 3 percentage points for **B1** | It holds only with spline gap-fill, only for some baselines, or only at one station or one period |
| C3 robustness (reported, not labelled) | — | Count of bandwidth × baseline combinations, out of 16, in which C3 holds. **Signal vs noise:** event peak anomaly compared with the 95th percentile of speed anomalies (relative to B4) outside the event windows | — |
| C4 | GNSS1 +120 mm (21–25 Dec); ~10 mm (3–5 Jan); none at GNSS2 | Period I uplift within ±20 mm of 120; Period II uplift between 0 and 20 mm; GNSS2 \|Δz\| < 20 mm over 21–25 Dec. Observed-only and spline-filled uplift reported separately | 120 mm is matched only with the spline fill (i.e. depends on the gap) |
| C6 | Pressure peak "broadly coincided" with speed peak (Period II) | Peak times within ±24 h at h = 12 h. Lag in hours reported for every h | Within ±24 h at some bandwidths but not others |
| C7 | Semidiurnal variations from 14 Jan, amplitude < 1 m, correlated with tide; BH2203 r = 0.965 (0.970 at 0.25 h lag) | BH2203 r within ±0.02 of 0.965. BH2201 and BH2202 (water level minus a 25 h running mean) against tide in Period III: r ≥ 0.5 and amplitude < 1 m. Also reported: best lag, and the amplitude ratio (m of water level per m of tide; about 1 is expected if pressure is transmitted hydraulically, `GAP_SOURCES.md` A8) | Correlation present (r ≥ 0.3) but weaker than 0.5 |
| C8 | Head difference BH2201 − BH2203 of 9–44 m; gradient 0.9–4.4 × 10⁻² over 1 km | Min and max of the difference over the common record within ±2 m of 9 and 44 | One bound within tolerance. Gradient also reported for 1.5 km (`GAP_SOURCES.md` D) |
| C9 | PDD 10.6 vs mean 18.2 °C·d; no significant trend | Deposit: within ±0.1 °C·d (already met, A2). Trend: OLS slope of PDD and of Dec–Jan mean temperature against year, p ≥ 0.05 | — |

C5 (the headline) receives no direct label. Its verdict is composed from C1–C4 and C6, and stated with its scope: number of events with pressure data, number of sites, number of seasons.

**Primary vs sensitivity.** Labels come from the **primary** processing:
- h = 12 h, the code's atmospheric constants, and the 2.5 h tide shift, because these produced the published figures;
- B1 as the baseline.

Results with h = 1 h (the paper text) are reported next to every primary number. **If a label changes between 12 h and 1 h, that is itself a finding** and is stated in the Outcome.

## 3. Outputs

- `results/claims_table.csv`: one row per claim: paper value, our value(s), tolerance, label, notes.
- `results/sensitivity_c3.csv`: speed-up by bandwidth × baseline × station × period × gap handling.
- `figures/main_result.png`: our regenerated Fig. 3 analogue (speed, uplift, water level, tide, weather), with Periods I–III shaded and observed vs gap-filled segments distinguished. Figures are drawn from the CC-BY data, never adapted from the CC BY-NC-ND article.
- Intermediate time series: NetCDF in `data/clean/` (DOMAIN.md: no `.npz`).

## Amendments

_None yet._
