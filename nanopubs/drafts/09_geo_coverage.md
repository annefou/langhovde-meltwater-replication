# 09 — Geographical coverage (optional)

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting. Read `docs/geo-coverage.md` first.
>
> **When to draft this.** Only when the paper's findings have a **specific geographic
> scope** — a study area, region, country, transect, or named site (typical for
> earth-observation, biodiversity, ecology, epidemiology work). A non-spatial paper
> (e.g. a lab cognition study with no study area) has **no** geographic coverage —
> delete this draft and skip the step. Do not invent a location to fill the form.
>
> **What it documents.** The geographic coverage of the **original paper** (subject =
> the paper DOI), backed by a **verbatim quotation** from the paper that names the
> area. Grounded, Record-side — place name and quote from the PDF; geometry resolved
> by the form's map/geocoder, never hand-written. Publishes with the platform's
> existing **"Document geographical coverage"** template; discoverable via GeoSPARQL.

## More than one location

A paper can cover **several areas**. Handle it one of two ways:

- **Distinct study sites** (separately meaningful — e.g. two estuaries compared, three
  field sites): publish **one coverage nanopub per site**, so each is individually
  named, quoted, and spatially searchable. Duplicate the *per-location block* below,
  once per site — each with its **own** area name, **own** verbatim quote, and own
  geometry. This is the atomic default.
- **One pooled coverage** (regions the study treats as a single combined extent —
  e.g. "North America, the EU and Australia" pooled in one analysis): publish **one**
  nanopub. In the form's location search, add each place in turn — it merges them into
  a single `GEOMETRYCOLLECTION` under one combined label. Use one block below, list
  the places in the label, and quote the sentence that names them together.

If unsure, prefer separate nanopubs — atomic coverage is easier to search and cite.

## Shared field

<!-- field: paper -->
### Cited DOI (text input, required — same for every location)

The **original paper's** DOI (bare, starting `10.` — the form prepends `https://doi.org/`). Same DOI as the Quote (step 01) / CiTO (step 06). Read it from `CITATION.cff` `references:`; do not recall it.

```
10.1038/s41467-026-72724-x
```

---

## Per-location block — duplicate this whole section once per distinct site

> Publish one "Document geographical coverage" nanopub per block below. For a single
> location, keep one block. For a pooled multi-region coverage, keep one block and add
> each place in the form's location search (it builds the GeometryCollection).

### Location A — Langhovde Glacier (primary study area)

> Verified with `verify_quote` (`normalized`, p. 3, `paper/sugiyama-2026.pdf`). 214 characters. The paper text states no coordinates. Fig. 1a/b has graticule and UTM-style labels, but those are figure annotations, so `wkt` is left blank for the form geocoder or the map.

<!-- field: quoteType -->
**Quote type** (radio: whole | ends, required) — `whole` if under 500 characters (usual); `ends` only for a long start/end passage.

```
whole
```

<!-- field: quotation -->
**Quoted Text** (textarea, required) — the **verbatim** sentence from the paper naming *this* area. Character-for-character from the PDF; never paraphrase. Each location needs its own quote.

```
From December 2021 to February 2022, we conducted hot-water drilling, borehole and glacier surface measurements on Langhovde Glacier, a 3-km-wide outlet glacier located on Lützow-Holm Bay, East Antarctica (Fig. 1).
```

<!-- field: quotation-end -->
**Quoted Text End** (textarea, optional — only if quote type = ends). Leave blank for `whole`.

```

```

<!-- field: location -->
**Short ID for location** (text input, required) — slug for the URI suffix (lowercase, hyphenated), unique per location. E.g. `sado-estuary`, `westerschelde`, `amazon-basin`.

```
langhovde-glacier
```

<!-- field: location-label -->
**Area name** (text input, required) — human-readable name as the paper frames it. E.g. `Sado Estuary, Portugal`. Typing this into the form's **location search** geocodes it and fills the geometry.

