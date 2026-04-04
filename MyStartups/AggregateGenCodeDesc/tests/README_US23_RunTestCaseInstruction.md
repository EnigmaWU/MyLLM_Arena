# US-23 Run Test Case Instruction

## Story Summary

US-23 is the scope parity matrix for Algorithm A — verifies all four scopes (A/B/C/D) produce valid, correctly-shaped summaries with isolation between scopes.

## Run All US-23 Tests

```bash
python3 -m pytest -q tests/test_us23_scope_parity_matrix_tdd.py -v
```

## Test Files

### test_us23_scope_parity_matrix_tdd.py

```bash
python3 -m pytest -q tests/test_us23_scope_parity_matrix_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_all_four_scopes_produce_valid_summaries_with_correct_field_names` | All scopes produce `totalCodeLines`, `fullGeneratedCodeLines`, `partialGeneratedCodeLines` | All 4 outputs have correct shape |
| `test_scope_a_counts_only_code_lines_excluding_comments` | Scope A excludes comment lines | totalCodeLines < Scope B |
| `test_scope_b_counts_code_and_comment_lines` | Scope B includes comment lines alongside code | totalCodeLines ≥ Scope A |
| `test_scope_c_counts_only_doc_file_lines` | Scope C counts only doc files | totalCodeLines reflects doc lines only |
| `test_scope_d_counts_all_source_and_doc_lines` | Scope D = union of source + doc | totalCodeLines = max across A/B/C variants |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us23_scope_parity_matrix_tdd.py::TestUs23ScopeParityMatrixTdd::test_scope_a_counts_only_code_lines_excluding_comments" -v
```
