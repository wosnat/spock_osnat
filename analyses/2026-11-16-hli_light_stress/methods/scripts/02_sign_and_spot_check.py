"""Methods step 4: photosystem II sign check, and spot check against pathway_enrichment.

4a  PSII genes' up / down / not-significant / not-in-table counts per timepoint in the
    extended light, extended darkness and Steglich high-white-light-vs-dark experiments.
4b  For one full-table experiment (N deprivation microarray, Tolonen 2006), our pipeline's
    Fisher p for photosystem_II and chaperones vs pathway_enrichment (cyanorak_role,
    term_ids J.8 / D.4, background table_scope).

Needs methods/data/control_tests.csv (from 03_run_controls.py) for 4b.
Writes methods/data/psii_sign_check.csv and methods/data/spot_check_pathway_enrichment.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/02_sign_and_spot_check.py
"""
import sys
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, pathway_enrichment

METHODS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(METHODS))
import kg_io  # noqa: E402

DATA = METHODS / "data"
SIGN_EXPS = {
    "10.64898/2026.04.15.718746_extended_light_med4": "Extended light",
    "10.64898/2026.04.15.718746_extended_darkness_med4": "Extended darkness",
    "10.1128/JB.01097-06_light_stress_high_white_light_55_med4_microarray": "High white 55 vs dark",
}
SPOT_EXP = "10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray"
SPOT_TERMS = {"cyanorak.role:J.8": "photosystem_II", "cyanorak.role:D.4": "chaperones"}


def main():
    sets = kg_io.load_gene_sets()
    psii = set(sets["photosystem_II"])
    ex = kg_io.load_experiments().set_index("experiment_id")
    rows = []
    with GraphConnection() as conn:
        for eid, label in SIGN_EXPS.items():
            de = kg_io.fetch_de(eid, conn)
            de = de[de.locus_tag.isin(psii)]          # PSII rows only
            de["timepoint"] = de["timepoint"].fillna("NA")
            for tp, g in de.groupby("timepoint", sort=False):
                st = g.expression_status
                up, down = int((st == "significant_up").sum()), int((st == "significant_down").sum())
                ns = int((st == "not_significant").sum())
                rows.append(dict(experiment_id=eid, label=label, timepoint=tp,
                                 treatment=ex.at[eid, "treatment_text"], control=ex.at[eid, "control_text"],
                                 light_treatment_umol=ex.at[eid, "light_treatment_umol"],
                                 light_control_umol=ex.at[eid, "light_control_umol"],
                                 orientation=ex.at[eid, "orientation"], psii_set_size=len(psii),
                                 n_up=up, n_down=down, n_ns_in_table=ns,
                                 n_not_in_table=len(psii) - g.locus_tag.nunique(),
                                 median_log2fc=float(g.log2fc.median())))
        sign = pd.DataFrame(rows)
        sign.to_csv(DATA / "psii_sign_check.csv", index=False, encoding="utf-8")
        pd.set_option("display.width", 250)
        print(sign.drop(columns=["experiment_id", "treatment", "control"]).to_string())

        pe = pathway_enrichment(organism="MED4", experiment_ids=[SPOT_EXP], ontology="cyanorak_role",
                                term_ids=list(SPOT_TERMS), direction="both", significant_only=True,
                                background="table_scope", min_gene_set_size=1, max_gene_set_size=None,
                                informative_only=False, conn=conn)
    r = pe.results.copy()
    print("pathway_enrichment params:", {k: pe.params.get(k) for k in
                                         ("background_mode", "n_clusters_tested", "n_clusters_skipped",
                                          "term2gene_row_count", "n_unique_terms")})
    print("clusters_skipped:", pe.clusters_skipped)
    r["set"] = r.term_id.map(SPOT_TERMS)
    r = r[["timepoint", "direction", "set", "count", "bg_count", "gene_ratio", "bg_ratio", "pvalue", "p_adjust"]]
    ours = pd.read_csv(DATA / "control_tests.csv", encoding="utf-8")
    ours = ours[(ours.experiment_id == SPOT_EXP) & ours.set.isin(SPOT_TERMS.values())]
    ours = ours[["timepoint", "direction", "set", "n_sig_in_set", "n_measured_in_background", "n_sig_total",
                 "background_size", "pvalue", "flags"]].rename(columns={"pvalue": "pvalue_ours"})
    m = ours.merge(r.rename(columns={"pvalue": "pvalue_pathway_enrichment",
                                     "count": "count_pe", "bg_count": "bg_count_pe"}),
                   on=["timepoint", "direction", "set"], how="outer")
    m["abs_diff"] = (m.pvalue_ours - m.pvalue_pathway_enrichment).abs()
    m.insert(0, "experiment_id", SPOT_EXP)
    m.to_csv(DATA / "spot_check_pathway_enrichment.csv", index=False, encoding="utf-8")
    print(m.drop(columns="experiment_id").to_string())


if __name__ == "__main__":
    main()
