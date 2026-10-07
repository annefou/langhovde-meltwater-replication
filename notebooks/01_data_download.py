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

import requests

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
# ## Source log

# %%
with open(RAW_DIR / "sources.json", "w") as f:
    json.dump({"sources": SOURCES, "mendeley_files_sha256": manifest}, f, indent=2)
print(f"Logged {len(SOURCES)} source(s) and {len(manifest)} file checksums to {RAW_DIR / 'sources.json'}")
