# AggregateGenCodeDesc — Algorithm C Run Test Case Instruction

## Purpose

This document is the TDD entry point for Algorithm C executable tests.

Current scope in this folder:

- `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01`
- `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08`
- Git-origin fixtures
- SVN-origin fixtures

The tests in `TestsNG-AlgC` are written before runtime implementation is complete.
During the initial TDD phase, red results are expected until the corresponding AlgC slice is implemented.

## Run The Covered AlgC TDD Files

```bash
python3 -m pytest -q TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_08_tdd.py -v
```

## Run One TC Only

```bash
python3 -m pytest -q "TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py::TestUsngAlgcHistorySimpleScopeA01Tdd::test_cli_matches_git_expected_result" -v
python3 -m pytest -q "TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_08_tdd.py::TestUsngAlgcHistorySimpleScopeA08Tdd::test_git_and_svn_share_same_observable_summary_contract" -v
```

## Expected TDD Lifecycle

1. First run: fail because `--algorithm C` is not implemented yet.
2. After `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01` lands: Git fixture should pass.
3. Then the SVN fixture should pass.
4. After `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08` lands: the cross-VCS contract and no-VCS-runtime checks should pass.

## Fixture Location

- `A-01` Git fixture: `TestdataNG-AlgC/history-simple/scope-a/01/git/default`
- `A-01` SVN fixture: `TestdataNG-AlgC/history-simple/scope-a/01/svn/default`
- `A-08` Git fixture: `TestdataNG-AlgC/history-simple/scope-a/08/git/default`
- `A-08` SVN fixture: `TestdataNG-AlgC/history-simple/scope-a/08/svn/default`

## What The Covered TDD Files Prove

- `A-01` proves Algorithm C can consume only `genCodeDescProtoV26.04` files, accumulate add/delete history, and compute the live changed source metric from embedded `blame.timestamp`.
- `A-08` proves Git-origin and SVN-origin produce the same observable `SUMMARY` contract for the same logical scenario.
- `A-08` also proves the current AlgC slice does not require `git` or `svn` binaries at runtime for these fixtures.
