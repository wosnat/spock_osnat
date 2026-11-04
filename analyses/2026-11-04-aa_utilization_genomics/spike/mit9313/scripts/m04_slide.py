"""THROWAWAY pilot slide: MIT9313 vs MED4, HOT1A3 as reference (no KG calls). Reuses a04.strip.
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/spike/mit9313/scripts/m04_slide.py
"""
from __future__ import annotations

import html
import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ALT = HERE.parent / "alteromonas_hot1a3"
spec = importlib.util.spec_from_file_location("a04", ALT / "scripts" / "a04_slide.py")
a04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a04)
DATA, REP = HERE / "data", HERE / "reports"
REP.mkdir(exist_ok=True)


def main():
    aa_m = pd.read_csv(ALT / "data" / "aa_status_med4.csv", encoding="utf-8")
    aa_a = pd.read_csv(ALT / "data" / "aa_status.csv", encoding="utf-8")
    aa_t = pd.read_csv(DATA / "aa_status.csv", encoding="utf-8")
    oc_t = pd.read_csv(DATA / "operon_calls.csv", encoding="utf-8")
    oc = pd.concat([pd.read_csv(ALT / "data" / "operon_calls.csv", encoding="utf-8"), oc_t], ignore_index=True)
    summ = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    gc = {k: v[0][1] for k, v in summ["gene_counts"].items()}
    hits_t = pd.read_csv(DATA / "hits.csv", encoding="utf-8")
    ps_t = pd.read_csv(DATA / "pathway_status.csv", encoding="utf-8").set_index("pathway_id")
    med_found = set(summ["MED4"]["dedicated_steps_found_ids"])
    only = [s for s in summ["MIT9313"]["dedicated_steps_found_ids"] if s not in med_found]
    cred = hits_t[(hits_t.call == "credited") & hits_t.step_id.isin(only)].drop_duplicates(["step_id", "locus_tag"])
    ex = []
    for r in cred.itertuples():
        o = oc_t[(oc_t.step_id == r.step_id) & (oc_t.anchor_locus_tag == r.locus_tag)]
        call = o.operon_call.iloc[0] if len(o) else "?"
        nbs = o.same_strand_within3_products.iloc[0] if len(o) and isinstance(o.same_strand_within3_products.iloc[0], str) else "none"
        pid = r.step_id.rsplit(".", 1)[0]
        st = ps_t.loc[pid, "status"]
        ex.append(f"<div class='ex'><b class='h'>{r.amino_acid} · {html.escape(pid)}</b>"
                  f" <span style='color:var(--muted);font-size:18px'>(pathway: {st})</span><br>"
                  f"{html.escape(str(r.gene_name))} <span class='lt'>{r.locus_tag}</span> · {html.escape(r.product)}"
                  f"<span class='pill {'pk2' if call == 'package' else 'ln2'}'>{call}</span>"
                  f"<br><span style='color:var(--muted);font-size:17px'>Same-strand neighbours (±3): {html.escape(nbs)}</span></div>")
    cnt = lambda df, s: int((df.cell_status == s).sum())  # noqa: E731
    cells = lambda df: f"{cnt(df,'complete')}/{cnt(df,'partial')}/{cnt(df,'absent')}/{cnt(df,chr(99)+'an'+chr(39)+'t be judged')}"  # noqa: E731
    css = (ALT / "reports" / "hot1a3_vs_med4_slide.html").read_text(encoding="utf-8")
    css = css[css.find("<style>"):css.find("</style>") + 8]
    m, t, a = summ["MED4"], summ["MIT9313"], summ["HOT1A3"]
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Prochlorococcus MIT9313 (low-light) vs MED4 (high-light), with Alteromonas HOT1A3 as reference — amino-acid breakdown pathways (pilot, draft catalogue)</title>
{css}
<style>.aa{{height:70px}} .row{{grid-template-columns:200px repeat(20,1fr);margin-bottom:7px}} h1{{font-size:33px}} .num b{{font-size:50px}} .num .pair{{gap:12px}} .ex{{margin-bottom:16px}}
.lab{{font-size:18px}} .ref .lab{{color:var(--muted)}} .ref{{margin-top:12px}}</style>
</head><body><div class="slide">
<div>
 <h1><i>Prochlorococcus</i> MIT9313 (low-light) vs MED4 (high-light), with <i>Alteromonas</i> HOT1A3 as reference <span class="tag">pilot · draft catalogue</span></h1>
 <p class="sub">Amino-acid breakdown pathways · same draft catalogue and rules for all three genomes: KO match + product keyword · shared steps not counted · N-freeing step required · cell = best pathway</p>
