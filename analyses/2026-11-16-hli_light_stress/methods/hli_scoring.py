"""Set-level scoring for the hli light/stress analysis (methods milestone).

Small, pure functions (no KG access) so they can be toy-tested:

- parse_light_umol / arm_light_levels : light level of each arm, in umol photons m-2 s-1
- build_test_grid      : DE rows -> one test per experiment x timepoint x direction
- main_background      : background gene list per table type
- test_flags           : too_few / genome_wide_response / not_testable / approximate / descriptive
- orient_direction     : flip up/down where darkness is the treatment
- run_fisher           : the package's fisher_ora over our own gene sets (no hand-rolled Fisher)
- bh                   : Benjamini-Hochberg, applied by us per gene set
- experiment_aggregate : min timepoint p x n testable timepoints (cap 1), BH across experiments
- call_from_padj       : up / down / both / neither
- ortholog_group_counts: a group counts as changed if any member changed
- draw_random_sets     : size-matched random sets from a test's own background (fixed seed)

The target gene set (hli) is a parameter of every scoring function; nothing in
this module knows which set is the target.
"""
from __future__ import annotations

import re
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

MIN_SIG_GENES = 10          # "too few changed genes": fewer than this many significant in a direction
GENOME_WIDE_FRACTION = 0.30  # "genome-wide response": more than this share of measured genes significant
ALPHA = 0.05

# ---------------------------------------------------------------- light levels

_NUM_UNIT = re.compile(
    r"(?P<a>\d+(?:\.\d+)?)\s*(?:-|–|to)?\s*(?P<b>\d+(?:\.\d+)?)?\s*"
    r"(?:umol|µmol|uE|µE|μE|μmol)",
    re.IGNORECASE,
)
_DARK_WORD = re.compile(r"\bdark(ness)?\b", re.IGNORECASE)


def parse_light_umol(text: str | None) -> tuple[float, str]:
    """Parse a light-intensity string to a number (umol photons m-2 s-1).

    Returns (value, note). note is "" for a clean single number, "range_midpoint"
    for "10-25 umol", "bare_number" for a unit-less number such as "0",
    "unparseable" (value NaN) otherwise. "~45 umol" parses to 45.
    """
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return float("nan"), "unparseable"
    s = str(text).strip()
    m = _NUM_UNIT.search(s)
    if m:
        a = float(m.group("a"))
        if m.group("b") is not None:
            return (a + float(m.group("b"))) / 2.0, "range_midpoint"
        return a, ""
    if re.fullmatch(r"~?\s*\d+(?:\.\d+)?", s):
        return float(s.lstrip("~").strip()), "bare_number"
    return float("nan"), "unparseable"


def arm_light_levels(treatment: str, control: str, light_condition: str,
                     light_intensity: str) -> dict:
    """Light level of the treatment and control arms.

    Rules (each arm): a number with a light unit in the arm's own text wins;
    else the word dark/darkness in the arm text means 0; else the experiment's
    light_intensity (0 when light_condition says constant darkness).
    """
    base, base_note = parse_light_umol(light_intensity)
    if re.search(r"constant darkness|complete darkness", str(light_condition or ""), re.I):
        base, base_note = 0.0, "constant_darkness"
    out = {}
    for arm, text in (("treatment", treatment), ("control", control)):
        text = str(text or "")
        m = _NUM_UNIT.search(text)
        if m:
            v, note = parse_light_umol(text)
            src = "arm_text"
        elif _DARK_WORD.search(text):
            v, note, src = 0.0, "", "arm_text_dark"
        else:
            v, note, src = base, base_note, "light_intensity"
        out[f"light_{arm}_umol"] = v
        out[f"light_{arm}_source"] = src
        out[f"light_{arm}_note"] = note
    out["light_parse_flag"] = "unparseable" if any(
        np.isnan(out[f"light_{a}_umol"]) for a in ("treatment", "control")) else ""
    return out


# ---------------------------------------------------------------- test grid

