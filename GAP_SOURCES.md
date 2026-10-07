# Gaps and sources

Compiled on 2026-10-06 from the deposit itself (Mendeley [doi:10.17632/8wvtxg53ry.1](https://doi.org/10.17632/8wvtxg53ry.1), v1, the only version), the paper, the Peer Review File, and two rounds of web research. Every DOI below resolved (HTTP 302 at doi.org). Quotes were copied from the fetched source, not recalled. Sources that could not be fetched are listed under **Unconfirmed** and are not used.

Status: **closed** (answered, with a checkable source) · **partial** (precedent or proxy only) · **open** (needs the authors) · **gap** (cannot be filled; record it as a limitation).

## A. Method gaps (Arm A, reproduction)

| # | Gap | Status | Source and evidence |
|---|---|---|---|
| A1 | Smoothing: the paper says a 1 h Gaussian filter; `fig3.m` and `fig_s6.m` call the missing `local_regression(t, x, ti, h)` with `h=12/24` (days, so 12 h) | **partial / open** | Same group, same chain: Sugiyama et al. 2025, *The Cryosphere* 19, 525–540, [10.5194/tc-19-525-2025](https://doi.org/10.5194/tc-19-525-2025), p. 527: "Horizontal ice speed was computed by filtering a time series of the positioning data using a local linear regression routine with a half-width time window of 1 h." Earlier: Sugiyama et al. 2014, *EPSL* 399, [10.1016/j.epsl.2014.05.001](https://doi.org/10.1016/j.epsl.2014.05.001): "filtered using a Gaussian smoothing routine with ±1 hour time window." So the routine is probably a local linear regression and h is a half-width. The kernel shape and the 12 h in the code are unexplained, and the code is not public (GitHub, File Exchange, and the 2025 Mendeley deposit all checked). **Plan:** run 1 h and 12 h, plus the range between them, as a sensitivity test; ask the authors. |
| A2 | PDD definition (not stated in the paper) | **closed** | `figS3/fig_s3.m`: `pdd = 0.5*(sum(abs(T))+sum(T))` over December–January daily means, i.e. the sum of positive daily means. Our Python version reproduces **10.6 °C·d** (2021/22) and **18.18** (1989/90–2025/26 mean) exactly. Standard definition: Braithwaite 1995, *J. Glaciol.* 41(137), [10.3189/S0022143000017846](https://doi.org/10.3189/S0022143000017846): "the sum of all temperatures above the melting point … i.e. the positive degree-day sum." **Caveat:** JMA lists Syowa (WMO 89532) station elevation as "18 (1973.2-2019.12) 29 (2019.12- )", an 11 m move inside the baseline period ([JMA](https://www.data.jma.go.jp/antarctic/datareport/index-e.html)). |
| A3 | "Background speed" (never defined) | **partial / open** | Precedents: Tuckett et al. 2019, *Nat. Commun.* 10, 4311, [10.1038/s41467-019-12039-2](https://doi.org/10.1038/s41467-019-12039-2): ">20% greater than the annual mean", detrended with "a 144-day running mean"; Sole et al. 2013, *GRL* 40, [10.1002/grl.50764](https://doi.org/10.1002/grl.50764): mean winter velocity, 1 Sep–30 Apr; Andrews et al. 2014, *Nature* 514, [10.1038/nature13796](https://doi.org/10.1038/nature13796): "percentage of winter background"; same group 2025 (above): "mean ice motion was computed by linear regression of the positioning data obtained in each season". **Plan:** declare several baselines before computing (pre-event window, campaign mean, campaign linear trend, running mean) and report C3 for each; ask the authors. |
| A4 | Thickness and bed: paper 552 m and ~440 m b.s.l.; code 551.31 m and −436.1 m | **closed** | `fig1/borehole_geometry220521.dat`: at BH2201/02, surface 115.167 m minus bed −436.1 m gives 551.27 m; the 552 m is the drilled depth. Context: Kondo et al. 2025, *Bull. Glaciol. Res.* 42, [10.5331/bgr.24R04](https://doi.org/10.5331/bgr.24R04): "drilled through ~550-m-thick ice". |
| A5 | Borehole names in the data files differ from the paper | **closed** | Field names in the data files; publication names applied in `fig1.m`; relabelled after review (R3: "Many of the boreholes are incorrectly labelled in (c)." Authors: "Corrected (Figure 1c)."). Mapping table in `nanopubs/drafts/00_paper_summary.md`. Paper BH2203 = field BH2205. |
| A6 | Atmospheric-pressure correction: the paper says hourly air pressure; the code subtracts constants (9.2 dbar; 0.089) | **closed (Arm B)** | The constants act as sensor offsets: 920 and 890 hPa, well below Syowa's ~985 hPa. Removing the time-varying part of JMA Syowa hourly station pressure changes water levels by −0.32 to +0.23 m and no C1/C2 label; the largest C2 shift is 0.22 m (`results/pressure_sensitivity.csv`, `results/arm_b_table.csv`). The authors' own pressure series (ADS A20220506-001) remains embargoed. |
| A7 | Tide lag | **closed** | `fig3.m`/`fig_s4.m` shift the tide by −2.5 h ("2.5 hours lag!"; not stated in the paper), plus an extra 0.25 h for BH2203 (SI Fig. 4 inset). Matching the deposit tide file against the IOC Sea Level Station Monitoring Facility mirror of the same gauge (station `syow`, UTC) shows the file is in **Syowa local time, UTC+3** (r = 0.99993, residual 0.28 cm). The best-fitting total shift is 2.75 h (the code's 2.5 h plus the SI's 0.25 h), i.e. the 3 h clock offset minus a real lag of ~15 min (1-min lag scan: best +15 min at BH2201, BH2202 and BH2203; ranges within 0.001 of the best r: 6–20, 15–21 and 0–16 min). The code's 2.5 h alone is 30 min short of the clock offset. In UTC the boreholes respond ~15 min after the gauge, the reverse of the SI's wording. |
| A8 | Tide correlation as evidence of hydraulic connection (C7) | **method point** | Walker et al. 2013, *EPSL* 361, [10.1016/j.epsl.2012.11.008](https://doi.org/10.1016/j.epsl.2012.11.008): tidal flexure can cause "basal pressure variations of sufficient magnitude to influence subglacial hydrology" beneath grounded ice. Correlation alone does not prove hydraulic connection. **Plan:** also test the amplitude ratio (about 10 kPa, or about 1 m of water, per metre of tide if transmitted hydraulically) and the lag. No r is given for BH2201/02, so compute it. Precedent: Sugiyama et al. 2014 EPSL: water levels "agreed with the ocean-tide levels". |
| A9 | Static GNSS positioning of a moving antenna (R1) | **gap** | King 2004, *J. Glaciol.* 50(171), [10.3189/172756504781829747](https://doi.org/10.3189/172756504781829747): coordinates "become biased in the ambiguity-free solution by a value approximately 5–10% of the magnitude of the horizontal velocity … once the ambiguity parameters are fixed there is no bias." That is the same order as the claimed speed-up. Untestable without raw GNSS (C below). |
| A10 | Syowa tide data (paper: 30 s, JHOD) | **partial** | Operator: Japan Coast Guard Hydrographic and Oceanographic Department ([real-time page](https://www1.kaiho.mlit.go.jp/KANKYO/KAIYO/jare/tide/tide_exp.html): "every 5 minutes observed data … Nisi-no-ura Cove, East Ongul Island"). Public: 5-min data via JODC and the IOC Sea Level Station Monitoring Facility (`syow`). The 30 s product is not public; the deposit's `tide_211231_220206.dat` is what we use. The paper's ref 69 (Aoyama et al. 2016, [10.1093/gji/ggw078](https://doi.org/10.1093/gji/ggw078)) is a gravimeter paper and only weakly supports the tide-gauge description. |

## B. Independent data (Arm B, replication)

| # | Need | Best source | Coverage / licence / notes |
|---|---|---|---|
| B1 | Hourly surface air pressure | **JMA Syowa (89532)**, [hourly](https://www.data.jma.go.jp/stats/etrn/view/hourly_s1.php?prec_no=99&block_no=89532&year=2022&month=1&day=2&view=) and 10-min (from Feb 2016) tables; [CSV download](https://www.data.jma.go.jp/risk/obsdl/index.php) | Dec 2021–Feb 2022 present, station pressure 0.1 hPa. **Times are local, UTC+3** ("日本中央標準時との時差は-6時間"). Licence: JMA Public Data Terms of Use v1.0 (attribution; CC BY 4.0 compatibility not verified). ~25 km from GNSS1. |
| B1b | Near-field pressure, temperature, wind | Kudoh et al. 2026, Yukidori Zawa / Langhovde AWS, [10.17592/001.2026052101](https://doi.org/10.17592/001.2026052101) | 2021-01-01 to 2022-12-31, 10-min, 1 h and daily; ~5 km from GNSS2; CC BY 4.0. Gaps in Dec–Jan not yet checked. An independent group, so it also tests Period I melt (temperature). |
| B1c | Cross-check | ERA5 hourly single levels, [10.24381/cds.adbb2d47](https://doi.org/10.24381/cds.adbb2d47) (`sp`, `t2m`) | CC BY 4.0; reanalysis, so a cross-check only. BSRN Syowa synop on PANGAEA (e.g. [10.1594/PANGAEA.965244](https://doi.org/10.1594/PANGAEA.965244), Jan 2022) has 1-min data but integer hPa. |
| B2 | Syowa climate 1989–2026 and rain frequency (C9) | JMA etrn daily pages (`daily_s1.php?prec_no=99&block_no=89532`) | Daily mean, max and min temperature give PDD from the original source. Syowa has **no precipitation amount**; rain only from the weather summary text (e.g. 2022-01-02 "曇時々雨一時みぞれ"; 2017-12-23 "曇後一時雨"). Count days containing 雨, keeping sleet (みぞれ) separate. GHCN-D `AYM00089532` ([10.7289/V5D21VHZ](https://doi.org/10.7289/V5D21VHZ)) as a secondary check. |
| B3 | Event context: 2–3 Jan rain, 21–25 Dec warm event | Hirasawa et al., [WAMC 2023 abstract](https://amrdc.ssec.wisc.edu/web_products/meetings/wamc2023/Hirasawa.pdf) (no DOI): "rainfall occurred on January 2-3, 2022, for the first time since December 24, 2017. Rainfall at Syowa Station is a rare event, occurring only about once every five years." | No peer-reviewed paper on the event found. |
| B3b | Atmospheric-river attribution (R1's unanswered question) | Favier 2025, AR catalogues at staffed Antarctic stations, [10.5281/zenodo.17165410](https://doi.org/10.5281/zenodo.17165410), CC BY 4.0; Wille, polar AR detection catalogues, [10.5281/zenodo.15830634](https://doi.org/10.5281/zenodo.15830634), CC BY 4.0 (method: [10.1029/2020JD033788](https://doi.org/10.1029/2020JD033788)) | Favier `Syowa_ARday.csv`: AR days **2021-12-31 to 2022-01-05** (covers Period II); **none on 21–25 Dec 2021** (Period I not AR-associated); also 12-26 to 12-28 and 01-16 to 01-19. Use Wille's gridded ERA5 tags for the glacier itself. |
| B4 | Surface melt, Dec 2021–Jan 2022 | Picard daily melt, SSM/I 25 km and AMSR2 10 km ([site](https://snow.univ-grenoble-alpes.fr/melting/); cite Picard & Fily 2006, [10.1016/j.rse.2006.05.010](https://doi.org/10.1016/j.rse.2006.05.010)); Zheng et al. PDD melt, [10.5281/zenodo.8327543](https://doi.org/10.5281/zenodo.8327543) (daily/hourly, to 2022) | Picard licence "AS IS". A 25 km cell mixes glacier, coast and sea ice. RACMO2.4p1 ([10.5281/zenodo.14217232](https://doi.org/10.5281/zenodo.14217232)) is monthly only and cannot resolve the event. MAR 2021/22 not found. |
| B4b | Optical melt evidence | Sentinel-2 L2A (Element84 STAC): clear scenes **2021-12-13, 12-20, 12-23, 2022-01-19**; 12-30 and 01-02 cloudy. Landsat 8/9 available. | Copernicus open data / public domain. Bracket Period I (20 and 23 Dec). |
| B5 | Satellite velocity at speed-up timescale | ITS_LIVE v2 granules (STAC `stac.itslive.cloud`; Landsat [10.5067/IMR9D3PEI28U](https://doi.org/10.5067/IMR9D3PEI28U), S1 [10.5067/0506KQLS6512](https://doi.org/10.5067/0506KQLS6512)) | **Shortest pair: 8 days** (L8/L9), S2B 10 days, S1A 12 days. Sentinel-1B failed on 23 Dec 2021 (ESA). An 8-day pair dilutes a ~5-day, 20% pulse to ~12%, near noise. **Feasibility spike only;** expect to record as a gap. |
| B6 | GNSS base station | IGS `SYOG00ATA` (~25 km), daily 30 s RINEX 3 on [BKG](https://igs.bkg.bund.de/root_ftp/IGS/obs/2022/002/) | Useful only if the raw rover GNSS is released. |

## C. The authors' raw data at NIPR ADS (found during research)

The authors (Sugiyama, Minowa, Kondo, Aoki 2022, project ROBOTICA) archived the 2021/22 field data at the [NIPR Arctic/Antarctic Data archive](https://ads.nipr.ac.jp/) (OAI-PMH `https://ads.nipr.ac.jp/portal/oai?verb=GetRecord&identifier=<ID>&metadataPrefix=DIF`). No DOIs.

| ID | Content | Access |
|---|---|---|
| A20220506-001 | Glacier weather station, 2021-12-19 to 2022-02-06; keyword "ATMOSPHERIC PRESSURE MEASUREMENTS" (would close A6) | Embargo |
| A20220506-002 | Subglacial water pressure and acceleration | Embargo |
| A20220506-003 | Water pressure in borehole 5 (= paper BH2203, see A5), 2022-01-24 to 02-06 | Public |
| A20220506-004 | Raw GNSS, 2021-12-16 to 2022-02-07 (would close A9) | Embargo |
| A20220506-005/-006 | Seismic; UAV imagery | Embargo |

These are the authors' own data, so they serve **reproduction**, not independent replication.

## D. Discrepancies to record

- **Smoothing:** 1 h (paper) vs 12 h (code) (A1).
- **Air pressure:** hourly measured (paper) vs constants (code) (A6).
- **Tide lag:** 2.5 h in the code, not stated in the paper (A7).
- **Coverage:** GNSS2 (`LG04`) covers 23 Dec – 27 Jan; the paper implies 19 Dec – 6 Feb. The weather-station file is 10-min; the paper says 5-min.
- **Grounding line:** "~1 km" from BH2201/02 (paper) vs "1.5 km upstream from the grounding line" (Kondo et al. 2025, [10.5331/bgr.24R04](https://doi.org/10.5331/bgr.24R04)).
- **Ref 37** is cited as Nat. Commun. 12, **3929**; the article is **4209** ([10.1038/s41467-021-23534-w](https://doi.org/10.1038/s41467-021-23534-w)).
- **Typos:** "24–25 December 2012" (for 2021); SI Fig. 3 "1989/20".

## E. Questions for the authors (draft; Anne decides whether to send)

To: corresponding author, Shin Sugiyama (address in the paper).

1. Could you share `local_regression.m` and `latlon2utm.m`, and confirm whether the GNSS speeds in Fig. 3 used h = 1 h (Methods) or h = 12 h (`fig3.m`), and whether h is a half-width or a Gaussian σ?
2. How was "background speed" defined for the 10–20% speed-up?
3. Could the air-pressure series used for the borehole correction be released, or ADS A20220506-001 lifted from embargo? The code subtracts constants (9.2 dbar; 0.089).
4. Could the raw GNSS (ADS A20220506-004) be released, so the positions can be reprocessed kinematically with final orbits, as Reviewer 1 suggested?
5. What is the basis of the 2.5 h tide lag in `fig3.m`?
6. Which surface elevation underlies the 551.31 m overburden, and is the grounding line ~1 km or 1.5 km from BH2201/02?

## Unconfirmed (not used)

- Hock 2003 ([10.1016/S0022-1694(03)00257-9](https://doi.org/10.1016/S0022-1694(03)00257-9)), Bartholomew et al. 2010, Horgan et al. 2013: DOIs resolve, publisher pages returned 403.
- Nakazawa et al. 2025 ([10.1039/D4VA00166D](https://doi.org/10.1039/D4VA00166D)): reportedly mentions the January 2022 rain; not read.
- Yukidori Zawa AWS gaps in Dec 2021–Jan 2022; Picard 2021/22 values; MAR 2021/22; ADS embargo end dates; JMA licence wording beyond the Japanese terms page.
