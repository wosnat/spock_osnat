"""Methods step 1: gene sets and the 29 MED4 experiments.

Writes methods/data/gene_sets.csv and methods/data/experiments.csv.
No expression values are read here (metadata and gene lists only).

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/01_build_lists.py
"""
import sys
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, list_experiments, list_publications

METHODS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(METHODS))
import hli_scoring as hs  # noqa: E402
import kg_io  # noqa: E402

SPIKE = METHODS.parent / "spike" / "step2_med4_inventory.csv"
DATA = METHODS / "data"
DATA.mkdir(exist_ok=True)

# ---- experiment groups (proposal.md "What the KG holds") -------------------
GROUP = {
    "10.1128/JB.01097-06_light_stress_blue_light_13_umol_med4_microarray": "light_onset_photoperiod",
    "10.1128/JB.01097-06_light_stress_green_light_13_umol_med4_microarray": "light_onset_photoperiod",
    "10.1128/JB.01097-06_light_stress_high_white_light_55_med4_microarray": "light_onset_photoperiod",
    "10.1128/JB.01097-06_light_stress_red_light_13_umol_med4_microarray": "light_onset_photoperiod",
    "10.1128/JB.01097-06_light_stress_white_light_13_umol_med4_microarray": "light_onset_photoperiod",
    "10.1371/journal.pone.0165375_light_stress_constant_dark_med4_rnaseq_dark": "light_onset_photoperiod",
    "10.1371/journal.pone.0165375_light_stress_constant_dark_med4_rnaseq_infected": "light_onset_photoperiod",
    "10.64898/2026.04.15.718746_extended_light_med4": "light_onset_photoperiod",
    "10.64898/2026.04.15.718746_extended_darkness_med4": "light_onset_photoperiod",
    "10.1128/JB.01097-06_light_stress_dcmu_white_light_13_med4_microarray": "electron_transport_DCMU",
    "10.1371/journal.pone.0165375_viral_phage_phm2_lysate_med4_rnaseq_dark": "phage_dark",
    "10.1038/ismej.2015.36_carbon_ambient_co2_no_o2_med4_microarray": "nonlight_stress",
    "10.1038/ismej.2015.36_carbon_low_co2_0004_co2_med4_microarray": "nonlight_stress",
    "10.1038/ismej.2015.36_carbon_low_co2_and_no_med4_microarray": "nonlight_stress",
    "10.1038/ismej.2011.49_iron_iron_starvation_med4_med4_microarray_light": "nonlight_stress",
    "10.1038/ismej.2017.88_nitrogen_stress_ndepleted_pro99_medium_med4_rnaseq": "nonlight_stress",
    "10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray": "nonlight_stress",
    "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_axenic": "nonlight_stress",
    "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture": "nonlight_stress",
    "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray": "nonlight_stress",
    "10.3389/fmicb.2022.1038136_salt_low_salinity_acclimation_28_med4_rnaseq": "nonlight_stress",
    "10.1038/nature06130_viral_phage_infected_med4_microarray": "nonlight_stress",
    "10.1371/journal.pone.0165375_viral_phage_phm2_lysate_med4_rnaseq_light": "nonlight_stress",
    "10.1038/ismej.2015.36_carbon_air_0036_co2_21_med4_microarray": "nonstress_possible_relief",
    "10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_med4_rnaseq": "nonstress_possible_relief",
    "10.1101/2025.11.24.690089_coculture_alteromonas_hot1a3_med4_rnaseq": "nonstress_possible_relief",
    "10.1038/ismej.2011.49_iron_rescue_med4_microarray": "nonstress_possible_relief",
    "10.1038/msb4100087_growth_medium_growth_on_cyanate_as_med4_microarray": "nonstress_possible_relief",
    "10.1038/msb4100087_growth_medium_growth_on_urea_as_med4_microarray": "nonstress_possible_relief",
}
LABEL = {
    "10.1128/JB.01097-06_light_stress_blue_light_13_umol_med4_microarray": "Blue 13 vs dark",
    "10.1128/JB.01097-06_light_stress_green_light_13_umol_med4_microarray": "Green 13 vs dark",
    "10.1128/JB.01097-06_light_stress_high_white_light_55_med4_microarray": "High white 55 vs dark",
    "10.1128/JB.01097-06_light_stress_red_light_13_umol_med4_microarray": "Red 13 vs dark",
    "10.1128/JB.01097-06_light_stress_white_light_13_umol_med4_microarray": "White 13 vs dark",
    "10.1371/journal.pone.0165375_light_stress_constant_dark_med4_rnaseq_dark": "Const dark vs light (no phage)",
    "10.1371/journal.pone.0165375_light_stress_constant_dark_med4_rnaseq_infected": "Const dark vs light (phage)",
    "10.64898/2026.04.15.718746_extended_light_med4": "Extended light",
    "10.64898/2026.04.15.718746_extended_darkness_med4": "Extended darkness",
    "10.1128/JB.01097-06_light_stress_dcmu_white_light_13_med4_microarray": "DCMU + white 13 vs white 13",
    "10.1371/journal.pone.0165375_viral_phage_phm2_lysate_med4_rnaseq_dark": "Phage lysate (dark)",
    "10.1038/ismej.2015.36_carbon_ambient_co2_no_o2_med4_microarray": "CO2: ambient, no O2",
    "10.1038/ismej.2015.36_carbon_low_co2_0004_co2_med4_microarray": "CO2: low",
    "10.1038/ismej.2015.36_carbon_low_co2_and_no_med4_microarray": "CO2: low, no O2",
    "10.1038/ismej.2011.49_iron_iron_starvation_med4_med4_microarray_light": "Iron starvation",
    "10.1038/ismej.2017.88_nitrogen_stress_ndepleted_pro99_medium_med4_rnaseq": "N-depleted (RNA-seq, top 50%)",
    "10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray": "N deprivation (array)",
    "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_axenic": "N starvation lowN (axenic)",
    "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture": "N starvation lowN (coculture)",
    "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray": "Phosphate starvation",
    "10.3389/fmicb.2022.1038136_salt_low_salinity_acclimation_28_med4_rnaseq": "Low salinity 28 psu",
    "10.1038/nature06130_viral_phage_infected_med4_microarray": "Phage infection (array, up-only)",
    "10.1371/journal.pone.0165375_viral_phage_phm2_lysate_med4_rnaseq_light": "Phage lysate (light)",
    "10.1038/ismej.2015.36_carbon_air_0036_co2_21_med4_microarray": "Air vs time 0",
    "10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_med4_rnaseq": "Coculture HOT1A3 (2016)",
    "10.1101/2025.11.24.690089_coculture_alteromonas_hot1a3_med4_rnaseq": "Coculture HOT1A3 vs axenic (2025)",
    "10.1038/ismej.2011.49_iron_rescue_med4_microarray": "Iron re-added",
    "10.1038/msb4100087_growth_medium_growth_on_cyanate_as_med4_microarray": "Cyanate as N source",
    "10.1038/msb4100087_growth_medium_growth_on_urea_as_med4_microarray": "Urea as N source",
}
# darkness is the treatment -> flip so that "up" reads "more light"
ORIENTATION_NEG = {
    "10.64898/2026.04.15.718746_extended_darkness_med4",
    "10.1371/journal.pone.0165375_light_stress_constant_dark_med4_rnaseq_dark",
    "10.1371/journal.pone.0165375_light_stress_constant_dark_med4_rnaseq_infected",
}
UP_ONLY = {"10.1038/nature06130_viral_phage_infected_med4_microarray"}
# in-table sensitivity background: union of genes over one multi-condition significance table
IN_TABLE_GROUP = {
    **{e: "steglich2006_any_of_6_light" for e in GROUP if e.startswith("10.1128/JB.01097-06")},
    **{e: "bagby2015_any_of_4_gas" for e in GROUP if e.startswith("10.1038/ismej.2015.36")},
    "10.1038/ismej.2011.49_iron_iron_starvation_med4_med4_microarray_light": "thompson2011_iron_any_timepoint",
    "10.1038/ismej.2011.49_iron_rescue_med4_microarray": "thompson2011_iron_any_timepoint",
    "10.1038/nature06130_viral_phage_infected_med4_microarray": "lindell2007_up_any_timepoint",
}
DESCRIPTIVE = {"10.1038/ismej.2017.88_nitrogen_stress_ndepleted_pro99_medium_med4_rnaseq"}
# phosphate table holds genes with q<0.05 at 48 h only: approximate at 48 h, descriptive at other times
PHOSPHATE = "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray"


