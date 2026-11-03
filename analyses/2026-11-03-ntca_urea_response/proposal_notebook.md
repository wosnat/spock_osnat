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
