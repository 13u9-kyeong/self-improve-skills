# Rule cost ledger

Rules accumulate monotonically and quietly become the ceiling. A rule whose cost nobody
measured is a rule nobody can argue against (L-12).

## Per rule
Count closures at the **smallest unit the rule actually applies to**, not per item.
Re-counting one rule per function instead of per item recovered the highest-value item of
a round.

| rule | what it closes | closures | of which judged | measured in round |
|---|---|---|---|---|

## Co-firing
Individual costs do not add up to the joint cost. Measured once: four rules each closed
~45% of judged items and fired together. Record which rules overlap.

| rules | overlap |
|---|---|

## Zero-cost rules
Rules measured to close nothing. Keep them — they cost nothing and may bind later. Record
them so nobody re-measures.

## Review
- Last re-derived:
- Does the accumulated rule set close more than new rules recover? If yes, say so and stop
  adding.
