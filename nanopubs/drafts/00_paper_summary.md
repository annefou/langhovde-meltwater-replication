# Paper summary

> This is a working scratchpad for the paper-analysis phase. Its content feeds the Quote / AIDA / Claim drafts; it is not itself a nanopub.
>
> **Verification note.** Every quotation below was checked with `verify_quote` (forrt-research MCP) against the local PDFs on 2026-10-06:
> - `paper/sugiyama-2026.pdf`, SHA-256 `493bbafd6e92f24b0ebfb384346d67a71510950c9b79edf12618af95c5560a3b`, 9 pages
> - `paper/supplementary/41467_2026_72724_MOESM1_ESM.pdf` (SI), SHA-256 `7dd7390f694ceedb07deaa1ac787e045adb644acd6d3dad3386f18dd4d3e293d`
> - `paper/supplementary/41467_2026_72724_MOESM6_ESM.pdf` (Peer Review File), SHA-256 `5004f01b7713732d9d837810ae9a099f662973d8c890e57ee5d3e07b3bc7bd99`
>
> Verdicts: **N** = `normalized`; **WI** = `whitespace_insensitive`. WI means pypdf split or merged words at line breaks; each WI quote was also checked against `pdftotext` output. **E** = `exact`. Page numbers are the PDF page numbers, which match the printed article pages. Any statement **not** quoted is labelled as a reading of a figure or as unverified.

**Reference paper:** Acceleration of an Antarctic outlet glacier driven by surface meltwater input to the base

**DOI:** 10.1038/s41467-026-72724-x (resolves to nature.com; checked 2026-10-06)

**Journal:** Nature Communications (2026) 17:6102. Received 25 October 2025, accepted 20 April 2026. Licence CC BY-NC-ND 4.0: do not adapt the paper's figures.

**Authors:** Shin Sugiyama (Institute of Low Temperature Science and Arctic Research Center, Hokkaido University; corresponding author), Ken Kondo (Graduate School of Environmental Studies, Nagoya University), Masahiro Minowa (Institute of Low Temperature Science, Hokkaido University), Akira Watanabe (Marine Works Japan Ltd.). Field campaign: 63rd Japanese Antarctic Research Expedition (JARE63).

**Year:** 2026

**Data and code:** Mendeley Data, doi:10.17632/8wvtxg53ry.1 (resolves to data.mendeley.com/datasets/8wvtxg53ry/1). The paper cites it as ref. 71, with the year printed as "(2021)" (p. 9, WI):
> Sugiyama, S., Kondo, K., Minowa, M. & Watanabe, A. Field data from Langhovde Glacier and MATLAB code for plotting, Mendeley Data, V1 https://doi.org/10.17632/8wvtxg53ry.1 (2021).

Code availability says the deposited code is for plotting only ("The code used for plotting the figures is deposited and available at Mendeley Data").

## Headline claim

Abstract, p. 1. Verified WI: pypdf joins "of" and "grounded" across a line break; pdftotext shows the normal space. 93 characters, under the 500-character cap (`template_fields("01_quote")` regex `[\s\S]{5,500}`).

> Our in-situ measurements confirm meltwater-driven acceleration of grounded ice in Antarctica.

This is sub-claim C5, the causal headline. It rests on C1–C4 and C6. Alternative candidates are listed in `01_quote.md`.

## Sub-claims C1–C9: headline numbers with verbatim support

