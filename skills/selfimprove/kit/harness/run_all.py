#!/usr/bin/env python3
"""Run every check in harness/ — the gate conformance test and every lesson check.

    python3 harness/run_all.py [--config loop.config.yaml] [--no-conformance]

`harness/` holds two kinds of check:

  harness/conformance/test_exit_codes.py   shipped with the kit: every gate in
                                           loop.config.yaml obeys the exit-code rule (L-9)
  harness/<lesson>/test_*.py               added by the loop: one per learned card, each
                                           failing on the defect that card is about (L-10)

Lesson checks accumulate one per measured loss. A check that nothing runs is a comment, so
this runner executes all of them and folds their exit codes into one verdict under the same
exit-code rule (L-8). Each check is run as its own process from the project root and must itself
obey the rule.

The conformance test exits 2 until loop.config.yaml names at least one gate. Before the
`setup:gates` phase that is expected; pass `--no-conformance` to run only the lesson checks.

Exit: 0 every check passed · 1 at least one check failed · 2 cannot judge (a check could
      not judge, or there was nothing to run) · 3 usage.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
sys.path.insert(0, str(HARNESS.parent / "scripts"))
import gatelib

CONFORMANCE = HARNESS / "conformance" / "test_exit_codes.py"


def lesson_checks():
    return sorted(p for p in HARNESS.glob("*/test_*.py")
                  if p.parent.name != "conformance" and "__pycache__" not in p.parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="loop.config.yaml",
                    help="passed to the conformance test (default: loop.config.yaml)")
    ap.add_argument("--no-conformance", action="store_true",
                    help="skip the gate conformance test (before setup:gates)")
    args = ap.parse_args()

    root = HARNESS.parent
    runs = []
    if not args.no_conformance:
        runs.append((CONFORMANCE, ["--config", args.config]))
    runs += [(p, []) for p in lesson_checks()]
    gatelib.require_inputs(
        runs, "harness check",
        hint="  No lesson checks exist yet under harness/<lesson>/test_*.py, and the conformance\n"
             "  test was skipped. Nothing was verified.")

    results = []
    for script, extra in runs:
        p = subprocess.run([sys.executable, str(script), *extra], cwd=root,
                           capture_output=True, text=True)
        rc = p.returncode
        if rc not in (gatelib.PASS, gatelib.FAIL, gatelib.CANNOT, gatelib.USAGE):
            rc = gatelib.CANNOT   # an unknown code is not a verdict
        elif rc == gatelib.FAIL and "Traceback (most recent call last)" in p.stderr:
            rc = gatelib.CANNOT   # Python exits 1 on a crash; a crash is not a verdict (L-8)
        results.append((script.relative_to(root), rc, p.stdout + p.stderr))

    label = {0: "pass  ", 1: "FAIL  ", 2: "CANNOT", 3: "USAGE "}
    for rel, rc, out in results:
        print(f"  {label[rc]} {rel}")
        if rc != gatelib.PASS:
            for line in out.strip().splitlines()[-6:]:
                print(f"           {line}")

    codes = [rc for _, rc, _ in results]
    print(f"\n{codes.count(0)}/{len(codes)} check(s) passed")
    if gatelib.FAIL in codes:
        return gatelib.FAIL
    if gatelib.CANNOT in codes or gatelib.USAGE in codes:
        print("At least one check could not judge. This is not a pass.", file=sys.stderr)
        return gatelib.CANNOT
    return gatelib.PASS


if __name__ == "__main__":
    sys.exit(main())
