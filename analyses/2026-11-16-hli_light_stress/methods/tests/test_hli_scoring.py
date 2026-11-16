"""Toy tests for hli_scoring (hand-computed expectations)."""
import math

import numpy as np
import pandas as pd
import pytest
from multiomics_explorer import EnrichmentInputs, fisher_ora
from scipy.stats import fisher_exact

import hli_scoring as hs

BG20 = [f"g{i:02d}" for i in range(20)]


# ---------------------------------------------------------------- Fisher
def test_fisher_hand_computed():
    # k=2 of n=4 significant genes in a set of M=4, N=20.
    # P(X>=2) = [C(4,2)C(16,2) + C(4,3)C(16,1) + C(4,4)] / C(20,4) = (720+64+1)/4845
    expected = 785 / 4845
    res = hs.run_fisher({"t": ["g00", "g01", "g02", "g03"]}, {"t": BG20},
                        {"S": ["g00", "g01", "g10", "g11"]}, fisher_ora, EnrichmentInputs)
    row = res.iloc[0]
    assert (row["count"], row["n_sig_in_bg"], row["bg_count"], row["background_size"]) == (2, 4, 4, 20)
    assert row["pvalue"] == pytest.approx(expected, rel=1e-9)
    assert row["pvalue"] == pytest.approx(
        fisher_exact([[2, 2], [2, 14]], alternative="greater").pvalue, rel=1e-9)


def test_fisher_genes_outside_background_dropped_and_empty_set_p1():
    res = hs.run_fisher({"a": ["g00", "zz"], "b": []}, {"a": BG20, "b": BG20},
                        {"S": ["g00", "yy"]}, fisher_ora, EnrichmentInputs).set_index("test_id")
    assert res.loc["a", "n_sig_in_bg"] == 1 and res.loc["a", "bg_count"] == 1
    assert res.loc["a", "pvalue"] == pytest.approx(1 / 20)   # C(1,1)C(19,0)/C(20,1)
    assert res.loc["b", "pvalue"] == 1.0 and res.loc["b", "count"] == 0


# ---------------------------------------------------------------- backgrounds
def test_backgrounds_per_table_type():
    genome = BG20
    bg, kind = hs.main_background("sound", ["g01", "g02", "g01"], genome)
    assert bg == ["g01", "g02"] and kind == "table_measured"
    bg, kind = hs.main_background("approximate", ["g01"], genome)
    assert bg == genome and kind == "genome_assumption"


def test_build_test_grid():
    de = pd.DataFrame(dict(
        experiment_id=["e"] * 5, timepoint=["1h", "1h", "1h", None, None],
        timepoint_order=[1, 1, 1, None, None], locus_tag=["a", "b", "c", "a", "b"],
        expression_status=["significant_up", "significant_down", "not_significant",
                           "significant_up", "significant_up"]))
    g = hs.build_test_grid(de).set_index(["timepoint", "direction"])
    assert g.loc[("1h", "up"), "sig_genes"] == ["a"]
    assert g.loc[("1h", "down"), "sig_genes"] == ["b"]
    assert g.loc[("1h", "up"), "measured_genes"] == ["a", "b", "c"]
    assert g.loc[("NA", "up"), "n_sig_total"] == 2
    assert len(g) == 4


# ---------------------------------------------------------------- flags
def test_too_few_threshold_9_vs_10():
    assert "too_few" in hs.test_flags(9, 1000, "up", up_only=False, test_type="sound")
    assert "too_few" not in hs.test_flags(10, 1000, "up", up_only=False, test_type="sound")


def test_genome_wide_boundary_30pct():
    assert "genome_wide_response" not in hs.test_flags(300, 1000, "up", up_only=False, test_type="sound")
    assert "genome_wide_response" in hs.test_flags(301, 1000, "up", up_only=False, test_type="sound")


def test_not_testable_descriptive_approximate():
    f = hs.test_flags(0, 1973, "down", up_only=True, test_type="approximate")
    assert "not_testable" in f and "too_few" not in f and "approximate" in f
    assert not hs.is_testable(f)
    f = hs.test_flags(50, 800, "up", up_only=False, test_type="descriptive")
    assert "descriptive" in f and not hs.is_testable(f)
    f = hs.test_flags(50, 1973, "up", up_only=True, test_type="approximate")
    assert f == ["approximate"] and hs.is_testable(f)


# ---------------------------------------------------------------- orientation
def test_orientation_flip():
    assert hs.orient_direction("up", 1) == "up"
    assert hs.orient_direction("up", -1) == "down"
    assert hs.orient_direction("down", -1) == "up"
    with pytest.raises(ValueError):
        hs.orient_direction("up", 0)


