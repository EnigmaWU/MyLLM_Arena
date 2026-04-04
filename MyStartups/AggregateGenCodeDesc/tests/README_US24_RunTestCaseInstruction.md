# US-24 Run Test Case Instruction

## Story Summary

US-24 proves Algorithm B + Scope B (source code with comments via live-changed replay) works correctly.

## Run All US-24 Tests

```bash
python3 -m pytest -q tests/test_us24_algorithm_b_scope_b_tdd.py -v
```

## Test Files

### test_us24_algorithm_b_scope_b_tdd.py

```bash
python3 -m pytest -q tests/test_us24_algorithm_b_scope_b_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scope_b_counts_comments_via_live_changed` | AlgB + `--scope B` counts comment lines alongside code via live-changed replay | totalCodeLines includes comments |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us24_algorithm_b_scope_b_tdd.py::TestUs24AlgorithmBScopeB::test_algorithm_b_scope_b_counts_comments_via_live_changed" -v
```
