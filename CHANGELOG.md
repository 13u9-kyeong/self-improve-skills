# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-10-27

First release on GitHub.

### Added
- The `/selfimprove` skill (`skills/selfimprove/SKILL.md`): interviews the user, builds a
  domain layer and its gates, then runs scored rounds against a sealed key.
- The kit (`skills/selfimprove/kit/`), installed into a project by `install_kit.py` without
  ever overwriting a file: loop rules L-1…L-16 (`CLAUDE.md`), orchestrator duties D-1…D-8,
  phase-0 gates, round procedure, scoring, contamination and verification guides.
- Answer-vs-key comparison (`scripts/compare.py`) and failure analysis
  (`scripts/failures.py`): every problem is compared with its key entry by fixed field
  rules, and every failure must carry a class, a stage and a cause before a round is
  reported.
- Tools obeying one exit-code rule (`0 PASS · 1 FAIL · 2 CANNOT · 3 USAGE`), the
  conformance test and `harness/run_all.py`.
- Agent templates: `failure-analyst` and `answer-judge` (scoring), `refuter` and
  `blind-rereader` (optional, for stages that drop or accept candidates before delivery).
- Domain-layer template with seven components and `new_domain.py --check`.
- Plugin packaging (`.claude-plugin/`), standalone `install.sh`, English and Korean READMEs,
  and a standard-library test suite.
