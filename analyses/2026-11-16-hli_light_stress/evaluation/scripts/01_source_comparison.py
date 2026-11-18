"""Source comparison: what the KG says each source publication said about MED4 hli genes,
next to this analysis's set-level and per-gene calls.

Sources pulled from the KG:
  - discussed_by_publication(verbose=True), all entity kinds (gene + kegg_pathway), with evidence quotes.
    Kept: rows whose entity is one of the 23 hli locus tags, plus any row (any gene/pathway/organism)
    whose entity_name or evidence matches the hli regex.
  - list_publications(verbose=True) abstract + description; sentences matching the hli regex.
Writes evaluation/data/source_comparison.csv, source_comparison_summary.csv, source_comparison_discusses_all.csv,
source_comparison_kg_calls.csv.
Run from repo root:
  PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/evaluation/scripts/01_source_comparison.py
"""
import re
from pathlib import Path

import pandas as pd
import multiomics_explorer as me

EVAL = Path(__file__).resolve().parents[1]
ROOT = EVAL.parent
ANA = ROOT / "analysis" / "data"
OUT = EVAL / "data"
OUT.mkdir(parents=True, exist_ok=True)

DROPPED = {"10.1038/ismej.2016.70": "dropped (Aharonovich & Sher 2016 coculture)",
           "10.1073/pnas.0601301103": "dropped (Martiny 2006 phosphate)"}
HLI_RE = re.compile(r"\bhli|high[\s-]*light[\s-]*inducible|\bHLIP", re.IGNORECASE)

refs = pd.read_csv(ANA / "references.csv", encoding="utf-8")
cons = pd.read_csv(ANA / "explore_D5_conservation.csv", encoding="utf-8")
hli_tags = list(cons.locus_tag)
assert len(hli_tags) == 23, len(hli_tags)
group = {r.locus_tag: (f"responder (cluster {r.cluster})" if r.cluster in (3, 4) else f"quiet (cluster {r.cluster})")
         for r in cons.itertuples()}
exps = pd.read_csv(ROOT / "methods" / "data" / "experiments.csv", encoding="utf-8")
exp_doi = dict(zip(exps.experiment_id, exps.publication_doi))
ecalls = pd.read_csv(ANA / "experiment_calls.csv", encoding="utf-8")
ecalls = ecalls[ecalls.set == "hli"].copy()
gcalls = pd.read_csv(ANA / "hli_gene_calls.csv", encoding="utf-8")
ecalls["doi"] = ecalls.experiment_id.map(exp_doi)
gcalls["doi"] = gcalls.experiment_id.map(exp_doi)
# experiments.csv may not list dropped experiments; fall back to prefix match on references DOIs
for df in (ecalls, gcalls):
    miss = df.doi.isna()
    for doi in refs.doi:
        df.loc[miss & df.experiment_id.str.startswith(doi + "_"), "doi"] = doi
    assert df.doi.notna().all(), df.loc[df.doi.isna(), "experiment_id"].unique()

kg_calls = []
dois = list(refs.doi)
pubs_r = me.list_publications(publication_dois=dois, verbose=True, limit=None)
kg_calls.append(dict(tool="list_publications", args=f"publication_dois={len(dois)} DOIs, verbose=True",
                     total_matching=pubs_r.get("total_matching"), returned=len(pubs_r["results"])))
pubs = {p["doi"].lower(): p for p in pubs_r["results"]}
disc = me.discussed_by_publication(publication_dois=dois, verbose=True, limit=None)
kg_calls.append(dict(tool="discussed_by_publication", args=f"publication_dois={len(dois)} DOIs, verbose=True, all kinds",
                     total_matching=disc["total_matching"], returned=len(disc["results"])))
assert disc["total_matching"] == len(disc["results"]), "truncated"
d = pd.DataFrame(disc["results"])
d.to_csv(OUT / "source_comparison_discusses_all.csv", index=False, encoding="utf-8")
print("discusses not_found:", disc["not_found"], "not_matched:", disc["not_matched"])


def set_call(doi):
    sub = ecalls[ecalls.doi == doi]
    parts = []
    for eid, g in sub.groupby("experiment_id", sort=False):
        lab = g.label.iloc[0]
        dd = {r.direction: r for r in g.itertuples()}
        s = []
        for dr in ("up", "down"):
            if dr in dd:
                r = dd[dr]
                s.append(f"{dr}-test: {r.timepoint_count}, padj_bh={r.padj_exp_bh}")
        parts.append(f"{lab}: call={g.experiment_call.iloc[0]} [{'; '.join(s)}]")
    return " | ".join(parts)


def gene_calls(doi, tag):
    sub = gcalls[(gcalls.doi == doi) & (gcalls.locus_tag == tag)].sort_values(["experiment_id", "timepoint_order"])
    parts = []
    for eid, g in sub.groupby("experiment_id", sort=False):
        tps = "; ".join(f"{r.timepoint}={r.call}" + (f" (log2fc={r.log2fc:.2f})" if pd.notna(r.log2fc) else "")
                        for r in g.itertuples())
        parts.append(f"{g.label.iloc[0]}: {tps}")
    return " | ".join(parts) if parts else "no rows for this gene in this publication's experiments"


