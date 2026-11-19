"""Verify every Figure 1 card quote verbatim against Spock's instructions in .claude/.

Whitespace is collapsed, markdown emphasis (* and `) is dropped, and quote marks are
normalised (‘’“” and ' all count as "). A quote is split on [editorial insertions] and
on "…"; each remaining part must appear in the card's source file. A sentence-final
period on the last part is ignored (the quote may stop mid-sentence in the source).

Run:  uv run python -X utf8 "docs/paper graphics/check_quotes.py"
Exit 0 when every quote is found; 1 otherwise. Prints OK|MISS <title> per card.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAUDE = HERE.parents[1] / ".claude"
sys.path.insert(0, str(HERE))

from make_figures import CARDS  # noqa: E402

QUOTE_MARKS = str.maketrans({"‘": '"', "’": '"', "“": '"', "”": '"', "'": '"'})


def norm(s):
    s = re.sub(r"[*`]", "", s).translate(QUOTE_MARKS)
    return re.sub(r"\s+", " ", s).strip()


def parts(quote):
    out = [norm(p) for p in re.split(r"\[[^\]]*\]|…", quote)]
    out = [p for p in out if p]
    if out and out[-1].endswith("."):
        out[-1] = out[-1][:-1]
    return out


def main():
    texts = {p.relative_to(CLAUDE).as_posix(): norm(p.read_text(encoding="utf-8"))
             for p in CLAUDE.rglob("*.md") if "evals" not in p.relative_to(CLAUDE).parts}
    bad = 0
    for card in CARDS:
        src = texts.get(card["source"])
        missing = ["<source file not found>"] if src is None else \
            [p for p in parts(card["quote"]) if p not in src]
        if missing:
            bad += 1
            print(f"MISS {card['title']}  ({card['source']}): " + " | ".join(missing))
        else:
            print(f"OK   {card['title']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
