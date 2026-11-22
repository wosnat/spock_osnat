# Paper figure: Spock concepts for unbiased, valid research

Short design: concept list and visual design for the new Figure 1. It replaces
the draft fig1e (the other drafts are in `docs/paper graphics/drafts/`).

## Intent

A paper figure showing the Spock concepts that drive unbiased and valid
AI-assisted research. Conceptual, not low level: each concept is a short
safeguard name, the danger it counters, and one verbatim quote from Spock's
instructions to the AI. Detail (code review mechanics, delta reviews,
multiple-testing specifics, worked incidents) goes to the caption or paper text.

## The six cards — ordered by research stage

| # | Stage | Card title (safeguard) | against: (danger) | Quote (verbatim; source) | Icon |
|---|---|---|---|---|---|
| 1 | Plan | Look it up | guessing | "Every claim traces to a KG query. Never take data from memory." (SKILL.md Rule 1) | database + magnifier |
| 2 | Plan | Scope first | the plan outruns the data | "… a throwaway test … of what the data and annotations can actually tell apart." (plan-phase.md, step 4) | bars |
| 3 | Plan | Pre-register the test | a test that can't fail | "Without both [positive and negative controls], a true null and a blind method look the same." (plan-phase.md, Framing) | clipboard + lock |
| 4 | Build | Check the computation | silent errors | "Toy tests catch logic errors; only an independent path catches wrong calls, defaults, filters and paging." (research-notebook.md, Verifying the method) | flask + check |
| 5 | Analyse | Separate the roles | grading your own work | "You execute; the main thread judges. You return artifacts, not conclusions." (agents/kg-coder.md) | three figures |
| 6 | Write up | Claims match evidence | narrative fabrication | "[Words like] 'every', 'none' … need a query against the data file, not a glance at a heatmap." (SKILL.md Rule 9) | balance |

Card 2 is the danger researchers feel most with Claude: it runs ahead of the
data. It and card 3 sit side by side — both slow the AI down before anything is
scored.

What each safeguard covers (for the caption):
1. Values, gene identity (locus tags), tool and field meanings, absence — from a
   KG query; gaps flagged, not filled.
2. Before any criteria are set, a quick test of what the data, annotations and
   candidate controls can actually tell apart; it may send the approach back.
   Big questions are split into smaller analyses.
3. Genes that must respond, genes that must not, and the reading of every
   outcome, fixed before the answer is seen; the plan reviewer can't open
   results; anything outside the plan is exploratory (an unplanned pattern is
   tested only via a prediction logged first, on data not used to find it); no
   confirmatory claim on already-published data. Details: Figure 2 panel B.
4. The method: toy tests in the real file format; one real case against an
   answer built another way, by someone other than the author; fresh code
   review. The statistics: in scripts, with the package's pipeline, correct
   background, multiple-testing correction, no effect-size comparison across
   platforms.
5. The coding AI returns files, not conclusions; the main AI judges from the
   files; a reviewer with no prior context re-checks every claim.
6. Numbers before interpretation; "therefore / all / independent" each need a
   contrast, file and number; each finding set against the other KG studies.

**How line** (plain language, one line under each quote — what Spock does, not
what the AI is told):
1. Each finding is tagged: from the KG, interpretation, or a gap.
2. Data, annotations and controls are checked before the criteria are set.
3. Controls and decision rule fixed before the answer is seen (Fig. 2B).
4. Toy data, an independent answer and a code review; correct background and
   multiple-testing correction.
5. One AI runs the code, another judges the output, a third, new to the work,
   reviews.
6. Numbers first, interpretation after; each finding set against other KG
   studies.

**Danger line — to try both and pick by eye:** terse ("against: guessing") vs
with a gloss ("against: guessing — facts recalled, not looked up"). Glosses:
1 facts recalled, not looked up · 2 criteria set for data that can't deliver
them · 3 any outcome can pass · 4 tests pass, real data breaks it · 5 the
author misses their own holes · 6 the wording outruns the evidence.

## Visual design (layout C, style 1)

- A 3 × 2 grid of cards, read left to right, top to bottom in stage order.
- Each card: stage tag (small caps) · safeguard title (bold, one line — sized
  so no title wraps) · "against: <danger>" (red, small) · the quote (roman,
  in quotation marks; [brackets] mark an editorial insertion) · one line icon
  in the top-right corner, in the safeguard colour.
- The frame is drawn literally: an orange rounded border around the grid,
  labelled "The researcher approves every step; the AI never moves on alone"
  (top-left) and "Everything is on the record" (bottom-right).
- A small note "quotes: Spock's instructions to the AI" on the frame, so the
  reader knows what the quotes are.
- Icons and colours: builder's choice, reusing `icon()` from make_figures.py
  where it fits (Figure 2 will be redone to match this figure, not the reverse).
- Built in `docs/paper graphics/make_figures.py` like the other figures: 170 mm
  wide, text ≥ 6.5 pt, SVG + PDF + PNG. Mockup:
  `docs/paper graphics/drafts/fig1_cards_mockup.html` (HTML wireframe; predates the scope-first / check-the-computation merge).

**Title / caption:** the figure as a whole is Spock's answer to hallucination
and bias — anti-hallucination is the umbrella, not a card. The caption names
the quote sources (the skill, the agent definitions).

## Approaches considered

- **Layout:** A table danger → safeguard (most room, tall) · B six columns
  along the research path (short, aligns with Fig. 2) · **C six cards inside
  the frame (chosen** — safeguards lead, the frame is a real frame).
- **Illustration:** **1 one icon per safeguard (chosen)** · 2 small drawings of
  each incident (dropped with the examples) · 3 warning icon + safeguard icon.
- **Card content:** examples from real incidents vs **verbatim quotes
  (chosen)**, plus a plain how line (adopted from the fig1/fig1e drafts);
  incidents may go to the caption.
- **Order:** by research stage (chosen) vs by importance vs by actor.
- **Framing:** own card vs folded into card 2 as **pre-registration**
  (chosen); its details are shown in Figure 2 panel B.
- **Scope first:** folded into card 3's how line vs **its own card (chosen** —
  "the AI runs ahead of the data" is what researchers feel most with Claude).
  To keep six cards, method and statistics merged into **Check the
  computation** (their overlap was borderline).
- **Merges agreed:** "fix the test first" + "honest labels" → card 2;
  anti-hallucination spread across cards 1, 5, 6 and the frame; statistics its
  own card, later merged with method checks (see above).

## Left to the builder

Exact colours per safeguard (one colour each, from the existing palette), card
and font sizes, icon drawing details, caption wording.

## Researcher decisions after the first render (2026-11-19)

- Danger line: terse (variant a); the gloss variant is not rendered.
- Quotes in italic (overrides "roman" above); stage tag lighter (regular weight, letter-spaced,
  grey; 13 units is the font floor, so it cannot be smaller); icons enlarged ×1.45.
- Card text stays as in the tables above: a trial with shortened quotes and lines read as
  fragmented and lost the points, and was reverted.

## Update 2026-11-22: aligned with the new Figure 2
Stage tags are now the phases of Figure 2A: PLAN (cards 1–3) and RUN (cards 4–6), and the last
two cards are swapped (Claims match evidence, then Separate the roles), so the cards read in the
same order as the AI steps in Figure 2A. See `2026-11-22-paper-process-figure-design.md`.
