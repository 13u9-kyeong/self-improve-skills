# Building the scorer

> Expands L-2 and Phase 0.2. The scorer is written **before** round 1, because it defines
> what the pipeline must emit. A pipeline built first will emit what is convenient, and the
> scorer will be bent to fit it.
>
> This file is organised by **key class**, because the key you have determines everything
> else. Find your class first; most of what follows does not apply to the other two.

---

## The two axes, never collapsed

True in every key class:

```
found      what the pipeline identified
delivered  what survived to the thing the domain actually counts
```

Report both, always, side by side. The gap between them is the most informative number the
loop produces and it is invisible in either axis alone.

Measured: recall **9 of 13** against the key, valid delivery **2**. The count metric
displayed a 78% loss as 69% success, and every improvement planned off that number targeted
detection, which was not the problem.

Make it structural: a scorer that can emit one number will eventually be asked to. Have it
refuse (`scripts/score_round.py` does).

What `delivered` means is domain-specific and you must write it down in
`loop.config.yaml` before round 1:

| Domain | `delivered` means |
|---|---|
| Upstream open-source work | the maintainer accepted it, or a fix landed |
| Internal or client work | it reached the client's deliverable and they acted on it |
| A paid-per-item program | it was paid |
| A competition | it was judged valid and in-scope |

Pick the hardest one the domain offers. A softer definition inflates the delivered axis and
hides exactly the losses the loop exists to find.

---

## Key class A — a fix history (most open-source work)

The key is a patch plus its parent commit. The strongest class, and the one with no prize
economics at all.

**Scoring unit:** did the pipeline identify the defect the patch fixed, at the location the
patch touches, by the mechanism the patch changes?

```
hit        same mechanism, within the patch's touched locations
near       right location, wrong mechanism      -> this is a MISS, recorded separately
miss       mechanism absent from every artifact -> a detection loss (scripts/ceiling.py)
```

**The `near` bucket is the one that matters here.** It is the measured dominant failure
shape: the right line reached by the wrong question. Do not fold it into hits, and do not
fold it into misses without recording it — a round whose misses are mostly `near` needs a
different change than one whose misses are absences.

**Currency:** there is no pot. Use, in this order:

1. **A grade under a published rubric**, applied by someone other than the pipeline.
2. **Whether it reproduces** — an executable reproduction is a stronger unit than any
   grade label and it is machine-checkable.
3. **Count**, with the two axes. Weak, but honest if you say so.

**What you cannot measure in this class:** value concentration. There is no duplicate or
rarity notion, so **L-16 is unmeasurable** and you must record that as a blind spot in
`PHASE0.md` rather than substituting a proxy. L-16's *prohibitions* still apply wherever
delivery is to a paid-per-item program; its *measurement* does not transfer.

**Hazard specific to this class:** a patch often fixes more than it says, and sometimes
less. Score against what the patch **changes**, not against its message. Measured in
adjacent work: commit messages systematically understate scope.

---

## Key class B — a judged set (competitions, formal review with a published verdict)

The key is someone else's verdict list. This class is where the source project's numbers
come from, and it is the only class with prize economics.

**Currency, in order of preference:**

1. **A published payout formula.** Reproduce it exactly. Recover any constant from a
   published total rather than guessing:

   ```
   k = pot / Σ(weight · decay(n) · adjust(n))
   ```

   Keep a `--k` override for instances where the total is not published — measured, several
   were not, and without the override those instances were unscoreable.

2. **Rank.** Only ever comparable **within one instance**. Measured: mean submitters per
   item were 8.97, 0.92 and 0.67 across three instances of the same domain, so identical
   output ranks wildly differently.

3. A published grading rubric plus accepted/rejected.

**The judged set is not the payable set.** Measured: of 60 judged items, 40 had already
been published as known and paid nothing. A round reporting "34 of 60" had said almost
nothing — 26 of those 34 were unpayable. Compute the eligible denominator first.

**This is the only class where L-16 is measurable.** See `CLAUDE.md` L-16 for the numbers.

---

## Key class C — no key (internal assessment, a live engagement)

The loop as written does not run. Say so. Then run what does, and be precise about what it
cannot tell you.

**Three substitutes, in order of practicality:**

1. **Historical reconstruction.** The target's own past findings plus the commits that fixed
   them. Check out each fix's parent and run. This is a real class-A key, built from private
   history, and it is the most underused option in client work — a client with three
   years of reports has a benchmark already.
