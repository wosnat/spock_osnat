# Concepts Figure (new Figure 1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the new Figure 1 — six safeguard cards in a 3 × 2 grid inside a labelled frame — in two danger-line variants, render it, and retire fig1e to `drafts/`.

**Architecture:** One new function `figure1_cards(variant)` in `docs/paper graphics/make_figures.py`, driven by a `CARDS` data list, reusing the existing `SVG`, `icon()`, `tint()` and `wrap()` helpers. A small `check_quotes.py` verifies every card quote verbatim against the skill and agent files.

**Tech Stack:** Python (uv), hand-written SVG, headless Chrome via `render_figures.sh`.

**Spec:** `docs/superpowers/specs/2026-11-19-paper-concepts-figure-design.md`

## Global Constraints

- Canvas 960 units wide, printed 170 mm; every text ≥ `MIN_FONT` (13 units ≈ 6.5 pt) — enforced by `SVG.text`.
- Quotes verbatim from `.claude/` (whitespace-normalised); `[brackets]` mark an editorial insertion and are excluded from the match.
- Card titles must not wrap (one line at their size and card width).
- Stage order of cards: Look it up, Scope first, Pre-register the test, Check the computation, Separate the roles, Claims match evidence.
- Frame labels: "The researcher approves every step; the AI never moves on alone" (top-left), "Everything is on the record" (bottom-right); note "quotes: Spock's instructions to the AI".

## Review Focus

1. A quote that wraps to many lines and overflows its card — cards must size to the tallest card in their row.
2. A quote edited in the skill later — `check_quotes.py` must fail loudly, naming the card.
3. Curly quotes / apostrophes in quotes (‘All’, can't) — the check must normalise or match exactly what the source contains.
4. Bracketed insertions — the check must split on `[...]` and match each remaining part.
5. Variant B gloss lengthening the danger line past one line — must wrap inside the card, not overflow.

---

### Task 1: Card data and quote check

**Files:**
- Modify: `docs/paper graphics/make_figures.py` (add `CARDS` after `ICONS_1B`)
- Create: `docs/paper graphics/check_quotes.py`

**Interfaces:**
- Produces: `CARDS: list[dict]` with keys `stage, title, danger, gloss, quote, source, how, icon, color`; `check_quotes.py` exit code 0 when every quote is found, 1 otherwise, printing `OK|MISS <title>`.

- [ ] **Step 1:** Write `check_quotes.py`: import `CARDS` from `make_figures` (path-insert its folder), load every `.md` under `<repo>/.claude` except `evals/`, collapse whitespace, split each quote on `\[[^\]]*\]` and `…`, require every non-empty part to appear in the card's `source` file.
- [ ] **Step 2:** Run `uv run python -X utf8 "docs/paper graphics/check_quotes.py"` — expected: fails (`CARDS` not defined).
- [ ] **Step 3:** Add `CARDS` with the six rows exactly as in the spec tables (title, danger, gloss, quote, source path relative to `.claude/`, how line). Icons: database, bars, lock, check, new "roles" (three figures), scales. Colours: one per card from the palette, none red.
- [ ] **Step 4:** Rerun — expected: six `OK` lines, exit 0.
- [ ] **Step 5:** Commit `Paper graphics: card data and quote check for the new Figure 1`.

### Task 2: Draw the figure, both variants

**Files:**
- Modify: `docs/paper graphics/make_figures.py` (add `figure1_cards(variant: str) -> None`; call both in `__main__`; add icon kind `roles`)

**Interfaces:**
- Consumes: `CARDS`, `SVG`, `icon(s, kind, x, y, c)`, `wrap`, `tint`.
- Produces: `fig1_concepts_cards_a.svg` (danger line "against: guessing") and `fig1_concepts_cards_b.svg` (danger line with gloss) at the top of `docs/paper graphics/`.

- [ ] **Step 1:** Implement: orange rounded frame with the two labels and the quotes note; 3 × 2 cards; per card stage tag (13, bold, INK2) · title (bold, card colour; assert `len(wrap(title, inner_w, size)) == 1`) · danger line (RED_TXT, 13) · quote (14, italic, in “ ”) · how line (13, INK) · icon top-right. Row height = tallest card in the row; canvas height computed.
- [ ] **Step 2:** Run `uv run python "docs/paper graphics/make_figures.py"` — expected: writes both SVGs, no assertion errors.
- [ ] **Step 3:** Run `bash "docs/paper graphics/render_figures.sh"`, then view both PNGs; check nothing overflows or wraps a title. Restore any SVG whose only diff is marker order (`git restore`).
- [ ] **Step 4:** Commit `Paper graphics: new Figure 1 (safeguard cards), variants a and b`.

### Task 3: Retire fig1e; captions

**Files:**
- Move: `fig1e_concepts.{svg,pdf,png}` → `drafts/`; `figure1e()` saves to `drafts/`
- Modify: `docs/paper graphics/captions.md` (move the 1e caption to `drafts/captions.md`; add the new Figure 1 caption from the spec's "What each safeguard covers", naming quote sources)

- [ ] **Step 1:** `git mv` the three fig1e files; edit the save path; move the caption section.
- [ ] **Step 2:** Write the new caption (plain language, anti-hallucination as the umbrella).
- [ ] **Step 3:** Run `make_figures.py` and confirm nothing new appears at the top level except the two card variants; restore marker-order-only diffs.
- [ ] **Step 4:** Commit `Paper graphics: retire fig1e to drafts; caption for the new Figure 1`.

Then show both variants to the researcher to pick the danger line.
