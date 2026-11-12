"""Pathway-level scoring of the catalogue for one genome (v5 rule) - the pilot scoring code, made a module.

Source: spike/alteromonas_hot1a3/scripts/a01_hits_status.py (units, get_hits, step_present, pathway_status,
aa_status, and the inline "dedicated steps found" count of a01/m01 main()). Copied unchanged except:
  1. product agreement uses product_match.agrees (normalized matching; keywords now include EC-name synonyms
     from the catalogue files) and records the matched keyword (`matched_keyword` column);
  2. bookkeeping fix: a pathway whose status is "excluded" (N-neutral, e.g. Glu_GABA_shunt) contributes no
     locus tags to `dedicated_locus_tags` and no steps to the "dedicated steps found" count
     (`exclude_excluded_routes=True`; False reproduces the pilot bookkeeping);
  3. organism is a parameter instead of a module global.

Rules (proposal section 3 step 3, v5):
  - hit call: credit_eligible False -> "shared-enzyme hit (not credited)"; product agrees -> "credited";
    else "flagged: KO/product mismatch"; broad-table KOs -> "broad (never credited)"
  - step present = every AND group (";") has >= 1 KO (alternatives "|") with a credited hit on that step
  - per pathway: k/n dedicated steps, N-freeing step present/missing; status from pathway_assessability.status_rule
  - per amino acid: complete > partial > absent > can't be judged; partial ties: highest k/n, then more steps
"""
from __future__ import annotations

import pandas as pd

from product_match import agrees, matched_keyword

AAS = ["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro",
       "Ser", "Thr", "Trp", "Tyr", "Val"]
RANK = {"complete": 0, "partial": 1, "absent": 2, "can't be judged": 3, "not assessable": 4, "excluded": 5}
HIT_COLS = ["step_id", "amino_acid", "flag", "ko", "locus_tag", "gene_name", "product", "call", "matched_keyword",
            "credit_eligible", "exclusion_reason", "product_keywords", "ko_groups", "credits_multiple_aa", "evidence",
            "sources"]


def units(mdata):
    long = pd.read_csv(mdata / "pathway_catalogue.csv", encoding="utf-8")
    steps = pd.read_csv(mdata / "pathway_catalogue_steps.csv", encoding="utf-8")
    ctrl = pd.read_csv(mdata / "proposed_controls.csv", encoding="utf-8")
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


def call_hits(hits: pd.DataFrame) -> pd.DataFrame:
    """Add product_agrees / matched_keyword / call to a units x genes table."""
    hits = hits.copy()
    hits["matched_keyword"] = [matched_keyword(p, k) for p, k in zip(hits["product"], hits.product_keywords)]
    hits["product_agrees"] = hits.matched_keyword != ""
    hits["call"] = [("shared-enzyme hit (not credited)" if not ok else "credited" if agree
                     else "flagged: KO/product mismatch")
                    for ok, agree in zip(hits.credit_eligible, hits.product_agrees)]
    return hits


def kg_genes(organism, kos):
    from multiomics_explorer import genes_by_ontology
    g = genes_by_ontology(ontology="kegg", organism=organism, term_ids=[f"kegg.orthology:{k}" for k in kos],
                          min_gene_set_size=0, max_gene_set_size=None, limit=None)
    log = {"tool": "genes_by_ontology", "organism": organism, "n_term_ids": len(kos),
           "total_matching": g["total_matching"], "returned": g["returned"], "truncated": g.get("truncated")}
    assert g["returned"] == g["total_matching"], "paging needed"
    gdf = pd.DataFrame(g["results"])
    gdf["ko"] = gdf.term_id.str.replace("kegg.orthology:", "", regex=False)
    return gdf, log


def get_hits(u, broad, organism):
    kos = sorted(set(u.ko) | set(broad.ko))
    gdf, log = kg_genes(organism, kos)
    keep = [c for c in ["ko", "locus_tag", "gene_name", "product", "evidence", "sources"] if c in gdf.columns]
    hits = call_hits(u.merge(gdf[keep], on="ko", how="inner"))
    b = broad[["ko", "label", "category"]].merge(gdf[keep], on="ko", how="inner")
    b = b.assign(step_id="BROAD:" + b.label, amino_acid="broad", step_key=b.label, flag="broad", credit_eligible=False,
                 call="broad (never credited)")
    hits = pd.concat([hits, b.drop(columns=["label", "category"])], ignore_index=True)
    return hits.sort_values(["amino_acid", "step_id", "locus_tag"]).reset_index(drop=True), log, gdf


def step_present(groups: str, credited_kos: set) -> bool:
    return all(any(k in credited_kos for k in grp.split("|")) for grp in str(groups).split(";"))


def pathway_status(steps, assess, hits, organism, exclude_excluded_routes=True):
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
        if exclude_excluded_routes and status == "excluded":
            ded_loci = []  # bookkeeping fix: excluded routes never contribute locus tags
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
                    "dedicated_locus_tags": ";".join(sorted({x for v in p.dedicated_locus_tags.fillna("")
                                                             for x in v.split(";") if x})),
                    "pathway_statuses": "; ".join(f"{r.pathway_id}={r.status}"
                                                  + (f"({r.k_of_n})" if r.status in ("partial", "complete") else "")
                                                  for r in p.itertuples())})
    return pd.DataFrame(out)


def dedicated_steps_found(steps, assess, hits, exclude_excluded_routes=True) -> list[str]:
    """Dedicated step_ids present (every AND group credited). Steps on excluded (N-neutral) routes are left out
    when exclude_excluded_routes (the pilot counted them)."""
    excluded = set(assess[assess.status_rule.str.startswith("excluded")].pathway_id)
    ded = steps[steps.flag == "dedicated"]
    if exclude_excluded_routes:
        ded = ded[~ded.pathway_id.isin(excluded)]
    cred = hits[hits.call == "credited"]
    return [sid for sid, g in ded.groupby("step_id")
            if step_present(g.ko_groups.iloc[0], set(cred[cred.step_id == sid].ko))]


def status_counts(aa: pd.DataFrame) -> dict:
    vc = aa.cell_status.value_counts()
    return {k: int(vc.get(k, 0)) for k in ("complete", "partial", "absent", "can't be judged", "not assessable")}
