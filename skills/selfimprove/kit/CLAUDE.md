# The Self-Improvement Loop — standing rules (L-1 … L-16)

> Drop this file at the root of any project where an agent pipeline is supposed to get
> measurably better over time. It holds the operating rules for the loop, not for the
> domain: nothing below mentions what is being audited, found, graded or built.
>
> These rules were extracted from 46 scored rounds of one pipeline. Each carries the
> measurement that produced it, because a rule without its cost attached is the first
> thing a future round talks itself out of.

---

## The invariant

A pipeline improves only when a round can be **wrong in a way you cannot argue with**.
Everything below exists to protect that property. When a rule here is inconvenient, it is
usually protecting the one channel that tells you you were wrong.

Three things make a round scoreable. Missing any one of them means you are not running
this loop, you are just iterating:

1. **A key you could not see while producing the output.**
2. **A scoring function denominated in the domain's own currency**, not a proxy you chose.
3. **A written record, made before the run, of what would count against you.**

---

## Measurement

### L-1. A round scores against a key you could not see.
Not a key you *tried not to look at*. One that was sealed, by a mechanism outside your
control, before the run started. A held-out set you curated yourself is not a key; you
chose it knowing what your pipeline does.

If no such key exists for a domain, the loop does not run there. Say so instead of
substituting self-assessment. (Substitutes that are *not* keys: your own prior output,
another model's opinion, an LLM judge you wrote, a metric you defined.)

### L-2. Score in the domain's currency, not a proxy.
Counting is the default proxy and it is the one that hides the most. Measured: a round
reported recall 9/13 against the judged set and had **2** valid submissions — a 78% loss
that the count metric showed as 69% success.

Where the domain has money, rank, or a payout formula, reproduce that formula and score
with it. Where it has none, score two numbers side by side and never collapse them: what
you found, and what survived to delivery.

### L-3. Preregister, and amend in writing.
Before the run, write `PREREGISTRATION.md` fixing: the order targets will be taken, the
definition of success (in *their* terms, not yours), the conditions under which the result
counts against you, and the reporting rules.

Changes are **numbered amendments appended to the same file**, each stating plainly whether
it was written before or after seeing results:

```
# Amendment 4 — scorer replaced, retroactively applied (written AFTER seeing the rank)
# Amendment 5 — target chosen by a human, not the rule (written BEFORE the run)
```

An amendment written after seeing results is not misconduct. Hiding *when* it was written
is. The honest trail is what makes the whole series readable later; nine amendments with
honest timestamps are worth more than a clean file nobody believes.

### L-4. Contamination is judged per stage, not per round.
Seeing part of the answer at delivery time is not the same as seeing it while deriving.
Judge each stage separately: **derivation / promotion / filing**. A leak at filing leaves
derivation clean, and that round still measures recall.

Judge it **mechanically, from the transcript** — search the actual prompts for the leaked
terms. Do not judge it from recall; your memory of what you knew when is the least reliable
input available. Measured: a round was first graded 3/5 on a recalled impression, then
re-graded 4/6 after searching all 12 agent prompts and finding zero leaked terms in any.

Where a leak forces a judgement call, write the cost of the call down next to it.

### L-5. The sealed key is a consumable. Budget it.
Each sealed target is spent the moment you score against it, and a methodology change
spends one. This is the loop's binding constraint and almost nobody plans for it.

Count your inventory before starting. Spend **one per methodology change**, never one per
idea. If inventory is under ~10, batch changes into fewer, larger rounds; if a domain
offers effectively unlimited sealed targets (a project with a long public fix history,
where the parent commit of any fix is a live instance), prefer it — your iteration rate is
set by this number and nothing else.

### L-6. Attribute every loss to a stage and a cause.
"We scored 60%" is not a measurement, it is a mood. The unit is:

```
<item> died at <stage> because <cause>, and that cost <amount in the domain's currency>
```

Measured, one round: low-tier misfiling 1,586.30 + gate-held 2,354.44 = **3,941** lost from a
round that otherwise looked like a success. Neither number is visible in a recall figure.

Where the key holds one expected answer per problem (past reports, answer sheets), success
is decided by **rule, not by eye**: `scripts/compare.py` compares each answer with its key
entry using field rules fixed before the run, and `scripts/failures.py` refuses to let the
round be reported until every failed problem carries a failure class, a stage and a cause.
"Wrong" is a symptom; the class is the reason.

### L-7. Find the ceiling stage before optimizing anything.
A metric has exactly one stage where its ceiling is set. Work anywhere else cannot move it.

Verify this mechanically, not by reasoning: search every item the pipeline produced for the
mechanism of a missed item. Measured: the recall ceiling sat at stage `[4]`, not `[6]` — a
search of all 27 findings found neither missed mechanism anywhere, which proved no amount of
`[6]` work could raise recall. `[6]` still moved delivered value 9,132 → 13,073 on an
unchanged finding set. **Both facts are useful and they are different facts.** Know which
one you are buying before you spend a round on it.

---

## Gates

### L-8. Gates fail closed, and the exit code is the rule.
A gate that prints a problem and exits 0 is the single most repeated defect in this loop's
history — **eight occurrences, each patched individually, none generalized** until the
convention was written down. Prose nobody reads plus an exit code that says "fine" is
indistinguishable from a clean result.

Every gate obeys one rule:

```
0  PASS    judged, and it passed
1  FAIL    judged, and it failed
2  CANNOT  could not judge — unparseable input, empty input set, missing tool.
           NOT a pass. The caller stops.
3  USAGE   the invocation was wrong
```

Specifically:

- **A crash is not a verdict.** Three gates died with a parser traceback and exited 1, the
  same code a judged rejection exits with. Wrap every input read so unreadable input exits
  CANNOT.
- **An empty input set is not a pass.** It is the shape that reads most like success: zero
  flagged, zero violations, zero withheld. Two gates examined nothing and exited 0.
- **An intermediate verdict blocks.** A gate state meaning "a human should look" that exits
  0 is a gate that does not exist. Make it exit 1 and clear it **on the record**:
  `--accept-review <id> --accept-reason '<why>'`. A waiver written down is an audit trail;
  a waiver that is the default is a disabled check.
- **Magic thresholds are gaps.** A parse-failure check guarded by `len(text) > 400` passed
  every 399-character document as clean.

### L-9. One conformance test asserts the rule across every gate.
Per-gate tests catch the gate you were thinking about. A single test that enumerates **all**
gates and asserts the rule on each catches the gate you were not thinking about —
including one added six months from now by someone who never read this file.

Three axes, all three required: unreadable input → CANNOT; missing required argument → not a
verdict; readable input containing a real violation → FAIL. That last axis is what notices a
gate that quietly stopped checking.

---

## Rules about rules

### L-10. Every measured loss becomes a card **and** a mechanical check.
A card alone is a note. A check alone has no reason attached and gets deleted by whoever
finds it inconvenient. Produce both, in the same commit, or the lesson does not survive
three rounds.

The check must fail on the original defect. Verify that by **sabotage**: reintroduce the bug
and confirm the check goes red. An untested check is indistinguishable from a comment.

### L-11. Cards are domain-general, and a linter enforces it.
A card naming a specific target teaches nothing about the next one. Ban proper nouns
mechanically with an allow-list of vocabulary any *different* target on the same runtime
would use identically.

The linter will reject things you think are generic — that is it working. When it rejects a
term, the fix is to restate the lesson as a **structural condition**, which is almost always
the better card anyway. Measured: a rule written as an interface callback name was rejected
and had to be rewritten as the structural condition it was really about.

Card shape that has survived: the measurement and its N up front → what the numbers say →
**what was tried and removed, with its score** → `## Therefore`, as prohibitions specific
enough to obey. Recording the removed tools is what stops the next round rebuilding them.

### L-12. Measure what each rule costs.
Rules accumulate monotonically and quietly destroy recall. Keep a ledger of what each one
closes.

Measured: four scope rules each closed ~45% of judged findings and **co-fired**, so their
individual costs did not add up to anything like their joint cost. One rule's cost was 0.
You cannot know which is which without the ledger, and a rule whose cost nobody measured is
a rule nobody can argue against.

Corollary: count a rule's closures **at the smallest unit the rule actually applies to**, not
per item. Re-counting one rule per function instead of per finding recovered the single
highest-value item in a round.

### L-13. The frozen set is off-limits; the learned set accumulates.
Split standing references in two. `frozen/` holds what must not drift — output format,
verification rules, the loop rules. `learned/` holds what each round adds. A round may
write only to `learned/`. Without the split, a bad round rewrites the definition of a good
one.

---

## Trust

### L-14. Self-reports are not results.
Every claim an agent makes about its own work gets verified mechanically before it is used.
Not because agents lie — because they report intent as outcome.

Measured: a reader reported "zero blanks" twice when blanks remained; a reader reported a
passing test, which passed only when run directly; a report lost 10 of its sources and
dropped 48 pages → 15 without any error. All three self-reports were confident.

Cheap verifications that each caught a real failure: count the rows yourself; run the test
yourself; diff the artifact size against the last round; `grep -c` the rendered output.

### L-15. Independence is mechanical, not requested.
An agent told to attack a conclusion while holding the reasoning behind it will reason
outward from that frame. Asking for independence does not produce it; **withholding the
input does.**

So: the attacker gets the claim and the file paths, never the derivation. At least one pass
reads the cited locations with **no conclusion attached at all** — not the finding, not the
rejection, not the reasoning. Measured, this is the pass that produced verdicts the other
two could not.

### L-16. Convex payoff + no predictor = never triage.

**Precondition — check this before reading on.** This rule's *measurement* needs a domain
where the same item can be found by several parties and value depends on how many did. If
your domain has no duplicate or rarity notion — most upstream open-source work, most
internal assessment — **L-16 is unmeasurable there**, and you record that as a blind spot in
`PHASE0.md` rather than substituting a proxy. The prohibitions at the end still apply
wherever delivery is to a paid-per-item program or a competition; the numbers below do not transfer.

Where value *is* heavy-tailed, find out whether you can predict which of your outputs
carries it. If you cannot, **stop ranking your own output and spend the effort on
coverage.**

Measured: value correlated with the *rarity* of a hit at rho = **-0.932** and with the
*count* of hits at +0.513. Every candidate predictor of rarity scored between -0.13 and
+0.32 — including two tools built on them and removed, one of which sent its predicted
high-value cluster 5/5 into groups worth nothing. One top-rank result took 41% of a pool for
**two** items.

Therefore, in such a domain: never drop an item for being "probably redundant"; never merge
two items to look tidy; treat a mis-grading that moves an item below the reporting threshold
as a total loss of that item, not a small error. And run the cheap completeness checks —
one of them caught **15 finished items that had never been submitted at all.**

---

## Operational hazards

Not principles. Things that cost real rounds, in this loop's own measurements.

- **Watchdog deaths.** A subagent killed after N seconds with no tool call. 16 agents died
  in one round. The dominant variable was **session elapsed time**, not block size and not
  concurrency — two earlier diagnoses, both wrong. Stabilised by shrinking blocks, dropping
  to 1–2 concurrent, and forcing the first action to be a trivial file read.
- **Re-rendering wipes hand-edits.** Any hand-appended section in a generated artifact is
  lost on the next render. Either make the generator own it or stop hand-editing.
- **Path arguments that join silently.** One flag defaulting to `.` erased 10 source
  references and the output shrank by 68% with exit 0. Check output size against the last
  run as a matter of course.
- **Agents that do not exist.** A stage with no agent definition gets filled by whatever is
  nearby, including an agent from an unrelated local project. **Every stage owns a named
  agent**, or that stage is improvised differently every round.
- **Encoding/typesetting failures exit 0.** A document rendered with every glyph of body
  text missing and returned success. Verify rendered output by extracting text back out and
  counting it.

---

## When this loop does not apply

Say so rather than running it degraded:

- **No sealed key, and none constructible.** The loop cannot run. What *does* still run
  without a key: L-6 attribution, L-8/L-9 gate exit-code rule, L-12 rule ledger, L-14 verification,
  and internal attrition accounting (candidates → filed → delivered). Measured, these found
  and fixed 15 real defects with no key involved. That is a real program; it just is not
  this loop, and it cannot tell you about recall.
- **A key exists but you cannot reproduce its scoring.** Build the scorer first. Scoring with
  your own metric against someone else's key measures nothing.
- **One target, one shot.** Preregister, run, report. Do not call it a round or average it
  with anything.
