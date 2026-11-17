"""Reference list for paper.md from the KG: publications of the 28 used experiments (+ the dropped one),
which experiments each supplied, and which publications name hli genes in their prose
(discussed_by_publication, KG literature index). Writes analysis/data/references.csv.
Run from the repo root: uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/21_references.py
"""
from pathlib import Path
import pandas as pd
import multiomics_explorer as me

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
exps = pd.read_csv(ROOT / "methods" / "data" / "experiments.csv")
hli = set(pd.read_csv(HERE / "data" / "hli_gene_calls.csv").locus_tag)
pubs = {p["doi"]: p for p in me.list_publications(limit=None)["results"]}
dois = sorted(exps.publication_doi.unique())
disc = me.discussed_by_publication(publication_dois=dois, entity_kind="gene", limit=None)
assert disc["total_matching"] == len(disc["results"]), "truncated"
d = pd.DataFrame(disc["results"])
idcol = "locus_tag" if "locus_tag" in d.columns else "entity_id"
rows = []
for doi in dois:
    p = pubs[doi]
    a = p["authors"] or []
    au = a[0].split()[-1] + (" et al." if len(a) > 2 else (" & " + a[1].split()[-1] if len(a) == 2 else ""))
    sub = d[d.doi == doi] if len(d) else d
    named = sorted(set(sub[idcol]).intersection(hli)) if len(sub) else []
    rows.append(dict(doi=doi, cite=f"{au} ({p['year']})", authors="; ".join(a), year=p["year"], title=p["title"],
                     journal=p["journal"], dropped_A8=doi == "10.1038/ismej.2016.70",
                     experiments=" | ".join(exps.loc[exps.publication_doi == doi, "label"]),
                     hli_genes_named=";".join(named), n_hli_named=len(named)))
out = pd.DataFrame(rows).sort_values(["year", "cite"])
out.to_csv(HERE / "data" / "references.csv", index=False, encoding="utf-8")
print(d.columns.tolist())
print(out[["cite", "journal", "dropped_A8", "n_hli_named", "experiments"]].to_string(index=False))
