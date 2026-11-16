"""KG access for the hli analysis (thin wrappers over the multiomics_explorer API).

Nothing here prints or saves expression rows. Callers hold DE rows in memory.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from multiomics_explorer import (
    differential_expression_by_gene,
    genes_by_homolog_group,
    genes_by_ontology,
    run_cypher,
)

METHODS = Path(__file__).resolve().parent
DATA = METHODS / "data"
ORGANISM = "Prochlorococcus MED4"

HLI_GROUPS = [
    "CK_00000050", "CK_00001414", "CK_00001058", "CK_00001313", "CK_00002026",
    "CK_00002025", "CK_00002168", "CK_00002332", "CK_00002661", "CK_00043616",
    "CK_00003573", "CK_00002103", "CK_00003421", "CK_00003510",
]
# reference set -> (Cyanorak role term, reference role). Iteration 2 (coordinator, 2026-11-16):
# nine Cyanorak reference categories; chaperones and oxidative stress kept as failed references.
REFERENCE_SETS = {
    "ribosomal_proteins": ("cyanorak.role:K.2", "broad_stress_growth"),
    "protein_folding": ("cyanorak.role:L.3", "broad_stress"),
    "protein_degradation": ("cyanorak.role:L.4", "broad_stress"),
    "adaptation_N": ("cyanorak.role:D.1.3", "specific_N"),
    "adaptation_P": ("cyanorak.role:D.1.5", "specific_P"),
    "adaptation_Fe": ("cyanorak.role:D.1.1", "specific_Fe"),
    "adaptation_light_minus_hli": ("cyanorak.role:D.1.2", "light_specific"),   # minus the 23 hli genes
    "photosystem_I": ("cyanorak.role:J.7", "photosynthesis"),
    "co2_fixation": ("cyanorak.role:J.2", "photosynthesis"),
    "photosystem_II": ("cyanorak.role:J.8", "photosynthesis"),
    "chaperones": ("cyanorak.role:D.4", "failed_reference"),
    "oxidative_stress": ("cyanorak.role:D.1.4", "failed_reference"),
}
COMPARISON_ROLES = {k: v[0] for k, v in REFERENCE_SETS.items()}
SET_ROLE = {k: v[1] for k, v in REFERENCE_SETS.items()}
COMPARISON_SETS = list(COMPARISON_ROLES)
MINUS_HLI = {"adaptation_light_minus_hli"}


def fetch_hli(conn=None) -> pd.DataFrame:
    res = genes_by_homolog_group(group_ids=HLI_GROUPS, organisms=["MED4"], limit=None, conn=conn)
    assert res["total_matching"] == len(res["results"])
    df = pd.DataFrame([{"locus_tag": r["locus_tag"], "group_id": r["group_id"],
                        "gene_name": r.get("gene_name"), "product": r.get("product")}
                       for r in res["results"]]).drop_duplicates()
    return df


def fetch_role_set(term_id: str, conn=None) -> pd.DataFrame:
    res = genes_by_ontology(ontology="cyanorak_role", organism="MED4", term_ids=[term_id],
                            min_gene_set_size=0, max_gene_set_size=100000, limit=None, conn=conn)
    assert res["total_matching"] == len(res["results"]), (res["total_matching"], len(res["results"]))
    return pd.DataFrame([{"locus_tag": r["locus_tag"], "gene_name": r.get("gene_name"),
                          "product": r.get("product")} for r in res["results"]]).drop_duplicates("locus_tag")


def fetch_genome(conn=None) -> list[str]:
    res = run_cypher("MATCH (g:Gene {organism_name: 'Prochlorococcus MED4'}) RETURN g.locus_tag AS locus_tag",
                     conn=conn)
    return sorted(r["locus_tag"] for r in res["results"])


def fetch_de(experiment_id: str, conn=None) -> pd.DataFrame:
    """All DE rows of one experiment (in memory only)."""
    res = differential_expression_by_gene(experiment_ids=[experiment_id], limit=None, conn=conn)
    assert res["total_matching"] == len(res["results"]), (experiment_id, res["total_matching"])
    cols = ["experiment_id", "locus_tag", "timepoint", "timepoint_order", "expression_status", "log2fc", "padj"]
    df = pd.DataFrame(res["results"])
    if df.empty:
        return pd.DataFrame(columns=cols)
    return df[cols]


def load_gene_sets() -> dict[str, list[str]]:
    gs = pd.read_csv(DATA / "gene_sets.csv", encoding="utf-8")
    return {s: sorted(g["locus_tag"]) for s, g in gs.groupby("set")}


def load_experiments() -> pd.DataFrame:
    return pd.read_csv(DATA / "experiments.csv", encoding="utf-8")