| # | Sub-claim | Page | Verbatim support (verdict) |
|---|---|---|---|
| C1 | Basal water pressure close to overburden | p. 1 (abstract) | "Borehole measurements revealed that the subglacial water pressure exceeded 90% of the ice overburden and the pressure elevated during periods of intensive melting and rain." (N) |
| C1 | 93–97% of flotation at BH2201/02 | p. 5 | "Subglacial water pressure at BH2201 and BH2202 was close to the ice overburden pressure (93–97% of flotation), a similar condition to those reported at large ice streams in West Antarctica." (WI) |
| C2 | Pre-event level | p. 4 | "After the installation of the pressure sensor at the bottom of borehole BH2201 on 31 December, the borehole water level was 29–33 m above sea level (a.s.l.) until 2 January." (WI) |
| C2 | Pre-event fraction | p. 4 | "These water levels corresponded to 93–94% of the flotation level, i.e., the subglacial water pressure was equivalent to 93–94% of the ice overburden pressure." (WI) |
| C2 | 3 Jan peak | p. 4 | "On January 3, the water level rose progressively by 20 m and peaked at 51 m a.s.l. (97% of the flotation)." (N) |
| C2 | Decline | p. 4 | "The water level dropped by ~10 m within an hour and gradually decreased ~30 m over the following 10 days." (N) |
| C2 | Speed-up with pressure rise | p. 4 | "The second speed-up event coincided with an increase in the subglacial water pressure (Fig. 3b)." (N) |
| C3 | Size of the speed-up | p. 1 (abstract) | "Coinciding with these events, ice speed increased by 10–20% and the surface rose by ~0.1 m." (WI) |
| C3 | Period I timing | p. 3 | "Following a period of good weather with daily maximum temperatures of about 5 °C, ice speed increased and peaked on 24 December 2021 (Period I in Fig. 3a, c)." (N) |
| C3 | Period I size | p. 3 | "The peak speed at GNSS2 was approximately 20% faster than the background speed, and a similar or even greater acceleration was observed at GNSS1." (N) |
| C3 | Period II timing | p. 3 | "The second speed-up occurred on 2–6 January 2022 (Period II in Fig. 3a)." (WI) |
| C3 | Speed error | p. 7 | "The relative error in the computed hourly ice speed was 7–12% for the mean speed at GNSS1, and the actual error after the smoothing procedure was smaller than this estimate." (WI) |
| C4 | Period I uplift | p. 3 | "During the first event from 21 to 25 December, GNSS1 showed an upward displacement of 120 mm (Fig. 3a)." (WI) |
| C4 | Period II uplift | p. 3 | "A smaller uplift (~10 mm from 3 to 5 January) was observed during the second event." (N) |
| C4 | No uplift on floating ice | p. 3 | "Importantly, no noticeable vertical displacement was observed at GNSS2, where ice was afloat." (N) |
| C4 | Interpretation of the uplift | p. 5 | "The absence of uplift at GNSS2 on the floating ice and the coincidence of the uplift with the acceleration both strongly suggest that the uplift was due to the separation of ice from the bed by pressurized subglacial water." (N) |
| C4 | Ruling out vertical strain | p. 5 | "The magnitude of the acceleration was similar at GNSS1 and GNSS2, thus significant change is unlikely in the vertical strain rates." (WI) |
| C5 | Headline (abstract) | p. 1 | see above (WI) |
| C5 | Headline (Discussion) | p. 4 | "Our subglacial measurements and in-situ GNSS data confirm the influence of surface meltwater on subglacial pressure and its impact on glacier speed in Antarctica." (N) |
| C5 | Hedged form | p. 4 | "The GNSS and borehole data, together with visual observations of glacier surface conditions, strongly suggest that surface meltwater penetrated the glacier to the base and enhanced basal sliding (Supplementary Fig. 1)." (N) |
| C6 | Timing of pressure peak vs speed peak | p. 4 | "The timing of the pressure peak broadly coincided with that of the ice speed peak (Fig. 3a, b)." (N) |
| C7 | Period III onset | p. 4 | "Beginning 14 January, the water level in borehole BH2201 exhibited semidiurnal variations with typical amplitudes smaller than 1 m (Period III in Fig. 3b)." (N) |
| C7 | Correlation with tide | p. 6 | "The semidiurnal pressure variations at BH2201 and BH2202 were correlated with ocean tides recorded at Syowa Station (Fig. 3b and Supplementary Fig. 4a–c)." (WI) |
| C7 | Inference | p. 6 | "Therefore, the glacier base at boreholes BH2201 and BH2202 was hydraulically connected to the sub-shelf cavity (Supplementary Fig. 1)." (N) |
| C7 | Tide lag (SI) | SI p. 3 | "The inset in (d) shows that the correlation improves by introducing a time lag of 0.25 hr, i.e. BH2203 level (t) v.s. tide (t+0.25 hr)." (N, SI PDF) |
| C8 | Head difference | p. 6 | "Despite the hydraulic connection, the water level in BH2201 was higher than the level in BH2203 by 9–44 m." (WI) |
| C8 | Hydraulic gradient | p. 6 | "Assuming a distance from BH2201 to the grounding line of 1 km, the difference in the hydraulic heads corresponds to hydraulic gradients of 0.9–4.4 × 10−2." (WI; the exponent is a superscript −2 in the PDF) |
| C9 | PDD | p. 5 | "The sum of positive degree days (PDD) during the 2021/22 summer period (December and January) (10.6 °C d) was 40% smaller than the mean from 1989/90 to 2025/26 (18.2 °C d) (Supplementary Fig. 3), suggesting that surface meltwater on Langhovde Glacier is generally more abundant than we observed in 2021/22." (WI) |
| C9 | Rain frequency | p. 5 | "Liquid precipitation has been reported seven times since December 1989 (Supplementary Fig. 3), i.e., rainfall occurs approximately every five years." (N) |
| C9 | No trend | p. 5 | "From 1989 to the present, no significant trend is observed in summer mean temperature, PDD, or the frequency of liquid precipitation (Supplementary Fig. 3)." (N) |
| C9 | Period II rain | p. 3 | "Approximately 30 mm of rainfall was recorded on 2 January (Fig. 3c)." (E) |
| C9 | Previous rain | p. 3 | "Liquid precipitation is unusual in this region, i.e., the last recorded rain at Syowa Station was in December 2017." (N) |

