#!/usr/bin/env python3
"""Every gate named in loop.config.yaml obeys the exit-code rule (L-8, L-9).

    python3 harness/conformance/test_exit_codes.py [--config loop.config.yaml]

Why one test over all gates instead of a test per gate: a per-gate test catches the gate
you were thinking about. In the loop this kit came from, the same defect class — a gate
that printed a problem and exited 0 — was patched EIGHT times, each time for the one gate
that had just failed, and the ninth gate failed the same way. Enumerating every gate from
config is what catches the one nobody is thinking about, including gates added later by
someone who never read CLAUDE.md.

Three axes, all three required:

  unreadable input        -> CANNOT (2).  A traceback that exits 1 is indistinguishable
                                          from a judged rejection.
  missing required arg    -> 2 or 3.      A caller error is not a verdict.
  readable real violation -> FAIL (1).    The axis that notices a gate which quietly
                                          stopped checking. Gates with no `fail_args`
                                          are reported as UNGUARDED, not as passing.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PASS, FAIL, CANNOT, USAGE = 0, 1, 2, 3


def cannot(msg: str) -> "NoReturn":
    # sys.exit("<message>") exits 1, which is FAIL. A config this test cannot read is
    # not a judged failure of any gate.
    print(f"CANNOT_JUDGE — {msg}\nThis is not a pass.", file=sys.stderr)
    sys.exit(CANNOT)


def load_config(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        cannot("PyYAML is not installed: pip install pyyaml")
    if not path.exists():
        cannot(f"config not found: {path}\nCopy loop.config.yaml from the kit root.")
    try:
        cfg = yaml.safe_load(path.read_text()) or {}
    except (OSError, yaml.YAMLError) as e:
        cannot(f"config unreadable: {path} ({e})")
    if not isinstance(cfg, dict):
        cannot(f"config is not a mapping: {path}")
    return cfg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="loop.config.yaml")
    ap.add_argument("--scripts-dir", default="scripts",
                    help="where the gate scripts live (default: scripts)")
    args = ap.parse_args()

    root = Path(args.config).resolve().parent
    cfg = load_config(Path(args.config))
    gates = cfg.get("gates") or []
    scripts = root / args.scripts_dir

    if not gates:
        print("CANNOT_JUDGE — loop.config.yaml names no gates, so this test checked "
              "nothing.\nAn empty gate list is exactly the fail-open shape this test "
              "exists to catch (L-8).\nList every gate under `gates:` before relying on "
              "this result.", file=sys.stderr)
        return CANNOT

    failures, unguarded = [], []

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        empty = tmp / "empty"
        empty.write_text("")
        badjson = tmp / "bad.json"
        badjson.write_text("{not json at all")

        def subst(argv, fixture=None):
            table = {"{empty}": str(empty), "{dir}": str(tmp), "{badjson}": str(badjson),
                     "{tmp}": str(tmp), "{fixture}": str(fixture) if fixture else ""}
            return [table.get(a, a) for a in argv]

        def run(name, argv, fixture=None):
            script = scripts / f"{name}.py"
            if not script.exists():
                return None, f"{script} does not exist"
            p = subprocess.run([sys.executable, str(script)] + subst(argv, fixture),
                               capture_output=True, text=True, timeout=300)
            return p.returncode, p.stdout + p.stderr

        print("── unreadable input must be CANNOT (2) ──")
        for g in gates:
            name = g["name"]
            rc, out = run(name, g.get("cannot_args") or [])
            if rc is None:
                failures.append(f"{name}: {out}")
                print(f"  MISS {name:24} {out}")
                continue
            ok = rc == CANNOT
            print(f"  {'ok  ' if ok else 'FAIL'} {name:24} exit={rc}")
            if not ok:
                why = (" — crashed with a traceback, which a caller cannot tell apart "
                       "from a judged rejection" if "Traceback" in out else
                       " — an unexamined input was reported as a verdict")
                failures.append(f"{name}: unreadable input exited {rc}, expected "
                                f"{CANNOT}{why}")

        print("\n── missing required argument must not be a verdict (2 or 3) ──")
        for g in gates:
            name = g["name"]
            rc, out = run(name, [])
            if rc is None:
                continue
            ok = rc in (USAGE, 2)
            print(f"  {'ok  ' if ok else 'FAIL'} {name:24} exit={rc}")
            if not ok:
                failures.append(f"{name}: no-arg invocation exited {rc}; a caller error "
                                f"must not be reported as PASS or FAIL")

        print("\n── a readable input holding a real violation must be FAIL (1) ──")
        for g in gates:
            name = g["name"]
            if not g.get("fail_args"):
                unguarded.append(name)
                print(f"  ---- {name:24} no fail_args in config")
                continue
            fx = tmp / f"{name}.fixture"
            fx.write_text(g.get("fail_fixture_body") or "")
            rc, out = run(name, g["fail_args"], fixture=fx)
            if rc is None:
                continue
            ok = rc == FAIL
            print(f"  {'ok  ' if ok else 'FAIL'} {name:24} exit={rc}")
            if not ok:
                failures.append(f"{name}: an input holding a real violation exited {rc}, "
                                f"expected {FAIL}. If this gate now passes it, it stopped "
                                f"checking something it used to check")

    print()
    for f in failures:
        print("FAIL  " + f)
    if unguarded:
        print(f"\nUNGUARDED  {len(unguarded)} gate(s) have no `fail_args` and were not "
              f"checked for still working: {', '.join(unguarded)}")
        print("  A gate verified only against bad input is verified against the easy half. "
              "Give each one the smallest input it must reject.")

    checked = len(gates) * 2 + (len(gates) - len(unguarded))
    print(f"\n{checked - len(failures)}/{checked} checks passed · {len(gates)} gate(s)")
    return FAIL if failures else PASS


if __name__ == "__main__":
    sys.exit(main())
