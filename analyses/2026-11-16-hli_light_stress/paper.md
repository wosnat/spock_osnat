# High-light-inducible (hli) genes in *Prochlorococcus*: light response or broad stress response?

## Question

*Prochlorococcus* MED4 carries 23 genes encoding small high-light-inducible proteins (HLIPs). We ask whether their transcripts respond to light, and whether they respond across stresses other than light. Where the available experiments allow it, we also ask whether that response is independent of light. The analysis is restricted to MED4 and is exploratory: it reuses published transcriptome experiments, several of which were inspected while the analysis was planned.

## Background

HLIPs are single-helix members of the chlorophyll a/b-binding protein superfamily. They are thought to protect the photosynthetic apparatus when absorbed light exceeds what photosynthesis can use [ref needed]. The *hli* gene family is greatly expanded in high-light-adapted *Prochlorococcus*; MED4 has 23 copies, many of them in clusters and near-identical in sequence [ref needed for the expansion]. Several of the transcriptome studies used here name *hli* genes in their results (Steglich et al. 2006; Tolonen et al. 2006; Bagby & Chisholm 2015; Thompson et al. 2016). Because a cell under nutrient or CO2 limitation uses less of the light it absorbs, induction under such stresses could reflect either a light-driven photoprotective response or a broader stress response. The experiments brought together here comprise 28 MED4 transcriptome comparisons from 11 publications, covering light onset and photoperiod, photosynthetic electron transport, nitrogen, phosphorus, iron, CO2, salt and phage infection, together with non-stress comparisons.

## Methods

**Data sources and experiment selection.** All expression data were taken from a multi-omics knowledge graph that collects published *Prochlorococcus* transcriptome and proteome studies, together with their gene annotations and ortholog groups. We used every MED4 transcriptome comparison in the graph, from both microarray and RNA-seq platforms, and relied on each original study's own calls of which genes were significantly up or down. Proteome data were not used. One RNA-seq comparison, a 2016 study of MED4 in coculture with *Alteromonas* HOT1A3 (Aharonovich & Sher 2016), was excluded after inspection. In that table 82% of all log2 fold changes were negative, 291 genes with an absolute log2 fold change above 5 were nonetheless called not significant, and 18 distinct fold-change values were each shared by ten or more genes. This pattern is what one expects when many genes have near-zero read counts in one arm, so the table could not be read reliably. A phosphate-starvation microarray (Martiny et al. 2006) was also excluded: the knowledge graph holds only the 34 genes significant at 48 h, which include one *hli* gene, so the *hli* genes could not be assessed at the earlier time points and only weakly at 48 h. The remaining 27 comparisons come from 10 publications.

The *hli* gene set was defined as the 23 MED4 genes belonging to the 14 Cyanorak ortholog groups annotated as high-light-inducible proteins. Gene name, product description and ortholog-group membership all identify the same 23 genes.

**Grouping the experiments.** The comparisons differ in what they can say about light, so we grouped them before reading any result. Five *light-onset* comparisons, from a single study (Steglich et al. 2006), measure the response 45 min after cells kept 5 h in the dark were exposed to blue, green, red or white light (13 µmol photons m⁻² s⁻¹), or to brighter white light (55 µmol). All five share one dark control. A sixth comparison from the same study adds DCMU, which blocks electron flow out of photosystem II, to illuminated cells. Two *schedule-extension* experiments (Johnson et al. 2026) compare cells kept in light past their normal dusk, or in darkness past their normal dawn, with cells on their usual 12:12 h light–dark cycle sampled at the same time of day. Two experiments compare constant darkness with constant light, with and without phage infection (Thompson et al. 2016). A phage experiment from the same study, run entirely in the dark, is the one stress comparison in the collection that does not involve light.

The remaining comparisons are stresses applied in the light, or comparisons we treated as non-stress. The stresses are:
- nitrogen limitation, four experiments (Tolonen et al. 2006; Read et al. 2017; Weissberg et al. 2025);
- CO2 limitation, three experiments (Bagby & Chisholm 2015);
- phage infection in the light, two experiments (Lindell et al. 2007; Thompson et al. 2016);
- iron starvation (Thompson et al. 2011);
- low salinity (He et al. 2022).

The non-stress comparisons are:
- growth on urea or cyanate as the sole nitrogen source (Tolonen et al. 2006);
- re-addition of iron to starved cells (Thompson et al. 2011);
- air sparging compared with time 0 (Bagby & Chisholm 2015);
- coculture with *Alteromonas* (Weissberg et al. 2025).

