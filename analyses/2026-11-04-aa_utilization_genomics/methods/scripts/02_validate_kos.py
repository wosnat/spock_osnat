"""Methods step 2 - validate every catalogue / broad / control KO against KEGG REST and the KG.

KEGG REST (network, https://rest.kegg.jp):
  * list/<K1+K2+...>       -> kegg_valid + KEGG name                         (batches of 10)
  * get/<ec:a+ec:b+...>    -> EC entry NAME + reaction text (ALL_REAC/REACTION) (batches of 10)
  * link/ko/ec:<ec>        -> every KO KEGG assigns to that EC (isozyme completeness check)
  Raw responses are cached under methods/data/kegg_cache/ so the run is reproducible offline.
KG (no organism argument - KO node existence only; per-organism counts are NOT recorded so no
strain other than MED4 is seen):
  * ontology_term_details(term_ids=[kegg.orthology:K...]) -> in_kg + KG name
  * for KOs not in the KG: search_ontology(search_text=<KEGG symbol>, ontology='kegg') to look for
    the same enzyme under another KO id.
Also selects the expected-negative from the ranked candidates in proposed_controls.csv.

Outputs: ko_validation.csv, ec_reactions.csv, ec_ko_completeness.csv, proposed_controls.csv (updated)
Run (repo root): uv run python analyses/2026-11-04-aa_utilization_genomics/methods/scripts/02_validate_kos.py
"""
from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

import pandas as pd
from multiomics_explorer import ontology_term_details, search_ontology

MDIR = Path(__file__).resolve().parents[1]
DATA = MDIR / "data"
CACHE = DATA / "kegg_cache"
BASE = "https://rest.kegg.jp"


