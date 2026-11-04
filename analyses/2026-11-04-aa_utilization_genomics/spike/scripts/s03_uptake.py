"""Spike: MED4 amino-acid uptake evidence, three lines kept separate.
Run: uv run python analyses/2026-11-04-aa_utilization_genomics/spike/scripts/s03_uptake.py
"""
import json
from pathlib import Path
import pandas as pd
from multiomics_explorer import genes_by_metabolite, genes_by_categorical_metric

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"; DATA.mkdir(exist_ok=True)
ORG = "MED4"
K = "kegg.compound:"
AA = {  # amino acid -> (ids, note)
 "Ala": ([K+"C01401", K+"C00041", K+"C00133"], "generic C01401 + L + D"),
 "Arg": ([K+"C00062", K+"C00792", K+"C02385"], "no generic 'Arginine' found; C02385 'Amino acid(Arg-)' added as the arginine-like entry"),
 "Asn": ([K+"C16438", K+"C00152"], "generic + L"),
 "Asp": ([K+"C16433", K+"C00049", K+"C00402"], "generic + L + D"),
 "Cys": ([K+"C00736", K+"C00097", K+"C00793"], "generic + L + D"),
 "Glu": ([K+"C00302", K+"C00025", K+"C00217"], "generic + L + D"),
 "Gln": ([K+"C00303", K+"C00064", K+"C00819"], "generic + L + D"),
 "Gly": ([K+"C00037"], "achiral"),
 "His": ([K+"C00768", K+"C00135"], "generic + L"),
 "Ile": (["chebi:24898", K+"C00407"], "generic is chebi:24898"),
 "Leu": ([K+"C16439", K+"C00123"], "generic + L"),
 "Lys": ([K+"C16440", K+"C00047", K+"C00739"], "generic + L + D"),
 "Met": ([K+"C01733", K+"C00073", K+"C00855"], "generic + L + D"),
 "Phe": ([K+"C02057", K+"C00079", K+"C02265"], "generic + L + D"),
 "Pro": ([K+"C16435", K+"C00148", K+"C00763"], "generic + L + D"),
 "Ser": ([K+"C00716", K+"C00065", K+"C00740"], "generic + L + D"),
 "Thr": ([K+"C00188"], "only L-Threonine found; no generic"),
 "Trp": ([K+"C00806", K+"C00078"], "generic + L"),
 "Tyr": ([K+"C01536", K+"C00082"], "generic + L"),
 "Val": ([K+"C16436", K+"C00183", K+"C06417"], "generic + L + D"),
}
CLASSES = {
 "class:amino_acid": [K+"C00045", "chebi:33709"],
 "class:L-amino_acid": [K+"C00151"],
 "class:D-amino_acid": [K+"C00405"],
 "class:branched-chain_aa": ["chebi:22918"],
 "class:polar_aa": ["chebi:26167"],
 "class:aromatic_aa": [K+"C01021"],
 "class:sulfur_aa": ["chebi:26834"],
}
KEEP = ["locus_tag","gene_name","product","evidence_source","tcdb_route","tcdb_family_id","tcdb_family_name",
        "tcdb_level_kind","tcdb_direction","tcdb_identity","tcdb_calls","tcdb_substrate_system_count",
        "metabolite_id","metabolite_name","via_stereo_form_of","go_term_id","go_term_name","go_namespace",
        "go_evidence","go_term_depth","go_axiom_term_id","go_axiom_term_name"]

rows, env = [], []
def run(target, ids, line, **kw):
    r = genes_by_metabolite(metabolite_ids=ids, organism=ORG, limit=None, **kw)
    assert r["returned"] == r["total_matching"], (target, line)
    env.append({"target": target, "line": line, "metabolite_ids": ";".join(ids),
                "total_matching": r["total_matching"], "returned": r["returned"],
                "not_found": json.dumps(r.get("not_found")), "not_matched": ";".join(r.get("not_matched") or []),
                "stereo_forms_added": json.dumps(r.get("stereo_forms_added")),
                "tcdb_family_substrates_not_shown": json.dumps(r.get("tcdb_family_substrates_not_shown")),
                "tcdb_family_substrates_skipped": json.dumps(r.get("tcdb_family_substrates_skipped")),
                "warnings": " | ".join(r.get("warnings") or [])})
    for x in r["results"]:
        d = {k: x.get(k) for k in KEEP}
        d["target"] = target; d["evidence_line"] = line
        if isinstance(d["tcdb_calls"], list): d["tcdb_calls"] = ";".join(d["tcdb_calls"])
        rows.append(d)

