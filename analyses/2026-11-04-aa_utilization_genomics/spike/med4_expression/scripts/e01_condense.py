"""Condense gene_response_profile (MED4, 14 genes, nitrogen + coculture experiments, group_by=experiment)
into a gene x experiment table. Input: data/gene_response_profile_raw.json (MCP output, 2026-11-04, KG 0.1.0-alpha.9).
Output: data/med4_aa_gene_responses.csv
Cell = direction (UP/DOWN/MIX/ns), largest |log2FC| in that direction, significant timepoints / tested timepoints."""
import json, csv, pathlib
here = pathlib.Path(__file__).resolve().parents[1]
d = json.load(open(here / "data/gene_response_profile_raw.json", encoding="utf-8"))
short = {'ismej.2016.70_coculture':'Cocult2016','growth_on_cyanate':'Tolonen-cyanate','growth_on_urea':'Tolonen-urea','nitrogen_deprivation_med4':'Tolonen-Ndep',
 '690089_coculture':'Cocult2025','ismej.2017.88':'Read-Ndep','proteomics_axenic':'2025-Nstarv-protein-axenic','rnaseq_axenic':'2025-Nstarv-RNA-axenic',
 'proteomics_coculture':'2025-Nstarv-protein-coculture','rnaseq_coculture':'2025-Nstarv-RNA-coculture'}
nm = lambda e: next((v for k, v in short.items() if k in e), e)
exps = sorted({e for r in d['results'] for e in r['response_summary']}, key=nm)
with open(here / "data/med4_aa_gene_responses.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["locus_tag", "gene_name", "product"] + [nm(e) for e in exps])
    for r in d['results']:
        row = [r['locus_tag'], r['gene_name'] or "", r['product']]
        for e in exps:
            s = r['response_summary'].get(e)
            if not s: row.append("not in experiment"); continue
            u, dn, t = s['timepoints_up'], s['timepoints_down'], s['timepoints_tested']
            lab = 'UP' if u and not dn else 'DOWN' if dn and not u else 'MIX' if u and dn else 'ns'
            fc = s['up_max_log2fc'] if u else (s['down_max_log2fc'] if dn else None)
            row.append(f"{lab}{'' if fc is None else f' ({fc:+.1f})'} {u+dn}/{t}")
        w.writerow(row)
print("rows", len(d['results']), "experiments", len(exps))
