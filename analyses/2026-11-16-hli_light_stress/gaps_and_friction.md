# Gaps and friction

- [pitfall] Gene-set counting during Plan step 1 went to `run_cypher` for convenience, although most of it was coverable by tools (`genes_by_function` per organism, `search_homolog_groups` + `genes_by_homolog_group`, `genes_by_ontology`). Counts should be cross-checked with the tools before the seed is frozen. (plan)
- [tool] No tool reports *which field* a text match hit (gene name vs product vs description) — `genes_by_function` searches them together, so "by name" vs "by product" counts need Cypher or post-filtering rows. (plan)
- [tool] `genes_by_ontology` is one organism per call; "which genes in which strains carry InterPro X" across 100 strains needs a loop or Cypher. (plan)
- [kg] Coculture vs axenic (2025, 10.1101/2025.11.24.690089): the experiment node gives one `growth_phase` per time point (day 11 exponential, day 18 nutrient_limited) but does not say which arm it describes, and does not record that the axenic control arm is N-starving and dying at day 18. Researcher-supplied (decisions A.3–A.4). (analysis)
- [kg] PRO99-lowN starvation series: the node names and `control_timing: baseline` do say "vs PRO99-lowN exponential growth", but they don't say that the baseline is the same culture at day 11. The axenic RNA-seq node has `is_time_course: false` and no time points or growth phase, while the matching proteomics node has day 14/31/89 "death". Researcher-supplied (A.5). (analysis)
- [pitfall] I asked the researcher for the lowN control arm before checking the experiment node, which already partly answered it. (analysis)
- [pitfall] I labelled hli groups "HL-only" from strain names before checking `list_organisms`, which has a `clade` field (HLI–HLIV, LLI–LLIV). The researcher pointed it out. (analysis)
- [kg] The publication title for 10.1128/JB.01097-06 (Steglich et al. 2006) reads "...Light Sensing in Prochlorococcus/H17188" in the KG, which looks like an encoding error in the strain name. It is cited as stored. (analysis)
