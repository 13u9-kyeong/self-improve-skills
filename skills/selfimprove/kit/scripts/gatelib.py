#!/usr/bin/env python3
"""gatelib.py — the exit-code rule every gate in this package obeys.

Built after an audit of the invocation rules found the same defect class the
pipeline had already patched eight times, one incident at a time, without ever
writing the convention down:

  - three gates died with a JSONDecodeError traceback on a malformed input file and
    exited 1 — the same code a JUDGED FAILURE exits with. A caller cannot tell "the
    gate rejected this item" from "the gate crashed and judged nothing".
  - one gate given an empty input directory printed a clean summary and exited 0.
    Another, given a document under 400 characters, printed "0 item(s) above
    threshold" and exited 0. Both read as a clean pass. Neither had checked anything.

A gate that cannot judge must say so in its exit code, because that is the only
channel a script or a CI step reads. Printing the reason is necessary and is not
sufficient: the measured failure mode of this whole project is a gate whose prose
nobody reads and whose exit code says "fine".

    0  PASS    judged, and it passed
    1  FAIL    judged, and it failed
    2  CANNOT  could not judge — unparseable input, empty input set, missing tool.
               NOT a pass. The caller must stop, not proceed.
    3  USAGE   the invocation itself was wrong (argparse already uses 2 for this,
               so gates that call `usage()` explicitly get 3 to keep 2 meaning
               CANNOT; argparse's own 2 is accepted by the conformance test as a
               usage error too, since both mean "the caller must fix the call").

`harness/conformance/test_exit_codes.py` asserts every gate in this package
obeys it. A new gate that fails open shows up there instead of in a lost round.
"""
import json
import sys
from pathlib import Path

PASS, FAIL, CANNOT, USAGE = 0, 1, 2, 3


def cannot(msg: str, *, hint: str = "") -> "NoReturn":
    """Exit 2. The gate could not reach a verdict — this is never a pass."""
    print(f"\nCANNOT_JUDGE — {msg}", file=sys.stderr)
    if hint:
        print(hint, file=sys.stderr)
    print("This is not a pass. Fix the input and re-run; do not proceed past this "
          "gate on a verdict it never reached.", file=sys.stderr)
    sys.exit(CANNOT)


def usage(msg: str) -> "NoReturn":
    """Exit 3. The invocation was wrong."""
    print(f"USAGE — {msg}", file=sys.stderr)
    sys.exit(USAGE)


def load_json(path, what: str):
    """Read and parse JSON, or exit CANNOT with the reason.

    Every gate that took a JSON path used to do `json.loads(Path(p).read_text())`
    bare, which turns a typo'd path or a half-written file into a traceback that
    exits 1 and is indistinguishable from a rejection.
    """
    p = Path(path)
    if not p.exists():
        cannot(f"{what} not found: {p}")
    try:
        text = p.read_text()
    except OSError as e:
        cannot(f"{what} could not be read: {p} ({e})")
    if not text.strip():
        cannot(f"{what} is empty: {p}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        cannot(f"{what} is not valid JSON: {p}",
               hint=f"  parser said: {e}")


def load_yaml(path, what: str):
    """Same rule for YAML inputs."""
    try:
        import yaml
    except ImportError:
        cannot("PyYAML is not installed, so a YAML input cannot be read")
    p = Path(path)
    if not p.exists():
        cannot(f"{what} not found: {p}")
    text = p.read_text()
    if not text.strip():
        cannot(f"{what} is empty: {p}")
    try:
        d = yaml.safe_load(text)
    except yaml.YAMLError as e:
        cannot(f"{what} is not valid YAML: {p}", hint=f"  parser said: {e}")
    if d is None:
        cannot(f"{what} parsed to nothing: {p}")
    return d


def require_inputs(items, what: str, *, hint: str = ""):
    """Exit CANNOT when the set a gate is supposed to check is empty.

    An empty input set is the shape that reads most like success: zero findings
    flagged, zero strands withheld, zero violations. The gate did no work and the
    line it prints is the same line it prints when the work came back clean.
    """
    if not items:
        cannot(f"no {what} to check — the gate examined nothing", hint=hint)
    return items
