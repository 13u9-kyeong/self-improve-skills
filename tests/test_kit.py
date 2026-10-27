"""Behavioural tests for the kit's tools.

Every tool in the kit promises the same exit-code rule (kit/scripts/gatelib.py):

    0 PASS · 1 FAIL · 2 CANNOT (not a pass) · 3 USAGE

These tests run each tool as a subprocess inside a throwaway project, the same way the
skill runs them, and assert the rule on three kinds of input: nothing, broken input,
and a readable input that holds a real problem.

    python3 -m unittest discover -s tests -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "selfimprove"
KIT = SKILL / "kit"

PASS, FAIL, CANNOT, USAGE = 0, 1, 2, 3


class Project:
    """A temporary project with the kit installed, as step 0 of the skill does it."""

    def __init__(self, install_kit=True):
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        if install_kit:
            shutil.copytree(KIT, self.root, dirs_exist_ok=True)

    def close(self):
        self._td.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(text))
        return p

    def run(self, script, *args, env=None):
        p = subprocess.run([sys.executable, str(self.root / script), *args],
                           cwd=self.root, capture_output=True, text=True, timeout=120,
                           env=env)
        return p.returncode, p.stdout + p.stderr


def env_without_yaml(tmp: Path):
    """An environment where `import yaml` fails, to exercise the missing-tool path."""
    shim = tmp / "_noyaml"
    shim.mkdir(exist_ok=True)
    (shim / "yaml.py").write_text("raise ImportError('PyYAML hidden by the test')\n")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(shim) + os.pathsep + env.get("PYTHONPATH", "")
    return env


STAGES_CONFIG = """\
    stages:
      - {id: "1", name: intake}
      - {id: "2", name: filing}
    cards:
      dir: references/learned
      vocab_allow: [AllowedThing]
    """


class KitTestCase(unittest.TestCase):
    def setUp(self):
        self.p = Project()

    def tearDown(self):
        self.p.close()

    def assertExit(self, expected, result):
        rc, out = result
        self.assertEqual(rc, expected, f"expected exit {expected}, got {rc}\n{out}")
        self.assertNotIn("Traceback", out, "a crash is not a verdict")
        return out


class TestEmptyInputIsNeverAPass(KitTestCase):
    """L-8: an empty or missing input set exits CANNOT, never PASS."""

    def test_conformance_test_with_no_gates(self):
        self.assertExit(CANNOT, self.p.run("harness/conformance/test_exit_codes.py"))

    def test_lint_cards_with_no_cards(self):
        self.assertExit(CANNOT, self.p.run("scripts/lint_cards.py"))

    def test_attrition_with_no_round(self):
        self.assertExit(CANNOT, self.p.run("scripts/attrition.py", "--round", "runs/nope"))

    def test_ceiling_with_no_round(self):
        self.assertExit(CANNOT, self.p.run("scripts/ceiling.py", "--round", "runs/nope",
                                           "--missed", "x"))

    def test_scorer_with_no_round(self):
        self.assertExit(CANNOT, self.p.run("scripts/score_round.py", "--round", "runs/nope"))

    def test_layer_check_with_no_layer(self):
        self.assertExit(CANNOT, self.p.run("scripts/new_domain.py", "--check", "domains/nope"))

    def test_scorer_with_empty_items(self):
        self.p.write("runs/r/scored.json", '{"items": [], "key_total": 3}')
        self.assertExit(CANNOT, self.p.run("scripts/score_round.py", "--round", "runs/r"))

    def test_scorer_without_denominator(self):
        self.p.write("runs/r/scored.json", '{"items": [{"id": "a", "found": true, '
                                           '"delivered": true}]}')
        self.assertExit(CANNOT, self.p.run("scripts/score_round.py", "--round", "runs/r"))


class TestBrokenInputIsCannotNotFail(KitTestCase):
    """L-8: unreadable input and a missing tool exit CANNOT (2). Not 1, which is a judged
    rejection, and not 3, which blames the caller."""

    def test_scorer_bad_json(self):
        self.p.write("runs/r/scored.json", "{not json")
        self.assertExit(CANNOT, self.p.run("scripts/score_round.py", "--round", "runs/r"))

    def test_conformance_test_bad_yaml(self):
        self.p.write("loop.config.yaml", "gates: [unclosed\n")
        self.assertExit(CANNOT, self.p.run("harness/conformance/test_exit_codes.py"))

    def test_conformance_test_missing_config(self):
        self.assertExit(CANNOT, self.p.run("harness/conformance/test_exit_codes.py",
                                           "--config", "nope.yaml"))

    def test_lint_cards_bad_yaml(self):
        self.p.write("loop.config.yaml", "cards: [unclosed\n")
        self.p.write("references/learned/a.md", "a card\n")
        self.assertExit(CANNOT, self.p.run("scripts/lint_cards.py"))

    def test_ceiling_bad_yaml(self):
        self.p.write("loop.config.yaml", "stages: [unclosed\n")
        self.p.write("runs/r/intake/a.md", "x\n")
        self.assertExit(CANNOT, self.p.run("scripts/ceiling.py", "--round", "runs/r",
                                           "--missed", "x"))

    def test_missing_pyyaml_is_cannot_everywhere(self):
        env = env_without_yaml(self.p.root)
        self.p.write("loop.config.yaml", STAGES_CONFIG)
        self.p.write("references/learned/a.md", "a card\n")
        self.p.write("runs/r/intake/a.md", "x\n")
        self.assertExit(CANNOT, self.p.run("scripts/lint_cards.py", env=env))
        self.assertExit(CANNOT, self.p.run("scripts/ceiling.py", "--round", "runs/r",
                                           "--missed", "x", env=env))
        self.assertExit(CANNOT, self.p.run("harness/conformance/test_exit_codes.py",
                                           env=env))
        self.assertExit(PASS, self.p.run("scripts/new_domain.py", "--name", "demo"))
        self.assertExit(CANNOT, self.p.run("scripts/new_domain.py", "--check",
                                           "domains/demo", env=env))


class TestRealProblemsAreFail(KitTestCase):
    """The axis that notices a tool which quietly stopped checking."""

    def test_scorer_reports_two_axes_and_attributed_loss(self):
        self.p.write("runs/r/scored.json", json.dumps({
            "items": [
                {"id": "a", "found": True, "delivered": True, "weight": 2},
                {"id": "b", "found": True, "delivered": False, "weight": 1,
                 "died_at_stage": "2", "cause": "graded below threshold"},
                {"id": "c", "found": False}],
            "key_total": 3}))
        out = self.assertExit(PASS, self.p.run("scripts/score_round.py", "--round",
                                               "runs/r", "--json"))
        data = json.loads(out[:out.rindex("}") + 1])
        self.assertEqual(data["axes"]["found"]["count"], 2)
        self.assertEqual(data["axes"]["delivered"]["count"], 1)
        self.assertEqual(data["loss_by_stage"], {"2": 1.0})

    def test_scorer_flags_unattributed_loss(self):
        self.p.write("runs/r/scored.json", json.dumps({
            "items": [{"id": "a", "found": True, "delivered": False, "weight": 1}],
            "key_total": 1}))
        out = self.assertExit(FAIL, self.p.run("scripts/score_round.py", "--round", "runs/r"))
        self.assertIn("a", out)

    def test_scorer_k_scales_value(self):
        self.p.write("runs/r/scored.json", json.dumps({
            "items": [{"id": "a", "found": True, "delivered": True, "weight": 3}],
            "key_total": 1}))
        out = self.assertExit(PASS, self.p.run("scripts/score_round.py", "--round",
                                               "runs/r", "--k", "2", "--json"))
        data = json.loads(out[:out.rindex("}") + 1])
        self.assertEqual(data["axes"]["delivered"]["value"], 6.0)

    def test_attrition_unaccounted_drop(self):
        self.p.write("runs/r/census.json", json.dumps({
            "stages": [{"id": "1", "name": "intake", "count": 10},
                       {"id": "2", "name": "filing", "count": 7}],
            "dropped": [{"item": "x", "stage": "2", "cause": "duplicate"}]}))
        self.assertExit(FAIL, self.p.run("scripts/attrition.py", "--round", "runs/r"))

    def test_attrition_every_drop_accounted(self):
        self.p.write("runs/r/census.json", json.dumps({
            "stages": [{"id": "1", "name": "intake", "count": 3},
                       {"id": "2", "name": "filing", "count": 2}],
            "dropped": [{"item": "x", "stage": "2", "cause": "duplicate"}]}))
        self.assertExit(PASS, self.p.run("scripts/attrition.py", "--round", "runs/r"))

    def test_lint_cards_rejects_proper_noun(self):
        self.p.write("loop.config.yaml", STAGES_CONFIG)
        self.p.write("references/learned/a.md", "The FooWidget handler drops items.\n")
        out = self.assertExit(FAIL, self.p.run("scripts/lint_cards.py"))
        self.assertIn("FooWidget", out)

    def test_lint_cards_accepts_allowlisted_and_quoted(self):
        self.p.write("loop.config.yaml", STAGES_CONFIG)
        self.p.write("references/learned/a.md",
                     "The AllowedThing path drops items; see `QuotedName` for the line.\n")
        self.assertExit(PASS, self.p.run("scripts/lint_cards.py"))

    def test_ceiling_locates_and_flags_absent(self):
        self.p.write("loop.config.yaml", STAGES_CONFIG)
        self.p.write("runs/r/intake/a.md", "mentions alpha-mechanism here\n")
        self.p.write("runs/r/filing/b.md", "nothing relevant\n")
        self.assertExit(PASS, self.p.run("scripts/ceiling.py", "--round", "runs/r",
                                         "--missed", "alpha-mechanism"))
        self.assertExit(FAIL, self.p.run("scripts/ceiling.py", "--round", "runs/r",
                                         "--missed", "never-mentioned"))

    def test_fresh_scaffold_is_rejected_until_filled(self):
        self.assertExit(PASS, self.p.run("scripts/new_domain.py", "--name", "demo",
                                         "--instances", "a"))
        self.assertExit(FAIL, self.p.run("scripts/new_domain.py", "--check", "domains/demo"))


class TestConformanceHarness(KitTestCase):
    """L-9 / L-10: the conformance test passes a gate that obeys the rule, and goes red
    when that gate is sabotaged to fail open."""

    GATE = """\
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import gatelib
        if len(sys.argv) < 2:
            gatelib.usage("need a file")
        data = gatelib.load_json(sys.argv[1], "input")
        items = gatelib.require_inputs(data.get("items"), "item")
        sys.exit(gatelib.FAIL if any(i.get("bad") for i in items) else gatelib.PASS)
        """

    CONFIG = """\
        gates:
          - name: demo_gate
            cannot_args: ["{badjson}"]
            fail_args: ["{fixture}"]
            fail_fixture_body: '{"items": [{"bad": true}]}'
        """

    def test_obeying_gate_passes(self):
        self.p.write("scripts/demo_gate.py", self.GATE)
        self.p.write("loop.config.yaml", self.CONFIG)
        self.assertExit(PASS, self.p.run("harness/conformance/test_exit_codes.py"))

    def test_sabotaged_gate_goes_red(self):
        sabotaged = self.GATE.replace(
            'sys.exit(gatelib.FAIL if any(i.get("bad") for i in items) else gatelib.PASS)',
            "sys.exit(gatelib.PASS)")
        self.assertNotEqual(sabotaged, self.GATE)
        self.p.write("scripts/demo_gate.py", sabotaged)
        self.p.write("loop.config.yaml", self.CONFIG)
        self.assertExit(FAIL, self.p.run("harness/conformance/test_exit_codes.py"))


class TestGateTemplate(KitTestCase):
    """templates/gate.py is what users copy for every gate, so it must pass the
    conformance test out of the box with the recipe documented in loop.config.yaml."""

    CONFIG = """\
        gates:
          - name: cause_gate
            cannot_args: ["{badjson}"]
            fail_args: ["{fixture}"]
            fail_fixture_body: '{"items": [{"id": "x"}]}'
        """

    def install_template(self, transform=lambda s: s):
        src = (self.p.root / "templates/gate.py").read_text()
        out = transform(src)
        self.p.write("scripts/cause_gate.py", out)
        self.p.write("loop.config.yaml", self.CONFIG)
        return src, out

    def test_template_passes_conformance(self):
        self.install_template()
        self.assertExit(PASS, self.p.run("harness/conformance/test_exit_codes.py"))

    def test_template_verdicts(self):
        self.install_template()
        self.p.write("ok.json", '{"items": [{"id": "a", "cause": "c"}]}')
        self.p.write("bad.json", '{"items": [{"id": "a"}]}')
        self.p.write("none.json", '{"items": []}')
        self.assertExit(PASS, self.p.run("scripts/cause_gate.py", "ok.json"))
        self.assertExit(FAIL, self.p.run("scripts/cause_gate.py", "bad.json"))
        self.assertExit(CANNOT, self.p.run("scripts/cause_gate.py", "none.json"))

    def test_sabotaged_template_goes_red(self):
        src, out = self.install_template(
            lambda s: s.replace("    problems = []\n", "    return []\n    problems = []\n", 1))
        self.assertNotEqual(src, out)
        self.assertExit(FAIL, self.p.run("harness/conformance/test_exit_codes.py"))


class TestHarnessRunner(KitTestCase):
    """harness/run_all.py folds the rule test and every lesson check into one verdict."""

    OK = "import sys; sys.exit(0)\n"
    BAD = "import sys; print('defect present'); sys.exit(1)\n"
    CRASH = "raise RuntimeError('boom')\n"

    def test_nothing_to_run_is_cannot(self):
        self.assertExit(CANNOT, self.p.run("harness/run_all.py", "--no-conformance"))

    def test_conformance_without_gates_is_cannot(self):
        self.p.write("harness/some-lesson/test_a.py", self.OK)
        self.assertExit(CANNOT, self.p.run("harness/run_all.py"))

    def test_passing_lessons(self):
        self.p.write("harness/one-lesson/test_a.py", self.OK)
        self.p.write("harness/two-lesson/test_b.py", self.OK)
        out = self.assertExit(PASS, self.p.run("harness/run_all.py", "--no-conformance"))
        self.assertIn("2/2", out)

    def test_one_failing_lesson_fails_all(self):
        self.p.write("harness/one-lesson/test_a.py", self.OK)
        self.p.write("harness/two-lesson/test_b.py", self.BAD)
        out = self.assertExit(FAIL, self.p.run("harness/run_all.py", "--no-conformance"))
        self.assertIn("defect present", out)

    def test_crashing_lesson_is_not_a_verdict(self):
        self.p.write("harness/one-lesson/test_a.py", self.CRASH)
        rc, out = self.p.run("harness/run_all.py", "--no-conformance")
        self.assertEqual(rc, CANNOT, out)

    def test_conformance_and_lessons_together(self):
        self.p.write("scripts/cause_gate.py", (self.p.root / "templates/gate.py").read_text())
        self.p.write("loop.config.yaml", TestGateTemplate.CONFIG)
        self.p.write("harness/one-lesson/test_a.py", self.OK)
        out = self.assertExit(PASS, self.p.run("harness/run_all.py"))
        self.assertIn("2/2", out)


COMPARE_CONFIG = """\
    stages:
      - {id: "1", name: intake}
      - {id: "2", name: answer}
    compare:
      unit: one invoice
      fields:
        - {name: total, rule: number, tol: 0.01}
        - {name: vendor, rule: text}
        - {name: tags, rule: set}
      failure_classes:
        - {id: input_misread, means: "input read wrong"}
        - {id: reasoning_error, means: "conclusion wrong"}
    """

KEY = {"items": [
    {"id": "a", "expected": {"total": 1204.5, "vendor": "ACME Corp", "tags": ["x", "y"]}},
    {"id": "b", "expected": {"total": 10, "vendor": "Beta", "tags": ["z"]}, "weight": 2},
    {"id": "c", "expected": {"total": 5, "vendor": "Gamma", "tags": []}},
    {"id": "d", "expected": {"total": 7, "vendor": "Delta", "tags": ["q"]}},
]}

ANSWERS = {"items": [
    {"id": "a", "answer": {"total": "1,204.50", "vendor": "  acme   corp ", "tags": "y, x"}},
    {"id": "b", "answer": {"total": 11, "vendor": "Beta", "tags": ["z"]}},
    {"id": "d", "answer": {"total": "seven", "vendor": "Delta", "tags": ["q"]}},
    {"id": "zz", "answer": {"total": 1, "vendor": "x", "tags": []}},
]}


class TestCompare(KitTestCase):
    """② answers vs key, by rule — the step that writes scored.json."""

    def setUp(self):
        super().setUp()
        self.p.write("loop.config.yaml", COMPARE_CONFIG)
        self.p.write("runs/r/answers.json", json.dumps(ANSWERS))
        self.key = self.p.write("sealed/key.json", json.dumps(KEY))

    def scored(self):
        return {i["id"]: i for i in
                json.loads((self.p.root / "runs/r/scored.json").read_text())["items"]}

    def compare(self, *extra):
        return self.p.run("scripts/compare.py", "--round", "runs/r", "--key",
                          str(self.key), *extra)

    def test_outcomes_per_problem(self):
        out = self.assertExit(PASS, self.compare())
        s = self.scored()
        self.assertTrue(s["a"]["found"] and s["a"]["delivered"])     # normalised match
        self.assertEqual(s["b"]["failure_class"], "wrong")
        self.assertEqual(s["c"]["failure_class"], "not_attempted")
        self.assertEqual(s["d"]["failure_class"], "format")
        self.assertIn("1 / 4", out.replace("   ", " ").replace("  ", " "))
        data = json.loads((self.p.root / "runs/r/scored.json").read_text())
        self.assertEqual(data["extra"], ["zz"])
        self.assertEqual(data["key_total"], 4)

    def test_number_tolerance(self):
        ans = json.loads(json.dumps(ANSWERS))
        ans["items"][1]["answer"]["total"] = 10.005
        self.p.write("runs/r/answers.json", json.dumps(ans))
        self.assertExit(PASS, self.compare())
        self.assertTrue(self.scored()["b"]["found"])

    def test_undelivered_answer(self):
        ans = json.loads(json.dumps(ANSWERS))
        ans["items"][0]["delivered"] = False
        self.p.write("runs/r/answers.json", json.dumps(ans))
        self.assertExit(PASS, self.compare())
        s = self.scored()["a"]
        self.assertTrue(s["found"])
        self.assertFalse(s["delivered"])

    def test_judge_fields_block_until_judged(self):
        self.p.write("loop.config.yaml", COMPARE_CONFIG.replace(
            "        - {name: tags, rule: set}\n", "        - {name: tags, rule: judge}\n"))
        self.assertExit(FAIL, self.compare())
        self.assertEqual(self.scored()["a"]["failure_class"], "judge_pending")
        self.p.write("runs/r/judgements.json", json.dumps({"items": [
            {"id": "a", "field": "tags", "match": True, "reason": "same"},
            {"id": "b", "field": "tags", "match": True, "reason": "same"},
            {"id": "d", "field": "tags", "match": False, "reason": "differs"}]}))
        out = self.assertExit(PASS, self.compare())
        self.assertIn("decided by a judge", out)
        self.assertTrue(self.scored()["a"]["found"])

    def test_rerun_keeps_recorded_analysis(self):
        self.assertExit(PASS, self.compare())
        path = self.p.root / "runs/r/scored.json"
        data = json.loads(path.read_text())
        for it in data["items"]:
            if it["id"] == "b":
                it.update(failure_class="reasoning_error", died_at_stage="2", cause="c")
        path.write_text(json.dumps(data))
        self.assertExit(PASS, self.compare())
        b = self.scored()["b"]
        self.assertEqual((b["failure_class"], b["died_at_stage"], b["cause"]),
                         ("reasoning_error", "2", "c"))

    def test_cannot_without_rules_key_or_answers(self):
        self.p.write("loop.config.yaml", "stages: [{id: '1', name: a}]\ncompare: {fields: []}\n")
        self.assertExit(CANNOT, self.compare())
        self.p.write("loop.config.yaml", COMPARE_CONFIG)
        self.assertExit(CANNOT, self.p.run("scripts/compare.py", "--round", "runs/r",
                                           "--key", "nope.json"))
        self.p.write("runs/r/answers.json", '{"items": []}')
        self.assertExit(CANNOT, self.compare())

    def test_duplicate_ids_are_cannot(self):
        self.p.write("runs/r/answers.json", json.dumps(
            {"items": [ANSWERS["items"][0], ANSWERS["items"][0]]}))
        self.assertExit(CANNOT, self.compare())


class TestFailures(KitTestCase):
    """④ every failure gets a class, a stage and a cause before the round is reported."""

    def setUp(self):
        super().setUp()
        self.p.write("loop.config.yaml", COMPARE_CONFIG)
        self.p.write("runs/r/answers.json", json.dumps(ANSWERS))
        key = self.p.write("sealed/key.json", json.dumps(KEY))
        self.assertExit(PASS, self.p.run("scripts/compare.py", "--round", "runs/r",
                                         "--key", str(key)))

    def failures(self, *extra):
        return self.p.run("scripts/failures.py", "--round", "runs/r", *extra)

    def test_unanalysed_failures_block(self):
        out = self.assertExit(FAIL, self.failures())
        for pid in ("b", "c", "d"):
            self.assertIn(f"- {pid}:", out)

    def test_apply_then_pass_and_count(self):
        self.p.write("analysis.json", json.dumps({"items": [
            {"id": "b", "failure_class": "reasoning_error", "died_at_stage": "2",
             "cause": "rounds totals before summing"},
            {"id": "c", "failure_class": "not_attempted", "died_at_stage": "1",
             "cause": "intake skips scanned PDFs"},
            {"id": "d", "failure_class": "input_misread", "died_at_stage": "1",
             "cause": "spelled-out numbers are not converted"}]}))
        self.assertExit(PASS, self.failures("--apply", "analysis.json"))
        out = self.assertExit(PASS, self.failures("--json"))
        rep = json.loads(out)
        self.assertEqual(rep["by_class"], {"reasoning_error": 2.0, "not_attempted": 1.0,
                                           "input_misread": 1.0})
        self.assertEqual(rep["largest_cell"]["failure_class"], "reasoning_error")

    def test_apply_rejects_bad_rows_and_writes_nothing(self):
        before = (self.p.root / "runs/r/scored.json").read_text()
        self.p.write("analysis.json", json.dumps({"items": [
            {"id": "b", "failure_class": "reasoning_error", "died_at_stage": "2",
             "cause": "ok"},
            {"id": "c", "failure_class": "wrong", "died_at_stage": "1", "cause": "x"},
            {"id": "d", "failure_class": "made_up", "died_at_stage": "9", "cause": ""},
            {"id": "a", "failure_class": "input_misread", "died_at_stage": "1",
             "cause": "x"}]}))
        out = self.assertExit(FAIL, self.failures("--apply", "analysis.json"))
        self.assertIn("symptom", out)
        self.assertIn("succeeded", out)
        self.assertEqual((self.p.root / "runs/r/scored.json").read_text(), before)

    def test_no_failures_is_pass(self):
        key = self.p.write("sealed/key2.json", json.dumps({"items": [KEY["items"][0]]}))
        self.p.write("runs/r/scored.json", "")
        (self.p.root / "runs/r/scored.json").unlink()
        self.assertExit(PASS, self.p.run("scripts/compare.py", "--round", "runs/r",
                                         "--key", str(key)))
        out = self.assertExit(PASS, self.failures())
        self.assertIn("no failures", out)

    def test_cannot_without_scored(self):
        (self.p.root / "runs/r/scored.json").unlink()
        self.assertExit(CANNOT, self.failures())


class TestLayerRequiresComparison(KitTestCase):
    def test_check_names_missing_comparison(self):
        self.assertExit(PASS, self.p.run("scripts/new_domain.py", "--name", "demo"))
        layer = self.p.root / "domains/demo"
        self.assertTrue((layer / "COMPARE.md").is_file())
        out = self.assertExit(FAIL, self.p.run("scripts/new_domain.py", "--check",
                                               "domains/demo"))
        self.assertIn("compare field is still a placeholder", out)
        self.assertIn("failure class is still a placeholder", out)
        (layer / "COMPARE.md").unlink()
        out = self.assertExit(FAIL, self.p.run("scripts/new_domain.py", "--check",
                                               "domains/demo"))
        self.assertIn("no COMPARE.md", out)


class TestLoopState(unittest.TestCase):
    def test_no_kit_is_cannot(self):
        p = Project(install_kit=False)
        try:
            shutil.copytree(KIT / "scripts", p.root / "_tools")
            rc, out = p.run("_tools/loop_state.py")
            self.assertEqual(rc, CANNOT, out)
        finally:
            p.close()

    def test_fresh_install_starts_at_interview(self):
        p = Project()
        try:
            rc, out = p.run("scripts/loop_state.py")
            self.assertEqual(rc, PASS, out)
            self.assertIn("setup:interview", out)
        finally:
            p.close()


class TestEveryToolHasHelp(unittest.TestCase):
    def test_help_exits_zero(self):
        p = Project()
        try:
            tools = sorted((p.root / "scripts").glob("*.py")) + \
                [p.root / "harness/conformance/test_exit_codes.py"]
            self.assertGreaterEqual(len(tools), 8)
            for t in tools:
                rc, out = p.run(str(t.relative_to(p.root)), "--help")
                self.assertEqual(rc, 0, f"{t.name} --help exited {rc}\n{out}")
        finally:
            p.close()


if __name__ == "__main__":
    unittest.main()
