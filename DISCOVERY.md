# Discovery and plan (handoff)

Written on 2026-10-06, before the replication started, to hand over everything found
during discovery to the session that runs it. Read this first, together with the paper
PDF, the Supplementary Information and the Peer Review File in `paper/`.

## Why this paper

- **Paper:** Sugiyama, S., Kondo, K., Minowa, M. & Watanabe, A. (2026). *Acceleration of
  an Antarctic outlet glacier driven by surface meltwater input to the base.* Nature
  Communications 17, 6102.
  [doi:10.1038/s41467-026-72724-x](https://doi.org/10.1038/s41467-026-72724-x)
  (open access, **CC BY-NC-ND 4.0**: do not adapt the paper's figures; regenerate every
  figure from the data).
- **Data and plotting code:** Mendeley Data
  [doi:10.17632/8wvtxg53ry.1](https://doi.org/10.17632/8wvtxg53ry.1), **CC BY 4.0**,
  published 2026-05-01, 38 files, 77 MB.
- **Peer Review File** (CC BY 4.0, `paper/supplementary/41467_2026_72724_MOESM6_ESM.pdf`):
  three named reviewers (D. Benn, S. Doyle, I. Willis). Their open points shape step 3
  below.
- **Not replicated yet:** Replication Radar `replication_status` returned `open` on
  2026-10-06.
- **How it came up:** proposed in private correspondence (October 2026) as a test case
  for a follow-up question: does the change at the ice–bed boundary give an *earlier*
  signal of acceleration than the speed record itself? That question is **not** part of
  this repo. This repo reproduces and partly replicates the published claim. The
  lead-time question belongs to a follow-up repo (see "Future question").

## The claim

Headline (abstract): *"Our in-situ measurements confirm meltwater-driven acceleration
of grounded ice in Antarctica."* The mechanism the paper argues: surface meltwater
reaches the bed through fractures in cold ice → subglacial water pressure rises → the
ice separates slightly from the bed (uplift) → friction drops → sliding speeds up.

Sub-claims, with the paper's numbers (verify every quote against the PDF before
drafting; `docs/verify-before-drafting.md`):

| # | Sub-claim | Testable from the deposit? |
|---|---|---|
| C1 | Subglacial water pressure exceeded 90% of ice overburden (93–97% of flotation at BH2201/02) | Yes |
| C2 | Pressure rose during melt and rain. Period II: 29–33 m a.s.l. (93–94%) until 2 Jan, rose by 20 m on 3 Jan to 51 m a.s.l. (97%), dropped ~10 m within an hour, then fell ~30 m over 10 days | Yes, but **only Period II has pressure data**. The sensor was installed on 31 Dec, so Period I has none |
| C3 | Ice speed rose by 10–20% during the events. Period I peaked on 24 Dec, GNSS2 ~20% above background, GNSS1 similar or more. Period II: 2–6 Jan | Yes |
| C4 | The surface rose ~0.1 m at GNSS1 (120 mm on 21–25 Dec; ~10 mm on 3–5 Jan), with no noticeable vertical motion at GNSS2 (afloat) | Yes |
| C5 | Headline causal claim (above) | Built from C1–C4 and C6; no direct test |
| C6 | Timing of the pressure peak "broadly coincided" with the speed peak | Yes |
| C7 | Semidiurnal pressure variations from 14 Jan (Period III) correlate with the Syowa tide, so the bed at BH2201/02 is hydraulically connected to the sub-shelf cavity | Yes |
| C8 | Head difference between BH2201 and BH2203 is 9–44 m, giving a hydraulic gradient of 0.9–4.4 × 10⁻² | Yes |
| C9 | 2021/22 was unexceptional: PDD 10.6 °C·d vs mean 18.2 (1989/90–2025/26); rain about every 5 years; no trend in summer temperature, PDD or rain frequency | Yes (Syowa series in `figS3/`) |
| — | Freshwater at the bed (CTD), sub-shelf fauna, borehole video, drone images | **No.** Not deposited; out of scope |

## The data, as checked on 2026-10-06

One field season, **19 Dec 2021 – 6 Feb 2022**. Download the whole deposit as a zip:
`https://data.mendeley.com/public-api/zip/8wvtxg53ry/download/1`.

| File (`fig3/`) | Content | Time step | Coverage |
|---|---|---|---|
| `LG05.dat` | **GNSS1** (grounded, next to BH2201/02): lat, lon, ellipsoidal height | 15 min | 19 Dec – 6 Feb, gaps |
| `LG04.dat` | **GNSS2** (2 km downglacier, afloat) | 15 min | 23 Dec – 27 Jan |
| `pressure_eliminate1.dat` | BH2201 pressure (dbar), 190 NaN rows | 1 min | 31 Dec – 5 Feb |
| `geokon_pressure2_AVW200_220206.dat` | BH2202 pressure (column 13, MPa-like units; see `fig3.m`) | 5 min | 7 Jan – 6 Feb |
| `geokon_pressure_AVW200_220206.dat` | BH2203 pressure (below the grounding line) | 5 min | 24 Jan – 6 Feb |
| `aws211219_220206.dat` | AWS: wind speed, wind direction, air temperature, rain | 10 min | 19 Dec – 6 Feb |
| `tide_211231_220206.dat` | Syowa tide (paper applies a 2.5 h lag) | 30 s | 31 Dec – 6 Feb |

Other folders: `fig1/` (Landsat 8 scenes, Pléiades DEM, borehole geometry, thermistor
snapshots from 2012–2019; **not time series**), `figS3/1989_2026_temperature.dat` (Syowa
daily mean/max/min), plus inputs for `figS2`, `figS4` and `figS6`.

**Careful:** `LG05` = GNSS1 and `LG04` = GNSS2 (from the coordinates: LG05 is upglacier at
~132 m ellipsoidal height, LG04 is lower and afloat). My first exploratory plot had them
swapped.

Constants from `fig3/fig3.m`: overburden `z_i = 551.31 × 0.91` m; bed elevation BH2201/02
−436.1 m, BH2203 −398.1 m; geoid offset 23.47 m.

A quick exploratory Python port (not in this repo) already gives BH2201 rising from about
0.93 to 0.97 of overburden on 2–3 Jan, matching C2.

### Gaps and discrepancies found in the deposit

1. **Code is plotting-only and does not run as deposited.** `fig3.m` and `fig_s6.m` call
   `local_regression()` and `latlon2utm()`, which are not in the deposit. No Fig. 2 code
   (Fig. 2 is borehole photos).
2. **Smoothing mismatch.** The Methods say a Gaussian filter with a **1 h** bandwidth;
   `fig3.m` passes `h = 12/24` (**12 h**) to `local_regression`. Speed-up size and
   timing depend on this.
3. **Atmospheric-pressure correction.** The Methods say hourly AWS air pressure was used.
   The deposited AWS file has no pressure column, and the code subtracts constants
   (9.2 dbar; 0.089). The effect is about ±0.2 m of water against a 20 m signal: small,
   but record it as a deviation.
4. **GNSS1 gap at the Period I peak.** GNSS1 has no data on 24–25 Dec (the Methods say
   "2012", a typo for 2021) or on 12–19 and 22–26 Jan; spline-filled (Supp. Fig. 6).
   Roughly 85 mm of the 120 mm uplift falls in data that exist before the gap; the rest
   spans it.
5. **Raw GNSS (1 s, RINEX) not deposited.** Reprocessing the positions, as Reviewer 1
   asked (kinematic positioning, final instead of broadcast ephemeris), is impossible
   without it.
6. **"Background speed"** is never defined.

## Plan: two arms, each outcome labelled by type

### Arm A — Reproduction (deposited data, our own Python code)

1. **Recompute C1–C4 and C6–C9** from the raw files and compare each number with the
   text, using tolerances declared before computing.
2. **Smoothing sensitivity:** 1 h vs 12 h and the range between them. Report whether C3
   (10–20%) and the C6 timing hold across the range.
3. **Signal vs noise for C3:** fix an operational "background" (declare it first), then
   compare the size of the Period I/II peaks with speed fluctuations elsewhere in the
   record that have no melt or rain. Paper's speed error: 7–12%.
4. **Alternative explanations, from data:**
   - *Tides:* do speed-ups line up with spring tides? Not tested in the paper.
   - *Vertical strain and inclined bed:* recompute the paper's two arguments (similar
     acceleration at GNSS1 and GNSS2; generally downward motion after the December
     uplift).
   - *Gap interpolation:* split C4 into observed vs spline-interpolated uplift.
   - *Ocean or buttressing changes:* no data, so record as untested.