def build_test_grid(de: pd.DataFrame) -> pd.DataFrame:
    """One row per experiment x timepoint x direction.

    de columns: experiment_id, timepoint, timepoint_order, locus_tag, expression_status.
    Null timepoints become "NA". Returns columns experiment_id, timepoint,
    timepoint_order, direction, sig_genes (sorted list), measured_genes (sorted
    list of every gene with a row at that timepoint), n_sig_total, n_rows.
    """
    d = de.copy()
    d["timepoint"] = d["timepoint"].fillna("NA").astype(str)
    d["timepoint_order"] = d["timepoint_order"].fillna(0)
    rows = []
    for (eid, tp), g in d.groupby(["experiment_id", "timepoint"], sort=False):
        measured = sorted(set(g["locus_tag"]))
        order = g["timepoint_order"].iloc[0]
        for direction in ("up", "down"):
            sig = sorted(set(g.loc[g["expression_status"] == f"significant_{direction}", "locus_tag"]))
            rows.append(dict(experiment_id=eid, timepoint=tp, timepoint_order=order,
                             direction=direction, sig_genes=sig, measured_genes=measured,
                             n_sig_total=len(sig), n_rows=len(measured)))
    return pd.DataFrame(rows)


def main_background(table_class: str, measured_genes: Sequence[str],
                    genome: Sequence[str]) -> tuple[list[str], str]:
    """Background for one test.

    full table ('sound')        -> the genes measured at that timepoint ('table_measured')
    significant-only tables     -> the organism's gene list ('genome_assumption'),
                                   because the KG holds no per-platform gene lists
    """
    if table_class == "sound":
        return sorted(set(measured_genes)), "table_measured"
    return sorted(set(genome)), "genome_assumption"


# ---------------------------------------------------------------- flags

def test_flags(n_sig_total: int, background_size: int, direction: str, *,
               up_only: bool, test_type: str,
               min_sig: int = MIN_SIG_GENES,
               max_fraction: float = GENOME_WIDE_FRACTION) -> list[str]:
    """Flags for one test. test_type is 'sound' | 'approximate' | 'descriptive'."""
    flags = []
    if test_type == "descriptive":
        flags.append("descriptive")
    if up_only and direction == "down":
        flags.append("not_testable")
    if "not_testable" not in flags:
        if n_sig_total < min_sig:
            flags.append("too_few")
        if background_size > 0 and n_sig_total / background_size > max_fraction:
            flags.append("genome_wide_response")
    if test_type == "approximate":
        flags.append("approximate")
    return flags


def is_testable(flags: Iterable[str]) -> bool:
    """A test enters BH and the per-experiment aggregate only if none of these flags is set."""
    return not (set(flags) & {"too_few", "not_testable", "descriptive"})


def orient_direction(direction: str, orientation: int) -> str:
    """Oriented direction: orientation -1 (darkness is the treatment) swaps up and down."""
    if orientation not in (1, -1):
        raise ValueError(f"orientation must be +1 or -1, got {orientation}")
    if orientation == 1:
        return direction
    return {"up": "down", "down": "up"}[direction]


# ---------------------------------------------------------------- Fisher via the package

def run_fisher(gene_sets: Mapping[str, Sequence[str]],
               backgrounds: Mapping[str, Sequence[str]],
               target_sets: Mapping[str, Sequence[str]],
               fisher_ora, EnrichmentInputs) -> pd.DataFrame:
    """One-sided Fisher (over-representation) of each target set in each gene set.

    gene_sets   : test_id -> significant genes
    backgrounds : test_id -> background genes
    target_sets : set name -> locus tags (these are the 'terms')
    Returns one row per (test_id, set): count (k), n_sig_in_bg (n), bg_count (M),
    background_size (N), pvalue. A test with no significant genes gets p = 1.
    fisher_ora's own p_adjust (BH across the sets inside one test) is NOT used.
    """
    t2g = pd.DataFrame(
        [(name, name, lt) for name, tags in target_sets.items() for lt in tags],
        columns=["term_id", "term_name", "locus_tag"],
    )
    nonempty = {k: list(v) for k, v in gene_sets.items() if len(set(v) & set(backgrounds[k])) > 0}
    rows = []
    if nonempty:
        inputs = EnrichmentInputs(
            organism_name="custom",
            gene_sets=nonempty,
            background={k: list(backgrounds[k]) for k in nonempty},
            cluster_metadata={k: {} for k in nonempty},
        )
        res = fisher_ora(inputs, t2g, min_gene_set_size=1, max_gene_set_size=None).results
        for r in res.itertuples(index=False):
            rows.append(dict(test_id=r.cluster, set=r.term_id, count=int(r.count),
                             bg_count=int(r.bg_count), pvalue=float(r.pvalue),
                             n_sig_in_bg=int(str(r.gene_ratio).split("/")[1]),
                             background_size=int(str(r.bg_ratio).split("/")[1])))
    out = pd.DataFrame(rows, columns=["test_id", "set", "count", "bg_count", "pvalue",
                                      "n_sig_in_bg", "background_size"])
    # fill (test, set) pairs fisher_ora did not return (empty gene set, or set absent from background)
    have = set(zip(out["test_id"], out["set"]))
    extra = []
    for k in gene_sets:
        bg = set(backgrounds[k])
        for name, tags in target_sets.items():
            if (k, name) not in have:
                extra.append(dict(test_id=k, set=name, count=0,
                                  bg_count=len(bg & set(tags)), pvalue=1.0,
                                  n_sig_in_bg=len(set(gene_sets[k]) & bg),
                                  background_size=len(bg)))
    if extra:
        out = pd.concat([out, pd.DataFrame(extra)], ignore_index=True)
    return out


