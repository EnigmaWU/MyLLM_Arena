# US-25 Run Test Case Instruction

## Story Summary

US-25 proves Algorithm B + Scope C (documentation text lines via live-changed replay) works correctly.

## Run All US-25 Tests

```bash
python3 -m pytest -q tests/test_us25_algorithm_b_scope_c_tdd.py -v
```

## Test Files

### test_us25_algorithm_b_scope_c_tdd.py

```bash
python3 -m pytest -q tests/test_us25_algorithm_b_scope_c_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_algorithm_b_scope_c_counts_doc_lines_via_live_changed` | AlgB + `--scope C` counts doc lines via live-changed replay | totalCodeLines reflects doc lines only |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us25_algorithm_b_scope_c_tdd.py::TestUs25AlgorithmBScopeC::test_algorithm_b_scope_c_counts_doc_lines_via_live_changed" -v
```