**Numbers read from figure images (not text, so `verify_quote` cannot check them):**
- SI Fig. 4d gives r = 0.965 (p < 0.001) for BH2203 against tide, and r = 0.970 (p < 0.001) with the 0.25 h lag (inset). **No r or p is shown for BH2201/BH2202 against tide** (SI Fig. 4b–c are a scatter plot and a time series without statistics). So the C7 claim for the grounded boreholes rests on visual correlation.
- SI Fig. 6f: the GNSS1 Period I speed peak (about 0.33 m d⁻¹, against about 0.23 m d⁻¹ afterwards) falls in the **dashed, spline-interpolated** segment. The solid, observed part peaks at about 0.29 m d⁻¹ before the gap. These are approximate eyeball readings; recompute them from the deposit.
- SI Fig. 3 shows 7 blue rain-event lines between 1989/90 and 2025/26, consistent with "seven times".

## Methodology summary

- **Field setting and time windows.** Hot-water drilling and surface measurements on Langhovde Glacier, December 2021 – February 2022. GNSS ran "from 19 December 2021 to 6 February 2022" (p. 6, WI). Periods, from the text: **Period I** = warm spell, speed peak on 24 Dec 2021, GNSS1 uplift 21–25 Dec. **Period II** = speed-up 2–6 Jan 2022, ~30 mm rain on 2 Jan, pressure peak on 3 Jan. **Period III** = semidiurnal pressure variations "Beginning 14 January". The text gives no end date for Period III; the grey band in Fig. 3 / SI Fig. 4a runs to early February (figure reading).
- **Boreholes.** BH2201: bed at 552 m depth, "440 m below sea level" (p. 3). BH2202: ~5 m away, bed at 552.5 m. These two are grounded, ~4 km from the front. BH2203 and BH2204 are 3.2 and 3.0 km from the front, under floating ice with a 3 m and 6 m seawater layer. Pressure sensors: Valeport miniIPS at BH2201 (inside a ploughmeter, installed 31 Dec), Geokon 4500S at BH2202 (installed 7 Jan) and BH2203 (the text gives no installation date). Accuracy/resolution ±1 kPa/0.1 kPa (BH2201, BH2203) and ±7.5 kPa/2 kPa (BH2202).
- **GNSS processing.** Dual-frequency receivers (Enabler GEM-1/GEM-2) sampling at 1 s on 2 m poles, differenced against a reference station on a side moraine: "GNSS processing software RTK-LIB (https://www.rtklib.com/rtklib.htm) was used to perform static differential carrier-phase positioning with a broadcast ephemeris to obtain three-dimensional coordinates of the stake positions every 15 min with an accuracy of 3–5 mm (ref. 70)." (p. 6, WI)
- **Smoothing and speed.** "We computed horizontal ice speed after smoothing the time series of x-, y- and z- coordinate data with a Gaussian filter having a" (p. 6, WI) / "bandwidth of 1 h (Supplementary Fig. 6). This bandwidth was chosen so that the mean deviation of the data from the smoothed curve was equivalent to the positioning accuracy." (p. 7, N). The sentence crosses the page break, so it was verified in two halves; the whole sentence returns `not_found` only because the running header sits in the middle of it. Gaps: "Data from GNSS1 was unavailable for the periods of 24–25 December 2012, 12–19, and 22–26 January 2022 because of device failure." (p. 7, WI) and "Ice speed during the period was computed by estimating the coordinates with spline interpretation (Supplementary Fig. 6)." (p. 7, N). "Background speed" is never defined.
- **Pressure to water level to overburden.** "The pressure data were corrected for atmospheric pressure, which was recorded every hour at an automatic weather station located ~2 km downglacier of BH2201 and BH2202 (Fig. 1b)." (p. 6, N). Water levels are in m a.s.l. and expressed as % of the flotation level at BH2201/02. Flotation level (Eq. 1, p. 7): z_f = z_b + (z_s − z_b)·ρ_i/ρ_s with ρ_i = 910 and ρ_s = 1025 kg m⁻³. The text gives no geoid or sea-level reference; DISCOVERY.md takes the constants from `fig3.m` (not verified here).
- **Tide correlation.** Syowa Station tide gauge data, 30 s intervals, from the Japan Coast Guard Hydrographic and Oceanographic Department. The correlation is shown in SI Fig. 4. The only lag reported is 0.25 h, for BH2203.
- **Weather and PDD.** On-glacier AWS (Vaisala WXT530, 54 m a.s.l.): "The sensor recording air temperature and liquid precipitation every 5 min was installed 2 m above the ice surface and connected to a data logger (Campbell Scientific, CR1000X)." (p. 7, N). Long-term context comes from Syowa Station daily mean/min/max temperature and the rain record from JMA. PDD is summed over December–January. The paper gives no PDD formula (daily mean > 0 °C is the likely convention, but it is not stated).
- **Sample size.** One glacier, one field season, two GNSS stations (one grounded, one afloat), one grounded borehole pair with pressure records (BH2201 from 31 Dec, BH2202 from 7 Jan), one floating-ice reference borehole (BH2203). **Two speed-up events, of which only one (Period II) has pressure data.** The climate context is 37 summers at Syowa (1989/90–2025/26).

