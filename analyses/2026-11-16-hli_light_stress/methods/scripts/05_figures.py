"""Methods step 6: comparison-set heatmaps (static PNG + SVG).

(a) rows = comparison set x oriented direction, columns = experiment x timepoint grouped by
    experiment group; (b) the same columns ordered by the treatment arm's light level.
Cell = -log10(BH padj), signed: up rows positive (orange), down rows negative (blue).
Direction is ORIENTED: for the three darkness-treatment experiments, up/down are swapped
so that "up" reads "higher with more light"; those columns carry a "(flipped)" label.
Flagged cells: too few significant genes = hatched, no value; not testable / descriptive =
gray "n/a"; genome-wide response (>30%) = small black dot.

Reads methods/data/control_tests.csv. Writes methods/figures/controls_heatmap_by_group.{png,svg}
and methods/figures/controls_heatmap_by_light.{png,svg}.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/05_figures.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

METHODS = Path(__file__).resolve().parents[1]
DATA, FIG = METHODS / "data", METHODS / "figures"
FIG.mkdir(exist_ok=True)

UP, DOWN, MID = "#eb6834", "#2a78d6", "#f0efec"
CMAP = LinearSegmentedColormap.from_list("spock_diverging", [DOWN, MID, UP])
INK, MUTED, GRID = "#1f1f1d", "#6b6b66", "#d9d8d4"
GROUP_ORDER = ["light_onset_photoperiod", "electron_transport_DCMU", "phage_dark", "nonlight_stress",
               "nonstress_possible_relief"]
GROUP_LABEL = {"light_onset_photoperiod": "Light onset / photoperiod", "electron_transport_DCMU": "DCMU",
               "phage_dark": "Phage, dark", "nonlight_stress": "Non-light stress",
               "nonstress_possible_relief": "Non-stress / possible relief"}
SETS = [("chaperones", "Chaperones"), ("oxidative_stress", "Oxidative stress"), ("photosystem_II", "Photosystem II")]


def save_figure(fig, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")


def build_columns(t: pd.DataFrame) -> pd.DataFrame:
    cols = (t[["experiment_id", "label", "group", "timepoint", "timepoint_order", "orientation",
               "light_treatment_umol", "light_control_umol"]].drop_duplicates(["experiment_id", "timepoint"]))
    cols["group_rank"] = cols.group.map({g: i for i, g in enumerate(GROUP_ORDER)})
    cols["col_label"] = [f"{lab} · {tp}" + (" (flipped)" if o == -1 else "")
                         for lab, tp, o in zip(cols.label, cols.timepoint, cols.orientation)]
    return cols


def draw(t: pd.DataFrame, cols: pd.DataFrame, stem: Path, title: str, block_col: str, block_label) -> None:
    rows = [(s, d) for s, _ in SETS for d in ("up", "down")]
    n_r, n_c = len(rows), len(cols)
    val = np.full((n_r, n_c), np.nan)
    state = np.full((n_r, n_c), "", dtype=object)
    gw = np.zeros((n_r, n_c), dtype=bool)
    idx = t.set_index(["experiment_id", "timepoint", "set", "direction_oriented"])
    for j, c in enumerate(cols.itertuples()):
        for i, (s, d) in enumerate(rows):
            r = idx.loc[(c.experiment_id, c.timepoint, s, d)]
            fl = str(r["flags"]) if pd.notna(r["flags"]) else ""
            if "not_testable" in fl or "descriptive" in fl:
                state[i, j] = "na"
            elif "too_few" in fl:
                state[i, j] = "few"
            else:
                v = -np.log10(max(r["padj_bh"], 1e-300))
                val[i, j] = v if d == "up" else -v
            gw[i, j] = "genome_wide_response" in fl
    lim = max(2.0, np.nanmax(np.abs(val)))
    norm = TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)

    fig_w = max(10, 0.2 * n_c + 3.2)
    fig, ax = plt.subplots(figsize=(fig_w, 6.4))
    for i in range(n_r):
        for j in range(n_c):
            x, y = j, i
            if state[i, j] == "na":
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor="#e4e3df", edgecolor="white", lw=0.8))
                ax.text(x + 0.5, y + 0.5, "n/a", ha="center", va="center", fontsize=3.6, color=MUTED)
            elif state[i, j] == "few":
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor="white", edgecolor="white", lw=0.8))
                ax.add_patch(Rectangle((x + 0.06, y + 0.06), 0.88, 0.88, facecolor="none",
                                       edgecolor="#b5b4ae", hatch="////", lw=0))
            else:
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor=CMAP(norm(val[i, j])), edgecolor="white", lw=0.8))
                if abs(val[i, j]) > -np.log10(0.05):
                    ax.text(x + 0.5, y + 0.5, "*", ha="center", va="center", fontsize=6, color=INK)
            if gw[i, j]:
                ax.plot(x + 0.85, y + 0.18, marker="o", ms=1.6, color=INK)
    ax.set_xlim(0, n_c)
    ax.set_ylim(n_r, 0)
    ax.set_yticks(np.arange(n_r) + 0.5)
    ax.set_yticklabels([f"{dict(SETS)[s]} — {'up' if d == 'up' else 'down'}" for s, d in rows], fontsize=7, color=INK)
    ax.set_xticks(np.arange(n_c) + 0.5)
    ax.set_xticklabels(cols.col_label, rotation=90, fontsize=5.2, color=INK)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    for k in (2, 4):
        ax.axhline(k, color=INK, lw=0.8)
    # blocks
    blocks = cols[block_col].tolist()
    start = 0
    for j in range(1, n_c + 1):
        if j == n_c or blocks[j] != blocks[start]:
            if j < n_c:
                ax.axvline(j, color=INK, lw=0.9)
            lab = block_label(blocks[start])
            if (j - start) <= 6:
                lab = lab.replace(", ", "\n").replace(" ", "\n")
            ax.text((start + j) / 2, -0.25, lab, ha="center", va="bottom", fontsize=6.2, color=INK)
            start = j
    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
    cb = fig.colorbar(sm, ax=ax, fraction=0.015, pad=0.01)
    cb.set_label("signed −log10(BH padj)\n← down (blue) · up (orange) →", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    ax.set_title(title, fontsize=9, color=INK, loc="left", pad=40)
    ax.text(0, -0.62,
             "Hatched = fewer than 10 genes significant in that direction (no test reported). "
             "n/a = not testable (up-only table) or descriptive table.\n• = more than 30% of measured genes "
             "significant in that direction. * = BH padj < 0.05 (BH per gene set across all testable tests). "
             "(flipped) = darkness is the treatment; up/down swapped so up = higher with more light.",
             fontsize=6, color=MUTED, transform=ax.transAxes, va="top")
    save_figure(fig, stem)
    plt.close(fig)


def main():
    t = pd.read_csv(DATA / "control_tests.csv", encoding="utf-8")
    t = t[t.set.isin([s for s, _ in SETS])]
    cols = build_columns(t)
    a = cols.sort_values(["group_rank", "label", "timepoint_order"])
    draw(t, a, FIG / "controls_heatmap_by_group",
         f"Comparison gene sets across {a.experiment_id.nunique()} MED4 transcript experiments "
         f"({len(a)} experiment × timepoints), grouped by experiment group", "group",
         lambda g: GROUP_LABEL[g])
    b = cols.sort_values(["light_treatment_umol", "light_control_umol", "group_rank", "label", "timepoint_order"])
    b["light_block"] = [f"{tr:g}" for tr in b.light_treatment_umol]
    draw(t, b, FIG / "controls_heatmap_by_light",
         "Comparison gene sets, columns ordered by the treatment arm's light level "
         "(µmol photons m⁻² s⁻¹; block label = treatment-arm level)", "light_block",
         lambda v: f"{v}")
    print("figures written:", sorted(p.name for p in FIG.iterdir()))


if __name__ == "__main__":
    main()
