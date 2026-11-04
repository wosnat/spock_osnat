"""Methods step 3 - cross-check the catalogue against the KG reaction layer, MED4 ONLY.

For each of the 20 amino acids: genes_by_metabolite(metabolite_ids=<generic + L (+ D) ids>,
organism='MED4', evidence_sources=['metabolism'], include_stereo_forms=True, limit=None).
Metabolite ids are the ones resolved in the pilot (spike/data/med4_aa_metabolite_ids.csv; KEGG
compound ids, not organism data); a copy is written to methods/data/aa_metabolite_ids.csv.

Each MED4 gene's KO comes from gene_ontology_terms(ontology='kegg', organism='MED4').
A row is "covered" only if its gene carries a KO of a step of THAT amino acid whose KEGG reaction list
(step_reactions.csv) contains the row reaction. Uncovered reactions are candidates; each is judged BY HAND from
the KEGG equation (which side the amino acid is on, whether N leaves it), never from the EC prefix.
The KG carries no substrate/product role or reversibility flag (docs://tools/genes_by_metabolite),
so `aa_side` is the side of the equation as KEGG writes it; direction is a curated judgement.

Outputs: crosscheck_all_reactions_med4.csv (every gene x reaction x amino-acid row, annotated)
         crosscheck_candidates_med4.csv   (one row per uncovered reaction x amino acid, with decision)
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/methods/scripts/03_crosscheck_med4.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from multiomics_explorer import gene_ontology_terms, genes_by_metabolite

MDIR = Path(__file__).resolve().parents[1]
DATA = MDIR / "data"
IDS = MDIR.parent / "spike" / "data" / "med4_aa_metabolite_ids.csv"
ORG = "MED4"

# Curated decisions for uncovered reactions, keyed by (amino_acid, reaction_id):
# (removes_N_from_aa: yes/no, aa_role, proposal: add/reject-proposed, reason)
# Filled after reading the first-pass dump; every judgement is [interpretation] from the equation.
R = "reject-proposed"
TRNA = ("no", "substrate (incorporated)", R, "Aminoacyl-tRNA synthetase: the amino acid is loaded onto tRNA for protein synthesis; N is kept.")
PROD = ("no", "product", R, "The amino acid is a product of this reaction (biosynthesis or release); nothing is removed from it.")
AMIDO = ("formally yes (amide N donated)", "substrate", R,
         "Glutamine amidotransferase of a biosynthetic pathway (nucleotide / cofactor / amino sugar / amino acid): "
         "the amide N is donated into a must-build product, Gln -> Glu. Shared biosynthesis, not breakdown; "
         "the shared Gln -> Glu conversion is already represented by Gln_GOGAT.")
AMIDO_REV = ("formally yes (amide N donated)", "product as written; substrate physiologically", R,
             "Written with Gln on the right, but physiologically Gln is the amide donor of this biosynthetic "
             "amidotransferase; shared biosynthesis, not breakdown (see Gln_GOGAT).")
GLU_FROM_GLN = ("no", "product", R, "Glutamate is the by-product of a glutamine amidotransferase; nothing is removed from glutamate.")
ASP_DONOR = ("formally yes (N donated)", "substrate", R,
             "Aspartate donates its amino N into a must-build product (nucleotide or arginine), with fumarate released "
             "later; biosynthesis, not breakdown.")
INCORP = ("no", "substrate (incorporated)", R, "The amino acid is incorporated whole into a biosynthetic product; N is kept.")
BIO_TA = ("formally yes (transamination)", "product as written; N donor physiologically", R,
          "Biosynthetic transamination with glutamate as the N donor into a must-build amino acid "
          "(arginine / lysine); shared biosynthesis, not breakdown.")

BROAD_D = ("yes (NH3)", "substrate (D-form)", R, "D-amino acid oxidase (PMM1703, K00273): broad / D-amino-acid enzyme, never credited.")
GLU_AT_PROD = ("no", "product", R, "Glutamate is formed from the 2-oxoglutarate acceptor of a transamination of another amino acid; "
               "nothing is removed from glutamate.")

DECISIONS: dict[tuple[str, str], tuple[str, str, str, str]] = {
    # ---- Ala
    ("Ala", "kegg.reaction:R00907"): ("formally yes (transamination)", "substrate as written; product physiologically", R,
        "beta-alanine--pyruvate transaminase (EC 2.6.1.18): KEGG places it in beta-alanine catabolism, where alanine is "
        "formed, not consumed. The MED4 gene PMM1472 carries K00822 and K00833 and its product is bioA "
        "(adenosylmethionine-8-amino-7-oxononanoate aminotransferase, biotin); KO/product disagreement."),
    ("Ala", "kegg.reaction:R04187"): ("formally yes (transamination)", "substrate as written; product physiologically", R,
        "Same enzyme as R00907 (EC 2.6.1.18, PMM1472 bioA product); valine/3-aminoisobutanoate catabolism forms alanine."),
    ("Ala", "kegg.reaction:R01150"): ("no", "substrate (incorporated)", R, "D-alanine--D-alanine ligase: D-Ala incorporated into peptidoglycan; D-form."),
    ("Ala", "kegg.reaction:R03038"): TRNA,
    ("Ala", "kegg.reaction:R03193"): INCORP,
    ("Ala", "kegg.reaction:R03599"): PROD,
    ("Ala", "kegg.reaction:R04112"): PROD,
    ("Ala", "kegg.reaction:R07460"): PROD,
    ("Ala", "kegg.reaction:R11528"): PROD,
    # ---- Arg
    ("Arg", "kegg.reaction:R01086"): PROD,
    ("Arg", "kegg.reaction:R03646"): TRNA,
    # ---- Asp
    ("Asp", "kegg.reaction:R00480"): ("no", "substrate", R, "Aspartate kinase: first step of Lys/Thr/Met biosynthesis; N kept."),
    ("Asp", "kegg.reaction:R00481"): ("no", "substrate", R,
        "L-aspartate oxidase (nadB) written as making iminoaspartate, whose N is kept in quinolinate (NAD "
        "biosynthesis); no NH4+ in this equation. The same gene is also linked to R00357 (NH3-releasing form), see that row."),
    ("Asp", "kegg.reaction:R00357"): ("yes (NH3, as written)", "substrate", "add",
        "L-aspartate oxidase (nadB, PMM0100, K00278) linked to the NH3-releasing equation. Its cellular role is NAD "
        "biosynthesis (shared), so if added it is an all-shared Asp route (cannot be judged), parallel to Gly_oxidase "
        "(thiO, thiamine), which the draft does include. Draft pilot had excluded nadB; researcher call for consistency."),
    ("Ala", "kegg.reaction:R00401"): ("no", "both (racemase)", R, "Alanine racemase (alr): L-Ala <=> D-Ala for peptidoglycan; N kept."),
    ("Gln", "kegg.reaction:R00256"): ("formally yes (glutaminase half-reaction)", "substrate", R,
        "Glutaminase half-reaction of carbamoyl-phosphate synthase (carA/carB, PMM0825/PMM0951, K01955/K01956): the NH3 "
        "is channelled into carbamoyl phosphate (arginine and pyrimidine biosynthesis). Shared biosynthesis. Its EC "
        "3.5.1.2 matches Gln_glutaminase, but the genes' KOs are not glutaminase KOs - an EC-only match."),
    ("Glu", "kegg.reaction:R00256"): PROD,
    ("Glu", "kegg.reaction:R04475"): BIO_TA,
    ("Gly", "kegg.reaction:R01221"): ("yes (glycine cleavage)", "substrate", R,
        "Overall glycine-cleavage reaction attached to the carrier proteins H (K02437, PMM1669) and L (K00382, PMM1298); "
        "already represented by Gly_cleavage (P and T proteins scored, carriers not)."),
    ("Asp", "kegg.reaction:R00488"): PROD,
    ("Asp", "kegg.reaction:R00526"): PROD,
    ("Asp", "kegg.reaction:R01135"): ASP_DONOR,
    ("Asp", "kegg.reaction:R01397"): INCORP,
    ("Asp", "kegg.reaction:R01954"): ASP_DONOR,
    ("Asp", "kegg.reaction:R04591"): ASP_DONOR,
    ("Asp", "kegg.reaction:R05577"): TRNA,
    # ---- Cys
    ("Cys", "kegg.reaction:R00897"): PROD,
    ("Cys", "kegg.reaction:R00899"): PROD,
    ("Cys", "kegg.reaction:R02508"): PROD,
    ("Cys", "kegg.reaction:R03217"): ("no", "substrate", R, "Cystathionine gamma-synthase (metB): Cys N kept in cystathionine (Met biosynthesis)."),
    ("Cys", "kegg.reaction:R03260"): ("no", "substrate", R, "Cystathionine gamma-synthase (metB): Cys N kept in cystathionine (Met biosynthesis)."),
    ("Cys", "kegg.reaction:R03650"): TRNA,
    ("Cys", "kegg.reaction:R04231"): INCORP,
    ("Cys", "kegg.reaction:R04859"): PROD,
    ("Cys", "kegg.reaction:R07460"): ("no (N moves to Ala)", "substrate", "add",
        "Cysteine desulfurase (iscS/sufS): Cys -> Ala + S for Fe-S clusters and other cofactors. The Cys N only moves into "
        "alanine, so by the v5 rule the route extends to alanine transamination. Both steps are shared (cofactor sulfur; "
        "Ala biosynthesis), so it would be an all-shared route (cannot be judged); it only affects the "
        "'all-shared route fully present' flag. Researcher call."),
    ("Cys", "kegg.reaction:R11528"): ("no (N moves to Ala)", "substrate", "add",
        "Same cysteine desulfurase as R07460 (protein-persulfide form of the reaction); see R07460."),
    # ---- Gln
    **{("Gln", f"kegg.reaction:{r}"): AMIDO for r in
       ["R00257", "R00573", "R00575", "R00768", "R00986", "R01231", "R01716", "R04463", "R04558", "R05224",
        "R05225", "R05815", "R08244"]},
    **{("Gln", f"kegg.reaction:{r}"): AMIDO_REV for r in ["R01072", "R03905", "R04212"]},
    # ---- Glu
    **{("Glu", f"kegg.reaction:{r}"): GLU_FROM_GLN for r in
       ["R00257", "R00573", "R00575", "R00768", "R00986", "R01231", "R01716", "R04463", "R04558", "R05224",
        "R05225", "R05815", "R08244"]},
    ("Glu", "kegg.reaction:R01072"): ("no", "substrate as written; product physiologically", R,
        "Amidophosphoribosyltransferase (purF) written in reverse; physiologically Gln is the donor and Glu the by-product."),
    ("Glu", "kegg.reaction:R03905"): ("no", "substrate as written; product physiologically", R,
        "Glu-tRNA(Gln) amidotransferase written in reverse; physiologically Glu is a by-product."),
    ("Glu", "kegg.reaction:R04212"): ("no", "substrate as written; product physiologically", R,
        "Asp-tRNA(Asn) amidotransferase written in reverse; physiologically Glu is a by-product."),
    ("Glu", "kegg.reaction:R00239"): ("no", "substrate", R, "Glutamate 5-kinase (proB): first step of proline biosynthesis; N kept."),
    ("Glu", "kegg.reaction:R00259"): ("no", "substrate", R, "N-acetylglutamate formation (argJ): arginine biosynthesis; N kept."),
    ("Glu", "kegg.reaction:R00260"): ("no", "both (racemase)", R, "Glutamate racemase: L-Glu <=> D-Glu for peptidoglycan; N kept."),
    ("Glu", "kegg.reaction:R00942"): INCORP,
    ("Glu", "kegg.reaction:R02237"): INCORP,
    ("Glu", "kegg.reaction:R04241"): INCORP,
    ("Glu", "kegg.reaction:R02282"): ("no", "substrate", R, "Ornithine acetyltransferase (argJ) acetyl transfer; arginine biosynthesis; N kept."),
    ("Glu", "kegg.reaction:R02283"): BIO_TA,
    ("Glu", "kegg.reaction:R07613"): BIO_TA,
    ("Glu", "kegg.reaction:R02783"): ("no", "substrate (incorporated)", R, "MurD: D-Glu incorporated into peptidoglycan; D-form."),
    ("Glu", "kegg.reaction:R05578"): TRNA,
    # ---- Gly
    ("Gly", "kegg.reaction:R00497"): INCORP,
    ("Gly", "kegg.reaction:R10994"): INCORP,
    ("Gly", "kegg.reaction:R00899"): PROD,
    ("Gly", "kegg.reaction:R04951"): PROD,
    ("Gly", "kegg.reaction:R03654"): TRNA,
    ("Gly", "kegg.reaction:R04144"): INCORP,
    ("Gly", "kegg.reaction:R08701"): INCORP,
    # ---- His
    ("His", "kegg.reaction:R01158"): PROD,
    ("His", "kegg.reaction:R01163"): PROD,
    ("His", "kegg.reaction:R01167"): ("no (N kept in histamine)", "substrate", R,
        "Histidine decarboxylation keeps N in histamine. No histamine N-freeing step is catalogued in KEGG modules "
        "[interpretation]. MED4 gene PMM0917 carries two KOs (K01590 hdc, K13745 L-2,4-diaminobutyrate "
        "decarboxylase) with a generic 'PLP-dependent decarboxylase' product. Consistency note: the analogous "
        "Lys route (cadA -> cadaverine -> patA) IS catalogued because KEGG M00956 defines it."),
    ("His", "kegg.reaction:R03655"): TRNA,
    # ---- Ile / Leu / Val
    ("Ile", "kegg.reaction:R03656"): TRNA,
    ("Leu", "kegg.reaction:R03657"): TRNA,
    ("Val", "kegg.reaction:R03665"): TRNA,
    # ---- Lys
    ("Lys", "kegg.reaction:R00451"): PROD,
    ("Lys", "kegg.reaction:R03658"): TRNA,
    ("Lys", "kegg.reaction:R09597"): INCORP,
    # ---- Met
    **{("Met", f"kegg.reaction:{r}"): PROD for r in ["R00946", "R01078", "R03472", "R07767", "R10652"]},
    ("Met", "kegg.reaction:R03659"): TRNA,
    # ---- Phe / Tyr / Trp
    ("Phe", "kegg.reaction:R00691"): PROD,
    ("Phe", "kegg.reaction:R03660"): TRNA,
    ("Tyr", "kegg.reaction:R00733"): PROD,
    ("Tyr", "kegg.reaction:R02918"): TRNA,
    ("Trp", "kegg.reaction:R00674"): PROD,
    ("Trp", "kegg.reaction:R02722"): PROD,
    ("Trp", "kegg.reaction:R03664"): TRNA,
    # ---- Pro
    ("Pro", "kegg.reaction:R00135"): PROD,
    ("Pro", "kegg.reaction:R01248"): ("no", "substrate as written; product physiologically", R,
        "Pyrroline-5-carboxylate reductase (proC, EC 1.5.1.2) is the last step of proline biosynthesis, written by KEGG "
        "in the Pro-oxidizing direction; even read that way, Pro -> P5C frees no N."),
    ("Pro", "kegg.reaction:R01251"): ("no", "substrate as written; product physiologically", R,
        "As R01248 (NADP+ form)."),
    ("Pro", "kegg.reaction:R03661"): TRNA,
    # ---- Ser
    ("Ser", "kegg.reaction:R00582"): PROD,
    ("Ser", "kegg.reaction:R00586"): ("no", "substrate", R, "Serine O-acetyltransferase (cysE): cysteine biosynthesis; N kept."),
    ("Ser", "kegg.reaction:R00674"): INCORP,
    ("Ser", "kegg.reaction:R02722"): INCORP,
    ("Ser", "kegg.reaction:R03662"): TRNA,
    ("Ser", "kegg.reaction:R08218"): TRNA,
    # ---- Thr
    ("Thr", "kegg.reaction:R01466"): PROD,
    ("Thr", "kegg.reaction:R03663"): TRNA,
    ("Thr", "kegg.reaction:R10463"): INCORP,
    # ---- rows newly uncovered by the per-amino-acid coverage rule (critic Blocker 2) ----
    ("Ala", "kegg.reaction:R00585"): PROD,
    ("Ala", "kegg.reaction:R03210"): ("no", "substrate (incorporated)", R,
        "8-amino-7-oxononanoate synthase (biotin): Ala incorporated, N kept. Gene PMM1468 carries K00639 (kbl) and "
        "K00652 (bioF); product bioF - KO/product mismatch for K00639 (flagged in med4_flagged_hits)."),
    ("Ala", "kegg.reaction:R10124"): ("no", "substrate (incorporated)", R, "As R03210 (ACP form); PMM1468 bioF."),
    ("Arg", "kegg.reaction:R02923"): BROAD_D,
    ("Pro", "kegg.reaction:R02894"): BROAD_D,
    ("Gly", "kegg.reaction:R00366"): ("yes (NH3)", "substrate", R,
        "Glycine deamination by PMM1703, whose KO is K00273 (D-amino-acid oxidase, broad table, never credited). "
        "The catalogued glycine oxidase step (Gly_oxidase, thiO K03153) is a different gene (PMM0047)."),
    ("Asp", "kegg.reaction:R00485"): PROD,
    ("Cys", "kegg.reaction:R00896"): ("yes (transamination)", "substrate", R,
        "Cysteine transamination to 3-mercaptopyruvate by aspartate aminotransferase (PMM0674, K00812). Listed under "
        "known omissions; if added it would be an all-shared route (aspartate aminotransferase is shared), like Cys_CDO.2. "
        "Researcher call."),
    ("Cys", "kegg.reaction:R01001"): PROD,
    ("Gln", "kegg.reaction:R00253"): PROD,
    ("Glu", "kegg.reaction:R00253"): ("no", "substrate", R, "Glutamine synthetase: Glu N kept in Gln (central N assimilation)."),
    ("Glu", "kegg.reaction:R00021"): ("no", "substrate as written; product physiologically", R,
        "Fd-GOGAT written in reverse; physiologically it forms Glu (Gln_GOGAT, shared)."),
    ("Glu", "kegg.reaction:R10086"): ("yes (NH3, as written)", "substrate", R,
        "KEGG links a Glu-deaminating (GDH-type) half-reaction to Fd-GOGAT PMM1512 (K00284). GOGAT is shared central N "
        "assimilation; a GDH-type step is shared by researcher decision 1. Not added."),
    **{("Glu", f"kegg.reaction:{r}"): GLU_AT_PROD for r in
       ["R00355", "R00372", "R00694", "R00734", "R00896", "R01090", "R01214", "R02199", "R02433", "R02619",
        "R03243", "R05052", "R10991"]},
    ("Gly", "kegg.reaction:R00371"): ("no", "substrate as written; product physiologically", R,
        "kbl written in reverse (glycine + acetyl-CoA); physiologically it forms glycine (Thr_TDH_kbl.2). Gene PMM1468 is bioF "
        "(flagged KO/product mismatch)."),
    ("Gly", "kegg.reaction:R00588"): PROD,
    ("Gly", "kegg.reaction:R00945"): ("no (N moves to Ser)", "substrate as written", R,
        "SHMT glycine -> serine direction; N kept (moves into serine). SHMT is shared (Ser_SHMT_GCS.1)."),
    ("Gly", "kegg.reaction:R09099"): PROD,
    ("Ser", "kegg.reaction:R00220"): ("yes (NH3)", "substrate", R,
        "Serine deamination by ilvA (PMM0908, K01754): side activity of the Ile-biosynthesis threonine dehydratase, "
        "listed in the broad table and never credited for Ser (Ser_dehydratase credits K01752 only)."),
    ("Ser", "kegg.reaction:R09099"): ("no (N moves to Gly)", "substrate", R,
        "SHMT, tetrahydromethanopterin form of R00945; same enzyme as Ser_SHMT_GCS.1 (shared)."),
}


def side_of(name: str, eq: str) -> str:
    if "<=>" not in eq:
        return "no equation"
    lhs, rhs = eq.split("<=>", 1)
    norm = lambda s: {re.sub(r"^\d+\s+|^n\s+", "", t.strip()).lower() for t in s.split(" + ")}
    n = name.lower()
    l, r = n in norm(lhs), n in norm(rhs)
    return "both" if (l and r) else "left" if l else "right" if r else "not matched by name"


def main():
    ids = pd.read_csv(IDS, encoding="utf-8")
    ids = ids[~ids.amino_acid.str.startswith("class:")]
    assert len(ids) == 20
    ids.to_csv(DATA / "aa_metabolite_ids.csv", index=False, encoding="utf-8")

    rows, calls = [], []
    for _, r in ids.iterrows():
        res = genes_by_metabolite(metabolite_ids=r.metabolite_ids.split(";"), organism=ORG,
                                  evidence_sources=["metabolism"], include_stereo_forms=True, limit=None)
        assert res["returned"] == res["total_matching"], r.amino_acid
        calls.append(dict(amino_acid=r.amino_acid, total_matching=res["total_matching"],
                          returned=res["returned"],
                          not_found=";".join(f"{k}={v}" for k, v in (res.get("not_found") or {}).items() if v),
                          stereo_forms_added=";".join(map(str, res.get("stereo_forms_added") or []))))
        for x in res["results"]:
            rn = x.get("reaction_name") or ""
            eq = rn.split("; ")[-1] if "<=>" in rn else ""
            rows.append(dict(amino_acid=r.amino_acid, locus_tag=x["locus_tag"], gene_name=x.get("gene_name"),
                             product=x.get("product"), reaction_id=x.get("reaction_id"), reaction_name=rn,
                             equation=eq, ec_numbers=";".join(x.get("ec_numbers") or []),
                             metabolite_id=x.get("metabolite_id"), metabolite_name=x.get("metabolite_name"),
                             via_stereo_form_of=x.get("via_stereo_form_of")))
    calls = pd.DataFrame(calls)
    print(calls.to_string())
    df = pd.DataFrame(rows)
    df["aa_side"] = [side_of(n or "", e) for n, e in zip(df.metabolite_name, df.equation)]
    df["is_D_form"] = df.metabolite_name.fillna("").str.startswith("D-")

    # MED4 gene KOs
    lts = sorted(df.locus_tag.unique())
    g = gene_ontology_terms(locus_tags=lts, organism=ORG, ontology="kegg", limit=None)
    print("gene_ontology_terms total_matching:", g["total_matching"], "returned:", g["returned"],
          "not_found:", g.get("not_found"), "no_terms:", len(g.get("no_terms") or []))
    assert g["returned"] == g["total_matching"]
    gk = {}
    for x in g["results"]:
        if x["term_id"].startswith("kegg.orthology:"):
            gk.setdefault(x["locus_tag"], set()).add(x["term_id"].split(":", 1)[1])
    df["gene_kos"] = df.locus_tag.map(lambda t: ";".join(sorted(gk.get(t, []))))

    # coverage
    steps = pd.read_csv(DATA / "pathway_catalogue_steps.csv", encoding="utf-8")
    broad = pd.read_csv(DATA / "broad_enzymes.csv", encoding="utf-8")
    ctrl = pd.read_csv(DATA / "proposed_controls.csv", encoding="utf-8")
    ko_where, ec_where = {}, {}
    for _, s in steps.iterrows():
        for k in s.kos.split(";"):
            ko_where.setdefault(k, set()).add(s.step_id)
        for e in str(s.ec).split(";"):
            ec_where.setdefault(e.strip(), set()).add(s.step_id)
    for _, b in broad.iterrows():
        ko_where.setdefault(b.ko, set()).add(f"broad:{b.label}")
        ec_where.setdefault(b.ec, set()).add(f"broad:{b.label}")
    for _, c in ctrl.iterrows():
        for k in c.kos.split(";"):
            ko_where.setdefault(k, set()).add(c.control_id)
        ec_where.setdefault(c.ec, set()).add(c.control_id)

    # COVERED (critic Blocker 2): the row's gene carries a KO of a step of THAT amino acid's own pathways
    # whose KEGG reaction list (step_reactions.csv) contains THIS reaction. A gene KO found only in another
    # amino acid's step, the broad table or the controls is NOT coverage; it is recorded as information.
    srn = pd.read_csv(DATA / "step_reactions.csv", encoding="utf-8").set_index("step_id").kegg_rn.fillna("")
    own = {}
    for _, s in steps.iterrows():
        rns = {f"kegg.reaction:{x}" for x in srn.get(s.step_id, "").split(";") if x}
        own.setdefault(s.amino_acid, []).append((s.step_id, set(s.kos.split(";")), rns))

    def cov_own(r):
        gk = set(r.gene_kos.split(";"))
        return " | ".join(sid for sid, ks, rns in own.get(r.amino_acid, []) if gk & ks and r.reaction_id in rns)

    def cov_info(r):
        return " | ".join(sorted({f"KO {k}: {w}" for k in r.gene_kos.split(";") for w in ko_where.get(k, [])}))

    def cov_ec(r):
        return " | ".join(sorted({f"EC {e}: {w}" for e in r.ec_numbers.split(";") for w in ec_where.get(e, [])}))
    df["catalogue_coverage"] = df.apply(cov_own, axis=1)
    df["ko_elsewhere_info"] = df.apply(cov_info, axis=1)
    df["ec_match_only_info"] = df.apply(cov_ec, axis=1)
    df["covered"] = df.catalogue_coverage != ""
    df.to_csv(DATA / "crosscheck_all_reactions_med4.csv", index=False, encoding="utf-8")
    print("rows:", len(df), "| distinct reactions:", df.reaction_id.nunique(),
          "| covered rows (gene KO in this aa's own step for this reaction):", int(df.covered.sum()),
          "| uncovered rows whose gene KO is elsewhere in catalogue/broad/controls:",
          int((~df.covered & (df.ko_elsewhere_info != "")).sum()))

    # candidates = uncovered reaction x amino acid
    unc = df[~df.covered]
    agg = (unc.groupby(["amino_acid", "reaction_id"], dropna=False)
           .agg(equation=("equation", "first"), reaction_name=("reaction_name", "first"),
                ec_numbers=("ec_numbers", "first"), metabolite_name=("metabolite_name", lambda s: ";".join(sorted(set(s)))),
                aa_side=("aa_side", lambda s: ";".join(sorted(set(s)))),
                is_D_form=("is_D_form", "any"),
                locus_tags=("locus_tag", lambda s: ";".join(sorted(set(s)))),
                gene_names=("gene_name", lambda s: ";".join(sorted(set(map(str, s))))),
                products=("product", lambda s: " | ".join(sorted(set(map(str, s))))),
                gene_kos=("gene_kos", lambda s: ";".join(sorted({k for v in s for k in v.split(';') if k}))),
                ko_elsewhere_info=("ko_elsewhere_info", lambda s: " | ".join(sorted(set(x for x in s if x)))),
                ec_match_only_info=("ec_match_only_info", lambda s: " | ".join(sorted(set(x for x in s if x)))))
           .reset_index())
    dec = agg.apply(lambda r: DECISIONS.get((r.amino_acid, r.reaction_id), ("", "", "UNDECIDED", "")), axis=1)
    agg["removes_N_from_aa"] = [d[0] for d in dec]
    agg["aa_role"] = [d[1] for d in dec]
    agg["proposal"] = [d[2] for d in dec]
    agg["reason"] = [d[3] for d in dec]
    agg.to_csv(DATA / "crosscheck_candidates_med4.csv", index=False, encoding="utf-8")
    print("candidate reaction x aa rows:", len(agg), "| undecided:", int((agg.proposal == "UNDECIDED").sum()))
    print(agg.proposal.value_counts().to_dict())


if __name__ == "__main__":
    main()