For the 2025 coculture-versus-axenic experiment (Weissberg et al. 2025), the knowledge graph's design notes record that the arms are matched by growth state rather than by sampling day: the axenic control came from a separate repeat run sampled on days 7 and 14. On day 11 the coculture is compared with axenic cells on day 7, both growing exponentially, so that time point is a non-stress comparison. On day 18 it is compared with axenic cells on day 14, by which time the axenic culture had run out of nitrogen and was dying, while the coculture survived. A gene "down in coculture" on day 18 is therefore one that is higher in the nitrogen-starved control. The low-nitrogen starvation series from the same study compare each culture with itself in exponential growth: the coculture on day 11, the axenic culture on day 7.

**Testing whether the *hli* set responds.** For every experiment, time point and direction (up or down), we asked whether *hli* genes were over-represented among the genes the study called significant, using a one-sided Fisher exact test. Where a study reported every measured gene, the background was the set of measured genes. Several studies reported only the genes they found significant. For those, a gene absent from the table was taken as not significant, the whole genome served as background, and the test is marked approximate. Tests with fewer than 10 significant genes genome-wide in that direction were not run, because a handful of changed genes cannot show over-representation. Down tests were not run on one phage microarray table that lists only induced genes. Where more than 30% of all genes changed in one direction, the test was run but flagged, since nearly any gene set then overlaps the changed genes.

P-values were corrected for multiple testing with the Benjamini–Hochberg procedure, separately for each gene set across all tests. To give each experiment a single call per direction, we took its smallest time-point p-value, multiplied it by the number of testable time points, and corrected these values across experiments. All contrasts are read as treatment versus control, as the studies reported them.

To see whether an *hli* response was specific or part of a general reaction, the same tests were run on ten reference sets from the Cyanorak functional categories. These were:
- ribosomal proteins;
- protein folding and protein degradation;
- adaptation to nitrogen, phosphorus and iron limitation;
- the light-adaptation category with the *hli* genes removed;
- photosystem I, photosystem II and CO2 fixation.

We also tested 200 random gene sets of the same size in each test, to estimate how often an arbitrary set reaches significance.

**Near-identical paralogs.** Many MED4 *hli* genes are near-identical copies. Four pairs (PMM0815/PMM1396, PMM0816/PMM1397, PMM0817/PMM1398 and PMM0818/PMM1399) had exactly the same fold change in every microarray table that listed both members, so each pair evidently shares one probe signal. In microarray tables that list only significant genes, usually only one member of a pair appears. Counting the other member as "not significant" would invent a difference that the platform cannot measure. We therefore treated it as undefined. As a sensitivity check, we repeated the set-level tests on the microarray tables with each pair counted once. RNA-seq tables, in which the pairs have different values, were left as reported.

**Gene-level patterns.** These analyses were exploratory and were added after the set-level results had been seen. Each gene's call in each experiment and time point was coded as up (+1), not significant (0), down (−1) or undefined. The 23 genes were then clustered by average linkage, using as distance the fraction of shared defined calls on which two genes disagree. We checked the stability of the clusters in two ways: with a correlation-based distance, and with the light-onset arrays removed.

For each gene we also recorded how widely its ortholog group is found among the 123 organisms in the knowledge graph, and in which *Prochlorococcus* clades (high-light or low-light, as recorded for each organism). Finally, we compared the strength of the *hli* response across studies with each study's background light intensity, using Spearman rank correlation.

All numbers reported here are produced by scripts in the analysis repository, and every figure is generated from saved tables.

## Results

**The *hli* genes are the light-onset responders.** In all four light-onset comparisons that could be tested, *hli* genes were strongly over-represented among the induced genes (per-experiment corrected p between 5 × 10⁻⁸ and 2 × 10⁻¹⁰). Blue, red and dim white light gave this result, and so did brighter white light. In each case 8 to 11 of the 11 *hli* genes on the array were induced, spread over 5 to 8 different ortholog groups. The green-light shift changed too few genes for a test. None of the ten reference sets was induced at light onset. Photosystem I genes went down in two of the six light-onset tests (Fig. 1).

