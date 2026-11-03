"""Real-KG check of the API calls in ntca_urea.fetch_de.

Asserts only against values already known from the MCP tools (proposal.md).
No ntcA values beyond the disclosed MED4 urea row are asserted or printed.
Skip offline with:  pytest -m "not kg"   (or set NTCA_OFFLINE=1).
Writes a QC table (counts + negative-log2FC fraction, no gene values) to methods/data/.
"""
import os
import sys
from pathlib import Path

import pytest

METHODS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(METHODS))
import ntca_urea as m  # noqa: E402

pytestmark = [pytest.mark.kg,
              pytest.mark.skipif(os.environ.get("NTCA_OFFLINE") == "1", reason="offline")]

P = "10.1038/msb4100087_"
EXP = {
    "med4_urea": P + "growth_medium_growth_on_urea_as_med4_microarray",
    "mit9313_urea": P + "growth_medium_growth_on_urea_as_mit9313_microarray",
    "med4_cyanate": P + "growth_medium_growth_on_cyanate_as_med4_microarray",
    "mit9313_nitrite": P + "growth_medium_growth_on_nitrite_as_mit9313_microarray",
    "med4_ndep": P + "nitrogen_nitrogen_deprivation_med4_med4_microarray",
    "mit9313_ndep": P + "nitrogen_nitrogen_deprivation_mit9313_mit9313_microarray",
}
# expected (n_genes, n_up, n_down) per (experiment key, timepoint label)
SINGLE = {"med4_urea": (1696, 14, 5), "mit9313_urea": (2241, 28, 41),
          "med4_cyanate": (1696, 14, 5), "mit9313_nitrite": (2241, 9, 5)}
NDEP = {
    "med4_ndep": (1696, {"0h": (0, 2), "3h": (6, 0), "6h": (81, 95), "12h": (92, 129),
                         "24h": (39, 108), "48h": (35, 32)}),
    "mit9313_ndep": (2241, {"0h": (0, 0), "3h": (1, 0), "6h": (18, 21), "12h": (19, 27),
                            "24h": (77, 100), "48h": (82, 240)}),
}
# locus tags from proposal.md and the gene names they must carry
NAMES_MED4 = {"PMM0246": {"ntcA"}, **{f"PMM{n:04d}": "ure" for n in range(963, 970)},
              "PMM0970": "urtA", "PMM0972": "urt", "PMM0973": "urt", "PMM0974": "urt"}
NAMES_MIT = {"PMT1831": {"ntcA"}, **{f"PMT{n}": "ure" for n in range(2230, 2237)},
             "PMT2229": "urtA", "PMT2225": "urt", "PMT2226": "urt", "PMT2227": "urt"}


@pytest.fixture(scope="module")
def frames():
    return {k: m.fetch_de([e]) for k, e in EXP.items()}


def _counts(df):
    s = df["expression_status"]
    return df["locus_tag"].nunique(), int((s == m.UP).sum()), int((s == m.DOWN).sum())


@pytest.mark.parametrize("key", list(SINGLE))
def test_single_timepoint_counts(frames, key):
    df = frames[key]
    assert df["timepoint"].nunique() == 1
    assert _counts(df) == SINGLE[key]


@pytest.mark.parametrize("key", list(NDEP))
def test_ndep_counts_per_timepoint(frames, key):
    n_genes, per_tp = NDEP[key]
    df = frames[key]
    assert set(df["timepoint"]) == set(per_tp)
    for tp, (up, dn) in per_tp.items():
        assert _counts(df[df["timepoint"] == tp]) == (n_genes, up, dn), tp


def test_known_med4_ntca_row(frames):
    row = frames["med4_urea"].query("locus_tag == 'PMM0246'")
    assert len(row) == 1
    assert row["log2fc"].iloc[0] == pytest.approx(-2.2711, abs=1e-3)
    assert row["expression_status"].iloc[0] == m.NS


@pytest.mark.parametrize("key,names", [("med4_urea", NAMES_MED4), ("mit9313_urea", NAMES_MIT)])
def test_locus_tags_resolve(frames, key, names):
    g = frames[key].set_index("locus_tag")["gene_name"]
    for lt, want in names.items():
        assert lt in g.index, lt
        got = str(g[lt])
        ok = got in want if isinstance(want, set) else got.startswith(want)
        assert ok, f"{lt}: {got!r} vs {want!r}"
    ure = {str(g[lt]) for lt, w in names.items() if w == "ure"}
    assert ure == {f"ure{c}" for c in "ABCDEFG"}


def test_sign_not_lost_and_write_qc(frames):
    rows = []
    for key, df in frames.items():
        for tp, sub in df.groupby("timepoint", sort=False):
            n, up, dn = _counts(sub)
            rows.append(dict(experiment_key=key, experiment_id=EXP[key], timepoint=tp,
                             n_rows=len(sub), n_genes=n, n_sig_up=up, n_sig_down=dn,
                             frac_log2fc_neg=float((sub["log2fc"] < 0).mean()),
                             frac_log2fc_zero=float((sub["log2fc"] == 0).mean()),
                             n_log2fc_null=int(sub["log2fc"].isna().sum())))
    import pandas as pd
    qc = pd.DataFrame(rows)
    out = METHODS / "data"
    out.mkdir(exist_ok=True)
    qc.to_csv(out / "qc_kg_api_checks.csv", index=False, encoding="utf-8")
    assert (qc["frac_log2fc_neg"] > 0.05).all()
    assert (qc["n_log2fc_null"] == 0).all()
