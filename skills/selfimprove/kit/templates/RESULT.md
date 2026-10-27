# <target> — result

## Result — both axes
Never collapse these into one number (L-2).

| axis | value |
|---|---|
| found | |
| delivered | |

## Comparison
Output of `scripts/compare.py`. Judged problems on their own line — they are tier 4.

| | count |
|---|---|
| success (all fields matched) | |
| — decided mechanically | |
| — decided by a judge | |
| not_attempted | |
| format | |
| extra answers (not in the key) | |

## Failure analysis
Output of `scripts/failures.py` — every failed problem has a class, a stage and a cause.

| failure class | stage | count (weighted) | cause, in one sentence about the pipeline |
|---|---|---|---|

Largest cell: <class at stage> — the first candidate for the next round's single change.

Key disputes (never dropped): <ids, and why the key looks wrong>

## Hit (n)
| item | found at stage | filed as | delivered? |
|---|---|---|---|

## Missed
Each row names a stage and a cause (L-6).

| item | died at | cause |
|---|---|---|

### <shared failure shape>
Two misses with the same cause are ONE defect in the pipeline, and that is the thing worth
a methodology change. Isolated misses are usually noise. Name the shape here.

## Nearly missed
Items that survived by luck. Treat them as misses — they are the next round's losses.

## Loss priced
| stage | cause | cost |
|---|---|---|
| | | |
| **total** | | |

## Ceiling check
Which stage sets this metric's ceiling, and how that was verified MECHANICALLY — the search
that was run, over what, and what it returned (L-7). Reasoning about which stage "should"
be responsible does not go here.

## Rule cost this round
What each standing rule closed, counted at the smallest unit the rule applies to (L-12).

| rule | closed | of which judged |
|---|---|---|

## Attrition
Output of `scripts/attrition.py`. Largest single drop, and whether it was accounted for.

## Self-reports verified
What an agent claimed, how it was checked, and whether it held (L-14).

## To carry into the next round
One methodology change, chosen from the ceiling stage.
