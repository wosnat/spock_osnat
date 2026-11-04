"""Build the methods-milestone HTML report(s) from methods/data/ (never edited by hand).

Pages:
  reports/catalogue_review.html  - the draft pathway catalogue for researcher review: summary counts,
                                   per-amino-acid pathway chains (dedicated = violet outline, shared =
                                   grey dashed outline, N-freeing step marked), per-pathway KO tables,
                                   debatable flags, KO problems, broad enzymes, MED4 cross-check
                                   candidates, proposed controls.
Self-contained (inline CSS/JS, no network). Printable.
Also writes data/catalogue_summary_by_aa.csv (the per-amino-acid table shown on the page).

Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/methods/scripts/build_reports.py
"""
from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

MDIR = Path(__file__).resolve().parents[1]
DATA, REP = MDIR / "data", MDIR / "reports"
AA_ORDER = ["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met",
            "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val"]
E = lambda x: html.escape("" if pd.isna(x) else str(x))

CSS = """
:root{--surface:#fcfcfb;--plane:#f9f9f7;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;
--ded:#6250d6;--sh:#8f8e89;--ring:rgba(11,11,11,.10)}
*{box-sizing:border-box}body{margin:0;background:var(--plane);color:var(--ink);
font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 28px 64px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 8px;padding-top:8px;border-top:1px solid var(--grid)}
h3{font-size:15px;margin:22px 0 6px}p.lead{color:var(--ink2);margin:0 0 16px}
.note{color:var(--ink2);font-size:13px}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:14px 0}
.tile{background:var(--surface);border:1px solid var(--ring);border-radius:8px;padding:10px 12px}
.tile .v{font-size:24px;font-weight:600}.tile .l{color:var(--ink2);font-size:12px}
.legend{display:flex;gap:18px;flex-wrap:wrap;align-items:center;margin:8px 0 4px;color:var(--ink2);font-size:13px}
.sw{display:inline-block;width:26px;height:14px;border-radius:4px;vertical-align:middle;margin-right:6px;background:var(--surface)}
.sw.ded{border:2px solid var(--ded)}.sw.sh{border:2px dashed var(--sh)}
nav.aa{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}
nav.aa a{padding:2px 8px;border:1px solid var(--ring);border-radius:12px;color:var(--ink);text-decoration:none;background:var(--surface)}
.pw{background:var(--surface);border:1px solid var(--ring);border-radius:8px;padding:12px 14px;margin:10px 0;break-inside:avoid}
.pwh{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.pwh b{font-size:14px}.pwh span{color:var(--ink2);font-size:12px}
.chain{display:flex;align-items:stretch;flex-wrap:wrap;gap:0;margin:10px 0 8px}
.step{position:relative;min-width:150px;max-width:220px;padding:7px 9px;border-radius:8px;background:var(--surface);font-size:12.5px}
.step.ded{border:2px solid var(--ded)}.step.sh{border:2px dashed var(--sh)}
.step .k{font-size:11px;color:var(--ink2)}.step .nm{font-weight:600}
.step .tag{font-size:10.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--ink2)}
.step.nf{box-shadow:inset 0 -4px 0 0 var(--ink)}
.nfb{display:inline-block;margin-top:3px;font-size:10.5px;font-weight:600;padding:0 5px;border-radius:4px;border:1px solid var(--ink);color:var(--ink)}
.arrow{align-self:center;color:var(--muted);padding:0 6px;font-size:16px}
.step .tip{display:none;position:absolute;z-index:5;left:0;top:100%;margin-top:4px;width:320px;background:#0b0b0b;color:#fff;
padding:8px 10px;border-radius:6px;font-size:12px;font-weight:400;line-height:1.35}
.step:hover .tip,.step:focus .tip{display:block}
table{border-collapse:collapse;width:100%;font-size:12.5px;background:var(--surface)}
th,td{text-align:left;vertical-align:top;padding:4px 6px;border-bottom:1px solid var(--grid)}
th{color:var(--ink2);font-weight:600;cursor:pointer;white-space:nowrap}
td.mono{word-break:break-word}
td.mono,span.mono{font-family:ui-monospace,Consolas,monospace;font-size:12px}
.bad{font-weight:600}.badge{display:inline-block;padding:0 5px;border-radius:4px;border:1px solid var(--ring);font-size:11px}
.pnote{color:var(--ink2);font-size:12px;margin-top:4px}
.scroll{overflow-x:auto}
input.f{margin:6px 0;padding:4px 8px;border:1px solid var(--grid);border-radius:6px;width:260px}
@media print{body{background:#fff}.step .tip,nav.aa,input.f{display:none!important}.pw,tr{break-inside:avoid}main{max-width:none}}
"""

