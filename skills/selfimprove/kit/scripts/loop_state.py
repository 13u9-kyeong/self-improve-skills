#!/usr/bin/env python3
"""Where is this project in the loop? Prints the phase the /selfimprove skill must run next.

    python3 scripts/loop_state.py [--root .] [--json]

The skill reads this instead of looking around and deciding. An orchestrator that infers its
own phase from an impression of the files is substituting judgement for a mechanism, which is
the shared shape of every orchestrator failure in ORCHESTRATOR.md.

Phases, in order — the first one whose condition holds is the answer:

  setup:interview    no INTERVIEW.md in any domain layer, or it records an unanswered choice
  setup:phase0       interview done, but a PHASE0 worksheet still has unchecked hard gates
                     and no recorded decision about them
  setup:layer        PHASE0 decided, but `new_domain.py --check` fails on the layer
  setup:gates        layer complete, but a gate named in loop.config.yaml has no script
  round:baseline     everything built, no round has been scored yet
  round:next         at least one round scored; the next one is due
  round:in-progress  a round directory exists with ROUND.md but no RESULT.md

Exit: 0 a phase was determined · 2 cannot judge (no kit here) · 3 usage.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib

CHOICES = ("goal", "material", "denominator", "verdict", "key", "delivered")


def unanswered(interview: Path):
    """INTERVIEW.md records each choice as `## <choice>` followed by an answer. A section
    still holding `<...>` or nothing is unanswered."""
    text = interview.read_text()
    missing = []
    for c in CHOICES:
        m = re.search(rf"^## +{c}\b.*?\n(.*?)(?=^## |\Z)", text, re.S | re.M | re.I)
        body = (m.group(1).strip() if m else "")
        if not body or body.startswith("<"):
            missing.append(c)
    return missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not (root / "CLAUDE.md").exists() or not (root / "scripts" / "gatelib.py").exists():
        gatelib.cannot(f"no self-improvement kit at {root}",
                       hint="  Install it first: run /selfimprove in this project, or\n"
                            "  python3 <skill-dir>/install_kit.py --into <project>")

    out = {"root": str(root), "layer": None, "phase": None, "detail": []}

    layers = [d for d in sorted((root / "domains").glob("*"))
              if d.is_dir() and not d.name.startswith("_")] \
        if (root / "domains").is_dir() else []

    def done(phase, *detail):
        out["phase"] = phase
        out["detail"] = list(detail)
        if args.json:
            print(json.dumps(out, indent=1))
        else:
            print(f"phase   {phase}")
            if out["layer"]:
                print(f"layer   {out['layer']}")
            for d in detail:
                print(f"        {d}")
        return 0

    # --- setup:interview --------------------------------------------------
    with_interview = [d for d in layers if (d / "INTERVIEW.md").exists()]
    if not with_interview:
        return done("setup:interview",
                    "no domain layer has an INTERVIEW.md yet — start from the user's goal")
    if len(with_interview) > 1:
        names = ", ".join(d.name for d in with_interview)
        return done("setup:interview",
                    f"more than one layer has an interview ({names}); ask which one "
                    f"this session is for and pass --root accordingly")
    layer = with_interview[0]
    out["layer"] = str(layer.relative_to(root))
    miss = unanswered(layer / "INTERVIEW.md")
    if miss:
        return done("setup:interview", f"unanswered: {', '.join(miss)}")

    # --- setup:phase0 -----------------------------------------------------
    p0 = sorted(layer.glob("PHASE0-*.md"))
    if not p0:
        return done("setup:phase0", "no PHASE0-<instance>.md written from the interview")
    for w in p0:
        t = w.read_text()
        boxes = re.findall(r"^- \[( |x|X|~)\] +0\.([123])", t, re.M)
        if not boxes:
            return done("setup:phase0", f"{w.name}: no verdict checkboxes")
        open_gates = [g for mark, g in boxes if mark == " "]
        # A placeholder parses as text. `<...>` is the template's, not the user's decision.
        decided = re.search(r"^\*\*Decision:\*\*[ \t]*[^<\s]", t, re.M)
        if open_gates and not decided:
            return done("setup:phase0",
                        f"{w.name}: hard gate(s) {', '.join('0.' + g for g in open_gates)} "
                        f"unchecked and no **Decision:** recorded (run the loop / run the "
                        f"no-key program / stop)")

    # --- setup:layer ------------------------------------------------------
    chk = subprocess.run([sys.executable, str(root / "scripts" / "new_domain.py"),
                          "--check", str(layer)], capture_output=True, text=True)
    if chk.returncode != 0:
        lines = [l.strip("- ").strip() for l in chk.stdout.splitlines()
                 if l.strip().startswith("- ")]
        return done("setup:layer", *(lines[:8] or ["new_domain.py --check failed"]))

    # --- setup:gates ------------------------------------------------------
    try:
        import yaml
        cfg = yaml.safe_load((layer / "loop.config.yaml").read_text()) or {}
    except Exception as e:
        gatelib.cannot(f"loop.config.yaml unreadable: {e}")
    missing_gates = [g["name"] for g in (cfg.get("gates") or [])
                     if not (root / "scripts" / f"{g['name']}.py").exists()]
    if missing_gates:
        return done("setup:gates", f"no script for: {', '.join(missing_gates)}")

    # --- rounds -----------------------------------------------------------
    runs = sorted(d for d in (root / "runs").glob("*") if d.is_dir()) \
        if (root / "runs").is_dir() else []
    for r in runs:
        if (r / "ROUND.md").exists() and not (r / "RESULT.md").exists():
            return done("round:in-progress", f"{r.relative_to(root)} has no RESULT.md")
    scored = [r for r in runs if (r / "RESULT.md").exists()]
    if not scored:
        return done("round:baseline",
                    "nothing scored yet; round 1 locates the ceiling and changes nothing")
    return done("round:next", f"{len(scored)} round(s) scored; last: "
                f"{scored[-1].relative_to(root)}")


if __name__ == "__main__":
    sys.exit(main())
