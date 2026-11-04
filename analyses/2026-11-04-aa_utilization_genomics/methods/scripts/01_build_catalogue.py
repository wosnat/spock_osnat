"""Methods step 1 - draft the amino-acid utilization pathway catalogue (for researcher review).

The catalogue is DATA defined in this script. It is drafted by Claude from KEGG reference
pathways/modules and standard bacterial biochemistry, i.e. an [interpretation] input that the
researcher approves (proposal.md section 3, step 1). Nothing here comes from the KG and no
organism is queried. KEGG module definitions used as source_ref were read from
https://rest.kegg.jp/get/<module> on 2026-11-04 (definitions quoted in SOURCE_NOTES below).

Rules applied (proposal v5):
  * A pathway ends at its N-freeing step: the first step that frees N from the amino acid
    (NH4+, transamination [acceptor recorded], via urea, or conversion of the skeleton to glutamate).
  * Amino acids with >1 N end at the FIRST N-freeing step; later N release is context only.
  * Routes that only move N into another amino acid (Thr -> Gly, Phe -> Tyr, Ser -> Gly,
    kynurenine -> Ala) are extended to the step that frees N from that product.
  * Each step: KO list (isozymes / paralog KOs grouped; step present if ANY KO present),
    EC, is_n_freeing, n_mode, dedicated/shared + one-line flag_reason, debatable + reason.
  * Shared = the step's reaction/enzyme is needed in cyanobacterial metabolism for something
    other than amino-acid breakdown: a must-build product (amino acid, polyamine, cofactor,
    nucleotide), central C/N metabolism, or another N source. Researcher decisions: GDH shared,
    urease shared, speA and cadA shared.
  * Broad-specificity and D-amino-acid enzymes go to a separate table, never credited.

Outputs (methods/data/):
  pathway_catalogue_steps.csv  one row per amino acid x pathway x step
  pathway_catalogue.csv        one row per amino acid x pathway x step x KO
  broad_enzymes.csv            broad / D-amino-acid / side-activity enzymes (never credited)
  pilot_reconciliation.csv     where every KO of the spike draft catalogue went
  flag_change_log.csv          every flag / KO-list change made after the critic review (old -> new)
  proposed_controls.csv        controls (02 adds validity, gene count and selection columns)

Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/methods/scripts/01_build_catalogue.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

MDIR = Path(__file__).resolve().parents[1]
DATA = MDIR / "data"
SPIKE = MDIR.parent / "spike" / "data" / "med4_n_release_catalogue.csv"

NH4, TR, UREA, GLU = "NH4+", "transamination", "via urea", "to glutamate"
DED, SH = "dedicated", "shared"
K00830_DEBATE = ("K00830 (AGXT) carries Ala-, Gly- and Ser- glyoxylate/pyruvate transamination; whether its "
                 "photorespiratory role holds in cyanobacteria is not established here. Same judgement in ALA_AT, GLY_AT, SER_AT.")
CTH_DEBATE = ("K01758 is cross-annotated onto forward-transsulfuration enzymes: in MED4 it sits on PMM0409 "
              "(product O-succinylhomoserine thiol-lyase, MetB) and PMM1670 (cystathionine beta-lyase family, MetC-like), "
              "both eggNOG family_inferred. MetB/MetC are Met-biosynthesis enzymes; only genes whose product names "
              "cystathionine gamma-lyase are credited. Cys is also only a side substrate of CTH.")

# ---------------------------------------------------------------------------------------------
# Reusable step definitions (same reaction in several pathways -> one step_key, one flag).
# Fields: step_key, step_name, reaction, kos, ec, is_n_freeing, n_mode, acceptor, flag,
#         flag_reason, debatable_reason ("" = not debatable), notes
# ---------------------------------------------------------------------------------------------
def S(step_key, step_name, reaction, kos, ec, n_freeing, n_mode, acceptor, flag, flag_reason,
      debatable="", notes=""):  # product_keywords, kegg_rn, ko_groups come from the lookup tables below
    return dict(step_key=step_key, step_name=step_name, reaction=reaction, kos=kos, ec=ec,
                is_n_freeing=n_freeing, n_mode=n_mode if n_freeing else "", acceptor=acceptor,
                flag=flag, flag_reason=flag_reason, debatable_reason=debatable, notes=notes)


GCS_P = S("GCS_P", "glycine cleavage P protein (glycine decarboxylase)",
          "glycine + lipoyl-H protein -> aminomethyl-H protein + CO2",
          ["K00281", "K00282", "K00283"], "1.4.4.2", False, "", "", SH,
          "Glycine cleavage is C1 / photorespiratory central metabolism in cyanobacteria.",
          notes="K00282+K00283 are the two subunits of the split P protein; H protein K02437 and "
                "L protein K00382 are carriers, not scored (M00621).")
GCS_T = S("GCS_T", "glycine cleavage T protein (aminomethyltransferase)",
          "aminomethyl-H protein + THF -> 5,10-methylene-THF + NH4+ + reduced H protein",
          ["K00605"], "2.1.2.10", True, NH4, "", SH,
          "Same glycine cleavage system: C1 (methylene-THF) supply and photorespiration.")
ALA_AT = S("ALA_AT", "alanine transamination",
           "L-alanine + 2-oxo acid <=> pyruvate + L-amino acid",
           ["K14260", "K00814", "K14272", "K00830", "K00827", "K05825", "K28204", "K00835"],
           "2.6.1.2;2.6.1.44;2.6.1.66", True, TR,
           "2-oxoglutarate (-> Glu; R00258), glyoxylate (-> Gly; R00369) or 2-oxoisovalerate (-> Val; R01215)", SH,
           "Same reaction makes alanine (pyruvate + Glu); alanine is a must-build amino acid.",
           debatable=K00830_DEBATE,
           notes="KO list = KEGG link/ko/rn for R00258 + R00369 + R01215.")
ASP_AT_KOS = ["K00811", "K00812", "K00813", "K11358", "K14454", "K14455", "K15849"]
# KEGG link/ko/rn:R00694 (Phe) and R00734 (Tyr) give the same 12 KOs.
AROM_AT_KOS = ["K00811", "K00812", "K00813", "K00815", "K00817", "K00832", "K00838", "K05821",
               "K11358", "K14454", "K14455", "K15849"]
AROM_AT_DEBATE = ("Route inferred from annotation only: MED4 PMM1504 is pheA (prephenate dehydratase, K04518) and "
                  "PMM1565 is tyrA (prephenate dehydrogenase), i.e. the phenylpyruvate / 4-hydroxyphenylpyruvate route, "
                  "whose last step is this transamination -> shared. KEGG also links those KOs to the arogenate "
                  "reactions (R00691/R00733), so the route is not proven; a strain using the arogenate route would "
                  "not need this reaction.")
ADC = S("ADC", "arginine decarboxylase", "L-arginine -> agmatine + CO2",
        ["K01585", "K02626", "K01584", "K01583"], "4.1.1.19", False, "", "", SH,
        "Polyamine (putrescine/spermidine) biosynthesis, M00133; researcher decision: speA shared.",
        notes="Biosynthetic speA (K01585), pdaD (K02626) and biodegradative adiA (K01584) grouped as "
              "isozymes of one reaction.")
TYR_AT = S("TYR_AT", "tyrosine transamination",
           "L-tyrosine + 2-oxoglutarate <=> 4-hydroxyphenylpyruvate + L-glutamate",
           AROM_AT_KOS, "2.6.1.1;2.6.1.5;2.6.1.9;2.6.1.57", True, TR, "2-oxoglutarate (-> Glu)", SH,
           "Same reaction (reverse) is the last step of Tyr biosynthesis via 4-hydroxyphenylpyruvate (M00025); MED4 tyrA "
           "PMM1565 (prephenate dehydrogenase) indicates this route [KG annotation + interpretation].",
           debatable=AROM_AT_DEBATE,
           notes="M00044 step 1 also lists K03334 (L-amino-acid oxidase), kept in the broad table.")

# ---------------------------------------------------------------------------------------------
# Pathways: (amino_acid, pathway_id, pathway_name, source_ref, [steps in order], pathway_note)
# ---------------------------------------------------------------------------------------------
P = []

def add(aa, pid, name, src, steps, note=""):
    P.append(dict(amino_acid=aa, pathway_id=pid, pathway_name=name, source_ref=src, steps=steps,
                  pathway_note=note))

# ---- Ala --------------------------------------------------------------------------------------
add("Ala", "Ala_dehydrogenase", "alanine dehydrogenase", "map00250", [
    S("ALD", "alanine dehydrogenase", "L-alanine + NAD+ + H2O <=> pyruvate + NH4+ + NADH",
      ["K00259", "K19244"], "1.4.1.1", True, NH4, "", DED,
      "Not needed to make alanine in cyanobacteria (made by transamination) [interpretation].",
      debatable="Reversible; in some bacteria AlaDH runs in the NH4+-assimilating (alanine-forming) direction.")])
add("Ala", "Ala_transamination", "alanine transamination", "map00250", [ALA_AT],
    note="All-shared route. avtA (K00835, Ala+2-oxoisovalerate -> pyruvate+Val) is listed under Val_BCAT.")

# ---- Arg (first N-freeing step) ---------------------------------------------------------------
add("Arg", "Arg_arginase", "arginase route", "map00330; M00134 (step 1)", [
    S("ARGINASE", "arginase", "L-arginine + H2O -> L-ornithine + urea", ["K01476"], "3.5.3.1",
      True, UREA, "", DED,
      "Cyanobacteria make ornithine from glutamate (M00028/M00845), so arginase is not needed for "
      "biosynthesis [interpretation].",
      debatable="KEGG M00134 places arginase in polyamine biosynthesis (Arg -> ornithine -> putrescine).",
      notes="Urea N is freed by urease later (urease is shared; context only).")])
add("Arg", "Arg_argZ", "arginine dihydrolase (ornithine-ammonia cycle)", "M00978 (last step); M00134", [
    S("ARGZ", "arginine dihydrolase (ArgZ)", "L-arginine + 2 H2O -> L-ornithine + CO2 + 2 NH4+ (KEGG R13308)",
      ["K27545", "K27542"], "3.5.3.27", True, NH4, "", DED,
      "Its only reaction breaks arginine down; ornithine is made from glutamate.",
      debatable="Part of the cyanobacterial ornithine-ammonia cycle (M00978), which can be read as "
                "central N storage/remobilization metabolism -> would be shared.")])
add("Arg", "Arg_ADI", "arginine deiminase route", "map00220", [
    S("ADI", "arginine deiminase", "L-arginine + H2O -> L-citrulline + NH4+", ["K01478"], "3.5.3.6",
      True, NH4, "", DED, "Arginine catabolism only (ADI pathway).",
      notes="Later steps (arcB OTC K00611, arcC carbamate kinase K00926) free more N; context only.")])
add("Arg", "Arg_AST", "arginine succinyltransferase (AST) route", "M00879", [
    S("ASTA", "arginine N-succinyltransferase", "L-arginine + succinyl-CoA -> N2-succinyl-L-arginine + CoA",
      ["K00673"], "2.3.1.109", False, "", "", DED, "Arginine catabolism only (AST pathway)."),
    S("ASTB", "succinylarginine dihydrolase", "N2-succinyl-L-arginine + 2 H2O -> N2-succinyl-L-ornithine + 2 NH4+ + CO2",
      ["K01484"], "3.5.3.23", True, NH4, "", DED, "Arginine catabolism only (AST pathway).")])
add("Arg", "Arg_transaminase", "arginine transamination", "map00330", [
    S("ARUH", "arginine:pyruvate transaminase", "L-arginine + pyruvate <=> 5-guanidino-2-oxopentanoate + L-alanine",
      ["K12252"], "2.6.1.84", True, TR, "pyruvate (-> Ala)", DED,
      "Not used in arginine biosynthesis; arginine catabolism (aru route).")])
add("Arg", "Arg_agmatinase", "agmatine route via agmatinase", "M00133", [
    ADC,
    S("AGMATINASE", "agmatinase", "agmatine + H2O -> putrescine + urea", ["K01480"], "3.5.3.11",
      True, UREA, "", SH, "Putrescine biosynthesis (M00133).")],
    note="All-shared route; urease (shared, researcher decision) would free the urea N.")
add("Arg", "Arg_agmatine_deiminase", "agmatine route via agmatine deiminase", "map00330", [
    ADC,
    S("AGUA", "agmatine deiminase", "agmatine + H2O -> N-carbamoylputrescine + NH4+", ["K10536"], "3.5.3.12",
      True, NH4, "", SH, "Alternative putrescine biosynthesis branch (aguA/aguB) [interpretation].",
      debatable="Only shared if the organism makes putrescine this way rather than via agmatinase.")],
    note="All-shared route.")

# ---- Asn ------------------------------------------------------------------------------------
add("Asn", "Asn_asparaginase", "asparaginase", "map00250", [
    S("ASNASE", "L-asparaginase", "L-asparagine + H2O -> L-aspartate + NH4+",
      ["K01424", "K13051", "K13278", "K05597"], "3.5.1.1;3.5.1.38", True, NH4, "", DED,
      "Breaks asparagine down; asparagine is made by asparagine synthetase, not this enzyme.",
      notes="K13051 (iaaA) is also an isoaspartyl peptidase; K13278 (ASPG) is mainly a eukaryotic "
            "lysophospholipase with asparaginase activity. K05597 (glutaminase-asparaginase, EC 3.5.1.38) added from "
            "KEGG link/ko/rn:R00485; it is also credited to Gln_glutaminase.",
      debatable="K05597 is a two-substrate glutaminase-asparaginase credited to both Asn and Gln.")])
add("Asn", "Asn_transaminase", "asparagine transamination", "map00250", [
    S("ASN_AT", "asparagine--oxo-acid transaminase", "L-asparagine + 2-oxo acid <=> 2-oxosuccinamate + L-amino acid",
      ["K22457"], "2.6.1.14", True, TR, "2-oxo acid (unspecified)", DED, "Asparagine catabolism only.")])

# ---- Asp ------------------------------------------------------------------------------------
add("Asp", "Asp_aspartase", "aspartate ammonia-lyase", "map00250", [
    S("ASPA", "aspartate ammonia-lyase", "L-aspartate -> fumarate + NH4+", ["K01744"], "4.3.1.1",
      True, NH4, "", DED, "Not used to make aspartate in cyanobacteria (made by transamination) [interpretation].",
      notes="Pilot: MED4 PMM0222 is named aspA but its product is aspartoacylase; matching is by KO only.")])
add("Asp", "Asp_transamination", "aspartate transamination", "map00250", [
    S("ASP_AT", "aspartate transamination", "L-aspartate + 2-oxoglutarate <=> oxaloacetate + L-glutamate",
      ASP_AT_KOS, "2.6.1.1", True, TR, "2-oxoglutarate (-> Glu)", SH,
      "Same reaction makes aspartate (OAA + Glu); aspartate is a must-build amino acid.")],
    note="All-shared route.")

# ---- Cys ------------------------------------------------------------------------------------
add("Cys", "Cys_desulfidase", "L-cysteine desulfidase / desulfhydrase", "map00270", [
    S("CYS_DESULF", "L-cysteine desulfidase", "L-cysteine + H2O -> pyruvate + H2S + NH4+",
      ["K20021", "K22207", "K28981"], "4.4.1.28", True, NH4, "", DED, "Cysteine catabolism only.")])
add("Cys", "Cys_CTH", "cystathionine gamma-lyase acting on cysteine", "map00270", [
    S("CTH_CYS", "cystathionine gamma-lyase (cysteine desulfhydrase activity)", "L-cysteine + H2O -> pyruvate + H2S + NH4+ (KEGG R00782, an 'other' reaction of EC 4.4.1.1)",
      ["K01758", "K17217"], "4.4.1.1", True, NH4, "", DED,
      "Reverse transsulfuration enzyme; cyanobacteria make cysteine via cysteine synthase and "
      "methionine via cystathionine beta-lyase, not this enzyme [interpretation].",
      debatable=CTH_DEBATE)])
add("Cys", "Cys_CDO", "cysteine dioxygenase route", "map00270", [
    S("CDO", "cysteine dioxygenase", "L-cysteine + O2 -> 3-sulfino-L-alanine", ["K00456"], "1.13.11.20",
      False, "", "", DED, "Cysteine catabolism only."),
    S("CSA_AT", "cysteine-sulfinate transamination (by aspartate aminotransferase)",
      "3-sulfino-L-alanine + 2-oxoglutarate <=> 3-sulfinylpyruvate + L-glutamate",
      ASP_AT_KOS, "2.6.1.1", True, TR, "2-oxoglutarate (-> Glu)", SH,
      "Carried by aspartate aminotransferase, which makes aspartate.")])

# ---- Gln ------------------------------------------------------------------------------------
add("Gln", "Gln_glutaminase", "glutaminase", "map00250", [
    S("GLNASE", "glutaminase", "L-glutamine + H2O -> L-glutamate + NH4+", ["K01425", "K05597"], "3.5.1.2;3.5.1.38",
      True, NH4, "", DED, "Free glutaminase; not part of GS-GOGAT assimilation.",
      notes="K23265 (EC 3.5.1.2) is excluded: it is PurQ, the glutaminase subunit of purine "
            "biosynthesis (FGAM synthase), i.e. a shared biosynthetic amidotransferase. CPS KOs (K01954-K01956, "
            "K11540) also link to R00256 and are excluded for the same reason. K05597 added from link/ko/rn:R00256.",
      debatable="K05597 is a two-substrate glutaminase-asparaginase credited to both Asn and Gln.")])
add("Gln", "Gln_GOGAT", "glutamate synthase (GOGAT)", "map00250; map00910", [
    S("GOGAT", "glutamate synthase", "L-glutamine + 2-oxoglutarate + reductant -> 2 L-glutamate",
      ["K00265", "K00266", "K00264", "K00284"], "1.4.1.13;1.4.1.14;1.4.7.1", True, GLU,
      "2-oxoglutarate (-> Glu)", SH, "GS-GOGAT is the central N-assimilation pathway.",
      notes="K00265+K00266 are two subunits of NADPH-GOGAT; K00264 NADH-GOGAT; K00284 Fd-GOGAT.")],
    note="All-shared route.")

# ---- Glu ------------------------------------------------------------------------------------
add("Glu", "Glu_GDH", "glutamate dehydrogenase", "map00250; map00910", [
    S("GDH", "glutamate dehydrogenase", "L-glutamate + NAD(P)+ + H2O <=> 2-oxoglutarate + NH4+ + NAD(P)H",
      ["K00260", "K00261", "K00262", "K15371"], "1.4.1.2;1.4.1.3;1.4.1.4", True, NH4, "", SH,
      "Researcher decision 1: GDH also assimilates NH4+ (central N metabolism).")],
    note="All-shared route.")
add("Glu", "Glu_GABA_shunt", "GABA shunt", "M00027", [
    S("GAD", "glutamate decarboxylase", "L-glutamate -> 4-aminobutanoate (GABA) + CO2", ["K01580"],
      "4.1.1.15", False, "", "", DED, "No biosynthetic role for GABA in cyanobacteria [interpretation]."),
    S("GABA_AT", "4-aminobutyrate transaminase", "4-aminobutanoate + 2-oxo acid <=> succinate semialdehyde + L-amino acid",
      ["K13524", "K07250", "K00823", "K16871", "K14268"], "2.6.1.19;2.6.1.96", True, TR,
      "2-oxoglutarate (-> Glu) or pyruvate (-> Ala; K16871)", DED,
      "GABA / polyamine catabolism; no must-build product.",
      debatable="With 2-oxoglutarate as acceptor the N returns to glutamate, so no net N leaves the Glu pool.")])

add("Glu", "Glu_methylaspartate", "methylaspartate route", "map00630 (C5-branched dibasic acid); map00250", [
    S("GLMUT", "glutamate mutase (methylaspartate mutase)", "L-glutamate <=> L-threo-3-methylaspartate",
      ["K01846", "K19268"], "5.4.99.1", False, "", "", DED, "Glutamate fermentation only (clostridial-type route).",
      notes="Two subunits: sigma K01846 (glmS/mutS) AND epsilon K19268 (glmE/mutE) are both required."),
    S("MAL", "3-methylaspartate ammonia-lyase", "L-threo-3-methylaspartate -> mesaconate + NH4+", ["K04835"],
      "4.3.1.2", True, NH4, "", DED, "Glutamate fermentation only.")],
    note="Added on critic review.")

# ---- Gly ------------------------------------------------------------------------------------
add("Gly", "Gly_cleavage", "glycine cleavage system", "M00621", [GCS_P, GCS_T],
    note="All-shared route.")
add("Gly", "Gly_oxidase", "glycine oxidase", "map00260; M00895", [
    S("THIO", "glycine oxidase", "glycine + O2 -> glyoxylate imine (-> glyoxylate + NH4+) + H2O2",
      ["K03153"], "1.4.3.19", True, NH4, "", SH,
      "Thiamine biosynthesis (M00895, thiazole moiety).",
      notes="In thiamine synthesis the imine N is kept in the thiazole; NH4+ is freed only if the imine hydrolyses.")],
    note="All-shared route.")
add("Gly", "Gly_transamination", "glycine transamination", "map00260; map00630", [
    S("GLY_AT", "glycine transamination", "glycine + 2-oxo acid <=> glyoxylate + L-amino acid",
      ["K00830", "K00827", "K05825", "K14272", "K28204"], "2.6.1.4;2.6.1.44", True, TR, "pyruvate (-> Ala) or 2-oxoglutarate (-> Glu)", SH,
      "Photorespiratory glyoxylate -> glycine conversion runs these enzymes in the glycine-forming direction.",
      debatable=K00830_DEBATE, notes="KO list = KEGG link/ko/rn for R00372 + R00369.")],
    note="All-shared route.")

# ---- His ------------------------------------------------------------------------------------
add("His", "His_hut", "histidine utilization (hut)", "M00045", [
    S("HUTH", "histidine ammonia-lyase", "L-histidine -> urocanate + NH4+", ["K01745"], "4.3.1.3",
      True, NH4, "", DED, "Histidine catabolism only.",
      notes="Later steps (hutU K01712, hutI K01468, hutG K01479 / K05603+K01458) free more N; context only.")])

# ---- Ile / Leu / Val ------------------------------------------------------------------------
for aa, full, extra_kos, extra_note in [
        ("Ile", "isoleucine", [], ""),
        ("Leu", "leucine", [], "M00036 step 1 (Leu degradation) is K00826."),
        ("Val", "valine", ["K00835", "K14260"], "K00835 avtA / K14260 alaA: L-valine + pyruvate <=> 2-oxoisovalerate + L-alanine (R01215).")]:
    add(aa, f"{aa}_BCAT", f"{full} transamination", "map00280; M00036",
        [S("BCAT_VAL" if extra_kos else "BCAT", "branched-chain amino acid transamination",
           f"L-{full} + 2-oxoglutarate <=> branched-chain 2-oxo acid + L-glutamate",
           ["K00826"] + extra_kos, "2.6.1.42" + (";2.6.1.66" if extra_kos else ""), True, TR,
           "2-oxoglutarate (-> Glu)" + ("; pyruvate (-> Ala; K00835)" if extra_kos else ""), SH,
           "Same reaction is the last step of Ile/Leu/Val biosynthesis (M00019, M00570).",
           notes=extra_note)],
        note="All-shared route.")
    add(aa, f"{aa}_LeuDH", "leucine dehydrogenase", "map00280", [
        S("LEUDH", "leucine dehydrogenase", f"L-{full} + NAD+ + H2O <=> 2-oxo acid + NH4+ + NADH",
          ["K00263"], "1.4.1.9", True, NH4, "", DED, "Branched-chain amino acid catabolism only.",
          debatable="Reversible dehydrogenase (could run in the amino-acid-forming direction); also one enzyme "
                    "credited to all three of Ile, Leu and Val.")])

# ---- Lys (first N-freeing step) -------------------------------------------------------------
add("Lys", "Lys_cadaverine", "lysine decarboxylase / cadaverine route", "M00956", [
    S("LDC", "lysine decarboxylase", "L-lysine -> cadaverine + CO2", ["K01582", "K28682"], "4.1.1.18",
      False, "", "", SH, "Cadaverine is a polyamine; researcher decision: cadA shared."),
    S("CAD_AT", "cadaverine / putrescine aminotransferase", "cadaverine + 2-oxoglutarate <=> 5-aminopentanal + L-glutamate",
      ["K09251"], "2.6.1.82", True, TR, "2-oxoglutarate (-> Glu)", DED,
      "Polyamine catabolism; no must-build product.")])
add("Lys", "Lys_davBA", "lysine 2-monooxygenase route", "M00957", [
    S("DAVB", "lysine 2-monooxygenase", "L-lysine + O2 -> 5-aminopentanamide + CO2 + H2O", ["K00468"],
      "1.13.12.2", False, "", "", DED, "Lysine catabolism only."),
    S("DAVA", "5-aminopentanamidase", "5-aminopentanamide + H2O -> 5-aminopentanoate + NH4+", ["K01506"],
      "3.5.1.30", True, NH4, "", DED, "Lysine catabolism only.")])
add("Lys", "Lys_6AT", "lysine 6-aminotransferase", "map00310", [
    S("LAT", "lysine 6-aminotransferase", "L-lysine + 2-oxoglutarate <=> allysine + L-glutamate",
      ["K03918"], "2.6.1.36", True, TR, "2-oxoglutarate (-> Glu)", DED, "Lysine catabolism only.")])
add("Lys", "Lys_6DH", "lysine 6-dehydrogenase", "map00310", [
    S("LYSDH", "lysine 6-dehydrogenase", "L-lysine + NAD+ -> allysine + NH4+ + NADH", ["K19064"],
      "1.4.1.18", True, NH4, "", DED, "Lysine catabolism only.",
      debatable="Reversible dehydrogenase; treated like the other amino-acid dehydrogenases.")])
add("Lys", "Lys_saccharopine", "saccharopine route", "M00032", [
    S("LKR", "lysine-ketoglutarate reductase", "L-lysine + 2-oxoglutarate + NADPH -> saccharopine",
      ["K14157"], "1.5.1.8", False, "", "", DED, "Lysine catabolism only."),
    S("SDH_SACCH", "saccharopine dehydrogenase", "saccharopine + NAD+ -> allysine + L-glutamate + NADH",
      ["K14157"], "1.5.1.9", True, GLU, "", DED, "Lysine catabolism only.",
      notes="K14157 (AASS) is bifunctional and carries both steps.")])

# ---- Met ------------------------------------------------------------------------------------
add("Met", "Met_gamma_lyase", "methionine gamma-lyase", "map00270", [
    S("MGL", "methionine gamma-lyase", "L-methionine + H2O -> methanethiol + 2-oxobutanoate + NH4+",
      ["K01761"], "4.4.1.11", True, NH4, "", DED, "Methionine catabolism only.")])
add("Met", "Met_transamination", "methionine transamination", "map00270", [
    S("MET_AT", "methionine transaminase", "L-methionine + 2-oxo acid <=> 4-methylthio-2-oxobutanoate + L-amino acid",
      ["K14287", "K21346"], "2.6.1.88", True, TR, "2-oxo acid (unspecified)", SH,
      "Same reaction (reverse) is the last step of the methionine salvage cycle, which rebuilds methionine.",
      debatable="Whether the methionine salvage cycle is required in cyanobacteria is not established here.")],
    note="All-shared route.")
add("Met", "Met_transsulfuration", "SAM cycle + reverse transsulfuration", "M00035; map00270", [
    S("METK", "S-adenosylmethionine synthetase", "L-methionine + ATP -> S-adenosyl-L-methionine", ["K00789"],
      "2.5.1.6", False, "", "", SH, "SAM is an essential cofactor.",
      notes="SAM -> SAH by any SAM-dependent methyltransferase (no single KO; not listed)."),
    S("SAHH", "adenosylhomocysteinase", "S-adenosyl-L-homocysteine + H2O -> L-homocysteine + adenosine",
      ["K01251"], "3.13.2.1", False, "", "", SH, "Recycles SAH from every SAM-dependent methylation."),
    S("CBS", "cystathionine beta-synthase", "L-homocysteine + L-serine -> L-cystathionine + H2O",
      ["K01697"], "4.2.1.22", False, "", "", DED,
      "Reverse transsulfuration; not needed to make Cys or Met in cyanobacteria [interpretation].",
      notes="K10150 (cysO, cysteine synthase with CBS activity) excluded: cysteine biosynthesis enzyme."),
    S("CTH", "cystathionine gamma-lyase", "L-cystathionine + H2O -> L-cysteine + 2-oxobutanoate + NH4+",
      ["K01758", "K17217"], "4.4.1.1", True, NH4, "", DED,
      "Reverse transsulfuration; frees the homocysteine-derived (methionine) N [interpretation].",
      debatable=CTH_DEBATE)])

# ---- Phe ------------------------------------------------------------------------------------
add("Phe", "Phe_PAL", "phenylalanine ammonia-lyase", "map00360", [
    S("PAL", "phenylalanine ammonia-lyase", "L-phenylalanine -> trans-cinnamate + NH4+", ["K10775", "K13064"],
      "4.3.1.24;4.3.1.25", True, NH4, "", DED, "Phenylalanine catabolism / secondary metabolism only.")])
add("Phe", "Phe_PheDH", "phenylalanine dehydrogenase", "map00360", [
    S("PHEDH", "phenylalanine dehydrogenase", "L-phenylalanine + NAD+ + H2O <=> phenylpyruvate + NH4+ + NADH",
      ["K00270"], "1.4.1.20", True, NH4, "", DED, "Phenylalanine catabolism only.",
      debatable="Reversible dehydrogenase; could run in the Phe-forming direction.")])
add("Phe", "Phe_transamination", "phenylalanine transamination", "map00360; M00024", [
    S("PHE_AT", "phenylalanine transamination", "L-phenylalanine + 2-oxoglutarate <=> phenylpyruvate + L-glutamate",
      AROM_AT_KOS, "2.6.1.1;2.6.1.5;2.6.1.9;2.6.1.57", True, TR, "2-oxoglutarate (-> Glu)", SH,
      "Same reaction (reverse) is the last step of Phe biosynthesis via phenylpyruvate (M00024); MED4 pheA PMM1504 "
      "(prephenate dehydratase) indicates this route [KG annotation + interpretation].",
      debatable=AROM_AT_DEBATE)])
add("Phe", "Phe_hydroxylase_Tyr", "phenylalanine hydroxylase to tyrosine, then tyrosine transamination", "map00360; M00044", [
    S("PHHA", "phenylalanine 4-hydroxylase", "L-phenylalanine + O2 + BH4 -> L-tyrosine", ["K00500"],
      "1.14.16.1", False, "", "", DED, "Tyrosine is made from prephenate via tyrA (MED4 PMM1565, prephenate "
      "dehydrogenase) and transamination, not by hydroxylating Phe; route inferred from annotation [KG + interpretation]."),
    TYR_AT])

# ---- Pro ------------------------------------------------------------------------------------
add("Pro", "Pro_PutA", "proline to glutamate (PutA)", "M00970", [
    S("PRODH", "proline dehydrogenase", "L-proline + acceptor -> 1-pyrroline-5-carboxylate", ["K00318", "K13821"],
      "1.5.5.2", False, "", "", DED, "Proline catabolism only (biosynthesis uses ProA/ProB/ProC)."),
    S("P5CDH", "1-pyrroline-5-carboxylate dehydrogenase", "L-glutamate 5-semialdehyde + NAD+ -> L-glutamate + NADH",
      ["K00294", "K13821"], "1.2.1.88", True, GLU, "", DED, "Proline catabolism only.",
      notes="K13821 (PutA) is bifunctional and carries both steps.")])

# ---- Ser ------------------------------------------------------------------------------------
add("Ser", "Ser_dehydratase", "L-serine dehydratase", "map00260", [
    S("SDA", "L-serine ammonia-lyase", "L-serine -> pyruvate + NH4+", ["K01752"],
      "4.3.1.17", True, NH4, "", DED, "Serine catabolism only (R00220 is not needed for any biosynthesis).",
      debatable="K01754 (ilvA) and K17989 (SDS) also carry R00220 but are the Ile-biosynthesis threonine "
                "dehydratases (M00570); they are treated identically as side activities (broad table) so the Ser "
                "and Thr contexts agree. Only K01752 is credited here.")])
add("Ser", "Ser_SHMT_GCS", "serine to glycine, then glycine cleavage", "map00260; M00621", [
    S("SHMT", "serine hydroxymethyltransferase", "L-serine + THF <=> glycine + 5,10-methylene-THF",
      ["K00600"], "2.1.2.1", False, "", "", SH, "Main C1 and glycine source."),
    GCS_P, GCS_T], note="All-shared route.")
add("Ser", "Ser_transamination", "serine transamination", "map00260; map00630", [
    S("SER_AT", "serine--pyruvate / serine--glyoxylate transamination",
      "L-serine + pyruvate (or glyoxylate) <=> 3-hydroxypyruvate + L-alanine (or glycine)",
      ["K00830", "K13290"], "2.6.1.51;2.6.1.45", True, TR, "pyruvate (-> Ala) or glyoxylate (-> Gly)", SH,
      "Photorespiratory serine/glyoxylate interconversion (needed for photorespiratory glycine/serine) [interpretation].",
      debatable=K00830_DEBATE, notes="KO list = KEGG link/ko/rn for R00585 + R00588.")],
    note="All-shared route.")

# ---- Thr ------------------------------------------------------------------------------------
add("Thr", "Thr_dehydratase", "threonine dehydratase", "M00570 (step 1)", [
    S("THR_DH", "threonine ammonia-lyase", "L-threonine -> 2-oxobutanoate + NH4+", ["K01754", "K17989"],
      "4.3.1.19", True, NH4, "", SH, "First step of isoleucine biosynthesis (M00570).",
      debatable="Catabolic isozymes (tdcB) share KO K01754 with biosynthetic ilvA, and K17989 (SDS) is listed in "
                "M00570 too; KO cannot separate catabolic from biosynthetic. The same KOs are side activities for Ser.")],
    note="All-shared route.")
add("Thr", "Thr_aldolase", "threonine aldolase, then glycine cleavage", "map00260; M00621", [
    S("LTAE", "threonine aldolase", "L-threonine -> glycine + acetaldehyde", ["K01620"], "4.1.2.48",
      False, "", "", DED, "Cyanobacteria make glycine from serine and photorespiration [interpretation].",
      debatable="In some organisms threonine aldolase is a glycine-biosynthesis route."),
    GCS_P, GCS_T])
add("Thr", "Thr_TDH_kbl", "threonine dehydrogenase + kbl, then glycine cleavage", "map00260; M00621", [
    S("TDH", "threonine 3-dehydrogenase", "L-threonine + NAD+ -> L-2-amino-3-oxobutanoate + NADH",
      ["K00060", "K15789"], "1.1.1.103", False, "", "", DED, "Threonine catabolism only."),
    S("KBL", "2-amino-3-ketobutyrate CoA ligase", "L-2-amino-3-oxobutanoate + CoA -> glycine + acetyl-CoA",
      ["K00639"], "2.3.1.29", False, "", "", DED, "Threonine catabolism only.",
      notes="Pilot: MED4 PMM1468 sits on K00639 but its product is 8-amino-7-oxononanoate synthase (bioF, "
            "biotin) - KO/product disagreement to review at scoring."),
    GCS_P, GCS_T])

# ---- Trp ------------------------------------------------------------------------------------
add("Trp", "Trp_tryptophanase", "tryptophanase", "map00380", [
    S("TNAA", "tryptophanase", "L-tryptophan + H2O -> indole + pyruvate + NH4+", ["K01667"], "4.1.99.1",
      True, NH4, "", DED, "Tryptophan catabolism only.")])
add("Trp", "Trp_kynurenine_Ala", "kynurenine route (kynureninase), then alanine transamination", "M00038; map00380", [
    S("TDO", "tryptophan 2,3-dioxygenase / indoleamine 2,3-dioxygenase", "L-tryptophan + O2 -> N-formylkynurenine",
      ["K00453", "K00463"], "1.13.11.11;1.13.11.52", False, "", "", DED, "Tryptophan catabolism only."),
    S("KFA", "kynurenine formamidase", "N-formylkynurenine + H2O -> L-kynurenine + formate",
      ["K01432", "K14263", "K07130"], "3.5.1.9", False, "", "", DED, "Tryptophan catabolism only."),
    S("KYNU", "kynureninase", "L-kynurenine + H2O -> anthranilate + L-alanine", ["K01556"], "3.7.1.3",
      False, "", "", DED, "Tryptophan catabolism only (N moves into alanine)."),
    ALA_AT],
    note="N leaves as alanine; extended to alanine transamination (shared anchor).")
add("Trp", "Trp_kynurenine_KAT", "kynurenine route (kynurenine aminotransferase)", "map00380", [
    S("TDO", "tryptophan 2,3-dioxygenase / indoleamine 2,3-dioxygenase", "L-tryptophan + O2 -> N-formylkynurenine",
      ["K00453", "K00463"], "1.13.11.11;1.13.11.52", False, "", "", DED, "Tryptophan catabolism only."),
    S("KFA", "kynurenine formamidase", "N-formylkynurenine + H2O -> L-kynurenine + formate",
      ["K01432", "K14263", "K07130"], "3.5.1.9", False, "", "", DED, "Tryptophan catabolism only."),
    S("KAT", "kynurenine--oxoglutarate transaminase", "L-kynurenine + 2-oxoglutarate -> kynurenate (via 4-(2-aminophenyl)-2,4-dioxobutanoate) + L-glutamate",
      ["K00816", "K00825", "K14264"], "2.6.1.7", True, TR, "2-oxoglutarate (-> Glu)", DED,
      "No biosynthetic role in cyanobacteria [interpretation].",
      debatable="K00816 (CCBL) and K00825 (AADAT) are multi-substrate aminotransferases.")])
add("Trp", "Trp_IAM", "indole-3-acetamide route", "map00380", [
    S("IAAM", "tryptophan 2-monooxygenase", "L-tryptophan + O2 -> indole-3-acetamide + CO2 + H2O", ["K00466"],
      "1.13.12.3", False, "", "", DED, "Tryptophan catabolism / auxin synthesis only."),
    S("IAAH", "indoleacetamide hydrolase", "indole-3-acetamide + H2O -> indole-3-acetate + NH4+", ["K21801"],
      "3.5.1.-", True, NH4, "", DED, "Tryptophan catabolism / auxin synthesis only.",
      notes="Generic amidase amiE (K01426, EC 3.5.1.4) can also hydrolyse IAM; not listed (broad amidase).")])
add("Trp", "Trp_transamination", "tryptophan transamination", "map00380", [
    S("TRP_AT", "tryptophan transamination", "L-tryptophan + 2-oxoglutarate <=> indole-3-pyruvate + L-glutamate",
      ["K14265", "K00838", "K00832"], "2.6.1.27", True, TR, "2-oxoglutarate (-> Glu)", DED,
      "Reaction-level rule: Trp biosynthesis uses no transamination, so R00684 is needed for nothing else.",
      debatable="KEGG links R00684 only to K14265 (Tam1); K00838 (via EC 2.6.1.27) and K00832 tyrB (multi-substrate "
                "aromatic AT, added on review) are biosynthetic aromatic aminotransferases present in nearly every genome, "
                "so by the exclusion rule they never credit this dedicated step: only K14265 can.")])

# ---- Tyr ------------------------------------------------------------------------------------
add("Tyr", "Tyr_TAL", "tyrosine ammonia-lyase", "map00350", [
    S("TAL", "tyrosine ammonia-lyase", "L-tyrosine -> 4-coumarate + NH4+", ["K10774", "K13064"],
      "4.3.1.23;4.3.1.25", True, NH4, "", DED, "Tyrosine catabolism / secondary metabolism only.")])
add("Tyr", "Tyr_phenol_lyase", "tyrosine phenol-lyase", "map00350", [
    S("TPL", "tyrosine phenol-lyase", "L-tyrosine + H2O -> phenol + pyruvate + NH4+", ["K01668"], "4.1.99.2",
      True, NH4, "", DED, "Tyrosine catabolism only.")])
add("Tyr", "Tyr_transamination", "tyrosine transamination", "M00044 (step 1)", [TYR_AT],
    note="All-shared route; downstream hppD (K00457) also serves tocopherol/plastoquinone synthesis.")

# ---------------------------------------------------------------------------------------------
# Broad-specificity, D-amino-acid and side-activity enzymes: never credited to an amino acid.
# ---------------------------------------------------------------------------------------------
BROAD = [
    ("K03334", "LAAO", "1.4.3.2", "broad L", "L-amino-acid oxidase, many L-amino acids -> 2-oxo acid + NH4+", "M00044 step 1 alternative"),
    ("K00273", "DAO", "1.4.3.3", "D-amino acid", "D-amino-acid oxidase", ""),
    ("K00285", "dadA", "1.4.5.1", "D-amino acid", "D-amino-acid dehydrogenase (D-Ala and others)", "pilot listed under Ala"),
    ("K00824", "dat", "2.6.1.21", "D-amino acid", "D-alanine transaminase", ""),
    ("K05396", "dcyD", "4.4.1.15", "D-amino acid", "D-cysteine desulfhydrase", "pilot listed under Cys"),
    ("K01753", "dsdA", "4.3.1.18", "D-amino acid", "D-serine ammonia-lyase", "pilot listed under Ser"),
    ("K20498", "DSD1", "4.3.1.18", "D-amino acid", "D-serine ammonia-lyase (eukaryotic type)", ""),
    ("K14267", "dapC", "2.6.1.17", "multi-substrate biosynthetic AT (enzyme-level override)", "N-succinyldiaminopimelate aminotransferase; class I AT used in lysine biosynthesis (M00016)", "pilot ALL row"),
    ("K10907", "K10907", "2.6.1.-", "broad aminotransferase", "aminotransferase, substrate unspecified", "pilot ALL row"),
    ("K00837", "ISS1/VAS1", "2.6.1.-", "broad aminotransferase", "aromatic aminotransferase, substrate unspecified", "pilot ALL row"),
    ("K01754", "ilvA", "4.3.1.19", "side activity", "threonine dehydratase also deaminates L-serine; credited only as Thr_dehydratase (shared)", ""),
    ("K17989", "SDS", "4.3.1.17;4.3.1.19", "side activity", "L-serine/L-threonine ammonia-lyase; listed in M00570 (Ile biosynthesis) -> credited only as Thr_dehydratase (shared); its Ser activity is a side activity like ilvA's", "pilot Ser;Thr"),
    ("K00817", "hisC", "2.6.1.9", "multi-substrate biosynthetic AT (enzyme-level override)", "histidinol-phosphate aminotransferase; also Phe/Tyr transamination; His biosynthesis", ""),
    ("K00811", "ASP5", "2.6.1.1", "multi-substrate biosynthetic AT (enzyme-level override)", "aspartate aminotransferase (chloroplastic)", ""),
    ("K00812", "aspB", "2.6.1.1", "multi-substrate biosynthetic AT (enzyme-level override)", "aspartate aminotransferase", ""),
    ("K00813", "aspC", "2.6.1.1", "multi-substrate biosynthetic AT (enzyme-level override)", "aspartate aminotransferase", ""),
    ("K11358", "yhdR", "2.6.1.1", "multi-substrate biosynthetic AT (enzyme-level override)", "aspartate aminotransferase", ""),
    ("K14454", "GOT1", "2.6.1.1", "multi-substrate biosynthetic AT (enzyme-level override)", "aspartate aminotransferase, cytoplasmic", ""),
    ("K14455", "GOT2", "2.6.1.1", "multi-substrate biosynthetic AT (enzyme-level override)", "aspartate aminotransferase, mitochondrial", ""),
    ("K15849", "PAT", "2.6.1.1;2.6.1.78;2.6.1.79", "multi-substrate biosynthetic AT (enzyme-level override)", "aspartate/prephenate aminotransferase", ""),
    ("K00832", "tyrB", "2.6.1.57", "multi-substrate biosynthetic AT (enzyme-level override)", "aromatic-amino-acid aminotransferase (Phe/Tyr biosynthesis)", ""),
    ("K00838", "ARO8", "2.6.1.57;2.6.1.39;2.6.1.27;2.6.1.5", "multi-substrate biosynthetic AT (enzyme-level override)", "aromatic amino acid aminotransferase I", ""),
    ("K01760", "metC", "4.4.1.13", "side activity", "cystathionine beta-lyase (Met biosynthesis); cysteine desulfhydrase side activity", "pilot listed under Cys"),
    ("K14155", "patB/malY", "4.4.1.13", "side activity", "cystathionine beta-lyase family; cysteine desulfhydrase side activity", ""),
]

# Spike draft catalogue -> where each KO went (manual reconciliation; reasons are [interpretation]).
PILOT_EXCLUDED = {
    "K00278": "nadB L-aspartate oxidase: NAD biosynthesis; the imino N is kept in quinolinate, so no N is freed. Not catalogued.",
    "K00611": "argF/arcB OTC: ADI step 2; Arg pathways end at the first N-freeing step (arcA). Context only.",
    "K00926": "arcC carbamate kinase: after the first N-freeing step of ADI. Context only.",
    "K00819": "rocD ornithine aminotransferase: after arginase (first N-freeing step). Context only.",
    "K01428": "ureC urease: urease is shared (researcher decision 3); after arginase/agmatinase. Context only.",
    "K01429": "ureB urease: as ureC.",
    "K01430": "ureA urease: as ureC.",
    "K01738": "cysK cysteine synthase: cysteine biosynthesis; no N-freeing reaction on cysteine. Not catalogued.",
    "K02437": "gcvH: carrier protein of glycine cleavage; not scored (P and T proteins scored).",
    "K01712": "hutU: after hutH (first N-freeing step). Context only.",
    "K01468": "hutI: after hutH. Context only.",
    "K01479": "hutG: after hutH. Context only.",
    "K00817": "hisC histidinol-phosphate aminotransferase: histidine biosynthesis, not breakdown. Moved to proposed controls.",
    "K01915": "glnA: validation probe, moved to proposed controls.",
}


# ---------------------------------------------------------------------------------------------
# Product-agreement rule (proposal section 3 step 2): a gene counts for a step only if its KG product
# contains one of the step's keywords (case-insensitive substring). Otherwise the hit is
# "flagged: KO/product mismatch" and does not count until the researcher reviews it.
# ---------------------------------------------------------------------------------------------
AT = ["aminotransferase", "transaminase"]
PRODUCT_KW = {
    "ALD": ["alanine dehydrogenase"], "ALA_AT": AT,
    "ARGINASE": ["arginase"], "ARGZ": ["arginine dihydrolase"], "ADI": ["arginine deiminase"],
    "ASTA": ["arginine n-succinyltransferase", "arginine succinyltransferase"], "ASTB": ["succinylarginine dihydrolase"],
    "ARUH": ["arginine:pyruvate", "arginine-pyruvate", "arginine transaminase", "arginine aminotransferase"], "ADC": ["arginine decarboxylase"], "AGMATINASE": ["agmatinase"], "AGUA": ["agmatine deiminase"],
    "ASNASE": ["asparaginase"], "ASN_AT": ["asparagine aminotransferase", "asparagine transaminase", "asparagine--oxo-acid", "asparagine-oxo-acid"], "ASPA": ["aspartate ammonia-lyase", "aspartase"], "ASP_AT": AT,
    "CYS_DESULF": ["cysteine desulfidase", "cysteine desulfhydrase"], "CTH_CYS": ["cystathionine gamma-lyase"],
    "CDO": ["cysteine dioxygenase"], "CSA_AT": AT, "GLNASE": ["glutaminase"], "GOGAT": ["glutamate synthase"],
    "GDH": ["glutamate dehydrogenase"], "GAD": ["glutamate decarboxylase"], "GABA_AT": ["4-aminobutyrate aminotransferase", "4-aminobutyrate transaminase", "4-aminobutyrate--", "gaba aminotransferase", "gaba transaminase"],
    "GLMUT": ["methylaspartate mutase", "glutamate mutase"], "MAL": ["methylaspartate ammonia-lyase"],
    "GCS_P": ["glycine dehydrogenase", "glycine cleavage system p"], "GCS_T": ["aminomethyltransferase", "glycine cleavage system t"],
    "THIO": ["glycine oxidase"], "GLY_AT": AT, "HUTH": ["histidine ammonia-lyase"], "BCAT": AT, "BCAT_VAL": AT,
    "LEUDH": ["leucine dehydrogenase"], "LDC": ["lysine decarboxylase"], "CAD_AT": ["putrescine aminotransferase", "diamine aminotransferase", "cadaverine aminotransferase", "putrescine--2-oxoglutarate"],
    "DAVB": ["lysine 2-monooxygenase", "lysine monooxygenase"], "DAVA": ["aminopentanamidase", "aminovaleramidase"], "LAT": ["lysine aminotransferase", "lysine 6-aminotransferase", "lysine epsilon", "lysine 6-transaminase"],
    "LYSDH": ["lysine 6-dehydrogenase", "lysine dehydrogenase"], "LKR": ["aminoadipic semialdehyde synthase", "lysine-ketoglutarate reductase"],
    "SDH_SACCH": ["aminoadipic semialdehyde synthase", "saccharopine dehydrogenase"], "MGL": ["methionine gamma-lyase"],
    "MET_AT": AT, "METK": ["adenosylmethionine synthe", "methionine adenosyltransferase"],
    "SAHH": ["adenosylhomocysteinase", "adenosylhomocysteine hydrolase"], "CBS": ["cystathionine beta-synthase"],
    "CTH": ["cystathionine gamma-lyase"], "PAL": ["phenylalanine ammonia", "phenylalanine/tyrosine ammonia"], "PHEDH": ["phenylalanine dehydrogenase"],
    "PHE_AT": AT, "PHHA": ["phenylalanine 4-hydroxylase", "phenylalanine hydroxylase", "phenylalanine-4-hydroxylase"],
    "TYR_AT": AT, "PRODH": ["proline dehydrogenase", "proline oxidase", "proline utilization", "putA"],
    "P5CDH": ["pyrroline-5-carboxylate dehydrogenase", "proline utilization", "putA"],
    "SDA": ["serine dehydratase", "serine ammonia-lyase"], "SHMT": ["hydroxymethyltransferase"], "SER_AT": AT,
    "THR_DH": ["threonine dehydratase", "threonine ammonia-lyase", "serine/threonine dehydratase"],
    "LTAE": ["threonine aldolase"], "TDH": ["threonine 3-dehydrogenase", "threonine dehydrogenase"],
    "KBL": ["2-amino-3-ketobutyrate", "glycine c-acetyltransferase"], "TNAA": ["tryptophanase"],
    "TDO": ["tryptophan 2,3-dioxygenase", "indoleamine 2,3-dioxygenase"], "KFA": ["kynurenine formamidase", "arylformamidase"],
    "KYNU": ["kynureninase"], "KAT": ["kynurenine aminotransferase", "kynurenine transaminase", "kynurenine--oxoglutarate"], "IAAM": ["tryptophan 2-monooxygenase"], "IAAH": ["indoleacetamide hydrolase", "indole-3-acetamide hydrolase", "indoleacetamide amidase"],
    "TRP_AT": ["tryptophan aminotransferase", "tryptophan transaminase"], "TAL": ["tyrosine ammonia", "phenylalanine/tyrosine ammonia"], "TPL": ["phenol-lyase"],
}

# KEGG reaction ids per step (checked with rest.kegg.jp list/rn and link/ko/rn on 2026-11-04). Steps not
# listed get their EC's main reactions in 02_validate_kos.py (kegg_rn_source = "EC main reactions").
KEGG_RN = {
    "ALA_AT": "R00258;R00369;R01215", "PHE_AT": "R00694", "TYR_AT": "R00734", "TRP_AT": "R00684",
    "ASP_AT": "R00355", "CSA_AT": "R02619", "BCAT": "R01090;R01214;R02199", "BCAT_VAL": "R01214;R01215",
    "GLY_AT": "R00372;R00369", "SER_AT": "R00585;R00588", "GCS_P": "R03425", "GCS_T": "R04125", "KAT": "R01956",
    "MET_AT": "R08618", "THR_DH": "R00996", "SDA": "R00220", "CYS_DESULF": "R00782", "CTH_CYS": "R00782",
    "CTH": "R01001", "GOGAT": "R00093;R00114;R00021", "GDH": "R00243;R00248", "THIO": "R00366;R07463",
    "ARGZ": "R13308", "ASNASE": "R00485", "GLNASE": "R00256", "ADC": "R00566", "LDC": "R00462", "METK": "R00177", "SHMT": "R00945",
    "KBL": "R00371",
}

# AND groups (CNF): groups separated by ";" (all required), alternatives within a group by "|".
# Steps not listed: one group, any KO.
KO_GROUPS = {
    "GCS_P": "K00281|K00282;K00281|K00283",                      # gcvP, or gcvPA AND gcvPB
    "GOGAT": "K00265|K00264|K00284;K00266|K00264|K00284",        # gltB AND gltD, or GLT1, or Fd-GOGAT
    "GLMUT": "K01846;K19268",                                    # sigma AND epsilon subunit
}

# Pathways excluded from assessability, and assessability notes.
N_NEUTRAL = {"Glu_GABA_shunt": "With 2-oxoglutarate as GABA acceptor the N returns to glutamate: no net N freed."}
ASSESS_NOTE = {"Arg_argZ": "ArgZ KOs K27545/K27542 have no node in the KG; assessing ArgZ would need a homolog-based "
                           "search (a possible later extension). KEGG M00978 lists (K27542,K27545) as alternatives, "
                           "not subunits, so no AND group."}

# Every flag / KO-list change made after the critic review (old -> new).
FLAG_CHANGE_LOG = [
    # step_key, field, old, new, reason
    ("CTH_CYS", "debatable_reason", "Cys side substrate", "K01758 MetB/MetC cross-annotation (see CTH_DEBATE)", "critic Blocker 1"),
    ("CTH", "debatable", "no", "yes", "critic Blocker 1: consistent with CTH_CYS; MetB/MetC cross-annotation"),
    ("ALA_AT", "kos", "K14260;K00814;K14272", "+K00830;K00827;K05825;K28204;K00835", "critic Blocker 2: KEGG link/ko/rn R00258+R00369+R01215"),
    ("ALA_AT", "debatable", "no", "yes", "K00830 consistency (ALA_AT/GLY_AT/SER_AT)"),
    ("PHE_AT", "kos", "K00815;K00832;K00838", "12 KOs of KEGG link/ko/rn R00694", "critic Blocker 2"),
    ("PHE_AT", "flag", "shared", "dedicated", "reaction-level rule; MED4 makes Phe via arogenate (R00691 PMM1504)"),
    ("PHE_AT", "debatable", "no", "yes", "multi-substrate biosynthetic ATs; phenylpyruvate route in other strains"),
    ("TYR_AT", "kos", "K00815;K00832;K00838", "12 KOs of KEGG link/ko/rn R00734", "critic Blocker 2"),
    ("TYR_AT", "flag", "shared", "dedicated", "reaction-level rule; MED4 makes Tyr via arogenate (R00733 PMM1565)"),
    ("TYR_AT", "debatable", "no", "yes", "as PHE_AT"),
    ("TRP_AT", "kos", "K00838;K14265", "K14265;K00838;K00832", "critic: add tyrB K00832"),
    ("TRP_AT", "flag", "shared", "dedicated", "reaction-level rule: Trp biosynthesis uses no transamination"),
    ("GLY_AT", "kos", "K00830;K00827;K14272", "+K05825;K28204", "KEGG link/ko/rn R00372+R00369"),
    ("GLY_AT", "debatable", "no", "yes", "K00830 consistency"),
    ("SER_AT", "debatable_reason", "photorespiration not established", "K00830 consistency text", "K00830 consistency"),
    ("SDA", "kos", "K01752;K17989", "K01752", "K17989 consistency: SDS treated like ilvA (side activity, broad table)"),
    ("SDA", "debatable", "no", "yes", "K17989/K01754 handling"),
    ("ALD", "debatable_reason", "reversible", "reversible (unchanged value yes)", "reversible dehydrogenases"),
    ("LEUDH", "debatable_reason", "credited to 3 aa", "reversible + credited to 3 aa (value yes)", "reversible dehydrogenases"),
    ("PHEDH", "debatable", "no", "yes", "reversible dehydrogenases"),
    ("LYSDH", "debatable", "no", "yes", "reversible dehydrogenases"),
    ("PHHA", "flag_reason", "Tyr from prephenate/arogenate", "Tyr from arogenate (MED4 R00733 PMM1565)", "reconciled with PHE_AT/TYR_AT"),
    ("GLMUT;MAL", "new", "", "dedicated", "critic: Glu methylaspartate pathway added"),
    ("ASNASE", "kos", "K01424;K13051;K13278", "+K05597", "KEGG link/ko/rn:R00485 (glutaminase-asparaginase)"),
    ("ASNASE", "debatable", "no", "yes", "K05597 credited to both Asn and Gln"),
    ("GLNASE", "kos", "K01425", "+K05597", "KEGG link/ko/rn:R00256"),
    ("GLNASE", "debatable", "no", "yes", "K05597 credited to both Asn and Gln"),
    ("BCAT_VAL", "kos", "K00826;K00835", "+K14260", "KEGG link/ko/rn:R01215"),
    ("PHE_AT", "flag", "dedicated", "shared", "delta critic: arogenate premise contradicted by pheA/tyrA products"),
    ("TYR_AT", "flag", "dedicated", "shared", "delta critic: arogenate premise contradicted by pheA/tyrA products"),
    ("PHE_AT;TYR_AT", "flag_reason", "arogenate route", "phenylpyruvate route (pheA PMM1504, tyrA PMM1565), annotation-inferred", "delta critic: arogenate premise contradicted by pheA/tyrA products"),
    ("PHHA", "flag_reason", "Tyr from arogenate", "Tyr from prephenate via tyrA + transamination", "delta critic: arogenate premise contradicted by pheA/tyrA products"),
    ("PHE_AT;TYR_AT", "ec", "2.6.1.1;2.6.1.5;2.6.1.57", "2.6.1.1;2.6.1.5;2.6.1.9;2.6.1.57", "delta critic: ec = KEGG ENZYME line of R00694/R00734 (K00817 hisC carries 2.6.1.9)"),
    ("TRP_AT", "ec", "2.6.1.27;2.6.1.57", "2.6.1.27", "delta critic: ec = KEGG ENZYME line of R00684"),
    ("TRP_AT", "credit", "K14265;K00838;K00832", "K14265 only (K00838, K00832 excluded)", "delta critic: exclusion rule"),
    ("ALL dedicated steps", "credit_eligible", "all KOs", "KOs on any shared step / positive control / broad table never credit", "delta critic: exclusion rule"),
    ("ARUH;ASN_AT;GABA_AT;CAD_AT;LAT;PAL;TAL;KFA;KAT;IAAH;TRP_AT;DAVA", "product_keywords", "generic class words", "substrate-naming words", "delta critic: substrate-naming keywords on dedicated steps"),
    ("GLNASE", "kegg_rn", "EC main reactions", "R00256", "delta critic"),
    ("GCS_P;GOGAT;GLMUT", "ko_groups", "any KO", "AND groups", "critic: multi-subunit steps"),
    ("ASN_AT;GABA_AT;CAD_AT;LAT;KAT;IAAH;TRP_AT", "product_keywords", "bare substrate word", "substrate + enzyme word", "delta critic pass 3"),
    ("TRP_AT", "observable", "computed over all KOs", "computed over credit-eligible KOs only (K14265 not in KG)", "delta critic pass 3"),
]

# ---------------------------------------------------------------------------------------------
# Proposed controls (researcher approves). Chosen from biology and KEGG modules, not from the
# MED4 pilot outcome. Expected-negative: a ranked list; 02_validate_kos.py selects the first
# candidate that is KEGG-valid AND whose KO node exists in the KG with an overall gene_count >= 1
# (ontology_term_details, no organism; per-organism counts are not read). A KO with no gene anywhere
# in the KG can never produce a hit, so it could not detect a KO-matching artefact.
# Disclosure: the ranking and this rule were written in the same working session/commit as the KG lookup.
# ---------------------------------------------------------------------------------------------
CONTROLS = [
    # control_type, control_id, step_name, kos, ec, source_ref, rank, rationale
    ("matching_sanity", "CTRL_glnA", "glutamine synthetase (glnA)", ["K01915"], "6.3.1.2",
     "map00910; M00978 step 1", "",
     "Proposal validation item 1 (fixed). GS is the NH4+ assimilation enzyme of cyanobacteria "
     "[interpretation]. MED4 seen in the pilot (PMM0920)."),
    ("n_transfer_positive", "CTRL_BCAT", "branched-chain amino acid aminotransferase step",
     ["K00826"], "2.6.1.42", "M00019 last step; M00570 last step; M00036 step 1", "core",
     "Last step of Val/Ile biosynthesis (KEGG lists only K00826 for it); Prochlorococcus makes all "
     "20 amino acids [interpretation]. Not blind for MED4 (pilot). Single-KO step: an alternative "
     "enzyme (e.g. tyrB K00832 for Leu, avtA K00835 for Val) would be invisible here."),
    ("n_transfer_positive", "CTRL_HisC", "histidinol-phosphate aminotransferase step",
     ["K00817"], "2.6.1.9", "M00026 (step K00817)", "core",
     "Histidine biosynthesis has no route around this transamination; KEGG M00026 lists only K00817. "
     "Not blind for MED4 (pilot). Some bacteria carry HisC activity on other class I ATs, which "
     "this KO list would miss."),
    ("n_transfer_positive", "CTRL_AspAT", "aspartate aminotransferase step (OAA + Glu -> Asp)",
     ASP_AT_KOS, "2.6.1.1", "map00250; M00040 (K15849)", "optional",
     "Aspartate is made by transamination of oxaloacetate [interpretation]; all KEGG KOs for "
     "EC 2.6.1.1 included. Not blind for MED4 (pilot: PMM0674 on K00812)."),
    ("expected_negative", "NEG_tnaA", "tryptophanase (Trp_tryptophanase.1)", ["K01667"], "4.1.99.1",
     "map00380", "1",
     "Tryptophanase (indole production) is described from enteric and other heterotrophic bacteria; "
     "no report places it in cyanobacteria [interpretation]. A hit is more likely a KO artefact."),
    ("expected_negative", "NEG_TPL", "tyrosine phenol-lyase (Tyr_phenol_lyase.1)", ["K01668"], "4.1.99.2",
     "map00350", "2",
     "Tyrosine phenol-lyase is known from enterobacteria (e.g. Citrobacter, Erwinia) and insect "
     "symbionts; not cyanobacteria [interpretation]."),
    ("expected_negative", "NEG_astB", "succinylarginine dihydrolase (Arg_AST.2)", ["K01484"], "3.5.3.23",
     "M00879", "3",
     "The AST arginine pathway is a proteobacterial (E. coli, Pseudomonas) route [interpretation]."),
]


CTRL_KW = {"CTRL_glnA": ["glutamine synthetase"], "CTRL_BCAT": AT, "CTRL_HisC": AT + ["histidinol-phosphate"],
           "CTRL_AspAT": AT, "NEG_tnaA": ["tryptophanase"], "NEG_TPL": ["phenol-lyase"],
           "NEG_astB": ["succinylarginine dihydrolase"]}


def main():
    ctrl = pd.DataFrame(CONTROLS, columns=["control_type", "control_id", "step_name", "kos", "ec",
                                           "source_ref", "rank_or_tier", "rationale"])
    ctrl["kos"] = ctrl.kos.map(";".join)
    ctrl["product_keywords"] = ctrl.control_id.map(lambda c: "|".join(CTRL_KW[c]))
    ctrl["disclosure"] = ctrl.control_type.map(lambda c: (
        "The ranking and the selection rule were written in the same commit as the KG lookup that applied them; "
        "they are not pre-registered independently of it.") if c == "expected_negative" else "")
    DATA.mkdir(parents=True, exist_ok=True)
    ctrl.to_csv(DATA / "proposed_controls.csv", index=False, encoding="utf-8")
    rows = []
    for p in P:
        for i, s in enumerate(p["steps"], 1):
            rows.append(dict(amino_acid=p["amino_acid"], pathway_id=p["pathway_id"],
                             pathway_name=p["pathway_name"], source_ref=p["source_ref"],
                             step_order=i, n_steps=len(p["steps"]),
                             step_id=f"{p['pathway_id']}.{i}", step_key=s["step_key"],
                             step_name=s["step_name"], reaction=s["reaction"],
                             kos=";".join(s["kos"]), ec=s["ec"], is_n_freeing=s["is_n_freeing"],
                             n_mode=s["n_mode"], acceptor=s["acceptor"], flag=s["flag"],
                             flag_reason=s["flag_reason"],
                             debatable="yes" if s["debatable_reason"] else "no",
                             debatable_reason=s["debatable_reason"], notes=s["notes"],
                             pathway_note=p["pathway_note"],
                             product_keywords="|".join(PRODUCT_KW[s["step_key"]]),
                             kegg_rn=KEGG_RN.get(s["step_key"], ""),
                             ko_groups=KO_GROUPS.get(s["step_key"], "|".join(s["kos"])),
                             n_neutral_pathway=N_NEUTRAL.get(p["pathway_id"], ""),
                             assess_note=ASSESS_NOTE.get(p["pathway_id"], "")))
    steps = pd.DataFrame(rows)

    # --- invariants of the v5 rules ---
    for pid, g in steps.groupby("pathway_id"):
        nf = g[g.is_n_freeing]
        assert len(nf) == 1, f"{pid}: expected exactly one N-freeing step, got {len(nf)}"
        assert nf.step_order.iloc[0] == g.step_order.max(), f"{pid}: N-freeing step is not the last step"
    for key, g in steps.groupby("step_key"):
        assert g.flag.nunique() == 1 and g.kos.nunique() == 1, f"step_key {key} inconsistent"
    assert steps.step_id.is_unique
    for _, s in steps.iterrows():  # every ko_groups KO is in the step's KO list and vice versa
        gk = {k for g in s.ko_groups.split(";") for k in g.split("|")}
        assert gk == set(s.kos.split(";")), s.step_id
    aas = sorted(steps.amino_acid.unique())
    assert len(aas) == 20, aas

    # pathway-level class (for the review page): all-shared = cannot be judged from genome
    pclass = steps.groupby("pathway_id").flag.apply(lambda f: "all-shared" if (f == SH).all() else "has dedicated")
    steps["pathway_class"] = steps.pathway_id.map(pclass)

    long = steps.assign(ko=steps.kos.str.split(";")).explode("ko")
    long = long[["amino_acid", "pathway_id", "pathway_name", "source_ref", "step_order", "step_id",
                 "step_key", "step_name", "ko", "ko_groups", "ec", "is_n_freeing", "n_mode", "acceptor", "flag",
                 "flag_reason", "debatable", "debatable_reason", "pathway_class", "product_keywords"]]

    # ---- exclusion rule (delta critic): a KO that sits on ANY shared step, ANY positive control
    # (matching_sanity / n_transfer_positive) or the broad table never credits a dedicated step.
    broad_kos = {b[0] for b in BROAD}
    shared_kos = set(long[long.flag == SH].ko)
    pos_kos = {k for c in CONTROLS if c[0] in ("matching_sanity", "n_transfer_positive") for k in c[3]}

    def excl(r):
        if r.flag != DED:
            return ""
        why = [w for w, s in (("on a shared step", shared_kos), ("positive-control KO", pos_kos),
                              ("broad table", broad_kos)) if r.ko in s]
        return "; ".join(why)
    long["exclusion_reason"] = long.apply(excl, axis=1)
    long["credit_eligible"] = long.exclusion_reason == ""
    ded_ok = long[(long.flag == DED) & long.credit_eligible]
    aa_by_ko = ded_ok.groupby("ko").amino_acid.apply(lambda s: sorted(set(s)))
    long["credits_multiple_aa"] = long.apply(
        lambda r: ";".join(aa_by_ko[r.ko]) if r.flag == DED and r.credit_eligible and len(aa_by_ko.get(r.ko, [])) > 1 else "", axis=1)
    moved = long[~long.credit_eligible][["step_id", "step_key", "amino_acid", "ko", "exclusion_reason"]]
    moved.to_csv(DATA / "exclusion_moves.csv", index=False, encoding="utf-8")
    empty = [sid for sid, g in long[long.flag == DED].groupby("step_id") if not g.credit_eligible.any()]
    print("exclusion rule: KO rows moved:", len(moved), "| dedicated steps left with no creditable KO:", empty)
    print(moved.to_string(index=False))

    broad = pd.DataFrame(BROAD, columns=["ko", "label", "ec", "category", "description", "pilot_note"])
    broad["credited"] = False

    # pilot reconciliation
    pilot = pd.read_csv(SPIKE, encoding="utf-8")
    cat_kos = set(long.ko)
    rec = []
    for _, r in pilot.iterrows():
        k = r.ko
        if k in cat_kos:
            where = "catalogue: " + ";".join(sorted(set(long.loc[long.ko == k, "step_id"])))
        elif k in set(broad.ko):
            where = "broad_enzymes"
        elif k in PILOT_EXCLUDED:
            where = "excluded: " + PILOT_EXCLUDED[k]
        else:
            where = "UNRECONCILED"
        rec.append(dict(pilot_amino_acid=r.amino_acid, ko=k, pilot_label=r.label,
                        pilot_shared=r.shared_interpretation, new_location=where))
    rec = pd.DataFrame(rec)
    log = pd.DataFrame(FLAG_CHANGE_LOG, columns=["step_key", "field", "old", "new", "reason"]).assign(date="2026-11-04")
    log.insert(0, "row_id", range(1, len(log) + 1))
    # rows later reversed by the delta critic (row ids count data rows; CSV line = row_id + 1)
    SUPERSEDED = {6: "29;31", 9: "30;31", 22: "32"}
    log["superseded_by"] = log.row_id.map(SUPERSEDED).fillna("")
    assert log.loc[log.row_id == 6, "step_key"].item() == "PHE_AT" and log.loc[log.row_id == 9, "step_key"].item() == "TYR_AT"
    assert log.loc[log.row_id == 22, "step_key"].item() == "PHHA"
    log.to_csv(DATA / "flag_change_log.csv", index=False, encoding="utf-8")

    DATA.mkdir(parents=True, exist_ok=True)
    steps.to_csv(DATA / "pathway_catalogue_steps.csv", index=False, encoding="utf-8")
    long.to_csv(DATA / "pathway_catalogue.csv", index=False, encoding="utf-8")
    broad.to_csv(DATA / "broad_enzymes.csv", index=False, encoding="utf-8")
    rec.to_csv(DATA / "pilot_reconciliation.csv", index=False, encoding="utf-8")

    print("pathways:", steps.pathway_id.nunique(), "| steps:", len(steps),
          "| distinct step_keys:", steps.step_key.nunique(), "| KO rows:", len(long),
          "| distinct KOs:", long.ko.nunique())
    print("step flags:", steps.flag.value_counts().to_dict(), "| debatable steps:",
          int((steps.debatable == "yes").sum()))
    print("pathway classes:", pclass.value_counts().to_dict())
    print("broad:", len(broad), "| pilot rows:", len(rec), "| unreconciled:",
          int((rec.new_location == "UNRECONCILED").sum()))
    print(rec[rec.new_location == "UNRECONCILED"].to_string())


if __name__ == "__main__":
    main()
