# Contamination — judging it per stage

> Expands L-4. The rule is one line: **seeing part of the answer at delivery time is not the
> same as seeing it while deriving.** This file is the procedure, because the rule was
> stated correctly for several rounds and still applied wrongly — twice too harshly, once
> too leniently.

---

## Why per-stage and not per-round

A round discarded for a leak spends a sealed target and returns nothing. A round kept
despite a derivation leak returns a number that is worthless and, worse, gets averaged with
honest rounds.

Neither is acceptable, so the judgement has to be finer than the round. The unit is the
**stage**, because a leak's damage is bounded by what the leak could have changed:

| Stage class | What a leak here does |
|---|---|
| **derivation** | Destroys the measurement. The pipeline may have found the item *because* of the leak, and no later evidence can separate the two. |
| **promotion** | Damages selection only. What was found is still measured; what was chosen is not. |
| **filing** | Damages nothing measurable. The item was already found and already graded. |

So the question is never "was this round contaminated". It is **"which stages could this
leak have reached, and what did each one produce after it."**

---

## The procedure

### 1. Record the leak the moment it happens

Not at scoring time. Write:

```
leaked:   <exactly what was seen — the terms, not a paraphrase>
where:    <the file/page/command that exposed it>
when:     <which stage was in flight>
reached:  <which stages ran AFTER this point>
```

A leak recalled at scoring time is a leak you will under-report, because by then you know
the result and the result argues for leniency.

### 2. Judge mechanically, from the transcript

**Search the actual dispatched prompts for the leaked terms.** Not your memory of what you
knew when — that is the least reliable input available, and it is biased by the outcome.

```bash
# every prompt sent to every worker in this round
grep -ril "<leaked term>" runs/<round>/dispatch/ runs/<round>/*/prompt*
```

Measured: a round was first graded 3/5 on a recalled impression. After searching all 12
worker prompts and finding **zero** leaked terms in any of them, it was re-graded 4/6. The
first grade was wrong in the *conservative* direction, which cost a real result and is just
as much an error as the lenient direction.

### 3. Judge each affected stage separately

For each stage that ran after the leak:

- **Could the leak have reached it?** If the terms are absent from its inputs, it is clean.
  Say so and move on.
- **If present:** that stage's output is contaminated. Its contribution is reported
  separately and excluded from the headline number.

### 4. Price the judgement

Whatever you decide, write the cost next to it:

```
F-07  flagged contaminated at promotion: the orchestrator selected it into the
      verification batch after reading the key.
      Cost of the flag: this item is excluded from the delivered axis (-1),
      and it is still counted on the found axis, because derivation never saw
      the key (verified: 0/12 prompts contain the term).
```

A flag without its cost is how rounds get quietly over-flagged. An item excluded from one
axis and kept on another is the normal case, not a special one.

### 5. Amend the preregistration

Every contamination judgement becomes a numbered amendment, stating whether it was written
before or after scoring (L-3). Amendments made after seeing results are fine. Hiding when
they were made is not.

---

## Common cases, pre-decided

Decide these once, here, so they are not re-litigated under outcome pressure.

| Case | Judgement |
|---|---|
| Read the key's own file while setting up the build | Leak. Record what was visible, judge which stages ran after. Measured: this happened via a config file holding 3 item titles. |
| The key was inside the target clone | Leak, and a setup defect. Fix isolation before the next round. |
| A worker opened a prior report on the target | Derivation leak for that worker. Its output is contaminated; the others are not. |
| The orchestrator selected items into a later stage after opening the key | Promotion leak. The found axis survives; the delivered axis for those items does not. |
| A leaked term appears in a worker's output but not its input | **Not a leak.** The worker derived it. This is the case most often misjudged as contamination. |
| Public knowledge of the target predates the round | Not a round-level leak. Record it as a property of the target and prefer targets without it. |
| The model may have the key in training data | Not judgeable per-stage. Handle it by **target selection** — prefer keys sealed by time (post-cutoff fixes), and record the cutoff you relied on. |

That last row is the one that cannot be fixed by procedure. If a domain's keys are all
likely in training data, the loop's recall numbers are not trustworthy no matter how clean
the round was, and the honest move is to say so in `PHASE0.md` under 0.1.

---

## What does not count as isolation

Measured failures, all of them:

- **An instruction not to look.** Workers wrote into a shared target directory against an
  explicit instruction. Instructions do not isolate.
- **A `.gitignore`.** It hides nothing from a worker with Read.
- **Putting it in a different directory in the same tree.** `grep -r` from the repo root
  reaches it.

What does isolate: the key outside the working tree entirely, and the target `chmod -R a-w`
so a worker that tries to write fails loudly instead of silently succeeding.

---

## Reporting

In `RESULT.md`, contamination gets its own lines, not a footnote:

```markdown
## Contamination
| what leaked | where | stage in flight | stages reached | verified how | cost |
|---|---|---|---|---|---|
```

A round with no leaks writes the table with one row saying so. An absent table reads as
"nobody checked", which over a series is indistinguishable from "nothing leaked" — and
those are very different facts.
