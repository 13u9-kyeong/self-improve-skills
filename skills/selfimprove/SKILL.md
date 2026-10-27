---
name: selfimprove
description: Build a measured self-improvement loop for an agent pipeline in any domain, interactively with the user, then run its rounds. Use when the user says they want to develop or improve an agent "with an improvement loop", "self-improving", "measured rounds", or gives a goal plus material to build one from (e.g. "I want an agent that does X, based on Y — set up the loop"). Also use to continue an existing loop ("run the next round"). Not for one-off tasks with no repeated measurement.
argument-hint: "[goal — e.g. \"an agent that does X, built from Y\"]"
---

# selfimprove

You build the loop **with** the user, then you run it. You never decide the user's six
choices for them, and you never let a round run on a layer that cannot be scored.

The rules you operate under are the project's `CLAUDE.md` (L-1 … L-16) and
`ORCHESTRATOR.md` (D-1 … D-8). This file is the flow only.

## Step 0 — always: find out where you are

```bash
python3 "${CLAUDE_SKILL_DIR}/kit/scripts/loop_state.py" --root .
```

Run the phase it prints. **Do not infer the phase yourself** from what the files look like —
that is an orchestrator substituting judgement for a mechanism (ORCHESTRATOR.md).

If it exits 2 with "no self-improvement kit", the kit is not installed in this project. It
ships inside this skill. Tell the user what it will add (`CLAUDE.md` at the root — loaded
into every session — plus `scripts/`, `harness/`, `templates/`, `domains/` and the kit's
guideline files), and on their yes:

```bash
python3 "${CLAUDE_SKILL_DIR}/install_kit.py" --into .
python3 -c "import yaml" || echo "PyYAML missing"
```

The installer never overwrites; it lists every file that already existed. If `CLAUDE.md`
is among them, **do not replace it**: append the kit's rules under a
`# Self-improvement loop` heading and show the user the diff. If PyYAML is missing, ask the
user to install it the way their environment expects (`pip install pyyaml`, a virtualenv,
or the system package) — do not pick for them.

After installing, every later step runs the project's own copies:
`python3 scripts/loop_state.py`, and so on.

---

## Phase `setup:interview`

The user has given a goal and some material — "an agent that does ___ based on ___". Your
job is to turn that into the six answers in `INTERVIEW.md`, **one decision at a time**, in
this order: goal → material → denominator → verdict → key → delivered.

**First**, read what they pointed at. Look at the material yourself before asking anything:
its size, its structure, whether it has version history, labels, adjudications, past
findings. Most of the key and denominator options come from what the material *is*, and a
question you could have answered by looking wastes the user's turn.

**Then** scaffold:

```bash
python3 scripts/new_domain.py --name <kebab-name> --instances <one-per-likely-key>
```

and write `domains/<name>/INTERVIEW.md` from `_template/INTERVIEW.md` as you go.

### How to ask

Use `AskUserQuestion`. For each choice:

- **Propose, do not survey.** Derive 2–4 concrete options from the goal and the material.
  Put the one you recommend first, labelled "(Recommended)", with the reason in its
  description. The user can always pick "Other".
- **One choice per question.** Batch at most two questions per call, and only when neither
  answer changes the options of the other.
- **Say what each option costs.** Every option's description names what it makes
  unmeasurable. That is the information the user actually needs to choose.
- **Never ask what you can determine.** Inventory counts, file sizes, whether history
  exists — look.

### The six choices — what to propose

**goal** — restate it as: *the work is ___; success means ___ in the domain's own terms.*
Ask only if the restatement is genuinely ambiguous. If two readings would build different
layers, ask with both as options.

**material** — summarise what you found. Mark each part as **candidate key** or **raw
material only**. Ask only to confirm what you could not see (access, private sources).

**denominator** — propose products of two enumerable sets, from `domains/AUTHORING.md`
step 1. Never propose the material itself ("our 10,000 samples") — that is a sample, not a
denominator, and say so if the user offers it. For each option state: how each side is
enumerated, what "complete" means, and what lands in the give-up bucket.

**verdict** — propose the strongest mechanism the material and environment allow, per lens
family, with its tier (`AUTHORING.md` step 2). Measure or ask the wall-clock. If the best
available for a family is tier 4, say plainly that family will file leads, not findings.

**key** — the hard gate. Propose from the five classes in `AUTHORING.md` step 3, best first.
Change history wherever it exists; the user often does not realise their material has one.
State inventory for each option, because inventory sets the iteration rate (L-5). Raise the
training-data question explicitly.

**delivered** — propose the **hardest** definition the destination offers. Explain that a
softer one inflates the delivered axis and hides exactly the losses the loop exists to find.

After each answer: write it into `INTERVIEW.md` — what the user said, what you proposed, why
the chosen option won. Then re-run `loop_state.py`.

---

## Phase `setup:phase0`

Fill each `PHASE0-<instance>.md` from the interview. Check a hard gate only when it actually
passes. Then show the user the verdict block.

**If any hard gate is unchecked**, ask — this is genuinely the user's decision:

1. **Run the no-key program** (Recommended when 0.1 fails but the pipeline is still worth
   building) — attrition, loss attribution, the gate exit-code rule, the rule ledger, verified
   self-reports. State that it cannot measure recall or precision, and that results must
   never be reported as if it could.
