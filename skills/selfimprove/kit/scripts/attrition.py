#!/usr/bin/env python3
"""Internal attrition census — candidates -> filed -> delivered (L-6, L-13).

    python3 scripts/attrition.py --round runs/<date>-<name> [--config loop.config.yaml]

This is the measurement that needs NO sealed key, and in the loop this kit came from it
found the largest single loss in the project's history: detection was 9 of 13 against the
judged set while valid submissions were 2. Recall looked like 69% success. The real figure
was a 78% loss, and all of it happened after the defect had already been found.

So: run this every round, including the cheap rounds that spend no sealed inventory. A drop
between two adjacent stages is a defect in the pipeline, not a fact about the target.

Input: a round directory holding `census.json`:

    {"stages": [{"id": "1", "name": "candidate-generation", "count": 412},
                {"id": "3", "name": "filing",               "count": 37},
                {"id": "4", "name": "delivered",            "count": 12}],
     "dropped": [{"item": "C-104", "stage": "3", "cause": "below reporting threshold"}]}

Every drop needs a cause. An item that vanished between two stages with no row in
`dropped` is reported as UNACCOUNTED, which is the finding — a loss nobody recorded is a
loss nobody can fix.

Exit: 0 every drop accounted for · 1 unaccounted drops · 2 cannot judge · 3 usage.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--round", required=True, help="the round directory")
    ap.add_argument("--census", default="census.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    data = gatelib.load_json(Path(args.round) / args.census, "census file")
    stages = data.get("stages") or []
    gatelib.require_inputs(
        stages, "pipeline stage",
        hint="  A census with no stages measures nothing. List every stage an item "
             "passes through, in order.")

    dropped = data.get("dropped") or []
    by_stage = {}
    for d in dropped:
        by_stage.setdefault(str(d.get("stage")), []).append(d)

    rows, unaccounted_total = [], 0
    prev = None
    for s in stages:
        sid, name, count = str(s.get("id")), s.get("name", ""), int(s.get("count") or 0)
        lost = (prev - count) if prev is not None else 0
        recorded = len(by_stage.get(sid, []))
        unaccounted = max(0, lost - recorded)
        unaccounted_total += unaccounted
        retention = (count / prev * 100) if prev else 100.0
        rows.append({"id": sid, "name": name, "count": count, "lost": lost,
                     "recorded": recorded, "unaccounted": unaccounted,
                     "retention_pct": round(retention, 1)})
        prev = count

    if args.json:
        print(json.dumps({"rows": rows, "unaccounted": unaccounted_total}, indent=1))
    else:
        print(f"# attrition — {Path(args.round).name}\n")
        print(f"{'stage':28} {'in':>7} {'lost':>7} {'kept%':>7} {'unaccounted':>12}")
        print("-" * 66)
        for r in rows:
            flag = "  <-- " if r["unaccounted"] else ""
            print(f"{r['id'] + ' ' + r['name']:28} {r['count']:>7} {r['lost']:>7} "
                  f"{r['retention_pct']:>6.1f}% {r['unaccounted']:>12}{flag}")
        worst = max((r for r in rows[1:]), key=lambda r: r["lost"], default=None)
        if worst and worst["lost"] > 0:
            print(f"\nlargest single drop: {worst['lost']} items at stage "
                  f"{worst['id']} ({worst['name']})")
            print("  A drop between two adjacent stages is a defect in the pipeline, "
                  "not a fact about the target.")

    if unaccounted_total:
        print(f"\n{unaccounted_total} item(s) vanished with no row in `dropped`.",
              file=sys.stderr)
        print("Every drop needs a cause. A loss nobody recorded is a loss nobody can "
              "fix — and it is indistinguishable, in the next round's numbers, from an "
              "item that was never generated.", file=sys.stderr)
        return 1
    print("\nevery drop is accounted for with a cause")
    return 0


if __name__ == "__main__":
    sys.exit(main())
