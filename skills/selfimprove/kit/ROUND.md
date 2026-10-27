# Round runbook

> Copy this file into `runs/<date>-<name>/ROUND.md` and check boxes as you go. One copy per
> round. The boxes are the record — an unchecked box at the end is a stage that did not run,
> and that is reportable (D-8).
>
> `PLAN.md` Phase 3 explains why each step exists. This is the executable form.

---

## Before — setup

- [ ] **Inventory checked.** `SEALED.md` has an unspent target. Which: `________`
- [ ] **One change named.** The single methodology change this round is measuring:
      `________________`
      Chosen from the ceiling stage? `yes / no — if no, say why`
- [ ] **Preregistration written.** `PREREGISTRATION.md` from the template, including the
      conditions that count against us.
- [ ] **Key isolated physically.** Not by intention. What was done:
      `________________`
      Verified the working tree cannot reach it: `________________`
- [ ] **Target read-only** where workers might write to it. `chmod -R a-w` or equivalent.
      Measured: blind workers wrote into a shared target directory against an explicit
      instruction not to.
- [ ] **Stage/agent table complete.** Every stage in `loop.config.yaml` has an agent
      (`STAGES.md`). No stage is "the orchestrator will do it" (D-1).

> Any box above unchecked → do not start. Each one is cheap now and unrecoverable later.

---

## During — per stage

Repeat for each stage. Do not batch the verification to the end.

- [ ] **Must-not-see checked.** The dispatched prompt was diffed against the stage's
      must-not-see list before sending (D-3).
- [ ] **Dispatched within the watchdog envelope.** Small blocks, 1–2 concurrent, first
      action forced to a trivial read.
- [ ] **Self-report verified** with a different tool than produced it (`VERIFY.md`).
      What was claimed: `________`  How checked: `________`  Held? `yes / no`
- [ ] **Denominator recorded** into `census.json`: how many units in, how many out, every
      drop with a cause.
- [ ] **Partial output checked** if any worker died and was re-dispatched, so the
      denominator does not double-count.

### If something leaks
- [ ] Recorded in the contamination note: **what** leaked, **which stage**, **what it
      cost** (`CONTAMINATION.md`).
- [ ] Round continued. A filing-time leak does not invalidate derivation (D-4).

### If a defect in the pipeline is found
- [ ] Written down. **Not fixed** (D-5). Where recorded: `________`

---

## Gating

- [ ] **Harness green** — the gate conformance test plus every lesson check.
      `python3 harness/run_all.py`
- [ ] **All gates run.** Every gate in `loop.config.yaml`, not the ones that came to mind.
- [ ] **No gate exited 2.** A CANNOT means the round stops here until the input is fixed
      (D-7). Do not read the prose and decide for it.
- [ ] **Attrition census clean.**
      `python3 scripts/attrition.py --round runs/<this>`
      Unaccounted drops: `______` (must be 0 — every drop needs a cause)
- [ ] **Card linter green** if any card was touched.
      `python3 scripts/lint_cards.py`

---

## Scoring

- [ ] **Key opened.** Not before this line.
- [ ] **Answers compared with the key**, by rule, not by eye. The pipeline's answers are in
      `answers.json`.
      `python3 scripts/compare.py --round runs/<this> --key <key.json>`
      Exit 1 means `judge` fields are pending: give each to the answer-judge agent
      (`templates/agents/answer-judge.md`, values only, no reasoning) and re-run until 0.
      Success: `____ / ____`   decided by a judge: `____`   extra answers: `____`
- [ ] **Every failure analysed** — a class, a stage and a cause for each, from the
      failure-analyst agent (`templates/agents/failure-analyst.md`), one problem per call.
      `python3 scripts/failures.py --round runs/<this> --apply <analysis.json>`
      `python3 scripts/failures.py --round runs/<this>` must exit 0.
      Largest (class, stage): `________`   key disputes: `____`
- [ ] **Both axes recorded.** Found, and delivered. Never collapsed into one number (L-2,
      `SCORING.md`).
      found: `______`   delivered: `______`
- [ ] **Scorer checked against a published result** at least once, ever. Which: `________`
- [ ] **Every miss attributed** to a stage and a cause (L-6) — `failures.py` exit 0 covers
      it for compared problems.
- [ ] **Loss priced** in the domain's currency, summed.
- [ ] **Ceiling re-established mechanically.**
      `python3 scripts/ceiling.py --round runs/<this> --missed <keywords>`
      Ceiling stage this round: `______`  (did it move? `yes / no`)
- [ ] **Rule costs counted** at the smallest unit each rule applies to (L-12).

---

## After — conversion

The round is not finished when it is scored. It is finished when the losses are nailed down.

- [ ] **`RESULT.md` written** from the template, including the `### <shared failure shape>`
      section. Two misses with one cause are **one** pipeline defect; that is the finding.
- [ ] **Each loss became a card AND a check**, in the same commit (L-10).
      Cards written: `______`   Checks written: `______`
- [ ] **Each check sabotage-verified.** Reintroduce the defect → confirm red → remove →
      confirm green. An untested check is a comment.
- [ ] **Card linter run** on the new cards. A rejection means restate as a structural
      condition, not add to the allow-list reflexively (L-11).
- [ ] **`SEALED.md` updated.** Target marked spent, with what methodology change it bought.
- [ ] **`RULE-LEDGER.md` updated.**
- [ ] **Next change named**, from the ceiling stage.
- [ ] **Skipped stages reported** by name, with reasons (D-8).

---

## Round closed

- Round id: `________`   Target: `________`
- Found / delivered: `______ / ______`
- Loss priced: `______`
- Ceiling stage: `______`
- Methodology change this round bought: `________________`
- Change for next round: `________________`

> If any of the five lines above is blank, the round produced a number but not a lesson,
> and the sealed target was spent for the number alone.
