"""Independent spot checks of the methods pipeline.

Written by the main thread, deliberately outside the kg-coder module, so the
pipeline is checked by separate code. Recomputes selected tests, flags and one
per-experiment aggregate straight from the KG API with scipy, without importing
methods/hli_scoring.py, pipeline.py or kg_io.py, and compares every count and
p-value with methods/data/control_tests.csv and control_experiment_calls.csv.
No hli genes are used, except to subtract them from D.1.2 for the
light-minus-hli check.

Run from the repo root:
    uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/07_spot_checks_independent.py
"""
from pathlib import Path

import pandas as pd
from scipy.stats import hypergeom
from multiomics_explorer import (
    differential_expression_by_gene, genes_by_homolog_group, genes_by_ontology, list_organisms,
)

HERE = Path(__file__).resolve().parents[1]
CT = pd.read_csv(HERE / "data" / "control_tests.csv", encoding="utf-8", keep_default_na=False,
                 na_values=[""])
CALLS = pd.read_csv(HERE / "data" / "control_experiment_calls.csv", encoding="utf-8")
OUT = HERE / "data" / "spot_checks_independent.csv"
STATUS = {"up": "significant_up", "down": "significant_down"}
TOO_FEW, GENOME_WIDE = 10, 0.30  # proposal.md Approach 5 and 6

# Genome size from the organism record (the pipeline uses its own genome fetch).
GENOME_N = list_organisms(organism_names=["MED4"])["results"][0]["gene_count"]

HLI_GROUPS = ["CK_00000050", "CK_00001414", "CK_00001058", "CK_00001313", "CK_00002026",
              "CK_00002025", "CK_00002168", "CK_00002332", "CK_00002661", "CK_00043616",
              "CK_00003573", "CK_00002103", "CK_00003421", "CK_00003510"]
_hli = genes_by_homolog_group(group_ids=HLI_GROUPS, organisms=["MED4"], limit=None)
HLI = {r["locus_tag"] for r in _hli["results"]}
assert len(HLI) == 23


def term_genes(term, minus=frozenset()):
    r = genes_by_ontology(ontology="cyanorak_role", organism="MED4", term_ids=[term],
                          min_gene_set_size=0, max_gene_set_size=100000, limit=None)
    assert r["total_matching"] == len(r["results"])
    return {x["locus_tag"] for x in r["results"]} - set(minus)


_cache = {}


def de_at(exp, tp):
    if exp not in _cache:
        r = differential_expression_by_gene(experiment_ids=[exp], limit=None)
        assert r["total_matching"] == len(r["results"])
        _cache[exp] = pd.DataFrame(r["results"])
    de = _cache[exp]
    if tp is None:
        tps = de["timepoint"].dropna().unique()
        assert len(tps) <= 1, f"{exp}: several timepoints, name one"
        return de, (tps[0] if len(tps) else None)
    return de[de["timepoint"] == tp], tp


def pipeline_row(exp, tp, d, setname=None):
    m = CT[(CT.experiment_id == exp) & (CT.timepoint.astype(str) == str(tp)) & (CT.direction == d)]
    if setname:
        m = m[m["set"] == setname]
    assert len(m) >= 1, (exp, tp, d, setname)
    return m.iloc[0]


def independent_test(exp, tp, d, genes, bgkind):
    sub, tp = de_at(exp, tp)
    bg = set(sub["locus_tag"]) if bgkind == "measured" else None
    N = len(bg) if bg is not None else GENOME_N
    K = len(genes & bg) if bg is not None else len(genes)
    sig = set(sub.loc[sub["expression_status"] == STATUS[d], "locus_tag"])
    n, k = len(sig), len(genes & sig)
    return tp, N, K, n, k, hypergeom.sf(k - 1, N, K, n)


rows = []

