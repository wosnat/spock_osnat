"""Toy tests for methods/ntca_urea.py — hand-built DataFrames only, no KG."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ntca_urea as m  # noqa: E402

NS, UP, DN = "not_significant", "significant_up", "significant_down"


def mk(rows, exp="e1", tp="steady state"):
    """rows: list of (locus_tag, log2fc, status[, product])."""
    out = []
    for r in rows:
        lt, fc, st = r[:3]
        prod = r[3] if len(r) > 3 else "hypothetical protein"
        out.append(dict(locus_tag=lt, gene_name=None, product=prod, experiment_id=exp,
                        timepoint=tp, log2fc=fc, padj=0.01 if st != NS else 1.0,
                        expression_status=st))
    return pd.DataFrame(out)


# ---- add_abs_rank_pct -------------------------------------------------------
def test_abs_rank_pct_within_group():
    df = pd.concat([mk([("a", 0.1, NS), ("b", -2.0, NS), ("c", 1.0, NS), ("d", 0.5, NS)], tp="t1"),
                    mk([("a", 5.0, NS), ("b", 0.0, NS)], tp="t2")])
    out = m.add_abs_rank_pct(df)
    t1 = out[out.timepoint == "t1"].set_index("locus_tag")["abs_rank_pct"]
    assert t1["b"] == pytest.approx(100.0)
    assert t1["a"] == pytest.approx(25.0)
    t2 = out[out.timepoint == "t2"].set_index("locus_tag")["abs_rank_pct"]
    assert t2["a"] == pytest.approx(100.0) and t2["b"] == pytest.approx(50.0)


# ---- classify_ntca ----------------------------------------------------------
@pytest.mark.parametrize("status,pct,expected", [
    (UP, 10.0, "up"),
    (DN, 99.0, "down"),
    (NS, 75.0, "suggestive"),
    (NS, 74.9, "not_changed"),
])
def test_classify_four_classes(status, pct, expected):
    row = pd.Series(dict(expression_status=status, abs_rank_pct=pct, log2fc=1.0))
    assert m.classify_ntca(row) == expected


# ---- positive_control -------------------------------------------------------
TAGS = [f"u{i}" for i in range(4)]


def test_pc_pass_sig_count():
    df = mk([("u0", 0.1, UP), ("u1", 0.2, UP), ("u2", -1, NS), ("u3", -1, NS), ("x", 0, NS)])
    assert m.positive_control(df, TAGS)["passed"] is True


def test_pc_pass_median_arm():
    df = mk([("u0", 0.6, NS), ("u1", 0.7, NS), ("u2", 0.5, NS), ("u3", -0.1, NS)])
    res = m.positive_control(df, TAGS)
    assert res["n_sig_up"] == 0 and res["passed"] is True  # median 0.55, 75% > 0


def test_pc_fail():
    df = mk([("u0", 0.6, UP), ("u1", 0.7, NS), ("u2", -0.5, NS), ("u3", -0.1, NS)])
    assert m.positive_control(df, TAGS)["passed"] is False  # 1 sig, 50% > 0


# ---- growth_rate_check ------------------------------------------------------
def _genome(ribo_fc, ribo_status=NS, n_ribo=10):
    rows = [(f"g{i}", 0.0, NS) for i in range(40)]
    rows += [(f"r{i}", ribo_fc, ribo_status, "50S Ribosomal Protein L2") for i in range(n_ribo)]
    return mk(rows)


def test_growth_flag_off():
    res = m.growth_rate_check(_genome(0.1))
    assert res["flag"] is False and res["n_ribo"] == 10


def test_growth_flag_on_median():
    assert m.growth_rate_check(_genome(1.0))["flag"] is True


def test_growth_flag_on_fraction_sig():
    assert m.growth_rate_check(_genome(0.0, ribo_status=DN))["flag"] is True


# ---- detectability ----------------------------------------------------------
def _ndep(fc_by_tp, status_by_tp):
    parts = []
    for tp in fc_by_tp:
        rows = [(f"g{i}", (i - 5) * 0.1, NS) for i in range(11)]  # |fc| 0..0.5
        rows.append(("NTCA", fc_by_tp[tp], status_by_tp[tp]))
        parts.append(mk(rows, tp=tp))
    return m.add_abs_rank_pct(pd.concat(parts, ignore_index=True))


def test_detect_pass_sig():
    df = _ndep({"6h": 0.01, "12h": 0.0}, {"6h": UP, "12h": NS})
    assert m.detectability(df, "NTCA", ["6h", "12h"])["passed"] is True


def test_detect_pass_magnitude():
    df = _ndep({"6h": 0.01, "12h": 3.0}, {"6h": NS, "12h": NS})
    assert m.detectability(df, "NTCA", ["6h", "12h"])["passed"] is True


def test_detect_fail_negative_large_and_excluded_tp():
    # large negative does not count; a sig-up at an unlisted timepoint does not count
    df = _ndep({"6h": -3.0, "3h": 0.1}, {"6h": NS, "3h": UP})
    assert m.detectability(df, "NTCA", ["6h"])["passed"] is False


# ---- final reading ----------------------------------------------------------
@pytest.mark.parametrize("cls,pc,det,expected", [
    ("up", False, True, "uninterpretable"),
    ("not_changed", True, False, "uninterpretable"),
    ("not_changed", True, True, "not_changed"),
    ("up", True, False, "up"),
    ("suggestive", True, False, "suggestive"),
])
def test_final_reading(cls, pc, det, expected):
    assert m.final_reading(cls, control_passed=pc, detectability_passed=det) == expected


# ---- identity_gate ----------------------------------------------------------
def test_identity_gate_fires():
    a = mk([("a", 1.0, UP), ("b", -0.5, NS)], exp="A")
    b = mk([("a", 1.0, UP), ("b", -0.5, NS), ("c", 9, DN)], exp="B")
    assert m.identity_gate(a, b) is True


def test_identity_gate_not_fired():
    a = mk([("a", 1.0, UP), ("b", -0.5, NS)], exp="A")
    b = mk([("a", 1.0, UP), ("b", -0.4, NS)], exp="B")
    assert m.identity_gate(a, b) is False
