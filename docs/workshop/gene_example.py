"""Collect one gene's connections for the workshop deck's map slide.

Run from the repo root:  uv run python docs/workshop/gene_example.py
Writes docs/workshop/gene_example.json.
"""
import json
from pathlib import Path

from multiomics_explorer.api import functions as f

LOCUS = "PMM0920"  # glnA, Prochlorococcus MED4
ORG = "Prochlorococcus MED4"
OUT = Path(__file__).with_name("gene_example.json")


def env(d):
    return {k: v for k, v in d.items() if k != "results"}


out = {
    "overview": f.gene_overview([LOCUS], verbose=True),
    "expression_summary": env(f.differential_expression_by_gene(locus_tags=[LOCUS], summary=True)),
    "expression_significant": env(f.differential_expression_by_gene(
        locus_tags=[LOCUS], significant_only=True, summary=True)),
    "homologs": env(f.gene_homologs([LOCUS], summary=True)),
    "ontology_terms": f.gene_ontology_terms([LOCUS], organism=ORG, limit=60),
    "metabolites": f.metabolites_by_gene([LOCUS], organism=ORG),
}
OUT.write_text(json.dumps(out, indent=1, default=str))
print(f"wrote {OUT}")
