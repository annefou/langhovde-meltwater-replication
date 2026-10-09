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

### 2026-10-07: operational details for C3, C4 and C6 (written before computing them)

**Processing.**
- `gnss.process_track`: observed-only.
- `gnss.fill_gaps_spline`: the not-a-knot cubic spline of `fig_s6.m`, matching the published dashed curves to 0.00013 m/d and 0.2 mm.
- Bandwidths 1, 3, 6 and 12 h. Gap threshold 12 h. Differencing as in `AUTHORS_FIG3` at h = 12 h; centred at the other bandwidths.

**Windows.**
- Paper text (primary): Period I = 21 Dec 00:00 – 25 Dec 23:59 UTC; Period II = 2 Jan 00:00 – 6 Jan 23:59.
- Code shading (`fig3.m`), reported alongside: 22–27 Dec and 2–7 Jan.

**C3, speed-up.**
- Peak = maximum hourly speed in the window. Speed-up = 100 × (peak / baseline − 1).
- Baselines use observed-only speeds of the same station and bandwidth, with both event windows masked:
  - **B1:** median over the 3 days before the window start and the 3 days after the window end.
  - **B2:** median over the whole record.
  - **B3:** OLS line of speed against time, evaluated at the peak time.
  - **B4:** 7-day centred running median (at least 24 hourly values), evaluated at the peak time.
- **Primary label** (h = 12 h, B1, paper-text windows, observed-only): reproduced if all four station × period speed-ups lie in 7–23% (10–20% ± 3 percentage points).
  - Partially reproduced if this holds only with the spline fill, or only for some baselines, stations or periods.
  - Not reproduced if no station × period is in range under any baseline or gap handling at h = 12 h.
  - A station × period with no observed data in its window is reported as "no data", not counted as a failure, and noted.
- **Robustness:** for each of the 16 bandwidth × baseline combinations, the number of station × periods in range, observed-only and spline.
- **Signal vs noise:** hourly anomaly = speed / B4 − 1. The event peak anomaly is compared with the 95th percentile of anomalies outside both event windows, per station, at h = 12 h and h = 1 h.

