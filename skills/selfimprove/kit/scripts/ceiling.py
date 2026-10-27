#!/usr/bin/env python3
"""Locate the stage where a metric's ceiling is set — by searching, not by reasoning (L-7).

    python3 scripts/ceiling.py --round runs/<r> --missed "<term>" [--missed "<term>" ...]
    python3 scripts/ceiling.py --round runs/<r> --missed-file missed.txt

A metric has exactly one stage where its ceiling is set, and work anywhere else cannot move
it. The temptation is to reason about which stage "should" have caught a missed item. Do not.
Measured: reasoning placed a ceiling at a late stage; the mechanical search placed it at an
early one, which meant every planned improvement to the late stage could not have raised
recall at all. (That work still moved delivered value by 43% — a different, also useful,
fact. Know which one you are buying.)

Method: for each missed item, search EVERY artifact the round produced for that item's
mechanism, in stage order. The earliest stage whose artifacts mention it is where the item
was last alive; the next stage is where it died. An item mentioned nowhere never entered the
pipeline, and its ceiling is the first stage.

Stage order comes from `stages:` in loop.config.yaml, matched against path components of
each artifact. A stage with no artifacts is reported, not skipped — it is the most likely
ceiling and the easiest thing to overlook.

Exit: 0 a ceiling was located for every term · 1 at least one term found nowhere ·
      2 cannot judge · 3 usage.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
SKIP_EXT = {".pyc", ".png", ".jpg", ".pdf", ".zip", ".gz", ".so", ".bin"}


def load_stages(cfg_path: Path):
    if not cfg_path.exists():
        gatelib.cannot(f"config not found: {cfg_path}",
                       hint="  Stage order comes from `stages:` in loop.config.yaml.")
    cfg = gatelib.load_yaml(cfg_path, "loop.config.yaml")
    if not isinstance(cfg, dict):
        gatelib.cannot(f"loop.config.yaml is not a mapping: {cfg_path}")
    stages = cfg.get("stages") or []
    gatelib.require_inputs(
        stages, "pipeline stage",
        hint="  Without an ordered stage list there is no 'earlier' or 'later', so a "
             "ceiling cannot be located. Fill in `stages:` first.")
    return [(str(s.get("id")), str(s.get("name") or "")) for s in stages]


def artifacts(root: Path):
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() in SKIP_EXT:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            if p.stat().st_size > 8_000_000:
                continue
            yield p, p.read_text(errors="replace")
        except OSError:
            continue


def stage_of(path: Path, stages, root: Path):
    """Match an artifact to a stage by path component or filename prefix."""
    rel = str(path.relative_to(root)).lower()
    for sid, name in stages:
        tokens = [t for t in (sid, name, name.replace("-", "_")) if t]
        for t in tokens:
            if re.search(rf"(^|[/_\-\.\[]){re.escape(t.lower())}([/_\-\.\]]|$)", rel):
                return sid
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--round", required=True)
    ap.add_argument("--config", default="loop.config.yaml")
    ap.add_argument("--missed", action="append", default=[],
                    help="a term naming a missed item's mechanism; repeatable")
    ap.add_argument("--missed-file", help="one term per line")
    args = ap.parse_args()

    root = Path(args.round)
    if not root.is_dir():
        gatelib.cannot(f"round directory not found: {root}")

    terms = list(args.missed)
    if args.missed_file:
        p = Path(args.missed_file)
        if not p.exists():
            gatelib.cannot(f"missed-file not found: {p}")
        terms += [l.strip() for l in p.read_text().splitlines() if l.strip()]
    gatelib.require_inputs(
        terms, "missed-item term",
        hint="  Pass --missed '<mechanism>' per item the key holds and the round did not\n"
             "  deliver. Use the MECHANISM, not the key's title: matching on titles is a\n"
             "  measured source of false hits.")

    stages = load_stages(Path(args.config))
    order = {sid: i for i, (sid, _) in enumerate(stages)}

    docs = list(artifacts(root))
    gatelib.require_inputs(
        docs, "artifact in the round directory",
        hint=f"  {root} holds no readable files, so nothing was searched.")

    by_stage = {}
    unmatched = 0
    for p, text in docs:
        sid = stage_of(p, stages, root)
        if sid is None:
            unmatched += 1
        by_stage.setdefault(sid, []).append((p, text))

    print(f"# ceiling — {root.name}")
    print(f"{len(docs)} artifact(s) searched · {len(stages)} stage(s) in config"
          + (f" · {unmatched} artifact(s) matched no stage" if unmatched else ""))

    empty = [f"{sid} {name}" for sid, name in stages if sid not in by_stage]
    if empty:
        print(f"\nstages with NO artifacts: {', '.join(empty)}")
        print("  A stage that produced nothing is the most likely ceiling and the easiest\n"
              "  to overlook. Confirm it ran at all before reading anything below.")

    nowhere = []
    print()
    for term in terms:
        rx = re.compile(re.escape(term), re.I)
        hits = []
        for sid, items in by_stage.items():
            for p, text in items:
                if rx.search(text):
                    hits.append((sid, p.relative_to(root)))
                    break
        if not hits:
            nowhere.append(term)
            first = f"{stages[0][0]} {stages[0][1]}"
            print(f"  {term}")
            print(f"      found NOWHERE -> never entered the pipeline. "
                  f"Ceiling is the first stage ({first}).")
            continue
        hits.sort(key=lambda h: order.get(h[0], 999) if h[0] else 999)
        last_alive = hits[-1][0]
        idx = order.get(last_alive, None)
        died = (stages[idx + 1] if idx is not None and idx + 1 < len(stages) else None)
        print(f"  {term}")
        print(f"      last seen at stage {last_alive or '(unmatched)'} "
              f"({hits[-1][1]})")
        if died:
            print(f"      -> died entering stage {died[0]} {died[1]}")
        else:
            print(f"      -> survived to the last stage; it was not a detection loss")

    print(f"\n{len(terms) - len(nowhere)}/{len(terms)} term(s) located in the pipeline")
    if nowhere:
        print(f"\n{len(nowhere)} term(s) appear in NO artifact. These are detection losses:\n"
              f"  {', '.join(nowhere)}\n"
              f"No amount of work in a later stage can recover them. Spend the next round's\n"
              f"change on the first stage, not on grading or delivery.", file=sys.stderr)
        return 1
    print("\nevery missed item was alive somewhere in the pipeline: these are not detection\n"
          "losses. The ceiling is downstream — selection, grading or delivery.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
