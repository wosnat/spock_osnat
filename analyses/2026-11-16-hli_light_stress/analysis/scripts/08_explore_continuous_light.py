"""Exploration B2: light-level views restricted to the continuous-light experiments.

The 18 experiments with light_reading_group == 'none' (non-light stress and non-stress; both arms at the
same light). Asserts that all 18 have light_condition 'continuous light'. Columns ordered by
light_treatment_umol (low -> high), one block per light level. Reuses the drawing functions of
analysis/scripts/03_figures.py unchanged (titles and the key are adjusted at save time).

Writes analysis/figures/explore_B2_{gene_heatmap,set_band,experiment_calls}_continuous_light_by_level.{png,svg}
and analysis/data/explore_continuous_light_experiments.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/08_explore_continuous_light.py
"""
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("figs", HERE / "03_figures.py")
figs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(figs)
DATA, FIG = figs.DATA, figs.FIG
SUFFIX = " — continuous-light experiments only (18, light_reading_group none), ordered by light level"


def main():
    ex = pd.read_csv(DATA.parents[1] / "methods" / "data" / "experiments.csv", encoding="utf-8")
    cl = ex[ex.light_reading_group == "none"]
    assert len(cl) == 18, len(cl)
    assert (cl.light_condition_raw == "continuous light").all(), cl.light_condition_raw.unique()
    assert (cl.light_treatment_umol == cl.light_control_umol).all()
    keep = set(cl.experiment_id)
    lst = cl[["experiment_id", "label", "group", "stress_type", "light_condition_raw", "light_treatment_umol",
              "light_control_umol"]].sort_values(["light_treatment_umol", "label"])
    lst.to_csv(DATA / "explore_continuous_light_experiments.csv", index=False, encoding="utf-8")

    t = figs.read("hli_tests.csv")
    gc = figs.read("hli_gene_calls.csv")
    calls = figs.read("experiment_calls.csv")
    t, gc, calls = (d[d.experiment_id.isin(keep)] for d in (t, gc, calls))

    key = "Continuous-light experiments (light level, µmol photons m⁻² s⁻¹, both arms):\n" + "\n".join(
        f"  {r.light_treatment_umol:g} µmol: {r.label} ({r.stress_type})" for r in lst.itertuples())
    figs.light_key = lambda _t: key
    orig_save = figs.save

    def save(fig, stem):
        ax = fig.axes[0]
        ttl = ax.get_title(loc="left")
        ttl = ttl.replace("across 29 experiments, ", "across 18 experiments, ").replace(
            ", columns ordered by treatment-arm light level (block label, µmol photons m⁻² s⁻¹)", "")
        ttl = ttl.replace(", columns ordered by treatment-arm light level", "").replace(
            ", ordered by treatment-arm light level", "")
        ax.set_title(ttl + "\n" + SUFFIX.strip(" —"), fontsize=9, loc="left", pad=38)
        for txt in ax.texts:   # role-band labels: move clear of the (narrower) row labels
            if txt.get_fontweight() == "bold":
                txt.set_x(-0.29)
        orig_save(fig, stem)

    figs.save = save
    figs.gene_heatmap(gc, t, "light", FIG / "explore_B2_gene_heatmap_continuous_light_by_level")
    figs.set_band(t, "light", FIG / "explore_B2_set_band_continuous_light_by_level")
    figs.experiment_calls(calls, t, "light", FIG / "explore_B2_experiment_calls_continuous_light_by_level")
    print(lst.to_string(index=False))


if __name__ == "__main__":
    main()
