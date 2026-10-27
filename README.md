# selfimprove

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill%20%2B%20plugin-8A63D2.svg)

**A Claude Code skill that builds a *measured* self-improvement loop for an agent pipeline,
in any domain. It interviews you, builds the scoring layer and the gates, and then runs
scored rounds.**

[한국어 README](README.ko.md)

```
/selfimprove "an agent that extracts fields from supplier invoices, built from our AP archive"
```

Most agent pipelines "improve" by someone rereading the output and feeling better about
it. This skill does not allow that. A round only counts if it can be **wrong in a way
nobody can argue with**, and that takes three things:

1. **A key the pipeline could not see.** It must be sealed by time or by another party, not
   be a held-out set you picked yourself.
2. **A scorer in the domain's own currency** that always reports two numbers, never merged
   into one: what was *found* and what was *delivered*.
3. **A written record, made before the run,** of what would count against you.

The skill builds these with you, one decision at a time. It then runs rounds that locate the
single stage where the metric's ceiling is set, and changes one thing per round. If your
domain has no such key, the skill tells you so, and it never invents a score.

---

## Contents

- [Install](#install)
- [Quick start](#quick-start)
- [A session, start to finish](#a-session-start-to-finish)
- [How it works](#how-it-works)
- [What it will never do](#what-it-will-never-do)
- [What it adds to your project](#what-it-adds-to-your-project)
- [Domain layers](#domain-layers)
- [Tools and the exit-code rule](#tools-and-the-exit-code-rule)
- [Where the effort goes](#where-the-effort-goes)
- [Contributing](#contributing) · [License](#license)

---

## Install

Requirements: [Claude Code](https://claude.com/claude-code), Python 3.9+, and
[PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`).

### As a plugin (recommended)

Inside Claude Code:

```
/plugin marketplace add https://github.com/13u9-kyeong/self-improve-skills.git
/plugin install selfimprove@selfimprove
```

Or from a shell:

```bash
claude plugin marketplace add https://github.com/13u9-kyeong/self-improve-skills.git
claude plugin install selfimprove@selfimprove
```

Plugin skills are namespaced, so it is invoked as **`/selfimprove:selfimprove`**. Pin a
release by appending `#v1.0.0` to the repository URL. The repository is private on GitHub,
so `git` must already be able to clone it (for example after `gh auth login` and
`gh auth setup-git`) before `/plugin` can.

### As a standalone skill

```bash
git clone https://github.com/13u9-kyeong/self-improve-skills.git
self-improve-skills/install.sh              # all projects -> ~/.claude/skills/selfimprove/
self-improve-skills/install.sh --project    # this project -> ./.claude/skills/selfimprove/
```

Invoked as **`/selfimprove`**. To update, pull and run `install.sh` again; it replaces the
installed copy completely.

Either way, the skill directory carries the whole kit in `kit/`. The first time you invoke
the skill in a project, it asks before installing the kit there. It never overwrites a file:
if the project already has a `CLAUDE.md`, the loop rules are appended under
`# Self-improvement loop` and you are shown the diff.

---

## Quick start

1. Open Claude Code in the project where the agent's work happens.
2. Say what you want in one sentence: `/selfimprove "an agent that does X, built from Y"`.
3. Answer the six questions. Each comes with 2–4 concrete options, the recommended one
   first, and states what each option leaves unmeasurable.
4. Let it build the layer and the gates, then say "run the next round" whenever you want
   another round.

You can stop at any point. Invoke `/selfimprove` again next week and it resumes at the first
unanswered question or the first unchecked box.

**Use it when** you want an agent to get measurably better at repeated work, for example:

- fixing bugs or writing tests against a codebase with a public change history
- extracting structured data from documents, classification, labelling
- forecasting, data analysis, spec-conformance work on a format or protocol
- anything else where you can say what counts as complete and what counts as proof

**Do not use it** for one-off tasks. Without repeated, scored rounds there is nothing for
the loop to improve.

---

## A session, start to finish

The domain is illustrative and the answers are made up, but the flow is what the skill does.

```
you   /selfimprove "an agent that extracts invoice fields, from our accounts-payable archive"

      [step 0]  loop_state.py -> kit not installed
skill The kit isn't in this project yet. It adds CLAUDE.md at the root (loaded into every
      session), plus scripts/, harness/, templates/, domains/. Install?
you   yes

      [setup:interview — goal]
skill Restating: the work is "fill the invoice schema from one scanned invoice"; success
      means "every field matches what the clerk posted to the ledger". Correct?
you   yes

      [setup:interview — material]   (the skill reads the archive first)
skill Found 41,200 invoices, OCR text for 38,900, received dates for all of them,
      and 1,140 invoices posted by clerks after the model's training cutoff.
        candidate key:   the 1,140 clerk-posted ledger entries (sealed by another party)
        raw material:    everything else

      [setup:interview — denominator]   AskUserQuestion
        > schema field × invoice   (Recommended)
            complete when every (field, invoice) cell has a disposition;
            give-up bucket: pages the OCR step could not read
        > line item × invoice
            enumerable, but misses header fields (totals, tax, terms)
        > the 41,200 invoices
            this is a sample, not a denominator — coverage would be unmeasurable

      [setup:interview — verdict]       one question per lens family
      [setup:interview — key]           inventory, sealing, training cutoff
      [setup:interview — delivered]     the hardest definition the destination offers

      [setup:phase0]
skill 0.1 passes: 1,140 post-cutoff invoices with clerk-posted entries. 0.2 passes after
      reproducing one month's reconciliation by hand. 0.3 passes: exact match by script.

      [setup:layer]  shows the stage table and lens families once, then writes
                     SURFACE / VERDICTS / STAGES / lenses / config / one agent per stage
      [setup:gates]  writes each gate, gives each a real failing input,
                     sabotage-verifies them, conformance test green

      [round:baseline]
skill Round 1 target: 60 unspent invoices from SEALED.md. Preregistration written, key moved
      out of the tree, target read-only. Running…
      compare: 41/60 success · failures: input_misread 9 at [3], reasoning_error 6 at [5]
      found 41/60 · delivered 29/60 · loss by stage: [6] grading 8, [7] delivery 4
      ceiling: 15 of 19 misses never appear in any artifact -> ceiling is [3] intake

      [round:next]
skill Proposed change for round 2: the one at [3] intake. A change at [6] could raise the
      delivered count but cannot raise recall, because recall is capped at [3]. Proceed?
```

---

## How it works

### The loop

The agent solves problems it has not seen. Each answer is compared, by rules fixed in
advance, with the key's answer for the same problem: a past report or an answer sheet.
Every failure gets a reason, the most common reason at the ceiling stage is fixed, and the
next round runs on fresh problems.

```
 problem ──▶ agent pipeline ──▶ answer
                                  │
 key (past report / answer sheet) ┴─▶ compare.py ──▶ success | failure
                                                          │
                       failure-analyst ──▶ failures.py ◀──┘   class · stage · cause
                                                │
            one change at the ceiling stage ◀───┘   (card + check, sabotage-verified)
                          │
                          └──▶ next round on unseen problems
```

### The skill never guesses its phase

On every invocation it runs `scripts/loop_state.py`, which reads the project's files and
prints the phase to run. In the history these rules came from, every orchestrator failure
had the same shape: an orchestrator guessed its phase from how the files looked.

| Phase | Entered when | What happens |
|---|---|---|
| `setup:interview` | no `INTERVIEW.md`, or one with unanswered choices | six decisions with you, recorded |
| `setup:phase0` | interview done; a hard gate unchecked with no recorded decision | the three hard gates; your call if one fails |
| `setup:layer` | Phase 0 decided; `new_domain.py --check` still rejects the layer | surface, verdicts, stages, agents, lenses, config |
| `setup:gates` | layer complete; a configured gate has no script | gate scripts, conformance test, sabotage checks |
| `round:baseline` | everything built; nothing scored | round 1: locates the ceiling, changes nothing |
| `round:in-progress` | a round has `ROUND.md` but no `RESULT.md` | resumes at the first unchecked box |
| `round:next` | at least one round scored | one change taken from the ceiling stage, then the next round |

### Six decisions, made with you

```
goal -> material -> denominator -> verdict -> key -> delivered
```

| Choice | What it asks | What the skill pushes back on |
|---|---|---|
| **goal** | "the work is ___; success means ___" in the domain's own terms | readings that would build different layers |
| **material** | what you have, each part marked *candidate key* or *raw material* | — |
| **denominator** | a product of two enumerable sets, each unit of which must get a disposition | a sample offered as the denominator ("our 10,000 files") |
| **verdict** | the strongest mechanism per lens family, with its tier and wall-clock time | a family whose only verdict is judgement: it files leads, not findings |
| **key** | one of five classes; how it is sealed; inventory; training-data cutoff | a curated set offered as the key |
| **delivered** | the strictest definition the destination offers | softer definitions, which inflate the delivered number and hide losses |

The skill reads your material before asking anything. It never asks what it can find out by
looking. Each question **proposes** options instead of asking open-endedly, and every
option states what it gives up. Answers are recorded with their reasons in
`domains/<name>/INTERVIEW.md`, so the design can later be re-argued from the record rather
than from memory.

### Three hard gates

| Gate | Passes when |
|---|---|
| **0.1** a key you could not see | sealed by time or by another party, and physically isolated (file permissions, not an instruction to the agent) |
| **0.2** the scoring can be reproduced | the scorer reproduces a known result you did not take part in |
| **0.3** the verdict is mechanical | a mechanism that runs (a test, a checker, an exact-match script), run by the orchestrator itself |
| 0.4 sizing | denominator chosen; completion can be counted |

If a hard gate fails, **you** choose: run the **no-key program** (attrition, loss
attribution, the gate exit-code rule, the rule ledger, verified self-reports, none of which
measure recall), **construct a key** (historical reconstruction, or injection, which gives
only a floor on recall), or **stop**. The skill never checks a gate that did not pass just
so setup can continue.

### Rounds

Round 1 has one job: **find the ceiling stage.** Nothing changes during it. Each round then:

1. takes an unspent target from `SEALED.md` and writes `PREREGISTRATION.md` before anything
   runs, including the conditions under which the result counts against you;
2. moves the key out of the working tree and makes the target read-only;
3. works through `ROUND.md` box by box, checking every agent self-report with a different
   tool, and records defects without fixing them mid-round;
4. opens the key only at the scoring box. `compare.py` compares each answer with the key by
   the layer's field rules, with a blind judge agent for fields no rule can decide. A
   failure-analyst agent gives every failed problem a class, a stage and a cause, and
   `failures.py` blocks until all have one. Then `score_round.py` (both axes, loss priced by
   stage) and `ceiling.py` (where each miss died) run;
5. writes `RESULT.md`: found, delivered, loss by stage, the ceiling, and **retention** (how
   many of last round's hits survived).

The next round makes **one** change, taken from the ceiling stage. It ships as a learned
card plus a mechanical check in a single commit, and the check is sabotage-verified: the
bug is reintroduced to confirm the check goes red.

---

## What it will never do

- Decide your denominator, verdict, key or definition of delivered without you.
- Check a Phase 0 gate that did not pass.
- Run a round on a layer that `new_domain.py --check` rejects.
- Fix anything in the middle of a round.
- Report a number from the no-key program as recall or precision.
- Treat an agent's self-report as a result.
- Open the key before the scoring step.
- Overwrite a file in your project.

---

## What it adds to your project

```
<project>/
  CLAUDE.md                  loop rules L-1 … L-16, loaded into every session
  ORCHESTRATOR.md PLAN.md PHASE0.md ROUND.md STAGES.md
  SCORING.md CONTAMINATION.md VERIFY.md FAILURES.md     the kit's guidelines
  loop.config.yaml           copied from your layer once its gates are green
  scripts/                   gatelib + tools + your gate scripts
  harness/                   run_all.py · conformance/ (exit-code test) · <lesson>/ checks
  templates/                 PREREGISTRATION, RESULT, SEALED, RULE-LEDGER, card, gate, agents
  .claude/agents/            one agent per stage
  domains/<your-domain>/
    INTERVIEW.md             your six decisions, with reasons
    PHASE0-<instance>.md     the hard gates, and the decision if one failed
    SURFACE.md VERDICTS.md COMPARE.md STAGES.md loop.config.yaml
    lenses/*.md              directed question families
  references/learned/        one card per measured loss
  runs/<date>-<name>/        PREREGISTRATION.md ROUND.md census.json scored.json RESULT.md
  SEALED.md                  key inventory: what is left and what each round spent
```

### The guidelines

| File | What it is |
|---|---|
| `CLAUDE.md` | Loop rules L-1 … L-16, each with the measurement that produced it |
| `ORCHESTRATOR.md` | Duties and prohibitions for the coordinating agent, D-1 … D-8 |
| `PLAN.md` | Bootstrap phases and the per-round cycle |
| `PHASE0.md` | Applicability worksheet: the hard gates, and what to do when 0.1 fails |
| `ROUND.md` | Per-round checklist, one copy per round |
| `STAGES.md` | Stage specification: seven fields, and what each one's absence cost |
| `SCORING.md` | Scorer construction by key class (A fix history / B judged set / C none) |
| `CONTAMINATION.md` | Judging a leak per stage instead of throwing the round away |
| `VERIFY.md` | Cookbook for mechanically checking self-reports |
| `FAILURES.md` | Catalogue of measured failures: 6 classes, each with its cost and current guard |

---

## Domain layers

The kit is domain-free: it says how a measured loop works, never what the work is. A
**domain layer** applies it to one kind of work. Normally the skill builds the layer with
you, but you can also scaffold one by hand:

```bash
python3 scripts/new_domain.py --name <domain> --instances <a> <b>
python3 scripts/new_domain.py --check domains/<domain>
```

A layer has seven components, and no round runs while any of them is missing:

| Component | Answers |
|---|---|
| `PHASE0-<instance>.md` | can the loop run here at all? |
| `SURFACE.md` | what is the denominator? |
| `VERDICTS.md` | what says "this is real" without relying on our opinion? |
| `COMPARE.md` | how is one answer compared with the key, and what is each failure called? |
| `STAGES.md` | which stages, under which specifications? |
| `lenses/` | which directed questions get run across the whole surface? |
| `loop.config.yaml` | everything above, in machine-readable form |

The same three choices, sketched for five domains:

| Domain | Denominator | Best verdict | Key sealed by |
|---|---|---|---|
| Bug fixing | reported issues × touched modules | the fix's regression test fails before, passes after | fix history, time |
| Test generation | public functions × documented behaviours | the test fails on the buggy revision, passes on the fix | fix history, time |
| Document extraction | schema fields × documents | exact match by script against the posted value | entries posted by another party after cutoff |
| Forecasting | questions × resolution dates | resolution against the realised outcome | questions that resolve after the run |
| Spec conformance | message types × fields × transitions | a synthesised message the real implementation accepts | a later-published specification |

What they share: every denominator is a **product of two enumerable sets**, every verdict
is a **mechanism that runs**, and every key is sealed by **time or by another party**. If
your three answers lack that shape, usually one of them has been replaced by something
weaker: a sample in place of a denominator, an opinion in place of a verdict, or a curated
set in place of a key.

---

## Tools and the exit-code rule

Every tool obeys one rule (`scripts/gatelib.py`):

```
0 PASS    judged, and it passed
1 FAIL    judged, and it failed
2 CANNOT  could not judge — unreadable input, empty input, missing tool. NOT a pass.
3 USAGE   the invocation was wrong
```

A gate that prints a problem and exits 0 was the most repeated defect in the history these
rules came from: it happened eight times, each patched individually. That is why the rule
is enforced by one conformance test over every gate, rather than by per-gate care.

| Tool | What it does |
|---|---|
| `scripts/loop_state.py` | Prints the phase the skill must run next |
| `scripts/new_domain.py` | Scaffolds a domain layer, or checks one (including leftover placeholders) |
| `scripts/score_round.py` | Two-axis scorer; refuses to output a single number; flags losses not attributed to a stage |
| `scripts/ceiling.py` | Finds the ceiling stage by searching every artifact, not by reasoning |
| `scripts/compare.py` | Compares each answer with the key's answer for the same problem, by field rules; writes `scored.json` |
| `scripts/failures.py` | Blocks until every failed problem has a failure class, a stage and a cause; counts them by class and stage |
| `scripts/attrition.py` | Candidates → filed → delivered census, with a cause for every drop; needs no key |
| `scripts/lint_cards.py` | Rejects target proper nouns in learned cards, so lessons stay general |
| `harness/conformance/test_exit_codes.py` | Asserts the rule on every configured gate, on three axes |
| `harness/run_all.py` | Runs the conformance test and every lesson check (`harness/<lesson>/test_*.py`) as one verdict |

New gates start from `templates/gate.py`, which already obeys the rule: copy it,
replace its `check()`, register it in `loop.config.yaml`, and run the conformance test.

The kit also ships four agent templates. Two do the scoring in every round:
`failure-analyst` (gives one failed problem a class, a stage and a cause, by searching the
round's artifacts) and `answer-judge` (decides fields no rule can, seeing only the two
values; needed only when the comparison has `judge` fields). Two are optional adversarial
passes, for pipelines with a stage that drops or accepts candidates before delivery:
`refuter` (gets the claim, never the reasoning) and `blind-rereader` (gets locations only,
with no conclusion attached).

**Verify an install.** In a freshly installed project, every tool must refuse to judge
empty input:

```bash
python3 harness/conformance/test_exit_codes.py              # 2
python3 scripts/lint_cards.py                               # 2
python3 scripts/attrition.py --round runs/nope              # 2
python3 scripts/ceiling.py --round runs/nope --missed x     # 2
python3 scripts/score_round.py --round runs/nope            # 2
python3 scripts/new_domain.py --check domains/nope          # 2
python3 scripts/loop_state.py                               # 0 -> phase setup:interview
```

If any of them exits 0, that tool reports success on empty input, and it will report
success on your real rounds the same way.

---

## Where the effort goes

Ranked by where value was actually won and lost in the rounds these rules came from:

1. **Delivery discipline**: selection, grading, filing. This was the largest measured loss.
   In one round, 9 of 13 key items were found but only 2 were delivered.
2. **Coverage of the denominator**: cheap completeness checks caught 15 finished items that
   had never been submitted.
3. **Interaction between two mechanisms**: defects that only exist where two correct parts
   meet. These carried the highest-value results.
4. **Independent re-attack**: the blind passes, especially the one that sees no conclusion.
5. **Raw detection breadth**: worth the least.

Effort tends to drift toward item 5 by instinct. Where your domain already has mature
mechanical tools, use them to generate candidates and spend the agent's effort on items 1–4.

---

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.
In short: the kit stays domain-neutral (a test enforces it), every tool obeys the exit-code
rule, and every fix ships with a test that fails on the original defect.

```bash
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