## Headline numbers the replication will compare against

C1: 93–97% of flotation. C2: 29–33 m a.s.l. (93–94%) until 2 Jan → +20 m to 51 m a.s.l. (97%) on 3 Jan → −10 m within 1 h → −30 m over 10 days. C3: +10–20% speed; Period I GNSS2 ~20% above background, GNSS1 "similar or even greater"; Period II 2–6 Jan; error 7–12%. C4: +120 mm at GNSS1 (21–25 Dec), ~10 mm (3–5 Jan), none at GNSS2. C6: pressure and speed peaks "broadly coincided". C7: semidiurnal from 14 Jan, amplitude < 1 m; BH2203 r = 0.965 / 0.970 with a 0.25 h lag (figure). C8: head difference 9–44 m, gradient 0.9–4.4 × 10⁻² over 1 km. C9: PDD 10.6 vs 18.2 °C d (40% lower); 7 rain events since Dec 1989; no significant trend.

## Where the PDF disagrees with, or refines, DISCOVERY.md

1. **Smoothing bandwidth.** The PDF says **1 h** (pp. 6–7) and gives a rationale (mean deviation ≈ positioning accuracy). DISCOVERY.md says `fig3.m` uses `h = 12/24` (12 h). I could not check the code; the deposit is not downloaded.
2. **Atmospheric-pressure correction.** The PDF says the correction used air pressure "recorded every hour" at the AWS ~2 km downglacier. The Methods AWS paragraph (p. 7), however, lists only air temperature and liquid precipitation for the WXT530. The paper is ambiguous about where the pressure series came from. The PDF does not mention the constants (9.2 dbar; 0.089) that DISCOVERY.md reports from the code (code not checked).
3. **"December 2012" typo.** Confirmed in the PDF (p. 7): "24–25 December 2012", obviously meaning 2021.
4. **Tide lag.** DISCOVERY.md says "paper applies a 2.5 h lag". The PDF/SI give a **0.25 h** lag, applied only to **BH2203** (SI Fig. 4d inset), and the main text mentions no lag. Either DISCOVERY.md has a decimal slip or the code uses a different value. Check `fig3.m` / `fig_s4` code.
5. **AWS sampling.** The PDF says **5 min**. DISCOVERY.md says the deposited `aws211219_220206.dat` is **10 min**. Fig. 3c plots "Hourly" and daily temperature. Record this as a deposit vs paper difference once checked.
6. **GNSS2 coverage.** The PDF says both GNSS ran 19 Dec – 6 Feb and lists device-failure gaps for **GNSS1 only**. DISCOVERY.md says `LG04` (GNSS2) covers only 23 Dec – 27 Jan. If so, GNSS2's coverage is not stated in the paper. Check against the deposit.
7. **C7 statistics.** DISCOVERY.md says the pressure "correlate[s] with the Syowa tide". The PDF reports r only for **BH2203**; no correlation coefficient is given for BH2201/02. The grounded-bed connection claim rests on visual agreement plus the BH2203 calibration.
8. **Period I GNSS1 peak lies in the interpolated segment.** From SI Fig. 6f (visual reading), the GNSS1 Period I maximum is in the dashed spline section. This strengthens DISCOVERY.md's gap point 4: "similar or even greater acceleration ... at GNSS1" depends on the interpolation.
9. **Ice thickness constant.** The PDF gives bed depths of 552 m (BH2201) and 552.5 m (BH2202) with ±1 m accuracy, and the bed at "440 m below sea level". DISCOVERY.md quotes `z_i = 551.31 × 0.91` and a bed elevation of −436.1 m from the code. These differ by ~0.7 m in thickness and ~4 m in bed elevation (possibly a geoid/ellipsoid offset). Check against the code; small, but it moves the % of flotation.
10. **Data citation year.** Ref. 71 prints "(2021)". DISCOVERY.md says the dataset was published 2026-05-01. Cite the DOI and take the date from the Mendeley record.
11. **SI typo.** The SI Fig. 3 title reads "1989/20 to 2025/26" (verified, N), meaning 1989/90.
12. **Reviewer identities.** The paper names Douglas Benn, Samuel Doyle and Ian Willis as reviewers. In the Peer Review File only Reviewer #3 self-identifies ("Review by Ian C Willis"). Nothing in the PDFs says which of Benn or Doyle is R1 or R2, so don't attribute R1/R2 comments to a named person.
13. **Abstract sentence the authors said they kept.** In reply to R2 the authors wrote that they would keep the first abstract sentence ("Glaciers flow faster when the base is lubricated by meltwater penetrating through the ice"). The **published** abstract does not contain that sentence; it starts "Despite its importance...". The R2 efficient-drainage caveat is therefore neither stated nor rebutted in the published abstract.
14. **Other typos (harmless):** "spline interpretation" (= interpolation, p. 7 and SI Fig. 6); drone sites "BH2021 and BH2022" (= BH2201/BH2202, p. 7); section heading "Subgacial"; "Laghovde" (p. 6).
15. **C2 wording.** DISCOVERY.md matches the PDF. The "dropped ~10 m within an hour" is in the text; the abstract's "periods" (plural) overstates, because only Period II has pressure. R3 says this plainly (see Peer Review notes in the report).