for tgt, ids in list({k: v[0] for k, v in AA.items()}.items()) + list(CLASSES.items()):
    run(tgt, ids, "tcdb_direct", evidence_sources=["transport"], include_stereo_forms=True)
    run(tgt, ids, "tcdb_family_walk", evidence_sources=["transport"], include_stereo_forms=True,
        include_tcdb_family_substrates=True)
    run(tgt, ids, "go_mf", evidence_sources=["go_transport"], include_stereo_forms=True,
        go_namespace=["molecular_function"], go_include_ancestors=True)

df = pd.DataFrame(rows)
# the family-walk run also returns direct rows; keep only family rows under that label
df = df[~((df.evidence_line == "tcdb_family_walk") & (df.tcdb_route != "family"))]
df.loc[df.evidence_line == "tcdb_family_walk", "evidence_line"] = "tcdb_family_candidate"

# SBP predictions
sbp = []
for mid in ["derived_metric:BST20200244:med4_sbp:sbp_predicted_substrate",
            "derived_metric:BST20200244:med4_sbp:sbp_nutrient_class"]:
    r = genes_by_categorical_metric(derived_metric_ids=[mid], organism=ORG, limit=None)
    assert r["returned"] == r["total_matching"]
    env.append({"target": "SBP", "line": mid, "total_matching": r["total_matching"], "returned": r["returned"]})
    for x in r["results"]:
        sbp.append({"locus_tag": x["locus_tag"], "gene_name": x.get("gene_name"), "product": x.get("product"),
                    "metric_type": mid.rsplit(":",1)[1], "value": x.get("value")})
sbpd = pd.DataFrame(sbp)
sbpd["metric_type"] = sbpd["metric_type"].fillna(sbpd.get("derived_metric_id", pd.Series(dtype=str)))
sbpw = (sbpd.fillna({"gene_name": "", "product": ""})
        .pivot_table(index=["locus_tag","gene_name","product"], columns="metric_type", values="value", aggfunc="first")
        .reset_index())
sbpw.to_csv(DATA/"med4_sbp_all.csv", index=False, encoding="utf-8")
AA_WORDS = {"amino_acids": "class:amino_acid", "glycine_betaine": None}
for _, s in sbpw.iterrows():
    sub = s.get("sbp_predicted_substrate")
    if sub == "amino_acids":
        rows_s = {"locus_tag": s.locus_tag, "gene_name": s.gene_name, "product": s["product"],
                  "evidence_line": "sbp", "target": "class:amino_acid",
                  "metabolite_name": f"SBP substrate={sub}; class={s.get('sbp_nutrient_class')}"}
        df = pd.concat([df, pd.DataFrame([rows_s])], ignore_index=True)

df = df[["target","evidence_line","locus_tag","gene_name","product"] + [c for c in KEEP if c not in ("locus_tag","gene_name","product")]]
df.to_csv(DATA/"med4_aa_uptake.csv", index=False, encoding="utf-8")
pd.DataFrame(env).to_csv(DATA/"med4_aa_uptake_envelopes.csv", index=False, encoding="utf-8")
pd.DataFrame([{"amino_acid": k, "metabolite_ids": ";".join(v[0]), "note": v[1]} for k, v in AA.items()]
             + [{"amino_acid": k, "metabolite_ids": ";".join(v), "note": "class-level"} for k, v in CLASSES.items()]
             ).to_csv(DATA/"med4_aa_metabolite_ids.csv", index=False, encoding="utf-8")
print(df.groupby(["evidence_line"]).size())
print(df.groupby(["target","evidence_line"]).locus_tag.apply(lambda s: ";".join(sorted(set(s)))).to_string())
print(sbpw.to_string())
