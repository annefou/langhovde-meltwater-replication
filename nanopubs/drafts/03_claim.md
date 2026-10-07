# 03 — FORRT Claim

> Fields from the live template (`template_fields("03_claim")`, 2026-10-07): claim (required), label (required), aida (required; filled by the chain wizard), forrtType (required, restricted choice), source (optional, full URL). Claim type chosen with `docs/claim-type-vocabulary.md`.

**Form heading:** *"FORRT Claim — Declare an original claim according to FORRT, linking it to an AIDA sentence with a specific FORRT type."*

## Field-by-field draft

<!-- field: claim -->
### Short URI suffix as claim ID (text input, required)

```
langhovde-meltwater-acceleration-claim
```

<!-- field: label -->
### Label of the claim, to find it later (text input, required)

```
Meltwater-driven acceleration of grounded ice at Langhovde Glacier, Antarctica (Sugiyama et al. 2026)
```

<!-- field: aida -->
### Search for an AIDA sentence (search/select, required)

The AIDA URI from step 02; the chain wizard fills it in.

```

```

<!-- field: forrtType -->
### Type of FORRT claim (dropdown, required)

The claim asserts an observed empirical relationship: meltwater input to the bed, then acceleration. It is not a test result or a model's accuracy.

- [ ] computational performance (Computational & Performance)
- [ ] data governance (access control, licensing, FAIR compliance)
- [ ] data quality (preprocessing, validation, normalization)
- [x] descriptive pattern (distribution, trend, proportion)
- [ ] model performance (accuracy, F1 score, evaluation metrics)
- [ ] scalability (Computational & Performance)
- [ ] statistical significance (significant difference, relationship, or effect)

<!-- field: source -->
### Source URI (text input, optional)

```
https://doi.org/10.1038/s41467-026-72724-x
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 03.
