# Proposal critical review — pass 1 (interpretation only), 2026-11-04

Fresh-context critic over `proposal.md`. Structure-only KG checks (kg_schema; KeggTerm counts by level; `reference_database` and gene-count ranges); no target results pulled. **No Blockers.** Six Concerns, three Notes.

| # | Severity | Finding (summary of critic text) | Disposition |
|---|---|---|---|
| 1 | Concern | The falsifiability check reads plausible true biology as method failure (uniform status across strains; shared-only steps), contradicting "a null is valid." | **Fixed.** Method failure is now judged only by the controls (Alteromonas, glnA, expected-negatives). Uniform or shared-only outcomes are listed as possible findings. |
| 2 | Concern | The Alteromonas control is confounded by genome size (~4,200–4,300 genes vs 1,870–3,203), so it passes almost automatically. "Clearly more" is undefined. 12 Alteromonas taxa, most gene-less. | **Fixed.** The control is now described as "catches gross breakage." "Clearly more" = ≥ 2× the Prochlorococcus median count. Added a route-level check: 3 routes with named KOs, fixed at catalogue approval, before scoring. The strains with genomes are confirmed in methods. |
| 3 | Concern | "KO exists in the KG" cannot tell an invalid KO from a valid KO no organism carries (the KG has 4,808 KO nodes, none gene-less). | **Fixed.** KO validity is checked against KEGG REST. Valid-but-unannotated KOs stay in the route, score absent, and are listed separately. |
| 4 | Concern | The non-shared status is undefined for routes whose steps are all shared. "Partial" is too coarse. "Best route" favours amino acids with many routes. | **Fixed.** Added the status "no dedicated step defined." Status is now reported as a k/n fraction. "Best route" is defined, and the number of routes per amino acid is shown. |
| 5 | Concern | Transporter calls have no completeness or direction rule. GO matching uses free text on definitions. | **Fixed.** Calls are recorded at the system level with subunit roles. Export systems (TCDB direction, LysE/RhtB families) are flagged and not counted as uptake. GO matching uses a researcher-approved term list. |
| 6 | Concern | Genome completeness and pipeline comparability are left open; the KG has no field for either. | **Fixed.** Completeness comes from NCBI assembly level (external input), and absences in incomplete genomes are flagged. The provenance check is tabulated from gene→KO edge `sources`/`evidence`, or stated as an assumption. |
| 7 | Note | SBP-only evidence has no summary label. | **Fixed.** Added an "SBP-only" label, and "no data" for the 3 strains without predictions. |
| 8 | Note | The urt/pst expected-negative is enforced by design. Class-only status is unclear. No degradation expected-negative. | **Fixed.** Class-only/SBP-only credit on urt/pst is reported but is not a failure. A degradation expected-negative route is named at catalogue approval, before scoring. |
| 9 | Note | Rules are approved after seeing bin samples, which leaves room for tuning. | **Fixed.** The catalogue, GO list and rules are approved before any strain results. Later changes are logged with reason and date. |

# Proposal critical review — pass 2 (delta over v2, interpretation only), 2026-11-04

Fresh-context critic over proposal.md v2 (N-release only; transporters deferred; Alteromonas removed; Synechococcus comparison). Structural spot-check: `list_organisms(["Synechococcus"])` → 54 genome strains. No target results pulled. **No Blockers.** Seven Concerns, four Notes.

