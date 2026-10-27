# Phase 0 — can the loop run in this domain?

> Fill this in before writing any pipeline code. Three hard gates and one sizing question.
> A domain that fails a hard gate does not run this loop; say so and run the no-key program
> instead (see the end of `CLAUDE.md`).
>
> Copy this file into the project and answer in place. Leaving a box blank is an answer of
> "no" — the loop's own rule L-8 applies to this worksheet too.

---

## Gate 0.1 — Is there a key you could not see? (hard)

A key is sealed by a mechanism **outside your control**, before your run.

| Key | Sealed by | Inventory | Machine-checkable |
|---|---|---|---|
| Public fix history (patch + parent commit) | time | effectively unlimited | yes, if a tool can detect the defect |
| Judged competition results | the judge | tens | no — needs matching |
| A client's / team's past findings + their fixes | the client | tens | sometimes |
| Deliberate injection / mutation | you | unlimited | yes |
| A held-out set you curated | **nobody** | — | — |

The last row is not a key: you chose it knowing what your pipeline does. Injection measures
only what you injected, which makes it a **floor on recall** and nothing more — useful, not
sufficient.

The first row is the strongest and is systematically underused. **The parent commit of any
fix is a live instance of that defect.** A domain with a long public fix history has
unlimited sealed inventory, and by L-5 that single number sets your whole iteration rate.

**Answer:**

- Which key: `________________`
- Sealed by what mechanism outside my control: `________________`
- How I will isolate it physically during a run (permissions/path — not intention):
  `________________`
- Inventory, counted: `______`

> **Fails this gate if:** the only key is one you curated, or isolation is "I will not look".
> Measured: a round had the key inside the clone it was working on, and another had agents
> writing into the shared target directory against an explicit instruction not to.
> Instructions do not isolate. File permissions do.

---

## Gate 0.2 — Can you reproduce the scoring function? (hard)

Find the domain's own denomination: payout formula, rank, a grade under a published
rubric, accepted/rejected. Then write the scorer **before round 1** and verify it reproduces
a known published result you did not participate in.

A scorer that cannot reproduce a known outcome will not measure your own. Where a formula
has a constant, recover it from a published total rather than guessing, and keep an override
for instances where it cannot be recovered.

**Answer:**

- The currency: `________________`
- The formula, or "none published": `________________`
- The published result I will reproduce as a check: `________________`
- Reproduced? `yes / no`  — if no, stop here and build the scorer.

> **Fails this gate if:** you plan to score with a metric you defined against someone
> else's key. That measures nothing.
>
> Also note what the currency makes **unscoreable**. A domain with no duplicate/rarity
> concept cannot measure L-16 at all, and you will not see the convex-payoff effect even
> if it is there.

---

## Gate 0.3 — Is a verdict mechanical? (hard)

Something must be able to say "this is real" without your pipeline's opinion.

```
an assertion / checker / failing test    best — a verdict with no interpretation
a test that exercises the real target    good — but you run it yourself, every time
a diff against a known fix               ok   — proves location, not impact
a human or model judgement               NOT a verdict
```

**Answer:**

- The verdict mechanism: `________________`
- Who runs it (must be you, not the agent that produced the artifact): `________________`
- Typical wall-clock per verdict: `______`  ← this sets your round cost more than anything

> **Fails this gate if:** the best available is the last row. Go back to 0.1 — you are
> measuring agreement, not correctness.
>
> If verdicts are **probabilistic** (a race, a flaky reproducer), record the success rate
> as part of the verdict and never report a single success as "reproduces".

---

## Question 0.4 — How big is the smallest useful unit? (sizing)

This decides whether exhaustive enumeration survives — the most valuable mechanic in the
pipeline and the first to break.

```
unit under ~5K lines      enumerate every line. Keep it.
unit 10K-100K lines       shift the denominator. Enumeration still works.
unit over ~1M lines       enumeration is dead without a candidate generator.
```

**Shifting the denominator** is the move that saves the mechanic. You do not abandon
exhaustiveness; you change what it counts:

```
every source line   ->   every entry point
                    ->   every input -> effect candidate pair
                    ->   every documented claim
```

