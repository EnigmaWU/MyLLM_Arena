# US-22 Run Test Case Instruction

## Story Summary

US-22 proves Scope D (all text: source + documentation) works end-to-end — all non-blank lines from both source and doc files are counted.

## Run All US-22 Tests

```bash
python3 -m pytest -q tests/test_us22_scope_d_all_text_tdd.py -v
```

## Test Files

### test_us22_scope_d_all_text_tdd.py

```bash
python3 -m pytest -q tests/test_us22_scope_d_all_text_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_d_counts_all_non_blank_lines_from_source_and_doc_files` | `--scope D` counts all non-blank lines from both source and doc files | totalCodeLines = source lines + doc lines |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us22_scope_d_all_text_tdd.py::TestUs22ScopeDAllTextTdd::test_scope_d_counts_all_non_blank_lines_from_source_and_doc_files" -v
```
