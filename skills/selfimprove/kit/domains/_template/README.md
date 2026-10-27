# Domain layer — <domain>

> One-line statement of what this domain's work actually is.

## What changes from the generic kit, and what does not

List only the structural differences. Three to find:

- **The denominator** — <what replaces "every unit of source">
- **<the second structural difference>**
- **<the third>**

What does not change: the gate exit-code rule, the scoring agents, attrition accounting, the
rule ledger, mechanical verification of self-reports, preregistration and amendments.

## Sub-instances

| | <instance A> | <instance B> |
|---|---|---|
| Worksheet | `PHASE0-<a>.md` | `PHASE0-<b>.md` |
| Key | <class, sealed by what> | <class, or **none**> |
| Inventory | <count or "unlimited"> | <count> |
| `delivered` means | <the hardest the destination offers> | <> |
| Best verdict | <tier + mechanism> | <> |
| Main hazard | <> | <> |

Start with the instance whose gate 0.1 passes outright. Iteration rate is set by sealed
inventory and nothing else.

## Files

| Path | What it is |
|---|---|
| `PHASE0-*.md` | filled applicability worksheets, one per sub-instance |
| `SURFACE.md` | the denominator |
| `VERDICTS.md` | verdict tiers per lens family |
| `COMPARE.md` | answer-vs-key rules per field, and the failure classes |
| `STAGES.md` | the pipeline, 7 fields per stage |
| `loop.config.yaml` | machine-readable form of the above |
| `lenses/*.md` | directed question families |

## Stages with no analogue in the generic pipeline

<Name them and say why they are load-bearing. If there are none, say so — but check for an
environment stage and an intake stage first (`../AUTHORING.md` step 4).>
