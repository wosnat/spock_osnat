"""Methods step 5b: flags per experiment x timepoint x direction vs proposal.md Known limits.

Reads methods/data/flag_counts.csv; writes methods/data/flag_check_vs_proposal.csv
(one row per flagged test, with whether proposal.md Known limits lists it).

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/04_flag_check.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"

# proposal.md Known limits, "Too few changes" bullets, transcribed as (label, timepoint or '*', direction or '*')
# '*' = every timepoint / both directions; EXCEPT lists the tests the proposal says stay testable.
EXPECTED_TOO_FEW = [
    ("Green 13 vs dark", "*", "*"),
    ("Red 13 vs dark", "*", "down"),
    ("White 13 vs dark", "*", "down"),
    ("DCMU + white 13 vs white 13", "*", "*"),
    ("Phage lysate (dark)", "*", "*", [("4.5h post-inoculation", "down")]),
    ("Phage lysate (light)", "*", "*", [("8.5h post-inoculation", "down")]),
    ("Const dark vs light (no phage)", "*", "*", [("8.5h post-inoculation", "down")]),
    ("Const dark vs light (phage)", "*", "*", [("8.5h post-inoculation", "down")]),
    ("Phage infection (array, up-only)", "6h", "up"),
    ("Phage infection (array, up-only)", "8h", "up"),
    ("Iron starvation", "12h", "down"),
    ("Iron starvation", "24h", "down"),
    ("Phosphate starvation", "0h", "up"),
    ("Phosphate starvation", "4h", "up"),
    ("Phosphate starvation", "12h", "up"),
    ("Phosphate starvation", "*", "down"),
    ("CO2: ambient, no O2", "*", "*"),
]


def expected(label, tp, d):
    for e in EXPECTED_TOO_FEW:
        lab, etp, ed = e[:3]
        exc = e[3] if len(e) > 3 else []
        if lab == label and etp in ("*", tp) and ed in ("*", d) and (tp, d) not in exc:
            return True
    return False


fl = pd.read_csv(DATA / "flag_counts.csv", encoding="utf-8")
fl["too_few_in_proposal"] = [expected(a, b, c) for a, b, c in zip(fl.label, fl.timepoint, fl.direction)]
fl["mismatch"] = fl.too_few != fl.too_few_in_proposal
# the proposal's list covers neither descriptive tests nor not_testable ones
fl.loc[fl.descriptive | fl.not_testable, "mismatch"] = False
out = fl[fl.too_few | fl.too_few_in_proposal | fl.genome_wide_response | fl.not_testable | fl.descriptive]
out.to_csv(DATA / "flag_check_vs_proposal.csv", index=False, encoding="utf-8")

pd.set_option("display.width", 250)
print("tests:", len(fl), "| testable:", fl.testable.sum())
print(fl.groupby("group")[["too_few", "genome_wide_response", "not_testable", "descriptive", "approximate",
                           "testable"]].sum().to_string())
print("\nMISMATCHES (too_few computed vs proposal Known limits):")
print(fl[fl.mismatch][["label", "timepoint", "direction", "n_sig_total", "too_few", "too_few_in_proposal",
                       "flags"]].to_string())
print("\ngenome_wide_response tests:")
print(fl[fl.genome_wide_response][["label", "timepoint", "direction", "n_sig_total", "background_size",
                                   "genome_share_sig"]].to_string())
print("\ndescriptive / not_testable tests:")
print(fl[fl.descriptive | fl.not_testable][["label", "timepoint", "direction", "n_sig_total", "flags"]].to_string())