JS = """
document.querySelectorAll('table.sortable').forEach(t=>{t.querySelectorAll('th').forEach((th,i)=>{th.addEventListener('click',()=>{
const tb=t.tBodies[0],rows=[...tb.rows],asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
rows.sort((a,b)=>{const x=a.cells[i].innerText,y=b.cells[i].innerText,nx=parseFloat(x),ny=parseFloat(y);
const c=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y);return asc?c:-c});rows.forEach(r=>tb.appendChild(r));});});});
document.querySelectorAll('input.f').forEach(inp=>{inp.addEventListener('input',()=>{const q=inp.value.toLowerCase();
document.getElementById(inp.dataset.t).querySelectorAll('tbody tr').forEach(r=>{r.style.display=r.innerText.toLowerCase().includes(q)?'':'none'})})});
"""


def table(df: pd.DataFrame, tid: str = "", mono=(), filt=False) -> str:
    h = ""
    if filt and tid:
        h += f'<input class="f" data-t="{tid}" placeholder="filter rows...">'
    h += f'<div class="scroll"><table class="sortable" id="{tid}"><thead><tr>' + "".join(f"<th>{E(c)}</th>" for c in df.columns) + "</tr></thead><tbody>"
    for _, r in df.iterrows():
        h += "<tr>" + "".join(f'<td class="{"mono" if c in mono else ""}">{E(r[c])}</td>' for c in df.columns) + "</tr>"
    return h + "</tbody></table></div>"


