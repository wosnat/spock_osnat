"""Spike: MED4 amino-acid N-removing enzymes.
Catalogue (KO, EC, mode, shared) is drafted from standard biochemistry = [interpretation];
KG checks: KO present in KG (name returned), MED4 genes annotated to each KO.
Run: uv run python analyses/2026-11-04-aa_utilization_genomics/spike/scripts/s05_n_release.py
"""
from pathlib import Path
import pandas as pd
from multiomics_explorer import ontology_term_details, genes_by_ontology, genes_by_metabolite

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
NH4, TR, OTH = "release_NH4", "transfer_transamination", "other_N_route"
# (amino_acid, KO, label, EC, mode, shared_with_biosynthesis_or_central [interpretation], note)
CAT = [
    ("Ala", "K00259", "ald", "1.4.1.1", NH4, "no", "alanine dehydrogenase"),
    ("Ala", "K00285", "dadA", "1.4.5.1", NH4, "no", "D-amino acid dehydrogenase (broad; D-Ala)"),
    ("Ala", "K14260", "alaA/alaC", "2.6.1.2", TR, "yes", "alanine aminotransferase"),
    ("Ala", "K00814", "GPT", "2.6.1.2", TR, "yes", "alanine aminotransferase"),
    ("Ala", "K00835", "avtA", "2.6.1.66", TR, "yes", "alanine-valine aminotransferase"),
    ("Arg", "K01476", "rocF", "3.5.3.1", NH4, "no", "arginase: urea + ornithine; NH4 via urease"),
    ("Arg", "K01478", "arcA", "3.5.3.6", NH4, "no", "arginine deiminase: citrulline + NH4"),
    ("Arg", "K00611", "argF/arcB", "2.1.3.3", OTH, "yes", "ornithine carbamoyltransferase (ADI step 2; also Arg biosynthesis)"),
    ("Arg", "K00926", "arcC", "2.7.2.2", NH4, "no", "carbamate kinase (ADI pathway; carbamoyl-P to NH4 + CO2)"),
    ("Arg", "K01585", "speA", "4.1.1.19", OTH, "yes", "arginine decarboxylase: agmatine (polyamines)"),
    ("Arg", "K01480", "speB", "3.5.3.11", NH4, "yes", "agmatinase: urea + putrescine; NH4 via urease"),
    ("Arg", "K12252", "aruH", "2.6.1.84", TR, "no", "arginine:pyruvate transaminase"),
    ("Arg", "K00819", "rocD", "2.6.1.13", TR, "no", "ornithine aminotransferase (ornithine from arginase)"),
    ("Arg", "K01428", "ureC", "3.5.1.5", NH4, "no", "urease alpha (urea from arginase/agmatinase)"),
    ("Arg", "K01429", "ureB", "3.5.1.5", NH4, "no", "urease beta"),
    ("Arg", "K01430", "ureA", "3.5.1.5", NH4, "no", "urease gamma"),
    ("Asn", "K01424", "ansA", "3.5.1.1", NH4, "no", "L-asparaginase"),
    ("Asn", "K13051", "iaaA/ansB", "3.5.1.1;3.4.19.5", NH4, "no", "isoaspartyl peptidase/L-asparaginase"),
    ("Asp", "K01744", "aspA", "4.3.1.1", NH4, "no", "aspartate ammonia-lyase"),
    ("Asp", "K00278", "nadB", "1.4.3.16", NH4, "yes", "L-aspartate oxidase (NAD biosynthesis)"),
    ("Asp", "K00812", "aspB", "2.6.1.1", TR, "yes", "aspartate aminotransferase"),
    ("Asp", "K00813", "aspC", "2.6.1.1", TR, "yes", "aspartate aminotransferase"),
    ("Asp", "K11358", "yhdR", "2.6.1.1", TR, "yes", "aspartate aminotransferase"),
    ("Asp", "K14454", "GOT1", "2.6.1.1", TR, "yes", "aspartate aminotransferase, cytoplasmic"),
    ("Asp", "K14455", "GOT2", "2.6.1.1", TR, "yes", "aspartate aminotransferase, mitochondrial"),
    ("Cys", "K01760", "metC", "4.4.1.13", NH4, "yes", "cystathionine beta-lyase / cysteine-S-conjugate beta-lyase (Met biosynthesis)"),
    ("Cys", "K05396", "dcyD", "4.4.1.15", NH4, "no", "D-cysteine desulfhydrase"),
    ("Cys", "K17217", "mccB", "4.4.1.1", NH4, "no", "cystathionine gamma-lyase"),
    ("Cys", "K01738", "cysK", "2.5.1.47", OTH, "yes", "cysteine synthase (side desulfhydrase activity in some isoforms)"),
    ("Glu", "K00261", "GLUD1_2", "1.4.1.3", NH4, "yes", "glutamate dehydrogenase NAD(P)+"),
    ("Glu", "K00262", "gdhA", "1.4.1.4", NH4, "yes", "glutamate dehydrogenase NADP+"),
    ("Glu", "K15371", "GDH2", "1.4.1.2", NH4, "yes", "glutamate dehydrogenase NAD+"),
    ("Glu", "K01580", "gadB", "4.1.1.15", OTH, "no", "glutamate decarboxylase: GABA (N retained)"),
    ("Gln", "K01425", "glsA", "3.5.1.2", NH4, "no", "glutaminase"),
    ("Gln", "K00265", "gltB", "1.4.1.13", TR, "yes", "GOGAT large subunit NADPH (amide N to 2-OG)"),
    ("Gln", "K00266", "gltD", "1.4.1.13", TR, "yes", "GOGAT small subunit"),
    ("Gln", "K00284", "GLU/glsF", "1.4.7.1", TR, "yes", "ferredoxin-dependent GOGAT (amide N to 2-OG)"),
    ("Gly", "K00281", "gcvP", "1.4.4.2", NH4, "yes", "glycine cleavage P protein (also C1 metabolism)"),
    ("Gly", "K00605", "gcvT", "2.1.2.10", NH4, "yes", "glycine cleavage T protein (releases NH4)"),
    ("Gly", "K02437", "gcvH", "-", NH4, "yes", "glycine cleavage H protein"),
    ("Gly", "K03153", "thiO", "1.4.3.19", NH4, "yes", "glycine oxidase (thiamine biosynthesis)"),
    ("Gly", "K00830", "AGXT", "2.6.1.44;2.6.1.51", TR, "yes", "alanine-glyoxylate / serine-pyruvate aminotransferase"),
    ("His", "K01745", "hutH", "4.3.1.3", NH4, "no", "histidine ammonia-lyase"),
    ("His", "K01712", "hutU", "4.2.1.49", OTH, "no", "urocanate hydratase"),
    ("His", "K01468", "hutI", "3.5.2.7", OTH, "no", "imidazolonepropionase"),
    ("His", "K01479", "hutG", "3.5.3.8", NH4, "no", "formimidoylglutamase"),
    ("His", "K00817", "hisC", "2.6.1.9", TR, "yes", "histidinol-phosphate aminotransferase (His biosynthesis; broad)"),
    ("Ile;Leu;Val", "K00826", "ilvE", "2.6.1.42", TR, "yes", "branched-chain aminotransferase"),
    ("Ile;Leu;Val", "K00263", "ldh", "1.4.1.9", NH4, "no", "leucine dehydrogenase"),
    ("Lys", "K03918", "lat", "2.6.1.36", TR, "no", "lysine 6-aminotransferase"),
    ("Lys", "K01582", "cadA", "4.1.1.18", OTH, "no", "lysine decarboxylase: cadaverine (N retained)"),
    ("Met", "K01761", "mdeA", "4.4.1.11", NH4, "no", "methionine gamma-lyase"),
    ("Phe;Tyr", "K00832", "tyrB", "2.6.1.57", TR, "yes", "aromatic-amino-acid aminotransferase"),
    ("Phe;Tyr", "K00838", "ARO8", "2.6.1.57", TR, "yes", "aromatic aminotransferase I"),
    ("Phe", "K10775", "PAL", "4.3.1.24", NH4, "no", "phenylalanine ammonia-lyase"),
    ("Phe;Tyr", "K13064", "PTAL", "4.3.1.25", NH4, "no", "phenylalanine/tyrosine ammonia-lyase"),
    ("Phe", "K00270", "pdh", "1.4.1.20", NH4, "no", "phenylalanine dehydrogenase"),
    ("Tyr", "K00815", "TAT", "2.6.1.5", TR, "no", "tyrosine aminotransferase"),
    ("Pro", "K00318", "PRODH", "1.5.5.2", OTH, "no", "proline dehydrogenase: P5C (N ends in Glu)"),
    ("Pro", "K13821", "putA", "1.5.5.2;1.2.1.88", OTH, "no", "bifunctional PutA (Pro to Glu)"),
    ("Pro", "K00294", "rocA", "1.2.1.88", OTH, "no", "P5C dehydrogenase (to Glu)"),
    ("Ser", "K01752", "sdaA", "4.3.1.17", NH4, "no", "L-serine dehydratase"),
    ("Ser", "K01753", "dsdA", "4.3.1.18", NH4, "no", "D-serine dehydratase"),
    ("Ser;Thr", "K01754", "ilvA", "4.3.1.19", NH4, "yes", "threonine dehydratase (Ile biosynthesis; also Ser)"),
    ("Ser;Thr", "K17989", "SDS", "4.3.1.17;4.3.1.19", NH4, "no", "serine/threonine dehydratase"),
    ("Thr", "K01620", "ltaE", "4.1.2.48", OTH, "no", "threonine aldolase: Gly (N ends in Gly)"),
    ("Thr", "K00060", "tdh", "1.1.1.103", OTH, "no", "threonine 3-dehydrogenase (to Gly via kbl)"),
    ("Thr", "K00639", "kbl", "2.3.1.29", OTH, "no", "2-amino-3-ketobutyrate CoA ligase"),
    ("Trp", "K01667", "tnaA", "4.1.99.1", NH4, "no", "tryptophanase"),
    ("ALL", "K03334", "LAAO", "1.4.3.2", NH4, "no", "L-amino-acid oxidase (broad)"),
    ("ALL", "K00273", "DAO", "1.4.3.3", NH4, "no", "D-amino-acid oxidase (broad)"),
    ("ALL", "K14267", "dapC", "2.6.1.17", TR, "yes", "N-succinyldiaminopimelate aminotransferase (class I AT, broad)"),
    ("ALL", "K10907", "K10907", "2.6.1.-", TR, "yes", "aminotransferase (unspecified)"),
    ("ALL", "K00837", "ALD1", "2.6.1.-", TR, "yes", "aminotransferase"),
    ("REF", "K01915", "glnA", "6.3.1.2", "NH4_assimilation", "yes", "validation probe: glutamine synthetase"),
]


