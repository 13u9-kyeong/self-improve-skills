#!/usr/bin/env python3
"""Scaffold a domain layer from the template, or check an existing one.

    python3 scripts/new_domain.py --name doc-extraction
    python3 scripts/new_domain.py --name doc-extraction --instances invoices receipts
    python3 scripts/new_domain.py --check domains/doc-extraction

The generic kit says how a measured loop works. A domain layer says what the work is. Seven
components, and a layer missing one cannot run a round — the missing one is always the same
shape: something unmeasurable left to the agent's judgement.

`--check` verifies the components exist, the config parses, every stage declares the seven
fields, every gate declares `cannot_args`, the comparison rules and failure classes are
defined, and every lens family holds questions. It does
NOT verify the three choices (denominator, verdict, key) are good. No tool can; that is
`PHASE0-<instance>.md`.

Exit: 0 complete · 1 incomplete · 2 cannot judge · 3 usage.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib

KIT = Path(__file__).resolve().parent.parent
TEMPLATE = KIT / "domains" / "_template"
STAGE_FIELDS = ["agent", "input", "output", "denominator", "must-not-see", "verdict",
                "verify"]


def scaffold(name: str, instances: list) -> int:
    if not TEMPLATE.is_dir():
        gatelib.cannot(f"template not found: {TEMPLATE}")
    dest = KIT / "domains" / name
    if dest.exists():
        gatelib.usage(f"{dest} already exists — pick another name, or use --check")

    shutil.copytree(TEMPLATE, dest)
    proto = dest / "PHASE0-instance.md"
    body = proto.read_text()
    for inst in instances:
        (dest / f"PHASE0-{inst}.md").write_text(
            body.replace("<instance>", inst, 1))
    proto.unlink()

    fam = dest / "lenses" / "_family.md"
    fam_body = fam.read_text()
    fam.unlink()
    (dest / "lenses" / "example-family.md").write_text(fam_body)

    for p in dest.rglob("*.md"):
        p.write_text(p.read_text().replace("<domain>", name))

    print(f"scaffolded domains/{name}")
    for p in sorted(dest.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(KIT)}")
    print(f"\nNow, in this order (domains/AUTHORING.md):")
    print("  1 denominator -> SURFACE.md        a product of two enumerable sets")
    print("  2 verdict     -> VERDICTS.md       per lens family, not once per domain")
    print("  3 key         -> PHASE0-*.md       prefer one sealed by time")
    print("  4 compare     -> COMPARE.md        answer vs key, per field; failure classes")
    print("  5 stages      -> STAGES.md         check for an environment and an intake stage")
    print("  6 lenses      -> lenses/*.md       directed questions, never yes/no")
    print("  7 config      -> loop.config.yaml  then --check")
    print("\nBackwards is the common failure: lens questions written before a denominator\n"
          "produce a checklist with no coverage claim.")
    return 0


def check(path: Path) -> int:
    if not path.is_dir():
        gatelib.cannot(f"not a directory: {path}")
    files = [p for p in path.rglob("*") if p.is_file()]
    gatelib.require_inputs(
        files, f"file in {path}",
        hint="  An empty layer directory is not a clean layer. Scaffold it with --name.")

    problems, notes = [], []

    # --- the seven components ---
    phase0 = sorted(path.glob("PHASE0-*.md"))
    if not phase0:
        problems.append("no PHASE0-<instance>.md — gate 0.1/0.2/0.3 unanswered, so there "
                        "is no record of whether the loop can run here at all")
    for f in ("SURFACE.md", "VERDICTS.md", "COMPARE.md", "STAGES.md", "loop.config.yaml"):
        if not (path / f).exists():
            problems.append(f"no {f}")
    lenses = sorted((path / "lenses").glob("*.md")) if (path / "lenses").is_dir() else []
    families = [p for p in lenses if p.name != "README.md"]
    if not families:
        problems.append("no lens families in lenses/ — nothing gets pushed across the "
                        "surface")

    # --- config ---
    cfg = {}
    cfgp = path / "loop.config.yaml"
    if cfgp.exists():
        try:
            import yaml
            cfg = yaml.safe_load(cfgp.read_text()) or {}
        except ImportError:
            gatelib.cannot("PyYAML is not installed, so loop.config.yaml cannot be "
                           "checked", hint="  pip install pyyaml")
        except Exception as e:
            problems.append(f"loop.config.yaml does not parse: {e}")

        stages = cfg.get("stages") or []
        if not stages:
            problems.append("loop.config.yaml names no stages — loss cannot be attributed "
                            "to one (L-6), so every stage absorbs the others' failures")
        gates = cfg.get("gates") or []
        if not gates:
            problems.append("loop.config.yaml names no gates — the conformance test would "
                            "check nothing (L-9)")
        for g in gates:
            if not g.get("cannot_args"):
                problems.append(f"gate `{g.get('name')}` has no cannot_args — it is never "
                                f"checked for refusing to judge unreadable input")
            if not g.get("fail_args"):
                notes.append(f"gate `{g.get('name')}` has no fail_args: it is verified "
                             f"against the easy half only")
        cur = cfg.get("currency") or {}
        for ax in ("found_axis", "delivered_axis"):
            v = str(cur.get(ax) or "")
            if not v or v.startswith("<"):
                problems.append(f"currency.{ax} is unset — the two axes must each be "
                                f"defined before round 1 (L-2)")
        # A placeholder parses fine and means the component was never authored. Catching
        # these is the difference between "the scaffold is well-formed" and "the layer is
        # finished", and only the second is worth a round.
        for st in stages:
            if str(st.get("name") or "").startswith("<") or \
               str(st.get("id") or "").startswith("<"):
                problems.append(f"stage `{st.get('id')}`/`{st.get('name')}` is still a "
                                f"scaffold placeholder")
        for g in gates:
            if str(g.get("name") or "").startswith("<"):
                problems.append("a gate in loop.config.yaml is still named `<gate>`")
        # comparison: how an answer meets the key, and what a failure is called
        comp = cfg.get("compare") or {}
        fields = comp.get("fields") or []
        if not fields:
            problems.append("compare.fields is empty — nothing says how an answer is "
                            "compared with the key, so success would be decided by hand")
        for f in fields:
            name, rule = str((f or {}).get("name") or ""), (f or {}).get("rule")
            if not name or name.startswith("<"):
                problems.append("a compare field is still a placeholder")
            elif rule not in ("exact", "text", "number", "set", "judge"):
                problems.append(f"compare field `{name}` has rule `{rule}` — use exact, "
                                f"text, number, set or judge")
        if fields and all((f or {}).get("rule") == "judge" for f in fields):
            notes.append("every compare field is `judge`: rounds measure agreement with a "
                         "judge, not correctness (tier 4) — say so in PHASE0")
        fclasses = comp.get("failure_classes") or []
        ids = [str(c.get("id") if isinstance(c, dict) else c) for c in fclasses]
        if not ids:
            problems.append("compare.failure_classes is empty — failures could only be "
                            "labelled by symptom, never by reason (L-6)")
        if any(i.startswith("<") for i in ids):
            problems.append("a failure class is still a placeholder")
        if (cfg.get("sealed") or {}).get("inventory") in (0, None):
            notes.append("sealed.inventory is 0: iteration rate is set by this number and "
                         "nothing else (L-5)")

    # --- stage specifications ---
    sp = path / "STAGES.md"
    if sp.exists():
        text = sp.read_text()
        blocks = re.split(r"^## +\[", text, flags=re.M)[1:]
        if not blocks:
            problems.append("STAGES.md declares no stages in `## [<id>] <name>` form")
        for b in blocks:
            sid = b.split("]")[0].strip()
            missing = [f for f in STAGE_FIELDS
                       if not re.search(rf"\*\*{re.escape(f)}\*\*", b)]
            if missing:
                problems.append(f"stage [{sid}] missing field(s): {', '.join(missing)}")
            for f in STAGE_FIELDS:
                m = re.search(rf"\*\*{re.escape(f)}\*\* +(.+)", b)
                if m and (m.group(1).strip().startswith("<")
                          or not m.group(1).strip()):
                    problems.append(f"stage [{sid}] field `{f}` is still a placeholder")

    # --- lens families hold questions ---
    for f in families:
        body = f.read_text()
        qs = re.findall(r"^\s*\d+\. +\*\*", body, re.M)
        if len(qs) < 3:
            notes.append(f"lenses/{f.name} holds {len(qs)} question(s): a family with "
                         f"almost none is a heading, not a lens")
        for q in re.findall(r"^\s*\d+\. +\*\*(.+?)\*\*", body, re.M):
            if re.match(r"^(is|are|does|do|can|has|have|was|were)\b", q.strip(), re.I):
                notes.append(f"lenses/{f.name}: \"{q[:54]}...\" reads as yes/no — "
                             f"a question answerable \"yes, fine\" will be (property 1)")

    print(f"# layer check — {path.name}")
    print(f"{len(files)} file(s) · {len(phase0)} instance worksheet(s) · "
          f"{len(families)} lens family(ies)")
    if problems:
        print(f"\nINCOMPLETE — {len(problems)}:")
        for p_ in problems:
            print(f"  - {p_}")
    if notes:
        print(f"\nnotes — {len(notes)} (not blocking):")
        for n in notes[:20]:
            print(f"  - {n}")
        if len(notes) > 20:
            print(f"  ... and {len(notes) - 20} more")
    if not problems:
        print("\nseven components present; config, comparison, stage specifications and "
              "gates well-formed.")
        print("This says nothing about whether the denominator, verdict and key are good.\n"
              "No tool can check that — it is PHASE0-<instance>.md.")
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help="scaffold a new layer under domains/")
    ap.add_argument("--instances", nargs="+", default=["instance"],
                    help="sub-instance names; one PHASE0 worksheet each (the key usually "
                         "differs between them and nothing else does)")
    ap.add_argument("--check", metavar="DIR", help="check an existing layer")
    args = ap.parse_args()

    if args.check:
        return check(Path(args.check))
    if args.name:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.name):
            gatelib.usage("--name must be lowercase kebab-case")
        return scaffold(args.name, args.instances)
    ap.print_help()
    return gatelib.USAGE


if __name__ == "__main__":
    sys.exit(main())
