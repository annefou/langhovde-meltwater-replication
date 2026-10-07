# Snakefile: runs the Arm A reproduction end to end.
#
# Each rule executes one jupytext notebook, so the notebook stays the source of truth.
#
# Usage:
#   pixi run snakemake --cores 1         # run everything
#   pixi run snakemake --cores 1 -n      # dry run

NOTEBOOKS = "notebooks"
DATA = "data"
RESULTS = "results"
FIGURES = "figures"


def execute(nb):
    return f"cd {NOTEBOOKS} && jupytext --to notebook --execute {nb} 2>&1 | tee ../{{log}}"


rule all:
    input:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/sensitivity_c3.png",
        f"{RESULTS}/claims_table.csv",
        f"{RESULTS}/arm_b_table.csv",


# ---------- 01: Data download (Mendeley deposit, checksums verified; IOC tide in UTC) ----------
rule data_download:
    output:
        f"{DATA}/raw/sources.json",
    log:
        f"{RESULTS}/logs/01_data_download.log",
    shell:
        execute("01_data_download.py")


# ---------- 02: Data clean (tidy NetCDF) ----------
rule data_clean:
    input:
        f"{DATA}/raw/sources.json",
    output:
        expand(f"{DATA}/clean/{{name}}.nc", name=["gnss_GNSS1", "gnss_GNSS2", "pressure_BH2201",
               "pressure_BH2202", "pressure_BH2203", "tide", "aws", "syowa_temperature"]),
        f"{DATA}/clean/jma_syowa_daily.parquet",
        f"{DATA}/clean/jma_syowa_hourly.parquet",
    log:
        f"{RESULTS}/logs/02_data_clean.log",
    shell:
        execute("02_data_clean.py")


# ---------- 03: Analysis (claims C1-C4, C6-C9 against ANALYSIS_PLAN.md) ----------
rule analysis:
    input:
        rules.data_clean.output,
        f"{NOTEBOOKS}/gnss.py",
    output:
        f"{RESULTS}/claims_table.csv",
        f"{RESULTS}/sensitivity_c3.csv",
        f"{RESULTS}/water_levels.nc",
        f"{RESULTS}/gnss_tracks.nc",
        f"{RESULTS}/pressure_sensitivity.csv",
    log:
        f"{RESULTS}/logs/03_analysis.log",
    shell:
        execute("03_analysis.py")


# ---------- 04: Figures ----------
rule figures:
    input:
        f"{RESULTS}/sensitivity_c3.csv",
        f"{RESULTS}/water_levels.nc",
        f"{RESULTS}/gnss_tracks.nc",
    output:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/sensitivity_c3.png",
    log:
        f"{RESULTS}/logs/04_figures.log",
    shell:
        execute("04_figures.py")


# ---------- 05: Replication (Arm B, independent data; ANALYSIS_PLAN.md § Arm B) ----------
rule replication:
    input:
        f"{DATA}/clean/jma_syowa_daily.parquet",
        f"{RESULTS}/pressure_sensitivity.csv",
    output:
        f"{RESULTS}/arm_b_table.csv",
        f"{RESULTS}/jma_rain_events.csv",
    log:
        f"{RESULTS}/logs/05_replication.log",
    shell:
        execute("05_replication.py")
