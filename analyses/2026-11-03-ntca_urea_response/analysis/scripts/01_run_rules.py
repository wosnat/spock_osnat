"""Apply the proposal's decision rules to the six experiments; write data/*.csv."""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]          # analysis/
sys.path.insert(0, str(HERE.parent / "methods"))
import ntca_urea as m  # noqa: E402

DATA = HERE / "data"
DATA.mkdir(exist_ok=True)
P = "10.1038/msb4100087_"
EXP = {
    "med4_urea": P + "growth_medium_growth_on_urea_as_med4_microarray",
    "med4_cyanate": P + "growth_medium_growth_on_cyanate_as_med4_microarray",
    "med4_ndep": P + "nitrogen_nitrogen_deprivation_med4_med4_microarray",
    "mit9313_urea": P + "growth_medium_growth_on_urea_as_mit9313_microarray",
    "mit9313_nitrite": P + "growth_medium_growth_on_nitrite_as_mit9313_microarray",
    "mit9313_ndep": P + "nitrogen_nitrogen_deprivation_mit9313_mit9313_microarray",
}
STRAIN = {
    "MED4": dict(ntca="PMM0246", urea="med4_urea", alt="med4_cyanate", ndep="med4_ndep",
                 ndep_tps=["6h", "12h", "24h", "48h"],
                 ure=[f"PMM{n:04d}" for n in range(963, 971)] + ["PMM0972", "PMM0973", "PMM0974"],
                 other=["PMM0263", "PMM0920", "PMM1463", "PMM0393"]),
    "MIT9313": dict(ntca="PMT1831", urea="mit9313_urea", alt="mit9313_nitrite", ndep="mit9313_ndep",
                    ndep_tps=["6h", "12h", "48h"],
                    ure=[f"PMT{n}" for n in range(2230, 2237)] + ["PMT2229", "PMT2225", "PMT2226", "PMT2227"],
                    other=["PMT1853", "PMT0601", "PMT1481", "PMT0205"]),
}

# ---- fetch -------------------------------------------------------------------
df = {}
for k, e in EXP.items():
    d = m.add_abs_rank_pct(m.fetch_de([e]))
    d.insert(0, "experiment_key", k)
    df[k] = d
    print(k, "rows", len(d), "genes", d["locus_tag"].nunique())

# ---- identity gate (MED4 cyanate vs MED4 urea) --------------------------------
a, b = df["med4_urea"], df["med4_cyanate"]
gate_fired = m.identity_gate(a, b)
j = a[["locus_tag", "log2fc", "expression_status"]].merge(
    b[["locus_tag", "log2fc", "expression_status"]], on="locus_tag", suffixes=("_urea", "_cyanate"))
def sig(d, s): return set(d.loc[d["expression_status"] == s, "locus_tag"])
gate = pd.DataFrame([dict(
    experiment_a=EXP["med4_urea"], experiment_b=EXP["med4_cyanate"],
    n_shared_genes=len(j),
    n_identical_log2fc=int((j["log2fc_urea"] == j["log2fc_cyanate"]).sum()),
    n_identical_status=int((j["expression_status_urea"] == j["expression_status_cyanate"]).sum()),
    pearson_r_log2fc=float(j["log2fc_urea"].corr(j["log2fc_cyanate"])),
    n_up_urea=len(sig(a, m.UP)), n_up_cyanate=len(sig(b, m.UP)),
    n_up_overlap=len(sig(a, m.UP) & sig(b, m.UP)),
    n_down_urea=len(sig(a, m.DOWN)), n_down_cyanate=len(sig(b, m.DOWN)),
    n_down_overlap=len(sig(a, m.DOWN) & sig(b, m.DOWN)),
    gate_fired=gate_fired)])
gate.to_csv(DATA / "qc_identity_gate.csv", index=False, encoding="utf-8")

# ---- controls, ntcA rows, readings, gene table --------------------------------
controls, ntca_rows, readings, genes = [], [], [], []
COLS = ["experiment_key", "experiment_id", "timepoint", "locus_tag", "gene_name",
        "log2fc", "padj", "expression_status", "abs_rank_pct"]
