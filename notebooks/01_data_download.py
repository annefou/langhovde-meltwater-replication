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
# # 01 — Data download
#
# Fetches the authors' data deposit for Sugiyama et al. (2026), *Acceleration of an
# Antarctic outlet glacier driven by surface meltwater input to the base*
# (Nature Communications, [doi:10.1038/s41467-026-72724-x](https://doi.org/10.1038/s41467-026-72724-x)):
#
# - **Mendeley Data** [doi:10.17632/8wvtxg53ry.1](https://doi.org/10.17632/8wvtxg53ry.1),
#   version 1, CC BY 4.0. GNSS positions, borehole pressure, AWS, Syowa tide and
#   temperature records, plus the authors' MATLAB plotting scripts.
#
# The deposit is fetched as one zip and extracted to `data/raw/mendeley/`. Each
# extracted file is checked against the SHA-256 that the Mendeley public API
# publishes for it, so a silently changed deposit fails here rather than downstream.
# The zip itself is generated on the fly by Mendeley, so its own hash is logged but
# not used for verification.
#
# No credentials are needed. Independent data for Arm B (JMA Syowa, ERA5, satellite
# imagery) is added in later cells as that arm starts.

# %%
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import xarray as xr
from pyproj import Transformer

SITES = {"GNSS1": (-69.214612056, 39.846029576), "GNSS2": (-69.203681309, 39.820243087)}   # first fixes, LG05/LG04

# %%
RAW_DIR = Path("../data/raw")
MENDELEY_DIR = RAW_DIR / "mendeley"
RAW_DIR.mkdir(parents=True, exist_ok=True)

DATASET_ID = "8wvtxg53ry"
VERSION = 1
API = "https://data.mendeley.com/public-api"
ZIP_URL = f"{API}/zip/{DATASET_ID}/download/{VERSION}"
ZIP_PATH = RAW_DIR / f"mendeley_{DATASET_ID}_v{VERSION}.zip"

SOURCES = [
    {
        "name": "Sugiyama et al. 2026 data deposit (Mendeley Data)",
        "doi": "10.17632/8wvtxg53ry.1",
        "url": ZIP_URL,
        "license": "CC-BY-4.0",
        "accessed_on": "2026-10-06",
        "sha256": None,  # zip hash, filled after download
    },
]


