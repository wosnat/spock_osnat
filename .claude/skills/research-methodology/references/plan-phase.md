# The Plan phase

The Plan is one grounded `superpowers:brainstorming` conversation, walked
through with the researcher in five steps. It ends with `proposal.md`, a
reviewed record of what was agreed, and an approval commit. This file owns
everything about the Plan; [step-protocol.md](step-protocol.md) owns the Run
phase and commits.

## Contents
1. [The five steps](#the-five-steps)
2. [Two modes](#two-modes)
3. [Looking at the data before the plan is set](#looking-at-the-data-before-the-plan-is-set)
4. [Framing (control-validated mode)](#framing-control-validated-mode)
5. [Just-in-time, and concrete](#just-in-time-and-concrete)
6. [How the dialog reads; decisions_log.md](#how-the-dialog-reads-decisions_logmd)
7. [Brainstorming overrides](#brainstorming-overrides)
8. [Closing the Plan](#closing-the-plan)

## The five steps

Each step is a short dialog, not a batch of questions, and ends with a
plain-language **"so far" summary** the researcher confirms. Each closed step
is recorded in `decisions_log.md` and `overview.html` and committed
(`<slug> plan: iteration — step N: …`). **Don't write `proposal.md` until all
five are agreed** — it records what was agreed and holds no surprises.
*(ntcA/urea: the researcher's first real question was a pop-up about a
threshold, for a plan they had not been shown.)*

1. **Clarify the question, and size it.** What the researcher wants to know;
   what the result is for (a standalone result, or part of a paper or a
   rewrite of one; whose hypothesis — theirs, possibly unpublished, or a
   published claim); and the **mode** (below), asked in plain words: *"Do you
   want an overview of what the KG holds on this, or a test of a specific
   expectation — where we first check the method on cases with a known answer,
   then look at yours?"* One question per message; the folder name is
   proposed as a default ("I'll call it `<slug>`; change it?"), not asked. If
   the question has several
   parts that each need their own answer, or many stresses, strains and
   papers to sort before anything can be scored, propose splitting it into
   smaller analyses, each with its own plan and result, done in order. A plan
   that keeps producing decisions without closing is the sign — raise the
   split again. *(General stress response: three parts in one plan, ~60
   decisions in a week, never closed.)*
2. **Show what the KG holds.** Run `list_publications`, `list_experiments`,
   `list_organisms` filtered to the question, and show experiments, designs,
   coverage and how each experiment's data look — as tables or plots, not
   descriptions. Surface structural surprises ("axenic RNA-seq is
   single-contrast, not a time course"). With many experiments to sort, offer
   a decision tree showing where each lands and keep it current. Log the facts
   in `decisions_log.md` before the choices they inform. Show per-time-point
   gene counts, not cumulative `gene_count`
   ([anti-hallucination.md 5.3](anti-hallucination.md#53-field-semantics-from-memory--cumulative-vs-per-timepoint-counts)).
3. **Agree the general approach**, in plain words.
4. **Check that the approach can work** — a throwaway test in `spike/` of what
   the data and annotations can actually tell apart: annotation depth and
   recall against a curated source, coverage of the candidate controls, a
   random sample of what lands in each group, distribution shape per
   experiment when platforms differ. **Required** when the method builds its
   own gene set or mixes platforms. It may send you back to step 3. *(N-import:
   inherited TCDB substrates and a "Medium" tier full of helicases surfaced
   only after the plan was locked; the module went through seven versions.)*
5. **Set the framing** — control-validated mode only (below). Offer a
   plain-language explainer for any statistic or method the researcher hasn't
   used.

If the researcher says "go fast", shorten the steps, but still show the
summary before writing anything.

## Two modes

Chosen in step 1.

- **Exploratory** — "show me what the KG has on X". Agree the scope and the
  deliverables (which overviews, which maps); no framing. Every result is
  exploratory. A pattern the results raise may be pursued when the
  researcher wants it (see [step-protocol.md — explore](step-protocol.md#explore)).
  Building persuasion for a mechanism the data did not raise is not done here;
  it becomes a suggested follow-up. *(Amino-acid pathways: an atlas drifted
  into "evidence visuals" for an unframed mechanism. hli light stress: an
  unplanned responder / quiet split became the best finding.)*
- **Control-validated** — "does X happen under Y?". The method must give the
  expected result on positive and negative controls before it touches the
  target. Run order: **controls pass → method frozen → targets scored once,
  last.** Thresholds and normalisation are tuned on controls and reference
  experiments, never on targets.

**A catalogue or classification** (transport systems, a candidate list, tiers,
classes) is control-validated, with the classifier as the method, even with no
hypothesis ("descriptive: the catalogue is the result"). Positive controls are
known members it must recover (curated genes, or a hand-built answer key for a
pilot strain); negative controls are what it must not include (a random sample
of each bin — helicases in a transporter tier). The decision rule is the tier
and class rules, fixed on the controls before the catalogue is built across all
strains. If the catalogue feeds a further question, split: the catalogue is its
own analysis. Its methods milestone is a **discovery milestone** — say so in
the proposal, and plan for many decisions at its decide gate and the four
verification layers in [research-notebook.md — Verifying the method](research-notebook.md#verifying-the-method).

Almost all KG data is published and already analysed, so Spock doesn't claim
confirmatory testing. Where a result needs confirming, the output is a
prediction for new experiments, or a test on KG data nobody has looked at
(another strain, paper or data type).

## Looking at the data before the plan is set

Look at anything; nothing is refused or debated. **One thing triggers a
question:** in control-validated mode, just before showing *the data that
answers the question* — the target genes' values in the target comparison for
an expression question; gene presence in the target strains for a genome
comparison. It depends on the question, not the data type. A reference the
question compares against — a known response used as the positive control, such
as N starvation for "do ntcA targets respond in coculture as under N
starvation?" — is control data and free; the target condition's values are the
answer. Ask, close to:

> "This will show the answer to our question. If we look now, before the plan
> is final, the result can no longer serve as a test of our prediction. It will
> be reported as exploratory. Look now, or wait until the plan is set?"

Everything else is free and needs no comment: what exists, coverage,
annotations, orthologs, neighbourhoods, distributions per experiment (compare
them across platforms — that difference must not be read as biology), and the
control genes. Check coverage with counts (`summary=True`), not values. Record
in `decisions_log.md` any experiment kept or dropped because of how the
controls looked. If the researcher chooses to look, record what was seen in
`decisions_log.md` without comment; it appears once, as a sentence in
`paper.md` Methods. Exploratory mode tracks nothing.

## Framing (control-validated mode)

A vague plan looks fine, gets approved, and falls apart in execution. Every
framing states, specifically:

- **Hypothesis** — in prose.
- **Approach** — how, and why it answers the question; concrete enough to poke
  holes in.
- **Statistics plan** — the specific test(s) and thresholds, *or* an explicit
  "no formal statistics, because descriptive", with the reason. Never implicit.
- **Positive controls** — named genes, pathways or experiments that must show
  the expected effect if the method works, each with its expected result and
  its coverage checked in step 4. A failed positive control makes the target
  result *uninterpretable*, not negative.
- **Negative controls** — a class that should *not* score if the signal is
  real, with its expected score stated, not assumed to be zero (growth genes
  move with growth rate; an alternative N source shares part of the N
  response). Without both kinds, a true null and a blind method look the same.
  A null is a valid outcome, written up as a bounded negative.
- **Decision rule** — every reading of the target named in advance (up / down /
  suggestive / not changed), each with its threshold.
- **Design comparability** — one row per experiment: its role; what each arm is
  compared against and that reference's physiological state (growth phase,
  nutrient status, sampling day); whether contrasts share samples or one fitted
  model (then they are not independent evidence); what it can and cannot
  confirm. Read `list_experiments(verbose=True)` `design_notes` first — they
  often record arm matching, the reference's state, sampling days and separate
  runs. Ask the researcher only for what the notes don't hold, say what they
  already state, and mark those cells researcher-supplied. *(Recurring hole: a
  comparable metric over incomparable designs — an FDR family size; a
  late-decline "early" reference; contrasts that were one fitted model. hli
  light stress: culture states were asked for and logged as KG gaps though
  `design_notes` held them.)*

The proposal also states what the result is for, whose hypothesis it is, and
its mode. An **exploratory** proposal is short: question, scope, deliverables.

## Just-in-time, and concrete

Two principles work together. *Just-in-time* governs **what** the plan commits
to: only what the data so far supports. *Concreteness* governs **how**: within
what it commits to, specific and reviewable. In practice:

- Ground every scope or framing choice in KG counts first; start with the
  simplest framing that fits.
- The Plan locks the question and framing, not sub-questions. Sub-narratives
  that form in the dialog ("protein persists while mRNA is gone") are for the
  Run phase to test.
- Name 1–3 predictions if confirmation bias is a real risk — not a matrix.
- Stability checks are added when a specific result triggers them; decisions
  are written when the data forces them ("we may decide X" is not a decision);
  caveats are harvested at evaluation, not pre-catalogued.
- The methods milestone is minimal — unless it builds the entity set (above).

If you find yourself listing things the analysis might need before the data
has arrived, stop.

## How the dialog reads; decisions_log.md

One topic per message, in plain words. Show data rather than describe it. Ask
open questions while exploring (steps 1–3); offer choices with a recommendation
when deciding (step 5). A choice the researcher answers by picking
"Recommended" without comment was probably not a real decision for them (see
also SKILL.md Rule 10, "Questions stand alone").

**`decisions_log.md`** is the researcher's record, in plain language — no tool,
field or file names in the decision text (a short `[KG]` tag on facts is fine).
One section per step, each with a numbered table: `#`, decision, decided by
(researcher / Claude proposed, researcher agreed / awaiting OK), reason. KG
facts the step relies on come before its table, tagged `[KG]`. Open questions
sit at the bottom until settled; caveats that emerge get their own section and
carry into `paper.md`. What the researcher chose to look at early is recorded
here without comment. Run-phase decisions go in the milestone's `notebook.md`;
established facts here are read before any Run-phase exploration.

## Brainstorming overrides

Brainstorming's pattern — clarifying questions one at a time, proposing
approaches, presenting the design in sections with a check-in after each — *is*
the five steps. Follow it; don't jump from a clarifying answer to writing
`proposal.md`. Three overrides, which take priority over brainstorming's own
defaults for research work in this repo:

1. **Where it's written:** the design doc is `analyses/<slug>/proposal.md`, not
   `docs/superpowers/specs/`; the dialog record is `decisions_log.md`.
2. **Grounded:** the dialog runs on live KG queries, shown as tables and plots.
3. **Terminal action:** begin the Run phase (methods milestone), not
   `superpowers:writing-plans` — `proposal.md` *is* the plan.

## Closing the Plan

After the five steps are agreed, in order:

1. **Write `proposal.md`** — nothing in it should be new to the researcher.
2. **Self-review** — does it match `decisions_log.md`? Is every framing item
   above actually stated (statistics decision made, controls with expected
   results, a decision rule covering every reading, a comparability row per
   experiment)? Fix vagueness, placeholders and contradictions inline.
3. **Critic** — dispatch `proposal-critic` via the `critical-review` skill
   (interpretation only; it never opens the data that answers the question).
4. **Bring the findings to the researcher** — each as *"the reviewer noticed X;
   I suggest Y, because Z"*, with the choice it opens. Never fix a finding
   silently and then ask about a detail of the fix. Resolve every Blocker.
5. **Delta critic pass** over whatever step 4 changed. Repeat 4–5 until the
   researcher approves with no further design change; expect several rounds —
   the close is a design review, not a sign-off. *(N-import: four approval
   prompts in a row were answered with design input.)*

Then populate `paper.md` Question and Background, and make the Plan approval
commit (contents in [step-protocol.md — Commits](step-protocol.md#commits)).
