# Published nanopub chain — URI registry

This file is the canonical registry of published nanopub URIs for this replication.

**Outcome:** partially supported (CiTO: *qualifies*), high confidence. The software release cited by the Outcome is v1.0.2, [doi:10.5281/zenodo.23257925](https://doi.org/10.5281/zenodo.23257925) (concept DOI [10.5281/zenodo.23257924](https://doi.org/10.5281/zenodo.23257924)). Reference paper: [doi:10.1038/s41467-026-72724-x](https://doi.org/10.1038/s41467-026-72724-x).

## Chain

| Step | Template | URI | Published |
|---|---|---|---|
| 01 | Quote-with-comment | [https://w3id.org/sciencelive/np/RADkPUhAtC5UJYyV-csRExs1Vbail-7MbZLUDmL-VquWA](https://w3id.org/sciencelive/np/RADkPUhAtC5UJYyV-csRExs1Vbail-7MbZLUDmL-VquWA) | 2026-10-09 |
| 02 | AIDA Sentence | [https://w3id.org/sciencelive/np/RAfKhugNjV0yN5oVrEQBr_JnjVx3NwgKe4eDjBlu6vAqY](https://w3id.org/sciencelive/np/RAfKhugNjV0yN5oVrEQBr_JnjVx3NwgKe4eDjBlu6vAqY) | 2026-10-09 |
| 03 | FORRT Claim | [https://w3id.org/sciencelive/np/RAm8LPD-uPRICSRaczUWa-k8dgyotonp8IdlG8kfAcFo0](https://w3id.org/sciencelive/np/RAm8LPD-uPRICSRaczUWa-k8dgyotonp8IdlG8kfAcFo0) | 2026-10-09 |
| 04 | FORRT Replication Study | [https://w3id.org/sciencelive/np/RAF0VQ4XaJBPc-9BUMoYnPnAxLA7z-UgBNidJVX2kR0Ck](https://w3id.org/sciencelive/np/RAF0VQ4XaJBPc-9BUMoYnPnAxLA7z-UgBNidJVX2kR0Ck) | 2026-10-09 |
| 05 | FORRT Replication Outcome | [https://w3id.org/sciencelive/np/RAQn6_6v0w8OARZmzh0BBV8maDh_dqNHBlYmgwzNMwGyo](https://w3id.org/sciencelive/np/RAQn6_6v0w8OARZmzh0BBV8maDh_dqNHBlYmgwzNMwGyo) | 2026-10-09 |
| 06 | CiTO Citation | [https://w3id.org/sciencelive/np/RAQrTZ5QeyY91Q8JcXIaK1agI4ZnaU1wPvFBa8MfP4NR4](https://w3id.org/sciencelive/np/RAQrTZ5QeyY91Q8JcXIaK1agI4ZnaU1wPvFBa8MfP4NR4) | 2026-10-09 |

## Verification (`/verify-chain`, 2026-10-09)

Ledger: `nanopubs/PUBLISHED.md` · mode: replication · steps published: 01–06
Cited paper: https://doi.org/10.1038/s41467-026-72724-x (source: cito-citedTargets)

| Check | Status | Notes |
|---|---|---|
| reachable | ✓ | steps 01–06 are each enumerated in the constellation |
| repository | ✓ | the Outcome pins an archived version DOI that resolves: 10.5281/zenodo.23257925 (langhovde-meltwater-replication) |
| verdict-relation | ✓ | verdict PartiallySupported matches CiTO qualifies |
| cited-target | ✓ | 10.1038/s41467-026-72724-x resolves: Acceleration of an Antarctic outlet glacier driven by surface meltwater input to the base |

**Verdict: GREEN.** The chain is internally consistent and externally resolves correctly.

## Optional layers

| Step | Template | URI | Published |
|---|---|---|---|
| 07 | Research Software (if applicable) | _not applicable: the repository is a replication pipeline, not a reusable installable tool_ | |
| 08 | Research Synthesis (if applicable) | _not applicable: a single chain_ | |

## Format

URIs from Science Live are of the form `https://w3id.org/sciencelive/np/RA…`. URIs from Nanodash (used as a fallback when the Science Live UI hits a bug) are of the form `https://w3id.org/np/RA…`. Both are valid and citable.

If a URI is not in the Science Live namespace, view it via the Science Live viewer by wrapping the URI:

```
https://platform.sciencelive4all.org/np/?uri=<full-URI>
```

## Cross-references

- Drafts: `nanopubs/drafts/`
- Form structure: `docs/forrt-form-fields.md`
- Chain shape decision: `docs/chain-decision-tree.md`
