# KG rules

Extends SKILL.md Rule 1 (KG is the sole data source) with
operational details for scoping, gap handling, and API choice.

## Common KG gaps
- Missing organisms or strains not yet in the KG
- Annotations not loaded (e.g., some GO terms, regulatory elements)
- Expression data not available for a condition/study
- No adjusted p-values in the original dataset
- Missing metadata (timepoints, replicates, normalization method)
- No physiological data (growth curves, Fv/Fm, cell counts)

## Separating KG from literature

Clearly separate KG-derived findings from literature context:
- Label them as SKILL.md Rule 3 says (`[KG]` / `[interpretation]` in chat and
  notebooks; in words in `paper.md`)
- Never cite a specific paper from intrinsic knowledge as if
  it were a KG reference
- If the user needs literature support, say so — this system is
  a KG explorer, not a literature review tool
- Paper citations from outside the KG come only from a web search the
  researcher authorised, for background and discussion — never data (see
  [SKILL.md Rule 1](../SKILL.md))

## Scoping: what to verify

When orienting in an unfamiliar corner of the KG, start from the MCP's
self-documentation: `docs://guide/start_here` (which tool answers which
question) and `docs://guide/conventions` (cross-tool semantics — see
[anti-hallucination.md §5.1](anti-hallucination.md#51-mcp-tool-capability-from-memory)).
These are version-matched to the installed explorer; don't reconstruct
tool behavior from memory.

Before diving into analysis, confirm the KG has what you need:
- Are the needed organisms present? (`list_organisms`; its `clade`
  field gives the ecotype — don't parse strain names)
- Are there experiments for the conditions of interest?
  (`list_experiments`)
- How was each experiment designed? (`list_experiments(verbose=True)`:
  `design_notes` record arm matching, reference-culture state, sampling
  days and separate runs — read them before asking the researcher or
  logging a design gap)
- Are relevant publications available? (`list_publications`)
- Is the gene set complete? (check `total_matching` vs `returned`)
- Document any gaps: "The KG does not contain [X] data for [Y]"

## MCP vs Python API

| Use MCP when | Use Python API when |
|---|---|
| Browsing and orienting | Extracting full datasets |
| Checking gene counts and summaries | Running enrichment or statistics |
| Navigating between tools | Producing tables and figures |
| Quick lookups (< 50 results) | Any computation on gene lists |
| Working in chat mode | Result set > MCP limit |
| Cross-experiment overview (`gene_response_profile`) | Reshaping or aggregating data |
| | Building response matrices (`response_matrix()`) |
| | Comparing gene sets (`gene_set_compare()`) |

### When to switch from MCP to utilities

If you need to reshape, aggregate, or compute on MCP results, use
the analysis utilities first. Write scripts only for project-specific
logic not covered by the utilities. Do not attempt to work around
MCP limits in chat with one-off parsing.
