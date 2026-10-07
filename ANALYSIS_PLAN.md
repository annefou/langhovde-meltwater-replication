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

### 2026-10-07: operational details for C1, C2 and C8 (written before computing them)

These fill in measurement details the plan left open. No tolerance or decision rule changes.

- **Resolution.** C1 and C8 bounds use the raw logger values: BH2201 1 min; BH2202 and BH2203 as logged. The plan says "min and max over the record" and specifies no smoothing. Hourly-mean bounds are reported alongside, for information only.
- **C2, pre-event range.** BH2201 from installation + 6 h to 2 Jan 23:59 UTC.
- **C2, rise.** Peak (maximum on 3 Jan UTC) minus the level at 3 Jan 00:00 UTC. This is anchored to the text: "On January 3, the water level rose progressively by 20 m".
- **C2, 1 h drop.** Peak minus the minimum within the 60 min after the peak.
- **C2, 10-day decline.** Hourly-mean level 1 h after the peak minus the hourly-mean level 10 days after the peak.
- **C8.** BH2201 interpolated linearly to BH2203 timestamps over their common record. Differences are taken only where both have data.
- **Flotation convention.** In `fig3.m`, % of flotation = 100 × (level − z_bed) / (551.31 × 0.91). That is overburden as freshwater head (ρ_i/ρ_w, ρ_w = 1000). This is the primary convention, as already stated in §1.

### 2026-10-07: paper-text windows for C1, C2 and C8 (written AFTER seeing the step-2 results; post hoc)

The pre-registered labels stand. These are additional, clearly labelled readings.

**Why.** The paper itself describes phases that the whole-record rule includes:
- BH2201: "High-frequency oscillations in the borehole level began on 29 January, followed in early February by a rapid increase to above the flotation level."
- BH2202: "…until 22 January, when the water level in BH2202 rapidly rose to the flotation level".

The authors' `fig3.m` also clips the water-level axis at 85 m a.s.l. So the paper's ranges cannot refer to the whole record. Each claim is therefore reported twice: under the pre-registered rule, and under a window taken from the paper's own text. Neither window is chosen from our numbers.

- **C1, paper-text window.** BH2201 from installation + 6 h to 28 Jan (before the oscillations); BH2202 from installation + 6 h to 21 Jan (before the rise). Also reported: Period II only (31 Dec – 6 Jan), the only period the 93–94% → 97% text numbers describe.
- **C8, paper-text window.** Common record up to the first time BH2201 exceeds 100% of flotation ("rapid increase to above the flotation level").
- **C2, alternative reading of the 10-day decline.** Peak minus the hourly mean 10 days later, in case "~30 m" was meant from the peak. The pre-registered reading (from 1 h after the peak, i.e. after the 10 m drop) stays primary.

### 2026-10-07: missing MATLAB functions reconstructed and validated against fig3.eps

`local_regression` and `latlon2utm` are reconstructed in the generic module `notebooks/gnss.py`, which never reads the figures. Gaps are detected from timestamps; any threshold of 8.3–29.1 h reproduces the hard-coded rows, and 12 h is used. The reconstruction was identified once by `scripts/validate_reconstruction.py` (output `results/reconstruction_validation.csv`) and is guarded by `tests/test_gnss.py`. That test runs the full generic pipeline on the raw files against `fig3.eps`, downloading the deposit if needed, alongside synthetic unit tests. The deposit includes `fig3.eps`, the vector output of the authors' own code. Its plotted curves were recomputed from the raw GNSS files for 4 kernels × 2 regression degrees × 8 bandwidths.

**Only one candidate matches:** a Gaussian-kernel local linear regression with σ = h, at **h = 12 h**:
- GNSS2 speed: 0.00007 m/d RMS
- GNSS1 speed: 0.00004 m/d RMS
- GNSS1 uplift: 0.06 mm RMS

These residuals are at the EPS rounding precision. h = 11 h and h = 13 h are about 9× worse. UTM zone 37S (WGS84, pyproj) reproduces `latlon2utm` within the same residuals.

This confirms the §1 smoother. It also establishes from the published figure itself that **Fig. 3 used 12 h smoothing**, against the Methods' "bandwidth of 1 h". The primary processing (h = 12 h) was already set in §2; no rule changes.

**Noted for step 4.** `fig3.m` shades Period I as 22–27 Dec (`tmin+3 … +8`) and Period II as 2–7 Jan (`tmin+14 … +19`). The plan's windows come from the paper text: 21–25 Dec and 2–6 Jan. Both will be reported.

### 2026-10-07: operational details for C7 (written before computing it)

- **Code reading.** `fig_s4.m` computes r only for BH2203 against tide:
  - window 25 Jan – 6 Feb, 15-min grid, linear interpolation, no filtering;
  - tide mean removed, timestamps shifted by −2.5 h;
  - the "with lag" r adds one more 15-min step (total −2.75 h).

  We reproduce exactly that and compare it with r = 0.965 / 0.970 (pre-registered ±0.02).
- **BH2201/BH2202 (pre-registered rule).** Period III, from 14 Jan to the end of each record, on the same 15-min grid. Water level minus a centred 25 h running mean, against the tide as in the code (mean removed, −2.5 h).
  - **Amplitude** = half the daily range (max − min) of the filtered level, median over days with complete data.
  - **Amplitude ratio** = OLS slope of filtered level on tide.
- **Code window (reported, not labelled).** BH2201/BH2202 against tide over 13–25 Jan, as plotted in SI Fig. 4b–c, with no correlation in the code. Computed the same way as the code's BH2203 r.
- **Lag scan and clock check.** r of each borehole against the raw tide timestamps for shifts of −6 h to +6 h in 0.25 h steps. If the tide file is Syowa local time (UTC+3), the best shift for BH2203 should be close to −3 h, minus any small physical lag.

### 2026-10-07: C7 post-hoc readings (written AFTER seeing the C7 results)

- **Windows.** Pre-registered labels stand. Over 14 Jan to the end of each record, BH2201 and BH2202 show no correlation with the tide: r = 0.09 and −0.17. The phases the paper describes separately dominate that window (BH2202's rise on 22 Jan; BH2201's oscillations from 29 Jan). The same paper-text windows already defined for C1 (BH2201 to 28 Jan, BH2202 to 21 Jan) are reused, not new ones.
- **Clock check.** The IOC Sea Level Station Monitoring Facility mirror of the Syowa gauge (station `syow`, UTC) was added to `01_data_download.py` to measure the deposit tide file's clock offset.
