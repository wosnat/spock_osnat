"""Methods step 4 - product-agreement rule on MED4 KO hits (MED4 ONLY).

Rule (proposal section 3 step 2, made operational on critic review): a gene counts for a step only if
its KG `product` contains one of the step's `product_keywords` (case-insensitive substring).
Otherwise the hit is "flagged: KO/product mismatch" and does not count until the researcher reviews it.

Exclusion rule (enforced here, defined in 01): on a DEDICATED step, a hit on a KO that sits on any shared
step, any positive control or the broad table is a "shared-enzyme hit" and is never credited.
Dedicated steps carry substrate-naming keywords only, so a class-generic product ("... family protein")
without the substrate is flagged.
Calls: credited | flagged: KO/product mismatch | shared-enzyme hit (not credited).

This lists MED4 hits per catalogue step and per control; it does NOT compute pathway status (that is
the next methods step, scoring).

KG call: genes_by_ontology(ontology='kegg', organism='MED4', term_ids=<all catalogue + control KOs>,
         min_gene_set_size=0, max_gene_set_size=None, limit=None)
Outputs: med4_step_hits.csv (one row per step x gene x KO), med4_flagged_hits.csv (mismatches only)
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/methods/scripts/04_product_agreement_med4.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from multiomics_explorer import genes_by_ontology

MDIR = Path(__file__).resolve().parents[1]
DATA = MDIR / "data"
ORG = "MED4"


def agrees(product: str, kws: str) -> bool:
    p = (product or "").lower()
    return any(k.lower() in p for k in kws.split("|") if k)


def main():
    long = pd.read_csv(DATA / "pathway_catalogue.csv", encoding="utf-8")
    steps = pd.read_csv(DATA / "pathway_catalogue_steps.csv", encoding="utf-8")
    ctrl = pd.read_csv(DATA / "proposed_controls.csv", encoding="utf-8")
    kw = steps.drop_duplicates("step_id").set_index("step_id").product_keywords
    units = [(r.step_id, r.amino_acid, r.step_key, r.ko, r.ko_groups, kw[r.step_id], r.flag, bool(r.credit_eligible),
              r.exclusion_reason if isinstance(r.exclusion_reason, str) else "", r.credits_multiple_aa
              if isinstance(r.credits_multiple_aa, str) else "") for _, r in long.iterrows()]
    for _, c in ctrl.iterrows():
        for k in c.kos.split(";"):
            units.append((c.control_id, "control", c.control_id, k, c.kos.replace(";", "|"), c.product_keywords,
                          c.control_type, True, "", ""))
    u = pd.DataFrame(units, columns=["step_id", "amino_acid", "step_key", "ko", "ko_groups", "product_keywords", "flag",
                                     "credit_eligible", "exclusion_reason", "credits_multiple_aa"])
    kos = sorted(set(u.ko))
    g = genes_by_ontology(ontology="kegg", organism=ORG, term_ids=[f"kegg.orthology:{k}" for k in kos],
                          min_gene_set_size=0, max_gene_set_size=None, limit=None)
    print("genes_by_ontology total_matching:", g["total_matching"], "returned:", g["returned"],
          "truncated:", g.get("truncated"))
    assert g["returned"] == g["total_matching"]
    gdf = pd.DataFrame(g["results"])
    gdf["ko"] = gdf.term_id.str.replace("kegg.orthology:", "", regex=False)
    keep = [c for c in ["ko", "locus_tag", "gene_name", "product", "evidence", "sources"] if c in gdf.columns]
    hits = u.merge(gdf[keep], on="ko", how="inner")
    hits["product_agrees"] = [agrees(p, k) for p, k in zip(hits["product"], hits.product_keywords)]
    hits["generic_product"] = hits["product"].fillna("").str.lower().str.contains("family protein|hypothetical|uncharacterized")
    hits["call"] = [("shared-enzyme hit (not credited)" if not ok else
                     "credited" if agree else "flagged: KO/product mismatch")
                    for ok, agree in zip(hits.credit_eligible, hits.product_agrees)]
    hits = hits.sort_values(["amino_acid", "step_id", "locus_tag"])
    hits.to_csv(DATA / "med4_step_hits.csv", index=False, encoding="utf-8")
    fl = hits[hits.call != "credited"]
    fl.to_csv(DATA / "med4_flagged_hits.csv", index=False, encoding="utf-8")
    print(hits.call.value_counts().to_dict())
    print("hit rows:", len(hits), "| distinct MED4 genes:", hits.locus_tag.nunique(), "| flagged rows:", len(fl),
          "| flagged genes:", fl.locus_tag.nunique())
    pd.set_option("display.width", 250)
    print(hits[["step_id", "flag", "ko", "locus_tag", "gene_name", "product", "call"]].to_string(index=False))


if __name__ == "__main__":
    main()