def main():
    cat = pd.DataFrame(CAT, columns=["amino_acid", "ko", "label", "ec", "mode", "shared_interpretation", "note"])
    kos = sorted(set("kegg.orthology:" + cat.ko))

    det = ontology_term_details(term_ids=kos, limit=None)
    print("ontology_term_details envelope:", {k: v for k, v in det.items() if k != "results"})
    found = {}
    for x in det["results"]:
        found[x.get("term_id") or x.get("id")] = x.get("name") or x.get("term_name")
    print("KO in KG:", len(found), "of", len(kos))
    cat["ko_in_kg"] = ("kegg.orthology:" + cat.ko).map(lambda k: k in found)
    cat["kg_ko_name"] = ("kegg.orthology:" + cat.ko).map(found)
    cat.to_csv(DATA / "med4_n_release_catalogue.csv", index=False, encoding="utf-8")

    g = genes_by_ontology(ontology="kegg", organism="MED4", term_ids=kos, min_gene_set_size=0,
                          max_gene_set_size=None, limit=None)
    assert g["returned"] == g["total_matching"]
    print("genes_by_ontology total_matching:", g["total_matching"], "returned:", g["returned"],
          "not_found:", g.get("not_found"))
    gdf = pd.DataFrame(g["results"])
    gdf["ko"] = gdf.term_id.str.replace("kegg.orthology:", "", regex=False)
    m = cat.merge(gdf[["ko", "locus_tag", "gene_name", "product"]], on="ko", how="left")
    m["med4_gene_found"] = m.locus_tag.notna()
    m.to_csv(DATA / "med4_aa_n_release.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 250)
    print(m[["amino_acid", "ko", "label", "mode", "ko_in_kg", "locus_tag", "gene_name", "product"]].to_string())

    ids = pd.read_csv(DATA / "med4_aa_metabolite_ids.csv", encoding="utf-8")
    rows = []
    for _, r in ids[~ids.amino_acid.str.startswith("class:")].iterrows():
        res = genes_by_metabolite(metabolite_ids=r.metabolite_ids.split(";"), organism="MED4",
                                  evidence_sources=["metabolism"], include_stereo_forms=True, limit=None)
        assert res["returned"] == res["total_matching"]
        for x in res["results"]:
            rows.append({"amino_acid": r.amino_acid, "locus_tag": x["locus_tag"], "gene_name": x.get("gene_name"),
                         "product": x.get("product"), "reaction_id": x.get("reaction_id"),
                         "reaction_name": x.get("reaction_name"),
                         "ec_numbers": ";".join(x.get("ec_numbers") or []), "mass_balance": x.get("mass_balance"),
                         "metabolite_id": x.get("metabolite_id"), "metabolite_name": x.get("metabolite_name")})
        print(r.amino_acid, "metabolism total_matching", res["total_matching"])
    pd.DataFrame(rows).to_csv(DATA / "med4_aa_metabolism_crosscheck.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
