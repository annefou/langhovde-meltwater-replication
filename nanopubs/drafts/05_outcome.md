# 05 — FORRT Replication Outcome

> Fields from the live template `https://w3id.org/np/RA2zljn0Nw9SadppOyxZoh-_Rxosslrq-vYG-p9SttnJE` (`template_fields("05_outcome")`, source: live, 2026-10-07): outcome, label, study, repo, date, validationStatus, conclusion, evidence, confidenceLevel, limitations. The three text fields have no length cap on the live template.
>
> Every number below is read from `results/claims_table.csv` (Arm A, reproduction) and `results/arm_b_table.csv` (Arm B, replication). Both are produced by `pixi run snakemake --cores 1` and judged against the tolerances pre-registered in `ANALYSIS_PLAN.md`. **Draft for Anne to review.** The validation status and confidence level are proposals.

## Field-by-field draft

<!-- field: outcome -->
### Short URI suffix for outcome ID (text input, required)

```
langhovde-meltwater-acceleration-outcome-01
```

<!-- field: label -->
### Plain-text label for the outcome (text input, required)

```
Reproduction and partial replication of meltwater-driven acceleration at Langhovde Glacier (Sugiyama et al. 2026)
```

<!-- field: study -->
### Choose study (search/select, required)

URI of the Replication Study published in step 04, from `nanopubs/PUBLISHED.md`. The wizard fills this in itself.

```

```

<!-- field: repo -->
### Repository URL (text input, required)

Zenodo **version DOI** of the release the results came from (Phase 4; recorded in `CITATION.cff` at release).

```
https://doi.org/{{ZENODO_VERSION_DOI}}
```

<!-- field: date -->
### Choose completion date (text input, required)

`build-chain-draft` takes this from `date-released` in `CITATION.cff`, which the release sets, so the published date is the release date. The value below is the date the analysis was completed.

```
2026-10-07
```

<!-- field: validationStatus -->
### Choose validation status (dropdown, required)

Maps to the CiTO intention in step 06: PartiallySupported → `qualifies`.

- [ ] contradicted
- [ ] inconclusive
- [ ] not tested
- [x] partially supported
- [ ] validated

<!-- field: confidenceLevel -->
### Choose confidence level (dropdown, required)

Proposed: high. The reproduction is exact (the published Fig. 3 curves are matched to within 0.0002 m d⁻¹) and mostly agrees with the original. The qualifications concern scope and reporting, not contrary evidence.

- [x] high - Strong evidence, mostly agrees with original
- [ ] low - Limited evidence, significant disagreement
- [ ] moderate - Adequate evidence, partial agreement
- [ ] very high - Extensive evidence, high agreement with original
- [ ] very low - Minimal evidence, major disagreement

<!-- field: conclusion -->
### Describe the overall conclusion about the original claim (textarea, required)

```
The authors' deposited data, processed with our own Python code, reproduce the paper's central observations. During the rain and melt event of 2–6 January 2022, basal water pressure at BH2201 rose by 20.2 m to 51.0 m a.s.l. (97.1% of flotation), ice speed rose by 12.5% at GNSS1 and 11.1% at GNSS2, and the GNSS1 speed peak came 2 h before the pressure peak. During the December warm spell, speed rose by 22.7% (GNSS1) and 21.8% (GNSS2), and the grounded station rose by 126 mm while the floating station stayed within 3 mm. Independent data support the setting: satellite melt flags and Sentinel-2 surface water during the December event, an atmospheric river during the January event, and Japan Meteorological Agency records confirming that rain is rare at Syowa and that summer 2021/22 had a below-average positive degree-day sum.

The headline claim is partially supported. It rests on one fully instrumented event at one site in one season: basal pressure was measured only for the January event. The reported 10–20% speed-up holds only with the 12 h smoothing used to make the published figures, whereas the Methods state 1 h; with 1 h, the same events give 44–72%. Two ranges stated in general terms ("93–97% of flotation", "9–44 m" head difference) are not reproduced over the whole record: the first holds for the January event, and the upper bound of the second is not reached in any window we could define from the text. No independent dataset can confirm the speed-up: satellite image-pair velocities cannot resolve it.
```

<!-- field: evidence -->
### Describe the evidence that supports your conclusion (textarea, required)

