"""Exploration E (decision A.11, exploratory, protein layer): MED4 iTRAQ proteomics, HL (100) vs LL (20 uE) and
ML (60) vs LL (20 uE) (Pandhal 2007, 10.1021/pr060460c).

Pulls all DE rows of both experiments (differential_expression_by_gene, limit=None, asserts no truncation) and the
experiment metadata (list_experiments, verbose). Reports hli proteins quantified, per-gene call and log2FC, twin-pair
identity, and reference-set counts (up / down / ns of quantified). Fisher ORA (fisher_ora, background = quantified
proteins) is run only if the table is full and >= 10 proteins are significant in a direction (gate recorded).

Writes analysis/data/explore_E_prot_experiments.csv, explore_E_prot_de.csv (all rows), explore_E_prot_hli.csv,
explore_E_prot_twins.csv, explore_E_prot_sets.csv, explore_E_prot_ora_gate.csv; figure explore_E4_proteomics.{png,svg}.
Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/23_explore_proteomics.py
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from multiomics_explorer import differential_expression_by_gene, list_experiments  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "methods"))
import conservation as cons  # noqa: E402
import kg_io  # noqa: E402

DATA, FIG = HERE.parent / "data", HERE.parent / "figures"
UP, DOWN, MID, INK, MUTED = "#eb6834", "#2a78d6", "#f0efec", "#1f1f1d", "#6b6b66"
EXPS = [("10.1021/pr060460c_light_HL_vs_LL_med4_proteomics", "HL 100 vs LL 20"),
        ("10.1021/pr060460c_light_ML_vs_LL_med4_proteomics", "ML 60 vs LL 20")]
SETS = [("hli", "hli"), ("photosystem_I", "PSI"), ("photosystem_II", "PSII"), ("ribosomal_proteins", "Ribosomal"),
        ("co2_fixation", "CO2 fixation")]
TWINS = [("PMM0815", "PMM1396"), ("PMM0816", "PMM1397"), ("PMM0817", "PMM1398"), ("PMM0818", "PMM1399")]
W = 7.2
plt.rcParams.update({"font.size": 8, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
                     "svg.fonttype": "none", "axes.linewidth": 0.6})


def main():
    meta = list_experiments(experiment_ids=[e for e, _ in EXPS], verbose=True, limit=None)
    assert meta["total_matching"] == len(meta["results"]) == 2
    m = pd.DataFrame(meta["results"])
    keep = ["experiment_id", "experiment_name", "omics_type", "is_time_course", "table_scope", "table_scope_detail",
            "control_timing", "gene_count", "treatment", "control", "light_condition", "light_intensity", "statistical_test",
            "experimental_context", "genes_by_status"]
    m = m[[c for c in keep if c in m.columns]].copy()
    m["genes_by_status"] = m.genes_by_status.map(json.dumps)
    m.to_csv(DATA / "explore_E_prot_experiments.csv", index=False, encoding="utf-8")
    rows = []
    for e, lab in EXPS:
        r = differential_expression_by_gene(experiment_ids=[e], limit=None, verbose=True)
        assert r["total_matching"] == len(r["results"]), (e, r["total_matching"], len(r["results"]))
        d = pd.DataFrame(r["results"])
        d["contrast"] = lab
        rows.append(d)
        print(e, "rows:", r["total_matching"], "timepoints:", sorted(d.timepoint.astype(str).unique()))
    de = pd.concat(rows, ignore_index=True)
    de["call"] = de.expression_status.map({"significant_up": "up", "significant_down": "down", "not_significant": "ns"})
    assert de.call.notna().all(), de.expression_status.unique()
    keepc = [c for c in ["contrast", "experiment_id", "locus_tag", "gene_name", "timepoint", "expression_status", "call",
                         "log2fc", "padj"] if c in de.columns]
    de[keepc].to_csv(DATA / "explore_E_prot_de.csv", index=False, encoding="utf-8")

    sets = kg_io.load_gene_sets()
    dc = pd.read_csv(DATA / "explore_D_gene_clusters.csv", encoding="utf-8").sort_values("leaf_order")
    genes = dc.locus_tag.tolist()
    assert set(genes) == set(sets["hli"])
    h = []
    for g in genes:
        for _, lab in EXPS:
            x = de[(de.contrast == lab) & (de.locus_tag == g)]
            assert len(x) <= 1
            h.append(dict(locus_tag=g, D_cluster=int(dc.set_index("locus_tag").at[g, "cluster"]),
                          copy_class=dc.set_index("locus_tag").at[g, "copy_class"], contrast=lab, quantified=len(x) == 1,
                          call=x.call.iloc[0] if len(x) else "not_quantified",
                          log2fc=float(x.log2fc.iloc[0]) if len(x) else np.nan,
                          padj=float(x.padj.iloc[0]) if len(x) and pd.notna(x.padj.iloc[0]) else np.nan))
    h = pd.DataFrame(h)
    h.to_csv(DATA / "explore_E_prot_hli.csv", index=False, encoding="utf-8")
    tw = []
    for a, b in TWINS:
        for _, lab in EXPS:
            xa = de[(de.contrast == lab) & (de.locus_tag == a)]
            xb = de[(de.contrast == lab) & (de.locus_tag == b)]
            tw.append(dict(pair=f"{a}/{b}", contrast=lab, a_quantified=len(xa) == 1, b_quantified=len(xb) == 1,
                           log2fc_a=xa.log2fc.iloc[0] if len(xa) else np.nan, log2fc_b=xb.log2fc.iloc[0] if len(xb) else np.nan,
                           identical=(len(xa) == 1 and len(xb) == 1 and round(xa.log2fc.iloc[0], 6) == round(xb.log2fc.iloc[0], 6))))
    pd.DataFrame(tw).to_csv(DATA / "explore_E_prot_twins.csv", index=False, encoding="utf-8")
    st = []
    gate = []
    for _, lab in EXPS:
        d = de[de.contrast == lab]
        q = set(d.locus_tag)
        for s, slab in SETS:
            x = d[d.locus_tag.isin(sets[s])]
            st.append(dict(contrast=lab, set=s, set_label=slab, set_size=len(sets[s]), n_quantified=len(x),
                           n_up=int((x.call == "up").sum()), n_down=int((x.call == "down").sum()),
                           n_ns=int((x.call == "ns").sum())))
        nu, nd = int((d.call == "up").sum()), int((d.call == "down").sum())
        gate.append(dict(contrast=lab, n_quantified=len(q), n_sig_up=nu, n_sig_down=nd,
                         table_full=True, ora_run_up=nu >= 10, ora_run_down=nd >= 10,
                         note="ORA run only with >= 10 significant proteins in a direction (A.11)"))
    st = pd.DataFrame(st)
    st.to_csv(DATA / "explore_E_prot_sets.csv", index=False, encoding="utf-8")
    gate = pd.DataFrame(gate)
    gate.to_csv(DATA / "explore_E_prot_ora_gate.csv", index=False, encoding="utf-8")
    assert not (gate.ora_run_up.any() or gate.ora_run_down.any()), "gate passed: implement ORA"

    # ---- E4
    nr = len(genes)
    H = 5.4
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([1.75 / W, 0.95 / H, 1.3 / W, (H - 1.35) / H])
    vmax = np.nanmax(np.abs(h.log2fc)) if h.log2fc.notna().any() else 1.0
    vmax = max(vmax, 0.5)
    cmap = LinearSegmentedColormap.from_list("div", [DOWN, MID, UP])
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    hi = h.set_index(["locus_tag", "contrast"])
    for i, g in enumerate(genes):
        for j, (_, lab) in enumerate(EXPS):
            r = hi.loc[(g, lab)]
            if not r.quantified:
                ax.add_patch(Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, facecolor="white", edgecolor="#d9d8d4", hatch="////", lw=0.4))
            else:
                ax.add_patch(Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, facecolor=cmap(norm(r.log2fc)), edgecolor="none"))
                if r.call in ("up", "down"):
                    ax.text(j + 0.5, i + 0.55, "*", ha="center", va="center", fontsize=10, color=INK)
    cls = dc.cluster.tolist()
    s0 = 0
    tr = ax.get_yaxis_transform()
    for i in range(1, nr + 1):
        if i == nr or cls[i] != cls[s0]:
            if i < nr:
                ax.axhline(i, color=INK, lw=0.8)
            ax.plot([-0.9, -0.9], [s0 + 0.15, i - 0.15], color=INK, lw=1.0, transform=tr, clip_on=False)
            ax.text(-0.93, (s0 + i) / 2, f"C{cls[s0]}", ha="right", va="center", fontsize=8, fontweight="bold", transform=tr)
            s0 = i
    ax.set_xlim(0, 2)
    ax.set_ylim(nr, 0)
    ax.set_yticks(np.arange(nr) + 0.5)
    ax.set_yticklabels(genes)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([0.5, 1.5])
    ax.set_xticklabels(["HL 100\nvs LL 20", "ML 60\nvs LL 20"])
    ax.xaxis.tick_top()
    ax.tick_params(axis="x", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    cax = fig.add_axes([1.75 / W, 0.45 / H, 1.3 / W, 0.1 / H])
    cax.imshow(np.linspace(-vmax, vmax, 100)[None, :], aspect="auto", cmap=cmap, norm=norm, extent=(-vmax, vmax, 0, 1))
    cax.set_yticks([])
    cax.set_xticks([-round(vmax, 1), 0, round(vmax, 1)])
    cax.set_title("protein log2FC (* = significant)", fontsize=8, loc="left", pad=2)
    fig.legend(handles=[Patch(facecolor="white", edgecolor="#b5b4ae", hatch="////", label="not quantified")],
               loc="lower left", bbox_to_anchor=(0.01, 0.0), frameon=False, fontsize=8)
    fig.text(0.02, 1 - 0.1 / H, "a", fontsize=11, fontweight="bold", va="top")
    # reference-set counts
    bx = fig.add_axes([4.6 / W, 0.95 / H, 2.4 / W, (H - 1.35) / H])
    labels = []
    y = 0
    for s, slab in SETS:
        for _, lab in EXPS:
            r = st[(st.set == s) & (st.contrast == lab)].iloc[0]
            left = 0
            for n, col in ((r.n_up, UP), (r.n_down, DOWN), (r.n_ns, "#d9d8d4")):
                if n:
                    bx.barh(y, n, left=left, color=col, height=0.7, edgecolor="white", lw=0.8)
                left += n
            bx.text(left + 0.3, y, f"{r.n_up}/{r.n_down}/{r.n_ns} of {r.set_size}", va="center", fontsize=8)
            labels.append(f"{slab} · {lab.split(' vs')[0]}")
            y += 1
        y += 0.4
    ys = [i + 0.4 * (i // 2) for i in range(len(labels))]
    bx.set_yticks(ys)
    bx.set_yticklabels(labels)
    bx.invert_yaxis()
    bx.set_xlabel("proteins quantified")
    for sp in ("top", "right"):
        bx.spines[sp].set_visible(False)
    bx.set_xlim(0, max(st.n_quantified.max(), 1) * 1.6)
    bx.legend(handles=[Patch(facecolor=UP, label="up"), Patch(facecolor=DOWN, label="down"), Patch(facecolor="#d9d8d4", label="ns")],
              loc="upper right", frameon=False, fontsize=8)
    fig.text(3.2 / W, 1 - 0.1 / H, "b", fontsize=11, fontweight="bold", va="top")
    fig.savefig(FIG / "explore_E4_proteomics.png", dpi=300)
    fig.savefig(FIG / "explore_E4_proteomics.svg")
    plt.close(fig)
    pd.set_option("display.width", 250)
    print(m.drop(columns=["experimental_context"]).T.to_string())
    print(h[h.quantified].to_string(index=False))
    print("hli quantified per contrast:", h[h.quantified].groupby("contrast").size().to_dict())
    print(pd.DataFrame(tw).to_string(index=False))
    print(st.to_string(index=False))
    print(gate.to_string(index=False))


if __name__ == "__main__":
    main()
