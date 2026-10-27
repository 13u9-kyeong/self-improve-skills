# Bootstrapping the loop in a new domain

> Companion to `CLAUDE.md` (rules L-1 … L-16). That file says what to obey while the loop
> runs. This one says how to get a loop running at all, and what each round does.
>
> Phases 0–2 are one-time. Phase 3 onward repeats forever.

---

## Phase 0 — Decide whether the loop can run here

Answer these four before writing any pipeline code. Three of them are hard gates.

**0.1 Is there a key you could not see?** (hard gate — L-1)

A key is sealed by a mechanism outside your control. Ranked by how good they are:

| Key | Sealed by | Inventory | Machine-checkable |
|---|---|---|---|
| Public fix history (patch + parent commit) | time | effectively unlimited | yes, if the defect is detectable by a tool |
| Judged competition results | the judge | tens | no — needs matching |
| Your client's own past reports + their fixes | the client | tens | sometimes |
| Deliberate injection / mutation | you | unlimited | yes |
| A held-out set you curated | **nobody** | — | — |

The last row is not a key. The second-to-last measures only what you injected, which makes
it a floor on recall and nothing else — useful, not sufficient.

The first row is the best and is systematically underused: **the parent commit of any fix
is a live instance of that defect.** A domain with a long public fix history has an
unlimited sealed inventory, which by L-5 sets your entire iteration rate.

**0.2 Can you reproduce the scoring function?** (hard gate — L-2)

Find the domain's own denomination — payout formula, rank, a grade under a published rubric,
accepted/rejected. Write the scorer **before** round 1 and verify it reproduces a known
published result you did not participate in. A scorer that cannot reproduce a known outcome
will not measure your own.

If the domain denominates in money, recover the constant from a published total rather than
guessing it, and leave a `--k` style override for instances where it cannot be recovered.

**0.3 Is a verdict mechanical?** (hard gate — L-14)

Something must be able to say "this is real" without your pipeline's opinion. Ranked:

```
an assertion / checker / failing test    best — a verdict with no interpretation
a test that exercises the real target    good — but verify the runner yourself
a diff against a known fix               ok   — proves location, not impact
a human or model judgement               not a verdict
```

If the best available is the last row, go back to 0.1 — you are measuring agreement, not
correctness.

**0.4 How big is the smallest useful unit?** (sizing, not a gate)

This decides whether exhaustive enumeration survives, which is the most valuable mechanic in
the whole pipeline and the first one to break.

```
unit under ~5K lines      enumerate every line. Keep it.
unit 10K-100K lines       shift the denominator (below). Enumeration still works.
unit over ~1M lines       enumeration is dead. Needs a candidate generator.
```

**Shifting the denominator** is the move that saves the mechanic. You do not abandon
exhaustiveness, you change what it counts:

```
every source line                 ->  every entry point
                                  ->  every input → effect candidate pair
                                  ->  every documented claim
```

Entry points and candidate pairs are enumerable even in very large targets. The gate stops
asking "did you read every line" and asks "does every candidate have a disposition" — which
is the same discipline on a tractable denominator.

**Choose the smallest unit that still produces a scoreable result.** Measured across ports:
reasoning stages transferred between domains almost unchanged; the cost landed entirely in
build, slicing and verdict adapters. Picking a small unit buys the cheap half first.

---

## Phase 1 — Build the scorer, then the smallest pipeline that feeds it

Order matters. The scorer first, because it defines what the pipeline must emit.

**1.1** Write the scorer. Verify against a published result (0.2).

**1.2** Write the thinnest end-to-end pipeline that produces a scoreable artifact. Thin means
*thin*: one candidate generator, one filter, one verdict step, one emitter. No lenses, no
adversarial passes, no gates beyond the rule.

Resist building the full pipeline before round 1. You do not yet know where your ceiling
stage is (L-7), and every stage built before the first measurement is a stage built on a
guess.

**1.3** Adopt the gate exit-code rule (L-8) and the conformance test (L-9) **now**, while there are
three gates instead of sixty. Retrofitting it later cost this loop eight separate incidents.

**1.4** Create the layout:

```
<project>/
  CLAUDE.md                 the loop rules (L-1 … L-16)
  PLAN.md                   this file
  scripts/
    gatelib.py              the exit-code rule (L-8)
    score_round.py          the scorer (1.1)
    <stage tools>
  references/
    frozen/                 off-limits: output format, verdict rules, loop rules
    learned/                one card per measured lesson (L-10, L-11)
  harness/
    run_all.py              runs every check below as one verdict
    conformance/               the gate conformance test (L-9)
    <per-lesson fixtures>   one per card, sabotage-verified (L-10)
  runs/
    <date>-<name>/
      PREREGISTRATION.md    written before the run, amended in place (L-3)
      <stage outputs>
      RESULT.md             written after scoring (Phase 4.6)
  SEALED.md                 inventory: what is unspent, what each round consumed (L-5)
```

**1.5** Write `SEALED.md` and count the inventory. If it is under ~10, plan to batch
methodology changes into fewer rounds from the start.

---

## Phase 2 — Round 1 is a baseline. Do not optimize it.

Run the thin pipeline on one sealed target. Score it. Write `RESULT.md`.

The only question round 1 answers is **where the ceiling is** (L-7). Establish it
mechanically: for each item the key contains and you missed, search every artifact your
pipeline produced for that item's mechanism. Where the mechanism first fails to appear is
your ceiling stage.

