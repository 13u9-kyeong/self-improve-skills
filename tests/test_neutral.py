"""The kit is domain-neutral: nothing shipped may depend on one domain's vocabulary.

The loop rules were extracted from one pipeline in one domain. Its vocabulary leaks back in
easily — through an example, a default formula, a docstring — and once it is there the kit
quietly teaches that domain instead of the loop. This test is the mechanical form of that
requirement: it fails on any banned term in anything the skill ships or the README shows.

If you are adding a worked example for a specific domain, put it in a separate repository or
a clearly separate add-on, not in `skills/selfimprove/`.

    python3 -m unittest tests.test_neutral -v
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SHIPPED = [REPO / "skills", REPO / "README.md", REPO / "README.ko.md",
           REPO / ".claude-plugin"]

# Vocabulary specific to one domain (smart-contract / blockchain security review and the
# contest platforms around it), plus names of pipelines and agents the kit must not depend on.
BANNED = [
    r"smart[\s-]?contracts?", r"solidity", r"\bevm\b", r"ethereum", r"blockchain",
    r"on-?chain", r"\bdefi\b", r"\berc-?\d+", r"msg\.sender", r"reentran\w*",
    r"\bfoundry\b", r"\bhardhat\b", r"\bsolana\b", r"\banchor\s+program", r"cosmwasm",
    r"code4rena", r"\bc4\b", r"sherlock", r"cantina", r"codehawks", r"immunefi",
    r"\bwardens?\b", r"\bsponsors?\b", r"\bauditforge\b", r"aegis\s*audit", r"\baf-[a-z]",
    r"vuln\s*research", r"\bsanitizer", r"\bkasan\b", r"\bexploit", r"\bpoc\b",
    r"\bbounty\b", r"\bcve-?\d*", r"\bmalware\b",
    # "contract" reads as the domain above even when it means an agreement or an exit-code
    # rule, so shipped text says "rule" or "specification" instead (계약 in Korean).
    r"\bcontracts?\b", r"계약",
]
PATTERN = re.compile("|".join(BANNED), re.I)

TEXT_EXT = {".md", ".py", ".yaml", ".yml", ".json", ".sh", ".txt", ""}


def shipped_files():
    for root in SHIPPED:
        if root.is_file():
            yield root
        elif root.is_dir():
            for p in sorted(root.rglob("*")):
                if p.is_file() and p.suffix in TEXT_EXT and "__pycache__" not in p.parts:
                    yield p


class TestDomainNeutral(unittest.TestCase):
    def test_something_was_scanned(self):
        files = list(shipped_files())
        self.assertGreater(len(files), 30, "the scan examined almost nothing (L-8)")

    def test_no_domain_vocabulary(self):
        hits = []
        for f in shipped_files():
            for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                for m in PATTERN.finditer(line):
                    hits.append(f"{f.relative_to(REPO)}:{n}: {m.group(0)!r}")
        self.assertEqual(hits, [], "domain-specific vocabulary in shipped files:\n"
                         + "\n".join(hits))

    def test_pattern_catches_what_it_bans(self):
        # Sabotage check for this test itself: a banned term must be caught.
        for s in ("a Solidity contract", "the Code4rena pot", "msg.sender check",
                  "an auditforge stage", "a PoC reproduces", "the bounty payout",
                  "the exit-code contract", "종료 코드 계약"):
            self.assertRegex(s, PATTERN)


if __name__ == "__main__":
    unittest.main()
