# US-21 Run Test Case Instruction

## Story Summary

US-21 proves Scope C (documentation text lines only) works end-to-end — only doc file lines are counted, using the `docLines` protocol field.

## Run All US-21 Tests

```bash
python3 -m pytest -q tests/test_us21_scope_c_doc_lines_tdd.py -v
```

## Test Files

### test_us21_scope_c_doc_lines_tdd.py

```bash
python3 -m pytest -q tests/test_us21_scope_c_doc_lines_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_c_counts_doc_file_lines_using_doc_lines_protocol` | `--scope C` counts only doc file lines from the `docLines` protocol field | totalCodeLines reflects only doc lines |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us21_scope_c_doc_lines_tdd.py::TestUs21ScopeCDocLinesTdd::test_scope_c_counts_doc_file_lines_using_doc_lines_protocol" -v
```