# %%
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def expected_checksums() -> dict[str, str]:
    """Map relative path -> SHA-256 for every file, from the Mendeley public API."""
    def files_in(folder_id: str) -> list[dict]:
        r = requests.get(
            f"{API}/datasets/{DATASET_ID}/files",
            params={"folder_id": folder_id, "version": VERSION},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()

    out = {f["filename"]: f["content_details"]["sha256_hash"] for f in files_in("root")}
    folders = requests.get(f"{API}/datasets/{DATASET_ID}/folders/{VERSION}", timeout=60)
    folders.raise_for_status()
    for folder in folders.json():
        for f in files_in(folder["id"]):
            out[f"{folder['name']}/{f['filename']}"] = f["content_details"]["sha256_hash"]
    return out


# %%
expected = expected_checksums()
print(f"Mendeley API lists {len(expected)} files")

# %% [markdown]
# ## Download and extract

# %%
if not ZIP_PATH.exists():
    with requests.get(ZIP_URL, stream=True, timeout=600) as r:
        r.raise_for_status()
        tmp = ZIP_PATH.with_suffix(".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
        tmp.rename(ZIP_PATH)
print(f"{ZIP_PATH.name}: {ZIP_PATH.stat().st_size / 1e6:.1f} MB")
SOURCES[0]["sha256"] = sha256(ZIP_PATH)

with zipfile.ZipFile(ZIP_PATH) as z:
    z.extractall(MENDELEY_DIR)

# %% [markdown]
# ## Verify against the published checksums

# %%
extracted = {
    p.relative_to(MENDELEY_DIR).as_posix(): p for p in MENDELEY_DIR.rglob("*") if p.is_file()
}
# The zip may wrap everything in a top-level directory; match on the API's relative paths.
def locate(rel: str) -> Path | None:
    matches = [p for k, p in extracted.items() if k == rel or k.endswith("/" + rel)]
    return matches[0] if len(matches) == 1 else None

manifest, problems = {}, []
for rel, want in sorted(expected.items()):
    path = locate(rel)
    if path is None:
        problems.append(f"missing or ambiguous: {rel}")
        continue
    got = sha256(path)
    manifest[rel] = got
    if got != want:
        problems.append(f"checksum mismatch: {rel}")

unexpected = len(extracted) - len(manifest)
print(f"verified {len(manifest) - sum('mismatch' in p for p in problems)}/{len(expected)} files; "
      f"{unexpected} extra file(s) in zip")
if problems:
    raise RuntimeError("Deposit verification failed:\n" + "\n".join(problems))

# %% [markdown]
# ## Syowa tide gauge in UTC (IOC), for the clock check
#
# The deposit's tide file has no time zone. The same gauge (JCG Hydrographic and
# Oceanographic Department, Nisi-no-ura Cove) is mirrored by the IOC Sea Level Station
# Monitoring Facility (station `syow`) with UTC timestamps. Three days are enough to
# measure the offset in `03_analysis.py`. The data are real time and not quality
# controlled (fill value 100 m), so we use them only to check the clock.

# %%
IOC_URL = ("https://www.ioc-sealevelmonitoring.org/service.php?query=data&code=syow"
           "&timestart=2022-01-25&timestop=2022-01-28&format=json")
IOC_PATH = RAW_DIR / "ioc_syow_20220125_20220128.json"
if not IOC_PATH.exists():
    r = requests.get(IOC_URL, timeout=120)
    r.raise_for_status()
    IOC_PATH.write_bytes(r.content)
SOURCES.append({
    "name": "IOC Sea Level Station Monitoring Facility, Syowa (syow), 2022-01-25 to 2022-01-28, UTC",
    "doi": None,
    "url": IOC_URL,
    "license": "IOC SLSMF terms of use (real-time, non-quality-controlled)",
    "accessed_on": "2026-10-07",
    "sha256": sha256(IOC_PATH),
})
print(f"{IOC_PATH.name}: {len(json.loads(IOC_PATH.read_text()))} records")

# %% [markdown]
# ## JMA Syowa daily weather summaries, December 1989 – March 2026 (Arm B)
#
# Japan Meteorological Agency past weather data for Syowa (station 89532), one HTML page
# per month. The daytime and night-time weather summaries (天気概況) are the only rain
# record at Syowa, which has no precipitation gauge. Pages are cached, so only missing
# months are fetched (one request per second). The licence is the JMA website terms
# (Public Data Terms of Use v1.0, attribution required).

# %%
import time  # noqa: E402

JMA_DIR = RAW_DIR / "jma"
JMA_DIR.mkdir(exist_ok=True)
JMA_URL = ("https://www.data.jma.go.jp/stats/etrn/view/daily_s1.php"
           "?prec_no=99&block_no=89532&year={y}&month={m}&day=&view=")
months = [(y, m) for y in range(1989, 2027) for m in range(1, 13) if (y, m) >= (1989, 12) and (y, m) <= (2026, 3)]
fetched = 0
for y, m in months:
    path = JMA_DIR / f"syowa_daily_{y}{m:02d}.html"
    if path.exists():
        continue
    r = requests.get(JMA_URL.format(y=y, m=m), timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    fetched += 1
    time.sleep(1)
SOURCES.append({
    "name": "JMA past weather data, Syowa (89532), daily values incl. weather summaries, 1989-12 to 2026-03",
    "doi": None,
    "url": JMA_URL.format(y="YYYY", m="M"),
    "license": "JMA website terms (Public Data Terms of Use v1.0, attribution)",
    "accessed_on": "2026-10-07",
    "sha256": None,  # one file per month; see data/raw/jma/
})
print(f"JMA: {len(months)} months, {fetched} fetched now, {len(list(JMA_DIR.glob('*.html')))} cached")

# %% [markdown]
# ## JMA Syowa hourly station pressure, 31 Dec 2021 – 6 Feb 2022 (Arm B, B-pressure)
#
# One page per day, hours 1–24 in Syowa local time (UTC+3). Same terms as above.

# %%
JMA_H_DIR = RAW_DIR / "jma_hourly"
JMA_H_DIR.mkdir(exist_ok=True)
JMA_H_URL = ("https://www.data.jma.go.jp/stats/etrn/view/hourly_s1.php"
             "?prec_no=99&block_no=89532&year={y}&month={m}&day={d}&view=")
days = pd.date_range("2021-12-31", "2022-02-06", freq="D")
for day in days:
    path = JMA_H_DIR / f"syowa_hourly_{day:%Y%m%d}.html"
    if not path.exists():
        r = requests.get(JMA_H_URL.format(y=day.year, m=day.month, d=day.day), timeout=60)
        r.raise_for_status()
        path.write_bytes(r.content)
        time.sleep(1)
SOURCES.append({
    "name": "JMA past weather data, Syowa (89532), hourly values, 2021-12-31 to 2022-02-06",
    "doi": None, "url": JMA_H_URL.format(y="YYYY", m="M", d="D"),
    "license": "JMA website terms (Public Data Terms of Use v1.0, attribution)",
    "accessed_on": "2026-10-07", "sha256": None,
})
print(f"JMA hourly: {len(list(JMA_H_DIR.glob('*.html')))} days cached")

# %% [markdown]
# ## Atmospheric-river days at Syowa (Arm B, B-AR)
#
# Favier (2025), merged ERA5–MERRA-2 AR catalogues at staffed Antarctic stations,
# doi:10.5281/zenodo.17165410 (CC BY 4.0). One date per AR-associated day. The
# record's ±1-day convention is already applied; the documented span is 1980 to March 2022.

# %%
AR_URL = "https://zenodo.org/api/records/17165410/files/Syowa_ARday.csv/content"
AR_PATH = RAW_DIR / "favier2025_Syowa_ARday.csv"
if not AR_PATH.exists():
    r = requests.get(AR_URL, timeout=120)
    r.raise_for_status()
    AR_PATH.write_bytes(r.content)
SOURCES.append({
    "name": "Favier (2025) merged ERA5-MERRA-2 atmospheric river catalogs at staffed Antarctic stations: Syowa",
    "doi": "10.5281/zenodo.17165410", "url": AR_URL, "license": "CC-BY-4.0",
    "accessed_on": "2026-10-07", "sha256": sha256(AR_PATH),
})
print(f"{AR_PATH.name}: {sum(1 for _ in AR_PATH.open())} AR days")

# %% [markdown]
# ## ERA5 hourly 2 m temperature at Langhovde, December–January 1989–2026 (Arm B, B-temp)
#
# ERA5 hourly single levels (doi:10.24381/cds.adbb2d47, CC BY 4.0), read from ECMWF's
# analysis-ready cloud-optimised (ARCO) Zarr store. The store is geo-chunked for point
# time series. Authentication uses the CDS API key as a Bearer token, from `CDSAPI_KEY`
# or the `key:` line of `~/.cdsapirc` (https://cds.climate.copernicus.eu/how-to-api).
# In CI, set `CDSAPI_KEY` from a secret. The key is never printed.

# %%
import os  # noqa: E402
import re  # noqa: E402

ERA5_ARCO = "https://arco.datastores.ecmwf.int/cadl-arco-geo-002/arco/reanalysis_era5_single_levels/sfc/geoChunked.zarr"
ERA5_PATH = RAW_DIR / "era5_arco_t2m_gnss1_dec_jan_1989_2026.nc"


def cds_key() -> str:
    if os.environ.get("CDSAPI_KEY"):
        return os.environ["CDSAPI_KEY"]
    m = re.search(r"^key:\s*(\S+)", Path("~/.cdsapirc").expanduser().read_text(), re.M)
    if not m:
        raise RuntimeError("set CDSAPI_KEY or add 'key: ...' to ~/.cdsapirc")
    return m.group(1)


if not ERA5_PATH.exists():
    era5 = xr.open_zarr(ERA5_ARCO, consolidated=True,
                        storage_options={"headers": {"Authorization": f"Bearer {cds_key()}"}})
    lat, lon = SITES["GNSS1"]
    pt = era5.t2m.sel(latitude=lat, longitude=lon % 360, method="nearest")
    pt = pt.sel(time=slice("1989-12-01", "2026-01-31T23:00"))
    pt = pt.sel(time=pt.time.dt.month.isin([12, 1])).load()
    pt.attrs.update(source=ERA5_ARCO, note="ERA5 grid cell nearest GNSS1 (first fix of LG05)")
    pt.to_dataset(name="t2m").to_netcdf(ERA5_PATH)
SOURCES.append({
    "name": "ERA5 hourly 2 m temperature at the grid cell nearest GNSS1, Dec and Jan 1989-2026 (ECMWF ARCO Zarr)",
    "doi": "10.24381/cds.adbb2d47", "url": ERA5_ARCO, "license": "CC-BY-4.0",
    "accessed_on": "2026-10-07", "sha256": sha256(ERA5_PATH),
})
_e = xr.open_dataset(ERA5_PATH)
print(f"{ERA5_PATH.name}: {_e.sizes['time']} hours at {float(_e.latitude):.2f}, {float(_e.longitude):.2f}")

# %% [markdown]
# ## Passive-microwave surface melt, Antarctica (Arm B, B-melt)
#
# Daily wet/dry snow status from G. Picard (Université Grenoble Alpes):
# - SSM/I 19 GHz, 25 km, 1979–2025 (zip with NetCDF);
# - AMSR-E/AMSR2, 10 km, 2002–present.
#
# Method: Picard & Fily (2006), doi:10.1016/j.rse.2006.05.010. The site gives no
# dataset DOI or licence beyond use with citation.

# %%
MELT = {
    "ssmi_25km": ("https://snow.univ-grenoble-alpes.fr/files/melting-1979-2025-v1.zip", "melting-1979-2025-v1.zip"),
    "amsr_10km": ("https://snow.univ-grenoble-alpes.fr/opendata/melt-AMSRJ-antarctic-10km.nc",
                  "melt-AMSRJ-antarctic-10km.nc"),
}
MELT_DIR = RAW_DIR / "melt"
MELT_DIR.mkdir(exist_ok=True)
for key, (url, fname) in MELT.items():
    path = MELT_DIR / fname
    if not path.exists():
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            tmp = path.with_suffix(".part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
            tmp.rename(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            z.extract("CumJour-Antarctic-ssmi-1979-2025-H19.nc", MELT_DIR)
    SOURCES.append({"name": f"Picard surface melt, {key}", "doi": None, "url": url,
                    "license": "cite Picard & Fily 2006 (doi:10.1016/j.rse.2006.05.010)",
                    "accessed_on": "2026-10-07", "sha256": sha256(path)})
print("melt:", sorted(p.name for p in MELT_DIR.iterdir()))

# %% [markdown]
# ## ITS_LIVE v2 image-pair velocities at the GNSS sites (Arm B, B-velocity)
#
# NASA MEaSUREs ITS_LIVE version 2 datacube (Zarr on public S3) for the 120 m tile
# containing Langhovde. For each GNSS site, the pixel containing its first position:
# every image pair with both acquisitions between 2021-12-01 and 2022-02-10.
# Velocities in m/yr. Landsat pairs: doi:10.5067/IMR9D3PEI28U; Sentinel-1:
# doi:10.5067/0506KQLS6512. NASA open data.

# %%
ITS_URL = ("https://its-live-data.s3.amazonaws.com/datacubes/v2-updated-october2024/S60E030/"
           "ITS_LIVE_vel_EPSG3031_G0120_X1450000_Y1750000.zarr")
ITS_PATH = RAW_DIR / "itslive_gnss_pixels_202112_202202.nc"
if not ITS_PATH.exists():
    cube = xr.open_dataset(ITS_URL, engine="zarr", consolidated=True)
    to_ps = Transformer.from_crs("EPSG:4326", "EPSG:3031", always_xy=True)
    keep = ["v", "v_error", "vx", "vy", "acquisition_date_img1", "acquisition_date_img2", "satellite_img1",
            "satellite_img2", "date_dt", "roi_valid_percentage", "granule_url"]
    parts = []
    for site, (lat, lon) in SITES.items():
        x, y = to_ps.transform(lon, lat)
        px = cube[keep].sel(x=x, y=y, method="nearest")
        a1, a2 = px.acquisition_date_img1.load(), px.acquisition_date_img2.load()
        sel = (a1 >= np.datetime64("2021-12-01")) & (a2 <= np.datetime64("2022-02-10"))
        parts.append(px.isel(mid_date=np.flatnonzero(sel.values)).load().expand_dims(site=[site]))
    out = xr.concat(parts, dim="site", join="outer")
    for k in out.data_vars:
        out[k].encoding = {}
    out.attrs = {"source": ITS_URL, "selection": "pixel nearest each GNSS site; pairs within 2021-12-01..2022-02-10"}
    out.to_netcdf(ITS_PATH)
SOURCES.append({"name": "ITS_LIVE v2 datacube pixels at GNSS1/GNSS2, Dec 2021 - Feb 2022", "doi": "10.5067/IMR9D3PEI28U",
                "url": ITS_URL, "license": "NASA open data", "accessed_on": "2026-10-07", "sha256": sha256(ITS_PATH)})
print(f"{ITS_PATH.name}: {xr.open_dataset(ITS_PATH).sizes}")

# %% [markdown]
# ## Sentinel-2 L2A subsets around GNSS1 (Arm B, B-optical)
#
# Element84 Earth Search STAC (`sentinel-2-l2a`). For every scene intersecting GNSS1
# between 10 Dec 2021 and 25 Jan 2022, a 2 km × 2 km box centred on GNSS1 is read
# from the cloud-optimised GeoTIFFs:
# - B03 (green) and B08 (NIR) at 10 m;
# - the scene classification (SCL, 20 m), resampled nearest to 10 m.
#
# Copernicus Sentinel data, free and open licence.

# %%
import rasterio  # noqa: E402
from pystac_client import Client  # noqa: E402
from rasterio.enums import Resampling  # noqa: E402
from rasterio.warp import transform_bounds  # noqa: E402
from rasterio.windows import from_bounds  # noqa: E402

S2_DIR = RAW_DIR / "s2"
S2_DIR.mkdir(exist_ok=True)
g1_lat, g1_lon = SITES["GNSS1"]
gx, gy = Transformer.from_crs("EPSG:4326", "EPSG:32737", always_xy=True).transform(g1_lon, g1_lat)
BOX = (gx - 1000, gy - 1000, gx + 1000, gy + 1000)                      # EPSG:32737
items = Client.open("https://earth-search.aws.element84.com/v1").search(
    collections=["sentinel-2-l2a"], intersects={"type": "Point", "coordinates": [g1_lon, g1_lat]},
    datetime="2021-12-10/2022-01-25").item_collection()
for item in items:
    path = S2_DIR / f"{item.id}.nc"
    if path.exists():
        continue
    bands = {}
    for name, asset in [("green", "green"), ("nir", "nir"), ("scl", "scl")]:
        with rasterio.open(item.assets[asset].href) as src:
            bounds = transform_bounds("EPSG:32737", src.crs, *BOX)
            win = from_bounds(*bounds, transform=src.transform)
            bands[name] = src.read(1, window=win, out_shape=(200, 200), resampling=Resampling.nearest,
                                   boundless=True, fill_value=0)
    xr.Dataset({k: (("y", "x"), v) for k, v in bands.items()},
               attrs={"item": item.id, "datetime": str(item.datetime), "box_epsg32737": str(BOX),
                      "platform": item.properties.get("platform", ""),
                      # Baseline >= 04.00 adds a BOA offset of -1000 unless already removed upstream.
                      "processing_baseline": str(item.properties.get("s2:processing_baseline", "")),
                      "boa_offset_applied": str(item.properties.get("earthsearch:boa_offset_applied", ""))}
               ).to_netcdf(path)
SOURCES.append({"name": "Sentinel-2 L2A 2 km subsets around GNSS1, 2021-12-10 to 2022-01-25 (Element84 Earth Search)",
                "doi": None, "url": "https://earth-search.aws.element84.com/v1", "license": "Copernicus free and open",
                "accessed_on": "2026-10-07", "sha256": None})
print(f"Sentinel-2: {len(items)} scenes found, {len(list(S2_DIR.glob('*.nc')))} subsets cached")

# %% [markdown]
# ## Source log

# %%
with open(RAW_DIR / "sources.json", "w") as f:
    json.dump({"sources": SOURCES, "mendeley_files_sha256": manifest}, f, indent=2)
print(f"Logged {len(SOURCES)} source(s) and {len(manifest)} file checksums to {RAW_DIR / 'sources.json'}")
