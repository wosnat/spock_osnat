"""THROWAWAY pilot: operon / neighbourhood check for every credited DEDICATED hit in Prochlorococcus MIT9313.

Same rule as spike/alteromonas_hot1a3/scripts/a02_neighbourhoods.py (is_transporter imported from it):
gene_neighbors(window=5, limit=None); neighbours within rank_offset +-3 on the same strand; transporter
(gene_category == 'Transport' or product regex) or a credited hit on another step of the same pathway -> "package",
else "lone gene". Positional adjacency only.
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/spike/mit9313/scripts/m02_neighbourhoods.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import gene_neighbors

HERE = Path(__file__).resolve().parents[1]
ALT = HERE.parent / "alteromonas_hot1a3"
spec = importlib.util.spec_from_file_location("a02", ALT / "scripts" / "a02_neighbourhoods.py")
a02 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a02)
OUT = HERE / "data"
ORGKEY = "MIT9313"


def main():
    steps = pd.read_csv(a02.MDATA / "pathway_catalogue_steps.csv", encoding="utf-8")
    sid2pid = steps.drop_duplicates("step_id").set_index("step_id").pathway_id.to_dict()
    h = pd.read_csv(OUT / "hits.csv", encoding="utf-8").assign(organism=ORGKEY)
    h = h[h.step_id.isin(sid2pid)].copy()
    h["pathway_id"] = h.step_id.map(sid2pid)
    cred = h[h.call == "credited"]
    anchors = cred[cred.flag == "dedicated"][["organism", "pathway_id", "step_id", "locus_tag", "gene_name",
                                               "product"]].drop_duplicates()
    tags = sorted(anchors.locus_tag.unique())
    r = gene_neighbors(locus_tags=tags, window=5, limit=None)
    log = {"tool": "gene_neighbors", "anchors": tags, "window": 5, "total_matching": r["total_matching"],
           "returned": r["returned"], "truncated": r.get("truncated"), "not_found": r.get("not_found"),
           "not_matched": r.get("not_matched")}
    print(json.dumps(log))
    assert r["returned"] == r["total_matching"]
    nb = pd.DataFrame(r["results"])
    anc = pd.DataFrame(r["anchors"]).rename(columns={"locus_tag": "anchor_locus_tag", "strand": "anchor_strand"})
    nb = nb.merge(anc[["anchor_locus_tag", "organism_name", "contig", "anchor_strand"]], on="anchor_locus_tag",
                  how="left")
    nb["transporter"] = [a02.is_transporter(c, p) for c, p in zip(nb.gene_category, nb["product"])]
    hit_by_tag = h.groupby("locus_tag").apply(
        lambda g: ";".join(sorted({f"{s}[{c.split(':')[0].split(' ')[0]}]" for s, c in zip(g.step_id, g.call)})),
        include_groups=False).to_dict()
    nb["neighbour_catalogue_hits"] = nb.neighbor_locus_tag.map(hit_by_tag).fillna("")
    nb["within3_same_strand"] = (nb.rank_offset.abs() <= 3) & nb.same_strand.astype(bool)
    nb.to_csv(OUT / "neighbourhoods.csv", index=False, encoding="utf-8")
    rows = []
    for a in anchors.itertuples():
        n = nb[(nb.anchor_locus_tag == a.locus_tag) & nb.within3_same_strand]
        pw_tags = set(cred[(cred.pathway_id == a.pathway_id) & (cred.step_id != a.step_id)].locus_tag) - {a.locus_tag}
        same_pw = n[n.neighbor_locus_tag.isin(pw_tags)]
        tr = n[n.transporter]
        why = []
        if len(tr):
            why.append("transporter: " + "; ".join(f"{t}({o:+d}) {p}" for t, o, p in
                                                    zip(tr.neighbor_locus_tag, tr.rank_offset, tr["product"])))
        if len(same_pw):
            why.append("same-pathway step: " + "; ".join(f"{t}({o:+d})" for t, o in
                                                          zip(same_pw.neighbor_locus_tag, same_pw.rank_offset)))
        rows.append({"organism": a.organism, "pathway_id": a.pathway_id, "step_id": a.step_id,
                     "anchor_locus_tag": a.locus_tag, "gene_name": a.gene_name, "product": a.product,
                     "n_neighbours_returned": int((nb.anchor_locus_tag == a.locus_tag).sum()),
                     "n_same_strand_within3": len(n), "transporter_within3": len(tr) > 0,
                     "same_pathway_step_within3": len(same_pw) > 0,
                     "operon_call": "package" if (len(tr) or len(same_pw)) else "lone gene",
                     "evidence": " | ".join(why),
                     "same_strand_within3_products": " | ".join(f"{t}({o:+d}) {p}" for t, o, p in
                                                                 zip(n.neighbor_locus_tag, n.rank_offset,
                                                                     n["product"]))})
    oc = pd.DataFrame(rows).sort_values(["pathway_id", "step_id"])
    oc.to_csv(OUT / "operon_calls.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 300)
    pd.set_option("display.max_colwidth", 250)
    print("neighbour rows:", len(nb), "| operon rows:", len(oc))
    print(oc[["pathway_id", "anchor_locus_tag", "gene_name", "operon_call", "evidence",
              "same_strand_within3_products"]].to_string(index=False))
    allnb = nb[nb.rank_offset.abs() <= 3][["anchor_locus_tag", "neighbor_locus_tag", "rank_offset", "strand",
                                            "same_strand", "gene_category", "product"]]
    print(allnb.to_string(index=False))


if __name__ == "__main__":
    main()
