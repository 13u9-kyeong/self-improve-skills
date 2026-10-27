# Stages — <domain>

> Concrete instantiation of `../../STAGES.md`. Seven fields per stage.

## Pipeline

```
[0] <>
[1] <>
...
```

## [<id>] <name>

**agent** `.claude/agents/<name>.md`
**input** <exactly what it is given, by path or shape>
**output** <exactly one artifact, by path>
**denominator** <what complete means here, as a number the orchestrator holds>
**must-not-see** <what it is forbidden to be shown, and why>
**verdict** <what this stage may decide, and what it may not>
**verify** <the command the orchestrator runs to check this stage's self-report>

<Repeat per stage. A field whose value is an adjective is not enforceable: denominators are
numbers, must-not-see lists name files, verify steps are commands.>

## Scoring agents (every round)

Use `../../templates/agents/{failure-analyst,answer-judge}.md`. Domain notes:

- **failure-analyst** — <where this domain's per-problem artifacts live, in stage order>
- **answer-judge** — <only if COMPARE.md has `judge` fields: what may legitimately vary>

## Adversarial passes (optional)

Only if a stage above drops or accepts candidates before delivery (a filter, a triage).
Otherwise delete this section and say why in one line.

Use `../../templates/agents/{refuter,blind-rereader}.md`. Domain notes:

- **refute** — <which drop/accept decision it attacks; a prose refutation of a prose clear is
  two opinions>
- **blind re-read** — <locations only; also the cheapest citation-integrity check>

## Retired

<Move stages here when they stop running, with the round and the reason. A stage that
silently stops is indistinguishable from one that ran and found nothing.>
