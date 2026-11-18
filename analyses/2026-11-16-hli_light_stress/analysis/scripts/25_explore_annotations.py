"""Exploratory: do KG annotations separate the two MED4 hli groups (responders = D clusters 3+4,
quiet = D clusters 1+2)? Researcher curiosity question; descriptive only.

Pulls, for the 23 MED4 hli genes in analysis/data/explore_D5_conservation.csv:
  - gene_ontology_terms over every registered ontology (ontology=None), leaf mode and rollup to level 1
  - gene_details scalar / list fields (product, gene name, TM regions, localization, ...)
  - gene_aa_sequence (length, simple composition, Kyte-Doolittle hydrophobic-window counts)
  - gene_neighbors (window=1: immediate up/downstream neighbour products)

Writes:
  analysis/data/explore_F_annotations.csv       long: locus_tag, group, cluster, mode, source, term_id, term_name, ...
  analysis/data/explore_F_term_by_group.csv     per (mode, source, term): n_responders_with, n_quiet_with, Fisher p
  analysis/data/explore_F_gene_features.csv     one row per gene
  analysis/data/explore_F_kg_calls.csv          KG call log (tool, args, total_matching, returned)
  analysis/data/explore_F_feature_by_group.csv  per-feature responder vs quiet comparison (descriptive)
  analysis/data/explore_F_details_keys.csv      gene_details keys and how many of the 23 genes carry each

Run from repo root:
  PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/25_explore_annotations.py
"""
from pathlib import Path
import json

import pandas as pd
from scipy.stats import fisher_exact, mannwhitneyu
from multiomics_explorer import gene_ontology_terms, gene_details, gene_aa_sequence, gene_neighbors

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"

cons = pd.read_csv(DATA / "explore_D5_conservation.csv", encoding="utf-8")
cons = cons[["locus_tag", "cluster", "ck_group", "copy_class", "n_organisms"]].copy()
GROUP = {1: "quiet", 2: "quiet", 3: "responder", 4: "responder"}
cons["group"] = cons["cluster"].map(GROUP)
assert cons["group"].notna().all(), "unexpected cluster id"
cons = cons.sort_values(["group", "cluster", "locus_tag"]).reset_index(drop=True)
LT = cons["locus_tag"].tolist()
assert len(LT) == 23, len(LT)
n_resp = int((cons["group"] == "responder").sum())
n_quiet = int((cons["group"] == "quiet").sum())

calls = []


def log(tool, args, r):
    calls.append({"tool": tool, "args": json.dumps(args), "total_matching": r.get("total_matching"),
                  "returned": r.get("returned", len(r.get("results", []))),
                  "truncated": r.get("truncated"), "not_found": json.dumps(r.get("not_found", [])),
                  "extra": json.dumps({k: r[k] for k in ("no_terms", "not_matched", "skipped_ontologies", "warnings")
                                       if k in r})})


# ---- 1. ontology terms, every registered ontology ----
ann_rows = []
registered = None
for mode, level in (("leaf", None), ("rollup", 1)):
    args = dict(locus_tags=LT, organism="MED4", ontology=None, mode=mode, level=level, limit=None)
    r = gene_ontology_terms(**args)
    log("gene_ontology_terms", {k: v for k, v in args.items() if k != "locus_tags"} | {"n_locus_tags": len(LT)}, r)
    assert r["total_matching"] == len(r["results"]), "truncated"
    if registered is None:
        registered = sorted(r["trust_axes"].keys())
    for x in r["results"]:
        ann_rows.append({"locus_tag": x["locus_tag"], "mode": mode if level is None else f"rollup_L{level}", "source": x.get("ontology_type"),
                         "term_id": x["term_id"], "term_name": x.get("term_name"), "level": x.get("level"),
                         "is_informative": x.get("is_informative"), "evidence": x.get("evidence")})

# ---- 2. gene_details ----
args = dict(locus_tags=LT, limit=None)
d = gene_details(**args)
log("gene_details", {"n_locus_tags": len(LT), "limit": None}, d)
assert d["total_matching"] == len(d["results"]) == 23
det = {x["locus_tag"]: x for x in d["results"]}

