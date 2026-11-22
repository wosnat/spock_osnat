# Paper Figure 2 (process + safeguards) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `fig2h` with `fig2_process_safeguards`: panel A = the Plan → Run flowchart whose AI steps wear Figure 1's safeguard cards; panel B = what "Pre-register the test" fixes, as the skill's framing headings with short verbatim fragments.

**Architecture:** One new function `figure2_safeguards()` in `docs/paper graphics/make_figures.py`, drawing with the existing `SVG` helper and reusing Figure 1's `CARDS` (colour, icon, title) and `icon_cards()`. Panel B's text lives in a new `FRAMING` constant that `check_quotes.py` verifies against the skill, like the Fig 1 quotes. Rendering via the existing `render_figures.sh`.

**Tech Stack:** Python (stdlib only) writing SVG; headless Chrome → PDF/PNG.

**Spec:** `docs/superpowers/specs/2026-11-22-paper-process-figure-design.md`

## Global Constraints

- Canvas 960 units wide (prints at 170 mm); every font ≥ `MIN_FONT` (13); `SVG.text` already asserts this.
- Same language as Figure 1: colours, icons and titles come **from `CARDS`** (look up by title), never re-typed; researcher = `ORANGE`; Fig 1 fonts/tints/radii.
- Panel A AI boxes, in order, and the card each carries:
  Plan: "Show what the KG holds" → Look it up; "Check the approach can work" → Scope first; "Fix controls and decision rule" → Pre-register the test; "Fresh AI reviews the plan" → Separate the roles.
  Run: "Coding AI runs it, returns files" → Check the computation; "Main AI reads files, judges" → Claims match evidence; "Fresh AI re-checks claims" → Separate the roles.
- Panel A researcher boxes: "Research question"; approve? (plan); "Agree what this stage does"; "Explore the results together"; approve? (run). Headers "1 · Plan the study" and "2 · Run it ×3: build the method, analyse, evaluate"; black "PLAN FROZEN" bar.
- Loops: dashed "no: revise or redo" (run approve → agree); dotted "results contradict the plan → plan reopened, change recorded" (main-AI box → back across the bar to the Pre-register box).
- "On the record": one small ring at each approve diamond + a one-line note. **Ring colour = `ORANGE`** (fig2h used `OCHRE`, which is now the Claims-match-evidence colour).
- Panel B, verbatim fragments (source `skills/research-methodology/references/plan-phase.md`):
  Hypothesis "in prose"; Approach "how, and why"; Statistics plan "test(s) and thresholds"; Positive controls "must show the expected effect"; Negative controls "should not score"; Decision rule "every reading … named in advance"; Design comparability "what each arm is compared against". Footer: "controls pass → method frozen → targets scored once, last."
- Panel B styled as the Pre-register card (its colour, `clipboard_lock` icon, title "Pre-register the test") and visibly linked to its panel-A box.
- Output `fig2_process_safeguards.svg` (+ pdf/png from the render script); `fig2h` saves to `drafts/`.

## Review Focus

1. Text overflowing a box or a box title wrapping to 2+ lines → each box asserts its wrapped lines fit (Task 2, Step 3).
2. Safeguard title drifting from Fig 1 (typo, short form) → titles read from `CARDS` by key; a missing key raises (Task 2).
3. Skill text changes and a panel-B fragment stops being verbatim → `check_quotes.py` reports `MISS` for `FRAMING` (Task 1).
4. A colour meaning two things (ochre ring vs Claims card) → rings `ORANGE` (Task 2, Step 4 visual check).
5. Fig 1 card 3 "(Fig. 2B)" and captions pointing at the wrong panel → caption check in Task 3.

---

### Task 1: Panel B text, checked against the skill

**Files:**
- Modify: `docs/paper graphics/make_figures.py` (new `FRAMING`, `FRAMING_FOOTER`, `FRAMING_SOURCE` after `CARDS`)
- Modify: `docs/paper graphics/check_quotes.py` (`main()`)

**Interfaces:**
- Produces: `FRAMING: list[tuple[str, str]]` — (heading, verbatim fragment), 7 items in the order of the Global Constraints; `FRAMING_FOOTER: str`; `FRAMING_SOURCE = "skills/research-methodology/references/plan-phase.md"`.