| # | Severity | Finding (summary) | Disposition |
|---|---|---|---|
| 1 | Concern | "ALL"/broad entries have no call rule. K00273 (DAO, non-shared, MED4 hit PMM1703) would make every amino acid "dedicated". D-amino-acid enzymes are out of scope. | **Fixed.** Broad/ALL entries get their own column and never make a per-amino-acid call. D-amino-acid enzymes are shown only there. A fixture invariant was added. |
| 2 | Concern | The N-releasing step of a multi-step route is undefined. Urease (non-shared in the pilot) makes Arg "dedicated". speB is mislabelled NH4+. | **Fixed.** The N-releasing step is the first step that frees N from the backbone; later steps are context. Mode "release as urea" added. Urease is shared (urea use; open choice 3). A worked Arg example and its wording were added. |
| 3 | Concern | `other_N_route` entries and non-2-OG transaminases fall outside the two-mode question. Pro is the clearest case. | **Fixed.** The question was widened ("free N from the carbon skeleton … NH4+ or amino group of Glu/another amino acid"). Modes: NH4+, transfer (acceptor recorded), conversion to glutamate, and context-only "N kept in another amino acid". |
| 4 | Concern | GDH is "dedicated" in the v2 text but shared in the pilot catalogue. | **Deferred to the researcher** as open choice 1, with the trade-off stated. The catalogue will record a reason for every shared flag. |
| 5 | Concern | The expected-absent dedicated enzyme is a halt condition (repeats pass-1 finding 1), and its shortlist was already seen in MED4. | **Fixed.** It is now an enzyme expected absent from cyanobacteria generally, a hit is flag-and-inspect rather than a halt, and a disclosure was added. A dedicated enzyme found in some strains is listed as a finding. |
| 6 | Concern | The aminotransferase control depends on KO stability, can halt everything, and was seen in MED4. | **Fixed.** It is defined at step level (all alternative KOs). Missing → inspect first; halt only if unexplained in >10% of complete genomes. "Complete genome" = NCBI "Complete Genome". MED4 non-blindness noted. |
| 7 | Concern | Synechococcus is undefined and mixed (freshwater, thermophile, other genera; genome sizes overlap). No wording rule. | **Fixed (rule recommended; researcher open choice 2).** Marine subclusters 5.1–5.3 only; list frozen in methods; size ranges corrected; wording rule "X of N vs Y of 45", no loss/gain claims. |
| 8 | Note | Some v2 wording implies N-source use. | **Fixed.** The shared-flag rationale is now "weaker evidence of a catabolic, N-releasing role"; the change-log wording was revised. |
| 9 | Note | KO-only matching inherits KO errors (PMM1468 bioF on K00639 kbl). | **Fixed.** KO/product disagreements are flagged, and a flagged hit makes no call until reviewed. |
| 10 | Note | "Shared-only never dedicated" is a code invariant, not a test. | **Fixed.** It was moved to the methods fixtures. |
| 11 | Note | The MED4 answer key is not blind. | **Fixed.** Stated; the two non-MED4 strains carry the weight. |

# Proposal critical review — pass 3 (delta over v4, interpretation only), 2026-11-04

Fresh-context critic over proposal.md v4 (utilization pathways scored on dedicated steps only). No target queries. **No Blockers.** Four Concerns, four Notes.

| # | Severity | Finding (summary) | Disposition |
|---|---|---|---|
| 1 | Concern | Status is not anchored on the N-freeing step: a pathway can be "complete" while its N leaves only through an unchecked shared step (Thr→Gly→gcv), or "partial" although N is freed at step 1 (His/hutH). Pathway end undefined for multi-N amino acids. | **Fixed (v5).** Each pathway ends at its first N-freeing step. "Complete" needs all dedicated steps AND the N-freeing step present; a shared N-freeing step is an uncounted precondition. A separate "N-freeing step present/missing" field was added. Multi-N rule and Thr→Gly extension stated. Arginase → urea counts as freeing N (mode "via urea", set in pass 2). |
| 2 | Concern | The dedicated/shared flag is not operational and is inconsistent in the draft (speA shared vs cadA dedicated; Thr→Gly; gadB). | **Fixed (v5).** Operational rule written (shared = needed for a must-build product, central C/N metabolism, or another N source; judged against cyanobacterial metabolism) and applied uniformly. cadA is now shared, like speA. Every flag is reasoned and researcher-approved at catalogue review. |
| 3 | Concern | Per-amino-acid cell has no precedence (absent vs can't-be-judged), no tie rule, and k/n is not comparable across pathway lengths. | **Fixed (v5).** Precedence complete > partial > absent > can't be judged; ties go to the longer pathway; "all-shared route fully present" flag; n always shown; non-comparability stated. The Arg example was updated to "absent + flag". |
| 4 | Concern | The pilot figure uses enzyme-level v3 categories after v4, draws the broad DAO as "complete", and hard-codes Lys "partial". | **Fixed.** Figure relabelled as an "enzyme-level preview"; broad row neutral; cadA reclassified shared (Lys partial removed). The notebook carries a correction note on the Lys example shown to the researcher. |
| 5 | Note | The Asn example should list K13051 with K01424. | **Fixed.** |
| 6 | Note | Name Gly with Glu as likely "can't be judged". | **Fixed.** |
| 7 | Note | The expected-negative should be a dedicated step within a catalogued pathway. | **Fixed.** |
| 8 | Note | paper.md Background has an unverified universal ("every genome carries them"). | **Fixed.** Sentence reworded. |
