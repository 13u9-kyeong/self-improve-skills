# Domain layers

> The kit one level up is domain-free: it says how a measured loop works, never what the
> work is. A **domain layer** instantiates it for one kind of work.
>
> `domains/` holds **your** layers — the ones `/selfimprove` builds with you. Bug fixing,
> test generation, document extraction, forecasting, spec conformance — each is its own
> layer, and the layer specification below is the same for all of them.

---

## The layer specification

Seven components. A layer missing any one of them cannot run a round, and the missing one is
always the same shape: something unmeasurable left to the agent's judgement.

| Component | Answers | Validated by |
|---|---|---|
| `PHASE0-<instance>.md` | can the loop run here at all? | three hard gates |
| `SURFACE.md` | what is the **denominator**? | a gate that can count it |
| `VERDICTS.md` | what says "this is real" without our opinion? | the tier ladder |
| `COMPARE.md` | how is one answer compared with the key, and what is a failure called? | `scripts/compare.py`, `scripts/failures.py` |
| `STAGES.md` | which stages, with what specifications? | 7 fields each |
| `lenses/` | what directed questions get pushed across the surface? | 4 properties each |
| `loop.config.yaml` | the above, machine-readable | every tool reads it |

A layer may have several `PHASE0-*.md` files — one per sub-instance, because the *key*
usually differs between them even when everything else is shared (for example, one instance
with a sealed key and one without).

---

## The three choices that are the whole job

Authoring a layer is mostly three decisions. `AUTHORING.md` is the procedure; this is the
shape.

**1. The denominator.** Something enumerable, countable and complete-able. Not the data you
happen to have — *the space of things that must each receive a disposition.*

**2. The verdict.** Something that says "real" with no interpretation. The ladder is
domain-invariant; only its rungs change.

**3. The key.** Something sealed by a mechanism outside your control. Five classes, all
domain-invariant.

Everything else in a layer follows from those three.

---

## Worked across domains

The same three choices, in five domains. Written out because the generality claim is only
worth anything if it survives contact with specifics.

| Domain | Denominator (must each get a disposition) | Best verdict | Key, sealed by |
|---|---|---|---|
| **Bug fixing** | every reported issue × every module the codebase has | the fix's regression test fails before and passes after, rest of the suite green | fix history, sealed by time (the parent commit of each fix) |
| **Test generation** | every public function × every documented behaviour | the generated test fails on the buggy revision and passes on the fixed one | fix history, sealed by time |
| **Document extraction** | every schema field × every document | exact match by script against the value another party posted | entries posted after your cutoff by someone outside the pipeline |
| **Forecasting** | every question × every resolution date | resolution against the realised outcome | questions that resolve after the run — sealed by time |
| **Spec conformance** | every message type × every field × every state transition | a synthesised message the real implementation accepts | a later-published specification, or a second independent implementation |

Note what the columns have in common: every denominator is a **product of two enumerable
sets**, every verdict is a **mechanism that runs**, and every key is sealed by **time or by
another party**. A layer whose three answers do not look like that has usually substituted a
sample for a denominator, an opinion for a verdict, or a curated set for a key.

---

## What ships

| Path | Domain | Sub-instances |
|---|---|---|
| `_template/` | skeleton the scaffold copies | — |

Normally you do not author a layer by hand: `/selfimprove "<goal>"` interviews you and
builds it. By hand: `python3 scripts/new_domain.py --name <domain>`.

---

## What a layer must NOT do

- **Redefine the loop rules.** L-1 … L-16 are above the layer. A layer that needs a rule
  relaxed has found either a real exception worth writing into `CLAUDE.md` with its
  measurement, or a reason to change the layer.
- **Replace the key with a proxy.** If gate 0.1 fails, the layer says so and runs the no-key
  program. A layer that invents a score where no key exists is the one failure this whole
  kit exists to prevent.
- **Let a tool define the denominator.** Tooling prioritises cells inside the denominator;
  it never sets its edges. A denominator that shrinks when a tool is upgraded was never a
  denominator.
- **Carry proper nouns into `lenses/` or `references/learned/`.** The card linter enforces
  this (L-11). Lens questions name structures, never targets.
- **Assume the generic kit's examples transfer.** The measurements quoted in `CLAUDE.md` come
  from one domain. Their *rules* transfer; their *numbers* are provenance. L-16 is the
  explicit case: its prohibitions hold wherever payoff is heavy-tailed, its correlations
  were measured somewhere with duplicate groups and most domains have none.

---

## Checking a layer is complete

```bash
python3 scripts/new_domain.py --check domains/<name>
```

It verifies the seven components exist, the config parses, every stage declares the seven
fields, every gate has `cannot_args`, the comparison rules and failure classes are defined,
and every lens family has questions. It does **not**
verify the three choices are good — that is `PHASE0-<instance>.md`, and no tool can do it
for you.

It exits 2 when a layer directory is empty rather than reporting it clean, for the same
reason everything else in this kit does.
