#!/usr/bin/env python3
"""Learned cards must be domain-general — no target proper nouns (L-11).

    python3 scripts/lint_cards.py [--config loop.config.yaml] [--dir references/learned]

A card that names the target it was learned from teaches nothing about the next one. The
test for whether a word is allowed is mechanical and it is the whole rule:

    would a DIFFERENT target on the same runtime use this word identically?

Yes -> it carries no target identity. Put it in `cards.vocab_allow`.
No  -> it names this target. Restate the lesson as the structural condition it is really
       about, which is almost always the better card anyway.

Expect this linter to reject terms you think are generic. That is it working. In the loop
this kit came from, a rule written around an interface callback name was rejected and had
to be rewritten as a structural condition — and the rewrite was the stronger rule.

Exit: 0 clean · 1 proper nouns found · 2 nothing to check · 3 usage.
"""
import argparse
import re
import sys
from pathlib import Path

PASS, FAIL, CANNOT, USAGE = 0, 1, 2, 3

# Candidate proper nouns: CamelCase, Capitalized runs, snake_case with a capital,
# and anything::scoped or dotted that starts capitalized.
CANDIDATE = re.compile(r"\b(?:[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+|[A-Z]{2,}[a-z0-9]\w*)\b")

# Sentence-initial and heading words are ordinary English, not identifiers.
ENGLISH = {
    "The", "This", "That", "These", "Those", "There", "Then", "Therefore", "Then",
    "What", "When", "Where", "Which", "While", "Why", "Who", "Whose", "How",
    "And", "But", "Not", "Never", "Always", "Measured", "Because", "Both", "Each",
    "Every", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "If", "It", "Its", "In", "On", "At", "To", "For", "From", "With", "Without",
    "Count", "Grade", "Spend", "Raising", "Read", "Dropping", "Submitted", "Our",
    "We", "You", "A", "An", "As", "Also", "After", "Before", "Against", "Across",
}


def code_spans(text: str):
    """Fenced blocks and inline code are quoted evidence, not prose. Cards must be able
    to show the real line they were learned from."""
    spans = []
    for m in re.finditer(r"```.*?```", text, re.S):
        spans.append(m.span())
    for m in re.finditer(r"`[^`\n]+`", text):
        spans.append(m.span())
    return spans


def in_span(i, spans):
    return any(a <= i < b for a, b in spans)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="loop.config.yaml")
    ap.add_argument("--dir", default=None, help="overrides cards.dir from config")
    args = ap.parse_args()

    allow = set(ENGLISH)
    cards_dir = args.dir
    cfg_path = Path(args.config)
    if cfg_path.exists():
        try:
            import yaml
        except ImportError:
            print("CANNOT_JUDGE — PyYAML is not installed, so the config (and its "
                  "allow-list) cannot be read: pip install pyyaml", file=sys.stderr)
            return CANNOT
        try:
            cfg = yaml.safe_load(cfg_path.read_text()) or {}
        except (OSError, yaml.YAMLError) as e:
            print(f"CANNOT_JUDGE — {cfg_path} is unreadable: {e}", file=sys.stderr)
            return CANNOT
        if not isinstance(cfg, dict):
            print(f"CANNOT_JUDGE — {cfg_path} is not a mapping", file=sys.stderr)
            return CANNOT
        cards = cfg.get("cards") or {}
        allow |= {str(v) for v in (cards.get("vocab_allow") or [])}
        cards_dir = cards_dir or cards.get("dir")
    cards_dir = cards_dir or "references/learned"

    d = Path(cards_dir)
    if not d.is_dir():
        print(f"CANNOT_JUDGE — card directory does not exist: {d}\n"
              f"This is not a pass; the linter checked nothing.", file=sys.stderr)
        return CANNOT
    files = sorted(d.glob("*.md"))
    if not files:
        print(f"CANNOT_JUDGE — no cards in {d}, so nothing was checked.\n"
              f"An empty input set is not a clean result (L-8).", file=sys.stderr)
        return CANNOT

    hits = {}
    for f in files:
        text = f.read_text(errors="replace")
        spans = code_spans(text)
        for m in CANDIDATE.finditer(text):
            tok = m.group(0)
            if tok in allow or in_span(m.start(), spans):
                continue
            line = text.count("\n", 0, m.start()) + 1
            hits.setdefault(f.name, []).append((line, tok))

    for name in sorted(hits):
        print(f"\n{name}")
        seen = set()
        for line, tok in hits[name]:
            if tok in seen:
                continue
            seen.add(tok)
            print(f"  :{line:<5} {tok}")

    n = sum(len({t for _, t in v}) for v in hits.values())
    print(f"\n{len(files)} card(s) · {n} candidate proper noun(s) in "
          f"{len(hits)} card(s)")
    if hits:
        print("\nFor each: would a DIFFERENT target on the same runtime use this word "
              "identically?\n"
              "  yes -> add it to `cards.vocab_allow` in loop.config.yaml\n"
              "  no  -> restate the lesson as the structural condition it is about")
    return FAIL if hits else PASS


if __name__ == "__main__":
    sys.exit(main())
