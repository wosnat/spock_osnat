"""Collect headline KG facts for the workshop infographic.

Run from the repo root:  uv run python docs/workshop/kg_facts.py
Writes docs/workshop/kg_facts.json (every number on the infographic comes from it).
"""
import json
from pathlib import Path

from multiomics_explorer.api import functions as f

OUT = Path(__file__).with_name("kg_facts.json")


def strip_rows(d):
    """Keep summary envelopes; drop long result lists."""
    return {k: v for k, v in d.items() if k != "results"}


facts = {
    "release": {k: v for k, v in f.kg_release_info().items()
                if not k.endswith("excluded_targets")},
    "organisms": f.list_organisms(verbose=False),
    "publications": strip_rows(f.list_publications(summary=True)),
    "experiments": strip_rows(f.list_experiments(summary=True)),
    "derived_metrics": strip_rows(f.list_derived_metrics(summary=True)),
    "clustering": strip_rows(f.list_clustering_analyses(summary=True)),
    "metabolite_assays": strip_rows(f.list_metabolite_assays(summary=True)),
    "metabolites": strip_rows(f.list_metabolites(summary=True)),
    "omics_types": f.list_filter_values("omics_type"),
    "treatment_types": f.list_filter_values("treatment_type"),
    "compartments": f.list_filter_values("compartment"),
}

# Per evidence layer, in matched units: datasets and the data points they hold,
# summed from the list tools' own per-row counts.
exps = [x for x in f.list_experiments(limit=1000)["results"] if (x.get("gene_count") or 0) > 0]
dms = f.list_derived_metrics(limit=1000)["results"]
cls = f.list_clustering_analyses(limit=1000)["results"]
assays = f.list_metabolite_assays(limit=1000)
facts["evidence_layers"] = {
    "expression": {"datasets": len(exps), "data_points": sum(x["gene_count"] for x in exps),
                   "unit": "experiments with a DE table / gene results (gene x timepoint)"},
    "derived_metrics": {"datasets": len(dms), "data_points": sum(x["total_gene_count"] or 0 for x in dms),
                        "unit": "metric columns / gene values"},
    "clusters": {"datasets": len(cls), "data_points": sum(x["total_gene_count"] or 0 for x in cls),
                 "unit": "clustering analyses / genes per analysis, summed"},
    "metabolomics": {"datasets": len(assays["results"]), "data_points": assays["metabolite_count_total"],
                     "unit": "mass-spec assays / assay x compound results"},
}

schema = f.kg_schema(section="both")
facts["schema_inventory"] = {
    "node_labels": sorted(schema.get("nodes", {})),
    "relationship_types": sorted(schema.get("relationships", {})),
}

OUT.write_text(json.dumps(facts, indent=1, default=str))
print(f"wrote {OUT}")
for k, v in facts.items():
    print(k, list(v)[:15] if isinstance(v, dict) else type(v))
