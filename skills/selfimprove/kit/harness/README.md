# harness/

Mechanical checks that keep the loop honest. There are two kinds of check here, and only the
first one ships with the kit.

```
harness/
  run_all.py                    runs everything below; one verdict under the exit-code rule
  conformance/
    test_exit_codes.py       shipped: every gate in loop.config.yaml obeys the rule (L-9)
  <lesson>/                     added by the loop, one directory per learned card (L-10)
    test_<what>.py
```

## `conformance/` — the one built-in check

`conformance/test_exit_codes.py` is not an example. It is the domain-independent
conformance test: it reads `gates:` from `loop.config.yaml` and asserts the exit-code
rule (`0 PASS · 1 FAIL · 2 CANNOT · 3 USAGE`) on every gate, on three axes. Your gates
change per domain; this test does not.

It exits 2 (CANNOT) while `gates:` is empty, because a conformance test over zero gates has
checked nothing.

## `<lesson>/` — one check per measured loss

Every loss a round measures becomes a learned card in `references/learned/<lesson>.md` and a
check in `harness/<lesson>/test_*.py`, in the same commit (L-10). The check:

- runs as a standalone script from the project root (`python3 harness/<lesson>/test_x.py`);
- calls the real pipeline tool or reads the real artifact the defect lived in;
- obeys the exit-code rule: `0` when the defect is absent, `1` when it is present, `2` when it
  cannot tell;
- is sabotage-verified before it is committed: reintroduce the defect, watch it exit 1,
  remove the defect, watch it exit 0.

Name the directory after the structural condition, not the target where it was found (the
card linter rules apply, L-11).

## Running

```bash
python3 harness/run_all.py                 # conformance test + every lesson check
python3 harness/run_all.py --no-conformance   # before setup:gates, when no gate exists yet
```

`ROUND.md` runs this before a round starts and again before results are reported.