def main():
    with GraphConnection() as conn:
        # ---- gene sets
        hli = kg_io.fetch_hli(conn)
        hli_tags = sorted(set(hli["locus_tag"]))
        assert len(hli_tags) == 23, len(hli_tags)
        assert hli.groupby("locus_tag")["group_id"].nunique().max() == 1, "hli gene in >1 group"
        rows = [dict(locus_tag=r.locus_tag, set="hli", role="target", term_id="", gene_name=r.gene_name,
                     product=r.product) for r in hli.drop_duplicates("locus_tag").itertuples()]
        rows += [dict(locus_tag=r.locus_tag, set=f"hli_group:{r.group_id}", role="target_group", term_id="",
                      gene_name=r.gene_name, product=r.product) for r in hli.itertuples()]
        for name, term in kg_io.COMPARISON_ROLES.items():
            df = kg_io.fetch_role_set(term, conn)
            if name in kg_io.MINUS_HLI:
                n_before = len(df)
                df = df[~df.locus_tag.isin(hli_tags)]
                print(f"{name}: {term} has {n_before} genes; {n_before - len(df)} hli removed -> {len(df)}")
                assert len(df) == 12, len(df)
            assert not set(df["locus_tag"]) & set(hli_tags), f"{name} overlaps hli"
            rows += [dict(locus_tag=r.locus_tag, set=name, role=kg_io.SET_ROLE[name], term_id=term,
                          gene_name=r.gene_name, product=r.product) for r in df.itertuples()]
        gs = pd.DataFrame(rows).sort_values(["set", "locus_tag"])
        gs.to_csv(DATA / "gene_sets.csv", index=False, encoding="utf-8")
        print("gene sets:", gs.groupby("set").size().to_dict())
        # pairwise overlaps among hli + reference sets (reported, not removed)
        names = ["hli"] + kg_io.COMPARISON_SETS
        mem = {s: set(gs.loc[gs.set == s, "locus_tag"]) for s in names}
        ov = pd.DataFrame([dict(set_a=a, set_b=b, size_a=len(mem[a]), size_b=len(mem[b]),
                                n_overlap=len(mem[a] & mem[b]),
                                overlap_genes=" ".join(sorted(mem[a] & mem[b])))
                           for i, a in enumerate(names) for b in names[i + 1:]])
        ov.to_csv(DATA / "gene_set_overlaps.csv", index=False, encoding="utf-8")
        print(ov[ov.n_overlap > 0].to_string())

        # ---- experiments
        inv = pd.read_csv(SPIKE, encoding="utf-8")
        keep = inv[(inv.proposed_group != "excluded") & (~inv.omics_type.str.contains("PROTEOMICS"))
                   & (~inv.experiment_name.str.lower().str.contains("glucose"))]
        ids = keep.experiment_id.tolist()
        assert len(ids) == 29, len(ids)
        assert set(ids) == set(GROUP), set(ids) ^ set(GROUP)
        meta = list_experiments(experiment_ids=ids, verbose=True, limit=None, conn=conn)
        assert meta["total_matching"] == len(meta["results"]) == 29
        pubs = list_publications(organism="MED4", limit=None, conn=conn)
        study = {p["doi"]: f"{p['authors'][0].split()[-1]} {p['year']}" for p in pubs["results"]}

    out = []
    for e in meta["results"]:
        eid = e["experiment_id"]
        tps = e.get("timepoints") or []
        light = hs.arm_light_levels(e.get("treatment"), e.get("control"),
                                    e.get("light_condition"), e.get("light_intensity"))
        if eid in DESCRIPTIVE:
            test_type = "descriptive"
        elif e["table_scope"] == "all_detected_genes":
            test_type = "sound"
        else:
            test_type = "approximate"
        out.append(dict(
            experiment_id=eid, label=LABEL[eid], group=GROUP[eid],
            study=study.get(e["publication_doi"], e["publication_doi"]),
            publication_doi=e["publication_doi"],
            stress_type=",".join(e["treatment_type"]), omics=e["omics_type"],
            table_scope=e["table_scope"], table_scope_detail=e.get("table_scope_detail") or "",
            test_type=test_type,
            test_type_note=("approximate at 48h; descriptive at other timepoints (table filtered on 48h q<0.05)"
                            if eid == PHOSPHATE else ""),
            up_only=eid in UP_ONLY,
            orientation=-1 if eid in ORIENTATION_NEG else 1,
            in_table_group=IN_TABLE_GROUP.get(eid, ""),
            control_timing=e.get("control_timing"),
            treatment_text=e.get("treatment"), control_text=e.get("control"),
            light_condition_raw=e.get("light_condition"), light_intensity_raw=e.get("light_intensity"),
            **light,
            n_timepoints=len(tps) or 1,
            timepoints=" | ".join(t["timepoint"] for t in sorted(tps, key=lambda t: t["timepoint_order"])) or "NA",
            distinct_gene_count=e["distinct_gene_count"],
            experiment_name=e["experiment_name"],
        ))
    ex = pd.DataFrame(out)
    order = ["light_onset_photoperiod", "electron_transport_DCMU", "phage_dark", "nonlight_stress",
             "nonstress_possible_relief"]
    ex["group_rank"] = ex.group.map({g: i for i, g in enumerate(order)})
    ex = ex.sort_values(["group_rank", "stress_type", "label"]).drop(columns="group_rank")
    ex.to_csv(DATA / "experiments.csv", index=False, encoding="utf-8")
    print(f"experiments: {len(ex)}")
    print(ex.groupby("group").size().to_string())
    print(ex[["label", "light_treatment_umol", "light_control_umol", "light_treatment_source",
              "light_control_source", "light_treatment_note", "light_control_note",
              "light_parse_flag"]].to_string())


if __name__ == "__main__":
    main()