# ---------------------------------------------------------------- BH and aggregate
def test_bh_hand_computed():
    # p = .01 .02 .03 .5, m=4 -> .04 .04 .04 .5
    assert np.allclose(hs.bh([0.01, 0.02, 0.03, 0.5]), [0.04, 0.04, 0.04, 0.5])
    out = hs.bh([0.01, np.nan, 0.04])     # m=2: .02, nan, .04
    assert np.isnan(out[1]) and np.allclose(out[[0, 2]], [0.02, 0.04])


def test_bonferroni_within_then_bh_across():
    t = pd.DataFrame(dict(
        experiment_id=["A", "A", "A", "B", "B"], set="S", direction="up",
        pvalue=[0.01, 0.2, 0.0001, 0.04, 0.5], padj_bh=[0.02, 0.3, 0.001, 0.06, 0.6],
        testable=[True, True, False, True, True]))
    agg = hs.experiment_aggregate(t).set_index("experiment_id")
    # A: untestable p=1e-4 ignored; min(.01,.2)*2 = .02. B: .04*2 = .08
    assert agg.loc["A", "p_exp_bonferroni"] == pytest.approx(0.02)
    assert agg.loc["B", "p_exp_bonferroni"] == pytest.approx(0.08)
    # BH across the 2 experiments: .02*2/1 = .04 ; .08*2/2 = .08
    assert agg.loc["A", "padj_exp_bh"] == pytest.approx(0.04)
    assert agg.loc["B", "padj_exp_bh"] == pytest.approx(0.08)
    assert agg.loc["A", "timepoint_count"] == "sig at 1 of 2"
    assert agg.loc["B", "timepoint_count"] == "sig at 0 of 2"


def test_bonferroni_cap_at_1():
    t = pd.DataFrame(dict(experiment_id="A", set="S", direction="up",
                          pvalue=[0.6, 0.7], padj_bh=[0.7, 0.7], testable=[True, True]))
    assert hs.experiment_aggregate(t)["p_exp_bonferroni"].iloc[0] == 1.0


def test_call_from_padj():
    assert hs.call_from_padj(0.01, 0.2) == "up"
    assert hs.call_from_padj(0.2, 0.01) == "down"
    assert hs.call_from_padj(0.01, 0.01) == "both"
    assert hs.call_from_padj(0.2, np.nan) == "neither"
    assert hs.call_from_padj(np.nan, np.nan) == "not_tested"


# ---------------------------------------------------------------- ortholog groups
def test_ortholog_group_counts():
    g2g = {"a1": "G1", "a2": "G1", "a3": "G1", "b1": "G2", "c1": "G3", "d1": "G4"}
    calls = {"a1": "ns", "a2": "up", "a3": "down", "b1": "up", "c1": "ns"}   # d1 not measured
    out = hs.ortholog_group_counts(calls, g2g)
    assert out == dict(n_groups=4, n_groups_measured=3, n_groups_up=2, n_groups_down=1)


# ---------------------------------------------------------------- random sets and light parsing
def test_random_sets_seeded_and_sized():
    r1 = hs.draw_random_sets(BG20, 5, 3, np.random.default_rng(1))
    r2 = hs.draw_random_sets(BG20, 5, 3, np.random.default_rng(1))
    assert r1 == r2 and len(r1) == 3
    assert all(len(v) == 5 and set(v) <= set(BG20) for v in r1.values())
    assert hs.draw_random_sets(BG20, 0, 3, np.random.default_rng(1)) == {}


@pytest.mark.parametrize("text,val,note", [
    ("~45 umol photons m-2 s-1", 45, ""), ("10-25 umol photons m-2 s-1", 17.5, "range_midpoint"),
    ("90 uE m-2 s-1", 90, ""), ("0", 0, "bare_number"), ("50 umol quanta m-2 s-1", 50, ""),
    ("bright", math.nan, "unparseable")])
def test_parse_light(text, val, note):
    v, n = hs.parse_light_umol(text)
    assert n == note and (math.isnan(v) if math.isnan(val) else v == val)


def test_arm_light_levels():
    ext_dark = hs.arm_light_levels("Extended darkness across dawn",
                                   "Normal diel light period (time-matched controls)",
                                   "12:12 light:dark cycle", "~45 umol photons m-2 s-1")
    assert (ext_dark["light_treatment_umol"], ext_dark["light_control_umol"]) == (0, 45)
    const = hs.arm_light_levels("Constant dark", "Constant light (90 µE m-2 s-1)",
                                "constant darkness", "0")
    assert (const["light_treatment_umol"], const["light_control_umol"]) == (0, 90)
    shift = hs.arm_light_levels("Blue light (13 umol photons m-2 s-1)", "Darkness control",
                                "blue light", "13 umol photons m-2 s-1")
    assert (shift["light_treatment_umol"], shift["light_control_umol"]) == (13, 0)
    phage_dark = hs.arm_light_levels("Phage (P-HM2) lysate", "Spent medium (uninfected)",
                                     "constant darkness", "0")
    assert (phage_dark["light_treatment_umol"], phage_dark["light_control_umol"]) == (0, 0)
