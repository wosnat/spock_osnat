"""THROWAWAY pilot: one 1920x1080 slide, Alteromonas HOT1A3 vs MED4 (no KG calls; reads a01/a02 outputs).
Strip and counts are generated from data; the example/controls text is written from hits.csv / operon_calls.csv.
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/spike/alteromonas_hot1a3/scripts/a04_slide.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
DATA, REP = HERE / "data", HERE / "reports"
REP.mkdir(exist_ok=True)
AAS = ["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro",
       "Ser", "Thr", "Trp", "Tyr", "Val"]
CLS = {"complete": "c", "partial": "p", "absent": "a", "can't be judged": "j", "not assessable": "na"}


def strip(df, oc, okey):
    out = []
    for aa in AAS:
        c = df.set_index("amino_acid").loc[aa]
        s = c.cell_status
        inner = f"<span class='nm'>{aa}</span>"
        mark = ""
        if s in ("complete", "partial"):
            inner += f"<span class='kn'>{c.cell_k_of_n}</span>"
            o = oc[(oc.organism == okey) & (oc.pathway_id == c.cell_pathway)]
            mark = "<i class='pk'></i>" if (o.operon_call == "package").any() else "<i class='ln'></i>"
        sh = "<b class='sh'></b>" if bool(c.all_shared_route_fully_present) else ""
        out.append(f"<div class='aa {CLS[s]}' title='{aa}: {s} {c.cell_k_of_n if isinstance(c.cell_k_of_n, str) else ''}'>"
                   f"{inner}{mark}{sh}</div>")
    return "".join(out)


def main():
    aa_a = pd.read_csv(DATA / "aa_status.csv", encoding="utf-8")
    aa_m = pd.read_csv(DATA / "aa_status_med4.csv", encoding="utf-8")
    oc = pd.read_csv(DATA / "operon_calls.csv", encoding="utf-8")
    summ = json.loads((DATA / "summary.json").read_text(encoding="utf-8"))
    st = pd.read_csv(DATA / "hot1a3_step_matrix.csv", encoding="utf-8")
    n_obs = int(st[(st.flag == "dedicated") & st.observable].shape[0])
    a, m = summ["HOT1A3"], summ["MED4"]
    n_ded = a["dedicated_steps_catalogued"]
    ga = summ["gene_counts"]["Alteromonas macleodii HOT1A3"][0][1]
    gm = summ["gene_counts"]["MED4"][0][1]
    n_part_a = int((aa_a.cell_status == "partial").sum())
    cnt = lambda df, s: int((df.cell_status == s).sum())  # noqa: E731
    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Alteromonas HOT1A3 vs MED4: amino-acid breakdown pathways (pilot, draft catalogue)</title>
<style>
:root{{--ink:#1f2328;--muted:#59636e;--line:#d0d7de;--bg:#fcfcfb;--panel:#f3f4f6;--ded:#6250d6;--lded:#c3bbf2;--shared:#8f8e89;--flag:#eda100;}}
*{{box-sizing:border-box}} html,body{{margin:0;background:#e9eaec}}
.slide{{width:1920px;height:1080px;background:var(--bg);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
 padding:40px 64px 28px;display:grid;grid-template-rows:auto auto 1fr auto;gap:18px;overflow:hidden}}
h1{{margin:0;font-size:40px;line-height:1.1;letter-spacing:-.01em}} h1 i{{font-style:italic}}
.sub{{margin:6px 0 0;font-size:20px;color:var(--muted)}}
.tag{{display:inline-block;font-size:15px;font-weight:600;border:1.5px solid var(--flag);color:#9a6700;border-radius:14px;padding:2px 12px;margin-left:12px;vertical-align:6px}}
.row{{display:grid;grid-template-columns:150px repeat(20,1fr);gap:6px;align-items:center;margin-bottom:8px}}
.lab{{font-size:19px;font-weight:600;line-height:1.1}} .lab small{{display:block;font-weight:400;color:var(--muted);font-size:14px}}
.aa{{height:84px;border-radius:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;overflow:hidden}}
.nm{{font-weight:700;font-size:25px}} .kn{{font-size:17px;margin-top:1px}}
.aa.c{{background:var(--ded);color:#fff}} .aa.p{{background:var(--lded);border:2px solid var(--ded)}}
.aa.a{{background:#fff;border:2px solid var(--shared)}}
.aa.j{{border:2px solid var(--shared);background:repeating-linear-gradient(45deg,#e6e5e1 0 6px,#cfceca 6px 8px)}}
.aa.j .nm{{background:#e6e5e1;padding:0 4px;border-radius:3px}}
.aa.na{{border:2px dashed var(--shared);background:#efeeea}}
.pk,.ln{{position:absolute;top:6px;right:6px;width:12px;height:12px;border-radius:50%;border:2px solid currentColor}}
.pk{{background:currentColor}}
.sh{{position:absolute;left:0;bottom:0;border-bottom:16px solid var(--shared);border-right:16px solid transparent}}
.legend{{display:flex;flex-wrap:wrap;gap:8px 26px;font-size:17px;color:var(--muted);margin-top:4px}}
.sw{{display:inline-block;width:16px;height:16px;border-radius:3px;vertical-align:-3px;margin-right:6px}}
.cols{{display:grid;grid-template-columns:0.9fr 1.35fr 1fr;gap:24px;min-height:0}}
.card{{background:var(--panel);border-radius:10px;padding:22px 26px;min-height:0;overflow:hidden}}
.card h2{{margin:0 0 14px;font-size:20px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}}
.card p,.card li{{font-size:22px;line-height:1.38}} .card ul{{margin:0;padding-left:20px}} .card li{{margin:0 0 14px}}
.num{{background:#fff;border-radius:8px;padding:14px 16px;border:1px solid var(--line);margin-bottom:18px}}
.num .pair{{display:flex;gap:20px;align-items:baseline}} .num b{{font-size:60px;line-height:1;color:var(--ded)}}
.num b.m{{color:#6b6a66}} .num span{{font-size:18px;color:var(--muted)}} .num .t{{font-size:19px;color:var(--ink);font-weight:600;margin-bottom:4px}}
.ex{{background:#fff;border:2px solid var(--ded);border-radius:8px;padding:16px 18px;margin-bottom:18px;font-size:21px;line-height:1.35}}
.ex b.h{{color:var(--ded);font-size:22px}} .lt{{font-weight:700}} .pill{{display:inline-block;font-size:14px;font-weight:700;border-radius:10px;padding:1px 9px;margin-left:6px;vertical-align:1px}}
.pill.pk2{{background:var(--ded);color:#fff}} .pill.ln2{{border:1.5px solid var(--ded);color:var(--ded)}}
.ctl td{{font-size:19px;padding:7px 6px;border-bottom:1px solid var(--line);vertical-align:top}} .ctl{{border-collapse:collapse;width:100%;margin-bottom:18px}}
.ok{{color:#1a7f37;font-weight:700}} .fl{{color:#9a6700;font-weight:700}}
.foot{{display:flex;justify-content:space-between;gap:30px;font-size:15px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px}}
</style></head><body><div class="slide">
<div>
 <h1><i>Alteromonas</i> HOT1A3 vs <i>Prochlorococcus</i> MED4: amino-acid breakdown pathways <span class="tag">pilot · draft catalogue</span></h1>
 <p class="sub">Same draft catalogue and rules for both genomes: KO match + product keyword · shared steps not counted · N-freeing step required · cell = best pathway</p>
</div>
<div>
 <div class="row"><div class="lab">MED4<small>{gm:,} genes</small></div>{strip(aa_m, oc, "MED4")}</div>
 <div class="row"><div class="lab">HOT1A3<small>{ga:,} genes</small></div>{strip(aa_a, oc, "HOT1A3")}</div>
 <div class="legend">
  <span><span class="sw" style="background:var(--ded)"></span>complete (k/n dedicated steps)</span>
  <span><span class="sw" style="background:var(--lded);border:2px solid var(--ded)"></span>partial</span>
  <span><span class="sw" style="background:#fff;border:2px solid var(--shared)"></span>absent (not found with these annotations)</span>
  <span><span class="sw" style="border:2px solid var(--shared);background:repeating-linear-gradient(45deg,#e6e5e1 0 3px,#cfceca 3px 5px)"></span>can't be judged (only all-shared routes)</span>
  <span>● package: gene sits next to a transporter or another step (±3 genes, same strand) &nbsp; ○ lone gene</span>
  <span><span class="sw" style="background:linear-gradient(to top right,var(--shared) 50%,transparent 50%)"></span>an all-shared route is fully present</span>
 </div>
</div>
<div class="cols">
 <div class="card"><h2>Key numbers</h2>
  <div class="num"><div class="t">Dedicated steps found (of {n_ded} catalogued; {n_obs} have KOs in the KG)</div>
   <div class="pair"><b class="m">{m['dedicated_steps_found']}</b><span>MED4</span><b>{a['dedicated_steps_found']}</b><span>HOT1A3</span></div></div>
  <div class="num"><div class="t">Complete pathways</div>
   <div class="pair"><b class="m">{len(m['complete_pathways'])}</b><span>MED4 (Asn)</span><b>{len(a['complete_pathways'])}</b><span>HOT1A3</span></div></div>
  <div class="num"><div class="t">Amino-acid cells: complete / partial / absent / can't judge</div>
   <div class="pair"><span style="font-size:20px;color:var(--ink)">MED4 <b class="m" style="font-size:24px">{cnt(aa_m,'complete')}/{cnt(aa_m,'partial')}/{cnt(aa_m,'absent')}/{cnt(aa_m,"can't be judged")}</b></span>
   <span style="font-size:20px;color:var(--ink)">HOT1A3 <b style="font-size:24px">{cnt(aa_a,'complete')}/{n_part_a}/{cnt(aa_a,'absent')}/{cnt(aa_a,"can't be judged")}</b></span></div></div>
  <p style="margin:6px 0 0;font-size:20px;color:var(--muted)">Trp is partial in HOT1A3 (kynurenine route 2/3: no kynurenine formamidase KO).</p>
 </div>
 <div class="card"><h2>Examples: complete in HOT1A3</h2>
  <div class="ex"><b class="h">Thr · threonine dehydrogenase route (2/2)</b><br>
   tdh <span class="lt">ACZ81_00315</span> + kbl <span class="lt">ACZ81_00310</span>, adjacent, same strand<span class="pill pk2">package</span><br>
   <span style="color:var(--muted);font-size:18px">N freed by glycine cleavage (shared): gcvP ACZ81_14455, gcvT ACZ81_14465</span></div>
  <div class="ex"><b class="h">Arg · succinyltransferase (AST) route (2/2)</b><br>
   astA <span class="lt">ACZ81_01910</span><span class="pill ln2">lone</span> · astB <span class="lt">ACZ81_08435</span><span class="pill pk2">package</span><br>
   <span style="color:var(--muted);font-size:18px">astB is 2 genes from ACZ81_08425 (dicarboxylate/amino acid:cation symporter); astA sits beside ACZ81_01905 succinylglutamate-semialdehyde DH (not in the catalogue)</span></div>
  <div class="ex"><b class="h">His · hut, histidine ammonia-lyase (1/1)</b><br>
   hutH <span class="lt">ACZ81_04180</span><span class="pill ln2">lone gene</span><br>
   <span style="color:var(--muted);font-size:18px">Neighbour ACZ81_04175 is urocanate hydratase: a later hut step, outside the catalogue (the pathway ends at hutH), so not counted</span></div>
 </div>
 <div class="card"><h2>Controls &amp; caveats</h2>
  <table class="ctl">
   <tr><td>glnA</td><td><span class="fl">found, flagged</span> ACZ81_15545 "glutamate--ammonia ligase": KO matches, keyword "glutamine synthetase" absent from the product</td></tr>
   <tr><td>ilvE</td><td><span class="ok">found</span> ACZ81_01635</td></tr>
   <tr><td>hisC</td><td><span class="ok">found</span> ACZ81_12705 (+ hisC2 ACZ81_11410, ACZ81_16160)</td></tr>
   <tr><td>astB</td><td>found ACZ81_08435 (expected-negative for cyanobacteria only)</td></tr>
  </table>
  <ul>
   <li>Draft catalogue, not approved; keywords miss synonyms (glnA, phhA "monooxygenase").</li>
   <li>Annotation ≠ function; enzymes may act on amino acids made inside the cell.</li>
   <li>HOT1A3 has {ga/gm:.1f}× MED4's genes.</li>
  </ul>
 </div>
</div>
<div class="foot"><span>Pathway-level status (proposal v5 rule) on the draft catalogue. Package = positional adjacency only, not co-expression. Data: spike/alteromonas_hot1a3/data/aa_status_med4_vs_hot1a3.csv, operon_calls.csv.</span>
<span style="white-space:nowrap">KG multiomics · 2026-11-04 · throwaway pilot</span></div>
</div></body></html>"""
    (REP / "hot1a3_vs_med4_slide.html").write_text(page, encoding="utf-8")
    print("written", REP / "hot1a3_vs_med4_slide.html")


if __name__ == "__main__":
    main()
