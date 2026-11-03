"""ntcA-on-urea methods module: DE extraction + the proposal's decision rules.

All thresholds are those fixed in ../proposal.md (approved plan).
"""
from __future__ import annotations

import pandas as pd

UP, DOWN, NS = "significant_up", "significant_down", "not_significant"
KEEP = ["locus_tag", "gene_name", "product", "experiment_id", "timepoint",
        "timepoint_order", "log2fc", "padj", "expression_status"]
PAGE = 5000


def fetch_de(experiment_ids, locus_tags=None, conn=None) -> pd.DataFrame:
    """All DE rows for the experiments (optionally a locus-tag subset).

    Pages explicitly and asserts the row count equals ``total_matching``.
    """
    from multiomics_explorer import differential_expression_by_gene, to_dataframe

    frames, offset, total = [], 0, None
    while True:
        r = differential_expression_by_gene(
            experiment_ids=list(experiment_ids), locus_tags=locus_tags,
            verbose=True, limit=PAGE, offset=offset, conn=conn)  # product needs verbose
        total = r["total_matching"]
        if r["results"]:
            frames.append(to_dataframe(r))
        offset += len(r["results"])
        if not r["truncated"] or not r["results"] or offset >= total:
            break
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=KEEP)
    if len(df) != total:
        raise RuntimeError(f"paging lost rows: {len(df)} fetched vs total_matching {total}")
    if df.duplicated(["experiment_id", "timepoint", "locus_tag"]).any():
        raise RuntimeError("duplicate (experiment, timepoint, locus_tag) rows after paging")
    return df[KEEP].copy()


def add_abs_rank_pct(df: pd.DataFrame) -> pd.DataFrame:
    """Percentile (0-100] of |log2FC| within each (experiment_id, timepoint)."""
    out = df.copy()
    out["abs_rank_pct"] = (out["log2fc"].abs()
                           .groupby([out["experiment_id"], out["timepoint"]])
                           .rank(pct=True, method="max") * 100)
    return out


def positive_control(df_strain_exp: pd.DataFrame, urea_tags) -> dict:
    """ure/urt control: >=2 significant_up, OR median log2FC >= 0.5 AND >=75% log2FC > 0."""
    sub = df_strain_exp[df_strain_exp["locus_tag"].isin(urea_tags)]
    n_up = int((sub["expression_status"] == UP).sum())
    med = float(sub["log2fc"].median()) if len(sub) else float("nan")
    frac_pos = float((sub["log2fc"] > 0).mean()) if len(sub) else 0.0
    passed = bool(n_up >= 2 or (med >= 0.5 and frac_pos >= 0.75))
    return dict(n_genes=len(sub), n_sig_up=n_up, median_log2fc=med,
                frac_pos=frac_pos, passed=passed)


def growth_rate_check(df_exp: pd.DataFrame) -> dict:
    """Ribosomal-protein genes: flag if |median_ribo - median_genome| > 0.3 OR >10% significant."""
    ribo = df_exp[df_exp["product"].fillna("").str.contains("ribosomal protein", case=False)]
    med_g = float(df_exp["log2fc"].median())
    med_r = float(ribo["log2fc"].median()) if len(ribo) else float("nan")
    frac_sig = float(ribo["expression_status"].isin([UP, DOWN]).mean()) if len(ribo) else 0.0
    flag = bool(abs(med_r - med_g) > 0.3 or frac_sig > 0.10)
    return dict(n_ribo=len(ribo), median_ribo=med_r, median_genome=med_g,
                frac_sig=frac_sig, flag=flag)


def detectability(df_ndep: pd.DataFrame, ntca_tag: str, timepoints) -> dict:
    """Pass if at any listed timepoint ntcA is significant_up OR (log2FC>0 AND pct >= 75).

    ``df_ndep`` must already carry ``abs_rank_pct`` (computed genome-wide).
    """
    sub = df_ndep[(df_ndep["locus_tag"] == ntca_tag) & df_ndep["timepoint"].isin(timepoints)]
    hits = sub[(sub["expression_status"] == UP)
               | ((sub["log2fc"] > 0) & (sub["abs_rank_pct"] >= 75))]
    return dict(n_timepoints=len(sub), passing_timepoints=list(hits["timepoint"]),
                passed=bool(len(hits) > 0))


def classify_ntca(row) -> str:
    """Decision table: up / down / suggestive / not_changed."""
    if row["expression_status"] == UP:
        return "up"
    if row["expression_status"] == DOWN:
        return "down"
    return "suggestive" if row["abs_rank_pct"] >= 75 else "not_changed"


def final_reading(classification: str, control_passed: bool, detectability_passed: bool) -> str:
    """'uninterpretable' if the control fails, or detectability fails on a not_changed call."""
    if not control_passed:
        return "uninterpretable"
    if not detectability_passed and classification == "not_changed":
        return "uninterpretable"
    return classification


def identity_gate(df_a: pd.DataFrame, df_b: pd.DataFrame) -> bool:
    """True (fires) if log2FC and expression_status are identical on every shared locus tag."""
    cols = ["locus_tag", "log2fc", "expression_status"]
    j = df_a[cols].merge(df_b[cols], on="locus_tag", suffixes=("_a", "_b"))
    if j.empty:
        return False
    return bool((j["log2fc_a"] == j["log2fc_b"]).all()
                and (j["expression_status_a"] == j["expression_status_b"]).all())
