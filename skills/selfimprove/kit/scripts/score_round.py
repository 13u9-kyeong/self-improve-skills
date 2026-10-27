#!/usr/bin/env python3
"""Two-axis scorer — a skeleton that refuses to emit one number (L-2, SCORING.md).

    python3 scripts/score_round.py --round runs/<r> [--config loop.config.yaml] [--json]

This is a skeleton on purpose: the value formula is domain-specific and belongs in
`value_of()` below. Everything around it is not domain-specific and is the part that goes
wrong, so it ships filled in:

  - **Two axes, never collapsed.** found, and delivered. A scorer that can emit one number
    will eventually be asked to. Measured: recall 9/13 with 2 delivered — a 78% loss that a
    single count displayed as 69% success.
  - **Per-item rows, not totals.** A total cannot be attributed to a stage, and an
    unattributed loss cannot become a card.
  - **As-scored separated from counterfactual.** The headline is always as-scored.

Input: `<round>/scored.json`

    {"items": [
       {"id": "C-1", "found": true,  "found_at_stage": "1", "filed_as": "lane-a",
        "delivered": true,  "weight": 1.0, "rarity": 2},
       {"id": "C-2", "found": true,  "found_at_stage": "1", "filed_as": "lane-b",
        "delivered": false, "weight": 1.0, "rarity": 1,
        "died_at_stage": "3", "cause": "graded below the reporting threshold"},
       {"id": "C-3", "found": false, "cause": "never generated"}
     ],
     "key_total": 13,
     "pot": null}

Every item with `delivered: false` needs `died_at_stage` and `cause`, or it is reported
UNATTRIBUTED — which is the finding (L-6).

Exit: 0 scored and every loss attributed · 1 unattributed losses · 2 cannot judge ·
      3 usage.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib


def value_of(item: dict, pot, k) -> float:
    """DOMAIN-SPECIFIC. Replace with your key class's unit (SCORING.md).

    Three classes, and most domains are NOT the third:

      A  fix history      no pot, no rarity. Unit is a grade under someone else's
                          rubric, or "a reproduction passes". Leave --k unset and put the
                          unit in `weight`.
      C  no key           there is nothing to value. Do not use this scorer for a
                          headline; use scripts/attrition.py and say what it cannot
                          tell you.
      B  judged set       the only class with a payout formula. --k applies.

    Rules from SCORING.md that survive whatever you put here:
      - recover any constant from a published total rather than guessing it (--k);
      - check the result against a published outcome you did not produce before
        trusting it on your own round;
      - watch for display scaling. Measured: a platform published figures at 1/100 of
        actual, and a scorer that matched the display perfectly was wrong by two orders
        of magnitude for three rounds.

    Default here is deliberately crude — weight alone — so that an unreplaced formula
    produces obviously unusable numbers rather than plausible wrong ones.
    """
    if k is None:
        return float(item.get("weight") or 0)
    # Class B: put the published formula here — including any sharing or decay term
    # the destination applies when several parties deliver the same item (`rarity`).
    return k * float(item.get("weight") or 0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--round", required=True)
    ap.add_argument("--config", default="loop.config.yaml")
    ap.add_argument("--scored", default="scored.json")
    ap.add_argument("--k", type=float, default=None,
                    help="value-formula constant, recovered from a published total")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    data = gatelib.load_json(Path(args.round) / args.scored, "scored file")
    items = data.get("items") or []
    gatelib.require_inputs(
        items, "scored item",
        hint="  A scorer with no items reports 0/0, which reads as a clean result and is\n"
             "  the shape L-8 is about. List every item the key holds.")

    key_total = int(data.get("key_total") or 0)
    if not key_total:
        gatelib.cannot(
            "`key_total` is missing or zero",
            hint="  Without the key's size there is no denominator, so 'found' is a count\n"
                 "  with nothing to be a fraction of.")

    k = args.k if args.k is not None else data.get("k")
    pot = data.get("pot")

    found = [i for i in items if i.get("found")]
    delivered = [i for i in found if i.get("delivered")]
    lost = [i for i in found if not i.get("delivered")]
    unattributed = [i for i in lost
                    if not (i.get("died_at_stage") and i.get("cause"))]

    v_found = sum(value_of(i, pot, k) for i in found)
    v_delivered = sum(value_of(i, pot, k) for i in delivered)

    by_stage = {}
    for i in lost:
        sid = str(i.get("died_at_stage") or "UNATTRIBUTED")
        by_stage.setdefault(sid, []).append(i)

    rows = [{"id": i.get("id"), "found": bool(i.get("found")),
             "found_at_stage": i.get("found_at_stage"),
             "filed_as": i.get("filed_as"),
             "delivered": bool(i.get("delivered")),
             "value": round(value_of(i, pot, k), 2),
             "died_at_stage": i.get("died_at_stage"),
             "cause": i.get("cause")} for i in items]

    out = {
        "axes": {
            "found": {"count": len(found), "of": key_total, "value": round(v_found, 2)},
            "delivered": {"count": len(delivered), "of": key_total,
                          "value": round(v_delivered, 2)},
        },
        "loss_priced": round(v_found - v_delivered, 2),
        "loss_by_stage": {s: round(sum(value_of(i, pot, k) for i in v), 2)
                          for s, v in sorted(by_stage.items())},
        "unattributed": [i.get("id") for i in unattributed],
        "k": k,
        "rows": rows,
    }

    if args.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"# score — {Path(args.round).name}\n")
        print("Two axes. Never report one without the other.\n")
        print(f"  found      {len(found):>4} / {key_total:<4}  value {v_found:>12,.2f}")
        print(f"  delivered  {len(delivered):>4} / {key_total:<4}  value "
              f"{v_delivered:>12,.2f}")
        print(f"\n  loss priced {v_found - v_delivered:>23,.2f}")
        if by_stage:
            print("\n  by stage:")
            for s, v in sorted(by_stage.items(),
                               key=lambda kv: -sum(value_of(i, pot, k) for i in kv[1])):
                amt = sum(value_of(i, pot, k) for i in v)
                print(f"    {s:<16} {len(v):>3} item(s)  {amt:>12,.2f}  "
                      f"{', '.join(str(i.get('id')) for i in v[:6])}")
        if k is None:
            print("\n  NOTE: no value formula constant given (--k). Values above are raw\n"
                  "  weights from the placeholder formula, not the domain's currency.\n"
                  "  Replace value_of() and recover k from a published total before\n"
                  "  reporting any of these numbers.")

    if unattributed:
        print(f"\n{len(unattributed)} found item(s) were not delivered and name no stage "
              f"or cause: {', '.join(str(i.get('id')) for i in unattributed)}",
              file=sys.stderr)
        print("A loss nobody attributed cannot become a card, so it will recur. Give each\n"
              "one a `died_at_stage` and a `cause` (L-6).", file=sys.stderr)
        return 1
    print("\nevery loss is attributed to a stage and a cause")
    return 0


if __name__ == "__main__":
    sys.exit(main())
