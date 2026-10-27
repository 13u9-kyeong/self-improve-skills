# Stage definitions

> Every stage in `loop.config.yaml` owns a named agent, declared inputs, a declared output,
> and a **must-not-see** list. A stage missing any of the four is not defined, and an
> undefined stage gets improvised differently every round (D-1).
>
> Measured: one stage had no agent definition. The gap was filled by an agent from an
> unrelated local project, caught only because a human noticed before it wrote files.

---

## The stage specification

Copy this block per stage into `STAGES.md` in your project and fill it in.

```markdown
## [<id>] <name>

**agent**        `.claude/agents/<name>.md`
**input**        <exactly what it is given, by path or shape>
**output**       <exactly one artifact, by path>
**denominator**  <what complete means here, as a number the orchestrator holds>
**must-not-see** <what it is forbidden to be shown, and why>
**verdict**      <what this stage is allowed to decide, and what it is not>
**verify**       <how the orchestrator checks this stage's self-report>
```

Each field exists because omitting it cost a round:

| Field | What its absence caused |
|---|---|
| `agent` | the stage filled by whatever was nearby |
| `input` | two rounds' outputs not comparable, because the stage was fed differently |
| `output` | hand-edits lost on the next render; nobody knew which file was authoritative |
| `denominator` | "complete" meaning whatever the worker looked at |
| `must-not-see` | the attack passes confirming the conclusion they were sent to attack |
| `verdict` | a stage re-grading what another stage owned, with no rule for which wins |
| `verify` | self-reports used downstream unchecked |

---

## Must-not-see is the load-bearing field

Independence is produced by **withholding the input**, not by instructing (L-15). Asking an
agent to be independent while handing it the reasoning produces an agent that reasons
outward from that reasoning and confirms it.

So the field is not a courtesy note. It is the list the orchestrator diffs the dispatched
prompt against before sending (D-3).

The same rule governs every agent template this kit ships. Two are part of every round's
scoring; two are optional adversarial passes:

```
failure-analyst  gets one failed problem + its artifacts.  Not scores, not other analyses.
answer-judge     gets the expected value + the answer.     Not the reasoning or the input.
refuter          gets the claim + file paths.              Not the reasoning.      (optional)
blind-rereader   gets locations ONLY.                      Not the claim, not that anyone
                                                           thought anything was wrong. (optional)
```

**The two adversarial passes are optional.** Use them only when the pipeline has a stage
that drops or accepts candidates *before* delivery — a filter, a triage, a "this one is
fine" decision. There, a wrongly dropped correct answer never reaches the comparison with
the key, and only an independent re-attack of the drop catches it a round earlier. A
pipeline that answers every problem and hands every answer over needs neither: the
comparison with the key already does their job.

The blind pass is the strictest and, measured, the one that produced verdicts the other
passes could not reach. Its definition instructs it to **declare itself void** if it finds itself
reading round artifacts — a stage that can detect its own contamination is worth more than
one that is merely told not to.

---

## Verdict scoping

A stage decides exactly one class of thing. Overlapping verdicts produce two answers with no
tie-break, and the orchestrator is supposed to own that rule rather than improvise it.

Measured failure: a grading stage re-graded items a detection stage had already accepted,
downgrading several below the reporting threshold. That converted their value to zero.
Misgrading is not a small error (L-16) — below-threshold lanes usually do not
compete for value at all.

Write the prohibition into the agent definition, not just here. The agent reads its own file.

---

## Example — a filled stage

```markdown
## [4] independent re-attack (blind)

**agent**        `.claude/agents/blind-rereader.md`
**input**        `runs/<round>/blind-locations.txt` — one `file:line` per row, no headers,
                 no commentary, generated mechanically from the cited-location set
**output**       `runs/<round>/blind-out.md` — one block per location, in input order
**denominator**  every row of blind-locations.txt. 416 rows this round; output must have
                 416 blocks including the ones where nothing was found
**must-not-see** findings, rejections, worksheets, reports, any statement that a problem
                 was suspected at any location. Reason: every other pass holds the original
                 conclusion, and that frame is the anchor their verdicts reason from
**verdict**      describes behaviour and assumptions only. No grade, no
                 recommendation, no overall conclusion — those need a frame it does not have
**verify**       `grep -c '^## ' blind-out.md` equals the input row count; spot-check 5
                 citations for existence and range; confirm no round artifact path appears
                 in its transcript
```

Note what makes it a usable definition: the denominator is a **number**, the must-not-see
list names **files**, and the verify step is a **command**. A definition whose fields are
adjectives is not enforceable.

---

## Adding a stage

1. Write the definition block above **first**, before the agent file.
2. Write the agent file. Put the prohibitions in it, not only in `STAGES.md` — the agent
   reads its own file and nothing else.
3. Add the stage to `loop.config.yaml` under `stages`, so loss can be attributed to it
   (L-6). A stage not listed there cannot be blamed, and it will absorb other stages'
   failures.
4. If the stage is a gate, add it under `gates` with `cannot_args` **and** `fail_args`, or
   the conformance test reports it `UNGUARDED` (L-9).
5. Run one round before trusting its output. A new stage's first output is a draft.

---

## Retiring a stage

Do not delete it silently. A stage that stops running must be reported as skipped by name
(D-8) — measured, an entire attack pass was never launched and nothing in the round's
output distinguished that from a pass that ran and found nothing.

Move the definition to a `## Retired` section with the round it stopped and why. The next
person to consider building it needs to know it existed and what it measured.
