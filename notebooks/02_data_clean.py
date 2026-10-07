# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 02 — Data clean
#
# Parses the Fig. 3 / SI Fig. 3 inputs from the Mendeley deposit
# ([doi:10.17632/8wvtxg53ry.1](https://doi.org/10.17632/8wvtxg53ry.1)) into tidy,
# self-describing NetCDF files in `data/clean/`. This notebook parses, renames and
# projects only. Physical conversions (pressure to water level, smoothing, speeds)
# are done in `03_analysis.py`, so every analysis constant sits in one place.
#
# The authors' MATLAB scripts (`fig3/fig3.m`, `figS4/fig_s4.m`, `figS6/fig_s6.m`,
# `figS3/fig_s3.m`) were used only as the reference for file layouts and columns.
#
# | File | Content | Column(s) used | Publication name |
# |---|---|---|---|
# | `fig3/LG05.dat` | GNSS, 15 min, lat/lon/ellipsoidal height | 1–4 | **GNSS1** (grounded) |
# | `fig3/LG04.dat` | GNSS, 15 min | 1–4 | **GNSS2** (afloat) |
# | `fig3/pressure_eliminate1.dat` | Valeport miniIPS, 1 min, dbar, spikes set to NaN | 1–2 | **BH2201** |
# | `fig3/geokon_pressure2_AVW200_220206.dat` | Geokon 4500S via AVW200, 5/30 min | 1, 13 | **BH2202** |
# | `fig3/geokon_pressure_AVW200_220206.dat` | Geokon 4500S via AVW200, 5/30 min | 1, 13 | **BH2203** (field name BH2205) |
# | `fig3/tide_211231_220206.dat` | Syowa tide gauge, 30 s, mm | field 3 of `+`-separated record | Tide |
# | `fig3/aws211219_220206.dat` | On-glacier AWS, 10 min | 1–6 | AWS |
# | `figS3/1989_2026_temperature.dat` | Syowa daily mean/max/min T, Dec–Jan | 1–4 | Syowa |
#
# ## Time bases
#
# No file states its time zone. What the files and code show:
#
# - **AWS: UTC.** The mean diurnal temperature cycle has its warm plateau centred
#   near 11:00 (above 0 °C from 07 to 15 h) and its minimum at 22:00 (computed below). Local solar noon at
#   39.8° E is about 09:20 UTC, so the cycle lags solar forcing by ~1.5 h in UTC.
#   In UTC+3 the maximum would precede solar noon, which is not physical.
# - **Borehole loggers: same clock as each other, consistent with UTC.** The code
#   applies no offset to the loggers. Independent confirmation is not possible from
#   the deposit alone.
# - **GNSS: treated as UTC/GPST.** RTKLIB writes solution epochs in GPST (UTC + 18 s)
#   or UTC; the code sets `dlt=0; % local time difference`. An 18 s difference is
#   irrelevant at hourly resolution.
# - **Tide: very likely local time, UTC+3.** The floating-ice borehole BH2203 best
#   matches the raw tide record shifted by **+2.75 h** (r = 0.965; lag scan in
#   `03_analysis.py`). The code's "2.5 hours lag!" plus the SI's extra 0.25 h gives
#   the same total. A hydrostatic response of floating ice 25 km from the gauge
#   cannot lag by ~3 h; a 3 h clock difference (Syowa local time is UTC+3, as for
#   the JMA records in `GAP_SOURCES.md` B1) minus a ~0.25 h physical lag can.
#   The raw tide timestamps are stored unchanged here; the shift is applied in 03.

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Transformer

