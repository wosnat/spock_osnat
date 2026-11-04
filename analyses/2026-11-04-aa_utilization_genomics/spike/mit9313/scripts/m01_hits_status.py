"""THROWAWAY pilot: Prochlorococcus MIT9313 on the DRAFT catalogue, scored with the unchanged a01 logic.

Imports units / get_hits / pathway_status / aa_status / step_present from
spike/alteromonas_hot1a3/scripts/a01_hits_status.py and only swaps the organism + output folder.
MED4 and HOT1A3 statuses are read from spike/alteromonas_hot1a3/data (no re-query).
Strains queried: Prochlorococcus MIT9313 only (researcher unblinded it, 2026-11-04).
KG calls: genes_by_ontology(kegg, organism='Prochlorococcus MIT9313', 131 KOs, min_gene_set_size=0,
          max_gene_set_size=None, limit=None); list_organisms(['Prochlorococcus MIT9313']).
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/spike/mit9313/scripts/m01_hits_status.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import list_organisms

HERE = Path(__file__).resolve().parents[1]
SPIKE = HERE.parent
ALT = SPIKE / "alteromonas_hot1a3"
spec = importlib.util.spec_from_file_location("a01", ALT / "scripts" / "a01_hits_status.py")
a01 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a01)
ORG = "Prochlorococcus MIT9313"
a01.ORG = ORG  # get_hits reads the module-level ORG
OUT = HERE / "data"
AAS = a01.AAS


def main():
    u, steps = a01.units()
    assess = pd.read_csv(a01.MDATA / "pathway_assessability.csv", encoding="utf-8")
    broad = pd.read_csv(a01.MDATA / "broad_enzymes.csv", encoding="utf-8")
    hits, log, _ = a01.get_hits(u, broad)
    cols = ["step_id", "amino_acid", "flag", "ko", "locus_tag", "gene_name", "product", "call", "credit_eligible",
            "exclusion_reason", "product_keywords", "ko_groups", "credits_multiple_aa", "evidence", "sources"]
    cols = [c for c in cols if c in hits.columns]
    hits[cols].to_csv(OUT / "hits.csv", index=False, encoding="utf-8")
    hits[hits.call.str.startswith("flagged")][cols].to_csv(OUT / "flagged_hits.csv", index=False, encoding="utf-8")
    hits[hits.amino_acid == "control"][cols].to_csv(OUT / "controls.csv", index=False, encoding="utf-8")
    print("hits rows:", len(hits), "| genes:", hits.locus_tag.nunique(), hits.call.value_counts().to_dict())

    ps = a01.pathway_status(steps, assess, hits[hits.amino_acid.isin(AAS)], ORG)
    ps.to_csv(OUT / "pathway_status.csv", index=False, encoding="utf-8")
    aa = a01.aa_status(ps, ORG)
    aa.to_csv(OUT / "aa_status.csv", index=False, encoding="utf-8")

    aa_m = pd.read_csv(ALT / "data" / "aa_status_med4.csv", encoding="utf-8")
    aa_a = pd.read_csv(ALT / "data" / "aa_status.csv", encoding="utf-8")
    keep = ["amino_acid", "cell_status", "cell_k_of_n", "cell_pathway", "complete_pathways",
            "all_shared_route_fully_present", "dedicated_locus_tags", "n_not_assessable"]
    three = aa_m[keep].rename(columns={c: f"{c}_med4" for c in keep if c != "amino_acid"})
    three = three.merge(aa[keep].rename(columns={c: f"{c}_mit9313" for c in keep if c != "amino_acid"}),
                        on="amino_acid")
    three = three.merge(aa_a[keep].rename(columns={c: f"{c}_hot1a3" for c in keep if c != "amino_acid"}),
                        on="amino_acid")
    three.insert(1, "n_pathways", aa.n_pathways)
    three.to_csv(OUT / "aa_status_med4_vs_mit9313_vs_hot1a3.csv", index=False, encoding="utf-8")

    ded = steps[steps.flag == "dedicated"]
    cred = hits[hits.call == "credited"]
    found = [sid for sid, g in ded.groupby("step_id")
             if a01.step_present(g.ko_groups.iloc[0], set(cred[cred.step_id == sid].ko))]
    r = list_organisms(organism_names=[ORG])
    log2 = {"tool": "list_organisms", "organism_names": [ORG], "total_matching": r["total_matching"],
            "returned": r["returned"]}
    print(json.dumps(log2))
    alt_s = json.loads((ALT / "data" / "summary.json").read_text(encoding="utf-8"))
    summ = {"MIT9313": {"dedicated_steps_catalogued": int(ded.step_id.nunique()),
                        "dedicated_steps_found": len(found), "dedicated_steps_found_ids": found,
                        "complete_pathways": ps[ps.status == "complete"].pathway_id.tolist()},
            "MED4": alt_s["MED4"], "HOT1A3": alt_s["HOT1A3"],
            "gene_counts": {"MIT9313": [(x["organism_name"], x["gene_count"], x.get("clade")) for x in r["results"]],
                            "MED4": alt_s["gene_counts"]["MED4"],
                            "HOT1A3": alt_s["gene_counts"]["Alteromonas macleodii HOT1A3"]},
            "kg_calls": [log, log2]}
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    pd.set_option("display.width", 300)
    pd.set_option("display.max_colwidth", 70)
    print(json.dumps(summ["MIT9313"], indent=1))
    print(three[["amino_acid", "cell_status_med4", "cell_status_mit9313", "cell_k_of_n_mit9313",
                 "cell_pathway_mit9313", "dedicated_locus_tags_mit9313", "cell_status_hot1a3"]].to_string(index=False))
    print(hits[["step_id", "flag", "ko", "locus_tag", "gene_name", "product", "call"]].to_string(index=False))


if __name__ == "__main__":
    main()
