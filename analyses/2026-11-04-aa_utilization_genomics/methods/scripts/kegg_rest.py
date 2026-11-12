"""KEGG REST helpers shared by 01_build_catalogue.py and 02_validate_kos.py.

Moved verbatim out of 02_validate_kos.py (kegg, chunks, parse_flat) so that 01 can read the KEGG ENZYME
NAME / SYSNAME lines for product-keyword synonyms through the same cached path. Raw responses are cached
under methods/data/kegg_cache/ so runs are reproducible offline.
"""
from __future__ import annotations

import re
import time
import urllib.request
from pathlib import Path

MDIR = Path(__file__).resolve().parents[1]
CACHE = MDIR / "data" / "kegg_cache"
BASE = "https://rest.kegg.jp"
EC_RE = re.compile(r"\d+\.\d+\.\d+\.\d+")


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
    """Split a KEGG flat-file multi-entry response into {FIELD: text} dicts (continuation lines joined by ' ')."""
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


def complete_ecs(ec_fields) -> list[str]:
    """Sorted set of complete EC numbers (a.b.c.d) from ';'-separated ec fields."""
    ecs = set()
    for e in ec_fields:
        for x in str(e).split(";"):
            if EC_RE.fullmatch(x.strip()):
                ecs.add(x.strip())
    return sorted(ecs)


def ec_entries(ecs: list[str]) -> list[dict]:
    """KEGG ENZYME entries for a sorted EC list, fetched in batches of 10 (same batching as 02 -> same cache files)."""
    out = []
    for ch in chunks(list(ecs)):
        out += parse_flat(kegg("get/" + "+".join("ec:" + e for e in ch)))
    return out


def ec_id(d: dict) -> str:
    ent = d.get("ENTRY", "").split()
    return ent[1] if len(ent) > 1 and ent[0] == "EC" else (ent[0] if ent else "")
