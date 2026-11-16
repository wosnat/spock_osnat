"""Plan step 2: inventory of MED4 experiments for the hli analysis.

Writes one row per MED4 experiment with: stress type, proposed group
(light / non-light stress / non-stress / excluded), table type, and how many
hli and comparison genes the experiment MEASURED.

Coverage only: expression direction and significance are deliberately not
written or printed (the non-light stress results stay unseen until the plan
is set).

Run from the repo root:
    uv run python analyses/2026-11-16-hli_light_stress/spike/step2_med4_inventory.py
"""
from pathlib import Path

import pandas as pd
from multiomics_explorer import (
    differential_expression_by_gene,
    genes_by_homolog_group,
    genes_by_ontology,
    list_experiments,
)

OUT = Path(__file__).parent / "step2_med4_inventory.csv"
ORG = "Prochlorococcus MED4"

# Curated Cyanorak hli ortholog groups with MED4 members (decisions_log, step 1).
HLI_GROUPS = [
    "CK_00000050", "CK_00001414", "CK_00001058", "CK_00001313", "CK_00002026",
    "CK_00002025", "CK_00002168", "CK_00002332", "CK_00002661", "CK_00043616",
    "CK_00003573", "CK_00002103", "CK_00003421", "CK_00003510",
]
COMPARISON_ROLES = {
    "chaperones": "cyanorak.role:D.4",
    "oxidative_stress": "cyanorak.role:D.1.4",
    "photosystem_II": "cyanorak.role:J.8",
}

# --- gene sets -------------------------------------------------------------
hli = genes_by_homolog_group(group_ids=HLI_GROUPS, organisms=["MED4"], limit=None)
hli_tags = sorted({r["locus_tag"] for r in hli["results"]})
assert len(hli_tags) == 23, f"expected 23 MED4 hli genes, got {len(hli_tags)}"

sets = {"hli": hli_tags}
for name, term in COMPARISON_ROLES.items():
    res = genes_by_ontology(
        ontology="cyanorak_role", organism="MED4", term_ids=[term],
        min_gene_set_size=0, max_gene_set_size=100000, limit=None,
    )
    tags = sorted({r["locus_tag"] for r in res["results"]})
    overlap = set(tags) & set(hli_tags)
    assert not overlap, f"{name} overlaps hli: {overlap}"
    sets[name] = tags
all_tags = sorted({t for v in sets.values() for t in v})

# --- experiments -----------------------------------------------------------
exps = list_experiments(organism="MED4", limit=None)["results"]
assert len(exps) == 45, len(exps)

TABLE_CLASS = {
    "all_detected_genes": "sound",
    "significant_only": "approximate",
    "significant_any_timepoint": "approximate",
    "filtered_subset": "approximate (check filter)",
    "top_n": "descriptive",
}


def proposed_group(e):
    """Proposed grouping; borderline calls are flagged for the researcher."""
    tt = set(e["treatment_type"])
    eid, name = e["experiment_id"], e["experiment_name"].lower()
    if e["gene_count"] == 0 or tt & {"genomic_analysis", "tss_mapping", "compartment", "rna_decay"}:
        return "excluded", "no stressed-vs-control fold changes"
    if tt & {"light", "darkness", "diel"}:
        return "light", ""
    if "glucose" in name:
        return "non-stress", "borderline: glucose addition (may relieve dark stress)"
    if "air (0.036% co2 / 21% o2) vs time 0" in name:
        return "non-stress", "borderline: air-sparged control vs time 0"
    if "urea" in name or "cyanate" in name:
        return "non-stress", "borderline: acclimated to alternative N source"
    if "iron rescue" in name:
        return "non-stress", "borderline: relief from iron starvation"
    if tt == {"coculture"}:
        return "non-stress", "borderline: partner may relieve or cause stress"
    return "non-light stress", ""


rows = []
for e in exps:
    group, note = proposed_group(e)
    row = {
        "experiment_id": e["experiment_id"],
        "experiment_name": e["experiment_name"],
        "stress_type": ",".join(e["treatment_type"]),
        "background": ",".join(e["background_factors"]),
        "proposed_group": group,
        "group_note": note,
        "omics_type": e["omics_type"],
        "table_scope": e["table_scope"],
        "table_class": TABLE_CLASS.get(e["table_scope"], "none"),
        "table_scope_detail": e.get("table_scope_detail") or "",
        "n_timepoints": len(e.get("timepoints") or []) or 1,
        "genes_in_table": e["distinct_gene_count"],
    }
    if e["gene_count"] > 0:
        de = differential_expression_by_gene(
            experiment_ids=[e["experiment_id"]], locus_tags=all_tags, limit=None,
        )
        assert len(de["results"]) == de["total_matching"]
        present = {r["locus_tag"] for r in de["results"]}  # presence only
    else:
        present = set()
    for name, tags in sets.items():
        row[f"{name}_measured"] = len(present & set(tags))
    rows.append(row)

df = pd.DataFrame(rows)
for name, tags in sets.items():
    df[f"{name}_set_size"] = len(tags)
df = df.sort_values(["proposed_group", "stress_type", "experiment_id"])
df.to_csv(OUT, index=False, encoding="utf-8")

print(f"gene sets: " + ", ".join(f"{k}={len(v)}" for k, v in sets.items()))
print(f"wrote {len(df)} experiments to {OUT}")
print(df.groupby("proposed_group").size().to_string())