```
Langhovde Glacier, Lützow-Holm Bay, East Antarctica
```

<!-- field: geometry -->
**Short ID for geometry** (text input, optional) — URI suffix for the geometry node; `coverage` is fine.

```
coverage
```

<!-- field: wkt -->
**Geometry as Well-known Text (WKT)** (map / text, resolved in the form) — **Do NOT hand-write coordinates.** The form geocodes the area name to a polygon, or you draw it on the map. Only paste explicit `POINT(...)` / `POLYGON((...))` if the paper **states coordinates verbatim** — copied exactly. A hallucinated bounding box is a fabricated datum; leave blank otherwise.

```

```

<!-- field: comment -->
**Comment** (textarea, required) — one or two sentences on **how the quoted text supports** this being the coverage. Grounded in the paper, no new claims.

```
The quoted Results sentence names Langhovde Glacier on Lützow-Holm Bay, East Antarctica, as the site of all drilling, borehole and surface measurements (December 2021 to February 2022). The paper's findings (basal water pressure, ice speed, uplift, tidal connection) all come from boreholes and GNSS stations on this glacier near its grounding line.
```

### Location B — Syowa Station (OPTIONAL: ancillary data site; delete this block if you only want the study area)

> Verified with `verify_quote` (`whitespace_insensitive`, p. 6; pdftotext confirms the word spacing). 162 characters. Recommendation: keep it only if you want the tide and climate data source to be place-searchable. The paper's findings are about Langhovde Glacier, not Syowa.

<!-- field: quoteType -->
**Quote type** (radio: whole | ends, required) — `whole` if under 500 characters (usual); `ends` only for a long start/end passage.

```
whole
```

<!-- field: quotation -->
**Quoted Text** (textarea, required) — the **verbatim** sentence from the paper naming *this* area. Character-for-character from the PDF; never paraphrase. Each location needs its own quote.

```
Ocean tide data are available at Syowa Station (Fig. 1a), where year-around sea-level measurements with pressure sensors have been performed since 1979 (ref. 69).
```

<!-- field: quotation-end -->
**Quoted Text End** (textarea, optional — only if quote type = ends). Leave blank for `whole`.

```

```

<!-- field: location -->
**Short ID for location** (text input, required) — slug for the URI suffix (lowercase, hyphenated), unique per location. E.g. `sado-estuary`, `westerschelde`, `amazon-basin`.

```
syowa-station
```

<!-- field: location-label -->
**Area name** (text input, required) — human-readable name as the paper frames it. E.g. `Sado Estuary, Portugal`. Typing this into the form's **location search** geocodes it and fills the geometry.

```
Syowa Station, Antarctica
```

<!-- field: geometry -->
**Short ID for geometry** (text input, optional) — URI suffix for the geometry node; `coverage` is fine.

```
coverage
```

<!-- field: wkt -->
**Geometry as Well-known Text (WKT)** (map / text, resolved in the form) — **Do NOT hand-write coordinates.** The form geocodes the area name to a polygon, or you draw it on the map. Only paste explicit `POINT(...)` / `POLYGON((...))` if the paper **states coordinates verbatim** — copied exactly. A hallucinated bounding box is a fabricated datum; leave blank otherwise.

```

```

<!-- field: comment -->
**Comment** (textarea, required) — one or two sentences on **how the quoted text supports** this being the coverage. Grounded in the paper, no new claims.

```
The quoted Methods sentence names Syowa Station as the source of the ocean tide record used to show that the glacier bed is hydraulically connected to the sub-shelf cavity. The same station supplies the long-term temperature and rain record behind the paper's climate context. It is an ancillary data site, not the glaciological study area.
```


## Publication note

Each location block is a **standalone** nanopub, not one of the six FORRT chain steps.
Publish each via the platform's **"Document geographical coverage"** template (Create →
that template). After publishing, paste each resulting URI into `nanopubs/PUBLISHED.md`
under a "Geographical coverage" row (one row per location) so `/verify-chain` and the
story page can find them.
