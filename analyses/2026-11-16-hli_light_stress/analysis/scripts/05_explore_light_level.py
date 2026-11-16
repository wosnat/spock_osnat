"""Exploration B: background light level vs hli (and ribosomal proteins) test results.

Tests of experiments with no light-reading role (light_reading_group == 'none': the non-light stress
and non-stress experiments, both arms at the same light). x = light_treatment_umol (= control arm).
y = signed -log10(p): BH padj for testable tests (up +, down -); for too-few tests the raw p is shown
with open markers; not-testable and descriptive tests have no p and sit at y = 0 as crosses.
Also the gene-level share of measured set genes significant (n_sig_in_set / n_measured_in_background).
Spearman per set x direction over testable tests, on unsigned -log10 BH padj and on the share. Cross-study: platform, design and stress differ
between experiments, so this is confounded and descriptive only.

Writes analysis/data/explore_light_level.csv, explore_light_level_spearman.csv and
analysis/figures/explore_B1_light_level.{png,svg}.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/05_explore_light_level.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
UP, DOWN, INK, MUTED = "#eb6834", "#2a78d6", "#1f1f1d", "#6b6b66"
SETS = [("hli", "hli (23 genes)"), ("ribosomal_proteins", "Ribosomal proteins (K.2)")]


def main():
    t = pd.read_csv(DATA / "hli_tests.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    t = t[(t.light_reading_group == "none") & t.set.isin([s for s, _ in SETS])].copy()
    t["flags"] = t["flags"].fillna("")
    t["status"] = np.select(
        [t["flags"].str.contains("not_testable|descriptive"), t["flags"].str.contains("too_few"),
         t["flags"].str.contains("genome_wide")], ["no_test", "too_few", "testable_genome_wide"], "testable")
    sign = np.where(t.direction == "up", 1, -1)
    t["y_signed_log10"] = np.where(t.testable, sign * -np.log10(t.padj_bh.clip(lower=1e-300)),
                                   np.where(t.status == "too_few", sign * -np.log10(t.pvalue.clip(lower=1e-300)), 0.0))
    t["y_source"] = np.where(t.testable, "BH padj", np.where(t.status == "too_few", "raw p (too few)", "none"))
    t["share_sig_in_set"] = t.n_sig_in_set / t.n_measured_in_background
    out = t[["set", "experiment_id", "label", "group", "stress_type", "study", "omics", "timepoint", "direction",
             "light_treatment_umol", "light_control_umol", "test_type", "flags", "status", "testable", "pvalue",
             "padj_bh", "y_signed_log10", "y_source", "n_sig_in_set", "n_measured_in_background", "share_sig_in_set"]]
    out.to_csv(DATA / "explore_light_level.csv", index=False, encoding="utf-8")

    sp = []
    for s, _ in SETS:
        for d in ("up", "down"):
            g = out[(out.set == s) & (out.direction == d) & out.testable]
            g = g.assign(y_abs=g.y_signed_log10.abs())   # unsigned within a direction: larger = stronger
            for ycol, lab in (("y_abs", "-log10 BH padj (unsigned, within direction)"),
                              ("share_sig_in_set", "share of set significant")):
                rho, p = spearmanr(g.light_treatment_umol, g[ycol]) if len(g) > 2 else (np.nan, np.nan)
                sp.append(dict(set=s, direction=d, y=lab, n_tests=len(g), n_experiments=g.experiment_id.nunique(),
                               n_distinct_light_levels=g.light_treatment_umol.nunique(), spearman_rho=rho,
                               p_value=p, note="cross-study; platform, design and stress confounded"))
    sp = pd.DataFrame(sp)
    sp.to_csv(DATA / "explore_light_level_spearman.csv", index=False, encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    rng = np.random.default_rng(1)
    for ax, (s, lab) in zip(axes, SETS):
        g = out[out.set == s]
        for d, col in (("up", UP), ("down", DOWN)):
            gd = g[g.direction == d]
            x = gd.light_treatment_umol + rng.uniform(-0.9, 0.9, len(gd))
            m = gd.status.isin(["testable", "testable_genome_wide"])
            ax.scatter(x[m & (gd.status == "testable")], gd.y_signed_log10[m & (gd.status == "testable")], s=26,
                       color=col, edgecolor="white", lw=0.6, zorder=3)
            ax.scatter(x[gd.status == "testable_genome_wide"], gd.y_signed_log10[gd.status == "testable_genome_wide"],
                       s=34, marker="D", color=col, edgecolor=INK, lw=0.6, zorder=3)
            ax.scatter(x[gd.status == "too_few"], gd.y_signed_log10[gd.status == "too_few"], s=26, facecolor="none",
                       edgecolor=col, lw=1, zorder=2)
            ax.scatter(x[gd.status == "no_test"], gd.y_signed_log10[gd.status == "no_test"], s=18, marker="x",
                       color=MUTED, lw=0.8, zorder=2)
        for yv in (-np.log10(0.05), np.log10(0.05)):
            ax.axhline(yv, color=MUTED, lw=0.6, ls=":")
        ax.axhline(0, color=INK, lw=0.6)
        r = sp[(sp.set == s) & (sp.y.str.startswith("-log10"))].set_index("direction")
        ax.set_title(f"{lab}\nSpearman, light vs −log10 padj (testable): up ρ={r.at['up', 'spearman_rho']:.2f} (n={r.at['up', 'n_tests']}), "
                     f"down ρ={r.at['down', 'spearman_rho']:.2f} (n={r.at['down', 'n_tests']})", fontsize=8.5, loc="left")
        ax.set_xlabel("light level, µmol photons m⁻² s⁻¹ (both arms)", fontsize=8)
        ax.tick_params(labelsize=7)
        for spn in ("top", "right"):
            ax.spines[spn].set_visible(False)
    axes[0].set_ylabel("signed −log10(BH padj)\n← significant down · significant up →", fontsize=8)
    axes[1].legend(handles=[Line2D([], [], marker="o", ls="", color=UP, label="up, testable"),
                            Line2D([], [], marker="o", ls="", color=DOWN, label="down, testable"),
                            Line2D([], [], marker="D", ls="", color=MUTED, markeredgecolor=INK,
                                   label="testable, genome-wide flag"),
                            Line2D([], [], marker="o", ls="", markerfacecolor="none", markeredgecolor=MUTED,
                                   label="too few significant genes (raw p)"),
                            Line2D([], [], marker="x", ls="", color=MUTED, label="not testable / descriptive (y=0)")],
                   fontsize=6.5, frameon=False, loc="upper right")
    fig.suptitle("Light level vs set-level result, non-light stress and non-stress experiments (18 experiments, MED4)",
                 fontsize=9.5, x=0.01, y=1.06, ha="left")
    fig.text(0.01, -0.04, "Cross-study comparison: light level is confounded with platform, design and stress type. "
             "x jittered ±0.9 for visibility. Dotted lines: padj = 0.05. Treatment vs control (no flip).",
             fontsize=6.5, color=MUTED)
    fig.savefig(FIG / "explore_B1_light_level.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / "explore_B1_light_level.svg", bbox_inches="tight")
    plt.close(fig)
    pd.set_option("display.width", 220)
    print(sp.to_string(index=False))


if __name__ == "__main__":
    main()
