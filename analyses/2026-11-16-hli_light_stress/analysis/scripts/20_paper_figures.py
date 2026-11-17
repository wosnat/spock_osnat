"""Paper figures (fixed 7.2 in width, text >= 8 pt): figures/paper_fig1..4 and paper_figS1 (PNG 300 dpi + SVG).

Only existing analysis data files are read; no test is recomputed. Exploration inputs already carry the twin rule
(microarray tables only), the A.8 drop of Coculture HOT1A3 (2016) and the A.3-A.6 display overrides. Part A test
tables (hli_tests.csv, experiment_calls.csv) are read with display_overrides.apply + drop.

One colour scheme: orange #eb6834 = up, blue #2a78d6 = down; sequential ramps mid-grey -> orange (% up) and
mid-grey -> blue (% down); family colours (d_scheme.FAMILY_ANCHOR) only in header strips / label patches;
conservation tiers = the 4 greys of conservation.py; clusters in ink.

Writes figures/paper_fig1, paper_fig2, paper_fig3, paper_fig4, paper_figS1 (.png, .svg);
data/paper_fig_source_fig1a.csv, _fig1b, _fig2, _fig3a, _fig3b, _fig4, _figS1.csv, data/paper_figS1_column_key.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/20_paper_figures.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.text import Text  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import conservation as cons  # noqa: E402
import d_scheme as ds  # noqa: E402
import display_overrides as dov  # noqa: E402

DATA, FIG = HERE.parent / "data", HERE.parent / "figures"
METHODS = HERE.parents[1] / "methods" / "data"
UP, DOWN, MID, INK, MUTED, NSG = "#eb6834", "#2a78d6", "#f0efec", "#1f1f1d", "#6b6b66", "#b5b4ae"
FAM = ds.FAMILY_ANCHOR
UPMAP = LinearSegmentedColormap.from_list("up", [MID, UP])
DNMAP = LinearSegmentedColormap.from_list("down", [MID, DOWN])
W = 7.2
plt.rcParams.update({"font.size": 8, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
                     "font.family": "DejaVu Sans", "svg.fonttype": "none", "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6})
FONT_LOG = {}

# scopes (Fig 1a rows, Fig 3a columns): d_scheme type -> scope
SCOPES = [("Light onset", "light / dark", "Light\nonset"), ("Schedule ext.", "light / dark", "Sched.\next."),
          ("Const. dark/light", "light / dark", "Dark/\nlight"), ("CO2", "stress", "CO2"), ("Iron", "stress", "Iron"),
          ("Nitrogen", "stress", "N"), ("Phosphorus", "stress", "P"), ("Salt", "stress", "Salt"),
          ("Phage (light)", "stress", "Phage\nlight"), ("Phage (dark)", "light / dark", "Phage\ndark"),
          ("Relief", "non-stress", "Relief"), ("N source", "non-stress", "N\nsource"),
          ("Coculture d11", "non-stress", "Cocult\nd11")]
TYPE_SCOPE = {"light onset": "Light onset", "schedule extension": "Schedule ext.", "constant dark vs light": "Const. dark/light",
              "carbon (CO2)": "CO2", "iron": "Iron", "nitrogen": "Nitrogen", "phosphorus": "Phosphorus", "salt": "Salt",
              "phage": "Phage (light)", "phage in the dark": "Phage (dark)", "iron re-added": "Relief", "air vs time 0": "Relief",
              "alternative N source": "N source", "coculture, both exponential": "Coculture d11"}
# not in any scope: DCMU (no testable test), "N stress, control side" (coculture 2025 day 18)
SETS = [("hli", "hli"), ("ribosomal_proteins", "Ribosomal"), ("photosystem_I", "PSI"), ("photosystem_II", "PSII"),
        ("co2_fixation", "CO2 fixation")]
EXP_SHORT = {
    "Blue 13 vs dark": "Blue light 13", "Green 13 vs dark": "Green light 13", "High white 55 vs dark": "White light 55",
    "Red 13 vs dark": "Red light 13", "White 13 vs dark": "White light 13", "Extended darkness": "Extended dark",
    "Extended light": "Extended light", "Const dark vs light (no phage)": "Dark vs light",
    "Const dark vs light (phage)": "Dark vs light, phage", "Phage lysate (dark)": "Phage lysate, dark",
    "CO2: low": "Low CO2", "CO2: low, no O2": "Low CO2, no O2", "CO2: ambient, no O2": "Ambient CO2, no O2",
    "Iron starvation": "Iron starvation", "N deprivation (array)": "N deprivation (array)",
    "N starvation lowN (axenic)": "lowN, axenic", "N starvation lowN (coculture)": "lowN, coculture",
    "N-depleted (RNA-seq, top 50%)": "N-depleted (RNA-seq)", "Phosphate starvation": "P starvation",
    "Low salinity 28 psu": "Low salinity", "Phage infection (array, up-only)": "Phage infection, array",
    "Phage lysate (light)": "Phage lysate, light", "Air vs time 0": "Air vs time 0", "Iron re-added": "Iron re-added",
    "Cyanate as N source": "Cyanate", "Urea as N source": "Urea", "Coculture HOT1A3 vs axenic (2025)": "Coculture 2025",
    "DCMU + white 13 vs white 13": "DCMU"}
assert all(len(v) <= 22 for v in EXP_SHORT.values())


def rd(name):
    return pd.read_csv(DATA / name, encoding="utf-8", keep_default_na=False, na_values=[""])


def axin(fig, l, b, w, h, H):
    return fig.add_axes([l / W, b / H, w / W, h / H])


def letter(fig, x, y, s, H):
    fig.text(x / W, 1 - y / H, s, fontsize=11, fontweight="bold", va="top", ha="left")


def min_font(fig):
    sizes = [t.get_fontsize() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()]
    return min(sizes)


def save(fig, stem):
    mf = min_font(fig)
    assert mf >= 8, (stem, mf)
    assert abs(fig.get_figwidth() - W) < 1e-6
    FONT_LOG[stem] = (mf, round(fig.get_figheight(), 2))
    fig.savefig(FIG / f"{stem}.png", dpi=300)
    fig.savefig(FIG / f"{stem}.svg")
    plt.close(fig)


def clean(ax, keep=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)


def tests():
    t = dov.drop(dov.apply(rd("hli_tests.csv")))
    t["type"] = [ds.category(r)[1] for r in t.to_dict("records")]
    t["scope"] = t.type.map(TYPE_SCOPE)
    t["testable"] = t.testable.astype(str) == "True"
    return t


# ------------------------------------------------------------------ Fig 1
def fig1():
    t = tests()
    rows = []
    for sc, fam, _ in SCOPES:
        for s, slab in SETS:
            for d in ("up", "down"):
                g = t[(t.scope == sc) & (t.set == s) & (t.direction == d) & t.testable]
                rows.append(dict(scope=sc, family=fam, set=s, set_label=slab, direction=d, n_testable=len(g),
                                 n_sig=int((g.padj_bh < 0.05).sum()), n_experiments=g.experiment_id.nunique(),
                                 n_tests_all=int(((t.scope == sc) & (t.set == s) & (t.direction == d)).sum())))
    a = pd.DataFrame(rows)
    a.to_csv(DATA / "paper_fig_source_fig1a.csv", index=False, encoding="utf-8")

    c = dov.drop(dov.apply(rd("experiment_calls.csv")))
    c = c[c.set == "hli"]
    first = t.drop_duplicates("experiment_id").set_index("experiment_id")
    eb = []
    for e, g in c.groupby("experiment_id"):
        call = g.experiment_call.iloc[0]
        if call == "not_tested":
            continue
        gi = g.set_index("direction")
        lab = g.label.iloc[0]
        if e == dov.COCULT25:
            sc, short = "Coculture d11", "Coculture 2025 d11+d18"
        else:
            sc, short = first.at[e, "scope"], EXP_SHORT[lab]
        eb.append(dict(experiment_id=e, label=lab, short=short, scope=sc, experiment_call=call,
                       padj_up=gi.at["up", "padj_exp_bh"], padj_down=gi.at["down", "padj_exp_bh"]))
    b = pd.DataFrame(eb)
    order = {s: i for i, (s, _, _) in enumerate(SCOPES)}
    b["o"] = b.scope.map(order)
    b = b.sort_values(["o", "short"]).drop(columns="o").reset_index(drop=True)
    CAP = 12
    b["x_up"] = np.minimum(-np.log10(b.padj_up.clip(lower=1e-300)), CAP)
    b["x_down"] = -np.minimum(-np.log10(b.padj_down.clip(lower=1e-300)), CAP)
    b["capped_up"] = b.padj_up < 10 ** -CAP
    b["capped_down"] = b.padj_down < 10 ** -CAP
    b.to_csv(DATA / "paper_fig_source_fig1b.csv", index=False, encoding="utf-8")

    nr_a, nr_b = len(SCOPES), len(b)
    rh_a, rh_b = 0.21, 0.165
    top_a = 0.55
    ha = top_a + nr_a * rh_a + 0.15
    hb = nr_b * rh_b + 1.15
    H = ha + hb + 0.2
    assert H <= 9, H
    fig = plt.figure(figsize=(W, H))
    # ---- a: scopes x sets, split cell up | down
    gl, gw = 1.75, 5.25
    ax = axin(fig, gl, H - ha + 0.15, gw, nr_a * rh_a, H)
    ncol = len(SETS)
    for i, (sc, fam, _) in enumerate(SCOPES):
        for j, (s, slab) in enumerate(SETS):
            for k, (d, cmap) in enumerate((("up", UPMAP), ("down", DNMAP))):
                r = a[(a.scope == sc) & (a.set == s) & (a.direction == d)].iloc[0]
                x0 = j + 0.5 * k
                if r.n_testable == 0:
                    ax.add_patch(Rectangle((x0 + 0.02, i + 0.06), 0.46, 0.88, facecolor="white", edgecolor="#d9d8d4",
                                           hatch="////", lw=0.4))
                    continue
                f = r.n_sig / r.n_testable
                ax.add_patch(Rectangle((x0 + 0.02, i + 0.06), 0.46, 0.88, facecolor=cmap(f), edgecolor="none"))
                ax.text(x0 + 0.25, i + 0.52, f"{r.n_sig}/{r.n_testable}", ha="center", va="center", fontsize=8,
                        color="white" if f > 0.6 else INK)
        ax.add_patch(Rectangle((-0.024, i + 0.14), 0.013, 0.72, facecolor=FAM[fam], clip_on=False,
                               transform=ax.get_yaxis_transform()))
    ax.set_xlim(0, ncol)
    ax.set_ylim(nr_a, 0)
    ax.set_yticks(np.arange(nr_a) + 0.5)
    ax.set_yticklabels([s for s, _, _ in SCOPES])
    ax.tick_params(axis="y", length=0, pad=11)
    ax.set_xticks(np.arange(ncol) + 0.5)
    ax.set_xticklabels([l for _, l in SETS])
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=12)
    for j in range(ncol):
        ax.text(j + 0.25, -0.12, "up", ha="center", va="bottom", fontsize=8, color=MUTED)
        ax.text(j + 0.75, -0.12, "down", ha="center", va="bottom", fontsize=8, color=MUTED)
    for j in range(1, ncol):
        ax.axvline(j, color="white", lw=2)
    clean(ax, keep=())
    letter(fig, 0.05, 0.05, "a", H)
    # family key for a and b
    fig.legend(handles=[Patch(facecolor=FAM[f], label=f) for f in ds.FAMILY_ORDER]
               + [Patch(facecolor="white", edgecolor="#b5b4ae", hatch="////", label="no testable test")],
               loc="upper left", bbox_to_anchor=(0.05 / W, 1 - (ha - 0.02) / H), ncol=4, frameon=False, fontsize=8,
               handlelength=1.2, columnspacing=1.2)
    # ---- b: per-experiment hli call
    bl, bw = 1.75, 4.25
    bb = 0.55
    ax = axin(fig, bl, bb, bw, nr_b * rh_b, H)
    for i, r in b.iterrows():
        for xv, p, col in ((r.x_up, r.padj_up, UP), (r.x_down, r.padj_down, DOWN)):
            if pd.isna(p):
                continue
            sig = p < 0.05
            ax.plot(xv, i + 0.5, marker="o", ms=5.5, mfc=col if sig else "white", mec=col if sig else NSG,
                    mew=1.0, ls="", zorder=3)
        fam = [f for s, f, _ in SCOPES if s == r.scope][0]
        ax.add_patch(Rectangle((-0.03, i + 0.15), 0.016, 0.7, facecolor=FAM[fam], clip_on=False,
                               transform=ax.get_yaxis_transform()))
    sc_ = b.scope.tolist()
    for i in range(1, nr_b):
        if sc_[i] != sc_[i - 1]:
            ax.axhline(i, color="#d9d8d4", lw=0.6)
    th = -np.log10(0.05)
    for xv in (th, -th):
        ax.axvline(xv, color=MUTED, lw=0.7, ls="--")
    ax.axvline(0, color=INK, lw=0.6)
    ax.set_xlim(-CAP - 0.5, CAP + 0.5)
    ax.set_ylim(nr_b, 0)
    ax.set_yticks(np.arange(nr_b) + 0.5)
    ax.set_yticklabels(b.short)
    ax.tick_params(axis="y", length=0, pad=11)
    ax.set_xticks([-12, -8, -4, 0, 4, 8, 12])
    ax.set_xticklabels(["12", "8", "4", "0", "4", "8", "≥12"])
    ax.set_xlabel("−log10 per-experiment BH padj   ← down · up →")
    for i in range(nr_b):
        if i == 0 or sc_[i] != sc_[i - 1]:
            ax.text(CAP + 1.2, i + 0.05, b.scope.iloc[i], ha="left", va="top", fontsize=8, color=MUTED, clip_on=False)
    clean(ax, keep=("bottom",))
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc=UP, mec=UP, label="up, padj < 0.05"),
                       Line2D([], [], marker="o", ls="", mfc=DOWN, mec=DOWN, label="down, padj < 0.05"),
                       Line2D([], [], marker="o", ls="", mfc="white", mec=NSG, label="not significant"),
                       Line2D([], [], color=MUTED, ls="--", label="padj = 0.05")],
              loc="lower left", bbox_to_anchor=(-0.38, 1.0), ncol=4, frameon=False, fontsize=8, handletextpad=0.3,
              columnspacing=1.0)
    letter(fig, 0.05, ha + 0.3, "b", H)
    save(fig, "paper_fig1")
    return a, b


# ------------------------------------------------------------------ Fig 2
FIG2 = [("Phage infection (array, up-only)", "h", [1, 2, 4, 6, 8]), ("N deprivation (array)", "h", [0, 6, 12, 24, 48]),
        ("Iron starvation", "h", [12, 24, 48]), ("N starvation lowN (coculture)", "d", [18, 31, 60, 89]),
        ("N-depleted (RNA-seq, top 50%)", "h", [3, 12, 24]), ("Phage lysate (light)", "h", [0.5, 2.5, 4.5, 8.5])]
FIG2_TITLE = {"N-depleted (RNA-seq, top 50%)": "N-depleted, RNA-seq"}


def fig2():
    tm = rd("explore_timing.csv")
    ex = pd.read_csv(METHODS / "experiments.csv", encoding="utf-8")
    uponly = set(ex[ex.up_only.astype(str) == "True"].experiment_id)
    fam_of = {r.label: ds.category(r._asdict())[0] for r in ex.itertuples()}
    src = []
    H = 4.9
    fig = plt.figure(figsize=(W, H))
    pw, ph = 1.95, 1.45
    xs = [0.62, 3.0, 5.15]
    ys = [H - 0.35 - ph, H - 0.35 - ph - 0.62 - ph - 0.1]
    for k, (lab, unit, ticks) in enumerate(FIG2):
        g = tm[(tm.label == lab) & tm.hours.notna()].copy()
        hl = g[g.set == "hli"].sort_values("hours")
        rb = g[g.set == "ribosomal_proteins"].sort_values("hours")
        eid = hl.experiment_id.iloc[0]
        f = 24.0 if unit == "d" else 1.0
        x = hl.hours.values / f
        ax = axin(fig, xs[k % 3], ys[k // 3], pw, ph, H)
        desc = (hl.test_type == "descriptive").all()
        ls = (0, (3, 2)) if desc else "-"
        up = 100 * hl.frac_up.values
        ax.plot(x, up, color=UP, lw=1.4, ls=ls, zorder=2)
        has_down = eid not in uponly
        dn = 100 * hl.frac_down.values
        if has_down:
            ax.plot(x, dn, color=DOWN, lw=1.4, ls=ls, zorder=2)
        ax.plot(rb.hours.values / f, 100 * rb.frac_down.values, color=MUTED, lw=0.9, ls=":", zorder=1)
        for xv, yv, sig, tst in zip(x, up, hl.sig_up.astype(str) == "True", hl.testable_up.astype(str) == "True"):
            if sig:
                ax.plot(xv, yv, "o", ms=4.5, color=UP, zorder=3)
            elif not tst:
                ax.plot(xv, yv, "o", ms=4.5, mfc="white", mec=UP, mew=0.9, zorder=3)
        if has_down:
            for xv, yv, sig, tst in zip(x, dn, hl.sig_down.astype(str) == "True", hl.testable_down.astype(str) == "True"):
                if sig:
                    ax.plot(xv, yv, "o", ms=4.5, color=DOWN, zorder=3)
                elif not tst:
                    ax.plot(xv, yv, "o", ms=4.5, mfc="white", mec=DOWN, mew=0.9, zorder=3)
        ax.set_ylim(-4, 104)
        ax.set_yticks([0, 50, 100])
        if k % 3:
            ax.set_yticklabels([])
        else:
            ax.set_ylabel("% of measured hli")
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{v:g}" for v in ticks])
        ax.set_xlabel("days" if unit == "d" else "hours", labelpad=1)
        clean(ax)
        ax.add_patch(Rectangle((0, 1.03), 1, 0.07, transform=ax.transAxes, facecolor=FAM[fam_of[lab]], clip_on=False))
        title = FIG2_TITLE.get(lab, EXP_SHORT[lab]) + (" (descr.)" if desc else "") + (" (up only)" if not has_down else "")
        ax.text(0, 1.13, title, transform=ax.transAxes, fontsize=8, va="bottom", ha="left")
        letter(fig, (0.05 if k % 3 == 0 else xs[k % 3] - 0.36), H - ys[k // 3] - ph - 0.32, "abcdef"[k], H)
        for r_h, r_r in zip(hl.itertuples(), [None] * len(hl)):
            pass
        rbi = rb.set_index("timepoint")
        for r in hl.itertuples():
            src.append(dict(panel="abcdef"[k], label=lab, experiment_id=eid, timepoint=r.timepoint, hours=r.hours,
                            x_plotted=r.hours / f, x_unit=unit, test_type=r.test_type, n_measured=r.n_measured,
                            n_up=r.n_up, n_down=r.n_down, pct_up=100 * r.frac_up,
                            pct_down=(100 * r.frac_down if has_down else np.nan), padj_up=r.padj_up, padj_down=r.padj_down,
                            sig_up=r.sig_up, sig_down=r.sig_down, testable_up=r.testable_up, testable_down=r.testable_down,
                            ribosomal_pct_down=100 * rbi.at[r.timepoint, "frac_down"] if r.timepoint in rbi.index else np.nan))
    fig.legend(handles=[Line2D([], [], color=UP, lw=1.4, label="hli % up"), Line2D([], [], color=DOWN, lw=1.4, label="hli % down"),
                        Line2D([], [], color=MUTED, lw=0.9, ls=":", label="ribosomal % down"),
                        Line2D([], [], marker="o", ls="", color=INK, ms=4.5, label="set test padj < 0.05"),
                        Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=4.5, label="not testable"),
                        Line2D([], [], color=INK, lw=1.2, ls=(0, (3, 2)), label="descriptive table")],
               loc="lower left", bbox_to_anchor=(0.02, 0.0), ncol=3, frameon=False, fontsize=8, columnspacing=1.2)
    pd.DataFrame(src).to_csv(DATA / "paper_fig_source_fig2.csv", index=False, encoding="utf-8")
    save(fig, "paper_fig2")
    return pd.DataFrame(src)


# ------------------------------------------------------------------ Fig 3
def fig3():
    pts = rd("explore_D_trajectory_points.csv")
    for c in ("up_defined", "down_defined"):
        pts[c] = pts[c].astype(str) == "True"
    pts["scope"] = pts.type.map(TYPE_SCOPE)
    cl = rd("explore_D_gene_clusters.csv").sort_values("leaf_order")
    cg = cons.by_gene().set_index("locus_tag")
    genes = cl.locus_tag.tolist()
    rows = []
    for g in genes:
        for sc, fam, _ in SCOPES:
            d = pts[(pts.locus_tag == g) & (pts.scope == sc)]
            ud, dd = d[d.up_defined], d[d.down_defined]
            rows.append(dict(locus_tag=g, cluster=int(cl.set_index("locus_tag").at[g, "cluster"]), scope=sc,
                             n_up=int((ud.call == "up").sum()), n_up_defined=len(ud),
                             pct_up=100 * (ud.call == "up").mean() if len(ud) else np.nan,
                             n_down=int((dd.call == "down").sum()), n_down_defined=len(dd),
                             pct_down=100 * (dd.call == "down").mean() if len(dd) else np.nan))
    a = pd.DataFrame(rows)
    a.to_csv(DATA / "paper_fig_source_fig3a.csv", index=False, encoding="utf-8")
    d5 = rd("explore_D5_conservation.csv")
    d5[["locus_tag", "cluster", "copy_class", "tier", "tier_name", "n_organisms", "xj", "n_up", "n_up_defined", "pct_up",
        "n_up_rnaseq", "n_up_defined_rnaseq", "pct_up_rnaseq", "n_up_array", "n_up_defined_array", "pct_up_array"]].to_csv(
        DATA / "paper_fig_source_fig3b.csv", index=False, encoding="utf-8")

    nr, nc = len(genes), len(SCOPES)
    rh = 0.205
    ha = 0.62 + nr * rh + 1.0
    hb = 2.55
    H = ha + hb
    assert H <= 9, H
    fig = plt.figure(figsize=(W, H))
    gl = 2.05
    gw = W - gl - 0.12
    ax = axin(fig, gl, H - 0.62 - nr * rh, gw, nr * rh, H)
    ai = a.set_index(["locus_tag", "scope"])
    for i, g in enumerate(genes):
        for j, (sc, fam, _) in enumerate(SCOPES):
            r = ai.loc[(g, sc)]
            for k, (pc, nd, cmap) in enumerate((("pct_up", "n_up_defined", UPMAP), ("pct_down", "n_down_defined", DNMAP))):
                x0 = j + 0.5 * k
                if r[nd] == 0:
                    ax.add_patch(Rectangle((x0 + 0.02, i + 0.06), 0.46, 0.88, facecolor="white", edgecolor="#d9d8d4",
                                           hatch="////", lw=0.4))
                else:
                    ax.add_patch(Rectangle((x0 + 0.02, i + 0.06), 0.46, 0.88, facecolor=cmap(r[pc] / 100), edgecolor="none"))
    for j in range(1, nc):
        ax.axvline(j, color="white", lw=1.6)
    cls = cl.cluster.tolist()
    for i in range(1, nr):
        if cls[i] != cls[i - 1]:
            ax.axhline(i, color=INK, lw=0.9)
    ax.set_xlim(0, nc)
    ax.set_ylim(nr, 0)
    ax.set_xticks(np.arange(nc) + 0.5)
    ax.set_xticklabels([s2 for _, _, s2 in SCOPES], linespacing=0.95)
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=8)
    for j, (sc, fam, _) in enumerate(SCOPES):
        ax.add_patch(Rectangle((j + 0.04, -0.28), 0.92, 0.18, facecolor=FAM[fam], clip_on=False))
    ax.set_yticks(np.arange(nr) + 0.5)
    ax.set_yticklabels(genes)
    ax.tick_params(axis="y", length=0, pad=30)
    clean(ax, keep=())
    # row annotations: copy (filled / hollow square), tier grey, cluster bracket
    tr = ax.get_yaxis_transform()
    for i, g in enumerate(genes):
        multi = cl.set_index("locus_tag").at[g, "copy_class"] == "multi"
        ax.plot(-0.032, i + 0.5, marker="s", ms=5.5, mfc=INK if multi else "white", mec=INK, mew=0.8,
                transform=tr, clip_on=False)
        ax.add_patch(Rectangle((-0.022, i + 0.1), 0.016, 0.8, facecolor=cons.TIER_GREY[int(cg.at[g, "tier"])],
                               transform=tr, clip_on=False))
    s0 = 0
    xb = -0.262
    for i in range(1, nr + 1):
        if i == nr or cls[i] != cls[s0]:
            ax.plot([xb, xb], [s0 + 0.15, i - 0.15], color=INK, lw=1.0, transform=tr, clip_on=False)
            ax.text(xb - 0.012, (s0 + i) / 2, f"C{cls[s0]}", ha="right", va="center", fontsize=8, fontweight="bold",
                    transform=tr)
            s0 = i
    letter(fig, 0.05, 0.05, "a", H)
    # legends under the heatmap: ramps, copy, tier
    lb = H - 0.62 - nr * rh - 0.5
    for k, (cmap, lab) in enumerate(((UPMAP, "% of defined cells up"), (DNMAP, "% down"))):
        cax = axin(fig, gl + k * 1.55, lb, 1.1, 0.1, H)
        cax.imshow(np.linspace(0, 1, 100)[None, :], aspect="auto", cmap=cmap, extent=(0, 100, 0, 1))
        cax.set_yticks([])
        cax.set_xticks([0, 50, 100])
        cax.tick_params(length=2, pad=1)
        cax.set_title(lab, fontsize=8, pad=2, loc="left")
    fig.legend(handles=[Line2D([], [], marker="s", ls="", mfc=INK, mec=INK, label="multi-copy"),
                        Line2D([], [], marker="s", ls="", mfc="white", mec=INK, label="single-copy"),
                        Patch(facecolor="white", edgecolor="#b5b4ae", hatch="////", label="not defined")],
               loc="lower left", bbox_to_anchor=((gl + 3.05) / W, (lb - 0.17) / H), ncol=1, frameon=False, fontsize=8,
               handletextpad=0.3, labelspacing=0.2)
    fig.text((gl - 0.05) / W, (lb - 0.42) / H, "ortholog-group breadth:", ha="right", va="center", fontsize=8)
    fig.legend(handles=[Patch(facecolor=cons.TIER_GREY[t_], label=cons.TIER_SHORT[t_]) for t_ in cons.TIER_NAME],
               loc="center left", bbox_to_anchor=((gl - 0.1) / W, (lb - 0.42) / H), ncol=4, frameon=False, fontsize=8,
               handletextpad=0.3, columnspacing=1.0)
    # ---- b: conservation vs % up (pooled filled, RNA-seq-only hollow companion)
    ax = axin(fig, 0.75, 0.48, 4.6, hb - 0.85, H)
    for r in d5.itertuples():
        m = ds.CLUSTER_STYLE[int(r.cluster)][1]
        ax.plot(r.xj - 0.35, r.pct_up, marker=m, ms=5.5, color=INK, ls="", zorder=3)
        ax.plot(r.xj + 0.35, r.pct_up_rnaseq, marker=m, ms=5.5, mfc="white", mec=INK, mew=0.9, ls="", zorder=3)
        ax.plot([r.xj - 0.35, r.xj + 0.35], [r.pct_up, r.pct_up_rnaseq], color=NSG, lw=0.6, zorder=2)
        ax.add_patch(Rectangle((r.xj - 0.45, -9), 0.9, 4.5, facecolor=cons.TIER_GREY[int(r.tier)], edgecolor="none"))
    ax.set_xlim(15, 101)
    ax.set_ylim(-11, 62)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_xticks([21, 30, 43, 60, 80, 96])
    ax.set_xlabel("organisms in the gene's ortholog group")
    ax.set_ylabel("% of defined cells up\n(stress + light onset)")
    ax.axhline(0, color=MUTED, lw=0.5)
    clean(ax)
    ks = sorted(d5.cluster.unique())
    ax.legend(handles=[Line2D([], [], marker=ds.CLUSTER_STYLE[int(k_)][1], ls="", color=INK, ms=5.5, label=f"C{k_}") for k_ in ks]
              + [Line2D([], [], marker="o", ls="", color=INK, ms=5.5, label="all platforms"),
                 Line2D([], [], marker="o", ls="", mfc="white", mec=INK, ms=5.5, label="RNA-seq only")],
              loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False, fontsize=8, ncol=1, handletextpad=0.3,
              labelspacing=0.3)
    letter(fig, 0.05, ha + 0.02, "b", H)
    save(fig, "paper_fig3")
    return a, d5


# ------------------------------------------------------------------ Fig 4
def fig4():
    ll = rd("explore_light_level.csv")
    ll["testable"] = ll.testable.astype(str) == "True"
    sp = rd("explore_light_level_spearman.csv")
    panels = [("hli", "up", UP, "hli, up"), ("ribosomal_proteins", "down", DOWN, "Ribosomal proteins, down")]
    H = 3.3
    fig = plt.figure(figsize=(W, H))
    src = []
    for k, (s, d, col, title) in enumerate(panels):
        g = ll[(ll.set == s) & (ll.direction == d) & ll.testable].sort_values(["light_treatment_umol", "label", "timepoint"]).copy()
        g["y"] = g.y_signed_log10.abs()
        g["xj"] = g.light_treatment_umol.astype(float)
        for lv, gg in g.groupby("light_treatment_umol"):
            n = len(gg)
            g.loc[gg.index, "xj"] = [lv + (i - (n - 1) / 2) * 1.2 for i in range(n)]
        ax = axin(fig, 0.62 + k * 3.45, 0.95, 2.95, H - 1.75, H)
        sig = g.padj_bh < 0.05
        ax.plot(g.xj[sig], g.y[sig], "o", ms=5, color=col, ls="")
        ax.plot(g.xj[~sig], g.y[~sig], "o", ms=5, mfc="white", mec=NSG, mew=0.9, ls="")
        ax.axhline(-np.log10(0.05), color=MUTED, lw=0.7, ls="--")
        r = sp[(sp.set == s) & (sp.direction == d) & sp.y.str.startswith("-log10")].iloc[0]
        ax.text(0, 1.04, f"Spearman ρ = {r.spearman_rho:.2f}, p = {r.p_value:.3f}; n = {int(r.n_tests)} tests, "
                f"{int(r.n_experiments)} exp.", transform=ax.transAxes, va="bottom", fontsize=8, color=MUTED)
        ax.set_xlabel("growth light, µmol photons m⁻² s⁻¹")
        if k == 0:
            ax.set_ylabel("−log10 BH padj")
        ax.set_title(title, fontsize=9, loc="left", pad=18)
        ax.set_xlim(0, 105)
        clean(ax)
        letter(fig, 0.05 + k * 3.45, 0.05, "ab"[k], H)
        for rr in g.itertuples():
            src.append(dict(panel="ab"[k], set=s, direction=d, experiment_id=rr.experiment_id, label=rr.label,
                            timepoint=rr.timepoint, light_umol=rr.light_treatment_umol, x_plotted=rr.xj, padj_bh=rr.padj_bh,
                            neg_log10_padj=rr.y, significant=bool(rr.padj_bh < 0.05), spearman_rho=r.spearman_rho,
                            spearman_p=r.p_value, n_tests=r.n_tests))
    fig.legend(handles=[Line2D([], [], marker="o", ls="", color=UP, label="hli up, padj < 0.05"),
                        Line2D([], [], marker="o", ls="", color=DOWN, label="ribosomal down, padj < 0.05"),
                        Line2D([], [], marker="o", ls="", mfc="white", mec=NSG, label="not significant"),
                        Line2D([], [], color=MUTED, ls="--", label="padj = 0.05")],
               loc="lower left", bbox_to_anchor=(0.0, 0.0), ncol=2, frameon=False, fontsize=8, columnspacing=1.5)
    pd.DataFrame(src).to_csv(DATA / "paper_fig_source_fig4.csv", index=False, encoding="utf-8")
    save(fig, "paper_fig4")
    return pd.DataFrame(src)


# ------------------------------------------------------------------ Fig S1
def figS1():
    M = pd.read_csv(DATA / "explore_D_matrix_twinrule.csv", encoding="utf-8", index_col=0)
    co = rd("explore_D_column_order.csv").sort_values("order")
    cl = rd("explore_D_gene_clusters.csv").sort_values("leaf_order")
    cg = cons.by_gene().set_index("locus_tag")
    genes = cl.locus_tag.tolist()
    co["code"] = [f"S{i + 1:02d}" for i in range(len(co))]
    co["row_label"] = [s.replace("Cocult", "Cocult.")[:22] for s in co.short]
    key = co[["code", "row_label", "col", "experiment_id", "label", "label_detailed", "timepoint", "family", "type",
              "col_cluster", "n_defined_genes"]]
    key.to_csv(DATA / "paper_figS1_column_key.csv", index=False, encoding="utf-8")
    Mo = M.loc[genes, co.col]
    Mo.T.assign(code=co.code.values, row_label=co.row_label.values).to_csv(DATA / "paper_fig_source_figS1.csv",
                                                                          encoding="utf-8")
    nr, nc = len(co), len(genes)
    H = 10.0
    top = 1.6
    bot = 1.05
    rh = (H - top - bot) / nr
    gl = 2.1
    cw = (W - gl - 1.55) / nc
    fig = plt.figure(figsize=(W, H))
    ax = axin(fig, gl, bot, nc * cw, nr * rh, H)
    colour = {1.0: UP, -1.0: DOWN, 0.0: "#d9d8d4"}
    for i, c in enumerate(co.col):
        for j, g in enumerate(genes):
            v = Mo.at[g, c]
            if np.isnan(v):
                ax.add_patch(Rectangle((j + 0.05, i + 0.08), 0.9, 0.84, facecolor="white", edgecolor="#d9d8d4",
                                       hatch="////", lw=0.3))
            else:
                ax.add_patch(Rectangle((j + 0.05, i + 0.08), 0.9, 0.84, facecolor=colour[v], edgecolor="none"))
    kk = co.col_cluster.tolist()
    for i in range(1, nr):
        if kk[i] != kk[i - 1]:
            ax.axhline(i, color=INK, lw=0.9)
    cls = cl.cluster.tolist()
    for j in range(1, nc):
        if cls[j] != cls[j - 1]:
            ax.axvline(j, color=INK, lw=0.9)
    ax.set_xlim(0, nc)
    ax.set_ylim(nr, 0)
    ax.set_yticks(np.arange(nr) + 0.5)
    ax.set_yticklabels(co.row_label)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.set_xticks(np.arange(nc) + 0.5)
    ax.set_xticklabels(genes, rotation=90)
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0, pad=30)
    clean(ax, keep=())
    tr = ax.get_yaxis_transform()
    for i, f in enumerate(co.family):
        ax.add_patch(Rectangle((-0.03, i + 0.12), 0.018, 0.76, facecolor=FAM[f], transform=tr, clip_on=False))
    s0 = 0
    for i in range(1, nr + 1):
        if i == nr or kk[i] != kk[s0]:
            ax.text(nc + 0.3, (s0 + i) / 2, f"K{kk[s0]}" if kk[s0] else "K0", ha="left", va="center", fontsize=8,
                    fontweight="bold")
            s0 = i
    xt = ax.get_xaxis_transform()
    for j, g in enumerate(genes):
        multi = cl.set_index("locus_tag").at[g, "copy_class"] == "multi"
        ax.plot(j + 0.5, 1.012, marker="s", ms=5, mfc=INK if multi else "white", mec=INK, mew=0.7, transform=xt, clip_on=False)
        ax.add_patch(Rectangle((j + 0.12, 1.022), 0.76, 0.012, facecolor=cons.TIER_GREY[int(cg.at[g, "tier"])],
                               transform=xt, clip_on=False))
    s0 = 0
    yb = 1 + (top - 0.22) / (nr * rh)
    for j in range(1, nc + 1):
        if j == nc or cls[j] != cls[s0]:
            ax.plot([s0 + 0.15, j - 0.15], [yb, yb], color=INK, lw=1.0, transform=xt, clip_on=False)
            ax.text((s0 + j) / 2, yb + 0.004, f"C{cls[s0]}", ha="center", va="bottom", fontsize=8, fontweight="bold",
                    transform=xt)
            s0 = j
    fig.legend(handles=[Patch(facecolor=UP, label="up"), Patch(facecolor=DOWN, label="down"),
                        Patch(facecolor="#d9d8d4", label="not significant"),
                        Patch(facecolor="white", edgecolor="#b5b4ae", hatch="////", label="not defined")]
               + [Patch(facecolor=FAM[f], label=f) for f in ds.FAMILY_ORDER],
               loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=4, frameon=False, fontsize=8, columnspacing=1.0,
               handletextpad=0.4)
    fig.legend(handles=[Line2D([], [], marker="s", ls="", mfc=INK, mec=INK, label="multi-copy"),
                        Line2D([], [], marker="s", ls="", mfc="white", mec=INK, label="single-copy")]
               + [Patch(facecolor=cons.TIER_GREY[t_], label=cons.TIER_SHORT[t_]) for t_ in cons.TIER_NAME],
               loc="lower left", bbox_to_anchor=(0.01, 0.45 / H), ncol=6, frameon=False,
               fontsize=8, handletextpad=0.4, columnspacing=0.9)
    save(fig, "paper_figS1")
    return co


def main():
    a1, b1 = fig1()
    s2 = fig2()
    a3, d5 = fig3()
    s4 = fig4()
    co = figS1()
    pd.set_option("display.width", 250)
    print("font check (min pt, height in):", FONT_LOG)
    h = a1[a1.set == "hli"].pivot_table(index="scope", columns="direction", values=["n_sig", "n_testable"], aggfunc="first")
    print(h.reindex([s for s, _, _ in SCOPES]).to_string())
    print(b1[["short", "scope", "experiment_call", "padj_up", "padj_down"]].to_string(index=False))
    print(s2[["panel", "label", "timepoint", "pct_up", "pct_down", "sig_up", "sig_down", "testable_up", "ribosomal_pct_down"]]
          .to_string(index=False))
    print(s4.groupby("panel").agg(n=("significant", "size"), n_sig=("significant", "sum"), rho=("spearman_rho", "first"),
                                  p=("spearman_p", "first")).to_string())
    print("S1 rows (experiment x time point):", len(co))


if __name__ == "__main__":
    main()
