# Contributing

Thanks for helping. This project is small and opinionated; the notes below keep it that way.

## Ground rules

1. **The kit stays domain-neutral.** Nothing under `skills/selfimprove/` may depend on one
   domain's vocabulary, tools or examples. `tests/test_neutral.py` enforces a list of banned
   terms; if you need a worked example for a specific domain, publish it as a separate
   repository that builds a layer with `new_domain.py`.
2. **Rules carry their measurements.** A new rule in `kit/CLAUDE.md` (L-n) or a new
   orchestrator duty (D-n) states the measurement that produced it and what it cost. A rule
   with no cost attached is the first one a future round argues away.
3. **Every tool obeys the exit-code rule** (`kit/scripts/gatelib.py`):
   `0 PASS · 1 FAIL · 2 CANNOT (not a pass) · 3 USAGE`. Empty input is never a pass, a
   crash is never a verdict, a missing dependency is CANNOT.
4. **A fix ships with a test that fails on the original defect.** Verify it by sabotage:
   reintroduce the bug, watch the test go red, restore. Say in the PR that you did.

## Development

```bash
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
uv run --python 3.9 --with pyyaml python -m unittest discover -s tests   # oldest supported
claude plugin validate .            # if you changed .claude-plugin/
./install.sh --project              # try the skill in a scratch project
```

There is no CI; run the suite yourself before pushing, on the oldest supported Python as
well. Python 3.9+ and the standard library only (plus PyYAML). No new runtime dependencies without
a strong reason.

## Layout

```
.claude-plugin/          plugin + marketplace manifests
skills/selfimprove/
  SKILL.md               the skill: the flow the agent follows
  install_kit.py         copies kit/ into a project, never overwriting
  kit/                   everything that lands in the user's project
tests/                   unittest suite (exit codes, installers, neutrality, README parity)
install.sh               standalone install without the plugin system
```

## Releasing

1. Bump `version` in `.claude-plugin/plugin.json`.
2. Add a matching `## [x.y.z]` section to `CHANGELOG.md` (a test checks they agree).
3. Tag `vx.y.z` and push the tag. Users can pin with
   `/plugin marketplace add https://github.com/13u9-kyeong/self-improve-skills.git#vx.y.z`.
