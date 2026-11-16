"""Compose hli_scoring into per-experiment scoring (no KG access; DE rows are passed in).

score_experiment(...) returns one row per test x target set, with flags, the
main-background Fisher p, the optional in-table sensitivity p, and (optionally)
random-set p-values. The target sets are a parameter; the caller decides which
sets are scored.
"""
from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
import pandas as pd

import hli_scoring as hs

PHOSPHATE = "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray"
# pooled timepoint duplicating day 60 and day 89 (critic finding 2): descriptive, kept out of BH and Bonferroni
POOLED_TIMEPOINTS = {
    ("10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture", "days 60+89"),
}


def test_type_for(exp: Mapping, timepoint: str) -> str:
    if (exp["experiment_id"], timepoint) in POOLED_TIMEPOINTS:
        return "descriptive"
    if exp["experiment_id"] == PHOSPHATE:
        return "approximate" if timepoint == "48h" else "descriptive"
    return exp["test_type"]


def de_qc(de: pd.DataFrame) -> dict:
    """Counts only: duplicated gene rows within a timepoint, genes both up and down."""
    d = de.copy()
    d["timepoint"] = d["timepoint"].fillna(hs.NULL_TIMEPOINT)
    dup = d.duplicated(["timepoint", "locus_tag"], keep=False)
    both = (d[d.expression_status.str.startswith("significant")]
            .groupby(["timepoint", "locus_tag"])["expression_status"].nunique())
    return dict(n_rows=len(d), n_dup_gene_rows=int(dup.sum()), n_genes_up_and_down=int((both > 1).sum()),
                n_null_timepoint_rows=int(de["timepoint"].isna().sum()))


def score_experiment(exp: Mapping, de: pd.DataFrame, genome: Sequence[str],
                     target_sets: Mapping[str, Sequence[str]], fisher_ora, EnrichmentInputs, *,
                     in_table_bg: Sequence[str] | None = None,
                     random_size_set: Sequence[str] | None = None,
                     n_random: int = 0, rng: np.random.Generator | None = None):
    """Score one experiment.

    Returns (tests, random_tests):
      tests: one row per experiment x timepoint x direction x target set.
      random_tests: one row per test x random set (empty if n_random == 0).
    random_size_set: the gene list whose count inside each timepoint's main
      background sets the random-set size (the proposal: the target set).
    """
    eid = exp["experiment_id"]
    grid = hs.build_test_grid(de)
    if grid.empty:
        return pd.DataFrame(), pd.DataFrame()
    grid["test_id"] = [f"{eid}|{tp}|{d}" for tp, d in zip(grid.timepoint, grid.direction)]
    grid["test_type"] = [test_type_for(exp, tp) for tp in grid.timepoint]
    bgs, bg_types = {}, {}
    for r in grid.itertuples():
        bg, kind = hs.main_background(exp["test_type"] if exp["test_type"] != "descriptive" else "sound",
                                      r.measured_genes, genome)
        bgs[r.test_id], bg_types[r.test_id] = bg, kind
    grid["background_type"] = grid.test_id.map(bg_types)
    grid["background_size"] = grid.test_id.map(lambda t: len(bgs[t]))
    grid["flags"] = [hs.test_flags(r.n_sig_total, r.background_size, r.direction,
                                   up_only=bool(exp["up_only"]), test_type=r.test_type)
                     for r in grid.itertuples()]
    grid["testable"] = grid["flags"].map(hs.is_testable)
    # Fisher is run for every test except descriptive / not_testable (too_few tests get a raw p)
    run_ids = [r.test_id for r in grid.itertuples()
               if not ({"descriptive", "not_testable"} & set(r.flags))]
    fis = hs.run_fisher({t: grid.set_index("test_id").at[t, "sig_genes"] for t in run_ids},
                        {t: bgs[t] for t in run_ids}, target_sets, fisher_ora, EnrichmentInputs) \
        if run_ids else pd.DataFrame(columns=["test_id", "set", "count", "bg_count", "pvalue",
                                               "n_sig_in_bg", "background_size"])
    rows = []
    gi = grid.set_index("test_id")
    for t in grid.test_id:
        g = gi.loc[t]
        for s, tags in target_sets.items():
            rows.append(dict(test_id=t, experiment_id=eid, timepoint=g.timepoint,
                             timepoint_order=g.timepoint_order, direction=g.direction, set=s,
                             test_type=g.test_type, background_type=g.background_type,
                             background_size=g.background_size, n_sig_total=g.n_sig_total,
                             n_measured_in_background=len(set(tags) & set(bgs[t])),
                             flags=";".join(g["flags"]), testable=bool(g.testable)))
    out = pd.DataFrame(rows)
    f = fis.rename(columns={"count": "n_sig_in_set"})[["test_id", "set", "n_sig_in_set", "pvalue"]]
    out = out.merge(f, on=["test_id", "set"], how="left")
    out["genome_share_sig"] = out.n_sig_total / out.background_size
    out["set_share_sig"] = out.n_sig_in_set / out.n_measured_in_background.replace(0, np.nan)

    # in-table sensitivity (multi-condition significance tables only)
    if in_table_bg is not None and len(in_table_bg) and run_ids:
        it = hs.run_fisher({t: gi.at[t, "sig_genes"] for t in run_ids}, {t: list(in_table_bg) for t in run_ids},
                           target_sets, fisher_ora, EnrichmentInputs)
        it = it.rename(columns={"pvalue": "pvalue_in_table", "background_size": "in_table_background_size",
                                "bg_count": "n_measured_in_table"})
        out = out.merge(it[["test_id", "set", "pvalue_in_table", "in_table_background_size",
                            "n_measured_in_table"]], on=["test_id", "set"], how="left")
    else:
        out["pvalue_in_table"] = np.nan
        out["in_table_background_size"] = np.nan
        out["n_measured_in_table"] = np.nan

    # random sets: one draw of n_random sets per timepoint, shared by its up and down tests
    rand_rows = []
    if n_random and random_size_set is not None and run_ids:
        for tp, g in grid.groupby("timepoint", sort=False):
            ids = [t for t in g.test_id if t in run_ids]
            if not ids:
                continue
            bg = bgs[ids[0]]
            size = len(set(random_size_set) & set(bg))
            rsets = hs.draw_random_sets(bg, size, n_random, rng)
            if not rsets:
                continue
            rf = hs.run_fisher({t: gi.at[t, "sig_genes"] for t in ids}, {t: bgs[t] for t in ids},
                               rsets, fisher_ora, EnrichmentInputs)
            rf["random_set_size"] = size
            rand_rows.append(rf)
    rand = pd.concat(rand_rows, ignore_index=True) if rand_rows else pd.DataFrame()
    if not rand.empty:
        meta = grid.set_index("test_id")[["timepoint", "direction", "flags", "testable", "n_sig_total"]]
        rand = rand.join(meta, on="test_id")
        rand["experiment_id"] = eid
        rand["flags"] = rand["flags"].map(";".join)
    return out, rand
