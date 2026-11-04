"""THROWAWAY pilot figures for MIT9313 (no KG calls). Reuses a03 drawing functions unchanged in logic.
(a) mit9313_step_matrix: step tiles for MIT9313.
(b) med4_mit9313_hot1a3_status: 3 x 20 per-amino-acid status tiles with package/lone markers and gene counts.
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/spike/mit9313/scripts/m03_figures.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ALT = HERE.parent / "alteromonas_hot1a3"
spec = importlib.util.spec_from_file_location("a03", ALT / "scripts" / "a03_figures.py")
a03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a03)
a03.FIG = HERE / "figures"
DATA = HERE / "data"


def main():
    hits = pd.read_csv(DATA / "hits.csv", encoding="utf-8")
    summ = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    st = a03.step_table(hits[hits.amino_acid.isin(a03.AAS)])
    ded = st[st.flag == "dedicated"]
    summ["n_observable_dedicated"] = int(ded.observable.sum())
    st.to_csv(DATA / "mit9313_step_matrix.csv", index=False, encoding="utf-8")
    aa_t = pd.read_csv(DATA / "aa_status.csv", encoding="utf-8")
    a03.fig_matrix(st, aa_t, summ, key="MIT9313", org_full="Prochlorococcus MIT9313 (LLIV)", stem="mit9313_step_matrix")

    aa_m = pd.read_csv(ALT / "data" / "aa_status_med4.csv", encoding="utf-8")
    aa_a = pd.read_csv(ALT / "data" / "aa_status.csv", encoding="utf-8")
    oc = pd.concat([pd.read_csv(ALT / "data" / "operon_calls.csv", encoding="utf-8"),
                    pd.read_csv(DATA / "operon_calls.csv", encoding="utf-8")], ignore_index=True)
    gc = {k: v[0][1] for k, v in summ["gene_counts"].items()}
    rows = [(f"Prochlorococcus MED4 (HLI)\n{gc['MED4']:,} genes", aa_m, "MED4"),
            (f"Prochlorococcus MIT9313 (LLIV)\n{gc['MIT9313']:,} genes", aa_t, "MIT9313"),
            (f"Alteromonas HOT1A3 (reference)\n{gc['HOT1A3']:,} genes", aa_a, "HOT1A3")]
    a03.fig_compare(aa_m, aa_a, oc, rows=rows, stem="med4_mit9313_hot1a3_status",
                    title="Amino-acid breakdown pathways: MED4 vs MIT9313, HOT1A3 as reference "
                          "(pathway-level status, draft catalogue)")
    print("step matrix rows:", len(st), "| dedicated:", len(ded), "| observable:", int(ded.observable.sum()),
          "| dedicated found:", int(ded.present.sum()), "| shared found:", int(st[st.flag == "shared"].present.sum()),
          "of", int((st.flag == "shared").sum()))


if __name__ == "__main__":
    main()
