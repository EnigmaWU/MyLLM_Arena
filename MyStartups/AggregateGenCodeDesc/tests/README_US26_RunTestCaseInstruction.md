# US-26 Run Test Case Instruction

## Story Summary

US-26 proves Algorithm B + Scope D (source + documentation text lines via live-changed replay) works correctly.

## Run All US-26 Tests

```bash
python3 -m pytest -q tests/test_us26_algorithm_b_scope_d_tdd.py -v
```

## Test Files

### test_us26_algorithm_b_scope_d_tdd.py

```bash
python3 -m pytest -q tests/test_us26_algorithm_b_scope_d_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scope_d_counts_source_and_doc_lines_via_live_changed` | AlgB + `--scope D` counts both source and doc lines via live-changed replay | totalCodeLines reflects source + doc lines combined |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us26_algorithm_b_scope_d_tdd.py::TestUs26AlgorithmBScopeD::test_algorithm_b_scope_d_counts_source_and_doc_lines_via_live_changed" -v
```