# %%
DEPOSIT = Path("../data/raw/mendeley/Field data from Langhovde Glacier and MATLAB code")
FIG3 = DEPOSIT / "fig3"
CLEAN_DIR = Path("../data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
if not FIG3.exists():
    raise FileNotFoundError(f"{FIG3} not found: run 01_data_download.py first")

SOURCE = "Sugiyama et al. (2026) Mendeley Data doi:10.17632/8wvtxg53ry.1 (CC BY 4.0)"


def write_nc(ds: xr.Dataset, name: str) -> None:
    ds.attrs.setdefault("source", SOURCE)
    ds.attrs.setdefault("Conventions", "CF-1.8")
    path = CLEAN_DIR / name
    enc = {"time": {"units": "seconds since 2021-12-01 00:00:00", "dtype": "float64"}}
    ds.to_netcdf(path, encoding=enc)
    print(f"wrote {path} ({ds.sizes})")


# %% [markdown]
# ## GNSS positions → UTM zone 37S
#
# EPSG:4326 lat/lon to EPSG:32737 easting/northing with `pyproj` (the deposit's
# `latlon2utm.m` is missing). Height is ellipsoidal (m), as delivered.

# %%
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32737", always_xy=True)


def read_gnss(path: Path, station: str, file_role: str) -> xr.Dataset:
    df = pd.read_csv(path, header=None, skipinitialspace=True)
    t = pd.to_datetime(df[0], format="%Y/%m/%d %H:%M:%S.%f")
    lat, lon, h = df[1].to_numpy(), df[2].to_numpy(), df[3].to_numpy()
    x, y = TO_UTM.transform(lon, lat)
    ds = xr.Dataset(
        {
            "lat": ("time", lat, {"units": "degrees_north"}),
            "lon": ("time", lon, {"units": "degrees_east"}),
            "x": ("time", x, {"units": "m", "long_name": "UTM 37S easting (EPSG:32737)"}),
            "y": ("time", y, {"units": "m", "long_name": "UTM 37S northing (EPSG:32737)"}),
            "z": ("time", h, {"units": "m", "long_name": "ellipsoidal height"}),
        },
        coords={"time": t.to_numpy()},
        attrs={"station": station, "role": file_role, "raw_file": path.name,
               "time_base": "UTC/GPST (RTKLIB epochs; code applies no offset)"},
    )
    return ds


gnss1 = read_gnss(FIG3 / "LG05.dat", "GNSS1", "grounded, near BH2201/02")
gnss2 = read_gnss(FIG3 / "LG04.dat", "GNSS2", "afloat")
for ds in (gnss1, gnss2):
    dt = np.diff(ds.time.values) / np.timedelta64(1, "h")
    print(f"{ds.station}: {ds.time.values[0]} to {ds.time.values[-1]}, n={ds.sizes['time']}, "
          f"gaps > 24 h: {[(str(ds.time.values[i])[:16], round(dt[i], 1)) for i in np.where(dt > 24)[0]]}")
write_nc(gnss1, "gnss_GNSS1.nc")
write_nc(gnss2, "gnss_GNSS2.nc")

# %% [markdown]
# ## Borehole pressure
#
# Raw sensor values, publication names. BH2201 is in dbar (Valeport); the Geokon
# column 13 is in MPa (101.97 m of water per MPa in the code's conversion).

# %%
p1 = pd.read_csv(FIG3 / "pressure_eliminate1.dat", header=None, names=["t", "p"],
                 skipinitialspace=True)
p1["t"] = pd.to_datetime(p1["t"], format="%Y/%m/%d %H:%M:%S")
bh2201 = xr.Dataset(
    {"pressure": ("time", p1["p"].to_numpy(dtype=float), {"units": "dbar"})},
    coords={"time": p1["t"].to_numpy()},
    attrs={"borehole": "BH2201", "field_name": "BH2201", "sensor": "Valeport miniIPS",
           "raw_file": "pressure_eliminate1.dat", "z_bed_m": -436.1,
           "time_base": "logger clock, consistent with UTC"},
)
print(f"BH2201: n={bh2201.sizes['time']}, NaN={int(bh2201.pressure.isnull().sum())}")


def read_geokon(path: Path, name: str, field_name: str, z_bed: float) -> xr.Dataset:
    g = pd.read_csv(path, header=None)
    t = pd.to_datetime(g[0], format="%Y-%m-%d %H:%M:%S")
    return xr.Dataset(
        {"pressure": ("time", g[12].to_numpy(dtype=float), {"units": "MPa"})},
        coords={"time": t.to_numpy()},
        attrs={"borehole": name, "field_name": field_name, "sensor": "Geokon 4500S (AVW200)",
               "raw_file": path.name, "raw_column": 13, "z_bed_m": z_bed,
               "time_base": "logger clock, consistent with UTC"},
    )


bh2202 = read_geokon(FIG3 / "geokon_pressure2_AVW200_220206.dat", "BH2202", "BH2202", -436.1)
bh2203 = read_geokon(FIG3 / "geokon_pressure_AVW200_220206.dat", "BH2203", "BH2205", -398.1)
for ds in (bh2201, bh2202, bh2203):
    print(f"{ds.borehole}: {ds.time.values[0]} to {ds.time.values[-1]}")
    write_nc(ds, f"pressure_{ds.borehole}.nc")

# %% [markdown]
# ## Tide (Syowa, 30 s)
#
# Each record is `YYYYMMDDHHMMSS+f1+f2+f3+f4`; the code reads `f2` (mm). Stored in
# metres, raw timestamps, mean **not** removed (03 removes it, as the code does).

# %%
raw = pd.read_csv(FIG3 / "tide_211231_220206.dat", header=None, dtype=str)[0].str.split("+", expand=True)
tide = xr.Dataset(
    {"tide": ("time", raw[2].astype(float).to_numpy() * 1e-3,
              {"units": "m", "long_name": "Syowa tide gauge level (field 2 of record)"})},
    coords={"time": pd.to_datetime(raw[0], format="%Y%m%d%H%M%S").to_numpy()},
    attrs={"raw_file": "tide_211231_220206.dat",
           "time_base": "raw timestamps; inferred local time UTC+3 (see notebook 02 header)"},
)
write_nc(tide, "tide.nc")

# %% [markdown]
# ## On-glacier AWS (10 min)
#
# Columns: wind speed, wind direction, air temperature, rain accumulated since the
# last 00:00 (the 00:00 record closes the previous day, then the counter resets),
# rain intensity. The final record (6 Feb 13:10, after a 4 h gap) is all zeros and
# is treated as a logger terminator.

# %%
a = pd.read_csv(FIG3 / "aws211219_220206.dat", header=None, skipinitialspace=True)
a[0] = pd.to_datetime(a[0].str.replace("\t", " "), format="%Y/%m/%d %H:%M")
blank = (a[1] == 0) & (a[2] == 0) & (a[3] == 0) & (a[4] == 0)
print(f"AWS: dropping {int(blank.sum())} all-zero record(s): {a.loc[blank, 0].astype(str).tolist()}")
a = a[~blank]
aws = xr.Dataset(
    {
        "wind_speed": ("time", a[1].to_numpy(float), {"units": "m s-1"}),
        "wind_direction": ("time", a[2].to_numpy(float), {"units": "degree"}),
        "air_temperature": ("time", a[3].to_numpy(float), {"units": "degC"}),
        "rain_accum": ("time", a[4].to_numpy(float), {"units": "mm", "long_name": "rain since last 00:00"}),
        "rain_intensity": ("time", a[5].to_numpy(float), {"units": "mm h-1"}),
    },
    coords={"time": a[0].to_numpy()},
    attrs={"raw_file": "aws211219_220206.dat", "time_base": "UTC (diurnal-cycle check below)"},
)
diurnal = aws.air_temperature.groupby("time.hour").mean()
print("AWS mean T by hour (h: degC):", {int(h): round(float(v), 2) for h, v in zip(diurnal.hour, diurnal)})
print(f"hours with mean T > 0: {[int(h) for h in diurnal.hour[diurnal > 0]]}; "
      f"coldest hour: {int(diurnal.idxmin())}")
write_nc(aws, "aws.nc")

# %% [markdown]
# ## Syowa daily temperature, December–January 1989/90–2025/26

# %%
s = pd.read_csv(DEPOSIT / "figS3" / "1989_2026_temperature.dat", header=None,
                names=["date", "t_mean", "t_max", "t_min"])
s["date"] = pd.to_datetime(s["date"], format="%Y/%m/%d")
s["season"] = np.where(s["date"].dt.month == 12, s["date"].dt.year + 1, s["date"].dt.year)
counts = s.groupby("season").size()
print(f"Syowa: {s['date'].iloc[0].date()} to {s['date'].iloc[-1].date()}, {len(counts)} seasons, "
      f"days/season: {sorted(counts.unique())}")
syowa = xr.Dataset(
    {c: ("time", s[c].to_numpy(float), {"units": "degC"}) for c in ["t_mean", "t_max", "t_min"]}
    | {"season": ("time", s["season"].to_numpy(), {"long_name": "year of the January in the Dec-Jan season"})},
    coords={"time": s["date"].to_numpy()},
    attrs={"raw_file": "1989_2026_temperature.dat", "station": "Syowa (JMA 89532)"},
)
write_nc(syowa, "syowa_temperature.nc")

# %% [markdown]
# ## JMA Syowa daily weather summaries (Arm B)
#
# One HTML page per month (`01_data_download.py`). Each day row gives station and
# sea-level pressure, daily mean/max/min temperature, and the weather summary for
# daytime (06–18) and night-time (18–06 next day), in Syowa local time (UTC+3).
# Syowa has no precipitation gauge: the precipitation columns are empty. JMA quality
# marks (e.g. `)`, `]`) are kept in the raw text and stripped from numbers.

# %%
import html  # noqa: E402
import re  # noqa: E402

JMA_DIR = Path("../data/raw/jma")
ROW = re.compile(r'<tr class="mtx"[^>]*>(.*?)</tr>', re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)


def _num(text: str) -> float:
    m = re.search(r"-?\d+(\.\d+)?", text)
    return float(m.group()) if m else np.nan


records = []
for path in sorted(JMA_DIR.glob("syowa_daily_*.html")):
    y, mth = int(path.stem[-6:-2]), int(path.stem[-2:])
    for row in ROW.findall(path.read_text(encoding="utf-8", errors="replace")):
        cells = [html.unescape(re.sub("<[^>]+>", "", c)).strip() for c in CELL.findall(row)]
        if len(cells) != 21 or not cells[0].isdigit():
            continue
        records.append(dict(date=pd.Timestamp(y, mth, int(cells[0])), p_station_hpa=_num(cells[1]),
                            t_mean=_num(cells[6]), t_max=_num(cells[7]), t_min=_num(cells[8]),
                            summary_day=cells[19], summary_night=cells[20]))
jma = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
n_months = jma.date.dt.to_period("M").nunique()
print(f"JMA: {len(jma)} days in {n_months} months, {jma.date.min().date()} to {jma.date.max().date()}; "
      f"days with a summary: {int(((jma.summary_day != '') | (jma.summary_night != '')).sum())}")
jma.to_parquet(CLEAN_DIR / "jma_syowa_daily.parquet", index=False)

# %% [markdown]
# ## JMA Syowa hourly station pressure (Arm B)
#
# Hours 1–24 are Syowa local time (UTC+3); hour 24 is midnight at the end of the day.
# Stored in UTC.

# %%
hourly = []
for path in sorted(Path("../data/raw/jma_hourly").glob("syowa_hourly_*.html")):
    day = pd.Timestamp(path.stem[-8:])
    for row in ROW.findall(path.read_text(encoding="utf-8", errors="replace")):
        cells = [html.unescape(re.sub("<[^>]+>", "", c)).strip() for c in CELL.findall(row)]
        if len(cells) < 2 or not cells[0].isdigit():
            continue
        t_local = day + pd.Timedelta(hours=int(cells[0]))
        hourly.append(dict(time=t_local - pd.Timedelta(hours=3), p_station_hpa=_num(cells[1])))
jma_h = pd.DataFrame(hourly).sort_values("time").drop_duplicates("time").reset_index(drop=True)
print(f"JMA hourly: {len(jma_h)} hours, {jma_h.time.min()} to {jma_h.time.max()} UTC, "
      f"pressure {jma_h.p_station_hpa.min():.1f}–{jma_h.p_station_hpa.max():.1f} hPa, "
      f"missing {int(jma_h.p_station_hpa.isna().sum())}")
jma_h.to_parquet(CLEAN_DIR / "jma_syowa_hourly.parquet", index=False)