![Fig. 1. hli is the gene set that responds to light onset, and it is induced across stresses applied in the light. (a) For hli and four reference sets, the number of testable set-level tests significant up or down (Benjamini–Hochberg padj < 0.05) out of the testable tests, by experiment group. Colour intensity shows the share of tests that are significant (orange, up; blue, down). Hatched cells had no testable test. The coloured patch beside each row gives its family: light/dark, stress or non-stress. Relief: iron re-added and air vs time 0. N source: urea or cyanate as the sole nitrogen source. (b) Per-experiment hli calls. Each experiment is plotted twice: up to the right and down to the left, at −log10 of the per-experiment corrected p-value. Filled points are significant, and the dashed lines mark padj = 0.05. Four experiments with no testable time point are omitted. The 2025 coculture experiment (days 11 and 18 together) is shown as one row.](analysis/figures/paper_fig1.png)

Adding DCMU to illuminated cells changed few genes, and only three *hli* genes, all of them down. Constant darkness compared with constant light, with or without phage, produced no set-level *hli* change.

**The same genes respond to several stresses applied in the light.** *hli* genes were over-represented among induced genes in four of the five stresses (Fig. 1):
- **CO2 limitation:** both testable experiments (corrected p 2 × 10⁻¹⁰ and 5 × 10⁻¹⁰);
- **Iron starvation:** p 6 × 10⁻⁵;
- **Nitrogen limitation:** three experiments (p 5 × 10⁻¹² to 8 × 10⁻³);
- **Phage infection:** on the microarray (p 8 × 10⁻¹²).

There was no response to low salinity or phage lysate in the light, nor to phage lysate in the dark. The response also ran in reverse when a stress was relieved. *hli* genes went down when iron was added back to starved cells (p 9 × 10⁻⁶), and when cultures were sparged with air relative to time 0 (p 1 × 10⁻⁶). They were also induced when urea or cyanate replaced ammonium as the nitrogen source (p 8 × 10⁻¹¹ and 2 × 10⁻¹²). These comparisons were classed as non-stress, although cells on these alternative sources may be mildly nitrogen-limited.

Counting each paralog pair once did not change any test or experiment call; 20 tests were significant before and after. It did reduce the phage result, which rests on five independent signals rather than nine, but that result remained clear (p 1 × 10⁻⁶).

**Which genes carry the response: two groups of *hli* genes.** The tests above treat the 23 *hli* genes as one set. Looking gene by gene shows that they are not one set. This part of the analysis was exploratory, and it was added after the set-level results had been seen. Three properties divide the genes in almost the same way:

1. **Their response pattern.** Clustering the genes on their calls in every experiment and time point gives four clusters. C3 and C4 (15 genes, the *responders*) respond together; C1 and C2 (8 genes, the *quiet genes*) mostly do not (Fig. 2).
2. **Their copy number in MED4.** 14 of the 15 responders are multi-copy; all 8 quiet genes are single-copy (Fig. 3a).
3. **How widely their ortholog group is shared.** Every responder is in a group found only in *Prochlorococcus*; the quiet genes include all four genes whose groups extend to *Synechococcus* and *Cyanobium* (Fig. 3a).

These are three views of one division, not three separate findings. Per gene, a median of 29% of the responders' stress and light-onset calls were up (27% on RNA-seq alone), against 2.5% (7%) for the quiet genes; Fig. 3b breaks this down by condition.

**The responders.** These 15 genes carry everything described above. In the heatmap they form one block of rows in which they go up together (Fig. 2). They were induced at light onset (35 of 55 defined calls; Fig. 3b), under CO2 limitation (22 of 37), nitrogen limitation (64 of 139) and iron starvation (7 of 33), and when urea or cyanate was the nitrogen source (13 of 20). After phage infection they were induced in 14 of 195 calls, 9 of them at the first hour on the microarray. They went down when iron was added back (7 of 11) or air was supplied (7 of 13). They did not change in the salt or dark-phage experiments. All of them belong to ortholog groups found only in *Prochlorococcus*. The six genes whose groups occur throughout the genus had a median of 33% of calls up (37% on RNA-seq).

**The quiet genes.** These eight genes rarely responded to stress (16 of 102 nitrogen-limitation calls up) and almost never to light onset (3 of 40). Their clearest response was to an extended light–dark schedule (11 of 32 calls up). This group holds all four genes whose ortholog groups are shared across nearly all picocyanobacteria in the knowledge graph (high- and low-light *Prochlorococcus*, *Synechococcus* and *Cyanobium*). These four were the least responsive of all: a median of 2.5% of their stress and light-onset calls were up (7% on RNA-seq). Not every quiet gene is conserved: two *Prochlorococcus*-specific single-copy genes, PMM1317 and TX50_RS09730, were as quiet as the conserved four.

