"""Product-agreement matching and KEGG EC-name synonyms for product keywords.

Product-agreement rule (proposal section 3 step 2): a gene counts for a step only if its KG `product`
contains one of the step's keywords. Matching is case-insensitive substring on NORMALIZED text:
  * lower case;
  * runs of hyphens collapsed to one ("glutamate--ammonia ligase" == "glutamate---ammonia ligase");
  * the L- stereo prefix removed at the start of a word ("L-serine ammonia-lyase" == "serine ammonia-lyase");
  * whitespace collapsed.
(The pilots used plain lower-case substring matching; the normalization is new in this iteration.)

EC-name synonyms: each step's (and control's) EC numbers are looked up in KEGG ENZYME; the NAME and SYSNAME
lines are candidate synonyms. A candidate is added to the step's keywords only if it passes these filters,
applied in order (the first failing filter is recorded as the drop reason):
  1. KEGG marks it "(ambiguous)", "(misleading)", "(incorrect)" or "(obsolete)" (round or square brackets) -> dropped
  2. other parenthetical qualifiers are stripped ("(ADP-forming)")
  3. abbreviation: one token, <= 6 characters or >= 2 capitals ("GS", "TDO", "AlaDH")  -> dropped
  4. bare enzyme-class word ("aminotransferase", "amidase", ...), or no specific word left once class words,
     "protein"/"enzyme"/... and tokens < 3 characters are removed ("transaminase A", "P-protein")  -> dropped
  5. dedicated steps only (pass-2/3 rules): must name the substrate (one of the step's substrate stems) AND
     contain an enzyme word (a word ending in -ase)                                   -> else dropped
  6. equals a curated keyword of another catalogue step whose ECs are disjoint
     (e.g. "tryptophanase" listed under EC 1.13.11.11)                                -> dropped
  7. already a curated keyword (after normalization)                                  -> not added (no change)
"""
from __future__ import annotations

import re

ABANDON_MARKS = ("(ambiguous)", "(misleading)", "(incorrect)", "(obsolete)",
                 "[ambiguous]", "[misleading]", "[incorrect]", "[obsolete]")
NON_SPECIFIC = {"protein", "enzyme", "complex", "system", "subunit", "component", "chain", "family", "type"}
GENERIC_CLASS = {"aminotransferase", "transaminase", "amidase", "amidohydrolase", "deaminase", "decarboxylase",
                 "dehydrogenase", "oxidase", "ammonia-lyase", "lyase", "hydrolase", "synthetase", "synthase", "ligase",
                 "dioxygenase", "monooxygenase", "oxidoreductase", "transferase", "aldolase", "dehydratase",
                 "hydroxylase", "reductase", "isomerase", "mutase", "peptidase"}
ENZYME_WORD = re.compile(r"[a-z]ase\b")


def normalize(text) -> str:
    s = "" if text is None or (isinstance(text, float) and text != text) else str(text)
    s = s.lower()
    s = re.sub(r"-{2,}", "-", s)
    s = re.sub(r"(?<![a-z0-9])l-(?=[a-z0-9])", "", s)
    return re.sub(r"\s+", " ", s).strip()


def split_keywords(kws) -> list[str]:
    if kws is None or (isinstance(kws, float) and kws != kws):
        return []
    return [k for k in str(kws).split("|") if k]


def matched_keyword(product, kws) -> str:
    """First keyword (as written) whose normalized form is a substring of the normalized product; '' if none."""
    p = normalize(product)
    if not p:
        return ""
    for k in split_keywords(kws):
        if normalize(k) and normalize(k) in p:
            return k
    return ""


def agrees(product, kws) -> bool:
    return bool(matched_keyword(product, kws))


def split_names(field: str) -> list[str]:
    """Split a KEGG NAME field on ';' outside parentheses."""
    out, depth, cur = [], 0, ""
    for ch in str(field or ""):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == ";" and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return [x for x in out if x]


def filter_synonym(syn: str, *, dedicated: bool, stems: list[str], foreign: set[str], curated: set[str]):
    """Return (cleaned_synonym, '') if kept, else (syn, reason)."""
    low = syn.lower()
    for m in ABANDON_MARKS:
        if m in low:
            return syn, f"KEGG marks it {m}"
    s = re.sub(r"\s*(\([^)]*\)|\[[^\]]*\])", "", syn).strip()
    if " " not in s and (len(s) <= 6 or sum(c.isupper() for c in s) >= 2):
        return syn, "abbreviation"
    n = normalize(s)
    if n in GENERIC_CLASS:
        return syn, "bare enzyme-class word"
    if not [t for t in re.split(r"[^a-z0-9+]+", n) if len(t) >= 3 and t not in GENERIC_CLASS and t not in NON_SPECIFIC]:
        return syn, "no specific word (only class / generic words, e.g. 'transaminase A', 'P-protein')"
    if dedicated:
        if not any(normalize(st) in n for st in stems):
            return syn, "dedicated step: does not name the substrate"
        if not ENZYME_WORD.search(n):
            return syn, "dedicated step: no enzyme word"
    if n in foreign:
        return syn, "names another catalogue enzyme (curated keyword of a step with disjoint EC)"
    if n in curated:
        return syn, "already a curated keyword"
    return s, ""


def ec_synonyms(ecs: list[str], entries: dict, *, dedicated: bool, stems: list[str], foreign: set[str],
                curated: list[str]):
    """Synonyms from KEGG NAME + SYSNAME of each EC. Returns (added, dropped) where
    added = [(synonym, 'EC x NAME|SYSNAME')] and dropped = [(candidate, source, reason)]."""
    cur = {normalize(c) for c in curated}
    added, dropped, seen = [], [], set(cur)
    for ec in ecs:
        d = entries.get(ec)
        if not d:
            continue
        cands = [(x, f"EC {ec} NAME") for x in split_names(d.get("NAME", ""))]
        if d.get("SYSNAME"):
            cands.append((d["SYSNAME"].strip(), f"EC {ec} SYSNAME"))
        for c, src in cands:
            s, why = filter_synonym(c, dedicated=dedicated, stems=stems, foreign=foreign, curated=cur)
            if why:
                dropped.append((c, src, why))
            elif normalize(s) in seen:
                continue
            else:
                seen.add(normalize(s))
                added.append((s, src))
    return added, dropped
