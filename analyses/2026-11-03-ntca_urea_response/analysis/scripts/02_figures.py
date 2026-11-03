"""One figure per strain: genome-wide log2FC per column, ure/urt marks, ntcA highlighted."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
DATA, FIG = HERE / "data", HERE / "figures"
FIG.mkdir(exist_ok=True)
UPC, DNC, MID, INK, MUTED = "#eb6834", "#2a78d6", "#d9d8d4", "#1f1f1e", "#6b6a66"
LABEL = {"med4_urea": "urea", "med4_cyanate": "cyanate", "mit9313_urea": "urea",
         "mit9313_nitrite": "nitrite"}
NTCA = {"MED4": "PMM0246", "MIT9313": "PMT1831"}

plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "svg.fonttype": "none"})

dist = pd.read_csv(DATA / "genome_log2fc_used.csv", encoding="utf-8")
gt = pd.read_csv(DATA / "gene_table.csv", encoding="utf-8")


def save_figure(fig, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")


for strain, ntca in NTCA.items():
    d = dist[dist["strain"] == strain]
    cols = []
    for key in d["experiment_key"].unique():
        sub = d[d["experiment_key"] == key]
        for tp in sub.sort_values("timepoint_order")["timepoint"].unique():
            name = LABEL.get(key, f"N-dep {tp}")
            cols.append((key, tp, name))
    fig, ax = plt.subplots(figsize=(1.0 * len(cols) + 1.6, 4.2))
    rng = np.random.default_rng(0)
    for i, (key, tp, name) in enumerate(cols):
        g = d[(d["experiment_key"] == key) & (d["timepoint"] == tp)]
        v = ax.violinplot(g["log2fc"], positions=[i], widths=0.8, showextrema=False)
        for b in v["bodies"]:
            b.set_facecolor(MID); b.set_edgecolor("none"); b.set_alpha(1)
        p75 = g["log2fc"].abs().quantile(0.75)
        for y in (p75, -p75):
            ax.hlines(y, i - 0.42, i + 0.42, colors=MUTED, linestyles="--", linewidth=1)
        ure = gt[(gt["experiment_key"] == key) & (gt["timepoint"] == tp) & (gt["set"] == "ure_urt")]
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(ure)), ure["log2fc"], s=14, marker="o",
                   facecolor="white", edgecolor=INK, linewidth=0.8, zorder=3,
                   label="ure/urt genes (11)" if i == 0 else None)
        n = gt[(gt["experiment_key"] == key) & (gt["timepoint"] == tp) & (gt["locus_tag"] == ntca)].iloc[0]
        c = UPC if n["log2fc"] > 0 else DNC
        ax.scatter([i], [n["log2fc"]], s=70, color=c, edgecolor="white", linewidth=2, zorder=4)
        ax.annotate(f"{n['log2fc']:+.2f}\n{n['expression_status'].replace('significant_', 'sig. ').replace('not_significant', 'n.s.')}",
                    (i, n["log2fc"]), xytext=(9, 0), textcoords="offset points",
                    va="center", fontsize=7, color=INK)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    if any(k.endswith("ndep") for k, _, _ in cols):
        first_nd = next(i for i, (k, _, _) in enumerate(cols) if k.endswith("ndep"))
        ax.axvline(first_nd - 0.5, color=MUTED, linewidth=0.8)
    ax.set_xticks(range(len(cols)), [c[2] for c in cols])
    ax.set_xlim(-0.6, len(cols) - 0.1)
    ax.set_ylabel("log2FC vs ammonium (N-dep: −N vs +NH4)\n← lower · higher →")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eeeeec", linewidth=0.6); ax.set_axisbelow(True)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="", color=UPC, ms=8, label=f"ntcA ({ntca}), log2FC > 0"),
               Line2D([], [], marker="o", ls="", color=DNC, ms=8, label=f"ntcA ({ntca}), log2FC < 0"),
               Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=5, label="ure/urt genes (11)"),
               Line2D([], [], ls="--", color=MUTED, label="±75th pct of |log2FC|"),
               plt.Rectangle((0, 0), 1, 1, fc=MID, label="all genes (violin)")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False, fontsize=7.5)
    ax.set_title(f"Prochlorococcus {strain} — microarray (Tolonen et al. 2006), n = {d['locus_tag'].nunique()} genes per column",
                 fontsize=9, loc="left", color=INK)
    save_figure(fig, FIG / f"ntca_{strain.lower()}")
    plt.close(fig)
    print("wrote", FIG / f"ntca_{strain.lower()}")
