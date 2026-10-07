# 06 — CiTO Citation

> Fields from the live template `https://w3id.org/np/RA43F9EoOuzF0xoNUnCMNyFsfIqlsuWDdPHCnN0wCdCAw` (`template_fields("06_citation")`, source: live, 2026-10-07): work (required), cites (required, repeatable, CiTO value list), cited (required, repeatable). Relations from `vocabulary("cito_relation")`.

**Description:** *"Declare citations between papers or other works, using Citation Typing Ontology"*

## Field-by-field draft

<!-- field: work -->
### Identifier for the citing creative work (text input, required)

The Outcome URI from step 05; the chain wizard fills it in.

```

```

### List citations (repeatable group, required ≥1)

#### Citation 1 — back to the original paper

##### Citation Type (dropdown)

The Outcome is PartiallySupported, so the relation is `qualifies`.

```
qualifies
```

##### DOI or other URL of the cited work (text input)

```
https://doi.org/10.1038/s41467-026-72724-x
```

#### Additional citations (optional)

- Type: uses data from → URL: https://doi.org/10.17632/8wvtxg53ry.1
- Type: uses data from → URL: https://doi.org/10.5281/zenodo.17165410
- Type: uses data from → URL: https://doi.org/10.24381/cds.adbb2d47

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 06.

This completes the six-step FORRT chain. Optional next layers:

- **Research Software** (`drafts/07_research_software.md`) — if the repo *produces* a reusable software artefact.
- **Research Synthesis** (`drafts/08_synthesis.md`) — if this chain is one of several testing facets of a shared property.
