"""Context: every MED4 TCDB assignment at levels 3 (subfamily) and 4 (system), for amino-acid-relevant review."""
from pathlib import Path
import pandas as pd
from multiomics_explorer import genes_by_ontology
DATA = Path(__file__).resolve().parents[1] / "data"
out = []
for lv in (2, 3, 4):
    t = genes_by_ontology(ontology="tcdb", organism="MED4", level=lv, min_gene_set_size=0, max_gene_set_size=None, limit=None)
    assert t["returned"] == t["total_matching"]
    print("level", lv, "total_matching", t["total_matching"])
    for x in t["results"]:
        x = dict(x); x["tcdb_calls"] = ";".join(x.get("tcdb_calls") or []); out.append(x)
df = pd.DataFrame(out)
df.to_csv(DATA / "med4_tcdb_all_levels.csv", index=False, encoding="utf-8")
pat = r"amino|glutam|aspart|arginin|lysin|histid|leucin|prolin|serin|glycin|alanin|cystin|cystein|methion|threon|tyros|tryptoph|phenylal|valin|PAAT|HAAT|APC|peptide|3\.A\.1\.3\b|3\.A\.1\.4\b|3\.A\.1\.5\b"
m = df[df.term_name.str.contains(pat, case=False, regex=True) | df.term_id.str.contains(r"tcdb:3\.A\.1\.(3|4|5)\b|tcdb:2\.A\.(3|23|27|26|22|25)\b", regex=True)
       | df["product"].fillna("").str.contains(pat, case=False, regex=True)]
print(m[["level","locus_tag","gene_name","product","term_id","term_name","tcdb_gate","tcdb_call","tcdb_calls"]].to_string())
