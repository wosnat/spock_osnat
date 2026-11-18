"""Paper Table 1: the two hli gene groups (exploratory) and how cluster, copy number and ortholog-group breadth line up.

Groups: responders = clusters C3 + C4; quiet = C1 + C2 (cluster calls from explore_D_gene_clusters.csv via
explore_D5_conservation.csv). Per-group condition counts are summed from explore_D_cluster_response.csv.
Reads local data only; nothing is recomputed. Writes data/paper_table1_gene_groups.csv and
data/paper_table1_condition_counts.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/24_paper_gene_groups.py
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import conservation as cons  # noqa: E402

DATA = HERE.parent / "data"
GROUP = {1: "quiet", 2: "quiet", 3: "responders", 4: "responders"}

d5 = pd.read_csv(DATA / "explore_D5_conservation.csv", encoding="utf-8")
d5["group"] = d5.cluster.map(GROUP)
rows = []
for g, x in d5.groupby("group"):
    tiers = "; ".join(f"{cons.TIER_SHORT[t]} {int((x.tier == t).sum())}" for t in sorted(cons.TIER_NAME) if (x.tier == t).any())
    clus = "; ".join(f"C{c} {int((x.cluster == c).sum())}" for c in sorted(x.cluster.unique()))
    rows.append(dict(group=g, n_genes=len(x), clusters=clus, n_multi=int((x.copy_class == "multi").sum()),
                     n_single=int((x.copy_class == "single").sum()), tiers=tiers,
                     median_pct_up=x.pct_up.median(), min_pct_up=x.pct_up.min(), max_pct_up=x.pct_up.max(),
                     median_pct_up_rnaseq=x.pct_up_rnaseq.median(),
                     genes=" ".join(x.sort_values(["cluster", "locus_tag"]).locus_tag)))
t1 = pd.DataFrame(rows)
t1.to_csv(DATA / "paper_table1_gene_groups.csv", index=False, encoding="utf-8")

cr = pd.read_csv(DATA / "explore_D_cluster_response.csv", encoding="utf-8")
cr["group"] = cr.cluster.map(GROUP)
cc = (cr.groupby(["group", "cluster", "type"]).agg(n_up=("n_up", "sum"), n_up_defined=("n_up_defined", "sum"),
                                                   n_down=("n_down", "sum"), n_down_defined=("n_down_defined", "sum"))
      .reset_index())
cc.to_csv(DATA / "paper_table1_condition_counts.csv", index=False, encoding="utf-8")
pd.set_option("display.width", 250)
print(t1.drop(columns="genes").to_string(index=False))
g = cc.groupby(["group", "type"])[["n_up", "n_up_defined", "n_down", "n_down_defined"]].sum()
print(g.to_string())
