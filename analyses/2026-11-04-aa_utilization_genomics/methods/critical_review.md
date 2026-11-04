# Methods critical review — pass 1 (draft pathway catalogue), 2026-11-04

Fresh-context critic over `methods/` (commit 4fc9d3d). Lens: **data-integrity + interpretation**. MED4-only spot checks.

**Clean:**
- no duplicate steps or rows;
- booleans parse correctly;
- reused step_keys are consistent;
- the HTML counts match the CSVs (57 pathways, 84 steps, 50 dedicated, 34 shared, 19 all-shared, 13 debatable, 110 KOs, 46 not in KG, 3 adds / 119 rejects);
- all 124 KOs are KEGG-valid;
- no KEGG KO is missing for any step's own EC.

**Findings: 2 Blockers, 6 Concerns, 3 Notes.**

| # | Severity | Finding (summary) | Disposition |
|---|---|---|---|
| 1 | Blocker | **Cys_CTH / Met CTH (K01758):** in MED4 the K01758 genes are MetB (PMM0409) and a MetC-family protein (PMM1670), both eggnog family_inferred. Cys's only observable dedicated route would be credited from the wrong enzyme. The CTH debatable value is inconsistent (Cys yes / Met no). | **Being fixed.** A product-agreement rule applies to all crediting: a mismatch is flagged and does not count until the researcher reviews it. CTH is debatable in both contexts, with the cross-annotation stated. |
| 2 | Blocker | **Cross-check coverage was catalogue-wide, not per amino acid.** This hid the fact that the Phe/Tyr/Ala transamination KO lists miss the enzymes MED4 uses (aspB PMM0674, hisC PMM0186, AGXT PMM0919). Two shared-anchor pathways (Phe_hydroxylase_Tyr, Trp_kynurenine_Ala) could never be complete. | **Being fixed.** Coverage is now per amino acid's own step. Anchor KO lists are completed from KEGG reaction→KO links. The cross-check is re-run. |
| 3 | Concern | 15 pathways contain a step whose KOs are all not in the KG, so they can never score present. Tyr has no observable dedicated route; Phe, Cys, Lys, Met and Arg (incl. ArgZ) rest on unobservable KOs. Not stated per amino acid. | **Being fixed.** Added `observable` per pathway and `assessable` per amino acid. Unobservable = "not assessable", never "absent". ArgZ is marked as needing homolog search. |
| 4 | Concern | Gly has no dedicated step; Glu's only dedicated route (GABA shunt) is N-neutral. These are unscorable by design, but not stated. | **Being fixed.** Stated in the HTML; carried into scoring and the paper. |
| 5 | Concern | PHE_AT / TYR_AT flagged shared "last step of biosynthesis", but MED4 makes Phe/Tyr via arogenate (R00691 PMM1504, R00733 PMM1565). | **Being fixed.** Re-judged at reaction level; marked debatable; reconciled with PHHA. |
| 6 | Concern | Flag inconsistencies: K17989 (Ser dedicated vs Thr shared); TRP_AT enzyme-level vs reaction-level elsewhere; K00830 debatable in SER_AT but not GLY_AT; PHEDH/LYSDH not debatable while ALD/LEUDH are. | **Being fixed.** Reaction-level rule applied everywhere; all reversible dehydrogenases debatable; changes logged in `flag_change_log.csv`. |
| 7 | Concern | Missing methylaspartate route for Glu (glutamate mutase → 3-methylaspartate ammonia-lyase, frees NH4+). | **Being fixed.** Added; minor omissions listed as known omissions. |
| 8 | Concern | Expected-negative astB: the rule and the ranking were committed with the KG lookup; whether K01484 has any gene in the KG is unverified. | **Being fixed.** Disclosed plainly; K01484 gene presence in the KG to be confirmed. |
| 9 | Note | Multi-subunit enzymes are treated as isozymes (any one subunit credits the step). | **Being fixed.** AND groups for subunits. |
| 10 | Note | HTML coverage wording contradicts the code; "3 adds" = 2 enzymes. | **Being fixed.** |
| 11 | Note | Spot-checked rejects: direction calls correct. His decarboxylase rejected vs Lys cadA catalogued (asymmetry). | **No change.** The asymmetry stays visible to the researcher. |

Dispositions are marked "being fixed" until the re-run lands. They will be updated with before/after counts, and a delta pass is run if the fixes change claims materially.