```
Reproduction (deposited data, doi:10.17632/8wvtxg53ry.1; tolerances pre-registered before analysis):
- Processing: the two MATLAB functions missing from the deposit were rebuilt and identified against the authors' own fig3.eps. A Gaussian local linear regression with sigma = 12 h reproduces every plotted speed curve to 0.00004–0.00007 m/d RMS and the uplift curve to 0.06 mm RMS; 11 h and 13 h are about 9 times worse.
- C2 pressure event: pre-event level 28.5–32.6 m (paper 29–33 m); peak 51.0 m at 23:07 UTC on 3 January (paper 51 m, 97%); rise 20.2 m (paper 20 m); drop of 7.9 m within 1 h (paper about 10 m). Decline over 10 days: 24.0 m measured from 1 h after the peak, 33.1 m measured from the peak (paper about 30 m).
- C1: 92.5–97.1% of flotation during the January event (paper 93–97%). Mid-January levels were 89.5–91.9% (BH2202) and from 90.1% (BH2201).
- C3 speed-up (12 h, local baseline, observed data): +22.7% and +12.5% at GNSS1, +21.8% and +11.1% at GNSS2 (paper 10–20%). The 95th percentile of speed fluctuations outside the events is 2.1–2.4%. With 1 h smoothing: +44% to +72%, against fluctuations of 15.6–28.3%.
- C4 uplift: 126 mm at GNSS1 in December (paper 120 mm; 90 mm of it observed before the data gap); 10 mm in January (paper about 10 mm); 3 mm at the floating GNSS2.
- C6: GNSS1 speed peak 2 h before the BH2201 pressure peak; 1–15 h before it at both stations and every smoothing bandwidth.
- C7: BH2203 against tide, r = 0.965 and 0.970 (paper 0.965 and 0.970). Grounded boreholes before their late anomalies: r = 0.70 (BH2201) and 0.91 (BH2202), amplitude ratio 0.92 and 0.87 m of water per m of tide. The deposit's tide file is Syowa local time (UTC+3; r = 0.99993 against the IOC record), and the boreholes respond about 15 min after the gauge.
- C8: head difference BH2201 − BH2203 of 7.6–122.9 m over the common record, and 7.6–58.4 m before BH2201 rose above flotation (paper 9–44 m). Partially reproduced: the lower bound matches; the window behind the upper bound is not stated.
- C9: positive degree-day sum 10.6 and 18.18 °C d (paper 10.6 and 18.2); no trend (p = 0.65); 29.8 mm of rain on 2 January (paper about 30 mm).

Replication (independent data):
- JMA Syowa weather summaries 1990–2026: all seven of the authors' rain events confirmed; mean interval 4.4 years; no trend (p = 0.79).
- JMA hourly pressure: removing measured air-pressure variations shifts water levels by −0.32 to +0.23 m and changes no label.
- AMSR 10 km melt flags: melt on 22–24 December and 3–6 January. Sentinel-2: surface water fraction near GNSS1 of 3.2% on 20 December, against 0.6% on 13 December.
- Atmospheric-river catalogue (Favier 2025, doi:10.5281/zenodo.17165410): AR days 2–5 January, none in the December event.
- ERA5 at the glacier: 2021/22 positive degree-day sum below the 1989/90–2025/26 median (32nd percentile).
```

<!-- field: limitations -->
### Describe what limits the conclusions of the study (textarea, optional)

```
- Sample size: one glacier, one season, two GNSS stations, and one speed-up event with basal pressure data. The abstract's "periods of intensive melting and rain" covers two events, but pressure exists for one.
- Smoothing: the Methods state a 1 h filter; the published figures use 12 h. The size of the reported speed-up depends on this choice.
- Interpolation: the December speed peak at GNSS1 ("peaked on 24 December", "similar or even greater acceleration") lies in a spline-filled data gap. Observed data show a speed-up similar to GNSS2's, not greater.
- No independent speed data: ITS_LIVE had 25 valid image pairs out of 155, none shorter than 8 days, with 0.44 m/d RMS against GNSS at GNSS1. The authors' raw GNSS, needed to reprocess positions kinematically as Reviewer 1 suggested, is embargoed at NIPR ADS (A20220506-004).
- Scope of stated ranges: "93–97% of flotation" fits the January event, not the whole record. The 9–44 m head difference is reproduced at its lower bound only; the paper does not state its window. The 10-day decline matches only if measured from the peak.
- Rain frequency: the seven events are December–January only. JMA also records rain on 2 February 1997 and 4 February 2018, the latter contradicting "the last recorded rain at Syowa Station was in December 2017".
- Climate context: 2021/22 had more December–January satellite melt days than the median (7 vs 0 at 25 km, 8 vs 2 at 10 km), and 13 December–January atmospheric-river days (95th percentile of 42 summers; maximum 14). These do not contradict the low positive degree-day sum but qualify the inference that meltwater is usually more abundant than in 2021/22.
- Untested: freshwater at the bed (CTD), borehole video, drone imagery, ocean or buttressing changes. Measured air pressure from the on-glacier station is embargoed; the independent Yukidori Zawa station was not retrievable by script. ERA5 at this coastal cell runs 2.3 °C colder than the glacier station and shows a step at its September 2007 change of sea-surface forcing, so it was not used for trends.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