# extra annotation-like fields from gene_details added to the long table (source prefixed 'details:')
for lt, x in det.items():
    for fld in ("gene_category", "subcellular_localization", "signal_peptide_type", "annotation_state"):
        if x.get(fld) not in (None, "", []):
            ann_rows.append({"locus_tag": lt, "mode": "details", "source": f"details:{fld}",
                             "term_id": str(x[fld]), "term_name": str(x[fld])})
    for fld in ("cluster_types", "merops_classes"):
        for v in x.get(fld) or []:
            ann_rows.append({"locus_tag": lt, "mode": "details", "source": f"details:{fld}",
                             "term_id": str(v), "term_name": str(v)})
    for fld in ("numeric_metric_types_observed", "boolean_metric_types_observed",
                "categorical_metric_types_observed"):
        for v in x.get(fld) or []:
            ann_rows.append({"locus_tag": lt, "mode": "details", "source": f"details:{fld}",
                             "term_id": str(v), "term_name": str(v)})

ann = pd.DataFrame(ann_rows).merge(cons[["locus_tag", "group", "cluster"]], on="locus_tag", how="left")
# kind: 'annotation' = sequence/curation-based; 'data_coverage' = which KG datasets/metrics/clusterings
# the gene appears in (derived from expression or TSS data, not from the gene's sequence or curation)
DATA_COV = {"details:cluster_types", "details:numeric_metric_types_observed",
            "details:boolean_metric_types_observed", "details:categorical_metric_types_observed",
            "details:annotation_state"}
ann["kind"] = ann["source"].map(lambda s: "data_coverage" if s in DATA_COV else "annotation")
ann = ann[["locus_tag", "group", "cluster", "kind", "mode", "source", "term_id", "term_name", "level",
           "is_informative", "evidence"]].sort_values(["mode", "source", "term_id", "group", "locus_tag"])
ann.to_csv(DATA / "explore_F_annotations.csv", index=False, encoding="utf-8")

# ---- 3. per-term summary ----
grp = cons.set_index("locus_tag")["group"]
trows = []
for (kind, mode, source, term_id), g in ann.groupby(["kind", "mode", "source", "term_id"], dropna=False):
    genes = set(g["locus_tag"])
    a = sum(grp[l] == "responder" for l in genes)
    b = sum(grp[l] == "quiet" for l in genes)
    _, p = fisher_exact([[a, n_resp - a], [b, n_quiet - b]], alternative="two-sided")
    trows.append({"kind": kind, "mode": mode, "source": source, "term_id": term_id,
                  "term_name": g["term_name"].iloc[0],
                  "locus_tags_with": ";".join(sorted(genes)),
                  "n_responders_with": a, "n_responders_total": n_resp, "n_quiet_with": b,
                  "n_quiet_total": n_quiet, "frac_responders": a / n_resp, "frac_quiet": b / n_quiet,
                  "fisher_p_two_sided": p,
                  "note": "descriptive only; n=15 vs 8, untested family of terms, no correction"})
tbg = pd.DataFrame(trows).sort_values(["kind", "fisher_p_two_sided", "mode", "source", "term_id"])
tbg.to_csv(DATA / "explore_F_term_by_group.csv", index=False, encoding="utf-8")

# ---- 4. sequences ----
args = dict(locus_tags=LT, limit=100)
s = gene_aa_sequence(**args)
log("gene_aa_sequence", {"n_locus_tags": len(LT), "limit": 100}, s)
assert s["total_matching"] == len(s["results"])
seq = {x["locus_tag"]: x.get("sequence") for x in s["results"]}

KD = {"A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5, "E": -3.5, "G": -0.4, "H": -3.2,
      "I": 4.5, "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8, "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9,
      "Y": -1.3, "V": 4.2}


def kd_features(sq, w=19, thr=1.6):
    """Max KD window mean, and number of separate stretches with window mean >= thr."""
    if not sq or len(sq) < w:
        return None, 0
    means = [sum(KD.get(c, 0) for c in sq[i:i + w]) / w for i in range(len(sq) - w + 1)]
    n, inside = 0, False
    for m in means:
        if m >= thr and not inside:
            n, inside = n + 1, True
        elif m < thr:
            inside = False
    return round(max(means), 3), n


# ---- 5. neighbours ----
args = dict(locus_tags=LT, window=1, limit=200)
nb = gene_neighbors(**args)
log("gene_neighbors", {"n_locus_tags": len(LT), "window": 1, "limit": 200}, nb)
assert nb["total_matching"] == len(nb["results"])
nbdf = pd.DataFrame(nb["results"])
nb_lt = set(nbdf["neighbor_locus_tag"])

