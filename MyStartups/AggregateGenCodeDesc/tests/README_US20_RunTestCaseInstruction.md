# US-20 Run Test Case Instruction

## Story Summary

US-20 proves Scope B (source code **with** comments) works end-to-end — comment lines are counted alongside code lines.

## Run All US-20 Tests

```bash
python3 -m pytest -q tests/test_us20_scope_b_source_with_comments_tdd.py -v
```

## Test Files

### test_us20_scope_b_source_with_comments_tdd.py

```bash
python3 -m pytest -q tests/test_us20_scope_b_source_with_comments_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_scope_b_counts_comment_lines_alongside_code_lines` | `--scope B` counts comment lines alongside code lines in the SUMMARY | totalCodeLines includes comment lines |

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us20_scope_b_source_with_comments_tdd.py::TestUs20ScopeBSourceWithCommentsTdd::test_scope_b_counts_comment_lines_alongside_code_lines" -v
```
