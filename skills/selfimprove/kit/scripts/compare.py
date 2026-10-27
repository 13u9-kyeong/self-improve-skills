#!/usr/bin/env python3
"""Compare the agent's answers with the key, problem by problem — and write scored.json.

    python3 scripts/compare.py --round runs/<r> --key <path/to/key.json>
                               [--answers answers.json] [--judgements judgements.json]
                               [--config loop.config.yaml] [--json]

This is the step between "the agent finished" and "the round is scored". Without it,
someone fills scored.json by hand, and if that someone is the agent that produced the
answers, the round is scored by a self-report (L-14).

Inputs
  <round>/answers.json   what the pipeline delivered, one entry per problem:
                           {"items": [{"id": "inv-17", "answer": {"total": "1,204.50",
                                       "vendor": "Acme"}, "delivered": true}]}
                         `delivered` is optional (default true): set it false for an answer
                         the pipeline produced but did not hand over.
  --key                  the sealed key, kept outside the working tree until this step:
                           {"items": [{"id": "inv-17", "expected": {"total": 1204.5,
                                       "vendor": "ACME Corp"}, "weight": 1}]}
  loop.config.yaml       `compare.fields` — one rule per field (see below).
  <round>/judgements.json   verdicts for `judge` fields, written by the answer-judge agent:
                           {"items": [{"id": "inv-17", "field": "summary", "match": true,
                                       "reason": "..."}]}

Rules (`compare.fields[].rule`)
  exact    JSON-equal
  text     equal after case-folding and collapsing whitespace
  number   |expected - got| <= tol (default 0); commas, spaces and currency marks ignored
  set      equal as sets of `text`-normalised strings (order and duplicates ignored)
  judge    decided by a judge, not by this script. Tier 4 — reported on its own line,
           never mixed into the mechanical count.

Every problem in the key gets exactly one outcome:
  success          every field matched
  not_attempted    no answer for this problem              (failure class set here)
  format           a field is missing or unparseable      (failure class set here)
  wrong            parsed, but a field differs             (a symptom: failures.py makes
                                                            you replace it with a cause)
  judge_pending    a `judge` field has no judgement yet    (blocks: exit 1)

Re-running is safe: failure analysis already recorded in scored.json (failure_class other
than the four above, died_at_stage, cause) is kept for every problem whose comparison did
not change. A re-render that wipes hand-recorded analysis is a known hazard (CLAUDE.md).

Exit: 0 every problem compared · 1 judgements pending · 2 cannot judge · 3 usage.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gatelib

RULES = ("exact", "text", "number", "set", "judge")
MECHANICAL_CLASSES = ("not_attempted", "format", "wrong", "judge_pending")
_NUM_STRIP = re.compile(r"[,\s$€£¥₩%]")


class Unparseable(Exception):
    pass


def norm_text(v) -> str:
    if v is None:
        raise Unparseable("missing")
    return " ".join(str(v).split()).casefold()


def to_number(v) -> float:
    if isinstance(v, bool) or v is None:
        raise Unparseable(f"not a number: {v!r}")
    if isinstance(v, (int, float)):
        return float(v)
    s = _NUM_STRIP.sub("", str(v))
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        raise Unparseable(f"not a number: {v!r}")


def to_set(v) -> set:
    if v is None:
        raise Unparseable("missing")
    if isinstance(v, str):
        v = [p for p in re.split(r"[,;\n]", v) if p.strip()]
    if not isinstance(v, (list, tuple, set)):
        raise Unparseable(f"not a list: {v!r}")
    return {norm_text(x) for x in v}


def field_match(rule: dict, expected, got):
    """True / False, or raise Unparseable when the agent's value cannot be read."""
    kind = rule["rule"]
    if kind == "exact":
        return expected == got
    if kind == "text":
        return norm_text(expected) == norm_text(got)
    if kind == "number":
        tol = float(rule.get("tol") or 0)
        return abs(to_number(expected) - to_number(got)) <= tol + 1e-12
    if kind == "set":
        return to_set(expected) == to_set(got)
    raise ValueError(kind)