for strain, s in STRAIN.items():
    nd = df[s["ndep"]]
    det = m.detectability(nd, s["ntca"], s["ndep_tps"])
    for tp in s["ndep_tps"]:
        r = nd[(nd["locus_tag"] == s["ntca"]) & (nd["timepoint"] == tp)].iloc[0]
        tp_pass = bool(r["expression_status"] == m.UP or (r["log2fc"] > 0 and r["abs_rank_pct"] >= 75))
        controls.append(dict(strain=strain, check="detectability_timepoint", experiment_key=s["ndep"],
                             timepoint=tp, ntca_log2fc=r["log2fc"], ntca_status=r["expression_status"],
                             ntca_abs_rank_pct=r["abs_rank_pct"], passed=tp_pass))
    controls.append(dict(strain=strain, check="detectability_overall", experiment_key=s["ndep"],
                         timepoint="|".join(s["ndep_tps"]), passed=det["passed"],
                         detail="passing timepoints: " + ("|".join(det["passing_timepoints"]) or "none")))
    ntca_rows.append(nd[(nd["locus_tag"] == s["ntca"]) & nd["timepoint"].isin(s["ndep_tps"])][COLS])
    genes.append(nd[nd["locus_tag"].isin([s["ntca"]] + s["ure"] + s["other"])
                    & nd["timepoint"].isin(s["ndep_tps"])][COLS])

    for key in (s["urea"], s["alt"]):
        d = df[key]
        pc = m.positive_control(d, s["ure"])
        controls.append(dict(strain=strain, check="positive_control_ure_urt", experiment_key=key,
                             timepoint="steady state", n_genes=pc["n_genes"], n_sig_up=pc["n_sig_up"],
                             median_log2fc=pc["median_log2fc"], frac_pos=pc["frac_pos"],
                             passed=pc["passed"]))
        gr = m.growth_rate_check(d)
        controls.append(dict(strain=strain, check="growth_rate_ribosomal", experiment_key=key,
                             timepoint="steady state", n_genes=gr["n_ribo"],
                             median_log2fc=gr["median_ribo"], median_genome=gr["median_genome"],
                             frac_sig=gr["frac_sig"], flag=gr["flag"]))
        row = d[d["locus_tag"] == s["ntca"]].iloc[0]
        ntca_rows.append(d[d["locus_tag"] == s["ntca"]][COLS])
        genes.append(d[d["locus_tag"].isin([s["ntca"]] + s["ure"] + s["other"])][COLS])
        skipped = key == "med4_cyanate" and gate_fired
        cls = "not_applied_identity_gate" if skipped else m.classify_ntca(row)
        readings.append(dict(strain=strain, experiment_key=key, experiment_id=EXP[key],
                             role="primary" if key == s["urea"] else "alternative_N_comparison",
                             ntca_locus_tag=s["ntca"], classification=cls,
                             control_passed=pc["passed"], detectability_passed=det["passed"],
                             growth_rate_flag=gr["flag"],
                             final_reading=cls if skipped else m.final_reading(cls, pc["passed"], det["passed"])))

pd.DataFrame(controls).to_csv(DATA / "controls.csv", index=False, encoding="utf-8")
pd.concat(ntca_rows).to_csv(DATA / "ntca_rows.csv", index=False, encoding="utf-8")
pd.DataFrame(readings).to_csv(DATA / "readings.csv", index=False, encoding="utf-8")
gt = pd.concat(genes)
gt["set"] = gt["locus_tag"].map(lambda t: "ntcA" if t in ("PMM0246", "PMT1831") else
                                ("ure_urt" if any(t in s["ure"] for s in STRAIN.values()) else "other_N"))
gt.to_csv(DATA / "gene_table.csv", index=False, encoding="utf-8")

# genome-wide distribution for the figure (used columns only)
dist = []
for strain, s in STRAIN.items():
    for key in (s["urea"], s["alt"]):
        dist.append(df[key].assign(strain=strain))
    nd = df[s["ndep"]]
    dist.append(nd[nd["timepoint"].isin(s["ndep_tps"])].assign(strain=strain))
pd.concat(dist)[["strain"] + COLS + ["timepoint_order"]].to_csv(
    DATA / "genome_log2fc_used.csv", index=False, encoding="utf-8")
print("gate_fired", gate_fired)
