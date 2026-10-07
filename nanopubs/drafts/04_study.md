# 04 — FORRT Replication Study

> Fields from the live template `https://w3id.org/np/RAuLEjPp-4dTvPwMkfHggTto1CgjIftiGRAgHlyeEonjQ` (`template_fields("04_study")`, source: live, 2026-10-07): study, label, type, claim (filled by the chain wizard), scope, methodology, deviation (optional), keyword (optional, repeatable, Wikidata), discipline (optional, single, Wikidata).
>
> Scope and method only, no results (`docs/pico-study-outcome-levels.md`). The method is written from the code that ran: `notebooks/01`–`05`, `notebooks/gnss.py`, `ANALYSIS_PLAN.md`.

## Field-by-field draft

<!-- field: study -->
### Short URI suffix for study ID (text input, required)

```
langhovde-meltwater-acceleration-study
```

<!-- field: label -->
### Label/name of replication study (text input, required)

```
Reproduction and partial replication of Sugiyama et al. (2026): meltwater, basal pressure and ice speed at Langhovde Glacier
```

<!-- field: type -->
### Choose the study type (dropdown, required)

Arm A reproduces with the authors' data; Arm B replicates parts with independent data.

- [ ] Replication Study - replication with different methodology or conditions
- [x] Reproduction/Replication Study - study that is both, reproduction and replication
- [ ] Reproduction Study - direct reproduction: same methodology, same tools

<!-- field: claim -->
### Choose FORRT claim (search/select, required)

The Claim URI from step 03; the chain wizard fills it in.

```

```

<!-- field: scope -->
### Describe what part of the claim is reproduced/replicated. (textarea, required)

```
The claim that surface meltwater reaching the bed accelerated grounded ice at Langhovde Glacier, East Antarctica, in summer 2021/22, tested through the observations it rests on:
- basal water pressure relative to the flotation level, and its rise during the January 2022 rain and melt event;
- the size of the speed-up at a grounded and a floating GNSS station during the December 2021 and January 2022 events;
- uplift of the grounded station and its absence on floating ice;
- the timing of the pressure and speed peaks;
- the tidal connection between the bed and the sub-shelf cavity, and the head difference to a borehole below the grounding line;
- the context that summer 2021/22 was unexceptional, with rare rain and no trend in temperature, positive degree-days or rain frequency.

The causal mechanism is assessed only through these observations. Out of scope, because no data were deposited: freshwater at the bed (CTD), borehole video, drone imagery, sub-shelf fauna, and changes in ocean forcing or buttressing.
```

<!-- field: methodology -->
### Describe how the claim is reproduced/replicated. (textarea, required)

```
Reproduction (authors' data):
- Input: the Mendeley deposit (doi:10.17632/8wvtxg53ry.1), downloaded and checked against the repository's published SHA-256 checksums, and analysed with new Python code. The authors' MATLAB scripts serve only as a reference for file formats, constants and conversions.
- Pre-registration: a tolerance and decision rule for each sub-claim were committed in ANALYSIS_PLAN.md before analysis. Later changes are dated amendments, and every result is labelled pre-registered or post hoc.
- Pressure: borehole pressures are converted to water level and to a fraction of flotation as in the authors' code; the paper's Eq. 1 is reported alongside.
- GNSS: positions are projected to UTM zone 37S and smoothed with a Gaussian-kernel local linear regression. This reconstructs the authors' missing local_regression function, identified by matching the deposited fig3.eps. Horizontal speed is differenced from the smoothed positions. Data gaps are detected from the timestamps and optionally bridged with a not-a-knot cubic spline, as in the authors' supplementary figure.
- Speed-up: computed against four declared background-speed baselines (local, campaign median, campaign trend, 7-day running median), at smoothing bandwidths of 1, 3, 6 and 12 h, and compared with speed fluctuations outside the events.
- Tide: the authors' BH2203 correlation is repeated, then extended to the grounded boreholes with a 25 h high-pass filter and a lag scan. The clock of the tide file is checked against the IOC record of the same gauge.

Replication (independent data, each test pre-registered before its data were downloaded):
- Japan Meteorological Agency (JMA) Syowa daily weather summaries for rain frequency, 1990–2026;
- JMA hourly station pressure for the borehole correction;
- JMA daily temperatures, and ERA5 2 m temperature from ECMWF's cloud-optimised archive, for the positive degree-day context;
- passive-microwave melt flags (SSM/I 25 km, AMSR 10 km) and Sentinel-2 NDWI for surface melt;
- an atmospheric-river catalogue (Favier 2025) for the January event;
- ITS_LIVE image-pair velocities, to test whether the speed-up can be detected independently.

The whole pipeline runs with pixi and Snakemake from a fresh checkout, and the GNSS processing is guarded by unit and regression tests.
```

<!-- field: deviation -->
### Describe any deviations from original methodology. (textarea, optional)

```
- Smoothing: the Methods state a Gaussian filter with a 1 h bandwidth, but the deposited code and published figures use 12 h, as identified from fig3.eps. 12 h is primary; 1, 3 and 6 h are reported.
- Atmospheric-pressure correction: the paper uses hourly air pressure from the on-glacier station, which is embargoed. The code's constant offsets are primary, with JMA Syowa hourly pressure as a sensitivity case.
- Tide: the deposit's tide file is in Syowa local time (UTC+3), and the authors shift it by 2.5 h. That shift is kept for the reproduction; the lag analysis uses UTC.
- Data gaps are detected from timestamps instead of hard-coded row numbers. This gives identical segments.
- Speed is differenced with the authors' schemes at 12 h (forward at GNSS2, centred at GNSS1) and centred at other bandwidths.
- The paper does not define "background speed"; four baselines are declared instead.
- Event windows come from the paper's text. The windows shaded in the authors' code are reported alongside.
- Correlations for the grounded boreholes, which the authors show only as a scatter plot, are computed.
- Rain frequency, air pressure and climate context use independent public records instead of the authors' extracts.
```

<!-- field: keyword -->
### Search keywords (Wikidata) (search/select, optional)

Wikidata items checked with `wikidata_lookup` on 2026-10-07.

```
Langhovde Glacier (Q6486120)
meltwater (Q360925)
Basal sliding (Q3962812)
Antarctic ice sheet (Q571430)
```

<!-- field: discipline -->
### Search discipline (Wikidata) (search/select, optional)

Wikidata types glaciology as "field of study", not "academic discipline" (Q11862829). The template declares no type, so it is used as is.

```
glaciology (Q52120)
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.