## Borehole names: field files vs publication

The deposit is Mendeley version 1, the only version (API checked 2026-10-06). The name differences are not a version mismatch: the data files keep the **field names** (coordinate file dated 2022-02-12, geometry file dated 2022-05-21), and `fig1/fig1.m` assigns the **publication names** only when it draws the labels. After review, the authors relabelled Fig. 1 in the code, not in the data: Reviewer 3 wrote "Many of the boreholes are incorrectly labelled in (c)."; the authors replied "Corrected (Figure 1c)." (Peer Review File).

| Publication name | `langhovde2022coordinate220212.dat` | `borehole_geometry220521.dat` | Evidence |
|---|---|---|---|
| BH2201/02 (grounded, at GNSS1) | `BH2201` (2021-12-25) | `BH2203` (bed −436.1 m) | Same coordinates (~4 m apart); `fig1.m` labels coordinate row 1 "BH2201/02"; bed matches `z_bed1 = -436.1` in `fig3.m` |
| BH2203 (below grounding line) | `BH2205` (2022-01-24) | `BH2205` (ice base −394.9, seabed −398.2) | `fig1.m` labels coordinate row 3 "BH2203"; paper: ice 474 m and cavity 3 m at BH2203, file gives 79.449 + 394.9 = 474.3 m and 3.3 m; `z_bed3 = -398.1`; BH2203 pressure record starts 24 Jan |
| BH2204 | `BH2204` (2022-01-22) | `BH2204` | Paper: 450 m and 6 m; file gives 449.5 m and 5.8 m |