5. **Event sequence in Period II, hourly:** rain/melt → pressure → uplift → speed. This
   tests the "broadly coincided" wording of C6 only. No predictive modelling here.
6. **Scope of the wording:** the abstract says pressure rose "during periods" (plural);
   pressure was recorded for one event. Period I melt is inferred from air temperature
   only; quantify it as AWS PDD.

### Arm B — Partial replication (independent data)

Commit to:

1. **Weather forcing:** JMA Syowa hourly/daily records, ERA5, and an atmospheric-river
   catalogue for 2–3 Jan 2022 and 21–25 Dec 2021. Syowa had its first rain since
   24 Dec 2017 on 2–3 Jan 2022 (see Hirasawa, WAMC 2023, radar/disdrometer analysis:
   <https://amrdc.ssec.wisc.edu/web_products/meetings/wamc2023/Hirasawa.pdf>).
   **This also answers Reviewer 1's unaddressed request** ("How often did similar events
   occur in the AWS and reanalysis data?"). The authors answered with the Syowa station
   record only, with no reanalysis and no AR analysis.
2. **Melt evidence for Period I:** Sentinel-2 and Landsat 8/9 surface water/slush around
   GNSS1 in Dec 2021 – Jan 2022. Optional: microwave melt flags, MAR/RACMO melt and
   runoff, *if* 2021/22 output is public (not yet checked).
3. **Climate context (C9) from the original JMA record**, not the authors' extract.
4. **Air-pressure correction** from Syowa (JMA) or ERA5, closing deposit gap 3.

**Feasibility spike before committing:** can satellite velocity (Sentinel-1, Sentinel-2,
Landsat; e.g. ITS_LIVE image pairs) resolve a ~20% speed-up (~0.05 m/d over ~5 days) at
the GNSS sites in Dec 2021 – Jan 2022? Likely not: pair intervals are 5–16 days, and
Sentinel-1B failed on 23 Dec 2021, leaving 12-day repeats. If it works, it is the
strongest replication available (independent speed data, and possibly other rainy
summers to break n = 1). If not, record it as a gap.

### What cannot be replicated

The core link (pressure → uplift → speed) has no independent counterpart: no other
subglacial pressure record exists for Langhovde. That link stays a reproduction.

## Reviewer points worth carrying (Peer Review File)

- **R1 (GNSS):** static positioning of a moving antenna can be biased (King 2004), and
  broadcast rather than final ephemeris was used. The authors kept their method; R1 judged
  the effect probably marginal. We cannot test it without raw GNSS (deposit gap 5).
- **R1 (interpolation):** "look to have been guessed"; the authors answered with spline
  interpolation and Supp. Fig. 6. Our gap split (A.4) tests how much depends on it.
- **R1 (AR / reanalysis):** see Arm B.1.
- **R2:** meltwater can also *slow* glaciers in an efficient drainage system. Check
  whether speed drops below background after the events, and whether the 10-day pressure
  decline matches.
- **R3:** pressure was not measured for Period I (stated plainly in the review).

## Expected verdict shape

C1, C2, C7 and C8 will very likely reproduce. C3 and C4 depend on A.2–A.4. C5 will likely
read as *supported for one fully instrumented event at one site*, with the mechanism
inferred rather than shown across repeated events. Any of confirms / qualifies / refutes
is a valid outcome.

## Constraints

- **Do not publish nanopublications yet.** Draft the FORRT chain; publishing waits for
  Anne's decision.
- Verify every quote against the PDF; no quotes from memory or from this file.
- Own Python code throughout; the MATLAB scripts are a reference for constants and
  processing choices only.
- Regenerate all figures from the CC-BY data; never adapt figures from the CC BY-NC-ND
  article.
- Label each outcome as *reproduction* (deposited data) or *replication* (independent
  data).

## Possible request to the authors (Anne decides)

Email the corresponding author (sugishin@lowtem.hokudai.ac.jp) for: `local_regression.m`
and `latlon2utm.m`; the AWS air-pressure series; raw GNSS RINEX; confirmation of the 1 h
vs 12 h smoothing.

## Future question (follow-up repo, not this one)

Once this chain is published, a second FORRT-template repo starts **from this chain's
constellation** and continues with a new research question. It was not tested in the
paper:

- **Question:** does the change at the ice–bed boundary, measured as basal water
  pressure and uplift, give an *earlier and better* signal of glacier acceleration than
  the glacier-speed record itself?
- **System boundary:** the contact between grounded ice and bedrock. **Endpoint:**
  glacier acceleration.
- **Proposed test:** compare held-out prediction of acceleration from three nested
  models:
  1. glacier-speed history alone;
  2. weather and melt observations plus speed history;
  3. basal pressure and uplift added to the same controls.
- **Key result to look for:** whether boundary observations provide genuine **lead
  time**, rather than simply changing at the same moment as speed.

**Feasibility on this data (checked 2026-10-06):** held-out prediction is not possible.
Only one event (Period II) has pressure, uplift, speed and weather together, over about
five weeks. At most, a descriptive within-event lead–lag analysis at hourly resolution,
clearly labelled n = 1. The likely main output is a **recorded knowledge gap**: which
observations (basal pressure + GNSS + weather), over how many seasons or events, would
make the predictive test possible. Arm A step 5 (event sequence) is the natural seed,
but in this repo it only checks the paper's "broadly coincided" wording.

**Credit:** the question came from an external researcher by private correspondence.
Do not name them in this repository unless they agree; ask Anne.

## To do before starting

- [x] Paper PDF, Supplementary Information, additional-files list and Peer Review File
  in `paper/` (supplementary movies not downloaded).
- [ ] Download the Mendeley deposit into `data/` (gitignored), via
  `notebooks/01_data_download.py`.
- [ ] Start the replication workflow (`/replication-study`), Phase 1 paper analysis.
