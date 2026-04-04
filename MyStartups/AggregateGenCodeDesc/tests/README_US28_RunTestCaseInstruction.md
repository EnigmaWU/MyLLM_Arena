# US-28 Run Test Case Instruction

## Story Summary

US-28 hardens production readiness: invalid `--scope` values are rejected early, and oversized VCS output is blocked by a file-size guard.

## Run All US-28 Tests

```bash
python3 -m pytest -q tests/test_us28_production_hardening_tdd.py -v
```

## Test Files

### test_us28_production_hardening_tdd.py

```bash
python3 -m pytest -q tests/test_us28_production_hardening_tdd.py -v
```

#### Class: TestInvalidScopeRejection

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_Z_rejected_algorithm_a` | `--scope Z` is rejected for Algorithm A | Exits with error mentioning invalid scope |
| `test_scope_Z_rejected_algorithm_b` | `--scope Z` is rejected for Algorithm B | Exits with error mentioning invalid scope |
| `test_scope_lowercase_a_rejected` | `--scope a` (lowercase) is rejected | Exits with error (scopes are case-sensitive) |
| `test_scope_empty_rejected` | `--scope ""` (empty string) is rejected | Exits with error mentioning invalid scope |

#### Class: TestFileSizeGuard

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_read_git_file_rejects_oversized_output` | Git file output exceeding MAX_FILE_SIZE_BYTES is rejected | Raises error before processing |
| `test_read_git_file_accepts_normal_output` | Git file output within limit is accepted | Processes normally, no error |
| `test_parse_blame_rejects_oversized_output` | Blame output exceeding MAX_FILE_SIZE_BYTES is rejected | Raises error before processing |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us28_production_hardening_tdd.py::TestInvalidScopeRejection::test_scope_Z_rejected_algorithm_a" -v
```