feat = []
for _, row in cons.iterrows():
    lt = row["locus_tag"]
    x = det.get(lt, {})
    sq = seq.get(lt) or ""
    kmax, kn = kd_features(sq)
    up = nbdf[(nbdf.anchor_locus_tag == lt) & (nbdf.rank_offset == -1)]
    dn = nbdf[(nbdf.anchor_locus_tag == lt) & (nbdf.rank_offset == 1)]

    def nbstr(t):
        if t.empty:
            return ""
        r0 = t.iloc[0]
        return f"{r0['neighbor_locus_tag']}|{r0['gene_name']}|{r0['product']}|{r0['strand']}|gap={r0['bp_gap']}"
    leaf_terms = ann[(ann.locus_tag == lt) & (ann["mode"] == "leaf")]
    tm = x.get("transmembrane_regions") or []
    feat.append({
        "locus_tag": lt, "group": row["group"], "cluster": row["cluster"], "ck_group": row["ck_group"],
        "copy_class": row["copy_class"], "n_organisms": row["n_organisms"],
        "gene_name": x.get("gene_name"), "product": x.get("product"), "gene_category": x.get("gene_category"),
        "all_identifiers": ";".join(x.get("all_identifiers") or []),
        "start": x.get("start"), "end": x.get("end"), "strand": x.get("strand"), "contig": x.get("contig"),
        "protein_length": len(sq) if sq else None,
        "n_tm_regions_kg": len(tm), "tm_regions_kg": ";".join(tm),
        "subcellular_localization": x.get("subcellular_localization"),
        "signal_peptide_type": x.get("signal_peptide_type"),
        "kd_max_window19": kmax, "kd_n_stretches_ge1.6": kn,
        "frac_hydrophobic_AILMFVWC": round(sum(c in "AILMFVWC" for c in sq) / len(sq), 3) if sq else None,
        "frac_charged_DEKR": round(sum(c in "DEKR" for c in sq) / len(sq), 3) if sq else None,
        "frac_aromatic_FWY": round(sum(c in "FWY" for c in sq) / len(sq), 3) if sq else None,
        "n_leaf_terms": len(leaf_terms), "leaf_ontologies": ";".join(sorted(leaf_terms["source"].dropna().unique())),
        "annotation_types": ";".join(x.get("annotation_types") or []),
        "informative_annotation_types": ";".join(x.get("informative_annotation_types") or []),
        "annotation_quality": x.get("annotation_quality"), "annotation_state": x.get("annotation_state"),
        "interpro_entry_count": x.get("interpro_entry_count"), "ncbifam_family_count": x.get("ncbifam_family_count"),
        "tcdb_assignment_count": x.get("tcdb_assignment_count"), "cazy_family_count": x.get("cazy_family_count"),
        "merops_family_count": x.get("merops_family_count"),
        "closest_ortholog_group_size": x.get("closest_ortholog_group_size"),
        "seed_ortholog": x.get("seed_ortholog"), "seed_ortholog_evalue": x.get("seed_ortholog_evalue"),
        "discussed_in_publication_count": x.get("discussed_in_publication_count"),
        "cluster_membership_count": x.get("cluster_membership_count"),
        "cluster_types": ";".join(x.get("cluster_types") or []),
        "numeric_metric_count": x.get("numeric_metric_count"), "boolean_metric_count": x.get("boolean_metric_count"),
        "categorical_metric_count": x.get("categorical_metric_count"),
        "expression_edge_count": x.get("expression_edge_count"),
        "significant_up_count": x.get("significant_up_count"),
        "significant_down_count": x.get("significant_down_count"),
        "upstream_neighbor": nbstr(up), "downstream_neighbor": nbstr(dn),
        "n_adjacent_neighbors_that_are_hli_set": int(sum(n in set(LT) for n in
                                                         nbdf[nbdf.anchor_locus_tag == lt].neighbor_locus_tag)),
        "sequence": sq,
    })
fdf = pd.DataFrame(feat)
fdf["has_adjacent_hli_in_set"] = fdf["n_adjacent_neighbors_that_are_hli_set"] > 0
fdf["sequence_identical_to_other_in_set"] = fdf["sequence"].duplicated(keep=False) & (fdf["sequence"] != "")
fdf["identical_sequence_partners"] = [
    ";".join(sorted(fdf.loc[(fdf.sequence == s) & (fdf.locus_tag != l), "locus_tag"])) for l, s in
    zip(fdf.locus_tag, fdf.sequence)]
