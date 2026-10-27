#!/usr/bin/env python3
"""Copy the self-improvement kit into a project, never overwriting anything.

    python3 install_kit.py --into <project> [--dry-run]

Every file of `kit/` that does not exist in the project is copied. Every file that already
exists is left untouched and listed as a conflict, so the caller can merge it by hand —
`CLAUDE.md` in particular, which the skill appends to under `# Self-improvement loop`
instead of replacing.

Exit: 0 installed (conflicts, if any, are listed) · 2 cannot (kit missing, target not a
      directory, a copy failed) · 3 usage.
"""
import argparse
import shutil
import sys
from pathlib import Path

PASS, FAIL, CANNOT, USAGE = 0, 1, 2, 3
KIT = Path(__file__).resolve().parent / "kit"
SKIP = {"__pycache__"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--into", required=True, help="the project root to install into")
    ap.add_argument("--dry-run", action="store_true", help="list what would happen")
    args = ap.parse_args()

    if not (KIT / "CLAUDE.md").is_file() or not (KIT / "scripts" / "gatelib.py").is_file():
        print(f"CANNOT_JUDGE — the kit is missing or incomplete at {KIT}", file=sys.stderr)
        return CANNOT
    dest = Path(args.into).resolve()
    if not dest.is_dir():
        print(f"CANNOT_JUDGE — not a directory: {dest}", file=sys.stderr)
        return CANNOT

    copied, conflicts = [], []
    for src in sorted(KIT.rglob("*")):
        rel = src.relative_to(KIT)
        if src.is_dir() or SKIP & set(rel.parts) or src.suffix == ".pyc":
            continue
        target = dest / rel
        if target.exists():
            conflicts.append(rel)
            continue
        copied.append(rel)
        if not args.dry_run:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
            except OSError as e:
                print(f"CANNOT_JUDGE — copy failed for {rel}: {e}", file=sys.stderr)
                return CANNOT

    if not copied and not conflicts:
        print("CANNOT_JUDGE — the kit holds no files; nothing was installed.",
              file=sys.stderr)
        return CANNOT

    verb = "would copy" if args.dry_run else "copied"
    print(f"{verb} {len(copied)} file(s) into {dest}")
    if conflicts:
        print(f"\n{len(conflicts)} file(s) already exist and were NOT touched:")
        for rel in conflicts:
            print(f"  {rel}")
        if Path("CLAUDE.md") in conflicts:
            print("\nCLAUDE.md exists: append the kit's rules under a "
                  "`# Self-improvement loop` heading and show the user the diff.\n"
                  f"  kit copy: {KIT / 'CLAUDE.md'}")
    return PASS


if __name__ == "__main__":
    sys.exit(main())
