# Paper Figure 2 — the process, with Figure 1's safeguards on it (design)

## Intent
Figure 2 shows **how Figure 1's six safeguards are reflected in the Spock process**. Figure 1
says what the safeguards are; Figure 2 says where in the process each one acts. The worked
example (ntcA/urea) belongs to the next paper chapter, a walkthrough of a real analysis, so
Figure 2 stays general. Panel B shows what pre-registering fixes, as concepts.

## Goals / non-goals / anti-goals
- Goal: a flowchart a reader takes in at a glance, close to the current `fig2h` panel A, with
  the safeguards in front.
- Goal: accurate to the current skill (`references/plan-phase.md`, `references/step-protocol.md`).
- Non-goal: every step of the skill (five plan steps, two modes, gates). The caption carries
  what the drawing leaves out.
- Goal: speak Figure 1's visual language (icons, colours, titles).
- Anti-goal: busy. Rejected along the way: safeguard tracks under the flow, a safeguard band
  with pills plus dot labels (both "too complex / overwhelming"), and a story of one analysis
  (that is the next chapter).

## Approaches considered
1. Re-skin `fig2h` only (Fig 1 icons on today's badges): quick, but the safeguards stay small
   badges read through a legend.
2. Safeguard tracks / band under the flowchart: answers the goal directly, but too heavy.
3. **Chosen: one safeguard per AI step.** Each AI box takes the colour, icon and name of the
   Figure 1 card it mainly carries. Simple enough to read at a glance; the goal shows directly.

## The design (as agreed on the wireframe `fig2-flow-v4`)
Two lanes, Researcher (orange, = Fig 1's frame) on top and AI below; header bars
"1 · Plan the study" and "2 · Run it ×3: build the method, analyse, evaluate"; a black
"PLAN FROZEN" bar between them.

| Lane | Plan | Run |
|---|---|---|
| Researcher | Research question → … → approve? | Agree what this stage does → … → Explore the results together → approve? |
| AI | Show what the KG holds (**Look it up**) → Check the approach can work (**Scope first**) → Fix controls and decision rule (**Pre-register**) → Fresh AI reviews the plan (**Separate the roles**) | Coding AI runs it, returns files (**Check the computation**) → Main AI reads files, judges (**Claims match evidence**) → [explore] → Fresh AI re-checks claims (**Separate the roles**) |

Loops: "no: revise or redo" (approve → agree) and "results contradict the plan → plan
reopened, change recorded" (dotted, back across the frozen bar to the framing box).

## Same language as Figure 1 (agreed)
Figure 2 reuses Figure 1's visual vocabulary exactly: the six card colours, the six card icons
(`icon_cards`), the full card titles ("Look it up", "Scope first", "Pre-register the test",
"Check the computation", "Separate the roles", "Claims match evidence"), orange for the
researcher, Fig 1's fonts, tints and corner radii, and "on the record" as in Fig 1's frame.
No legend is needed beyond what Fig 1 already teaches.

## Panel B — what "Pre-register the test" fixes (agreed: keep; the concepts, not the example)
Panel B expands the **Pre-register the test** box of panel A, styled as that card (slate,
clipboard-lock icon, card title), linked visually to its box in A. It lists the seven things
a framing states (`references/plan-phase.md`, Framing): the skill's own headings, each with a
few **verbatim** words (checked like Fig 1's quotes), kept short:

- **Hypothesis** — "in prose"
- **Approach** — "how, and why"
- **Statistics plan** — "test(s) and thresholds"
- **Positive controls** — "must show the expected effect"
- **Negative controls** — "should not score"
- **Decision rule** — "every reading … named in advance"
- **Design comparability** — "what each arm is compared against"

Footer, verbatim: "controls pass → method frozen → targets scored once, last."

## My calls (check these)
- Figure 1 card 3 keeps "(Fig. 2B)".
- **"On the record"**: one small ring at each approve diamond, explained in a one-line note,
  matching Fig 1's "Everything is on the record".
- Same size rules as Figure 1 (170 mm wide, fonts >= 13 px in the SVG); `make_figures.py`
  function `figure2_safeguards()`, output `fig2_process_safeguards.svg/pdf/png`.
- `fig2h` moves to `drafts/`; its caption in `captions.md` is replaced. The caption mentions
  what the drawing omits: overview mode skips the framing; "check it can work" may send the
  approach back; a pattern found while exploring needs a prediction recorded first; code review
  at each stage's approval.

## Left to the builder
Exact box widths, wrapping and arrow routing; exact box wording within the meaning above.

## Changes after the first build (2026-11-22, agreed with the researcher)
- **Panel B display:** the plan as a locked sheet: a slate header with the card's icon and
  title, seven rows (heading + verbatim fragment), a "FROZEN" stamp, and the run order as three
  chevrons on the right (the skill's sentence split at its arrows). Content unchanged.
- **Plan steps are a dialog:** orange two-way arrows join the researcher lane to the first three
  plan steps, labelled "a dialog: the researcher confirms each step".
- **Figure 1 matches Figure 2A:** stage tags are PLAN / RUN (Fig 2A's phases), and cards 5 and 6
  are swapped to Fig 2A's order (Claims match evidence, then Separate the roles).