def bh(pvalues: Sequence[float]) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (NaN entries stay NaN and are not counted)."""
    p = np.asarray(pvalues, dtype=float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    m = ok.sum()
    if m == 0:
        return out
    pv = p[ok]
    order = np.argsort(pv)
    ranked = pv[order] * m / np.arange(1, m + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(m)
    adj[order] = np.minimum(ranked, 1.0)
    out[ok] = adj
    return out


# ---------------------------------------------------------------- per-experiment aggregate

def experiment_aggregate(tests: pd.DataFrame, alpha: float = ALPHA) -> pd.DataFrame:
    """Aggregate per experiment x set x direction.

    tests columns: experiment_id, set, direction, pvalue, padj_bh, testable (bool).
    p_exp = min(pvalue over testable timepoints) x n_testable, capped at 1
    (Bonferroni within the experiment). BH across experiments x directions,
    separately per set. Also "sig at X of Y" timepoint counts (padj_bh < alpha
    over testable timepoints).
    """
    rows = []
    for (eid, s, d), g in tests.groupby(["experiment_id", "set", "direction"], sort=False):
        t = g[g["testable"]]
        n = len(t)
        p_exp = min(1.0, float(t["pvalue"].min()) * n) if n else np.nan
        rows.append(dict(experiment_id=eid, set=s, direction=d, n_timepoints=len(g),
                         n_testable=n, n_sig_timepoints=int((t["padj_bh"] < alpha).sum()),
                         p_exp_bonferroni=p_exp))
    agg = pd.DataFrame(rows)
    agg["padj_exp_bh"] = np.nan
    for s, idx in agg.groupby("set").groups.items():
        agg.loc[idx, "padj_exp_bh"] = bh(agg.loc[idx, "p_exp_bonferroni"].values)
    agg["timepoint_count"] = [f"sig at {a} of {b}" for a, b in zip(agg["n_sig_timepoints"], agg["n_testable"])]
    return agg


def call_from_padj(padj_up: float, padj_down: float, alpha: float = ALPHA) -> str:
    """up / down / both / neither / not_tested (both NaN)."""
    if np.isnan(padj_up) and np.isnan(padj_down):
        return "not_tested"
    up = (not np.isnan(padj_up)) and padj_up < alpha
    down = (not np.isnan(padj_down)) and padj_down < alpha
    return {(True, True): "both", (True, False): "up", (False, True): "down"}.get((up, down), "neither")


# ---------------------------------------------------------------- ortholog groups

def ortholog_group_counts(gene_calls: Mapping[str, str],
                          gene_to_group: Mapping[str, str]) -> dict:
    """Count ortholog groups by their members' calls.

    gene_calls: locus_tag -> 'up' | 'down' | 'ns' | 'not_measured'.
    A group counts as up (down) if any member is up (down); as measured if any
    member is measured. Genes absent from gene_calls are 'not_measured'.
    """
    groups: dict[str, list[str]] = {}
    for lt, grp in gene_to_group.items():
        groups.setdefault(grp, []).append(gene_calls.get(lt, "not_measured"))
    return dict(
        n_groups=len(groups),
        n_groups_measured=sum(any(c != "not_measured" for c in cs) for cs in groups.values()),
        n_groups_up=sum("up" in cs for cs in groups.values()),
        n_groups_down=sum("down" in cs for cs in groups.values()),
    )


# ---------------------------------------------------------------- random sets

def draw_random_sets(background: Sequence[str], size: int, n_sets: int,
                     rng: np.random.Generator, prefix: str = "random") -> dict[str, list[str]]:
    """n_sets random gene sets of `size` genes drawn without replacement from background."""
    bg = np.array(sorted(set(background)))
    if size <= 0 or size > len(bg):
        return {}
    return {f"{prefix}_{i:03d}": sorted(rng.choice(bg, size=size, replace=False).tolist())
            for i in range(n_sets)}