- [ ] **Step 1: Extend the check first.** In `check_quotes.py`, import `FRAMING, FRAMING_FOOTER, FRAMING_SOURCE` and, after the CARDS loop, check each fragment and the footer with `in_order(parts(frag), texts[FRAMING_SOURCE])`, printing `OK   B: <heading>` / `MISS B: <heading>: …` and counting misses into `bad`. Each fragment is checked on its own (not in order with the others).
- [ ] **Step 2: Run, expect failure.** `uv run python -X utf8 "docs/paper graphics/check_quotes.py"` → `ImportError: cannot import name 'FRAMING'`.
- [ ] **Step 3: Add the constants** with the exact strings from Global Constraints (use the real "…" and "→" characters).
- [ ] **Step 4: Run, expect pass.** Same command → 6 `OK` card lines + 8 `OK   B:` lines, exit 0. If a fragment fails only because of `*emphasis*`/line breaks, that's already normalised; any other MISS means the fragment is wrong — fix the fragment, not the checker.
- [ ] **Step 5: Commit** `Paper graphics: Figure 2 panel B text, checked against the skill`.

### Task 2: Draw `figure2_safeguards()`

**Files:**
- Modify: `docs/paper graphics/make_figures.py` (new function after `figure2h`; `__main__` calls it; `figure2h` saves to `drafts/fig2h_process_framing.svg`)

**Interfaces:**
- Consumes: `CARDS`, `icon_cards(s, kind, x, y, c)`, `tint`, `wrap`, `SVG`, `FRAMING*` (Task 1).
- Produces: `figure2_safeguards() -> None`, writes `fig2_process_safeguards.svg`; helper `card(title: str) -> dict` returning the `CARDS` entry with that title (raises `KeyError` otherwise).

- [ ] **Step 1: Layout from the wireframe** `.superpowers/brainstorm/644-1795339596/content/fig2-flow-v4.html` (lanes: researcher on top, AI below, frozen bar between Plan and Run). Panel A label "A", panel B label "B" as in fig2h. Height is free; aim ≤ 620 units total (≈110 mm).
- [ ] **Step 2: AI boxes** carry: the step text (13–14, `INK`), the card's icon via `icon_cards` (scaled as in Fig 1, smaller is fine), and the card title in bold in the card colour; box fill `tint(c, 0.06)`, stroke `c` — same treatment as a Fig 1 card. Researcher boxes and diamonds: `ORANGE` / `tint(ORANGE, 0.14)` as Fig 1's pills.
- [ ] **Step 3: Fit asserts.** For every box: `assert len(wrap(title, inner_w, size)) == 1` for the card title, and the wrapped step text fits the box height (same pattern as `figure1_cards`).
- [ ] **Step 4: Panel B** below A: a card-styled block (Pre-register colour, thick left edge like Fig 1 cards, `clipboard_lock` icon, title "Pre-register the test", subtitle "what the plan fixes before the result is seen"); the 7 items in two or three columns as **bold heading** + italic “fragment”; footer line italic “controls pass → method frozen → targets scored once, last.” A thin connector (or matching colour tab) from the Pre-register box in A to panel B.
- [ ] **Step 5: Generate and render.** `uv run python "docs/paper graphics/make_figures.py"` (no AssertionError) then `bash "docs/paper graphics/render_figures.sh"` → prints `rendered fig2_process_safeguards: 170 x … mm`.
- [ ] **Step 6: Look at the PNG** next to `fig1_concepts_cards.png`: same colours/icons/titles; no overlaps or clipped text; arrows land on boxes; rings orange. Fix and re-render until clean.
- [ ] **Step 7: Commit** `Paper graphics: new Figure 2 — process with Figure 1's safeguards; framing panel` (include svg/pdf/png and the drafts move: `git mv` fig2h pdf/png into `drafts/`, delete the stale top-level fig2h svg).

### Task 3: Captions and docstring

**Files:**
- Modify: `docs/paper graphics/captions.md` (replace the "Figure 2h" section with "Figure 2 — fig2_process_safeguards"; move the old text to `drafts/captions.md`)
- Modify: `docs/paper graphics/make_figures.py` module docstring (Fig 2 line)

- [ ] **Step 1: Write the caption.** Panel A: what each lane and box is, that each AI step carries a Figure 1 safeguard (named), the loops, the rings; plus what the drawing omits: overview mode skips the framing; "check it can work" may send the approach back; a pattern found while exploring needs a prediction recorded first; code review before each stage's approval. Panel B: the seven items the plan fixes, quoted from `references/plan-phase.md`, and the run order. Plain language, matching Fig 1's caption style.
- [ ] **Step 2: Cross-reference check.** `grep -n "Fig. 2\|Figure 2" "docs/paper graphics/captions.md" "docs/paper graphics/make_figures.py"` — Fig 1's "(Fig. 2B)" and "(Figure 2A)/(Figure 2B)" now point at panels that exist with that content.
- [ ] **Step 3: Re-run** `check_quotes.py` (all OK) and commit `Paper graphics: Figure 2 caption`.
