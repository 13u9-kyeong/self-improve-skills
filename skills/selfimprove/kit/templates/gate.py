#!/usr/bin/env python3
"""<gate_name> — <one line: what this gate rejects> (template; copy to scripts/<gate_name>.py).

    python3 scripts/<gate_name>.py <input.json>

A gate is a script that reads one input and returns a verdict through its exit code, and
nothing else. Copy this file, replace the CHECK section, then register the gate in
loop.config.yaml with a `fail_args` recipe and run harness/conformance/test_exit_codes.py.

The parts below the CHECK section are the rule (L-8) and should not need to change:
  - unreadable / empty / missing input  -> CANNOT (2) via gatelib, never a traceback
  - an empty set of items to check      -> CANNOT (2), because "0 problems" over nothing
                                           reads exactly like a clean pass
  - a real problem found                -> FAIL (1)
  - checked everything, nothing wrong   -> PASS (0)

Before trusting it, sabotage it (L-10): make CHECK return no problems, confirm the
conformance test goes red on the `fail_args` axis, and restore.

Exit: 0 pass · 1 fail · 2 cannot judge · 3 usage.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib


def check(item: dict) -> list:
    """CHECK — return a list of problems for one item; an empty list means it passes.

    Replace this. The example rejects any item without an `id` or a `cause`.
    """
    problems = []
    if not item.get("id"):
        problems.append("item has no id")
    if not item.get("cause"):
        problems.append(f"{item.get('id', '?')}: no cause recorded")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="the JSON file this gate judges")
    args = ap.parse_args()

    data = gatelib.load_json(args.input, "gate input")
    items = gatelib.require_inputs(data.get("items") if isinstance(data, dict) else None,
                                   "item", hint="  Expected {\"items\": [...]}.")

    problems = [p for item in items for p in check(item)]
    for p in problems:
        print(f"  FAIL  {p}")
    print(f"\n{len(items)} item(s) checked · {len(problems)} problem(s)")
    return gatelib.FAIL if problems else gatelib.PASS


if __name__ == "__main__":
    sys.exit(main())