</div>
<div>
 <div class="row"><div class="lab">MED4 · HLI<small>{gc['MED4']:,} genes</small></div>{a04.strip(aa_m, oc, "MED4")}</div>
 <div class="row"><div class="lab">MIT9313 · LLIV<small>{gc['MIT9313']:,} genes</small></div>{a04.strip(aa_t, oc, "MIT9313")}</div>
 <div class="row ref"><div class="lab">HOT1A3 (reference)<small>{gc['HOT1A3']:,} genes</small></div>{a04.strip(aa_a, oc, "HOT1A3")}</div>
 <div class="legend">
  <span><span class="sw" style="background:var(--ded)"></span>complete (k/n dedicated steps)</span>
  <span><span class="sw" style="background:var(--lded);border:2px solid var(--ded)"></span>partial</span>
  <span><span class="sw" style="background:#fff;border:2px solid var(--shared)"></span>absent (not found with these annotations)</span>
  <span><span class="sw" style="border:2px solid var(--shared);background:repeating-linear-gradient(45deg,#e6e5e1 0 3px,#cfceca 3px 5px)"></span>can't be judged (only all-shared routes)</span>
  <span>● package (±3 genes, same strand: transporter or another step) &nbsp; ○ lone gene</span>
  <span><span class="sw" style="background:linear-gradient(to top right,var(--shared) 50%,transparent 50%)"></span>an all-shared route is fully present</span>
 </div>
</div>
<div class="cols">
 <div class="card"><h2>Key numbers</h2>
  <div class="num"><div class="t">Dedicated steps found (of {t['dedicated_steps_catalogued']}; 34 have KOs in the KG)</div>
   <div class="pair"><b class="m">{m['dedicated_steps_found']}</b><span>MED4</span><b>{t['dedicated_steps_found']}</b><span>MIT9313</span><b class="m">{a['dedicated_steps_found']}</b><span>HOT1A3</span></div></div>
  <div class="num"><div class="t">Complete pathways</div>
   <div class="pair"><b class="m">{len(m['complete_pathways'])}</b><span>MED4</span><b>{len(t['complete_pathways'])}</b><span>MIT9313</span><b class="m">{len(a['complete_pathways'])}</b><span>HOT1A3</span></div></div>
  <div class="num"><div class="t">Cells: complete / partial / absent / can't judge</div>
   <p style="margin:2px 0 0;font-size:20px">MED4 <b class="m" style="font-size:24px">{cells(aa_m)}</b> · MIT9313 <b style="font-size:24px">{cells(aa_t)}</b> · HOT1A3 <b class="m" style="font-size:24px">{cells(aa_a)}</b></p></div>
 </div>
 <div class="card"><h2>Dedicated hits in MIT9313 that MED4 lacks</h2>
  {''.join(ex)}
  <p style="margin:8px 0 0;font-size:19px;color:var(--muted)">Shared by both: asparaginase, MIT9313 <b>PMT0825</b> / MED4 <b>PMM0821</b> (both lone genes). The glutamate decarboxylase route is N-neutral and excluded, so its hit does not change the Glu cell.</p>
 </div>
 <div class="card"><h2>Controls (MIT9313) &amp; caveats</h2>
  <table class="ctl">
   <tr><td>glnA</td><td><span class="ok">found</span> PMT0601 "glutamine synthetase, type I"</td></tr>
   <tr><td>ilvE</td><td><span class="ok">found</span> PMT0728</td></tr>
   <tr><td>hisC</td><td><span class="ok">found</span> PMT2069</td></tr>
   <tr><td>astB</td><td>expected-negative: no gene on K01484</td></tr>
  </table>
  <ul>
   <li>Draft catalogue, not approved. Product keywords miss synonyms (e.g. HOT1A3 glnA "glutamate--ammonia ligase" is flagged).</li>
   <li>Annotation ≠ function.</li>
   <li>Genome sizes: MED4 {gc['MED4']:,}, MIT9313 {gc['MIT9313']:,}, HOT1A3 {gc['HOT1A3']:,} genes.</li>
  </ul>
 </div>
</div>
<div class="foot"><span>Pathway-level status (proposal v5 rule) on the draft catalogue. Package = positional adjacency only. MIT9313 was unblinded by the researcher for this pilot. Data: spike/mit9313/data/aa_status_med4_vs_mit9313_vs_hot1a3.csv.</span>
<span style="white-space:nowrap">2026-11-04 · throwaway pilot</span></div>
</div></body></html>"""
    (REP / "mit9313_vs_med4_slide.html").write_text(page, encoding="utf-8")
    print("MIT9313-only dedicated steps:", only)


if __name__ == "__main__":
    main()
