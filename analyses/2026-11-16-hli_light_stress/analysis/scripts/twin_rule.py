"""Twin rule for identical-signal hli paralog pairs (critic #1; researcher-approved).

Detection: two hli genes form an identical-signal pair if, within one experiment (table), they have identical
log2FC (rounded to 1e-6) in >= MIN_IDENTICAL shared cells (cells where both have a log2FC).
Rule: in a significant-only table, where one member of a detected pair is listed (call_source 'table_row') and the
other is 'absent_from_significant_only_table', the absent twin is recoded as not defined
(call 'not_defined', call_source 'shared_signal_reported_under_twin'). Cells where both are listed or both absent
are not changed. Display/exploration only: the part A CSVs on disk are not altered.
Delta critic fix: the rule is applied in MICROARRAY tables only (omics from methods/data/experiments.csv), where
the pairs share array probes; RNA-seq tables are never recoded. Pair detection is unchanged.
"""
from itertools import combinations

import numpy as np
import pandas as pd

MIN_IDENTICAL = 3
TWIN_SOURCE = "shared_signal_reported_under_twin"
TWIN_CALL = "not_defined"
POOLED = ("10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture", "days 60+89")


def microarray_experiments() -> set:
    from pathlib import Path
    ex = pd.read_csv(Path(__file__).resolve().parents[2] / "methods" / "data" / "experiments.csv", encoding="utf-8")
    assert set(ex.omics) <= {"MICROARRAY", "RNASEQ"}, set(ex.omics)
    return set(ex[ex.omics == "MICROARRAY"].experiment_id)


MICROARRAY = microarray_experiments()


def detect_pairs(gc: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (pairs, per_experiment): pairs with >= MIN_IDENTICAL identical shared cells in one experiment;
    per_experiment = identical / differing shared-cell counts per pair x experiment."""
    d = gc[~((gc.experiment_id == POOLED[0]) & (gc.timepoint == POOLED[1]))]
    d = d[d.log2fc.notna()].copy()
    d["lf"] = d.log2fc.round(6)
    piv = d.pivot_table(index=["experiment_id", "timepoint"], columns="locus_tag", values="lf", aggfunc="first")
    exps = piv.index.get_level_values(0)
    rows = []
    for a, b in combinations(sorted(piv.columns), 2):
        both = piv[[a, b]].dropna()
        if both.empty:
            continue
        same = (both[a] == both[b])
        for e in sorted(set(both.index.get_level_values(0))):
            m = both.index.get_level_values(0) == e
            rows.append(dict(gene_a=a, gene_b=b, experiment_id=e, n_shared=int(m.sum()), n_identical=int(same[m].sum()),
                             n_differ=int((~same[m]).sum())))
    per = pd.DataFrame(rows)
    q = per.groupby(["gene_a", "gene_b"]).n_identical.max()
    keep = q[q >= MIN_IDENTICAL].index
    per = per.set_index(["gene_a", "gene_b"]).loc[keep].reset_index()
    pairs = (per.groupby(["gene_a", "gene_b"]).agg(n_shared=("n_shared", "sum"), n_identical=("n_identical", "sum"),
                                                   n_differ=("n_differ", "sum")).reset_index())
    lab = gc.drop_duplicates("experiment_id").set_index("experiment_id").label
    per["label"] = per.experiment_id.map(lab)
    pairs["experiments_identical"] = [" | ".join(f"{r.label} ({r.n_identical}/{r.n_shared})" for r in
                                                 per[(per.gene_a == a) & (per.gene_b == b) & (per.n_identical > 0)].itertuples())
                                      for a, b in zip(pairs.gene_a, pairs.gene_b)]
    pairs["experiments_differ"] = [" | ".join(f"{r.label} ({r.n_differ}/{r.n_shared})" for r in
                                              per[(per.gene_a == a) & (per.gene_b == b) & (per.n_differ > 0)].itertuples())
                                   for a, b in zip(pairs.gene_a, pairs.gene_b)]
    del exps
    return pairs, per


def apply(gc: pd.DataFrame, pairs: pd.DataFrame) -> pd.DataFrame:
    """Recode absent twins (see module doc). Returns a copy with an added column 'twin_recoded' (bool)."""
    d = gc.copy()
    d["twin_recoded"] = False
    idx = d.set_index(["experiment_id", "timepoint", "locus_tag"]).index
    pos = {k: i for i, k in enumerate(idx)}
    src = d.call_source.values
    for a, b in zip(pairs.gene_a, pairs.gene_b):
        for (e, tp) in d[["experiment_id", "timepoint"]].drop_duplicates().itertuples(index=False):
            if e not in MICROARRAY:   # delta critic: microarray tables only
                continue
            ia, ib = pos.get((e, tp, a)), pos.get((e, tp, b))
            if ia is None or ib is None:
                continue
            sa, sb = src[ia], src[ib]
            for listed, absent in ((ia, ib), (ib, ia)):
                if src[listed] == "table_row" and src[absent] == "absent_from_significant_only_table":
                    d.iat[absent, d.columns.get_loc("call")] = TWIN_CALL
                    d.iat[absent, d.columns.get_loc("call_source")] = TWIN_SOURCE
                    d.iat[absent, d.columns.get_loc("twin_recoded")] = True
            del sa, sb
    return d


def load(data_dir) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Pairs detected from analysis/data/hli_gene_calls.csv (cached in explore_twin_pairs.csv)."""
    gc = pd.read_csv(data_dir / "hli_gene_calls.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    pairs, per = detect_pairs(gc)
    return pairs, per


def recode_gene_calls(gc: pd.DataFrame) -> pd.DataFrame:
    """Detect identical-signal pairs in gc and apply the twin rule (one call for the A, D and timing displays)."""
    pairs, _ = detect_pairs(gc)
    return apply(gc, pairs)
