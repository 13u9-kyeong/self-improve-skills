# Phase 0 — <domain>, <instance>

> A filled instance of `../../PHASE0.md`. Answer honestly, including gates that fail.

## 0.1 — a key you could not see  [PASS / FAIL]

**Which key:** <>
**Sealed by:** <time / another party / the client>
**Inventory:** <count, or "unlimited" with the reason>

**Isolation — physically, not by intention:**

```
<the commands. Remember that version history inside the subject reaches the key.>
```

**Training-data hazard:** <the cutoff relied on, and how pre/post-cutoff results are kept
as separate series>

## 0.2 — can you reproduce the scoring function?  [PASS / FAIL / PARTIAL]

**Currency:** <in preference order>
**`delivered` means:** <the hardest the destination offers>
**Scoring unit:** <hit / near / miss definitions for this key class>
**Reproduced a known result?** <which one>

**What this currency cannot see:**
- <>

## 0.3 — is a verdict mechanical?  [PASS / FAIL]

**Mechanism:** <tier, per family>
**Who runs it:** the orchestrator, every time, pasting the output
**Wall-clock per verdict:** <measured>
**Probabilistic?** <k/n protocol if so>
**Authorization:** <what is in writing, if the subject is not yours>

## 0.4 — the smallest useful unit

**Unit:** <>
**Size:** <>
**Denominator:** <>
**Complete when:** <>

## Verdict

- [ ] 0.1
- [ ] 0.2
- [ ] 0.3
- [ ] 0.4

**All hard gates pass** → `../../PLAN.md` Phase 1.
**Any hard gate fails** → run the no-key program and say what it cannot tell you.

**Decision:** <run the loop / run the no-key program / stop — and why. Required whenever a
hard gate above is unchecked; `scripts/loop_state.py` will not move past setup without it.>

Recorded blind spots: <>

## Round 1 shape

1. <>

Round 1's only job is to locate the ceiling. Do not optimize it.
