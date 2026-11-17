"""A.9 (exploratory): ortholog-group breadth tiers for the MED4 hli genes, from data/og_conservation.csv
(15_og_conservation.py; KG genes_by_homolog_group + list_organisms clade). Display helper only.

Tier rule (coordinator update to A.9), in this order:
  1 picocyanobacteria-wide             n_synechococcus > 0
  4 HL Prochlorococcus only            n_pro_LL == 0
  2 Prochlorococcus-wide (HL + LL)     n_pro_HL >= 22 and n_pro_LL >= 19
  3 Prochlorococcus, partial           otherwise
Greys (darkest = widest): validated with the dataviz validator for adjacent-pair separation
(worst adjacent dE 17.3 normal / 17.2 deutan); lightness-band and chroma checks fail by design (neutral greys),
contrast WARN on the two light greys -> tier name is always in the legend and the hover.
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
TIER_NAME = {1: "picocyanobacteria-wide (Pro HL + LL, Syn, Cyanobium)",
             2: "Prochlorococcus-wide (HL + LL)",
             3: "Prochlorococcus, partial (HL + some LL)",
             4: "HL Prochlorococcus only"}
TIER_SHORT = {1: "picocyano-wide", 2: "Pro-wide", 3: "Pro partial", 4: "HL Pro only"}
TIER_GREY = {1: "#33322f", 2: "#62615c", 3: "#96958f", 4: "#cccbc6"}
LEGEND_TITLE = "ortholog-group breadth (exploratory)"
EXPECTED = {1: {"CK_00000050", "CK_00001058", "CK_00001414", "CK_00001313"},
            2: {"CK_00002025", "CK_00002026"},
            3: {"CK_00002661", "CK_00002332", "CK_00002168", "CK_00003573"},
            4: {"CK_00002103", "CK_00043616", "CK_00003510", "CK_00003421"}}


def tier(r) -> int:
    if r["n_synechococcus"] > 0:
        return 1
    if r["n_pro_LL"] == 0:
        return 4
    if r["n_pro_HL"] >= 22 and r["n_pro_LL"] >= 19:
        return 2
    return 3


def groups() -> pd.DataFrame:
    og = pd.read_csv(DATA / "og_conservation.csv", encoding="utf-8")
    og["ck"] = og.group.str.split(":").str[-1]
    og["tier"] = [tier(r) for r in og.to_dict("records")]
    got = {t: set(og[og.tier == t].ck) for t in TIER_NAME}
    assert got == EXPECTED, got
    og["tier_name"] = og.tier.map(TIER_NAME)
    og["tier_grey"] = og.tier.map(TIER_GREY)
    return og


def by_gene() -> pd.DataFrame:
    """One row per MED4 hli locus tag: ck, n_organisms, HL / LL / Syn / other counts, tier."""
    og = groups()
    rows = []
    for r in og.itertuples():
        for lt in r.med4_loci.split(";"):
            rows.append(dict(locus_tag=lt, ck=r.ck, n_organisms=int(r.n_organisms), n_pro_HL=int(r.n_pro_HL),
                             n_pro_LL=int(r.n_pro_LL), n_synechococcus=int(r.n_synechococcus), n_other=int(r.n_other),
                             med4_genes_in_group=int(r.med4_genes), tier=int(r.tier), tier_name=r.tier_name,
                             tier_grey=r.tier_grey))
    out = pd.DataFrame(rows)
    assert len(out) == 23 and out.locus_tag.is_unique, len(out)
    return out


def hover(r) -> str:
    return (f"{LEGEND_TITLE}: <b>{TIER_NAME[r['tier']]}</b><br>{r['ck']}: {r['n_organisms']} organisms "
            f"(Pro HL {r['n_pro_HL']}, Pro LL {r['n_pro_LL']}, Syn {r['n_synechococcus']}, other {r['n_other']})")


def mpl_strip(ax, genes, w_in=0.09, gap_in=0.03, side="left", pad=None):
    """Static figures: a tier-grey cell per gene row (rows at data y = i .. i+1), w_in inches wide, gap_in inches
    outside the axes on `side`. pad (points) moves the y tick labels clear of the strip."""
    from matplotlib.patches import Rectangle
    from matplotlib.transforms import blended_transform_factory
    t = by_gene().set_index("locus_tag")
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    ax_w = ax.get_position().width * ax.figure.get_figwidth()
    w = w_in / ax_w
    x = -(gap_in / ax_w) - w if side == "left" else 1 + gap_in / ax_w
    for i, g in enumerate(genes):
        ax.add_patch(Rectangle((x, i + 0.06), w, 0.88, transform=tr, facecolor=TIER_GREY[t.at[g, "tier"]],
                               edgecolor="none", clip_on=False))
    if pad is not None:
        ax.tick_params(axis="y", pad=pad)


def mpl_handles():
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    return [Line2D([], [], ls="", label=LEGEND_TITLE.upper())] + [
        Patch(facecolor=TIER_GREY[k], label="   " + TIER_NAME[k]) for k in TIER_NAME]
