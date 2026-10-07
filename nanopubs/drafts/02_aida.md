# 02 — AIDA Sentence

> Fields from the live template `https://w3id.org/np/RALmXhDw3rHcMveTgbv8VtWxijUHwnSqhCmtJFIPKWVaA` (`template_fields("02_aida")`, source: live, 2026-10-07): aida (required; regex `[\S ]{5,500}\.`), topic (optional, repeatable, Wikidata), project (required; filled by the chain wizard), dataset (optional, repeatable), publication (optional, repeatable).

**Form heading:** *"AIDA Sentence — Make structured scientific claims following the AIDA model"*

## Field-by-field draft

<!-- field: aida -->
### AIDA sentence (text input, required)

Atomic, Independent, Declarative, Absolute. One empirical finding. Must end with a full stop.

> Restates the paper's headline claim (the quote in `01_quote.md`) as one finding, at the paper's own scope ("in Antarctica"). The Outcome then judges that scope. Alternative at site scope, if Anne prefers: "Surface meltwater that reaches the glacier bed accelerated grounded ice at Langhovde Glacier in summer 2021/22." Single finding, no hedge.

```
Surface meltwater that reaches the bed of grounded Antarctic ice accelerates its flow.
```

<!-- field: topic -->
### Select related topics/tags (search/select, optional)

Wikidata items checked with `wikidata_lookup` on 2026-10-07. The template restricts this field to concepts (Wikidata classes with P279), so place names such as Langhovde Glacier (Q6486120) and Antarctic ice sheet (Q571430) go in the Study keywords instead. Basal sliding (Q3962812) has no type statements and is rejected.

```
meltwater (Q360925)
glacier (Q35666)
ice sheet (Q12599)
ice-sheet dynamics (Q4290336)
```

<!-- field: project -->
### Relates to this nanopublication (search/select, required)

The Quote-with-comment URI from step 01; the chain wizard fills it in.

```

```

<!-- field: dataset -->
### Supported by datasets (text input, optional)

- https://doi.org/10.17632/8wvtxg53ry.1

<!-- field: publication -->
### Supported by other publications (text input, optional)

*(skip — optional; the paper is already cited through the Quote, and filling both support fields has caused publishing failures, see below)*

> **Known platform bug (2026-04-26):** if both *Supported by datasets* AND *Supported by other publications* are populated and publishing fails, fall back to publishing this AIDA via Nanodash. The URI namespace becomes `https://w3id.org/np/...` (still valid and citable).

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 02.