Do not fix anything during round 1. A fix applied mid-round makes the round unscoreable and
spends a sealed target for nothing.

---

## Phase 3 — The round cycle

This is the loop. Each pass spends exactly one sealed target and produces exactly one
methodology change set.

### 3.1 Preregister
Write `PREREGISTRATION.md`: target, order, success definition in the domain's terms, the
conditions under which the result counts against you, reporting rules. Amend in place,
numbered, with before/after-results stated (L-3).

### 3.2 Isolate the key
Physically. Move it out of the working tree, or make the tree read-only. Measured: a round
had the key inside the clone it was working on, and another had blind agents writing into the
shared target directory against explicit instruction. Instructions do not isolate; file
permissions do.

### 3.3 Run, without looking
Keep a contamination note open. When something leaks, record **what** leaked, **at which
stage**, and **what it cost** — then keep going (L-4). A leak at filing does not invalidate
derivation.

### 3.4 Verify self-reports before using them
Every count, every "passed", every "complete" gets checked by you, mechanically, with a
different tool than the one that produced it (L-14). This is the cheapest high-yield step in
the cycle.

### 3.5 Gate, then score
Gates run to the rule. A CANNOT stops the round — fix the input, do not proceed on a
verdict nobody reached.

Then open the key and score. Record **both** numbers (L-2): what the pipeline found, and
what survived to delivery. Never collapse them.

### 3.6 Write `RESULT.md`
Structure that has held up over 46 rounds:

```markdown
# <target> — result
## Result — both axes          what was found / what was delivered, in the domain's currency
## Hit (n)                     each with where it was found and where it was filed
## Missed                      each attributed to a stage and a cause (L-6)
### <shared failure shape>     group misses that share a cause — this is the finding
## Nearly missed               items that survived by luck; treat as misses
## Loss priced                 <stage>: <amount>, summed (L-6)
## Ceiling check               which stage can move this metric, verified mechanically (L-7)
## Rule cost this round        what each standing rule closed (L-12)
## To carry into the next round
```

The `### <shared failure shape>` section is where the value is. Two misses with the same
cause are one defect in the pipeline, and that is the thing worth a change. Isolated misses
are usually noise.

### 3.7 Convert each loss into a card **and** a check
In one commit (L-10):

- `references/learned/<lesson>.md` — measurement and N up front, then what the numbers say,
  then **what was tried and removed with its score**, then `## Therefore` as obeyable
  prohibitions.
- `harness/<lesson>/test_*.py` — fails on the original defect. **Sabotage-verify it**:
  reintroduce the bug, confirm red, remove it, confirm green. `harness/run_all.py` picks
  it up automatically from then on.
- Run the card linter. When it rejects a term, restate the lesson as a structural condition
  (L-11).

### 3.8 Update the ledgers
- `SEALED.md` — mark the target spent, note what methodology change it bought.
- Rule ledger — what each standing rule closed this round, counted at the **smallest unit
  the rule applies to** (L-12).

### 3.9 Decide the next change set
One methodology change per round (L-5). Pick it from the ceiling stage (L-7) — a change
anywhere else cannot move the metric you are trying to move, however obviously correct it
looks.

---

## Phase 4 — Keeping it honest over many rounds

**Retention, not total.** Re-measure on fresh targets and track how many of the previous
round's hits survive. Measured: a re-measurement kept **10 of 20** prior hits while the total
held steady. A flat total across rounds can be a moving sample window, not convergence. If
you only track totals you will not see this.

**Rule-cost review.** Periodically re-derive what the accumulated rules close (L-12). Rules
only ever get added. Without review the rule set silently becomes the ceiling.

**Attrition audit, no key needed.** Count candidates → filed → delivered every round. This
needs no sealed target and it is where the loop's largest single loss was found: detection at
9/13 with 2 valid submissions. Spend cheap rounds here; they cost no inventory.

**Port test.** When the pipeline is working, port it to one adjacent domain. It is the only
honest measure of which parts are general. Measured on one port: reasoning stages transferred
nearly unchanged; the cost was concentrated in verdict adapters, build and slicing, and one
gate had **never run at all** in the new domain. You will not find that by reading your own
code.

**Stop conditions.** Stop a line of work when: the ceiling stage stops moving across two
rounds, or inventory drops below the batch size you need, or the measured rule cost exceeds
what new rules recover. Say which one happened.

---

## Phase 5 — Where to put the effort

From 46 rounds, the measured ranking of where value was actually won and lost:

1. **Delivery discipline** — selection, grading, filing. The largest measured loss by a wide
   margin (L-16). In most domains this half is also the one nobody else works on.
2. **Coverage of the denominator** — exhaustiveness on whatever unit 0.4 settled on. Cheap
   completeness checks caught 15 finished items that were never submitted.
3. **Interaction between two mechanisms** — defects that exist only where two correct things
   meet. These carried the top-value results and no single-axis pass can see them.
4. **Independent re-attack** — blind passes (L-15), especially the one holding no conclusion
   at all.
5. **Raw detection breadth** — last. Where mature mechanical tooling already exists in your
   domain, use it as the candidate generator and spend your own effort on 1–4.

That ordering is the loop's main transferable result. Most effort goes to 5 by instinct, and
5 is where it is worth least.
