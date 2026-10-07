# langhovde-meltwater-replication

> **Acceleration of an Antarctic outlet glacier driven by surface meltwater input to the base**: reproduction and partial replication.
>
> Reference paper: Sugiyama, S., Kondo, K., Minowa, M. & Watanabe, A. (2026). *Nature Communications* 17, 6102. [doi:10.1038/s41467-026-72724-x](https://doi.org/10.1038/s41467-026-72724-x)

The paper reports that surface meltwater reached the bed of Langhovde Glacier, East Antarctica, in summer 2021/22, raised basal water pressure to near flotation, and accelerated the grounded ice. This repository tests that claim in two arms:

- **Reproduction:** the authors' data deposit ([doi:10.17632/8wvtxg53ry.1](https://doi.org/10.17632/8wvtxg53ry.1)) analysed with new Python code.
- **Partial replication:** independent public data: JMA Syowa station records, ERA5, satellite melt flags, Sentinel-2 imagery, an atmospheric-river catalogue, and ITS_LIVE velocities.

Every test was pre-registered in the [analysis plan](ANALYSIS_PLAN.md) before its data were analysed. Each result is labelled pre-registered or post hoc.

## Result

**Partially supported.** The deposited data reproduce the paper's central observations:
- During the rain and melt event of 2–6 January 2022, basal water pressure rose by 20.2 m to 97.1% of flotation.
- Ice speed rose by 11–13%, and the speed peak came 2 h before the pressure peak.
- In the December warm spell, speed rose by 22–23%, and the grounded station rose by 126 mm while the floating station stayed within 3 mm.
- Independent data confirm surface melt in both events, an atmospheric river during the January event, and that rain is rare at Syowa.

The qualifications:
- The evidence is one fully instrumented event at one site.
- The reported 10–20% speed-up holds only with the 12 h smoothing used for the published figures. The Methods state 1 h, which gives 44–72%.
- Some stated ranges apply only to the event.
- No independent dataset can confirm the speed-up.

```{figure} figures/main_result.png
:alt: Six stacked panels of horizontal speed, vertical displacement, borehole water level, tide, air temperature and daily rain at Langhovde Glacier, 19 December 2021 to 7 February 2022
:width: 100%

Our regeneration of the paper's Fig. 3 from the CC BY 4.0 deposit, in UTC. a, horizontal speed (12 h smoothing; dashed where a data gap is spline-filled); b, vertical displacement; c, borehole water level and flotation level; d, Syowa tide; e, air temperature; f, daily rain. Grey bands: Periods I and II (paper text); light band: Period III.
```

Full results: [`results/claims_table.csv`](results/claims_table.csv) (reproduction) and [`results/arm_b_table.csv`](results/arm_b_table.csv) (replication). Gaps and sources: [`GAP_SOURCES.md`](GAP_SOURCES.md).

## Quick start

```bash
git clone https://github.com/annefou/langhovde-meltwater-replication.git
cd langhovde-meltwater-replication
pixi install
pixi run snakemake --cores 1
```

ERA5 is read from ECMWF's cloud-optimised (ARCO) store and needs a CDS API key in `CDSAPI_KEY` or `~/.cdsapirc`. Every other input is public and downloaded by `notebooks/01_data_download.py`.

## Structure

- `paper/`: the source paper, Supplementary Information and Peer Review File.
- `notebooks/`: jupytext notebooks: 01 download, 02 clean, 03 reproduction analysis, 04 figures, 05 replication; `gnss.py` holds the GNSS processing.
- `tests/`: unit tests, and a regression test against the authors' published figure.
- `results/`, `figures/`: outputs of the pipeline.
- `nanopubs/`: the FORRT nanopublication chain, drafted field by field.

## Nanopublication chain

The FORRT chain (Quote → AIDA → Claim → Study → Outcome → CiTO) is drafted in [`nanopubs/drafts/`](nanopubs/drafts/). Once published, it is listed in [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md).

## Citation

Please cite both:

- This work: [`CITATION.cff`](CITATION.cff).
- The original paper: [doi:10.1038/s41467-026-72724-x](https://doi.org/10.1038/s41467-026-72724-x).