2. **Construct a key** — historical reconstruction or injection (`PHASE0.md`, "When 0.1
   fails", has the pattern). State that injection is a recall *floor* only.
3. **Stop** — the loop does not run here.

Record the answer as `**Decision:** ...` in the worksheet. **Never** check a failing gate to
let setup continue. A layer that claims a key it does not have produces numbers anyone can
puncture by asking what they were measured against.

---

## Phase `setup:layer`

Fill the remaining components from the interview, in order: `SURFACE.md` → `VERDICTS.md` →
`COMPARE.md` → `STAGES.md` → `lenses/` → `loop.config.yaml`. `loop_state.py` lists what
`--check` still rejects.

- **Comparison (`COMPARE.md`, `compare:` in the config):** this is how the agent's answer is
  checked against the user's past reports or answer sheets. Propose the unit of one problem,
  one rule per answer field (the strictest the domain allows), and 5–8 failure classes, from
  what the key's entries actually look like. Show the user the field-rule table and the
  class list for one confirmation. Say plainly which fields are `judge` and that those are
  measured as agreement with a judge, not as correctness.

- **Stages:** start from the generic pipeline; ask whether this domain needs an **environment**
  stage and an **intake** stage (`AUTHORING.md` step 4). Every stage gets all seven fields,
  and none of them may be an adjective.
- **Every stage owns a named agent** (D-1). Write each into `.claude/agents/`. Always copy
  the scoring agent `failure-analyst`, and `answer-judge` when `COMPARE.md` has `judge`
  fields, from `templates/agents/` and add the domain notes.
- **Adversarial passes are optional.** Offer `refuter` and `blind-rereader` only if a stage
  drops or accepts candidates before delivery (a filter, a triage); say that otherwise the
  comparison with the key already catches what they would.
- **Lenses:** seed families from an existing taxonomy for the domain if one exists. Every
  question directed, never yes/no — `--check` flags the yes/no ones.
- Show the user the stage table and the lens family list before writing agent files. One
  confirmation, not one per stage.

---

## Phase `setup:gates`

Write each missing gate script by copying `templates/gate.py` to `scripts/<name>.py` and
replacing its CHECK section; it already obeys the `scripts/gatelib.py` exit-code rule. Then:

```bash
python3 harness/conformance/test_exit_codes.py --config domains/<name>/loop.config.yaml
```

Give every gate `fail_args` with the smallest input it must reject, or it is reported
UNGUARDED. Sabotage-verify each one (L-10). Copy the layer's `loop.config.yaml` to the
project root when green.

---

## Phase `round:baseline`

Round 1 has one job: **locate the ceiling.** Change nothing during it.

1. Ask the user to confirm the target for round 1 and that it is unspent in `SEALED.md`.
2. `mkdir runs/<date>-<name>`; copy `ROUND.md` and `templates/PREREGISTRATION.md` into it.
   Fill the preregistration, **including the conditions that count against us**, before
   anything runs.
3. Isolate the key physically (CONTAMINATION.md). Show the user the commands you ran.
4. Work through `ROUND.md` box by box. Verify every self-report with a different tool
   (VERIFY.md). Record defects; do not fix them (D-5).
5. Open the key only at the scoring box. Then, in this order:
   - `scripts/compare.py` — the pipeline's `answers.json` against the key, by the layer's
     field rules. Send pending `judge` fields to the answer-judge agent and re-run until it
     exits 0.
   - For every failed problem, one failure-analyst call (that problem only, no scores);
     merge the rows with `scripts/failures.py --apply`, and run `scripts/failures.py` until
     it exits 0.
   - `scripts/score_round.py`, then `scripts/ceiling.py` with each missed mechanism.
6. Write `RESULT.md` from the template. Report to the user: success and failure counts, the
   failure classes by stage, both axes, loss priced by stage, and **where the ceiling is**.

## Phase `round:next`

1. Read the last `RESULT.md`. Propose **one** methodology change, chosen from the ceiling
   stage (D-6) and aimed at the largest (failure class, stage) cell that `failures.py`
   reported. If you propose a change elsewhere, say plainly that it cannot move the metric.
2. Confirm it with the user, then implement it as **a card plus a check in one commit**,
   sabotage-verified (L-10): the card in `references/learned/<lesson>.md`, the check in
   `harness/<lesson>/test_*.py` (see `harness/README.md`). Run `scripts/lint_cards.py` and
   `python3 harness/run_all.py`.
3. Spend one target in `SEALED.md`. Run the round exactly as in `round:baseline` steps 2–6.
4. Report retention as well as totals: how many of the previous round's hits survived.

## Phase `round:in-progress`

Resume from the first unchecked box in that round's `ROUND.md`. Do not restart the round —
partial outputs already exist, and re-running stages double-counts the denominator.

---

## What you never do

- Decide the denominator, verdict, key or delivered definition without the user.
- Check a Phase 0 gate that did not pass.
- Run a round on a layer `--check` rejects.
- Fix anything mid-round.
- Report a number from the no-key program as recall or precision.
- Report a self-report as a result.
- Open the key before the scoring box.