# 1. Fisher tests: every count and the p-value must match.
FISHER = [
    ("Fe set, iron starvation 12h up", "10.1038/ismej.2011.49_iron_iron_starvation_med4_med4_microarray_light", "12h", "up", "adaptation_Fe", "cyanorak.role:D.1.1", False, "genome"),
    ("Ribosomal, N deprivation 12h down", "10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray", "12h", "down", "ribosomal_proteins", "cyanorak.role:K.2", False, "measured"),
    ("P set, phosphate 48h up", "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray", "48h", "up", "adaptation_P", "cyanorak.role:D.1.5", False, "genome"),
    ("PSII, extended darkness 2h up (raw)", "10.64898/2026.04.15.718746_extended_darkness_med4", "2h", "up", "photosystem_II", "cyanorak.role:J.8", False, "measured"),
    ("Ribosomal, salt down", "10.3389/fmicb.2022.1038136_salt_low_salinity_acclimation_28_med4_rnaseq", None, "down", "ribosomal_proteins", "cyanorak.role:K.2", False, "measured"),
    ("Light minus hli, N deprivation 48h down", "10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray", "48h", "down", "adaptation_light_minus_hli", "cyanorak.role:D.1.2", True, "measured"),
]
for label, exp, tp, d, setname, term, minus_hli, bgkind in FISHER:
    genes = term_genes(term, HLI if minus_hli else frozenset())
    tp, N, K, n, k, p = independent_test(exp, tp, d, genes, bgkind)
    m = pipeline_row(exp, tp, d, setname)
    match = (N == m.background_size and K == m.n_measured_in_background and n == m.n_sig_total
             and k == m.n_sig_in_set and abs(p - m.pvalue) < 1e-9)
    rows.append(dict(kind="fisher", check=label, timepoint=tp, independent=f"N={N} K={K} n={n} k={k} p={p:.4g}",
                     pipeline=f"N={m.background_size} K={m.n_measured_in_background} n={m.n_sig_total} "
                              f"k={int(m.n_sig_in_set)} p={m.pvalue:.4g}; orientation {m.orientation} -> {m.direction_oriented}",
                     match=match))

# 2. Flags: computed here from the thresholds, compared with the pipeline's flag string.
FLAGS = [
    ("10.1128/JB.01097-06_light_stress_green_light_13_umol_med4_microarray", None, "up", "genome"),
    ("10.64898/2026.04.15.718746_extended_light_med4", "16h", "up", "measured"),
    ("10.64898/2026.04.15.718746_extended_darkness_med4", "2h", "up", "measured"),
    ("10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray", "24h", "up", "genome"),
]
for exp, tp, d, bgkind in FLAGS:
    sub, tp = de_at(exp, tp)
    n = int((sub["expression_status"] == STATUS[d]).sum())
    denom = sub["locus_tag"].nunique() if bgkind == "measured" else GENOME_N
    exp_flags = {f for f, on in [("too_few", n < TOO_FEW), ("genome_wide_response", n / denom > GENOME_WIDE)] if on}
    m = pipeline_row(exp, tp, d)
    got = set(str(m["flags"]).split(";")) & {"too_few", "genome_wide_response"}
    rows.append(dict(kind="flag", check=f"{exp.split('_', 1)[1][:45]} {tp} {d}", timepoint=tp,
                     independent=f"n={n} share={n / denom:.3f} -> {sorted(exp_flags) or 'none'}",
                     pipeline=f"{m['flags']}", match=exp_flags == got))

# 3. Per-experiment aggregate, from independently computed per-timepoint p-values.
exp = "10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray"
genes = term_genes("cyanorak.role:K.2")
de_all, _ = _cache[exp], None
ps = []
for tp in sorted(de_all["timepoint"].dropna().unique()):
    sub = de_all[de_all["timepoint"] == tp]
    if (sub["expression_status"] == "significant_down").sum() < TOO_FEW:
        continue
    *_, p = independent_test(exp, tp, "down", genes, "measured")
    ps.append(p)
p_exp = min(1.0, min(ps) * len(ps))
c = CALLS[(CALLS.experiment_id == exp) & (CALLS["set"] == "ribosomal_proteins") & (CALLS.direction == "down")].iloc[0]
rows.append(dict(kind="aggregate", check="N deprivation, ribosomal, down", timepoint="all",
                 independent=f"testable={len(ps)} p_exp={p_exp:.4g}", pipeline=f"{c.timepoint_count} p_exp={c.p_exp_bonferroni:.4g}",
                 match=abs(p_exp - c.p_exp_bonferroni) <= 1e-9 * max(p_exp, 1e-300) + 1e-300))

out = pd.DataFrame(rows)
out.to_csv(OUT, index=False, encoding="utf-8")
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 90)
print(f"MED4 genome (organism record): {GENOME_N}")
print(out.to_string(index=False))
print("ALL MATCH" if out["match"].all() else "MISMATCH FOUND")