def load_items(path: Path, what: str) -> dict:
    data = gatelib.load_json(path, what)
    items = data.get("items") if isinstance(data, dict) else None
    gatelib.require_inputs(items, f"item in {what}",
                           hint=f'  Expected {{"items": [...]}} in {path}.')
    out = {}
    for it in items:
        if not isinstance(it, dict) or it.get("id") in (None, ""):
            gatelib.cannot(f"{what} has an item with no `id`: {it!r}")
        key = str(it["id"])
        if key in out:
            gatelib.cannot(f"{what} lists id `{key}` twice")
        out[key] = it
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--round", required=True)
    ap.add_argument("--key", required=True, help="the sealed key (JSON)")
    ap.add_argument("--answers", default="answers.json")
    ap.add_argument("--judgements", default="judgements.json")
    ap.add_argument("--config", default="loop.config.yaml")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rnd = Path(args.round)
    cfg = gatelib.load_yaml(args.config, "loop.config.yaml")
    comp = (cfg.get("compare") if isinstance(cfg, dict) else None) or {}
    fields = gatelib.require_inputs(
        comp.get("fields"), "compare field",
        hint="  Define `compare.fields` in loop.config.yaml: one rule per answer field.")
    for f in fields:
        if not isinstance(f, dict) or not f.get("name") or f.get("rule") not in RULES:
            gatelib.cannot(f"compare field is malformed: {f!r}",
                           hint=f"  Each needs `name` and `rule` in {', '.join(RULES)}.")

    key = load_items(Path(args.key), "key")
    answers = load_items(rnd / args.answers, "answers")

    judged = {}
    jpath = rnd / args.judgements
    if jpath.exists():
        for j in load_items_list(jpath):
            judged[(str(j.get("id")), str(j.get("field")))] = j

    prior = {}
    spath = rnd / "scored.json"
    if spath.exists():
        try:
            for it in json.loads(spath.read_text()).get("items") or []:
                prior[str(it.get("id"))] = it
        except (ValueError, AttributeError):
            gatelib.cannot(f"existing {spath} is unreadable; refusing to overwrite the "
                           f"analysis it may hold")

    rows, pending = [], []
    for pid, k in key.items():
        exp = k.get("expected") or {}
        a = answers.get(pid)
        row = {"id": pid, "weight": k.get("weight", 1), "found": False,
               "delivered": False, "verdict": "mechanical", "fields": {},
               "failure_class": None, "died_at_stage": None, "cause": None}
        if a is None:
            row["failure_class"] = "not_attempted"
        else:
            got_all = a.get("answer") if isinstance(a.get("answer"), dict) else {}
            outcome = "success"
            for f in fields:
                name = f["name"]
                if name not in exp:
                    gatelib.cannot(f"key item `{pid}` has no expected `{name}`")
                cell = {"rule": f["rule"], "expected": exp[name], "got": got_all.get(name)}
                if f["rule"] == "judge":
                    row["verdict"] = "judged"
                    j = judged.get((pid, name))
                    if j is None or not isinstance(j.get("match"), bool):
                        cell["match"] = None
                        pending.append({"id": pid, "field": name})
                        outcome = "judge_pending" if outcome == "success" else outcome
                    else:
                        cell["match"] = j["match"]
                        cell["reason"] = j.get("reason")
                        if not j["match"] and outcome in ("success", "judge_pending"):
                            outcome = "wrong"
                elif name not in got_all:
                    cell["match"] = False
                    cell["problem"] = "missing"
                    outcome = "format"
                else:
                    try:
                        cell["match"] = bool(field_match(f, exp[name], got_all[name]))
                    except Unparseable as e:
                        cell["match"] = False
                        cell["problem"] = str(e)
                        outcome = "format"
                    if not cell["match"] and outcome in ("success", "judge_pending"):
                        outcome = "wrong"
                row["fields"][name] = cell
            if outcome == "success":
                row["found"] = True
                row["delivered"] = a.get("delivered", True) is not False
            else:
                row["failure_class"] = outcome

        # keep analysis recorded earlier for a problem whose comparison did not change
        old = prior.get(pid)
        if old and old.get("found") == row["found"] and \
                old.get("delivered") == row["delivered"] and \
                old.get("fields") == row["fields"]:
            for keep in ("died_at_stage", "cause", "evidence"):
                if old.get(keep):
                    row[keep] = old[keep]
            if old.get("failure_class") and old["failure_class"] not in MECHANICAL_CLASSES:
                row["failure_class"] = old["failure_class"]
        rows.append(row)

    extra = sorted(set(answers) - set(key))
    out = {"key_total": len(key), "items": rows, "extra": extra,
           "pending_judgements": pending}
    spath.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")

    n_ok = sum(1 for r in rows if r["found"])
    mech = [r for r in rows if r["verdict"] == "mechanical"]
    judg = [r for r in rows if r["verdict"] == "judged"]
    by = {}
    for r in rows:
        if not r["found"]:
            by[r["failure_class"]] = by.get(r["failure_class"], 0) + 1

    if args.json:
        print(json.dumps({"success": n_ok, "of": len(rows), "failures": by,
                          "extra": extra, "pending_judgements": pending}, indent=1))
    else:
        print(f"# compare — {rnd.name}\n")
        print(f"  success   {n_ok:>4} / {len(rows)}")
        print(f"    decided mechanically  {sum(r['found'] for r in mech):>4} / {len(mech)}")
        if judg:
            print(f"    decided by a judge    {sum(r['found'] for r in judg):>4} / "
                  f"{len(judg)}   (tier 4 — report separately)")
        for cls, n in sorted(by.items(), key=lambda kv: -kv[1]):
            print(f"  {cls:<16}{n:>4}")
        if extra:
            print(f"\n  {len(extra)} answer(s) for problems not in the key: "
                  f"{', '.join(extra[:8])}{' …' if len(extra) > 8 else ''}")
        print(f"\nwrote {spath}")
        if by:
            print("Next: python3 scripts/failures.py --round "
                  f"{args.round}   (every failure needs a class, a stage and a cause)")

    if pending:
        print(f"\n{len(pending)} judgement(s) pending — give each to the answer-judge agent "
              f"(templates/agents/answer-judge.md) and re-run. Not scored until then.",
              file=sys.stderr)
        return gatelib.FAIL
    return gatelib.PASS


def load_items_list(path: Path) -> list:
    data = gatelib.load_json(path, "judgements")
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        gatelib.cannot(f'judgements file must be {{"items": [...]}}: {path}')
    return items


if __name__ == "__main__":
    sys.exit(main())
