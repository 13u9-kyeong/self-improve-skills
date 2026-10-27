#!/usr/bin/env python3
"""Every failed problem gets a class, a stage and a cause — and the classes get counted.

    python3 scripts/failures.py --round runs/<r> [--config loop.config.yaml] [--json]
    python3 scripts/failures.py --round runs/<r> --apply analysis.json

`compare.py` says WHICH problems failed and what the symptom was (missing answer, bad
format, wrong value). This script makes sure each failure is turned into a reason before the
round is reported, because a failure nobody explained cannot become a lesson (L-6, L-10).

A failure is analysed when it has:
  failure_class   one of `compare.failure_classes` in loop.config.yaml, or a built-in:
                    not_attempted   the pipeline produced no answer
                    format          an answer exists but a field is missing or unreadable
                    key_dispute     the key itself looks wrong — listed, never dropped
                  `wrong` and `judge_pending` are symptoms, not reasons: they must be
                  replaced by a class.
  died_at_stage   a stage id from `stages:` — where the problem was last handled correctly
  cause           one sentence, about the pipeline rather than this one problem

The analysis rows come from the failure-analyst agent (templates/agents/failure-analyst.md),
one per failed problem, in a file passed to --apply:

    {"items": [{"id": "inv-17", "failure_class": "input_misread", "died_at_stage": "1",
                "cause": "the totals table spanning two pages is read as two tables",
                "evidence": "runs/r/intake/inv-17.json:12"}]}

--apply validates every row before writing anything; one bad row and nothing is written.

The report counts failures by class and by stage, and names the largest (class, stage) cell:
two failures with one cause are one pipeline defect, and the largest cell is the first
candidate for next round's single change.

Exit: 0 every failure analysed · 1 some failure unanalysed, or an --apply row rejected ·
      2 cannot judge · 3 usage.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib

BUILTIN = {"not_attempted", "format", "key_dispute"}
SYMPTOMS = {"wrong", "judge_pending", None, ""}


def allowed_classes(cfg: dict) -> set:
    comp = cfg.get("compare") or {}
    out = set(BUILTIN)
    for c in comp.get("failure_classes") or []:
        out.add(str(c.get("id") if isinstance(c, dict) else c))
    return out


def failed(items):
    return [i for i in items if not i.get("found") or not i.get("delivered")]


def problems_of(item, classes, stage_ids):
    p = []
    cls = item.get("failure_class")
    if cls in SYMPTOMS:
        p.append(f"class is `{cls or 'unset'}` — a symptom; name the reason")
    elif cls not in classes:
        p.append(f"class `{cls}` is not in compare.failure_classes")
    if str(item.get("died_at_stage") or "") not in stage_ids:
        p.append(f"died_at_stage `{item.get('died_at_stage')}` is not a stage id")
    if not str(item.get("cause") or "").strip():
        p.append("no cause")
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--round", required=True)
    ap.add_argument("--config", default="loop.config.yaml")
    ap.add_argument("--apply", metavar="ANALYSIS_JSON",
                    help="merge failure-analyst rows into scored.json, after validating")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = gatelib.load_yaml(args.config, "loop.config.yaml")
    if not isinstance(cfg, dict):
        gatelib.cannot("loop.config.yaml is not a mapping")
    stage_ids = {str(s.get("id")) for s in (cfg.get("stages") or []) if isinstance(s, dict)}
    gatelib.require_inputs(stage_ids, "stage in loop.config.yaml",
                           hint="  Without stages a failure cannot be attributed (L-6).")
    classes = allowed_classes(cfg)

    spath = Path(args.round) / "scored.json"
    scored = gatelib.load_json(spath, "scored file")
    items = gatelib.require_inputs(scored.get("items") if isinstance(scored, dict) else None,
                                   "scored item",
                                   hint="  Run scripts/compare.py first.")
    by_id = {str(i.get("id")): i for i in items}

    if args.apply:
        rows = gatelib.load_json(args.apply, "analysis file")
        rows = rows.get("items") if isinstance(rows, dict) else None
        gatelib.require_inputs(rows, "analysis row")
        rejected = []
        for r in rows:
            rid = str(r.get("id"))
            if rid not in by_id:
                rejected.append(f"{rid}: not in scored.json")
                continue
            if by_id[rid].get("found") and by_id[rid].get("delivered"):
                rejected.append(f"{rid}: this problem succeeded; nothing to analyse")
                continue
            errs = problems_of(r, classes, stage_ids)
            if errs:
                rejected.append(f"{rid}: " + "; ".join(errs))
        if rejected:
            print(f"REJECTED — {len(rejected)} row(s); nothing was written:")
            for x in rejected:
                print(f"  - {x}")
            return gatelib.FAIL
        for r in rows:
            tgt = by_id[str(r["id"])]
            for k in ("failure_class", "died_at_stage", "cause", "evidence"):
                if r.get(k) is not None:
                    tgt[k] = r[k]
        spath.write_text(json.dumps(scored, indent=1, ensure_ascii=False) + "\n")
        print(f"applied {len(rows)} row(s) to {spath}\n")

    fails = failed(items)
    todo = [(i, problems_of(i, classes, stage_ids)) for i in fails]
    todo = [(i, p) for i, p in todo if p]
    done = [i for i in fails if i not in [t[0] for t in todo]]

    by_class, by_stage, cells = {}, {}, {}
    for i in done:
        w = float(i.get("weight") or 1)
        c, s = i["failure_class"], str(i["died_at_stage"])
        by_class[c] = by_class.get(c, 0) + w
        by_stage[s] = by_stage.get(s, 0) + w
        cells[(c, s)] = cells.get((c, s), 0) + w
    disputes = [i["id"] for i in done if i.get("failure_class") == "key_dispute"]

    report = {"problems": len(items), "failed": len(fails), "analysed": len(done),
              "unanalysed": [i.get("id") for i, _ in todo],
              "by_class": by_class, "by_stage": by_stage,
              "largest_cell": None, "key_disputes": disputes}
    if cells:
        (c, s), w = max(cells.items(), key=lambda kv: kv[1])
        report["largest_cell"] = {"failure_class": c, "stage": s, "weight": w}

    if args.json:
        print(json.dumps(report, indent=1, ensure_ascii=False))
    else:
        print(f"# failures — {Path(args.round).name}\n")
        print(f"  {len(fails)} of {len(items)} problem(s) failed · {len(done)} analysed")
        if by_class:
            print("\n  by class (weighted):")
            for c, w in sorted(by_class.items(), key=lambda kv: -kv[1]):
                print(f"    {c:<22}{w:>8.2f}")
            print("\n  by stage (weighted):")
            for s, w in sorted(by_stage.items(), key=lambda kv: -kv[1]):
                print(f"    {'[' + s + ']':<22}{w:>8.2f}")
        if report["largest_cell"]:
            lc = report["largest_cell"]
            print(f"\n  largest shape: {lc['failure_class']} at stage [{lc['stage']}] "
                  f"({lc['weight']:.2f}) — first candidate for the next round's one change")
        if disputes:
            print(f"\n  key disputes (not dropped, reported): {', '.join(map(str, disputes))}")
        if not fails:
            print("\n  no failures in this round")
        if todo:
            print(f"\nUNANALYSED — {len(todo)} failure(s). Give each to the failure-analyst "
                  f"agent, then --apply its rows:")
            for i, p in todo[:30]:
                print(f"  - {i.get('id')}: {'; '.join(p)}")
            if len(todo) > 30:
                print(f"  ... and {len(todo) - 30} more")

    return gatelib.FAIL if todo else gatelib.PASS


if __name__ == "__main__":
    sys.exit(main())
