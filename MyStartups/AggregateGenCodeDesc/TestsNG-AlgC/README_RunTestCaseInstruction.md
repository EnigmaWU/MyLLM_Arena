# AggregateGenCodeDesc — Algorithm C Run Test Case Instruction

## Purpose

This document is the TDD entry point for Algorithm C executable tests.

Current scope in this folder:

- `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01`
- Git-origin fixture
- SVN-origin fixture
- parity-style summary check across the two origins

The tests in `TestsNG-AlgC` are written before runtime implementation is complete.
During the initial TDD phase, red results are expected until the corresponding AlgC slice is implemented.

## Run The First AlgC TDD File

```bash
python3 -m pytest -q TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py -v
```

## Run One TC Only

```bash
python3 -m pytest -q "TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py::TestUsngAlgcHistorySimpleScopeA01Tdd::test_cli_matches_git_expected_result" -v
```

## Expected TDD Lifecycle

1. First run: fail because `--algorithm C` is not implemented yet.
2. After first AlgC slice lands: Git fixture should pass.
3. Then SVN fixture should pass.
4. Then the parity-style contract check should pass.

## Fixture Location

- Git fixture: `TestdataNG-AlgC/history-simple/scope-a/01/git/default`
- SVN fixture: `TestdataNG-AlgC/history-simple/scope-a/01/svn/default`

## What The First TDD File Proves

- Algorithm C can consume only `genCodeDescProtoV26.04` files.
- No repository checkout is required at runtime.
- Incremental add/delete accumulation produces the expected live surviving set.
- Time-window filtering is based on embedded `blame.timestamp`.
- Git-origin and SVN-origin produce the same `SUMMARY` contract for the same logical scenario.