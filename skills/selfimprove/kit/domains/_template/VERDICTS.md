# Verdict adapters — <domain>

## The ladder

```
tier 1  <the mechanism that runs and reports, in this domain>
tier 2  <exercising the real subject; you run it, every time>
tier 3  <comparison against a known answer>
tier 4  a model or human judgement        NOT a verdict
```

## Per lens family

| Lens family | Best available verdict | Consequence |
|---|---|---|
| | | |

A family whose best verdict is tier 4 files **leads**, in their own lane, never findings.
Do not delete the family — a lane that admits rather than rejects is measurably worth more
than one that silently drops.

## What a tier-1 verdict must contain

```
the setup      <toolchain / environment / configuration / version>
the input      <the exact stimulus, as an artifact>
the output     <the mechanism's report, verbatim, not summarised>
the mapping    <which part of that report corresponds to the claimed mechanism>
```

The last field is the one that gets skipped and the one that catches false positives.

## Probabilistic verdicts

<Delete if this domain has none.>

```
attempts       n, fixed before the run, not stopped early on success
successes      k
first success  which attempt
conditions     <what affects the rate>
```

Report `k/n`. A single success is not "reproduces".

## Tier-2 conditions

1. It exercises the real subject, not a reimplementation.
2. It asserts impact, not a symptom.
3. It starts from a state the claimed actor can actually reach.
4. The verdict is what the runner printed, pasted.

"Does not reproduce" is a result.

## Cost

```
<measured wall-clock per verdict, per tier>
```

If minutes: verdicts are asynchronous jobs, not steps inside a worker's turn. Budget `n`
per round before the round, or the round contains an unrecorded selection step.

## The environment is a stage

<If getting the subject to build / run / decode / execute is a frequent blocker, say so
here and give it stage [0] in STAGES.md with its own gap list. The gap list caps recall.>