Entry points and candidate pairs are enumerable even in very large targets. The gate stops
asking "did you read every line" and asks **"does every candidate have a disposition"** —
the same discipline on a tractable denominator.

**Answer:**

- Smallest unit that still produces a scoreable result: `________________`
- Its size: `______`
- My denominator: `________________`
- How I will know it is complete: `________________`

> Choose the **smallest** unit that still scores. Measured across one port: reasoning stages
> transferred between domains almost unchanged, and the entire cost landed in build,
> slicing and verdict adapters. A small unit buys the cheap half first.

---

## Verdict

- [ ] 0.1 passes — a key I could not see, physically isolated
- [ ] 0.2 passes — scorer written and verified against a published result
- [ ] 0.3 passes — a mechanical verdict I run myself
- [ ] 0.4 answered — denominator chosen, completeness definable

**All four checked** → go to `PLAN.md` Phase 1.

**Any hard gate unchecked** → the loop does not run here. Run the no-key program instead:
loss attribution (L-6), the gate exit-code rule (L-8/L-9), the rule ledger (L-12), mechanical
verification of self-reports (L-14), and attrition accounting
(`scripts/attrition.py`). Measured, that program found and fixed 15 real defects with no key
involved. It is real work. It just cannot tell you anything about recall, and you must not
report it as if it could.

---

## When 0.1 fails — constructible substitutes

There is no sealed verdict list for a target nobody has judged. The temptation is to curate
a held-out set from your own outputs, which is not a key. Three substitutes, in order of
practicality:

### A. Historical reconstruction — the one that actually works

The target's own past findings, plus the changes that resolved them.

```
for each historical item H with resolving change F:
    restore the state before F  -> a live instance
    the key is: H's write-up, its grade, its reproduction
```

This **is** a class-A key (`SCORING.md`), built from private history. It is the most
underused option in client or internal work: anyone with years of past reports has a
benchmark already built, and is usually willing to share it because it costs nothing.

Inventory = the number of historical items with an identifiable resolving change. Count it
in `SEALED.md`. Typically tens — so **batch methodology changes into fewer, larger rounds
from day one** (L-5). Isolation is the same as any key: strip history, keep the write-up
outside the tree, `chmod -R a-w`.

**Hazard:** historical items are biased toward what the previous worker looked for. A
pipeline tuned to them inherits that bias and looks good on the benchmark while missing the
classes nobody checked before. Record it as a known limitation.

### B. Injection — a floor, not a measurement

Insert defects deliberately, or mutate existing material, and measure what the pipeline
finds. Measures a **floor on recall** and nothing more: you only find what you planted.
Genuinely useful for one thing — catching stages and gates that pass on empty input, which
is FAILURES class 1. Never report an injection result as recall.

### C. Differential — localizes, never validates

Two independent configurations; measure disagreement. Agreement between two of your own
configurations is not correctness. Useful for pointing at contested items, worthless as a
score.

**If none is available:** do not run the loop and do not report as if you had. Run the
no-key program, and say in the deliverable that it measures attrition, not recall.

---

## Worked example — a domain that passes

Filled in for a bug-fixing agent on an open-source library, to show the shape of a good
answer:

- **0.1** Public fix history; sealed by time; parent commit of each bug-fix commit is a live
  instance; inventory unlimited. Isolated by cloning the target at the parent commit into a
  directory with the fix commit and issue text absent, `chmod -R a-w`.
- **0.2** Currency: the maintainer merged it. Check: reproduce the accept/reject of a set of
  historical pull requests. Note: there is no duplicate concept, so L-16 is unmeasurable
  here — recorded as a known blind spot.
- **0.3** The fix's own regression test: fails before, passes after, rest of the suite
  green. Run by me, not the agent. ~40 s per verdict including build.
- **0.4** One module, 1–3K lines. Denominator: every public function × every documented
  behaviour. Complete when every cell has a disposition.

Note what makes it a good answer: unlimited inventory, a verdict needing no interpretation,
and a unit small enough that exhaustive enumeration survives. Also note that it records what
it **cannot** measure, which is the part most worksheets leave out.
