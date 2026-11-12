"""Spike: genome-first amino-acid AND peptide utilization gene table, per organism.
One row per (locus_tag, role). Membership is by ontology ids / KG routes, never by product text;
product text is used only to LABEL (aa_class, subrole, housekeeping flag).

Run (repo root):
  PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s01_build_table.py MED4 med4
  PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s01_build_table.py HOT1A3 hot1a3
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import multiomics_explorer as me

ORG, TAG = sys.argv[1], sys.argv[2]
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
PRIOR = ROOT.parents[1] / "2026-11-04-aa_utilization_genomics"
K = "kegg.compound:"

# ---- metabolite ids (reused from the prior spike s03_uptake.py; verified there) ----
AA = {
 "Ala": [K+"C01401", K+"C00041", K+"C00133"], "Arg": [K+"C00062", K+"C00792", K+"C02385"],
 "Asn": [K+"C16438", K+"C00152"], "Asp": [K+"C16433", K+"C00049", K+"C00402"],
 "Cys": [K+"C00736", K+"C00097", K+"C00793"], "Glu": [K+"C00302", K+"C00025", K+"C00217"],
 "Gln": [K+"C00303", K+"C00064", K+"C00819"], "Gly": [K+"C00037"], "His": [K+"C00768", K+"C00135"],
 "Ile": ["chebi:24898", K+"C00407"], "Leu": [K+"C16439", K+"C00123"], "Lys": [K+"C16440", K+"C00047", K+"C00739"],
 "Met": [K+"C01733", K+"C00073", K+"C00855"], "Phe": [K+"C02057", K+"C00079", K+"C02265"],
 "Pro": [K+"C16435", K+"C00148", K+"C00763"], "Ser": [K+"C00716", K+"C00065", K+"C00740"],
 "Thr": [K+"C00188"], "Trp": [K+"C00806", K+"C00078"], "Tyr": [K+"C01536", K+"C00082"],
 "Val": [K+"C16436", K+"C00183", K+"C06417"],
}
CLASSES = {
 "class:amino_acid": [K+"C00045", "chebi:33709"], "class:L-amino_acid": [K+"C00151"],
 "class:D-amino_acid": [K+"C00405"], "class:branched-chain_aa": ["chebi:22918"],
 "class:polar_aa": ["chebi:26167"], "class:aromatic_aa": [K+"C01021"], "class:sulfur_aa": ["chebi:26834"],
}
PEPTIDES = {"peptide": [K+"C00012"], "dipeptide": [K+"C00107"], "oligopeptide": [K+"C00098"],
            "tripeptide": ["chebi:47923"]}

# ---- substrate keyword -> aa_class (labelling only; word-bounded) ----
KW = [
 (r"\bbranched[- ]chain\b|\bleucine\b|\bisoleucine\b|\bvaline\b|\bleucyl\b", "hydrophobic/branched-chain"),
 (r"\bglutamate\b|\baspartate\b|\bglutamic\b|\baspartic\b|\bglutamyl\b|\baspartyl\b", "acidic"),
 (r"\bglutamine\b|\basparagine\b|\bglutaminase\b|\basparaginase\b", "amides (Asn/Gln)"),
 (r"\bglycine\b|\balanine\b|\bserine\b|\balanyl\b|\bseryl\b|\bglycyl\b", "small (Gly/Ala/Ser)"),
 (r"\barginine\b|\blysine\b|\bhistidine\b|\bornithine\b|\barginase\b|\bagmatin", "basic"),
 (r"\bphenylalanine\b|\btyrosine\b|\btryptophan\b|\baromatic[- ]amino\b|\btryptophanase\b", "aromatic"),
 (r"\bcysteine\b|\bmethionine\b|\bcystathionine\b|\bcystine\b|\bmethionyl\b", "sulfur"),
 (r"\bthreonine\b|\bproline\b|\bprolyl\b|\bpolar amino\b", "polar/neutral"),
]
CLASS_OF_AA = {"Ala": "small (Gly/Ala/Ser)", "Gly": "small (Gly/Ala/Ser)", "Ser": "small (Gly/Ala/Ser)",
 "Leu": "hydrophobic/branched-chain", "Ile": "hydrophobic/branched-chain", "Val": "hydrophobic/branched-chain",
 "Asp": "acidic", "Glu": "acidic", "Asn": "amides (Asn/Gln)", "Gln": "amides (Asn/Gln)",
 "Arg": "basic", "Lys": "basic", "His": "basic", "Phe": "aromatic", "Tyr": "aromatic", "Trp": "aromatic",
 "Cys": "sulfur", "Met": "sulfur", "Thr": "polar/neutral", "Pro": "polar/neutral",
 "class:branched-chain_aa": "hydrophobic/branched-chain", "class:polar_aa": "polar/neutral",
 "class:aromatic_aa": "aromatic", "class:sulfur_aa": "sulfur", "class:amino_acid": "broad/unknown",
 "class:L-amino_acid": "broad/unknown", "class:D-amino_acid": "broad/unknown",
 "peptide": "peptides", "dipeptide": "peptides", "oligopeptide": "peptides", "tripeptide": "peptides"}

def kw_classes(text):
    t = (text or "").lower()
    hits = [c for pat, c in KW if re.search(pat, t)]
    subs = sorted({m.group(0) for pat, _ in KW for m in re.finditer(pat, t)})
    return hits, subs

envelopes = []
def env(call, args, r):
    envelopes.append({"organism": ORG, "call": call, "args": json.dumps(args)[:300],
                      "total_matching": r.get("total_matching"), "returned": r.get("returned"),
                      "not_found": json.dumps(r.get("not_found")), "warnings": " | ".join(r.get("warnings") or [])})

def gbo(ontology, term_ids=None, **kw):
    args = dict(ontology=ontology, organism=ORG, term_ids=term_ids, min_gene_set_size=0,
                max_gene_set_size=100000, limit=None, **kw)
    r = me.genes_by_ontology(**args)
    assert r["returned"] == r["total_matching"], (ontology, term_ids)
    env("genes_by_ontology", {k: v for k, v in args.items() if k != "organism"}, r)
    return r["results"]

def gbm(ids, **kw):
    args = dict(metabolite_ids=ids, organism=ORG, limit=None, include_stereo_forms=True, **kw)
    r = me.genes_by_metabolite(**args)
    assert r["returned"] == r["total_matching"], ids
    env("genes_by_metabolite", {k: v for k, v in args.items() if k != "organism"}, r)
    return r["results"]

# rows: (locus_tag, role) -> dict of sets
REC = defaultdict(lambda: defaultdict(set))
GENE = {}
def add(lt, role, subrole=None, evidence=None, quality=None, substrate=None, aa_class=None, note=None,
        gene_name=None, product=None, **extra):
    d = REC[(lt, role)]
    if subrole: d["subrole"].add(subrole)
    if evidence: d["evidence"].add(evidence)
    if quality: d["quality"].add(quality)
    if substrate: d["substrate"].add(substrate)
    if aa_class: d["aa_class"].add(aa_class)
    if note: d["notes"].add(note)
    for k, v in extra.items():
        if v: d[k].add(v)
    if lt not in GENE or (not GENE[lt].get("product") and product):
        GENE[lt] = {"gene_name": gene_name, "product": product}

# =================== UPTAKE ===================
def abc_part(product):
    p = (product or "").lower()
    if re.search(r"atp-binding|atpase", p):
        return "ABC transporter ATPase"
    if re.search(r"substrate[- ]binding|periplasmic|binding protein|binding component|solute-binding", p):
        return "ABC transporter SBP"
    if re.search(r"permease|membrane component|transmembrane|membrane protein|inner membrane", p):
        return "ABC transporter permease"
    return "ABC transporter (component unclear)"

def uptake_subrole(product, fam):
    fam = fam or ""
    if fam.startswith("tcdb:3.A.1") or re.search(r"\babc\b", (product or "").lower()):
        return abc_part(product)
    if fam.startswith("tcdb:2.A"):
        return "secondary transporter"
    return "transporter (type unclear)"

targets = {**AA, **CLASSES, **PEPTIDES}
for tgt, ids in targets.items():
    for x in gbm(ids, evidence_sources=["transport"], include_tcdb_family_substrates=True):
        route = x.get("tcdb_route")
        fam = x.get("tcdb_family_id")
        q = "tcdb direct system" if route != "family" else "tcdb family-walk candidate (weak)"
        add(x["locus_tag"], "uptake", uptake_subrole(x.get("product"), fam),
            f"TCDB {fam} [{route}] -> {x.get('metabolite_name')}", q,
            substrate=f"TCDB: {x.get('metabolite_name')}", aa_class=CLASS_OF_AA[tgt],
            gene_name=x.get("gene_name"), product=x.get("product"),
            tcdb_dir=x.get("tcdb_direction"))
    for x in gbm(ids, evidence_sources=["go_transport"], go_include_ancestors=True,
                 go_namespace=["molecular_function"]):
        add(x["locus_tag"], "uptake", uptake_subrole(x.get("product"), None),
            f"GO {x.get('go_term_id')} {x.get('go_term_name')} (depth {x.get('go_term_depth')})",
            f"GO {x.get('go_evidence')}", substrate=f"GO: {x.get('go_term_name')}",
            aa_class=CLASS_OF_AA[tgt], gene_name=x.get("gene_name"), product=x.get("product"))

# TCDB families relevant to AA / peptides (ids verified with search_ontology / genes_by_ontology)
TCDB_FAMS = {"tcdb:3.A.1.3": "PAAT", "tcdb:3.A.1.4": "HAAT", "tcdb:3.A.1.5": "PepT",
             "tcdb:2.A.3": "APC", "tcdb:2.A.23": "DAACS", "tcdb:2.A.26": "LIVCS", "tcdb:2.A.17": "POT",
             "tcdb:2.A.27": "ESS", "tcdb:2.A.22": "NSS", "tcdb:2.A.25": "AGCS", "tcdb:2.A.78": "LIV-E",
             "tcdb:2.A.76": "RhtB", "tcdb:2.A.67": "OPT", "tcdb:3.A.1.124": "Pep4E?"}
FAM_CLASS = {"PAAT": "polar/neutral", "HAAT": "hydrophobic/branched-chain", "PepT": "peptides",
             "POT": "peptides", "OPT": "peptides", "LIVCS": "hydrophobic/branched-chain",
             "ESS": "acidic", "DAACS": "acidic", "AGCS": "small (Gly/Ala/Ser)",
             "LIV-E": "hydrophobic/branched-chain"}
for fid, short in TCDB_FAMS.items():
    rows = gbo("tcdb", [fid])
    for x in rows:
        add(x["locus_tag"], "uptake", uptake_subrole(x.get("product"), fid),
            f"TCDB family {fid} ({short}) via {x.get('term_id')} [{x.get('tcdb_call')}/{x.get('tcdb_gate')}]",
            f"tcdb family {x.get('evidence')}",
            substrate=f"TCDB family name: {short}",
            aa_class=FAM_CLASS.get(short, "broad/unknown"),
            gene_name=x.get("gene_name"), product=x.get("product"),
            fam_class_note=f"aa_class from TCDB family name ({short}), not a stated system substrate")

# GO MF: amino acid / peptide transmembrane transporter subtrees
for gid, cls in [("GO:0015171", "broad/unknown"), ("GO:1904680", "peptides"), ("GO:0015658", "hydrophobic/branched-chain")]:
    for x in gbo("go_mf", [gid]):
        add(x["locus_tag"], "uptake", uptake_subrole(x.get("product"), None),
            f"GO {x.get('term_id')} {x.get('term_name')}", f"GO {x.get('evidence')}",
            substrate=f"GO: {x.get('term_name')}", aa_class=cls,
            gene_name=x.get("gene_name"), product=x.get("product"))

# SBP derived metric (BST20200244) — covers picocyanobacteria only
try:
    r = me.genes_by_categorical_metric(metric_types=["sbp_predicted_substrate"], organism=ORG, limit=None)
    env("genes_by_categorical_metric", {"metric_types": ["sbp_predicted_substrate"]}, r)
    sbp = {x["locus_tag"]: x.get("value") for x in r["results"]}
except Exception as e:  # organism outside the survey
    envelopes.append({"organism": ORG, "call": "genes_by_categorical_metric", "args": "sbp_predicted_substrate",
                      "total_matching": 0, "returned": 0, "not_found": "", "warnings": f"ERR {e}"})
    sbp = {}
SBP_CLASS = {"peptide": "peptides", "amino_acids": "broad/unknown", "polar_amino_acids": "polar/neutral",
             "branched_chain_amino_acids": "hydrophobic/branched-chain"}
for lt, v in sbp.items():
    if v in SBP_CLASS or "amino" in str(v) or "peptide" in str(v):
        add(lt, "uptake", "ABC transporter SBP", f"SBP metric BST20200244 sbp_predicted_substrate={v}",
            "derived metric (sequence-based prediction)", substrate=f"SBP: {v}",
            aa_class=SBP_CLASS.get(v, "broad/unknown"))

# =================== PEPTIDASES ===================
EC_SUB = {"3.4.11": "aminopeptidase", "3.4.13": "dipeptidase", "3.4.14": "dipeptidyl/tripeptidyl-peptidase",
          "3.4.15": "peptidyl-dipeptidase", "3.4.16": "serine carboxypeptidase", "3.4.17": "metallocarboxypeptidase",
          "3.4.18": "cysteine carboxypeptidase", "3.4.19": "omega peptidase", "3.4.21": "serine endopeptidase",
          "3.4.22": "cysteine endopeptidase", "3.4.23": "aspartic endopeptidase", "3.4.24": "metalloendopeptidase",
          "3.4.25": "threonine endopeptidase", "3.4.99": "endopeptidase (unknown mechanism)"}
HOUSEKEEPING = (r"signal peptid|ftsh|\bclp|lon protease|\blon\b|htpx|processing peptid|processing protease|"
                r"protease iv|sppa|maturation protease|prepilin|site-2|rsep|glycoprotease|tsad|kae1|"
                r"methionine aminopeptidase|transpeptidase|penicillin[- ]binding|d-alanyl-d-alanine|"
                r"murein|hflk|hflc|deg[pqs]|htra|serine endoprotease|protease do|ctpa|carboxyl-terminal processing|"
                r"c-terminal processing|deformylase|sodx|zinc metalloprotease|psb|d1 protein|ycf3|hyb|hydrogenase")
pep_ec = defaultdict(set)
for x in gbo("ec", ["ec:3.4.-.-"]):
    add(x["locus_tag"], "peptidase", None, f"EC {x['term_id']} {x.get('term_name')}", f"EC {x.get('evidence')}",
        aa_class="peptides", gene_name=x.get("gene_name"), product=x.get("product"))
# leaf ECs for sub-subclass
pep_lts = sorted({lt for (lt, role) in REC if role == "peptidase"})
for x in gbo("go_mf", ["GO:0008233"]):
    add(x["locus_tag"], "peptidase", None, f"GO {x['term_id']} {x.get('term_name')}", f"GO {x.get('evidence')}",
        aa_class="peptides", gene_name=x.get("gene_name"), product=x.get("product"))
for x in gbo("merops", None, level=1, call_class=["peptidase"]):
    add(x["locus_tag"], "peptidase", None, f"MEROPS {x['term_id']} {x.get('term_name')}",
        f"MEROPS {x.get('evidence')}", aa_class="peptides", gene_name=x.get("gene_name"), product=x.get("product"),
        merops=f"{x['term_id']} {x.get('term_name')}")

# =================== N-ENTRY ENZYMES ===================
NE_EC = {"ec:2.6.1.-": "aminotransferase", "ec:1.4.-.-": None, "ec:3.5.1.-": "amidohydrolase (linear amide)",
         "ec:3.5.3.-": "amidinohydrolase/ureohydrolase", "ec:4.3.1.-": "AA ammonia-lyase",
         "ec:4.1.1.-": "decarboxylase"}
ne_gate = {}  # locus -> needs gating (3.5.1 / 4.1.1)
for eid, sub in NE_EC.items():
    for x in gbo("ec", [eid]):
        s = sub
        if eid == "ec:1.4.-.-":
            tid = x["term_id"]
            s = ("AA dehydrogenase" if tid.startswith("ec:1.4.1") else "AA oxidase" if tid.startswith("ec:1.4.3")
                 else "glycine cleavage (P protein)" if tid.startswith("ec:1.4.4") else "oxidoreductase on CH-NH2 (other)")
        add(x["locus_tag"], "N-entry enzyme", s, f"EC {x['term_id']} {x.get('term_name')}",
            f"EC {x.get('evidence')}", gene_name=x.get("gene_name"), product=x.get("product"),
            ecname=x.get("term_name"))
        if eid in ("ec:3.5.1.-", "ec:4.1.1.-"):
            ne_gate.setdefault(x["locus_tag"], True)
        else:
            ne_gate[x["locus_tag"]] = False

# catalogue KOs from the prior analysis (pathway_catalogue_steps.csv), plus glycine cleavage KOs
cat = pd.read_csv(PRIOR / "methods/data/pathway_catalogue_steps.csv", encoding="utf-8")
ko_info = defaultdict(list)
for _, s in cat.iterrows():
    for ko in str(s["kos"]).split(";"):
        ko = ko.strip()
        if ko.startswith("K"):
            ko_info[ko].append((s["amino_acid"], s["step_key"], s["step_name"], s["flag"]))
GCV = {"K00281": "gcvP", "K00282": "gcvPA", "K00283": "gcvPB", "K00605": "gcvT", "K02437": "gcvH"}
ko_rows = gbo("kegg", [f"kegg.orthology:{k}" for k in sorted(set(ko_info) | set(GCV))])
cat_flag = defaultdict(set)
for x in ko_rows:
    ko = x["term_id"].split(":")[-1]
    if ko in GCV:
        add(x["locus_tag"], "N-entry enzyme", "glycine cleavage", f"KO {ko} {x.get('term_name')}",
            f"KO {x.get('evidence')}", substrate="glycine (KO name)", aa_class="small (Gly/Ala/Ser)",
            gene_name=x.get("gene_name"), product=x.get("product"))
        ne_gate[x["locus_tag"]] = False
    for aa, key, name, flag in ko_info.get(ko, []):
        add(x["locus_tag"], "N-entry enzyme", f"catalogue step: {name}", f"KO {ko} (catalogue {aa} {key})",
            f"KO {x.get('evidence')}", aa_class=CLASS_OF_AA.get(aa), substrate=f"catalogue: {aa}",
            gene_name=x.get("gene_name"), product=x.get("product"), kos=f"{ko} {x.get('term_name')}")
        cat_flag[x["locus_tag"]].add(flag)
        ne_gate[x["locus_tag"]] = False

# reaction layer: which N-entry candidates touch an amino acid in a KEGG reaction
rx_aa = defaultdict(set)
for aa, ids in AA.items():
    for x in gbm(ids, evidence_sources=["metabolism"]):
        rx_aa[x["locus_tag"]].add(aa)

# gate 3.5.1 / 4.1.1 rows: keep if reaction layer links an AA, or catalogue KO, or AA word in product/EC name
excluded = []
for (lt, role), d in list(REC.items()):
    if role != "N-entry enzyme" or not ne_gate.get(lt):
        continue
    text = (GENE[lt].get("product") or "") + " " + " ".join(d.get("ecname", []))
    hits, _ = kw_classes(text)
    if rx_aa.get(lt) or hits or re.search(r"amino[- ]acid", text.lower()):
        continue
    excluded.append({"organism": ORG, "locus_tag": lt, "gene_name": GENE[lt]["gene_name"],
                     "product": GENE[lt]["product"], "evidence": "; ".join(sorted(d["evidence"])),
                     "reason": "EC 3.5.1/4.1.1 with no amino-acid link (reaction layer, catalogue KO, or AA word)"})
    del REC[(lt, role)]

# =================== N-ASSIMILATION CORE + REGULATION ===================
CORE = {"K01915": "GS (glnA)", "K00284": "GOGAT (ferredoxin)", "K00265": "GOGAT (NADPH, large)",
        "K00266": "GOGAT (NADPH, small)", "K00260": "GDH", "K00261": "GDH", "K00262": "GDH", "K15371": "GDH",
        "K01427": "urease", "K01428": "urease", "K01429": "urease", "K01430": "urease", "K14048": "urease",
        "K03187": "urease accessory", "K03188": "urease accessory", "K03189": "urease accessory",
        "K03190": "urease accessory", "K03320": "ammonium transporter (amt)", "K01953": "asparagine synthetase",
        "K01914": "asparagine synthetase (ammonia)"}
REG = {"K04751": "PII (glnB)", "K04752": "PII (glnK)", "K00990": "glnD (PII uridylyltransferase)",
       "K07708": "ntrB/glnL", "K07712": "ntrC/glnG", "K03719": "Lrp/AsnC", "K03092": "rpoN (sigma-54)"}
for ko_map, role in [(CORE, "N-assimilation core"), (REG, "regulation-if-found")]:
    for x in gbo("kegg", [f"kegg.orthology:{k}" for k in ko_map]):
        ko = x["term_id"].split(":")[-1]
        add(x["locus_tag"], role, ko_map[ko], f"KO {ko} {x.get('term_name')}", f"KO {x.get('evidence')}",
            gene_name=x.get("gene_name"), product=x.get("product"), kos=f"{ko} {x.get('term_name')}")
for name in ["ntcA", "pipX", "glnB"]:
    r = me.resolve_gene(identifier=name, organism=ORG)
    env("resolve_gene", {"identifier": name}, r)
    for x in r["results"]:
        add(x["locus_tag"], "regulation-if-found", f"{name} (resolve_gene)", f"resolve_gene '{name}'",
            "name match", gene_name=x.get("gene_name"), product=x.get("product"))

# =================== per-gene KO / EC labels (for subrole + disagreement notes) ===================
lts = sorted({lt for lt, _ in REC})
r = me.gene_ontology_terms(locus_tags=lts, organism=ORG, ontology=["kegg", "ec"], mode="leaf", limit=None)
env("gene_ontology_terms", {"n_locus_tags": len(lts), "ontology": ["kegg", "ec"]}, r)
ko_of, ec_of = defaultdict(set), defaultdict(set)
for x in r["results"]:
    tid = x.get("term_id", "")
    if tid.startswith("kegg.orthology:"):
        ko_of[x["locus_tag"]].add(f"{tid.split(':')[-1]} {x.get('term_name')}")
    elif tid.startswith("ec:"):
        ec_of[x["locus_tag"]].add(f"{tid} {x.get('term_name')}")
    if x["locus_tag"] in GENE and not GENE[x["locus_tag"]].get("product"):
        GENE[x["locus_tag"]].update({k: x.get(k) for k in ("gene_name", "product") if x.get(k)})
missing = [lt for lt in lts if not GENE.get(lt, {}).get("product")]
if missing:
    r = me.gene_overview(locus_tags=missing, limit=None) if hasattr(me, "gene_overview") else {"results": []}
    for x in r.get("results", []):
        GENE.setdefault(x["locus_tag"], {}).update({"gene_name": x.get("gene_name"), "product": x.get("product")})

# =================== neighbours ===================
neigh = defaultdict(list)
for i in range(0, len(lts), 200):
    r = me.gene_neighbors(locus_tags=lts[i:i+200], window=3, limit=100000)
    env("gene_neighbors", {"n_anchors": len(lts[i:i+200]), "window": 3}, r)
    for x in r["results"]:
        neigh[x["anchor_locus_tag"]].append(x)

# =================== assemble ===================
KNOWN = {"PMM0674": "gene name aspC on KO K00812 (known name/KO disagreement from prior analysis)",
         "PMM1468": "gene name bioF; carries KO K00639 (kbl, glycine C-acetyltransferase) and K00652 (bioF) — flagged in prior analysis",
         "PMM0222": "gene name aspA; KO K01437 (ASPA, aspA; aspartoacylase) and product aspartoacylase — the symbol aspA here is not aspartate ammonia-lyase; flagged in prior analysis",
         "PMM0970": "urtA: in TCDB HAAT 3.A.1.4 family but TCDB system = high-affinity urea porter",
         "PMM0971": "urtB: in TCDB HAAT 3.A.1.4 family but TCDB system = high-affinity urea porter",
         "PMM0972": "urtC: HAAT family + curated GO branched-chain AA transporter, but product/TCDB system = urea porter",
         "PMM0973": "urtD: in TCDB HAAT 3.A.1.4 family but TCDB system = high-affinity urea porter",
         "PMM0974": "urtE: HAAT family + curated GO branched-chain AA transporter, but product/TCDB system = urea porter"}

def ec_subrole(lt):
    subs = set()
    for e in ec_of.get(lt, []):
        m = re.match(r"ec:(3\.4\.\d+)", e)
        if m and m.group(1) in EC_SUB:
            subs.add(EC_SUB[m.group(1)])
    return subs

def shared(role, subrole, lt, product):
    if role == "uptake":
        return "no — transport step"
    if role == "peptidase":
        return "no — hydrolyses peptide bonds" if "housekeeping" not in subrole else "no — protein processing/turnover"
    if role == "regulation-if-found":
        return "n/a — regulator"
    if role == "N-assimilation core":
        if subrole.startswith(("GS", "GOGAT", "asparagine")):
            return "yes — primary NH4+ assimilation / amide synthesis"
        if subrole.startswith("GDH"):
            return "unclear — GDH direction not set by annotation"
        return "no — urea/ammonium handling" if ("urease" in subrole or "amt" in subrole) else "unclear"
    flags = cat_flag.get(lt, set())
    if flags:
        if flags == {"dedicated"}:
            return "no — prior catalogue flag 'dedicated'"
        if "shared" in flags:
            return f"yes — prior catalogue flag(s) {'/'.join(sorted(flags))}"
        return f"unclear — prior catalogue flag(s) {'/'.join(sorted(flags))}"
    if "aminotransferase" in subrole:
        return "yes — transamination is reversible, used in AA biosynthesis"
    if "glycine cleavage" in subrole:
        return "unclear — glycine cleavage runs in both directions"
    return "unclear — no catalogue flag; direction not set by annotation"

table_lts = set(lts)
out = []
for (lt, role), d in sorted(REC.items()):
    g = GENE.get(lt, {})
    product, gname = g.get("product") or "", g.get("gene_name") or ""
    text = " ".join([product] + sorted(d.get("ecname", [])) + sorted(ko_of.get(lt, [])))
    kw_hit, kw_subs = kw_classes(product + " " + " ".join(sorted(d.get("ecname", []))))
    notes = set(d.get("notes", set())) | set(d.get("fam_class_note", set()))
    # subrole
    subs = set(d.get("subrole", set()))
    if role == "peptidase":
        subs |= ec_subrole(lt)
        if re.search(HOUSEKEEPING, (product + " " + gname).lower()):
            subs = {"housekeeping protease (by product keyword)"} | subs
        srcs = {e.split(" ")[0] for e in d.get("evidence", set())}
        if not subs:
            subs = {"GO-only peptidase call (check)"} if srcs == {"GO"} else {"peptidase (EC sub-subclass not stated)"}
        if d.get("merops"):
            notes.add("MEROPS: " + "; ".join(sorted(d["merops"])))
    # aa_class
    classes = set(d.get("aa_class", set())) - {None}
    if role in ("N-entry enzyme", "N-assimilation core", "regulation-if-found"):
        classes |= set(kw_hit)
    if role == "N-assimilation core" and not classes:
        classes = set()
    classes.discard("broad/unknown") if len(classes) > 1 else None
    if not classes:
        classes = {"broad/unknown"} if role != "regulation-if-found" else {"not applicable"}
    subs_stated = sorted(set(d.get("substrate", set())) | {f"name: {s}" for s in kw_subs})
    # disagreement notes
    if lt in KNOWN:
        notes.add(KNOWN[lt])
    kos = ko_of.get(lt, set())
    if gname and kos:
        syms = set()
        for k in kos:
            head = k.split(" ", 1)[1].split(";")[0] if " " in k else ""
            syms |= {s.strip().lower() for s in head.split(",")}
        base = re.sub(r"\d+$", "", gname.lower())
        if syms and gname.lower() not in syms and base not in syms:
            notes.add(f"gene name '{gname}' not among KO symbols ({'; '.join(sorted(kos))})")
    if rx_aa.get(lt) and role == "N-entry enzyme":
        notes.add("KG reaction layer links AA: " + ",".join(sorted(rx_aa[lt])))
    if d.get("tcdb_dir"):
        notes.add("TCDB direction: " + ",".join(sorted(d["tcdb_dir"])))
    # neighbours
    nb = sorted(neigh.get(lt, []), key=lambda x: x["rank_offset"])
    nb_str = "; ".join(f"{x['rank_offset']:+d} {x['neighbor_locus_tag']} {x.get('gene_name') or '-'}"
                       f"{' [IN TABLE]' if x['neighbor_locus_tag'] in table_lts else ''}" for x in nb)
    nb_in = sum(x["neighbor_locus_tag"] in table_lts for x in nb)
    q = d.get("quality", set())
    quality = ("curated" if any("curated" in s for s in q) else "inferred/family") + " | " + "; ".join(sorted(q))
    if role == "uptake" and re.search(r"translocase|translocation|sec[a-z]|tat[a-z]", (product + " " + gname).lower()):
        subs = {"protein translocation (by product keyword)"} | subs
    ev = d.get("evidence", set())
    weak = "no"
    if role == "uptake" and ev and all("[family]" in e for e in ev):
        weak = "yes - TCDB family-walk only"
    if role == "peptidase":
        srcs = {e.split(" ")[0] for e in ev}
        weak = "yes - GO only" if srcs == {"GO"} else "no"
    sub_join = " | ".join(sorted(subs))
    out.append({"organism": ORG, "role": role, "subrole": sub_join,
                "aa_class": " | ".join(sorted(classes)),
                "substrates_stated": " | ".join(subs_stated),
                "locus_tag": lt, "gene_name": gname, "product": product,
                "evidence": " || ".join(sorted(d.get("evidence", set()))),
                "evidence_quality": quality, "weak_evidence_only": weak,
                "evidence_sources": ",".join(sorted({e.split(" ")[0] for e in ev})),
                "ko": " | ".join(sorted(kos)), "ec": " | ".join(sorted(ec_of.get(lt, set()))),
                "shared_with_biosynthesis [interpretation]": shared(role, sub_join, lt, product),
                "operon_neighbours": nb_str, "n_neighbours_in_table": nb_in,
                "notes": " | ".join(sorted(notes))})

df = pd.DataFrame(out)
ROLE_ORDER = ["uptake", "peptidase", "N-entry enzyme", "N-assimilation core", "regulation-if-found"]
df["role"] = pd.Categorical(df["role"], ROLE_ORDER, ordered=True)
df = df.sort_values(["role", "subrole", "locus_tag"]).reset_index(drop=True)
df.to_csv(DATA / f"{TAG}_aa_peptide_gene_table.csv", index=False, encoding="utf-8")
pd.DataFrame(excluded).to_csv(DATA / f"{TAG}_excluded_nentry_candidates.csv", index=False, encoding="utf-8")
pd.DataFrame(envelopes).to_csv(DATA / f"{TAG}_query_envelopes.csv", index=False, encoding="utf-8")
print(ORG, "rows", len(df), "unique genes", df.locus_tag.nunique(), "excluded", len(excluded))
print(df.groupby("role", observed=True).agg(rows=("locus_tag", "size"), genes=("locus_tag", "nunique")))