Using the publication names, the overburden thickness constant `551.31` in `fig3.m` is surface 115.167 m minus bed −436.1 m (551.27 m) at BH2201/02. The paper's "552 m" is the drilled depth. The labels for the older holes (2012/2018) are also reassigned in the Fig. 1d cross-section (for example, geometry row `BH1801` is drawn as "BH1804"). Those holes feed only the thermistor panels, not claims C1–C9, so this is noted here and not resolved. **Rule for the notebooks:** always use publication names, mapped as in this table.

## Replication design choice

- [ ] **Reproduction Study** — direct reproduction: same methodology, same tools.
- [ ] **Replication Study** — replication with different methodology or conditions.
- [x] **Reproduction/Replication Study** — both.

**Justification.** The deposit (Mendeley doi:10.17632/8wvtxg53ry.1) holds the processed GNSS positions, borehole pressures, AWS, tide and Syowa temperature series behind Fig. 3 and SI Figs. 3–6. It holds no runnable analysis code (plotting scripts only, per the Code availability statement). **Arm A (Reproduction)** therefore recomputes C1–C4 and C6–C9 from the deposited data with our own Python code. It adds sensitivity tests where the paper leaves choices open or inconsistent: smoothing bandwidth (1 h in the text vs 12 h reported in the code), the "background speed" definition, the observed vs spline-interpolated parts of the GNSS1 record, and the atmospheric-pressure correction. **Arm B (partial Replication)** tests the parts that independent data can reach: weather forcing and rain/melt frequency (JMA Syowa original records, ERA5, an atmospheric-river catalogue, which also answers R1's unaddressed reanalysis request), Period I surface melt evidence (Sentinel-2/Landsat), and the air-pressure correction (JMA/ERA5). The core link (pressure → uplift → speed) has no independent counterpart, because no other subglacial pressure record exists for Langhovde. That link stays a reproduction, and each outcome must be labelled reproduction or replication.

## Geographical coverage

**Spatial: yes.** A single study area, Langhovde Glacier (Lützow-Holm Bay, East Antarctica), quoted verbatim in `09_geo_coverage.md`. Syowa Station is a second named place, but only as a data source (tide gauge, climate record). It is drafted there as an **optional** Location B for the user to keep or delete. The text states no coordinates. Fig. 1a/b carries graticule and easting/northing labels, but those are figure annotations, not stated coordinates, so no WKT is drafted.

## Notes for downstream drafts

- **AIDA atomicity:** the abstract bundles speed (C3) and uplift (C4). Split them if either becomes an AIDA. The headline (C5) is causal and n = 1 for the fully instrumented event; scope the AIDA/Claim wording accordingly.
- **Scope language:** pressure exists for **one** event (Period II). Period I's melt is inferred from air temperature and observation ("Intensive ice melting was observed on the glacier during the relatively warm conditions, which lasted about five days", p. 3; not run through `verify_quote` separately).
- **Speed error (7–12%) is the same size as the 10–20% signal.** The Outcome should report the speed-up against that error and against fluctuations with no forcing.
- Use **"percentage points"** in prose when comparing % of flotation (DOMAIN.md style).
- Out of scope (not deposited): CTD freshwater result, borehole video, fauna, drone imagery.
