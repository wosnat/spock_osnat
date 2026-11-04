"""THROWAWAY pilot: Alteromonas macleodii HOT1A3 vs MED4 on the DRAFT (unapproved) pathway catalogue.

Task 1 (hits): same rules as methods/scripts/04_product_agreement_med4.py
  - KO matching via genes_by_ontology(kegg) on every catalogue + control KO (+ broad table KOs, informational)
  - product-agreement keywords (case-insensitive substring of KG product); mismatch -> "flagged: KO/product mismatch"
  - exclusion rule: credit_eligible == False (KO on a shared step / control / broad table, sitting on a dedicated
    step) -> "shared-enzyme hit (not credited)"
  - broad-table KOs -> "broad (never credited)"
Task 2 (status): v5 rule (proposal section 3 step 3)
  - step present = every AND group (";") has >= 1 KO (alternatives "|") with a credited hit on that step
  - per pathway: k/n dedicated steps, N-freeing step present/missing; status from pathway_assessability.status_rule
  - per amino acid: complete > partial > absent > can't be judged; partial ties: highest k/n, then more steps
  - MED4 computed the same way from methods/data/med4_step_hits.csv (no MED4 re-query of hits)
Task 4 (controls): CTRL_* rows of the hits + NEG_astB (informational).

KG calls: genes_by_ontology(ontology='kegg', organism='Alteromonas macleodii HOT1A3', term_ids=<KOs>,
          min_gene_set_size=0, max_gene_set_size=None, limit=None); list_organisms for gene counts (HOT1A3, MED4).
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/spike/alteromonas_hot1a3/scripts/a01_hits_status.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import genes_by_ontology, list_organisms

HERE = Path(__file__).resolve().parents[1]
ANALYSIS = HERE.parents[1]
MDATA = ANALYSIS / "methods" / "data"
OUT = HERE / "data"
ORG = "Alteromonas macleodii HOT1A3"
AAS = ["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro",
       "Ser", "Thr", "Trp", "Tyr", "Val"]
RANK = {"complete": 0, "partial": 1, "absent": 2, "can't be judged": 3, "not assessable": 4, "excluded": 5}


def agrees(product: str, kws: str) -> bool:
    p = (product or "").lower()
    return any(k.lower() in p for k in str(kws).split("|") if k)


def units():
    long = pd.read_csv(MDATA / "pathway_catalogue.csv", encoding="utf-8")
    steps = pd.read_csv(MDATA / "pathway_catalogue_steps.csv", encoding="utf-8")
    ctrl = pd.read_csv(MDATA / "proposed_controls.csv", encoding="utf-8")
    kw = steps.drop_duplicates("step_id").set_index("step_id").product_keywords
    rows = [(r.step_id, r.amino_acid, r.step_key, r.ko, r.ko_groups, kw[r.step_id], r.flag, bool(r.credit_eligible),
             r.exclusion_reason if isinstance(r.exclusion_reason, str) else "",
             r.credits_multiple_aa if isinstance(r.credits_multiple_aa, str) else "") for _, r in long.iterrows()]
    for _, c in ctrl.iterrows():
        for k in c.kos.split(";"):
            rows.append((c.control_id, "control", c.control_id, k, c.kos.replace(";", "|"), c.product_keywords,
                         c.control_type, True, "", ""))
    return pd.DataFrame(rows, columns=["step_id", "amino_acid", "step_key", "ko", "ko_groups", "product_keywords",
                                       "flag", "credit_eligible", "exclusion_reason", "credits_multiple_aa"]), steps


def get_hits(u, broad):
    kos = sorted(set(u.ko) | set(broad.ko))
    g = genes_by_ontology(ontology="kegg", organism=ORG, term_ids=[f"kegg.orthology:{k}" for k in kos],
                          min_gene_set_size=0, max_gene_set_size=None, limit=None)
    log = {"tool": "genes_by_ontology", "organism": ORG, "n_term_ids": len(kos),
           "total_matching": g["total_matching"], "returned": g["returned"], "truncated": g.get("truncated")}
    print(json.dumps(log))
    assert g["returned"] == g["total_matching"], "paging needed"
    gdf = pd.DataFrame(g["results"])
    gdf["ko"] = gdf.term_id.str.replace("kegg.orthology:", "", regex=False)
    keep = [c for c in ["ko", "locus_tag", "gene_name", "product", "evidence", "sources"] if c in gdf.columns]
    hits = u.merge(gdf[keep], on="ko", how="inner")
    hits["product_agrees"] = [agrees(p, k) for p, k in zip(hits["product"], hits.product_keywords)]
    hits["call"] = [("shared-enzyme hit (not credited)" if not ok else "credited" if agree
                     else "flagged: KO/product mismatch")
                    for ok, agree in zip(hits.credit_eligible, hits.product_agrees)]
    b = broad[["ko", "label", "category"]].merge(gdf[keep], on="ko", how="inner")
    b = b.assign(step_id="BROAD:" + b.label, amino_acid="broad", step_key=b.label, flag="broad", credit_eligible=False,
                 call="broad (never credited)")
    hits = pd.concat([hits, b.drop(columns=["label", "category"])], ignore_index=True)
    return hits.sort_values(["amino_acid", "step_id", "locus_tag"]).reset_index(drop=True), log, gdf


def step_present(groups: str, credited_kos: set) -> bool:
    return all(any(k in credited_kos for k in grp.split("|")) for grp in str(groups).split(";"))


def pathway_status(steps, assess, hits, organism):
    rows = []
    cred = hits[hits.call == "credited"]
    for pid, s in steps.sort_values("step_order").groupby("pathway_id", sort=False):
        a = assess[assess.pathway_id == pid].iloc[0]
        st_rows, loci = [], []
        for r in s.itertuples():
            h = cred[cred.step_id == r.step_id]
            pres = step_present(r.ko_groups, set(h.ko))
            st_rows.append((r.step_id, r.flag, bool(r.is_n_freeing), pres))
            if pres:
                loci.append(f"{r.step_id}:" + ",".join(sorted(h.locus_tag.unique())))
        ded = [x for x in st_rows if x[1] == "dedicated"]
        k, n = sum(x[3] for x in ded), len(ded)
        nf = [x for x in st_rows if x[2]]
        nf_present = all(x[3] for x in nf) if nf else False
        all_present = all(x[3] for x in st_rows)
        rule = a.status_rule
        if rule.startswith("not assessable"):
            status = "not assessable"
        elif rule.startswith("excluded"):
            status = "excluded"
        elif rule.startswith("cannot be judged"):
            status = "can't be judged"
        elif k == n and nf_present:
            status = "complete"
        elif k == 0:
            status = "absent"
        else:
            status = "partial"
        ded_loci = sorted({lt for sid, fl, _, pres in st_rows if fl == "dedicated" and pres
                           for lt in cred[cred.step_id == sid].locus_tag})
        rows.append({"organism": organism, "amino_acid": s.amino_acid.iloc[0], "pathway_id": pid,
                     "pathway_name": s.pathway_name.iloc[0], "n_steps": len(st_rows), "k_dedicated": k,
                     "n_dedicated": n, "k_of_n": f"{k}/{n}" if n else "-",
                     "n_freeing_steps": ";".join(x[0] for x in nf),
                     "n_freeing_present": "present" if nf_present else "missing",
                     "all_steps_present": all_present,
                     "all_shared_route_fully_present": bool(rule.startswith("cannot be judged") and all_present),
                     "status_rule": rule, "status": status,
                     "dedicated_locus_tags": ";".join(ded_loci), "present_steps_loci": " | ".join(loci),
                     "missing_steps": ";".join(x[0] for x in st_rows if not x[3])})
    return pd.DataFrame(rows)


def aa_status(ps, organism):
    out = []
    for aa in AAS:
        p = ps[ps.amino_acid == aa].copy()
        p["rank"] = p.status.map(RANK)
        p["frac"] = p.k_dedicated / p.n_dedicated.where(p.n_dedicated > 0, 1)
        best_rank = p["rank"].min()
        if best_rank >= RANK["not assessable"]:
            cell = "not assessable"
            pick = p.iloc[0]
        else:
            cell = [s for s, r in RANK.items() if r == best_rank][0]
            cand = p[p["rank"] == best_rank].sort_values(["frac", "n_steps"], ascending=[False, False])
            pick = cand.iloc[0]
        comp = p[p.status == "complete"]
        out.append({"organism": organism, "amino_acid": aa, "cell_status": cell,
                    "cell_k_of_n": pick.k_of_n if cell in ("partial", "complete") else "",
                    "cell_pathway": pick.pathway_id if cell in ("partial", "complete") else "",
                    "complete_pathways": ";".join(comp.pathway_id),
                    "n_pathways": len(p), "n_not_assessable": int((p.status == "not assessable").sum()),
                    "n_excluded": int((p.status == "excluded").sum()),
                    "all_shared_route_fully_present": bool(p.all_shared_route_fully_present.any()),
                    "all_shared_routes_present": ";".join(p[p.all_shared_route_fully_present].pathway_id),
                    "dedicated_locus_tags": ";".join(sorted({x for v in p.dedicated_locus_tags for x in v.split(";")
                                                             if x})),
                    "pathway_statuses": "; ".join(f"{r.pathway_id}={r.status}"
                                                  + (f"({r.k_of_n})" if r.status in ("partial", "complete") else "")
                                                  for r in p.itertuples())})
    return pd.DataFrame(out)


def main():
    u, steps = units()
    assess = pd.read_csv(MDATA / "pathway_assessability.csv", encoding="utf-8")
    broad = pd.read_csv(MDATA / "broad_enzymes.csv", encoding="utf-8")
    hits, log, gdf = get_hits(u, broad)
    cols = ["step_id", "amino_acid", "flag", "ko", "locus_tag", "gene_name", "product", "call", "credit_eligible",
            "exclusion_reason", "product_keywords", "ko_groups", "credits_multiple_aa", "evidence", "sources"]
    cols = [c for c in cols if c in hits.columns]
    hits[cols].to_csv(OUT / "hits.csv", index=False, encoding="utf-8")
    fl = hits[hits.call.str.startswith("flagged")]
    fl[cols].to_csv(OUT / "flagged_hits.csv", index=False, encoding="utf-8")
    print("hits rows:", len(hits), "| genes:", hits.locus_tag.nunique(), hits.call.value_counts().to_dict())

    ps_a = pathway_status(steps, assess, hits[hits.amino_acid.isin(AAS)], ORG)
    ps_a.to_csv(OUT / "pathway_status.csv", index=False, encoding="utf-8")
    aa_a = aa_status(ps_a, ORG)
    aa_a.to_csv(OUT / "aa_status.csv", index=False, encoding="utf-8")

    med = pd.read_csv(MDATA / "med4_step_hits.csv", encoding="utf-8")
    ps_m = pathway_status(steps, assess, med[med.amino_acid.isin(AAS)], "Prochlorococcus MED4")
    ps_m.to_csv(OUT / "pathway_status_med4.csv", index=False, encoding="utf-8")
    aa_m = aa_status(ps_m, "Prochlorococcus MED4")
    aa_m.to_csv(OUT / "aa_status_med4.csv", index=False, encoding="utf-8")

    keep = ["amino_acid", "cell_status", "cell_k_of_n", "cell_pathway", "complete_pathways",
            "all_shared_route_fully_present", "dedicated_locus_tags", "n_not_assessable"]
    side = aa_m[keep].merge(aa_a[keep], on="amino_acid", suffixes=("_med4", "_hot1a3"))
    side.insert(1, "n_pathways", aa_a.n_pathways)
    side.to_csv(OUT / "aa_status_med4_vs_hot1a3.csv", index=False, encoding="utf-8")

    # controls
    ctrl = hits[hits.amino_acid == "control"][cols]
    ctrl.to_csv(OUT / "controls.csv", index=False, encoding="utf-8")

    # dedicated step counts (searched vs found), by step
    ded_steps = steps[steps.flag == "dedicated"]
    obs = assess.set_index("pathway_id")
    summ = {}
    for name, h in (("HOT1A3", hits), ("MED4", med)):
        cred = h[h.call == "credited"]
        found = [sid for sid, g in ded_steps.groupby("step_id") if step_present(g.ko_groups.iloc[0],
                                                                                   set(cred[cred.step_id == sid].ko))]
        summ[name] = {"dedicated_steps_catalogued": int(ded_steps.step_id.nunique()),
                      "dedicated_steps_found": len(found), "dedicated_steps_found_ids": found}
    summ["HOT1A3"]["complete_pathways"] = ps_a[ps_a.status == "complete"].pathway_id.tolist()
    summ["MED4"]["complete_pathways"] = ps_m[ps_m.status == "complete"].pathway_id.tolist()
    # unobservable dedicated steps (no KG node for any KO)
    unobs = set()
    for v in assess.unobservable_steps.dropna():
        unobs |= set(v.split(";"))
    summ["dedicated_steps_unobservable"] = sorted(unobs & set(ded_steps.step_id))
    orgs = {}
    for o in (ORG, "MED4"):
        r = list_organisms(organism_names=[o])
        log2 = {"tool": "list_organisms", "organism_names": [o], "total_matching": r["total_matching"],
                "returned": r["returned"]}
        print(json.dumps(log2))
        orgs[o] = [(x["organism_name"], x["gene_count"]) for x in r["results"]]
    summ["gene_counts"] = orgs
    summ["kg_calls"] = [log]
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    print(json.dumps(summ, indent=1))
    print(side.to_string(index=False))
    print(hits[["step_id", "flag", "ko", "locus_tag", "gene_name", "product", "call"]].to_string(index=False))


if __name__ == "__main__":
    main()