def set_gene_counts(doi):
    sub = gcalls[gcalls.doi == doi]
    parts = []
    for eid, g in sub.groupby("experiment_id", sort=False):
        tp = []
        for t, gt in g.sort_values("timepoint_order").groupby("timepoint", sort=False):
            vc = gt.call.value_counts()
            tp.append(f"{t}: up {vc.get('up', 0)}/down {vc.get('down', 0)}/ns {vc.get('ns', 0)}/not_measured {vc.get('not_measured', 0)}")
        parts.append(f"{g.label.iloc[0]}: " + "; ".join(tp))
    return " | ".join(parts)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text or "") if HLI_RE.search(s)]


rows, summ = [], []
for ref in refs.itertuples():
    doi = ref.doi
    status = DROPPED.get(doi, "analysed")
    eids = " | ".join(sorted(ecalls.loc[ecalls.doi == doi, "experiment_id"].unique()))
    base = dict(doi=doi, cite=ref.cite, status=status, experiment_ids=eids)
    sc = set_call(doi)
    sub = d[d.doi.str.lower() == doi.lower()] if len(d) else d
    n_gene_rows = 0
    for r in sub.itertuples():
        ev = r.evidence if isinstance(r.evidence, str) else ""
        name = r.entity_name if isinstance(r.entity_name, str) else ""
        is_hli = r.entity_id in hli_tags
        txt_match = bool(HLI_RE.search(ev) or HLI_RE.search(name))
        if not (is_hli or txt_match):
            continue
        if r.entity_kind == "gene" and is_hli:
            ent, grp, gc, n_gene_rows = r.entity_id, group[r.entity_id], gene_calls(doi, r.entity_id), n_gene_rows + 1
            note = "hli locus tag"
        elif r.entity_kind == "gene":
            ent, grp = r.entity_id, "not in 23-gene hli set"
            gc = "n/a (not an analysed hli gene)"
            note = f"gene not in hli set ({r.organism}); name/evidence matches hli text"
        else:
            ent, grp, gc = "hli set", "n/a", set_gene_counts(doi)
            note = f"kegg_pathway {r.entity_id}; evidence matches hli text"
        rows.append(dict(**base, entity=ent, entity_name=name, entity_kind=r.entity_kind,
                         organism=getattr(r, "organism", None), prominence=r.prominence, match_basis=note,
                         source_statement_verbatim=ev, source_field="discusses.evidence",
                         our_set_call=sc, our_gene_calls_summary=gc, group=grp))
    p = pubs.get(doi.lower(), {})
    mentions = []
    for fld in ("abstract", "description"):
        for s in sentences(p.get(fld)):
            mentions.append(f"[{fld}] {s}")
            rows.append(dict(**base, entity="hli set", entity_name="", entity_kind="publication_text",
                             organism=None, prominence=None, match_basis=f"{fld} sentence matches hli text",
                             source_statement_verbatim=s, source_field=f"publication.{fld}",
                             our_set_call=sc, our_gene_calls_summary=set_gene_counts(doi), group="n/a"))
    hli_disc = sub[sub.entity_id.isin(hli_tags)] if len(sub) else sub
    summ.append(dict(doi=doi, cite=ref.cite, status=status,
                     n_discusses_edges_total=len(sub),
                     n_hli_genes_discussed=hli_disc.entity_id.nunique() if len(sub) else 0,
                     hli_genes_discussed=";".join(sorted(hli_disc.entity_id.unique())) if len(sub) else "",
                     n_other_rows_text_mentions_hli=sum(1 for x in rows if x["doi"] == doi and x["source_field"] == "discusses.evidence"
                                                        and x["entity"] not in hli_tags),
                     abstract_or_description_mentions_hli=bool(mentions),
                     verbatim_mention=" || ".join(mentions),
                     kg_holds_hli_statement=bool(len(hli_disc)) or any(x["doi"] == doi for x in rows),
                     our_set_call=sc))
    if not any(x["doi"] == doi for x in rows):
        rows.append(dict(**base, entity="hli set", entity_name="", entity_kind="none", organism=None, prominence=None,
                         match_basis="none", source_statement_verbatim="KG holds no hli statement",
                         source_field="none", our_set_call=sc, our_gene_calls_summary=set_gene_counts(doi), group="n/a"))

out = pd.DataFrame(rows)
out.to_csv(OUT / "source_comparison.csv", index=False, encoding="utf-8")
sm = pd.DataFrame(summ)
sm.to_csv(OUT / "source_comparison_summary.csv", index=False, encoding="utf-8")
pd.DataFrame(kg_calls).to_csv(OUT / "source_comparison_kg_calls.csv", index=False, encoding="utf-8")
print(pd.DataFrame(kg_calls).to_string(index=False))
print(len(out), "rows;", len(sm), "publications")
print(sm[["cite", "status", "n_discusses_edges_total", "n_hli_genes_discussed", "n_other_rows_text_mentions_hli",
          "abstract_or_description_mentions_hli", "kg_holds_hli_statement"]].to_string(index=False))
