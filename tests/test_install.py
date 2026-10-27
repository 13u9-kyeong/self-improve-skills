"""Packaging: the standalone installer, the in-project kit installer, and the plugin manifests.

    python3 -m unittest tests.test_install -v
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "selfimprove"
KIT = SKILL / "kit"


def kit_files():
    return sorted(p.relative_to(KIT) for p in KIT.rglob("*")
                  if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")


class TestInstallSh(unittest.TestCase):
    def run_install(self, *args, home=None, cwd=None):
        env = dict(os.environ)
        if home:
            env["HOME"] = str(home)
        return subprocess.run(["bash", str(REPO / "install.sh"), *args], env=env,
                              cwd=cwd or REPO, capture_output=True, text=True, timeout=60)

    def test_user_install_copies_skill_and_whole_kit(self):
        with tempfile.TemporaryDirectory() as home:
            p = self.run_install(home=home)
            self.assertEqual(p.returncode, 0, p.stderr)
            dest = Path(home) / ".claude" / "skills" / "selfimprove"
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertTrue((dest / "install_kit.py").is_file())
            installed = sorted(q.relative_to(dest / "kit") for q in (dest / "kit").rglob("*")
                               if q.is_file())
            self.assertEqual(installed, kit_files())
            self.assertFalse(list(dest.rglob(".git")), "a .git leaked into the skill")
            self.assertFalse(list(dest.rglob("__pycache__")))

    def test_project_install(self):
        with tempfile.TemporaryDirectory() as proj:
            p = self.run_install("--project", cwd=proj)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertTrue((Path(proj) / ".claude/skills/selfimprove/SKILL.md").is_file())

    def test_reinstall_replaces_stale_files(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertEqual(self.run_install(home=home).returncode, 0)
            stale = Path(home) / ".claude/skills/selfimprove/kit/stale.md"
            stale.write_text("left over from an older version")
            self.assertEqual(self.run_install(home=home).returncode, 0)
            self.assertFalse(stale.exists())

    def test_bad_flag_is_usage(self):
        with tempfile.TemporaryDirectory() as home:
            self.assertEqual(self.run_install("--bogus", home=home).returncode, 3)


class TestInstallKit(unittest.TestCase):
    def run_kit(self, *args):
        return subprocess.run([sys.executable, str(SKILL / "install_kit.py"), *args],
                              capture_output=True, text=True, timeout=60)

    def test_installs_into_empty_project(self):
        with tempfile.TemporaryDirectory() as proj:
            p = self.run_kit("--into", proj)
            self.assertEqual(p.returncode, 0, p.stderr)
            for rel in kit_files():
                self.assertTrue((Path(proj) / rel).is_file(), rel)
            state = subprocess.run([sys.executable, "scripts/loop_state.py"], cwd=proj,
                                   capture_output=True, text=True)
            self.assertEqual(state.returncode, 0, state.stderr)
            self.assertIn("setup:interview", state.stdout)

    def test_never_overwrites_and_reports_claude_md(self):
        with tempfile.TemporaryDirectory() as proj:
            mine = Path(proj) / "CLAUDE.md"
            mine.write_text("# my project rules\n")
            p = self.run_kit("--into", proj)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(mine.read_text(), "# my project rules\n")
            self.assertIn("CLAUDE.md", p.stdout)
            self.assertIn("Self-improvement loop", p.stdout)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as proj:
            p = self.run_kit("--into", proj, "--dry-run")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(list(Path(proj).iterdir()), [])

    def test_missing_target_is_cannot(self):
        self.assertEqual(self.run_kit("--into", "/nonexistent/dir/xyz").returncode, 2)

    def test_no_args_is_usage_not_verdict(self):
        self.assertIn(self.run_kit().returncode, (2, 3))


class TestAgentTemplates(unittest.TestCase):
    """The scoring agents ship; the adversarial passes ship but say they are optional."""

    AGENTS = KIT / "templates" / "agents"

    def test_expected_set(self):
        names = sorted(p.stem for p in self.AGENTS.glob("*.md"))
        self.assertEqual(names, ["answer-judge", "blind-rereader", "failure-analyst",
                                 "refuter"])

    def test_optional_passes_say_so(self):
        for name in ("refuter", "blind-rereader"):
            self.assertIn("**Optional pass.**", (self.AGENTS / f"{name}.md").read_text())
        for name in ("failure-analyst", "answer-judge"):
            self.assertNotIn("Optional pass", (self.AGENTS / f"{name}.md").read_text())

    def test_every_template_has_frontmatter(self):
        for p in self.AGENTS.glob("*.md"):
            t = p.read_text()
            self.assertTrue(t.startswith("---\n"), p.name)
            front = t.split("---\n")[1]
            self.assertIn(f"name: {p.stem}", front)
            self.assertIn("description:", front)

    def test_no_reference_to_removed_agent(self):
        hits = [str(p.relative_to(REPO)) for root in (SKILL, REPO / "README.md",
                REPO / "README.ko.md") for p in ([root] if root.is_file() else root.rglob("*"))
                if p.is_file() and "second-loser" in p.read_text(errors="replace")]
        self.assertEqual(hits, [])


class TestManifests(unittest.TestCase):
    def test_plugin_and_marketplace_agree(self):
        plugin = json.loads((REPO / ".claude-plugin/plugin.json").read_text())
        market = json.loads((REPO / ".claude-plugin/marketplace.json").read_text())
        self.assertEqual(plugin["name"], "selfimprove")
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        names = [p["name"] for p in market["plugins"]]
        self.assertIn(plugin["name"], names)
        self.assertTrue(market["owner"]["name"])

    def test_version_matches_changelog(self):
        plugin = json.loads((REPO / ".claude-plugin/plugin.json").read_text())
        self.assertIn(f"## [{plugin['version']}]", (REPO / "CHANGELOG.md").read_text())

    def test_readme_pin_matches_version(self):
        plugin = json.loads((REPO / ".claude-plugin/plugin.json").read_text())
        for name in ("README.md", "README.ko.md"):
            pins = re.findall(r"#v(\d+\.\d+\.\d+)", (REPO / name).read_text())
            self.assertEqual(set(pins), {plugin["version"]}, name)

    def test_skill_frontmatter(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\n"))
        front = text.split("---\n")[1]
        self.assertIn("name: selfimprove", front)
        self.assertIn("description:", front)
        self.assertLess(len(text.splitlines()), 500, "SKILL.md should stay under 500 lines")

    def test_skill_resolves_kit_through_skill_dir(self):
        # A hard-coded ~/.claude path breaks plugin installs, which live elsewhere.
        text = (SKILL / "SKILL.md").read_text()
        self.assertIn("${CLAUDE_SKILL_DIR}/install_kit.py", text)
        self.assertNotIn("~/.claude/skills/selfimprove/kit", text)


if __name__ == "__main__":
    unittest.main()