**The two groups explain the schedule-extension result.** In two of the four schedule-extension time points more than 30% of the genome changed. Six responder genes were higher in the darker arm of both experiments. Two quiet genes, PMM0064 and PMM0093, rose in both experiments instead. At the set level these opposing movements cancel, so the set-level reading of these experiments is unclear.

**How firm the grouping is.** The clusters held for 16 of the 23 genes under a correlation-based distance, and for 21 of 23 without the light-onset arrays; the quiet cluster was the less stable. An earlier clustering split the responders in two. That split reflected which member of each identical paralog pair a study had happened to list, and it disappeared once the pairs were handled as described in Methods. Copy number and ortholog breadth are confounded: every gene in a picocyanobacteria-wide group is single-copy, and every gene in a *Prochlorococcus*-wide group is multi-copy. These data cannot tell which of the two matters.

![Fig. 2. Calls for all 23 hli genes (columns) in all 55 experiment × time-point combinations (rows) (exploratory). Orange, up; blue, down; light grey, not significant; hatched, no defined call (gene absent from the table, or one of an identical paralog pair whose signal is reported under its partner). Columns: responders (C4, C3) left of the thick line, quiet genes (C2, C1) right of it; dotted lines separate clusters, and genes within a cluster are in clustering order (clustered on these calls after the paralog-twin correction). Above each gene: copy number (filled square, multi-copy) and a stacked bar giving the number of genomes in the knowledge graph that carry its ortholog group: high-light Prochlorococcus (gold), low-light Prochlorococcus (dark grey) and Synechococcus or Cyanobium (light grey). Rows are grouped by family (labelled strip at left; thick rules) and by condition (right; thin rules); within a condition each experiment is named once, with its time points in the second column (light onset: 45 min after transfer from dark to the stated light, µmol photons m⁻² s⁻¹; peak: the study's maximum across 70 min–24 h; d: day). Row labels are expanded in analysis/data/paper_fig2_row_key.csv](analysis/figures/paper_fig2.png)

![Fig. 3. The two groups of hli genes (exploratory). (a) What the genes are: each square is one gene, placed by the number of organisms in the knowledge graph that carry its ortholog group (stacked where values coincide); filled, multi-copy in MED4; hollow, single-copy. Shading marks groups found only in Prochlorococcus and groups that extend to Synechococcus and Cyanobium. (b) How they respond: the percentage of defined gene calls that are up (orange) or, for the two relief comparisons, down (blue), for responders (dark) and quiet genes (light); labels give calls / defined calls, summed over genes and time points.](analysis/figures/paper_fig3.png)

**The timing of the response depends on the stress.** In the time courses, phage infection induced 9 of the 23 *hli* genes (five independent signals) one hour after infection, and none from two hours on (Fig. 4). Nutrient limitation produced a slow build-up instead:
- **Nitrogen deprivation:** no *hli* gene was induced in the first three hours. The response rose to 10 of 17 measured genes by 48 h, after ribosomal-protein genes had already fallen.
- **Iron starvation:** none of 19 measured genes was up at 12 h, and 6 of 19 at 48 h.
- **Months-long low-nitrogen coculture:** induction peaked at day 31 and declined by day 89.

The *hli* response is therefore not confined to the onset of a stress. It is brief when the stress is acute and builds slowly when nutrients run out.

![Fig. 4. The timing of the hli response depends on the stress. The orange and blue lines give the percentage of measured hli genes called up and down at each time point; the dotted grey line gives ribosomal-protein genes called down, for reference. Filled points: set-level test padj < 0.05. Open points: too few changed genes to test. Dashed lines: descriptive table, not tested. (a) Phage infection, microarray; this table lists induced genes only, so there is no down line. (b) Nitrogen deprivation. (c) Iron starvation. (d) Low-nitrogen coculture, compared with the same culture in exponential growth on day 11. (e) Nitrogen-depleted RNA-seq; the table holds only the top half of genes by expression. (f) Phage lysate in the light.](analysis/figures/paper_fig4.png)

**Background light level.** Across studies, the strength of *hli* induction rose with the background light intensity under which the experiment was run (Spearman ρ = 0.49, p = 0.010). The strength of ribosomal-protein repression rose with it to the same degree (ρ = 0.48, p = 0.05), which points to stronger responses overall in the brighter studies rather than something specific to *hli*. The 27 tests come from only 13 experiments at 6 light levels, so these p-values overstate the evidence. In addition, cells in each experiment were acclimated to that light, and both arms were compared at the same intensity. We therefore do not read background light level as a driver of the *hli* response (Fig. 5).

![Fig. 5. Background light intensity and response strength across studies. (a) hli up tests. (b) Ribosomal-protein down tests. Each point is one testable test plotted at its study's growth light, at −log10 of its corrected p-value. Filled points are significant; points at the same light level are offset slightly. The Spearman correlation is given above each panel. Tests within a study are not independent, and each study's control was at the same light as its treatment.](analysis/figures/paper_fig5.png)


## Discussion

## References

Data sources (publication metadata from the knowledge graph):

- Dikla Aharonovich, Daniel Sher (2016). Transcriptional response of Prochlorococcus to co-culture with a marine Alteromonas: differences between strains and the involvement of putative infochemicals. *The ISME Journal*. https://doi.org/10.1038/ismej.2016.70
- Sarah C Bagby, Sallie W Chisholm (2015). Response of Prochlorococcus to varying CO2:O2 ratios. *ISME Journal*. https://doi.org/10.1038/ismej.2015.36
- Xiayu He, Huan Liu, Lijuan Long, Junde Dong, Sijun Huang (2022). Acclimation and stress response of Prochlorococcus to low salinity. *Frontiers in Microbiology*. https://doi.org/10.3389/fmicb.2022.1038136
- Zachary Johnson, Natalie C. Sadler, Marci R. Garcia, Xiaolu Li, Jordan Rozum, Lindsey Anderson, et al. (2026). Extreme genome reduction selectively retains modular regulatory architecture in Prochlorococcus MED4: conserved transcriptional modules reveal core physiological regulatory programs. *bioRxiv*. https://doi.org/10.64898/2026.04.15.718746
- Debbie Lindell, Jacob D. Jaffe, Maureen L. Coleman, Matthias E. Futschik, Ilka M. Axmann, Trent Rector, et al. (2007). Genome-wide expression dynamics of a marine virus and host reveal features of co-evolution. *Nature*. https://doi.org/10.1038/nature06130
- Adam C. Martiny, Maureen L. Coleman, Sallie W. Chisholm (2006). Phosphate acquisition genes in Prochlorococcus ecotypes: Evidence for genome-wide adaptation. *PNAS*. https://doi.org/10.1073/pnas.0601301103
- Robert W Read, Paul M Berube, Steven J Biller, Iva Neveux, Andres Cubillos-Ruiz, Sallie W Chisholm, et al. (2017). Nitrogen cost minimization is promoted by structural changes in the transcriptome of N-deprived Prochlorococcus cells. *The ISME Journal*. https://doi.org/10.1038/ismej.2017.88
- Claudia Steglich, Matthias Futschik, Trent Rector, Robert Steen, Sallie W. Chisholm (2006). Genome-Wide Analysis of Light Sensing in Prochlorococcus/H17188. *Journal of Bacteriology*. https://doi.org/10.1128/JB.01097-06
- Anne W Thompson, Katherine Huang, Mak A Saito, Sallie W Chisholm (2011). Transcriptome response of high- and low-light-adapted Prochlorococcus strains to changing iron availability. *The ISME Journal*. https://doi.org/10.1038/ismej.2011.49
- Luke R. Thompson, Qinglu Zeng, Sallie W. Chisholm (2016). Gene Expression Patterns during Light and Dark Infection of Prochlorococcus by Cyanophage. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0165375
- Andrew C Tolonen, John Aach, Debbie Lindell, Zackary I Johnson, Trent Rector, Robert Steen, et al. (2006). Global gene expression of Prochlorococcus ecotypes in response to changes in nitrogen availability. *Molecular Systems Biology*. https://doi.org/10.1038/msb4100087
- Osnat Weissberg, Dikla Aharonovich, Daniel Sher (2025). Transcriptomic and Proteomic Analysis Reveals Nitrogen Recycling as a Core Mechanism for Prochlorococcus Prolonged Survival. *bioRxiv*. https://doi.org/10.1101/2025.11.24.690089

Background literature: citations marked [ref needed] in the Background are still to be added.
