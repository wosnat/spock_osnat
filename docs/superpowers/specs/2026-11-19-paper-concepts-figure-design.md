# Paper figure: Spock concepts for unbiased, valid research — concept list

Short design (concept content only; the figure's visual design comes next).

## Intent

A paper figure showing the Spock concepts that drive unbiased and valid
AI-assisted research. Conceptual plus example, not low level: each concept is a
two-word idea with one short concrete story. Detail (code review mechanics,
delta reviews, multiple-testing specifics) goes to the caption or paper text.
The existing figures (1e, 2h, 3) are drafts and may be scrapped.

## The concepts — danger → safeguard, ordered by research stage

| # | Stage | Danger | Safeguard | Example |
|---|---|---|---|---|
| 1 | Plan | Guessing | Look it up, don't guess — values, gene identity (locus tags), tool and field meanings, absence; gaps flagged, not filled | hli: a protein response was called "missed", though the KG holds no protein measurements for those genes |
| 2 | Plan | A test that can't fail — without controls, "no effect" can't be told from a method that couldn't see one; criteria chosen after the result let any outcome pass | Pre-register the test — genes that must respond, genes that must not, and the reading of every outcome, fixed before the answer is seen; the plan reviewer can't open results; anything outside the plan is labelled exploratory (an unplanned pattern is tested only via a prediction logged first, on data not used to find it); no confirmatory claim on already-published data | urea plan: urea-use genes must switch on, growth genes must stay flat, named in advance (details → Fig. 2B). hli (unplanned pattern labelled exploratory, its test predicted first) → caption or row 6 |
| 3 | Build the method | Silent method errors | Prove the method on known answers — toy tests, one real case against an answer built another way by someone other than the author, fresh code review | a bug passed all 27 toy tests (the text "False" read as true); on real data it would have collapsed every class |
| 4 | Build the method | Statistical errors | Statistics done right — the pre-registered test (row 2) computed correctly: in scripts with the package's pipeline, correct background, multiple-testing correction, no effect-size comparison across platforms | illustrative (no recorded incident): enrichment against the whole genome instead of the genes the experiment measured |
| 5 | Analyse | Grading your own work | Separate doing, judging and reviewing — the coding AI returns files, not conclusions; the main AI judges from the files; a reviewer with no prior context re-checks every claim | a heatmap narrated "all 5 up" while the data file showed them down |
| 6 | Write up | Narrative fabrication | Claims no bigger than the evidence — numbers before interpretation; "therefore / all / independent" each need a contrast, file and number; each finding set against the other KG studies | hli: "independent" support that re-read the same arrays; "explains" for a partial split |

**The framing** (hypothesis, approach, statistics plan, positive and negative
controls, decision rule, fair comparison) appears here as a concept
(row 2, pre-registration); its details are shown in Figure 2 panel B (the
process figure), on the urea example. Row 2 points to it ("see Fig. 2B").

**Frame (not rows):** the researcher approves every step and can lift any rule;
everything is on the record (computation in scripts, every version kept, never
overwritten).

**Title / caption:** the figure as a whole is Spock's answer to hallucination —
anti-hallucination is the umbrella, not a row.

## Approaches considered

- **Examples:** several analyses (chosen, for now) vs one running example
  threaded through all six (may revisit — reads as one story, but not every
  danger has an incident in one study).
- **Order:** by research stage (chosen — reads as a story, links to the
  process figure, puts fabrication-at-start and over-selling-at-end at the two
  ends) vs by importance vs by actor.
- **Framing:** own row ("a result you can't interpret → controls and a decision
  rule") vs folded into row 2 as **pre-registration** (chosen — one concept
  readers already know, covering both what is fixed and when; six rows). The
  framing's details are shown in Figure 2 panel B.
- **Rows 3 and 4:** kept separate (borderline overlap — both ask "is the
  computation correct?"; row 3's code review also checks backgrounds). Row 4
  keeps statistics visible for readers who look for it. Revisit — merge into
  "wrong computation → check method and statistics on known answers" — if the
  figure feels crowded.
- **Merges agreed:** "fix the test first" + "honest labels" → row 2;
  anti-hallucination spread across rows 1, 5, 6 and the frame; "don't guess" is
  row 1; statistics promoted to its own row.

## Left to the figure design

Layout, whether rows carry a verbatim skill quote, icons/colours, and how the
frame is drawn. Examples must stay traceable to the skill's incident notes or
the analyses' records.
