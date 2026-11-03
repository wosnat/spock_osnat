# Proposal notebook

## Grounding queries (2026-11-03)
- `kg_release_info` → KG 0.1.0-alpha.9, explorer 0.1.0-alpha.6, verdict ok.
- `list_experiments(search_text="urea")` → 4 hits; 2 relevant (Tolonen 2006 urea vs Pro99,
  MED4 + MIT9313, microarray, all_detected_genes, matched control). 2 Pandhal light proteomics
  hits are irrelevant (text match only).
- `resolve_gene("ntcA")` → PMM0246 (MED4), PMT1831 (MIT9313).
- `genes_by_function` for N genes in MED4 and MIT9313 → ure/urt/amt1/glnA/glnB/pipX locus tags.

## Decisions
- Readout = ntcA transcript only (researcher choice). Regulon-level readout rejected for this exercise.
- Slug `2026-11-03-ntca_urea_response` approved.
- Critical review: 3 concerns + 1 note, all fixed — see proposal_critical_review.md
- Design review: control bar (≥2 sig up or median ≥0.5 & ≥75% positive) and 75th-percentile suggestive cutoff confirmed as written; no change → no delta critic pass. Plan approved.
- Design review round 2: researcher added N-deprivation (ntcA detectability control; MED4 12h+24h, MIT9313 12h) and cyanate/nitrite (alt-N comparison, cyanate gated on identity check vs urea — identical sig counts 14/5 observed).
