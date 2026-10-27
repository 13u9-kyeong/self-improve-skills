# Authoring a domain layer

> The procedure. `README.md` here is the rule; this is how to satisfy it.
>
> Expect the three choices in steps 1–3 to take longer than all the writing. They are the
> job. If you find yourself writing lens questions before you have a denominator, you are
> building a checklist.

```bash
python3 scripts/new_domain.py --name <domain>     # scaffolds the seven components
```

---

## Step 1 — the denominator

**You are looking for:** a set of things that must each receive a disposition, which is
enumerable, countable, and whose completion a gate can check.

**The trap:** confusing the denominator with the data you have. "Our 10,000 samples", "the
captures from last month", "the files in scope" — these are *samples*. A sample tells you
nothing about coverage, so a round measured against one cannot be compared to the next
round, and coverage becomes an opinion.

**The move that almost always works: a product of two enumerable sets.**

```
every <unit of input the work receives>  ×  every <thing the output must get right>
```

Both sides are usually enumerable even when the raw material is not, because both are
*declared somewhere* — a dispatch table, a schema, a published taxonomy, a state diagram, a
capability list, a registration call.

**Test your candidate against four questions:**

1. Can you write the number down today? (If not, it is not enumerable.)
2. Does the number stay fixed when you change tools? (If a better tool shrinks it, it was a
   tool's output, not a denominator.)
3. Can a gate check completion mechanically? (If completion needs judgement, rounds are not
   comparable.)
4. Does an empty denominator exit CANNOT rather than PASS? (If "0 units, all dispositioned"
   reads as success, you have built the kit's most-repeated defect into your layer.)

**Record the give-up bucket.** Every mechanical analysis fails somewhere — an unresolved
indirection, an encrypted region, a packed section, a field whose meaning nobody knows, a
log source that was not collecting. Those belong **in** the denominator as their own bucket
with their own completion gate. A give-up recorded as a clear is indistinguishable,
downstream, from a location someone examined.

Write the result into `SURFACE.md` with: the chosen denominator, how each side is enumerated,
what "complete" means, the `surface.json` shape, and the gate's exit codes.

---

## Step 2 — the verdict

**You are looking for:** a mechanism that says "this is real" without your pipeline's
opinion in it.

The ladder is domain-invariant. Only the rungs change:

```
tier 1  a mechanism runs and reports        no interpretation at all
tier 2  you exercise the real thing         you run it, every time
tier 3  compare against a known answer      proves correspondence, not mechanism
tier 4  a model or human judgement          NOT a verdict
```

Instances of tier 1 across domains: a regression test that fails before and passes after ·
an assertion or checker firing · an exact match by script against a posted value · a
forecast resolved against the realised outcome · a synthesised message the real
implementation accepts.

**Do this per lens family, not once per domain.** The usual outcome is that some families
get tier 1 and others only tier 3, and that split is the most important fact about your
round costs and your blind spots. Typically one family is decided by a test (tier 1) while
another can only be compared against a known answer (tier 3); those two families need
different budgets and produce differently trustworthy findings.

**A family whose best verdict is tier 4 does not file findings.** It files leads, in their
own lane, and they never enter the delivered axis. Do not delete the family — a lane that
*admits* rather than rejects recovered 8 items in one measured round, while silently
dropping them cost a round outright.

**If the verdict is probabilistic** — a race, a sandbox that sometimes fails to trigger, a
detection with a false-negative rate — fix `n` before the run and report `k/n`. A single
success is not "reproduces". A failure at small `n` is not "does not reproduce".

**Measure the wall-clock.** It sets round cost more than anything else, and if it is minutes
the verdict becomes an asynchronous job: a worker that waits on one will hit the watchdog.

Write the result into `VERDICTS.md`: the ladder with your rungs, the per-family table, the
probabilistic protocol if you need one, and the cost consequences.

---

## Step 3 — the key

**You are looking for:** something sealed by a mechanism outside your control.

Five classes, domain-invariant:

| Class | Sealed by | Inventory | Typical instance |
|---|---|---|---|
| change history | time | unlimited | a fix/patch and its parent state |
| a judged or labelled set | another party | tens–thousands | published labels, competition verdicts, adjudicated datasets |
| private history | the client | tens | their own past findings plus what fixed them |
| injection | you | unlimited | mutation or deliberate insertion — **a floor on recall only** |
| a set you curated | **nobody** | — | not a key |

**Prefer the first row wherever it exists**, because inventory sets your iteration rate and
nothing else does (L-5). The first row is also systematically overlooked: anything with a
version history has one, since the state before a change is a live instance of whatever the
change addressed.

**Then ask the question that has no procedural answer: is the key in the model's training
data?** Mitigation is target *selection*, never procedure:

- prefer keys sealed by time, dated after your cutoff;
- record the cutoff you relied on, per round, in `PREREGISTRATION.md`;
- keep pre-cutoff results as a separate series and never average them with post-cutoff ones.

Write the result into `PHASE0-<instance>.md` — one file per sub-instance, since the key is
usually the only thing that differs between them. Fill it in honestly, including the gates
that fail.

---

## Step 3b — the comparison

**You are looking for:** a rule, fixed before round 1, that says whether one answer of the
agent matches the key's entry for the same problem — and a short list of reasons a problem
can fail.

The verdict (step 2) says whether an output is *real*; the comparison says whether it is
*the answer the key holds*. In most domains with a key of past reports or answer sheets the
comparison is the scorer, and without it someone decides success by hand.

1. **Name the unit.** One problem, one answer, one key entry. If a past report holds many
   items, the unit is usually the item, not the report.
2. **One rule per answer field**, the strictest the domain honestly allows: `exact`, `text`,
   `number` with a tolerance, `set`, or `judge`. Every loosening is a place a wrong answer
   passes. A field that only a judge can decide is tier 4; if most fields are `judge`, the
   loop measures agreement with a judge and `PHASE0` must say so.
3. **Five to eight failure classes**, mutually exclusive and about the pipeline (input read
   wrong, rule unknown, reasoning wrong, instructions not followed, right answer in the
   wrong form …). These are what `failures.py` counts across rounds, so a vague list makes
   every later round unreadable.

Write it into `COMPARE.md` and `compare:` in `loop.config.yaml`. The tools are
`scripts/compare.py` (answers vs key → `scored.json`) and `scripts/failures.py` (every
failure gets a class, a stage and a cause).

---

## Step 4 — stages

Take the generic pipeline and ask, per stage, whether this domain needs it. Then ask what
this domain needs that the generic pipeline does not have. The second question is where the
value is: in the layers this kit was built from, it produced an environment stage and an intake
stage, and both turned out to be load-bearing.

Two stages worth checking for in any domain:

- **An environment stage.** If getting the subject to build, run, decode, replay or execute
  is a frequent total blocker, that is a stage with its own output and its own gate — not an
  informal setup step. Its **gap list** caps the round's recall.
- **An intake stage.** If mature mechanical tooling already exists in your domain, it is
  almost certainly better at detection than reasoning is, and worse at triage. Let it
  generate candidates; spend reasoning on triage and on what it structurally cannot see.
  The measured effort ranking puts raw detection breadth **last** of five.

Every stage gets seven fields (`../STAGES.md`): agent, input, output, denominator,
must-not-see, verdict, verify. A field whose value is an adjective is not enforceable —
denominators are numbers, must-not-see lists name files, verify steps are commands.

---

## Step 5 — lens families

A lens is a fixed set of **directed questions** pushed across the whole assigned surface.
Four properties, domain-invariant:

1. **It has a direction.** Not "is this X?" but "what is X, and who established it?" A
   question answerable with "yes, fine" will be.
2. **It demands an answer per location.** Every cell gets a citation or an explicit `n/a`
   with a reason.
3. **It is refutable.** `REFUTED` with a filed defect, or `STANDS` with a ledger naming what
   was opened, what closed it, and **what was not opened**.
4. **It is about meaning, not form.** Measured: checking that two quantities shared a *unit*
   had zero discriminative power — three readers closed the same defective line clean on
   that basis.

**Write "what never counts as a clear" for your domain.** Three entries are
domain-invariant and you should copy them:

- documentation agrees with the subject (if the documentation describes the defect, agreement
  is a false clear — this framing cost a judged item);
- a test exists for this path (a test asserts expected behaviour, not safety);
- the form matches (property 4).

Then add yours. Each entry should be something you measured closing a real item.

**Seed families from an existing taxonomy where one exists** — it saves inventing an
ontology and it makes coverage legible to people outside the loop. Then let rounds reshape
it: each measured miss adds the question that would have caught it, with a fixture, in the
same commit (L-10). A family whose questions were never measured against a miss is a
checklist.

---

## Step 6 — config, then validate

Fill `loop.config.yaml`: currency with both axes named, stages in order, gates with
`cannot_args` and ideally `fail_args`, the card vocabulary allow-list, sealed inventory.

```bash
python3 scripts/new_domain.py --check domains/<name>
python3 harness/conformance/test_exit_codes.py --config domains/<name>/loop.config.yaml
```

The second will report your gates as missing until you build them. That is correct — it
reports them as `MISS`/`UNGUARDED`, never as passing.

---

## The order matters

```
denominator -> verdict -> key -> stages -> lenses -> config
```

Backwards is the common failure. Lens questions written before a denominator produce a
checklist with no coverage claim. Stages designed before a verdict produce a pipeline whose
output nothing can adjudicate. A key chosen last means discovering in round 4 that nothing
can be measured.

And the honest stopping point: **if step 3 fails and no substitute exists, stop.** Write the
layer with the no-key program (`../PHASE0.md`, "When 0.1 fails", has the substitutes) and say plainly what it
cannot tell you. A layer that reports recall without a key is making a claim anyone can
puncture by asking what it was measured against.