def main():
    steps = pd.read_csv(DATA / "pathway_catalogue_steps.csv", encoding="utf-8")
    long = pd.read_csv(DATA / "pathway_catalogue.csv", encoding="utf-8")
    val = pd.read_csv(DATA / "ko_validation.csv", encoding="utf-8").set_index("ko")
    broad = pd.read_csv(DATA / "broad_enzymes.csv", encoding="utf-8")
    cand = pd.read_csv(DATA / "crosscheck_candidates_med4.csv", encoding="utf-8")
    ctrl = pd.read_csv(DATA / "proposed_controls.csv", encoding="utf-8")
    comp = pd.read_csv(DATA / "ec_ko_completeness.csv", encoding="utf-8")
    rec = pd.read_csv(DATA / "pilot_reconciliation.csv", encoding="utf-8")
    passess = pd.read_csv(DATA / "pathway_assessability.csv", encoding="utf-8").set_index("pathway_id")
    aassess = pd.read_csv(DATA / "aa_assessability.csv", encoding="utf-8").set_index("amino_acid")
    hits = pd.read_csv(DATA / "med4_step_hits.csv", encoding="utf-8")
    flagged = pd.read_csv(DATA / "med4_flagged_hits.csv", encoding="utf-8")
    fchg = pd.read_csv(DATA / "flag_change_log.csv", encoding="utf-8")
    rcomp = pd.read_csv(DATA / "rn_ko_completeness.csv", encoding="utf-8")
    srn = pd.read_csv(DATA / "step_reactions.csv", encoding="utf-8").set_index("step_id")

    long = long.join(val[["kegg_valid", "kegg_name", "in_kg"]], on="ko")
    steps["n_kos"] = steps.kos.str.split(";").map(len)
    steps["kos_in_kg"] = steps.kos.map(lambda s: sum(bool(val.loc[k, "in_kg"]) for k in s.split(";")))
    steps["kos_invalid"] = steps.kos.map(lambda s: ";".join(k for k in s.split(";") if not val.loc[k, "kegg_valid"]))

    # ---- per amino acid summary ----
    pcls = steps.groupby("pathway_id").pathway_class.first()
    summ = []
    for aa in AA_ORDER:
        g = steps[steps.amino_acid == aa]
        pids = g.pathway_id.unique()
        summ.append(dict(amino_acid=aa, pathways=len(pids), steps=len(g),
                         dedicated_steps=int((g.flag == "dedicated").sum()),
                         shared_steps=int((g.flag == "shared").sum()),
                         all_shared_pathways=int(sum(pcls[p] == "all-shared" for p in pids)),
                         n_freeing_step_ids="; ".join(g[g.is_n_freeing].step_id),
                         n_pathways=int(aassess.loc[aa, "n_pathways"]),
                         n_observable_dedicated_routes=int(aassess.loc[aa, "n_observable_dedicated_routes"]),
                         assessable=aassess.loc[aa, "assessable"], assessable_reason=aassess.loc[aa, "reason"]))
    summ = pd.DataFrame(summ)
    summ.to_csv(DATA / "catalogue_summary_by_aa.csv", index=False, encoding="utf-8")

    all_kos = val.reset_index()
    n_invalid = int((~all_kos.kegg_valid).sum())
    n_notkg = int((~all_kos.in_kg).sum())
    cat_kos = set(long.ko)
    cat_notkg = sorted(k for k in cat_kos if not val.loc[k, "in_kg"])
    deb = steps[steps.debatable == "yes"].drop_duplicates("step_key")
    tiles = [
        (steps.pathway_id.nunique(), "pathways (20 amino acids)"),
        (len(steps), "steps (pathway x position)"),
        (steps.step_key.nunique(), "distinct reactions (step keys)"),
        (int((steps.flag == "dedicated").sum()), "dedicated steps"),
        (int((steps.flag == "shared").sum()), "shared steps"),
        (int((pcls == "all-shared").sum()), "all-shared pathways (cannot be judged)"),
        (len(deb), "debatable flags (distinct reactions)"),
        (len(cat_kos), "distinct KOs in catalogue"),
        (n_invalid, "KOs not valid in KEGG (all tables)"),
        (len(cat_notkg), "catalogue KOs with no gene in the KG"),
        (int((cand.proposal == "add").sum()), "cross-check reaction rows proposed 'add'"),
        (int((summ.assessable == "yes").sum()), "amino acids assessable"),
        (int((summ.assessable == "partly").sum()), "amino acids partly assessable"),
        (int((summ.assessable == "no").sum()), "amino acids not assessable"),
        (int((~passess.observable).sum()), "pathways not observable (status 'not assessable')"),
        (flagged.locus_tag.nunique(), "MED4 genes flagged KO/product mismatch"),
    ]
    unsc = summ[summ.assessable == "no"]
    unsc_html = ("<p><b>Not assessable from KO annotation (by design):</b> " + "; ".join(
        f"<b>{E(r.amino_acid)}</b> ({E(r.assessable_reason)})" for _, r in unsc.iterrows()) + ".</p>"
        + "<p><b>Partly assessable:</b> " + "; ".join(
        f"<b>{E(r.amino_acid)}</b> ({E(r.assessable_reason)})" for _, r in summ[summ.assessable == "partly"].iterrows()) + ".</p>"
        '<p class="note">A pathway is observable if every scored step (each dedicated step and the N-freeing anchor) has, in every '
        "required subunit group, at least one KO with a node in the KG. An unobservable pathway is reported as "
        "<b>not assessable</b>, never as absent. Assessable counts only routes with a dedicated step that are not N-neutral.</p>")

    H = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         "<title>Draft amino-acid utilization pathway catalogue - review</title>",
         '<meta name="description" content="Draft catalogue of amino-acid breakdown pathways to the N-freeing step, '
         'with dedicated/shared flags, KO validity, MED4 reaction-layer cross-check and proposed controls, for researcher review.">',
         f"<style>{CSS}</style></head><body><main>",
         "<h1>Draft pathway catalogue - for review</h1>",
         '<p class="lead">Methods milestone, step 1. Each amino acid\'s known bacterial breakdown pathways, drawn up to the '
         "first step that frees nitrogen. Drafted from KEGG reference maps and modules plus standard biochemistry "
         "(an interpretation input, not KG data); KO validity checked against KEGG REST; KG presence = the KO node exists "
         "in the KG. Only MED4 was queried (cross-check section). Nothing on this page is a strain score.</p>",
         '<div class="tiles">' + "".join(f'<div class="tile"><div class="v">{v}</div><div class="l">{E(l)}</div></div>' for v, l in tiles) + "</div>",
         '<div class="legend"><span><span class="sw ded"></span>dedicated step (violet solid outline) - counts toward k/n</span>'
         '<span><span class="sw sh"></span>shared step (grey dashed outline) - never counts</span>'
         '<span><span class="nfb">N-freeing</span> the pathway\'s anchor step (also underlined in black)</span>'
         "<span>Hover a step for its reaction and flag reason.</span></div>",
         "<h2>Per amino acid</h2>",
         unsc_html,
         table(summ, "t_summ", mono=("n_freeing_step_ids",)),
         '<nav class="aa">' + "".join(f'<a href="#aa-{a}">{a}</a>' for a in AA_ORDER)
         + '<a href="#debatable">debatable</a><a href="#kos">KO checks</a><a href="#broad">broad</a>'
           '<a href="#xcheck">MED4 cross-check</a><a href="#hits">MED4 product check</a><a href="#controls">controls</a>'
           '<a href="#changes">flag changes</a><a href="#omissions">known omissions</a><a href="#pilot">pilot</a></nav>']

    # ---- pathways ----
    H.append("<h2>Pathways by amino acid</h2>")
    for aa in AA_ORDER:
        H.append(f'<h3 id="aa-{aa}">{aa}</h3>')
        g = steps[steps.amino_acid == aa]
        for pid, p in g.groupby("pathway_id", sort=False):
            p = p.sort_values("step_order")
            cls = p.pathway_class.iloc[0]
            H.append('<div class="pw"><div class="pwh">'
                     f'<b>{E(p.pathway_name.iloc[0])} <span class="mono">({E(pid)})</span></b>'
                     f'<span>{E(cls)} · {len(p)} step(s), {int((p.flag=="dedicated").sum())} dedicated · '
                     f'{"observable" if passess.loc[pid, "observable"] else "<b>NOT ASSESSABLE</b> (KOs not in KG)"} · source: {E(p.source_ref.iloc[0])}</span></div>')
            if isinstance(passess.loc[pid, "note"], str) and passess.loc[pid, "note"]:
                H.append(f'<div class="pnote"><b>Assessability:</b> {E(passess.loc[pid, "note"])}</div>')
            chain = []
            for _, s in p.iterrows():
                c = "ded" if s.flag == "dedicated" else "sh"
                nf = " nf" if s.is_n_freeing else ""
                tip = (f"<b>{E(s.reaction)}</b><br>EC {E(s.ec)}<br>{E(s.flag)}: {E(s.flag_reason)}"
                       + (f"<br>N mode: {E(s.n_mode)}" + (f" (acceptor: {E(s.acceptor)})" if isinstance(s.acceptor, str) and s.acceptor else "") if s.is_n_freeing else "")
                       + (f"<br><i>Debatable:</i> {E(s.debatable_reason)}" if s.debatable == "yes" else ""))
                chain.append(f'<div class="step {c}{nf}" tabindex="0"><div class="k mono">{E(s.step_id)}</div>'
                             f'<div class="nm">{E(s.step_name)}</div><div class="tag">{E(s.flag)}'
                             f'{" · debatable" if s.debatable == "yes" else ""}</div>'
                             + (f'<span class="nfb">N-freeing: {E(s.n_mode)}</span>' if s.is_n_freeing else "")
                             + f'<div class="tip">{tip}</div></div>')
            H.append('<div class="chain">' + '<div class="arrow">&rarr;</div>'.join(chain) + "</div>")
            sub = long[long.pathway_id == pid].copy()
            sub["kegg_valid"] = sub.kegg_valid.map({True: "yes", False: "NO"})
            sub["in_kg"] = sub.in_kg.map({True: "yes", False: "no"})
            sub = sub.merge(p[["step_id", "flag_reason", "ko_groups", "product_keywords"]].rename(columns={"flag_reason": "fr"}), on="step_id", suffixes=("", "_s"))
            sub["kegg_rn"] = sub.step_id.map(lambda s: srn.loc[s, "kegg_rn"] if s in srn.index else "")
            show = sub[["step_id", "ko", "kegg_name", "ec", "kegg_rn", "ko_groups", "flag", "fr", "debatable", "kegg_valid", "in_kg", "product_keywords"]].rename(
                columns={"fr": "flag_reason", "kegg_name": "KEGG name", "ko_groups": "ko_groups (; = AND, | = OR)"})
            H.append(table(show, mono=("step_id", "ko", "ec")))
            notes = [f"{E(s.step_id)}: {E(s.notes)}" for _, s in p.iterrows() if isinstance(s.notes, str) and s.notes]
            if isinstance(p.pathway_note.iloc[0], str) and p.pathway_note.iloc[0]:
                notes.insert(0, E(p.pathway_note.iloc[0]))
            if notes:
                H.append('<div class="pnote">' + "<br>".join(notes) + "</div>")
            H.append("</div>")

    # ---- debatable ----
    H.append('<h2 id="debatable">Debatable flags</h2><p class="note">One row per distinct reaction (step key); the steps that use it are listed.</p>')
    d = deb[["step_key", "step_name", "flag", "flag_reason", "debatable_reason"]].copy()
    d["used_in_steps"] = d.step_key.map(lambda k: ";".join(steps[steps.step_key == k].step_id))
    H.append(table(d, "t_deb", mono=("step_key", "used_in_steps")))

    # ---- KO checks ----
    H.append('<h2 id="kos">KO checks</h2>')
    prob = all_kos[(~all_kos.kegg_valid) | (~all_kos.in_kg)][["ko", "used_in", "kegg_valid", "kegg_name", "in_kg", "kg_search_for_symbol"]]
    H.append(f'<p class="note">{len(all_kos)} KOs checked (catalogue + broad + controls). {n_invalid} not valid in KEGG; '
             f"{n_notkg} valid but with no KO node in the KG (they stay in and score absent). Table: every KO with a problem.</p>")
    H.append(table(prob, "t_prob", mono=("ko",), filt=True))
    mism = all_kos[all_kos.kg_name_matches_kegg == False]  # noqa: E712
    H.append(f'<p class="note">KG name differs from the KEGG name for {len(mism)} KO(s).</p>')
    if len(mism):
        H.append(table(mism[["ko", "kegg_name", "kg_name"]], mono=("ko",)))
    c2 = comp[comp.not_in_step.fillna("") != ""][["step_id", "ec", "not_in_step"]]
    H.append(f'<h3>Other KOs KEGG assigns to a step\'s EC ({len(c2)} step x EC rows)</h3>'
             '<p class="note">KEGG link/ko/ec: KOs carrying the same EC number that the step does not list. '
             "Listed for the researcher to decide whether any is a missing isozyme; most are deliberate exclusions "
             "(see each step's notes).</p>")
    H.append(table(c2, "t_comp", mono=("step_id", "ec"), filt=True))
    r2 = rcomp[rcomp.not_in_step.fillna("") != ""][["step_id", "flag", "is_n_freeing", "reaction", "not_in_step"]]
    H.append(f"<h3>Other KOs KEGG links to a step's reaction ({len(r2)} step x reaction rows)</h3>"
             '<p class="note">KEGG link/ko/rn on each step\'s reaction ids (manual list, or the EC\'s main reactions). '
             "Anchor (N-freeing) transamination steps were filled from these links.</p>")
    H.append(table(r2, "t_rcomp", mono=("step_id", "reaction"), filt=True))

    # ---- broad ----
    H.append('<h2 id="broad">Broad-specificity, D-amino-acid and side-activity enzymes (never credited)</h2>')
    b = broad.join(val[["kegg_valid", "in_kg"]], on="ko")
    H.append(table(b[["ko", "label", "ec", "category", "description", "kegg_valid", "in_kg", "pilot_note"]], "t_broad", mono=("ko", "ec")))

    # ---- cross-check ----
    H.append('<h2 id="xcheck">MED4 reaction-layer cross-check</h2>')
    allx = pd.read_csv(DATA / "crosscheck_all_reactions_med4.csv", encoding="utf-8")
    H.append(f'<p class="note">genes_by_metabolite(evidence_sources=[metabolism], organism=MED4, include_stereo_forms=True) for the 20 '
             f"amino acids: {len(allx)} gene x reaction x amino-acid rows, {allx.reaction_id.nunique()} distinct reactions, "
             f"{int(allx.covered.sum())} rows covered. <b>Covered</b> = the gene's KO is in a step of <i>that amino acid's own</i> "
             "pathways whose KEGG reaction list contains this reaction; a KO found only in another amino acid's step, the broad "
             "table or the controls is not coverage (shown as 'ko_elsewhere_info'). Uncovered reactions are grouped below "
             f"(one row per amino acid x reaction, {len(cand)} rows). 'aa_side' is the side of the KEGG equation as written; "
             "the KG carries no substrate/product role, so 'aa_role' and the proposal are hand judgements from the equation.</p>")
    adds = cand[cand.proposal == "add"]
    n_enz = adds.ec_numbers.fillna("").map(lambda s: s.split(";")[0]).nunique()
    H.append(f"<p class=\"note\">Proposal counts: {E(cand.proposal.value_counts().to_dict())}. "
             f"Proposed adds: <b>{n_enz} enzymes / {len(adds)} reaction rows</b>.</p>")
    H.append('<p class="note"><b>Consistency note (asymmetry kept visible):</b> histidine decarboxylase (R01167, MED4 PMM0917) '
             "is rejected because decarboxylation keeps N in histamine and no KEGG module defines a histamine N-freeing step, "
             "whereas the analogous lysine route (cadA -> cadaverine -> patA, Lys_cadaverine) is catalogued because KEGG M00956 "
             "defines it. The researcher may want the two treated the same way.</p>")
    cshow = cand[["proposal", "amino_acid", "reaction_id", "equation", "ec_numbers", "aa_side", "aa_role", "removes_N_from_aa",
                  "locus_tags", "gene_kos", "products", "reason"]].sort_values(["proposal", "amino_acid"])
    H.append(table(cshow, "t_x", mono=("reaction_id", "ec_numbers", "locus_tags", "gene_kos"), filt=True))
    cov = (allx[allx.covered].groupby(["amino_acid", "reaction_id"])
           .agg(equation=("equation", "first"), aa_side=("aa_side", "first"),
                locus_tags=("locus_tag", lambda s: ";".join(sorted(set(s)))),
                gene_kos=("gene_kos", "first"), catalogue_coverage=("catalogue_coverage", "first")).reset_index())
    H.append(f"<h3>Covered reactions ({len(cov)} amino acid x reaction rows)</h3>"
             '<p class="note">catalogue_coverage = the amino acid\'s own step(s) whose KO and reaction match.</p>')
    H.append(table(cov, "t_cov", mono=("reaction_id", "locus_tags", "gene_kos"), filt=True))

    # ---- MED4 product agreement ----
    H.append('<h2 id="hits">MED4 product-agreement check</h2>')
    H.append(f'<p class="note">Rule: a gene counts for a step only if its KG product contains one of the step\'s product keywords; '
             f"otherwise it is <b>flagged: KO/product mismatch</b> and does not count until the researcher reviews it. "
             f"genes_by_ontology(kegg, MED4) on all catalogue + control KOs: {len(hits)} step x gene rows, "
             f"{hits.locus_tag.nunique()} MED4 genes; {len(flagged)} rows / {flagged.locus_tag.nunique()} genes flagged. "
             "This is a hit list, not a pathway score.</p>")
    H.append(table(flagged[["step_id", "amino_acid", "ko", "locus_tag", "gene_name", "product", "product_keywords", "call"]],
                   "t_flag", mono=("step_id", "ko", "locus_tag"), filt=True))

    # ---- controls ----
    H.append('<h2 id="controls">Proposed controls (researcher approves)</h2>')
    H.append(table(ctrl[["control_type", "control_id", "step_name", "kos", "ec", "source_ref", "rank_or_tier",
                         "kegg_valid_all", "in_kg_any", "in_kg_kos", "proposed", "rationale"]], "t_ctrl", mono=("kos", "ec")))
    H.append('<p class="note">Expected-negative rule: first candidate in biology rank that is valid in KEGG and whose KO node '
             "exists in the KG with an overall gene count of at least 1 (kg_gene_count_total; no per-organism counts read). A KO "
             "with no gene anywhere in the KG cannot produce a hit, so it could not reveal a KO-matching artefact. "
             "<b>Disclosure:</b> the ranking and this rule were written in the same commit as the KG lookup that applied them.</p>")
    H.append(table(ctrl[["control_id", "kg_gene_count_total", "product_keywords", "disclosure"]], "t_ctrl2", mono=("control_id",)))

    # ---- flag changes ----
    H.append('<h2 id="changes">Flag and KO-list changes after the critic review</h2>')
    H.append(table(fchg, "t_chg", mono=("step_key",)))

    # ---- known omissions ----
    H.append('<h2 id="omissions">Known omissions (not catalogued)</h2><ul>'
             "<li>Glycine reductase (anaerobic, Stickland; glycine -> acetyl-P + NH4+).</li>"
             "<li>Proline reductase (anaerobic, Stickland; N kept in 5-aminovalerate).</li>"
             "<li>Lysine 2,3-aminomutase route (kamA; anaerobic lysine fermentation).</li>"
             "<li>Cysteine -> 3-mercaptopyruvate by cysteine transamination (aspartate aminotransferase side activity, R00896).</li>"
             "<li>Aromatic amino-acid decarboxylase + tynA amine oxidase (tyramine / phenylethylamine routes).</li>"
             "<li>ArgZ (Arg_argZ) is catalogued but not assessable: its KOs have no node in the KG; a homolog-based search would be "
             "needed (possible later extension).</li></ul>")

    # ---- pilot ----
    H.append('<h2 id="pilot">Where each pilot (spike) catalogue KO went</h2>')
    H.append(table(rec, "t_pilot", mono=("ko",), filt=True))

    H.append(f"<script>{JS}</script></main></body></html>")
    REP.mkdir(parents=True, exist_ok=True)
    (REP / "catalogue_review.html").write_text("\n".join(H), encoding="utf-8")
    print("wrote", REP / "catalogue_review.html")
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()