def kegg(op: str) -> str:
    """GET https://rest.kegg.jp/<op>, cached on disk."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (re.sub(r"[^A-Za-z0-9.+_-]", "_", op)[:180] + ".txt")
    if f.exists():
        return f.read_text(encoding="utf-8")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(f"{BASE}/{op}", timeout=60) as r:
                txt = r.read().decode("utf-8")
            break
        except Exception as e:  # noqa: BLE001
            if attempt == 2:
                raise RuntimeError(f"KEGG REST failed for {op}: {e}") from e
            time.sleep(3)
    f.write_text(txt, encoding="utf-8")
    time.sleep(0.5)  # be polite
    return txt


def chunks(xs, n=10):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def parse_flat(txt: str) -> list[dict]:
    """Split a KEGG flat-file multi-entry response into {FIELD: text} dicts."""
    out = []
    for block in txt.split("///"):
        if not block.strip():
            continue
        d, cur = {}, None
        for line in block.splitlines():
            if not line.strip():
                continue
            if line[:12].strip():
                cur = line[:12].strip()
                d[cur] = line[12:].strip()
            elif cur:
                d[cur] += " " + line[12:].strip()
        out.append(d)
    return out


def main():
    cat = pd.read_csv(DATA / "pathway_catalogue.csv", encoding="utf-8")
    broad = pd.read_csv(DATA / "broad_enzymes.csv", encoding="utf-8")
    ctrl = pd.read_csv(DATA / "proposed_controls.csv", encoding="utf-8")

    use = {}
    for _, r in cat.iterrows():
        use.setdefault(r.ko, set()).add("catalogue")
    for k in broad.ko:
        use.setdefault(k, set()).add("broad")
    for ks in ctrl.kos:
        for k in ks.split(";"):
            use.setdefault(k, set()).add("control")
    kos = sorted(use)
    print("KOs to validate:", len(kos))

    # ---- KEGG list/<KO> ----
    names = {}
    for ch in chunks(kos):
        for line in kegg("list/" + "+".join(ch)).splitlines():
            if "\t" in line:
                k, nm = line.split("\t", 1)
                names[k.replace("ko:", "")] = nm
    # ---- KG presence ----
    det = ontology_term_details(term_ids=[f"kegg.orthology:{k}" for k in kos], limit=None)
    print("ontology_term_details total_matching:", det["total_matching"], "returned:", det["returned"],
          "truncated:", det["truncated"], "not_found:", len(det["not_found"]))
    assert not det["truncated"]
    kg = {x["term_id"].split(":", 1)[1]: x["name"] for x in det["results"]}
    # Overall (all-organism) gene_count is read ONLY for expected-negative candidate KOs, to confirm a
    # hit is possible somewhere in the KG; per-organism counts are never read.
    neg_kos = {k for _, c in ctrl[ctrl.control_type == "expected_negative"].iterrows() for k in c.kos.split(";")}
    kg_total = {x["term_id"].split(":", 1)[1]: x.get("gene_count") for x in det["results"]
                if x["term_id"].split(":", 1)[1] in neg_kos}

    rows = []
    for k in kos:
        valid = k in names
        sym = names.get(k, "").split(";")[0].split(",")[0].strip()
        alt = ""
        if k not in kg and sym:
            s = search_ontology(search_text=f'"{sym}"', ontology="kegg", limit=5)
            hits = [f"{x['id'] if 'id' in x else x.get('term_id')}|{x.get('name')}" for x in s.get("results", [])
                    if (x.get("id") or x.get("term_id", "")).startswith("kegg.orthology:")]
            alt = f"search_ontology total_matching={s.get('total_matching')}: " + " || ".join(hits)
        kname = names.get(k, "")
        kgname = kg.get(k, "")
        rows.append(dict(ko=k, used_in=";".join(sorted(use[k])), kegg_valid=valid, kegg_name=kname,
                         in_kg=k in kg, kg_name=kgname,
                         kg_name_matches_kegg=(kgname == kname) if (kgname and kname) else None,
                         kg_search_for_symbol=alt))
    val = pd.DataFrame(rows)
    val.to_csv(DATA / "ko_validation.csv", index=False, encoding="utf-8")
    print("kegg_valid:", val.kegg_valid.value_counts().to_dict(), "| in_kg:", val.in_kg.value_counts().to_dict())
    print("kg name != kegg name:", int((val.kg_name_matches_kegg == False).sum()))  # noqa: E712

    # ---- EC entries: reaction text ----
    steps = pd.read_csv(DATA / "pathway_catalogue_steps.csv", encoding="utf-8")
    ecs = set()
    for e in list(steps.ec) + list(ctrl.ec):
        for x in str(e).split(";"):
            if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", x.strip()):
                ecs.add(x.strip())
    ecs = sorted(ecs)
    ec_rows = []
    for ch in chunks(ecs):
        for d in parse_flat(kegg("get/" + "+".join("ec:" + e for e in ch))):
            ent = d.get("ENTRY", "").split()
            ecid = ent[1] if len(ent) > 1 and ent[0] == "EC" else (ent[0] if ent else "")
            ec_rows.append(dict(ec=ecid, ec_name=d.get("NAME", ""), kegg_reaction=d.get("REACTION", ""),
                                all_reac=d.get("ALL_REAC", "")))
    ecdf = pd.DataFrame(ec_rows)
    missing_ec = sorted(set(ecs) - set(ecdf.ec))
    print("EC entries:", len(ecdf), "of", len(ecs), "| not returned:", missing_ec)
    ecdf.to_csv(DATA / "ec_reactions.csv", index=False, encoding="utf-8")

    # ---- EC -> KO completeness per step ----
    comp = []
    for _, s in steps.iterrows():
        step_kos = set(s.kos.split(";"))
        for e in str(s.ec).split(";"):
            e = e.strip()
            if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", e):
                comp.append(dict(step_id=s.step_id, ec=e, kegg_kos_for_ec="", not_in_step="",
                                 note="EC incomplete; not checked"))
                continue
            ks = sorted(l.split("\t")[1].replace("ko:", "") for l in kegg(f"link/ko/ec:{e}").splitlines() if "\t" in l)
            extra = [k for k in ks if k not in step_kos]
            comp.append(dict(step_id=s.step_id, ec=e, kegg_kos_for_ec=";".join(ks),
                             not_in_step=";".join(f"{k} ({names.get(k) or kegg('list/' + k).split(chr(9), 1)[-1].strip()})" for k in extra),
                             note=""))
    comp = pd.DataFrame(comp)
    comp.to_csv(DATA / "ec_ko_completeness.csv", index=False, encoding="utf-8")
    print("step x EC rows:", len(comp), "| with KOs outside the step:", int((comp.not_in_step != "").sum()))

    # ---- reaction -> KO completeness per step (KEGG link/ko/rn) ----
    ecd = ecdf.set_index("ec")
    srows, rcomp = [], []
    for _, s in steps.iterrows():
        rn, src = (str(s.kegg_rn), "manual (verified list/rn)") if isinstance(s.kegg_rn, str) and s.kegg_rn else ("", "")
        if not rn:
            ids = []
            for e in str(s.ec).split(";"):
                e = e.strip()
                if e in ecd.index and isinstance(ecd.loc[e, "all_reac"], str):
                    main_part = ecd.loc[e, "all_reac"].split("(other)")[0]
                    ids += [x for x in re.findall(r"R\d{5}", main_part)]
            rn, src = ";".join(dict.fromkeys(ids)), "EC main reactions (ALL_REAC before '(other)')"
        srows.append(dict(step_id=s.step_id, step_key=s.step_key, amino_acid=s.amino_acid, kegg_rn=rn, kegg_rn_source=src))
        step_kos = set(s.kos.split(";"))
        for r in [x for x in rn.split(";") if x]:
            ks = sorted(l.split("\t")[1].replace("ko:", "") for l in kegg(f"link/ko/rn:{r}").splitlines() if "\t" in l)
            extra = [k for k in ks if k not in step_kos]
            rcomp.append(dict(step_id=s.step_id, step_key=s.step_key, flag=s.flag, is_n_freeing=s.is_n_freeing,
                              reaction=r, kegg_kos_for_rn=";".join(ks),
                              not_in_step=";".join(f"{k} ({names.get(k) or kegg('list/' + k).split(chr(9), 1)[-1].strip()})" for k in extra)))
    pd.DataFrame(srows).to_csv(DATA / "step_reactions.csv", index=False, encoding="utf-8")
    rcomp = pd.DataFrame(rcomp)
    rcomp.to_csv(DATA / "rn_ko_completeness.csv", index=False, encoding="utf-8")
    print("step x reaction rows:", len(rcomp), "| with KOs outside the step:", int((rcomp.not_in_step != "").sum()))
    print(rcomp[rcomp.not_in_step != ""][["step_id", "reaction", "not_in_step"]].drop_duplicates(["reaction", "not_in_step"]).to_string())

    # ---- assessability (observable = every SCORED step - dedicated steps + the N-freeing anchor - has
    #      >=1 KO with a KG node in EVERY AND-group; also reported over all steps) ----
    inkg = val.set_index("ko").in_kg

    def step_obs(s):
        return all(any(bool(inkg[k]) for k in g.split("|")) for g in s.ko_groups.split(";"))
    steps["step_observable"] = steps.apply(step_obs, axis=1)
    prow = []
    for pid, g in steps.groupby("pathway_id", sort=False):
        scored = g[(g.flag == "dedicated") | g.is_n_freeing]
        has_ded = bool((g.flag == "dedicated").any())
        nneut = g.n_neutral_pathway.iloc[0] if isinstance(g.n_neutral_pathway.iloc[0], str) else ""
        obs = bool(scored.step_observable.all())
        prow.append(dict(amino_acid=g.amino_acid.iloc[0], pathway_id=pid, has_dedicated=has_ded,
                         n_neutral=bool(nneut), observable=obs, all_steps_observable=bool(g.step_observable.all()),
                         unobservable_steps=";".join(g[~g.step_observable].step_id),
                         status_rule=("not assessable (never 'absent')" if not obs else
                                      ("cannot be judged (all-shared)" if not has_ded else "scored")),
                         note=";".join(x for x in [nneut, g.assess_note.iloc[0] if isinstance(g.assess_note.iloc[0], str) else ""] if x)))
    pdf = pd.DataFrame(prow)
    pdf.to_csv(DATA / "pathway_assessability.csv", index=False, encoding="utf-8")
    arow = []
    for aa, g in pdf.groupby("amino_acid", sort=False):
        ded = g[g.has_dedicated & ~g.n_neutral]
        nobs = int(ded.observable.sum())
        if len(ded) == 0:
            a, why = "no", ("no dedicated step in any route (all routes all-shared)" if not g.n_neutral.any()
                            else "only dedicated route is N-neutral; other routes all-shared")
        elif nobs == 0:
            a, why = "no", "no dedicated route is observable (its KOs have no node in the KG): " + ";".join(ded.pathway_id)
        elif nobs < len(ded):
            a, why = "partly", "not observable: " + ";".join(ded[~ded.observable].pathway_id)
        else:
            a, why = "yes", "all dedicated routes observable"
        if g.n_neutral.any():
            why += "; N-neutral route excluded: " + ";".join(g[g.n_neutral].pathway_id)
        arow.append(dict(amino_acid=aa, n_pathways=len(g), n_dedicated_routes=len(ded),
                         n_observable_dedicated_routes=nobs, n_all_shared=int((~g.has_dedicated).sum()),
                         assessable=a, reason=why))
    adf = pd.DataFrame(arow)
    adf.to_csv(DATA / "aa_assessability.csv", index=False, encoding="utf-8")
    print("pathways observable:", int(pdf.observable.sum()), "of", len(pdf),
          "| differs from all-steps definition:", int((pdf.observable != pdf.all_steps_observable).sum()))
    print(adf.to_string(index=False))

    # ---- expected-negative selection (first rank that is KEGG-valid and has a KG KO node with gene_count >= 1) ----
    ok = val.set_index("ko")
    chosen = None
    ctrl["kegg_valid_all"] = ctrl.kos.map(lambda s: all(ok.loc[k, "kegg_valid"] for k in s.split(";")))
    ctrl["in_kg_any"] = ctrl.kos.map(lambda s: any(ok.loc[k, "in_kg"] for k in s.split(";")))
    ctrl["in_kg_kos"] = ctrl.kos.map(lambda s: ";".join(k for k in s.split(";") if ok.loc[k, "in_kg"]))
    ctrl["kg_gene_count_total"] = ctrl.apply(lambda r: ";".join(f"{k}={kg_total.get(k, 0)}" for k in r.kos.split(";"))
                                             if r.control_type == "expected_negative" else "", axis=1)
    neg = ctrl[ctrl.control_type == "expected_negative"].copy()
    neg["r"] = neg.rank_or_tier.astype(int)
    for _, r in neg.sort_values("r").iterrows():
        if r.kegg_valid_all and r.in_kg_any and all((kg_total.get(k) or 0) >= 1 for k in r.kos.split(";") if ok.loc[k, "in_kg"]):
            chosen = r.control_id
            break
    ctrl["proposed"] = ctrl.apply(
        lambda r: ("yes" if r.control_id == chosen else "no (alternate)") if r.control_type == "expected_negative"
        else ("yes" if r.rank_or_tier in ("", "core") or pd.isna(r.rank_or_tier) else "optional"), axis=1)
    ctrl.to_csv(DATA / "proposed_controls.csv", index=False, encoding="utf-8")
    print("expected-negative chosen:", chosen)
    print(ctrl[["control_id", "kos", "kegg_valid_all", "in_kg_any", "proposed"]].to_string())


if __name__ == "__main__":
    main()
