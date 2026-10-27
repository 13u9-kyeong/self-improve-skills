# Comparison and failure classes — <domain>

> How one answer of the agent is compared with the key, and what a failure is called when it
> happens. Machine form: `compare:` in `loop.config.yaml`. Tool: `scripts/compare.py`, then
> `scripts/failures.py`.
>
> Write this before round 1. A comparison rule invented after seeing the answers is a scorer
> fitted to the result (L-3).

## The unit

**One problem is:** <e.g. one invoice; one bug report and its repository state; one question>

**The agent's answer for one problem is:** <the fields it must produce, with their types>

**The key's entry for one problem is:** <where it comes from — the past report, the posted
ledger entry, the merged fix — and who sealed it>

## Field rules

One row per answer field. Prefer the strictest rule the domain honestly allows; every
loosening is a place where a wrong answer can pass.

| field | rule | why this rule |
|---|---|---|
| <name> | <exact / text / number tol=… / set / judge> | <what a correct answer may vary in, and what it may not> |

`judge` fields are decided by the answer-judge agent (`templates/agents/answer-judge.md`),
which sees the expected value and the agent's value and nothing else. A judge is tier 4: it
is not a verdict in the sense of `VERDICTS.md`, and `compare.py` reports judged problems on
their own line. If most fields are `judge`, say so in `PHASE0-*.md` — the loop is measuring
agreement with a judge, not correctness.

**What counts as success for a problem:** every field matches. <If the domain needs a
weaker rule — e.g. a required subset — state it and the reason.>

## Failure classes

`compare.py` only knows symptoms (`not_attempted`, `format`, `wrong`). The classes below are
the **reasons** a failure-analyst may assign, and `failures.py` refuses a failure left at
`wrong`. Keep the list short (5–8), mutually exclusive, and about the pipeline rather than
about one problem, so the counts across rounds mean something.

| id | means | how the analyst tells it apart |
|---|---|---|
| <input_misread> | <the input was read incorrectly before any reasoning> | <the intake artifact already differs from the source> |
| <knowledge_gap> | <the rule or fact needed was not available to the agent> | <> |
| <reasoning_error> | <inputs were right, the conclusion drawn from them was wrong> | <> |
| <instruction_violation> | <the agent did not follow its stage instructions> | <> |
| <output_mapping> | <the right answer was reached but written into the wrong field or form> | <> |

Built in, always available: `not_attempted`, `format`, and `key_dispute` — the key itself
looks wrong. A key dispute is listed in `RESULT.md` and never silently dropped or "fixed".

## Weight

<Are all problems worth the same? If not, where does each problem's weight come from, and
who set it before the run?>
