"""Twin rule step 1: detect identical-signal hli pairs and count the cells the rule recodes.

Input: analysis/data/hli_gene_calls.csv. Writes analysis/data/explore_twin_pairs.csv (one row per detected pair),
explore_twin_pairs_by_experiment.csv (identical / differing shared cells per pair x experiment) and
explore_twin_recoded_counts.csv (recoded cells per experiment).

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/12_twin_pairs.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import twin_rule as tw  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"


def main():
    gc = pd.read_csv(DATA / "hli_gene_calls.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    pairs, per = tw.detect_pairs(gc)
    pairs.to_csv(DATA / "explore_twin_pairs.csv", index=False, encoding="utf-8")
    per.to_csv(DATA / "explore_twin_pairs_by_experiment.csv", index=False, encoding="utf-8")
    rc = tw.apply(gc, pairs)
    cnt = (rc[rc.twin_recoded].groupby(["experiment_id", "label"]).size().rename("n_cells_recoded").reset_index()
           .sort_values("n_cells_recoded", ascending=False))
    cnt.to_csv(DATA / "explore_twin_recoded_counts.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 200)
    print(pairs.to_string(index=False))
    print(cnt.to_string(index=False), "| total", int(cnt.n_cells_recoded.sum()))
    print(rc[rc.twin_recoded].groupby("locus_tag").size().to_string())


if __name__ == "__main__":
    main()
