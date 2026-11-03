# Gaps and friction

- [tool] `differential_expression_by_gene` Python API: `product` is only returned with `verbose=True` (KeyError otherwise). (methods)
- [bkm] Page DE calls and assert rows fetched == `total_matching`; N-deprivation experiments need 3 pages at limit 5000. (methods)
- [tool] The kg-coder subagent had no MCP resource reader; it read `docs://guide/python_api` from the copy bundled in the package. (methods)
- [pitfall] A critic spot-check surfaced a primary result (MED4 ntcA on urea) before the plan was locked. Critic prompts for the proposal should forbid pulling target-gene values. (plan)
- [kg-gap] Tolonen 2006 significance is list-based (padj only 0.01 or 1) and does not track |log2FC|; ntcA at |log2FC| rank 6 is `not_significant`. (plan)
