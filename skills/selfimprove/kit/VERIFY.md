# Verification cookbook

> Expands L-14: **self-reports are not results.** The rule is easy to agree with and easy to
> skip, because verification feels like distrust and the report usually sounds right.
>
> It is not distrust. Workers report **intent as outcome** — what the work was supposed to
> produce, not what it produced. That is a property of describing your own work, not a
> defect of any particular agent, and the orchestrator has it too.

---

## The rule in operational form

> Every claim gets checked with a **different tool than produced it**, by the orchestrator,
> before anything downstream uses it.

"Different tool" is load-bearing. Asking the worker to double-check runs the same process
that produced the claim and returns the same answer. Measured: a worker reported "zero
blanks" **twice**, the second time after being asked to re-verify. The blanks were still
there. A `grep -c` by the orchestrator found them in one call.

---

## Cookbook

Each row below caught a real failure in the source project.

| Claim | Cheap check | What it caught |
|---|---|---|
| "all N rows complete" | count them yourself: `grep -c` the marker in the output file | a worker reporting zero blanks twice while blanks remained |
| "the test passes" | run it yourself and paste the runner's output | a reported-passing test that only passed when run directly |
| "coverage is complete" | diff the produced unit list against the enumerated denominator | a stage that silently dropped units past a row cap |
| "the report is rendered" | extract text back out of the artifact and count it | a document rendered with **every glyph of body text missing**, exit 0 |
| "n items filed" | count the files on disk, not the summary | 15 finished items that had never been submitted at all |
| "nothing found here" | check the worker actually opened the locations: are the cited lines real? | citations to lines that do not exist |
| "stage complete" | is there output for every input unit, including the boring ones? | locations skipped silently, indistinguishable from locations cleared |
| any generated artifact | compare its size against the last round's | a flag erasing 10 sources; output shrank 68%, exit 0 |

---

## The four claim types and how each fails

**1. Counts.** Fail by being the *intended* count. A worker that was asked for 40 rows
reports 40. Check: count the artifact, not the sentence about it.

**2. Verdicts** ("passes", "holds", "clean"). Fail by being the expected verdict. Check:
run the verdict mechanism yourself. If the claim is a test, this is non-negotiable — a test
nobody ran is a hypothesis.

**3. Completeness** ("all", "every", "no remaining"). Fail by being scoped to what the
worker looked at rather than what existed. Check against the **denominator**, which only the
orchestrator holds. This is why D-1 puts denominators on the orchestrator.

**4. Absences** ("nothing found", "no issues"). The hardest, because there is no artifact to
count. Check the *work*, not the conclusion: were the locations opened, are the citations
real, is there a row for every input unit including the empty ones. An absence with no
evidence of looking is indistinguishable from a stage that did not run.

---

## Verify citations, always

A citation to a line that does not exist invalidates everything else in that output, because
the reader cannot tell which other citations are real. This is cheap to check and it fails
more often than expected:

```bash
# every file:line cited in a worker's output, checked for existence and range
python3 - "$OUT" <<'PY'
import re, sys
from pathlib import Path
bad = 0
for m in re.finditer(r"([\w./-]+\.\w+):(\d+)", Path(sys.argv[1]).read_text()):
    p, n = Path(m.group(1)), int(m.group(2))
    if not p.exists():
        print(f"MISSING  {m.group(0)}"); bad += 1
    elif n > len(p.read_text(errors='replace').splitlines()):
        print(f"OUT OF RANGE  {m.group(0)}"); bad += 1
print(f"{bad} bad citation(s)")
PY
```

Measured on one round: 122 of 916 citations were out of range (13.3%) while the aggregate
looked survivable — and five of that pass's upheld conclusions rested on premises that were
false, three of them naming lines that do not exist. **Report the rate per worker, never
aggregated**: an aggregate hides which worker is unreliable, and the next stage inherits
that worker's premises whole.

---

## Verify the verifier

The gates are tools, and tools fail open (L-8). Before trusting a green gate run:

- [ ] The harness is green (`python3 harness/run_all.py`): the conformance test and every
      lesson check.
- [ ] The gate was given a **readable input containing a real violation** and exited 1.
      A gate verified only against bad input is verified against the easy half.
- [ ] The gate actually ran this round. Measured: one gate had **never run at all** in a
      domain the pipeline had been ported to, and nothing in any round's output said so.

---

## What not to do

- **Do not ask the worker to re-verify.** Same process, same answer (see above).
- **Do not accept a summary in place of an artifact.** The summary is the claim.
- **Do not verify at the end of the round.** By then the claims are load-bearing and the
  cost of finding one wrong is the whole round. Verify as each stage closes (`ROUND.md`).
- **Do not skip verification because the claim is plausible.** All three measured failures
  were plausible. That is why they survived to be measured.
