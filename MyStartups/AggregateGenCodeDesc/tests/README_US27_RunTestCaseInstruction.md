# US-27 Run Test Case Instruction

## Story Summary

US-27 verifies cross-algorithm × cross-scope parity: Algorithm A and Algorithm B produce identical summaries for the same input when using the same scope.

## Run All US-27 Tests

```bash
python3 -m pytest -q tests/test_us27_cross_algorithm_scope_parity_tdd.py -v
```

## Test Files

### test_us27_cross_algorithm_scope_parity_tdd.py

```bash
python3 -m pytest -q tests/test_us27_cross_algorithm_scope_parity_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_a_algorithm_a_and_b_produce_same_summary` | Scope A parity: AlgA and AlgB yield identical summary | Summaries match exactly |
| `test_scope_b_algorithm_a_and_b_produce_same_summary` | Scope B parity: AlgA and AlgB yield identical summary | Summaries match exactly |
| `test_scope_c_algorithm_a_and_b_produce_same_summary` | Scope C parity: AlgA and AlgB yield identical summary | Summaries match exactly |
| `test_scope_d_algorithm_a_and_b_produce_same_summary` | Scope D parity: AlgA and AlgB yield identical summary | Summaries match exactly |
| `test_cross_algorithm_contract_shape_matches_for_all_scopes` | All four scopes produce same JSON shape across both algorithms | Output keys and structure match for every scope pair |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us27_cross_algorithm_scope_parity_tdd.py::TestUs27CrossAlgorithmScopeParityTdd::test_scope_a_algorithm_a_and_b_produce_same_summary" -v
```