**C4, uplift.**
- Uplift = maximum smoothed vertical displacement in the window minus the value at the window start (Period I GNSS1: 21 Dec 00:00; Period II: 3 Jan 00:00, the paper's "3 to 5 January").
- Observed-only Period I uses observed samples only. The part reached before the 24–25 Dec gap is reported separately.
- GNSS2: maximum minus minimum over the part of 21–25 Dec with data (from 23 Dec 15:00).
- Primary: h = 12 h. At h = 1 h the floating GNSS2 will also carry tidal motion; reported, not labelled.

**C6, timing.** Δt = time of the GNSS1 Period II speed peak (observed-only) minus the BH2201 pressure peak (3 Jan 23:07 UTC, from C2). Reproduced if |Δt| ≤ 24 h at h = 12 h. Δt is also reported for every bandwidth and for GNSS2.

---

# Arm B (replication with independent data)

Each Arm B test is pre-registered here before its data are downloaded in full. Labels: **replicated**, **partially replicated**, **not replicated**. Amendments follow the same rules as Arm A.

## B-rain: rain frequency at Syowa (C9), pre-registered 2026-10-07

**Why.** The seven rain events behind "Liquid precipitation has been reported seven times since December 1989" are hard-coded in `fig_s3.m`, as summer years 1991, 1996, 2004, 2009, 2013, 2018 and 2022. No rain record is deposited. Arm A could only check that the text matches this list.

**Source.** Japan Meteorological Agency, past weather data for Syowa (station 89532): monthly daily-value pages (`daily_s1.php?prec_no=99&block_no=89532`). For each day the page gives a daytime (06–18) and night-time (18–06) weather summary (天気概況). Times are Syowa local time (UTC+3), and days are counted in local time. Syowa has no precipitation-amount record, so the summaries are the only rain record. Scope: every month from December 1989 to March 2026. Fetch politely (one request per second) and cache in `data/raw/jma/`.

**Only inspected before this plan:** the pages for 1989-12, 1991-01, 2017-12 and 2022-01, to learn the layout. December 1989 has no summaries.

**Definitions.**
- **Rain day:** a day whose daytime or night-time summary contains 雨 (rain, including 霧雨, drizzle). This is the primary definition.
- **Sleet-only day:** contains みぞれ (sleet) but not 雨. Used for the sensitivity case "rain or sleet".
- **Rain event:** rain days separated by at most 2 days, merged into one event.
- **Season:** July–June, labelled by the year of its January (2017/18 → 2018), as in `fig_s3.m`.
- **Coverage:** a month counts as covered if at least 90% of its days have a summary. Report months without coverage. A season counts as covered if its December–February is covered.

**Tests and decision rules** (primary definition; sensitivity reported alongside):
1. **Which seasons had rain.**
   - Replicated if the covered seasons with at least one rain event are exactly the authors' seven, restricted to covered seasons.
   - Partially replicated if at least 5 of the authors' covered seasons have a rain event, or if the number of rain seasons is within ±2 of the authors' covered count.
   - Otherwise not replicated.
2. **"Approximately every five years."** Mean interval between consecutive rain seasons of 4–6 years.
3. **No significant trend in frequency.** Poisson regression of rain events per covered season on season year: p ≥ 0.05.
4. **"The last recorded rain at Syowa Station was in December 2017"** before 2 January 2022: no rain day between 25 Dec 2017 and 1 Jan 2022.

The JMA record is derived from the same station observations the authors cite. It is independent of the authors' extraction, not of the observing system.

### 2026-10-07: B-rain post-hoc reading (written AFTER seeing the results)

Test 4's pre-registered window (25 Dec 2017 – 1 Jan 2022) includes the first night of the January 2022 event (rain in the night of 1 Jan, local time, merged with 2 Jan). The pre-registered label stands. A post-hoc row reports the window with that event excluded, which isolates the one genuine extra rain day: 4 Feb 2018.
- **December–January restriction (post hoc).** All of the authors' seven events fall in December or January, and both events JMA adds (2 Feb 1997, 4 Feb 2018) fall in February. SI Fig. 3 is captioned "Summer (December and January)". A post-hoc row therefore restricts the events to December–January.

## B-pressure: measured air pressure in the borehole correction (C1, C2), pre-registered 2026-10-07

**Why.** The paper says pressures were corrected with hourly air pressure from the on-glacier station. The code subtracts constants instead (9.2 dbar for BH2201; 0.089 MPa for the Geokon sensors), and the station's pressure record is embargoed (`GAP_SOURCES.md` C). The constants (920 and 890 hPa) are well below Syowa's typical 985 hPa. That suggests they are sensor zero readings at deployment, sensor offset included, not a mean air pressure.

**Method.** Keep the code's constants for the offset and remove only the time-varying part of the air pressure:
- level_B = level_code − (p_air(t) − mean p_air over the record) / (ρ_w g), with ρ_w = 1000 kg m⁻³ and g = 9.81 m s⁻².
- p_air(t) is JMA Syowa hourly station pressure (`hourly_s1.php`, 31 Dec 2021 – 6 Feb 2022), converted from local time (UTC+3) to UTC and interpolated linearly to the logger times.
- Syowa is ~25 km from the boreholes. Synoptic pressure changes are coherent over that distance.

**Tests.**
- Recompute the C1 bounds and the C2 items with level_B.
- **Replicated** if every C1/C2 label is unchanged and no C2 value moves by more than 0.5 m. Partially replicated if any label changes.
- Report the range of the correction in metres.

## B-AR: atmospheric rivers during Periods I and II (reviewer question, context), pre-registered 2026-10-07

**Why.** Reviewer 1 asked whether the events were linked to atmospheric rivers and how often similar events occur. The authors answered with Syowa station data only. The paper makes no AR attribution, so this test is context and is labelled "reported", not replicated.

**Source.** Favier (2025), merged ERA5–MERRA-2 atmospheric-river catalogues at staffed Antarctic stations, doi:10.5281/zenodo.17165410 (CC BY 4.0), file for Syowa (AR days, 1980 to March 2022).

**Reported.**
1. AR days overlapping Period I (21–25 Dec 2021) and Period II (2–6 Jan 2022).
2. The number of December–January AR days in 2021/22, and its percentile among all December–January seasons in the catalogue.
3. The fraction of JMA rain events (B-rain, within the catalogue span) with an AR day within ±1 day.

## Remaining Arm B tests, pre-registered 2026-10-07 (before their data are downloaded in full)

**Access note.** The independent Yukidori Zawa / Langhovde AWS for 2021/22 (Kudoh et al. 2026, doi:10.17592/001.2026052101) is listed as public. Its files are served only through the NIPR ADS web application, and no scriptable download path was found. The AMRDC mirror holds metadata only, and the authors' own on-glacier record (A20220506-001) is embargoed. It is recorded as a gap. JMA Syowa and ERA5 replace it.

**Format checks done before this plan:**
- the Picard SSM/I file: daily 0/1 melt flag on a 25 km EPSG:3976 grid, 1979-04 to 2025-03, with 3–5 flagged cells out of 8,487 in winter;
- the AMSR2 10 km file size;
- the existence of a CDS API credentials file (not read).

### B-temp: temperature context from records independent of the authors' extract (C3 Period I, C9)
1. **PDD from the original JMA daily record** (`jma_syowa_daily.parquet`), with the authors' definition: the sum of positive daily means over December–January.
   - Replicated if 2021/22 is within ±0.5 °C·d of 10.6 and the 1989/90–2025/26 mean is within ±0.5 of 18.2, using seasons with complete December–January data.
2. **Period I warmth** ("daily maximum temperatures of about 5 °C"). JMA Syowa daily maxima and the deposit's on-glacier AWS daily maxima, 19–25 Dec 2021. Reported.
3. **ERA5 at the glacier.**
   - Data: hourly 2 m temperature, ERA5 single levels (doi:10.24381/cds.adbb2d47), at the grid cell nearest GNSS1, December–January 1989/90–2025/26.
   - Daily means from hourly UTC values; PDD as above.
   - Replicated "2021/22 below average" if the 2021/22 PDD is below the median. "No trend" if the OLS p ≥ 0.05.
   - Period I and II daily maxima reported.

### B-melt: satellite surface-melt flags (C3/C4 Period I, C9)
- **Products:** Picard SSM/I 25 km daily melt (cite Picard & Fily 2006, doi:10.1016/j.rse.2006.05.010) and the AMSR-E/AMSR2 10 km product from the same site, at the grid cell nearest GNSS1 (and nearest GNSS2, reported).
1. Melt flagged on at least one day of Period I (21–25 Dec 2021); same for Period II (2–6 Jan).
   - Replicated if flagged in at least one product. Not replicated if neither product flags melt.
   - A 25 km and a 10 km cell both mix glacier, rock and sea ice; this is stated with the result.
2. December–January melt days in 2021/22 against all December–January seasons in each product.
   - Consistent with C9 ("meltwater generally more abundant than we observed in 2021/22") if 2021/22 is below the median.

### B-velocity: satellite velocity feasibility (C3)
- **Source:** ITS_LIVE v2 image-pair velocities (Landsat 8/9, Sentinel-2, Sentinel-1; NASA MEaSUREs, open). All pairs with both acquisitions between 2021-12-01 and 2022-02-10, at the pixel containing each GNSS site, with their reported errors. Read via the ITS_LIVE v2 datacube (Zarr) or the granules, whichever is reachable.
1. **Agreement.** For each pair, the GNSS mean horizontal speed over the same interval (h = 12 h track; spline fill where needed, flagged). Report bias, RMS difference and correlation.
2. **Detectability of the Period I speed-up.**
   - Mean ITS_LIVE speed of pairs whose interval contains at least 3 days of 21–25 Dec, against pairs overlapping neither period.
   - Feasible if the difference exceeds twice its standard error and has the same sign as GNSS. Otherwise not feasible.
   - The paper's speed-up claim has no other independent test; a "not feasible" result is recorded as the gap.

### B-optical: Sentinel-2 surface water around GNSS1 (Period I melt)
- Sentinel-2 L2A scenes (Element84 Earth Search STAC) with at least 90% clear sky over a 2 km × 2 km box centred on GNSS1, from 10 Dec 2021 to 25 Jan 2022.
- NDWI = (B03 − B08) / (B03 + B08). Fraction of box pixels with NDWI > 0.25, the meltwater threshold on ice of Yang & Smith 2013.
- Reported: the fraction per scene. "Surface water detected in Period I" if the fraction on a Period I scene (20–25 Dec) is at least twice the fraction on the clear scene before (≤ 19 Dec) and above 1%.

### 2026-10-07: B-melt operational detail (before any AMSR value was seen)

The AMSR 10 km file has four flags: ascending and descending passes, each "filter" and "raw". Daily melt = 1 if either filtered flag is 1, NaN if both are missing. SSM/I has a single flag, which is used as is. The "December–January melt days" test needs at least 55 days per season.

### 2026-10-07: B-temp access (before the ERA5 values were seen)

A single CDS request for all years exceeded the CDS cost limit, and yearly requests were slow (about 2.5 min each in the queue). ERA5 is instead read from ECMWF's ARCO Zarr store (geo-chunked, CDS key as Bearer token) at the grid cell nearest GNSS1. Variable, months and years are unchanged; the 0.25° box became the single nearest cell, as the test specified.

### 2026-10-07: B-optical duplicate scenes (written after seeing the results)

The STAC search returns reprocessed duplicates of the same acquisitions. One item per acquisition is kept, the one with the latest processing baseline. The 20 Dec duplicates give water fractions of 0.042 and 0.032. Both satisfy the pre-registered rule against 13 Dec (≈0.007), so the label does not depend on this choice.

### 2026-10-07: B-temp ERA5 inhomogeneity (written AFTER seeing the ERA5 results)

The pre-registered ERA5 trend test gives p = 0.03 ("not replicated"), and that label stands. ERA5 PDD at the cell nearest GNSS1 drops in steps after 2007 (seasonal means 24.6 → 3.5 °C d between halves). ECMWF's ERA5 documentation records that SST/sea-ice forcing came from HadISST2 before September 2007 and from OSTIA after. A post-hoc row splits the record there and compares it with JMA Syowa over the same seasons. A second post-hoc row reports ERA5 against the deposit's on-glacier AWS during the field season.

### 2026-10-09: B-rain cross-check with NOAA ISD WMO present-weather codes (post hoc; written after the JMA results, before any ISD summer data were examined)

**Why.** JMA publishes the daily Syowa weather summaries only in Japanese. The same Syowa SYNOP reports are redistributed by NOAA's Integrated Surface Database (ISD, global-hourly, station 89532099999, NOAA open data on AWS), coded with WMO present-weather codes (`MW1`, "ww,quality"). They are an independent processing chain in an international, language-neutral format. The pre-registered B-rain labels (JMA) stand. ISD is reported as a cross-check.

**Inspected before this amendment:** column names; the share of reports carrying MW1 (41% in 2022; SYNOP omits ww when there is no significant weather); and MW1 values in July 2022 only.

**Definitions** (WMO code table 4677):
- **Rain report:** ww in 50–67 (drizzle, rain, freezing drizzle or rain) or 80–82 (rain showers). Primary.
- **Mixed report:** ww in 68, 69, 83 or 84 (rain or drizzle with snow), the counterpart of JMA's みぞれ (sleet). Used in the "rain or sleet" case.
- **Days and events:** reports are grouped into Syowa local days (UTC+3), the same days as JMA. Events, seasons, coverage and tests 1–3 are the same as the pre-registered B-rain definitions. A season counts as covered if each of December, January and February has reports on at least 90% of its days.
- **Agreement:** each JMA rain event is "confirmed" if ISD has a rain day within ±1 day. ISD events without a JMA event are listed.
