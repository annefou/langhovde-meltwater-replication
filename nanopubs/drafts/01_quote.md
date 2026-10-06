# 01 — Quote-with-comment (paper-rooted chains)

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> If this is a question-rooted chain, use `01_pico.md` or `01_pcc.md` instead — see `docs/chain-decision-tree.md`.
>
> **After choosing the chain shape, delete the two step-1 alternates you aren't using.** Once you've decided this chain is paper-rooted and keep `01_quote.md`, run:
> ```bash
> rm nanopubs/drafts/01_pico.md nanopubs/drafts/01_pcc.md
> ```

**Form heading:** *"Annotate a paper quotation — Annotating a paper quotation with personal interpretation"*

## Field-by-field draft

<!-- field: paper -->
### Cited DOI (text input, required)

Format: starts with `10.` — bare DOI, **NOT** `https://doi.org/...` form.

```
10.1038/s41467-026-72724-x
```

### Quote mode (radio button)

- [x] **Quote whole text (less than 500 characters)**
- [ ] Quote start/end *(use this if the quote exceeds 500 chars)*

<!-- field: quotation -->
### The exact quotation from the paper (max. 500 characters) (textarea, required)

Verbatim from the paper PDF in `paper/`. Character-for-character. ≤ 500 chars in whole-text mode.

> Headline candidate (abstract, p. 1). Verified with `verify_quote` against
> `paper/sugiyama-2026.pdf` (SHA-256 `493bbafd6e92f24b0ebfb384346d67a71510950c9b79edf12618af95c5560a3b`):
> found on page 1. The tool's verdict was `whitespace_insensitive` only because the pypdf text
> layer glues "of" and "grounded" together across a line break ("ofgrounded"); `pdftotext`
> reads the same line as "acceleration of grounded ice in Antarctica." with the space in
> place. Every letter, digit and its order matched. Accepted by Anne on 2026-10-06 as the headline quote; the alternatives below are kept for reference.

```
Our in-situ measurements confirm meltwater-driven acceleration of grounded ice in Antarctica.
```

Character count: 93 / 500 (template regex `[\s\S]{5,500}`, confirmed live via `template_fields("01_quote")`).

<!-- field: quotation-end -->
### End of quotation (optional - use when quoting beginning and end of a longer passage, max. 500 characters) (textarea, optional)

Only when quoting the beginning *and* end of a longer passage — set the mode above to
**Quote start/end**, put the opening phrase under the previous heading and the closing
phrase here. Leave empty for a single short quote.

*(skip — optional; whole-text mode)*

```

```

<!-- field: comment -->
### Our interpretation and explanation of why this quotation is relevant (max. 800 characters) (textarea, required)

Why this quote matters on its own terms (see `docs/forrt-form-fields.md`: the comment must stand independently of any replication; the live form caps it at 500 characters even though the template regex reads 800).

> **Accepted by Anne on 2026-10-06.** 484 / 500 characters. Each point of context is checked against the paper:
> mountain glaciers and Greenland ("Borehole observations in mountain glaciers have shown ice acceleration during
> periods of elevated water pressure…, and similar observations have been reported in Greenland", Introduction);
> sparse Antarctic observations ("…beneath grounded ice in Antarctica are sparse"); pressure was recorded for
> Period II only (sensor installed 31 December, after Period I); more melt expected ("Under a warming climate
> projected in Antarctica, meltwater production and its impact on glacier dynamics are expected to increase along
> the coast", Discussion). The comment does not mention the replication, per the form rules.

```
Meltwater-driven acceleration through elevated basal water pressure is known from mountain glaciers and Greenland, but direct observations beneath grounded Antarctic ice are sparse. This sentence claims that link for Langhovde Glacier, based on borehole pressure and GNSS speed and uplift. The evidence comes from one site in one summer, and pressure was recorded for only one of the two speed-up events. With more melt expected along the Antarctic coast, how general this is matters.
```

## Alternative quote candidates (all verified with `verify_quote`; pick one, or keep the headline)

All against `paper/sugiyama-2026.pdf`. A `whitespace_insensitive` verdict means pypdf split or merged words across a line break; the wording was checked against `pdftotext` output as well.

1. **Abstract, p. 1: speed-up plus uplift (sub-claims C3 + C4). 91 characters.** Verdict: `whitespace_insensitive` (pypdf reads "10- 20%" and "~0 .1 m").
   > Coinciding with these events, ice speed increased by 10–20% and the surface rose by ~0.1 m.

   Caveat: "these events" points back to the previous sentence, so read alone the quote does not say which events. It also joins two findings (speed and uplift), which is not atomic for AIDA.

2. **Abstract, p. 1: pressure above 90% of overburden, rising during melt and rain (C1 + C2). 172 characters.** Verdict: `normalized`.
   > Borehole measurements revealed that the subglacial water pressure exceeded 90% of the ice overburden and the pressure elevated during periods of intensive melting and rain.

   Caveat: says "during periods" (plural), but pressure was only recorded for Period II. The sensor went in on 31 December, after Period I.

3. **Discussion, p. 4: the body-text version of the headline (C5). 162 characters.** Verdict: `normalized`.
   > Our subglacial measurements and in-situ GNSS data confirm the influence of surface meltwater on subglacial pressure and its impact on glacier speed in Antarctica.

   Note: names the evidence (subglacial measurements plus GNSS) and the two links (meltwater → pressure → speed) more explicitly than the abstract sentence does.

4. **Results, p. 4: timing statement (C6). 95 characters.** Verdict: `normalized`.
   > The timing of the pressure peak broadly coincided with that of the ice speed peak (Fig. 3a, b).

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 01.
