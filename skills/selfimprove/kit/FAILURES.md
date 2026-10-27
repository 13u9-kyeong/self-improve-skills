# Measured failure catalogue

> Not rules — `CLAUDE.md` has those. This is the reference list of how the loop actually
> failed across 46 rounds, with each failure's measured cost and the mechanism that now
> prevents it.
>
> Read it once before round 1, and again whenever a round produces a number you want to
> believe. Most of these were found *after* a round that looked fine.

---

## Class 1 — a check that reports success over nothing

The single most repeated class. **Eight occurrences**, each patched for the one gate that had
just failed, none generalized, until the exit-code rule was written down.

| Failure | Cost | Prevented by |
|---|---|---|
| Gate crashed on malformed input, exited 1 — same code as a judged rejection | caller could not tell rejection from crash | `gatelib.load_json` → exit 2 |
| Gate examined an empty input set, printed "0 flagged", exited 0 | checked nothing, read as clean | `gatelib.require_inputs` |
| Parse-failure check guarded by `len(text) > 400` | every 399-char document passed as clean | threshold removed; empty vs unparseable split |
| An intermediate "a human should look" verdict exited 0 | the check ran, flagged, and told the pipeline it was fine | verdict blocks; cleared only with a recorded reason |
| A gate had **never run at all** after a port to a new domain | unknown; nothing in any round's output said so | conformance test enumerates every gate from config |
| `--help` crashed on an unescaped `%` in an argparse string | the first command a caller types | included in the conformance sweep |

**Mechanism now:** `0 PASS / 1 FAIL / 2 CANNOT / 3 USAGE`, plus one conformance test over
**every** gate in config, with three axes — unreadable → CANNOT, missing arg → not a verdict,
real violation → FAIL. The third axis is what notices a gate that quietly stopped checking.

---

## Class 2 — a self-report used as a result

| Failure | Cost | Prevented by |
|---|---|---|
| Worker reported "zero blanks" **twice**, once after being asked to re-verify | a stage treated as complete that was not | orchestrator counts the artifact itself, different tool |
| Worker reported a passing test; it passed only when run directly | a verdict accepted that had never been produced | orchestrator runs every test and pastes the output |
| 122 of 916 citations out of range (13.3%), aggregate looked survivable | five upheld conclusions rested on false premises, three naming lines that do not exist | citation check, **reported per worker, never aggregated** |
| Render dropped 10 sources, 48 pages → 15, exit 0 | a deliverable silently gutted | artifact size diffed against the previous round |
| Document rendered with **every glyph of body text missing**, exit 0 | a shipped document with no body | text extracted back out and counted |

**Mechanism now:** `VERIFY.md` cookbook. All five self-reports were confident and plausible —
that is why they survived long enough to be measured.

---

## Class 3 — the measurement instrument measured the wrong thing

| Failure | Cost | Prevented by |
|---|---|---|
| Counted recall instead of delivered value | a 78% loss (9/13 found, 2 delivered) displayed as 69% success | two axes, never collapsed |
| Precision computed from the pipeline's own report | the report held only what passed the gates, so it measured the gates | precision computed over everything produced, including drops |
| Scorer matched a platform's **1/100 display scale** | wrong by two orders of magnitude for three rounds | scorer verified against a published result first |
| Rank compared across instances | meaningless: mean submitters per item were 8.97 / 0.92 / 0.67 | rank comparable only within one instance |
| Matched on title instead of mechanism | a counted hit that shared only a title with the key's item | match on mechanism and location |
| Ceiling located by reasoning, not search | planned work on a late stage could not have moved recall at all | `scripts/ceiling.py`, mechanical search |

---

## Class 4 — value destroyed after the item was already found

The loop's largest cumulative loss, and the half most projects do not work on.

| Failure | Cost | Prevented by |
|---|---|---|
| Items graded below the reporting threshold | below-threshold lanes do not compete for value; the item is worth zero | a lane that **admits** rather than rejects; 8 items recovered in one round |
| Items held by a gate and never released | 2,354 in one round | gate-held items enumerated before delivery |
| Items misfiled into the wrong lane | 1,586 in one round | filing census |
| 15 finished items **never submitted at all** | unmeasured, recovered | cheap completeness check against the denominator |
| A grading stage re-graded what a detection stage had accepted | several items pushed below threshold | verdict scoping per stage (`STAGES.md`) |
| Items merged to look tidy | a downstream grader splits; a self-merge removes their ability to | never merge (L-16) |

Priced on one round: misfiling 1,586.30 + gate-held 2,354.44 = **3,941** lost from a round
that otherwise looked like a success. Neither figure appears in a recall number.

---

## Class 5 — the round stopped being a measurement

| Failure | Cost | Prevented by |
|---|---|---|
| Key sat inside the target clone | round's isolation void | key outside the tree; target `chmod -R a-w` |
| Blind workers wrote into the shared target against instruction | contaminated the shared input for later stages | permissions, not instructions |
| Contamination judged from recall, conservatively | a real result discarded (graded 3/5, actually 4/6) | judged mechanically by searching dispatched prompts |
| Fixed a defect mid-round | round unscoreable, sealed target spent for nothing | record it, fix between rounds (D-5) |
| An attack pass never launched; output identical to "ran, found nothing" | unknown recall loss | skipped stages reported by name (D-8) |

---

## Class 6 — operational

| Failure | Cost | Prevented by |
|---|---|---|
| **16 workers** killed by a watchdog in one round | the round nearly lost; two misdiagnoses cost two more | small blocks, 1–2 concurrent, first action forced to a trivial read |
| Watchdog cause blamed on block size, then on concurrency | both wrong; dominant variable was **session elapsed time** | measure before diagnosing |
| Re-rendering wiped hand-appended sections | sections silently lost | the generator owns every section, or nobody hand-edits |
| A path flag defaulting to `.` joined wrongly | erased 10 sources, output shrank 68%, exit 0 | output size diffed every run |
| A stage with no agent filled by an unrelated project's agent | caught by a human before it wrote | every stage owns a named agent (D-1) |

---

## The shape they share

Every class above is one of two shapes:

1. **A mechanism was replaced by a judgement.** Prose instead of an exit code, recall
   instead of a search, an instruction instead of a permission bit, a summary instead of a
   count.
2. **An absence was read as a pass.** Zero flagged, zero withheld, no output, empty set,
   skipped stage — all of them look exactly like success.

When something new fails, check which of the two it is first. The fix is almost always
already written down for the other shape.