fdf["has_pfam_PF00504"] = fdf.locus_tag.isin(ann[(ann["mode"] == "leaf") & (ann.term_id == "pfam:PF00504")].locus_tag)
fdf["has_any_go"] = fdf.locus_tag.isin(ann[(ann["mode"] == "leaf") & ann.source.isin(["go_bp", "go_cc", "go_mf"])].locus_tag)
fdf.to_csv(DATA / "explore_F_gene_features.csv", index=False, encoding="utf-8")

# per-feature group comparison (descriptive only; tiny n, no correction)
cmp_rows = []
R, Q = fdf[fdf.group == "responder"], fdf[fdf.group == "quiet"]
for c in ["protein_length", "n_tm_regions_kg", "kd_max_window19", "kd_n_stretches_ge1.6",
          "frac_hydrophobic_AILMFVWC", "frac_charged_DEKR", "frac_aromatic_FWY", "n_leaf_terms",
          "annotation_quality", "closest_ortholog_group_size", "discussed_in_publication_count"]:
    a, b = R[c].dropna().astype(float), Q[c].dropna().astype(float)
    p = mannwhitneyu(a, b, alternative="two-sided").pvalue
    cmp_rows.append({"feature": c, "test": "Mann-Whitney U two-sided", "responder_values": ";".join(map(str, sorted(a))),
                     "quiet_values": ";".join(map(str, sorted(b))), "responder_median": a.median(),
                     "quiet_median": b.median(), "p": p})
for c in ["has_adjacent_hli_in_set", "sequence_identical_to_other_in_set", "has_pfam_PF00504", "has_any_go"]:
    a, b = int(R[c].sum()), int(Q[c].sum())
    p = fisher_exact([[a, len(R) - a], [b, len(Q) - b]], alternative="two-sided")[1]
    cmp_rows.append({"feature": c, "test": "Fisher exact two-sided", "responder_values": f"{a}/{len(R)}",
                     "quiet_values": f"{b}/{len(Q)}", "responder_median": None, "quiet_median": None, "p": p})
cmp = pd.DataFrame(cmp_rows)
cmp["note"] = "descriptive only; n=15 vs 8; no multiple-testing correction; identical-sequence copies not collapsed"
# sensitivity: one row per distinct protein sequence (identical copies collapsed; all copies share a group)
U = fdf[fdf["sequence"] != ""].drop_duplicates("sequence")
UR, UQ = U[U.group == "responder"], U[U.group == "quiet"]
for c in ["protein_length", "frac_charged_DEKR", "frac_hydrophobic_AILMFVWC"]:
    a, b = UR[c].dropna().astype(float), UQ[c].dropna().astype(float)
    p = mannwhitneyu(a, b, alternative="two-sided").pvalue
    cmp = pd.concat([cmp, pd.DataFrame([{
        "feature": c + " (distinct sequences)", "test": "Mann-Whitney U two-sided",
        "responder_values": ";".join(map(str, sorted(a))), "quiet_values": ";".join(map(str, sorted(b))),
        "responder_median": a.median(), "quiet_median": b.median(), "p": p,
        "note": f"identical copies collapsed: {len(UR)} responder vs {len(UQ)} quiet distinct proteins"}])],
        ignore_index=True)
cmp.to_csv(DATA / "explore_F_feature_by_group.csv", index=False, encoding="utf-8")

# all gene_details keys seen (for the manifest)
keys = sorted({k for x in det.values() for k in x})
pd.DataFrame({"gene_details_key": keys,
              "n_genes_nonnull": [sum(det[l].get(k) not in (None, "", [], 0) for l in det) for k in keys]}
             ).to_csv(DATA / "explore_F_details_keys.csv", index=False, encoding="utf-8")
pd.DataFrame(calls).to_csv(DATA / "explore_F_kg_calls.csv", index=False, encoding="utf-8")

print("registered ontologies:", registered)
print("annotations rows:", len(ann), "| term_by_group rows:", len(tbg), "| features rows:", len(fdf))
print(pd.DataFrame(calls)[["tool", "total_matching", "returned", "truncated", "not_found", "extra"]].to_string())