2. **Injection.** Mutation or deliberate defect insertion. Measures a **floor on recall**
   and nothing else, because you only find what you planted. Useful for catching checks that
   pass on empty input; not evidence of recall.
3. **Differential.** Two independent configurations; measure disagreement. Localizes, never
   validates. Agreement between two of your own configurations is not correctness.

**What still works with no key at all** — and these found and fixed 15 real defects in the
source project:

- attrition accounting, candidates → filed → delivered (`scripts/attrition.py`)
- loss attribution per stage (L-6)
- the gate exit-code rule and its conformance test (L-8, L-9)
- the rule-cost ledger (L-12)
- mechanical verification of self-reports (L-14)

**What does not:** recall, precision, and any claim about completeness. Do not report an
attrition improvement as a detection improvement. They are different facts and the first one
is silent about the second.

---

## Per-problem answer keys — past reports and answer sheets

The most common key outside open-source work: a set of problems the work has already been
done on, each with the answer that was accepted at the time — a past report, a posted
entry, a graded answer sheet. It is a class-A or private-history key (who sealed it decides
which), scored per problem:

```
answers.json  ──compare.py──▶  scored.json  ──failures.py──▶  every failure: class · stage · cause
   (pipeline)     field rules      success / not_attempted / format / wrong
                  from COMPARE.md
                                           ──score_round.py──▶  found / delivered, loss by stage
```

- **The comparison is fixed before round 1** (`COMPARE.md`): the unit, one rule per field,
  the failure classes. A rule chosen after seeing the answers fits the scorer to the result.
- **The judge is a separate, blind agent** for fields no rule can decide, and judged
  problems are reported on their own line. A round that is mostly judged measures agreement
  with the judge.
- **A failure is not analysed until it has a reason.** `wrong` says a value differed;
  `input_misread` or `reasoning_error` says what to change. `failures.py` blocks the round
  until every failure has one, and its largest (class, stage) cell is the first candidate
  for the next round's single change.
- **Never use the same past report to build the agent and to score it.** Reports used as
  examples, templates or reference material for any stage are spent as keys (L-1); record
  which are which in `SEALED.md` before round 1.

## Rules that hold in every class

### Check the scorer against something you did not produce

Before round 1, reproduce a **known result you did not participate in**. A scorer that
cannot reproduce a known outcome will not measure your own, and you will not find out until
the number matters.

Watch for display scaling. Measured: a source published figures at **1/100 of actual** — a
displayed `515.03` was really `51,503.12`. The scorer matched the display perfectly and was
wrong by two orders of magnitude for three rounds.

### As-scored versus counterfactual

```
as-scored       what this round actually earned
counterfactual  what it would have earned had <x> been filed or graded differently
```

Counterfactuals are the most useful output of the loop — they price losses (L-6), and that
is what turns a miss into a methodology change. They are also the easiest thing to quietly
promote into the headline.

**The headline is always as-scored.** Counterfactuals go in their own section, each labelled
with the specific change assumed. Never average the two.

### Score misses, not just hits

The scorer emits per-item rows, not totals:

```
item · found? · at which stage · filed as what · delivered? · value · if missed, why
```

A total cannot be attributed (L-6), and an unattributed loss cannot become a card (L-10). A
scorer that emits only aggregates ends the round with a number and no lesson.

### Write down what your currency cannot see

In `PHASE0.md` under 0.2. Every currency is blind to something:

| Currency | Blind to |
|---|---|
| count | value concentration, grade, reproducibility |
| grade label | whether anyone would pay or act |
| payout | anything outside the program's scope rules |
| reproduction passes | defects that produce no observable failure |
| fix landed | defects the maintainer declined for policy reasons |

Recording the blind spot is what stops the next round optimizing into it.

---

## Things that are not scoring

- **Your own report is not a precision measurement.** Measured: a round's report was used to
  compute precision, but it held only what passed the gates — so the figure measured the
  gates. Precision is computed over everything the pipeline produced, including drops.
- **A matched title is not a matched item.** Match on mechanism and location. Measured once
  in each direction: a gate rejected a real item over phrasing, and a later round counted a
  hit that shared only a title with the key's item.
- **A passing reproduction is not a grade.** It proves the mechanism. Impact is a separate
  judgement and a separate stage.
- **Agreement between two of your own configurations is not correctness.**
