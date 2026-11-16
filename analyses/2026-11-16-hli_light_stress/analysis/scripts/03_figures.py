"""Analysis part A, step 3: static figures (PNG 300 dpi + SVG) in analysis/figures/.

a  hli_gene_heatmap_by_group / _by_light: 23 hli genes x experiment-timepoints, cell = up / down / ns / not measured
b  set_band_by_group / _by_light: hli + 12 reference sets x direction, signed -log10(BH padj), flags marked
c  aggregate_by_scope: rows = hli + references (grouped by role), columns = reading scopes; each cell split
   into the fraction of testable tests significant up (left, orange) and down (right, blue), n testable printed
c2 experiment_calls_by_group / _by_light: per-experiment aggregate call (up / down / both / neither / not tested)
Direction is always treatment vs control as stored in the KG. Reads analysis/data/ only.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/03_figures.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, to_rgb  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS.parent / "methods"))
import kg_io  # noqa: E402

DATA, FIG = ANALYSIS / "data", ANALYSIS / "figures"
FIG.mkdir(exist_ok=True)
UP, DOWN, MID = "#eb6834", "#2a78d6", "#f0efec"
NS, NA_FILL = "#d9d8d4", "#e4e3df"
INK, MUTED, GRID = "#1f1f1d", "#6b6b66", "#d9d8d4"
CMAP = LinearSegmentedColormap.from_list("spock_diverging", [DOWN, MID, UP])
BLOCK_ORDER = ["light_onset", "constant_dark_vs_light", "schedule_extension", "electron_transport_DCMU",
               "phage_dark", "nonlight_stress", "nonstress_possible_relief"]
BLOCK_LABEL = {"light_onset": "Light onset", "constant_dark_vs_light": "Constant dark vs light",
               "schedule_extension": "Schedule extension", "electron_transport_DCMU": "DCMU",
               "phage_dark": "Phage, dark", "nonlight_stress": "Non-light stress",
               "nonstress_possible_relief": "Non-stress / possible relief"}
SET_ROWS = [("hli", "hli (23 genes, 14 CK groups)", "Target")] + kg_io.set_rows()
SCOPES = [("light_reading_group", "light_onset", "Light onset"),
          ("light_reading_group", "constant_dark_vs_light", "Constant dark\nvs light"),
          ("light_reading_group", "schedule_extension", "Schedule\nextension"),
          ("light_reading_group", "phage_dark", "Phage, dark"),
          ("nonlight_stress_type", "carbon", "CO2"), ("nonlight_stress_type", "iron", "Iron"),
          ("nonlight_stress_type", "nitrogen", "Nitrogen"), ("nonlight_stress_type", "phosphorus", "Phosphorus"),
          ("nonlight_stress_type", "salt", "Salt"), ("nonlight_stress_type", "viral", "Phage, light"),
          ("group", "nonstress_possible_relief", "Non-stress")]
DIRECTION_NOTE = "Direction = treatment vs control, as stored in the KG (no light flip)."


def read(name):
    return pd.read_csv(DATA / name, encoding="utf-8", keep_default_na=False, na_values=[""])


def save(fig, stem):
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def mix(c, f):
    a, b = np.array(to_rgb(MID)), np.array(to_rgb(c))
    return tuple(a + (b - a) * max(0.0, min(1.0, f)))


def columns(t, by):
    c = (t[["experiment_id", "label", "label_detailed", "group", "light_reading_group", "timepoint", "timepoint_order",
            "light_treatment_umol", "light_control_umol", "test_type"]]
         .drop_duplicates(["experiment_id", "timepoint"]).copy())
    c["block"] = [lr if lr != "none" else g for lr, g in zip(c.light_reading_group, c.group)]
    c["rank"] = c.block.map({b: i for i, b in enumerate(BLOCK_ORDER)})
    if by == "group":
        c = c.sort_values(["rank", "label", "timepoint_order"])
        c["blockkey"] = c.block
    else:
        c = c.sort_values(["light_treatment_umol", "light_control_umol", "rank", "label", "timepoint_order"])
        c["blockkey"] = [f"{v:g}" for v in c.light_treatment_umol]
    c["col_label"] = [f"{lab} · {tp}" for lab, tp in zip(c.label, c.timepoint)]
    return c.reset_index(drop=True)


def blocks(ax, keys, labeler, y=-0.3, n_rows=None):
    start = 0
    for j in range(1, len(keys) + 1):
        if j == len(keys) or keys[j] != keys[start]:
            if j < len(keys):
                ax.axvline(j, color=INK, lw=0.9)
            lab = labeler(keys[start])
            if (j - start) <= 6:
                lab = lab.replace(", ", "\n").replace(" ", "\n")
            ax.text((start + j) / 2, y, lab, ha="center", va="bottom", fontsize=6, color=INK)
            start = j


def light_key(t):
    lr = t[t.light_reading_group != "none"].drop_duplicates("experiment_id")
    lr = lr.assign(r=lr.light_reading_group.map({b: i for i, b in enumerate(BLOCK_ORDER)})).sort_values(["r", "label"])
    return "Light-reading experiments (treatment vs control):\n" + "\n".join(
        f"  {r.label} = {r.label_detailed}" for r in lr.itertuples())


def caption(ax, text, offset=-215):
    ax.annotate(text, xy=(0, 0), xycoords="axes fraction", xytext=(0, offset), textcoords="offset points",
                fontsize=6, color=MUTED, va="top")


# ---------------------------------------------------------------- a: gene heatmap
def gene_heatmap(gc, t, by, stem):
    cols = columns(t, by)
    genes = (gc[["locus_tag", "ck_group", "gene_name"]].drop_duplicates("locus_tag")
             .sort_values(["ck_group", "locus_tag"]).reset_index(drop=True))
    idx = gc.set_index(["experiment_id", "timepoint", "locus_tag"])
    n_r, n_c = len(genes), len(cols)
    fig, ax = plt.subplots(figsize=(max(10, 0.2 * n_c + 3.5), 1.6 + 0.24 * n_r))
    colour = {"up": UP, "down": DOWN, "ns": NS}
    for j, c in enumerate(cols.itertuples()):
        for i, g in enumerate(genes.itertuples()):
            r = idx.loc[(c.experiment_id, c.timepoint, g.locus_tag)]
            if r["call"] == "not_measured":
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white", lw=0.8))
                ax.add_patch(Rectangle((j + 0.08, i + 0.08), 0.84, 0.84, facecolor="none", edgecolor="#c9c8c3",
                                       hatch="////", lw=0))
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=colour[r["call"]], edgecolor="white", lw=0.8))
        if c.test_type == "descriptive":
            ax.text(j + 0.5, n_r + 0.15, "d", ha="center", va="top", fontsize=5, color=MUTED)
    grp = genes.ck_group.tolist()
    for i in range(1, n_r):
        if grp[i] != grp[i - 1]:
            ax.axhline(i, color=GRID, lw=0.6)
    ax.set_xlim(0, n_c)
    ax.set_ylim(n_r + 0.6, 0)
    ax.set_yticks(np.arange(n_r) + 0.5)
    ax.set_yticklabels([f"{g.locus_tag} ({g.ck_group.replace('cyanorak:', '')})" for g in genes.itertuples()],
                       fontsize=6, color=INK)
    ax.set_xticks(np.arange(n_c) + 0.5)
    ax.set_xticklabels(cols.col_label, rotation=90, fontsize=5.2, color=INK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    blocks(ax, cols.blockkey.tolist(), (lambda b: BLOCK_LABEL[b]) if by == "group" else (lambda v: f"{v} µmol"))
    ax.legend(handles=[Patch(facecolor=UP, label="up (significant)"), Patch(facecolor=DOWN, label="down (significant)"),
                       Patch(facecolor=NS, label="not significant"),
                       Patch(facecolor="white", edgecolor="#c9c8c3", hatch="////", label="not measured")],
              loc="upper left", bbox_to_anchor=(1.005, 1), fontsize=6, frameon=False)
    ttl = ("hli genes (MED4, 23 locus tags, ordered by Cyanorak CK group) across 29 experiments, "
           + ("grouped by light reading and experiment group" if by == "group"
              else "columns ordered by treatment-arm light level (block label, µmol photons m⁻² s⁻¹)"))
    ax.set_title(ttl, fontsize=9, loc="left", color=INK, pad=38)
    caption(ax, f"{DIRECTION_NOTE} Calls are each study's own significance calls. In significant-only tables a gene absent from the "
                "table counts as not significant (genome background); in full tables an absent gene is not measured.\n"
                "d = descriptive table or time point (no set-level test). " + light_key(t))
    save(fig, stem)


# ---------------------------------------------------------------- b: set band
def set_band(t, by, stem):
    cols = columns(t, by)
    rows = [(s, d) for s, _, _ in SET_ROWS for d in ("up", "down")]
    lab = {s: l for s, l, _ in SET_ROWS}
    band = {s: b for s, _, b in SET_ROWS}
    idx = t.set_index(["experiment_id", "timepoint", "set", "direction"])
    n_r, n_c = len(rows), len(cols)
    lim = 6.0
    norm = TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)
    fig, ax = plt.subplots(figsize=(max(10, 0.2 * n_c + 3.5), 2.0 + 0.27 * n_r))
    for j, c in enumerate(cols.itertuples()):
        for i, (s, d) in enumerate(rows):
            r = idx.loc[(c.experiment_id, c.timepoint, s, d)]
            fl = r["flags"] if isinstance(r["flags"], str) else ""
            if "not_testable" in fl or "descriptive" in fl:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=NA_FILL, edgecolor="white", lw=0.8))
                ax.text(j + 0.5, i + 0.5, "n/a", ha="center", va="center", fontsize=3.4, color=MUTED)
            elif "too_few" in fl:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white", lw=0.8))
                ax.add_patch(Rectangle((j + 0.06, i + 0.06), 0.88, 0.88, facecolor="none", edgecolor="#b5b4ae",
                                       hatch="////", lw=0))
            else:
                v = -np.log10(max(r["padj_bh"], 1e-300))
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=CMAP(norm(v if d == "up" else -v)), edgecolor="white",
                                       lw=0.8))
                if r["padj_bh"] < 0.05:
                    ax.text(j + 0.5, i + 0.5, "*", ha="center", va="center", fontsize=6, color=INK)
            if "genome_wide_response" in fl:
                ax.plot(j + 0.85, i + 0.18, marker="o", ms=1.5, color=INK)
    roles = [band[s] for s, _ in rows]
    start = 0
    for i in range(1, n_r + 1):
        if i == n_r or roles[i] != roles[start]:
            if i < n_r:
                ax.axhline(i, color=INK, lw=2.2 if roles[i] in ("Failed references", "Broad stress") else 0.9)
            ax.text(-0.205, (start + i) / 2, roles[start].replace(" ", "\n"), ha="center", va="center", fontsize=6.6,
                    fontweight="bold", color=INK, transform=ax.get_yaxis_transform())
            start = i
    ax.set_xlim(0, n_c)
    ax.set_ylim(n_r, 0)
    ax.set_yticks(np.arange(n_r) + 0.5)
    ax.set_yticklabels([f"{lab[s]} — {d}".replace(" (kept;", "\n(kept;") for s, d in rows], fontsize=6, color=INK)
    ax.set_xticks(np.arange(n_c) + 0.5)
    ax.set_xticklabels(cols.col_label, rotation=90, fontsize=5.2, color=INK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    blocks(ax, cols.blockkey.tolist(), (lambda b: BLOCK_LABEL[b]) if by == "group" else (lambda v: f"{v} µmol"))
    sm = plt.cm.ScalarMappable(cmap=CMAP, norm=norm)
    cb = fig.colorbar(sm, ax=ax, fraction=0.012, pad=0.01, shrink=0.5, extend="both")
    cb.set_label("signed −log10(BH padj), capped at 6\n← down (blue) · up (orange) →", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    ax.set_title("hli and reference gene sets: set-level over-representation among significant genes, "
                 + ("grouped by light reading and experiment group" if by == "group"
                    else "columns ordered by treatment-arm light level"), fontsize=9, loc="left", color=INK, pad=38)
    caption(ax, "Hatched = fewer than 10 genes significant in that direction (no test). n/a = not testable (up-only table) "
                "or descriptive. • = more than 30% of measured genes significant in that direction. * = BH padj < 0.05 "
                "(BH per gene set across its 64 testable tests).\n" + DIRECTION_NOTE + "\n" + light_key(t))
    save(fig, stem)


# ---------------------------------------------------------------- c: aggregate by scope
def aggregate(res, stem):
    rows = SET_ROWS
    n_r, n_c = len(rows), len(SCOPES)
    idx = res.set_index(["set", "scope_type", "scope"])
    fig, ax = plt.subplots(figsize=(1.0 * n_c + 4.2, 0.42 * n_r + 2.2))
    for i, (s, _, _) in enumerate(rows):
        for j, (st, sc, _) in enumerate(SCOPES):
            r = idx.loc[(s, st, sc)]
            n = int(r["n_testable"])
            if n == 0:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor=GRID, lw=0.6))
                ax.text(j + 0.5, i + 0.5, "no test", ha="center", va="center", fontsize=5, color=MUTED)
                continue
            fu, fd = r["frac_sig_up"], r["frac_sig_down"]
            ax.add_patch(Rectangle((j, i), 0.5, 1, facecolor=mix(UP, fu), edgecolor="white", lw=1.2))
            ax.add_patch(Rectangle((j + 0.5, i), 0.5, 1, facecolor=mix(DOWN, fd), edgecolor="white", lw=1.2))
            ax.text(j + 0.25, i + 0.42, f"{int(r['n_sig_up'])}", ha="center", va="center", fontsize=6.5,
                    color="white" if fu > 0.55 else INK)
            ax.text(j + 0.75, i + 0.42, f"{int(r['n_sig_down'])}", ha="center", va="center", fontsize=6.5,
                    color="white" if fd > 0.55 else INK)
            ax.text(j + 0.5, i + 0.85, f"n={n}", ha="center", va="center", fontsize=4.6, color=MUTED)
    band = [b for _, _, b in rows]
    start = 0
    for i in range(1, n_r + 1):
        if i == n_r or band[i] != band[start]:
            if i < n_r:
                ax.axhline(i, color=INK, lw=2.0 if band[i] in ("Failed references", "Broad stress") else 0.8)
            ax.text(-0.25, (start + i) / 2, band[start].replace(" ", "\n"), ha="center", va="center", fontsize=7,
                    fontweight="bold", color=INK, transform=ax.get_yaxis_transform())
            start = i
    for k in (4, 10):
        ax.axvline(k, color=INK, lw=0.9)
    for x, txt in ((2, "Light readings"), (7, "Non-light stress (by type)")):
        ax.text(x, -0.9, txt, ha="center", va="bottom", fontsize=7, color=INK)
    ax.set_xlim(0, n_c)
    ax.set_ylim(n_r, -0.2)
    ax.set_yticks(np.arange(n_r) + 0.5)
    ax.set_yticklabels([l.replace(" (kept;", "\n(kept;") for _, l, _ in rows], fontsize=7, color=INK)
    ax.set_xticks(np.arange(n_c) + 0.5)
    ax.set_xticklabels([l for _, _, l in SCOPES], fontsize=7, color=INK)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(handles=[Patch(facecolor=UP, label="left half: share of testable tests significant up"),
                       Patch(facecolor=DOWN, label="right half: share significant down")],
              loc="upper left", bbox_to_anchor=(0, -0.02), fontsize=6.5, frameon=False, ncol=2)
    ax.set_title("Share of testable tests with BH padj < 0.05, per gene set and reading scope (MED4)",
                 fontsize=9, loc="left", color=INK, pad=34)
    ax.annotate("Numbers = tests significant up | down; n = testable tests (fewer than 10 significant genes, not testable "
                "and descriptive tests excluded).\n" + DIRECTION_NOTE + " Light onset: treatment lit. Constant dark vs light: "
                "control lit. Schedule extension: extended light (treatment lit) and extended darkness (control lit) pooled, "
                "so its direction mixes lit arms.\nDCMU (no testable test) is not shown.",
                xy=(0, 0), xycoords="axes fraction", xytext=(0, -34), textcoords="offset points", fontsize=6,
                color=MUTED, va="top")
    save(fig, stem)


# ---------------------------------------------------------------- c2: per-experiment calls
def experiment_calls(calls, t, by, stem):
    cols = columns(t, by).drop_duplicates("experiment_id").reset_index(drop=True)
    rows = SET_ROWS
    idx = calls.drop_duplicates(["experiment_id", "set"]).set_index(["experiment_id", "set"])["experiment_call"]
    n_r, n_c = len(rows), len(cols)
    fig, ax = plt.subplots(figsize=(0.3 * n_c + 4.5, 0.32 * n_r + 2.0))
    for j, c in enumerate(cols.itertuples()):
        for i, (s, _, _) in enumerate(rows):
            call = idx.get((c.experiment_id, s), "not_tested")
            if call == "up":
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=UP, edgecolor="white", lw=1))
            elif call == "down":
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=DOWN, edgecolor="white", lw=1))
            elif call == "both":
                ax.add_patch(Rectangle((j, i), 1, 0.5, facecolor=UP, edgecolor="white", lw=1))
                ax.add_patch(Rectangle((j, i + 0.5), 1, 0.5, facecolor=DOWN, edgecolor="white", lw=1))
            elif call == "neither":
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor=NS, edgecolor="white", lw=1))
            else:
                ax.add_patch(Rectangle((j, i), 1, 1, facecolor="white", edgecolor="white", lw=1))
                ax.add_patch(Rectangle((j + 0.08, i + 0.08), 0.84, 0.84, facecolor="none", edgecolor="#c9c8c3",
                                       hatch="////", lw=0))
    band = [b for _, _, b in rows]
    for i in range(1, n_r):
        if band[i] != band[i - 1]:
            ax.axhline(i, color=INK, lw=2.0 if band[i] in ("Failed references", "Broad stress") else 0.8)
    ax.set_xlim(0, n_c)
    ax.set_ylim(n_r, 0)
    ax.set_yticks(np.arange(n_r) + 0.5)
    ax.set_yticklabels([l.replace(" (kept;", "\n(kept;") for _, l, _ in rows], fontsize=6.5, color=INK)
    ax.set_xticks(np.arange(n_c) + 0.5)
    ax.set_xticklabels(cols.label, rotation=90, fontsize=6, color=INK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    blocks(ax, cols.blockkey.tolist(), (lambda b: BLOCK_LABEL[b]) if by == "group" else (lambda v: f"{v} µmol"))
    ax.legend(handles=[Patch(facecolor=UP, label="up"), Patch(facecolor=DOWN, label="down"),
                       Patch(facecolor=UP, edgecolor=DOWN, label="both (upper up, lower down)"),
                       Patch(facecolor=NS, label="neither"),
                       Patch(facecolor="white", edgecolor="#c9c8c3", hatch="////", label="not tested")],
              loc="upper left", bbox_to_anchor=(1.005, 1), fontsize=6, frameon=False)
    ax.set_title("Per-experiment call per gene set (smallest time-point p × testable time points, then BH across "
                 "experiments per set; padj < 0.05)" + ("" if by == "group" else ", ordered by treatment-arm light level"),
                 fontsize=8.5, loc="left", color=INK, pad=38)
    caption(ax, DIRECTION_NOTE + " not tested = no testable time point.\n" + light_key(t), offset=-150)
    save(fig, stem)


def main():
    t = read("hli_tests.csv")
    gc = read("hli_gene_calls.csv")
    res = read("resemblance.csv")
    calls = read("experiment_calls.csv")
    for by in ("group", "light"):
        gene_heatmap(gc, t, by, FIG / f"hli_gene_heatmap_by_{by}")
        set_band(t, by, FIG / f"set_band_by_{by}")
        experiment_calls(calls, t, by, FIG / f"experiment_calls_by_{by}")
    aggregate(res, FIG / "aggregate_by_scope")
    print(sorted(p.name for p in FIG.iterdir()))


if __name__ == "__main__":
    main()
