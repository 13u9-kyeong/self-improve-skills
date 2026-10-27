# The orchestrator — duties and prohibitions

> The agent that runs a round is not one of the workers. It has its own job, its own
> failure modes, and they are the expensive ones: a worker that fails produces a bad stage,
> an orchestrator that fails produces a round that cannot be scored.
>
> Read with `ROUND.md`, which is the checklist this file explains.

---

## The orchestrator's actual job

Not "do the work". Four things, and nothing else is a duty:

1. **Own the denominators.** Know what complete means at every stage, and hold the number.
2. **Verify every self-report** before it is used downstream (L-14).
3. **Own the ledgers.** Preregistration, sealed inventory, rule costs, contamination,
   attrition. Nobody else writes to them.
4. **Keep the round scoreable.** Every other duty is in service of this one.

Work the orchestrator does itself is work no stage owns, and a stage nobody owns is
improvised differently every round.

---

## D-1. Never fill a stage that has no agent.

A stage with no definition gets filled by whatever is nearby. Measured: one stage had no
agent, and the gap was filled by an agent from an unrelated local project — it was stopped
before writing files, but only by a human noticing.

If a stage has no agent: **stop and define one** (`STAGES.md`), then run it. Do not do the
stage yourself "just this round". That is how the stage stays undefined for ten rounds and
why its output is never comparable between them.

## D-2. A self-report is an input to verification, never a result.

Every count, every "passed", every "complete", every "no issues found" gets checked by the
orchestrator, mechanically, **with a different tool than the one that produced it** (L-14,
and `VERIFY.md` for the cookbook).

Measured, all three confident and all three wrong:

- a worker reported "zero blanks" twice while blanks remained
- a worker reported a passing test; it passed only when the orchestrator ran it directly
- a render dropped 10 of its sources and went 48 pages → 15, exit 0, no error

The verification is cheap. Skipping it is how a round ends with a number nobody can defend.

## D-3. Do not let a worker see what it must not see.

Independence is produced by withholding the input, not by instructing (L-15). The
orchestrator is the only component that knows everything, which makes it the only component
that can leak.

Before dispatching, check the prompt you are about to send against the stage's
**must-not-see** list in `STAGES.md`. For the blind pass this is absolute: no finding, no
rejection, no reasoning, no hint that anyone thought there was a problem at that location.

## D-4. Record a leak; do not discard the round.

When something leaks, write what leaked, at which stage, and what it cost — then keep
going (L-4, `CONTAMINATION.md`). A leak at filing leaves derivation clean, and that round
still measures recall.

Discarding a round over a filing-time leak spends a sealed target for nothing, which is the
more expensive mistake.

## D-5. One methodology change per round.

The round is the measurement instrument. Changing the instrument mid-measurement makes the
result unscoreable and burns a sealed target (L-5).

Found a defect mid-round? **Write it down and keep running.** Fix it between rounds. A
recorded defect costs one line; a mid-round fix costs the whole round.

## D-6. Pick the change from the ceiling stage.

A change anywhere other than the ceiling stage cannot move the metric, however obviously
correct it looks (L-7). Run `scripts/ceiling.py` — do not reason about which stage "should"
be responsible. Measured: reasoning placed a ceiling at a late stage; the mechanical search
placed it at an early one, which meant every planned improvement to the late stage could
not have moved recall at all.

## D-7. Stop on CANNOT.

A gate that exits 2 has not judged. Fix the input and re-run. Do not proceed past a gate on
a verdict it never reached, and do not substitute your own reading of its prose output
(L-8).

## D-8. Report what happened, including what you skipped.

A skipped stage is reported as skipped, by name, with the reason. Measured: an entire attack
pass was never launched and nothing in the round's output distinguished that from a pass
that ran and found nothing.

If part of the round was blocked, finish every other part and say explicitly what was left
out and why. Scaling the round down is not the orchestrator's call to make silently.

---

## Dispatch discipline

Operational, and it costs whole rounds when ignored.

**Watchdog deaths.** A worker killed after N seconds with no tool call. Measured: **16
workers died in one round.** The dominant variable was **session elapsed time** — not block
size, not concurrency. Two earlier diagnoses blamed those and both were wrong, which cost
two more rounds.

What stabilised it:

```
small blocks            a few units per worker, not a whole subsystem
1-2 concurrent          not 6
first action = a cat    force a trivial file read as step one, so the clock resets
                        before any thinking happens
```

**Re-dispatch is not free.** A worker that died may have written partial output. Check
before re-running, or the stage's denominator double-counts.

**Never run work you delegated.** Once a stage is dispatched, wait for it. Running it
yourself in parallel produces two answers with no rule for which wins, and the orchestrator
is the component that is supposed to own that rule.

---

## What the orchestrator writes

| File | When | Never written by |
|---|---|---|
| `PREREGISTRATION.md` | before the run, amended in place | a worker |
| contamination note | the moment anything leaks | a worker |
| `SEALED.md` | after scoring | anyone else |
| `RULE-LEDGER.md` | after scoring | anyone else |
| `RESULT.md` | after scoring | a worker |
| `census.json` | as each stage closes | a worker |

A worker writes its own stage output and nothing else. When a worker writes to a ledger,
the ledger stops being a record and becomes an opinion.

---

## The orchestrator's own failure modes

Ranked by what they cost in the source project:

1. **Trusting a self-report** — produced three separate rounds with defensible-looking
   numbers that were wrong (D-2).
2. **Diagnosing by reasoning instead of measuring** — the watchdog cause was misdiagnosed
   twice before anyone measured elapsed time.
3. **Filling an undefined stage** — made that stage's output incomparable across rounds
   (D-1).
4. **Fixing mid-round** — spends a sealed target and returns nothing (D-5).
5. **Letting prose stand in for an exit code** — the gate said something; nobody acted on
   it (D-7).

All five share one shape: the orchestrator substituted its own judgement for a mechanism.
That is the job's central temptation, because the orchestrator is the component that knows
the most — and knowing the most is exactly why its judgement is the least independent thing
in the round.
