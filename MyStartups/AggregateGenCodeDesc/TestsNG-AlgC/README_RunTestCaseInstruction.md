# AggregateGenCodeDesc — Algorithm C Run Test Case Instruction

## Purpose

This document is the TDD entry point for Algorithm C executable tests.

Current scope in this folder:

- `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-06`
- `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01`
- `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08`
- `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02`
- `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03`
- `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04`
- `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-05`
- `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-07`
- `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09`
- `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10`
- `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11`
- `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-12`
- `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-13`
- Git-origin fixtures
- SVN-origin fixtures

The tests in `TestsNG-AlgC` are written before runtime implementation is complete.
During the initial TDD phase, red results are expected until the corresponding AlgC slice is implemented.

## Run The Covered AlgC TDD Files

```bash
python3 -m pytest -q TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_06_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_08_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_02_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_03_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_04_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_05_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_07_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_09_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_10_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_11_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_12_git_tdd.py -v
python3 -m pytest -q TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_13_svn_tdd.py -v
```

## Run One TC Only

```bash
python3 -m pytest -q "TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_06_tdd.py::TestUsngAlgcHistorySimpleScopeA06Tdd::test_algorithm_c_summary_matches_story_golden_summary_for_all_covered_fast_scenarios" -v
python3 -m pytest -q "TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_01_tdd.py::TestUsngAlgcHistorySimpleScopeA01Tdd::test_cli_matches_git_expected_result" -v
python3 -m pytest -q "TestsNG-AlgC/history-simple/scope-a/test_usng_algc_history_simple_scope_a_08_tdd.py::TestUsngAlgcHistorySimpleScopeA08Tdd::test_git_and_svn_share_same_observable_summary_contract" -v
python3 -m pytest -q "TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_02_tdd.py::TestUsngAlgcHistoryComplicatedScopeA02Tdd::test_cli_matches_git_expected_result_when_human_rewrite_resets_ai_attribution" -v
python3 -m pytest -q "TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_03_tdd.py::TestUsngAlgcHistoryComplicatedScopeA03Tdd::test_cli_matches_git_expected_result_when_ai_rewrite_replaces_human_ownership" -v
python3 -m pytest -q "TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_04_tdd.py::TestUsngAlgcHistoryComplicatedScopeA04Tdd::test_cli_matches_git_expected_result_when_deleted_ai_lines_are_excluded" -v
python3 -m pytest -q "TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_05_tdd.py::TestUsngAlgcHistoryComplicatedScopeA05Tdd::test_cli_matches_git_expected_result_when_rename_preserves_lineage" -v
python3 -m pytest -q "TestsNG-AlgC/history-complicated/scope-a/test_usng_algc_history_complicated_scope_a_07_tdd.py::TestUsngAlgcHistoryComplicatedScopeA07Tdd::test_cli_matches_git_expected_result_when_merge_preserves_effective_attribution" -v
python3 -m pytest -q "TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_09_tdd.py::TestUsngAlgcHistoryComplexScopeA09Tdd::test_cli_matches_git_expected_result_for_large_file_set" -v
python3 -m pytest -q "TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_10_tdd.py::TestUsngAlgcHistoryComplexScopeA10Tdd::test_cli_matches_git_expected_result_for_deep_history" -v
python3 -m pytest -q "TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_11_tdd.py::TestUsngAlgcHistoryComplexScopeA11Tdd::test_cli_matches_git_expected_result_for_many_merged_branches" -v
python3 -m pytest -q "TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_12_git_tdd.py::TestUsngAlgcHistoryComplexScopeA12GitTdd::test_cli_matches_expected_result_for_git_production_scale_fixture" -v
python3 -m pytest -q "TestsNG-AlgC/history-complex/scope-a/test_usng_algc_history_complex_scope_a_13_svn_tdd.py::TestUsngAlgcHistoryComplexScopeA13SvnTdd::test_cli_matches_expected_result_for_svn_production_scale_fixture" -v
```

## Expected TDD Lifecycle

1. First run: fail because `--algorithm C` is not implemented yet.
2. After `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-01` lands: Git fixture should pass.
3. Then the SVN fixture should pass.
4. After `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08` lands: the cross-VCS contract and no-VCS-runtime checks should pass.
5. After `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02` lands: human-overwrite fixtures should show that one surviving line resets from AI ownership to Manual.
6. After `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03` lands: AI-rewrite fixtures should show that later AI ownership replaces earlier human ownership on the surviving lines.
7. After `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04` lands: deleted AI lines should disappear from both numerator and denominator because they are absent from the final surviving set.
8. After `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-05` lands: rename or move fixtures should preserve original line lineage even though the final file path changed.
9. After `USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-07` lands: merge fixtures should preserve per-line origin attribution rather than collapsing to merge revision identity.
10. After `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-09` lands: large exhaustive end snapshots should preserve the same per-line attribution semantics at larger file counts.
11. After `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-10` lands: deep-history origin timestamps should still control in-window filtering and attribution.
12. After `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-11` lands: many merged branches should still preserve independent per-line attribution.
13. After `USNG-ALGC-HISTORY-COMPLEX-SCOPE-A-12` and `A-13` land: the synthetic production-scale Git and SVN gates should preserve correctness at branch-heavy scale.
14. After `USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-06` lands: the suite-level parity gate should confirm all covered fast scenarios stay aligned at the repository `SUMMARY` level and reject wrong protocol versions.

## Fixture Location

- `A-01` Git fixture: `TestdataNG-AlgC/history-simple/scope-a/01/git/default`
- `A-01` SVN fixture: `TestdataNG-AlgC/history-simple/scope-a/01/svn/default`
- `A-08` Git fixture: `TestdataNG-AlgC/history-simple/scope-a/08/git/default`
- `A-08` SVN fixture: `TestdataNG-AlgC/history-simple/scope-a/08/svn/default`
- `A-02` Git fixture: `TestdataNG-AlgC/history-complicated/scope-a/02/git/default`
- `A-02` SVN fixture: `TestdataNG-AlgC/history-complicated/scope-a/02/svn/default`
- `A-03` Git fixture: `TestdataNG-AlgC/history-complicated/scope-a/03/git/default`
- `A-03` SVN fixture: `TestdataNG-AlgC/history-complicated/scope-a/03/svn/default`
- `A-04` Git fixture: `TestdataNG-AlgC/history-complicated/scope-a/04/git/default`
- `A-04` SVN fixture: `TestdataNG-AlgC/history-complicated/scope-a/04/svn/default`
- `A-05` Git fixture: `TestdataNG-AlgC/history-complicated/scope-a/05/git/default`
- `A-05` SVN fixture: `TestdataNG-AlgC/history-complicated/scope-a/05/svn/default`
- `A-07` Git fixture: `TestdataNG-AlgC/history-complicated/scope-a/07/git/default`
- `A-07` SVN fixture: `TestdataNG-AlgC/history-complicated/scope-a/07/svn/default`
- `A-09` Git fixture: `TestdataNG-AlgC/history-complex/scope-a/09/git/default`
- `A-09` SVN fixture: `TestdataNG-AlgC/history-complex/scope-a/09/svn/default`
- `A-10` Git fixture: `TestdataNG-AlgC/history-complex/scope-a/10/git/default`
- `A-10` SVN fixture: `TestdataNG-AlgC/history-complex/scope-a/10/svn/default`
- `A-11` Git fixture: `TestdataNG-AlgC/history-complex/scope-a/11/git/default`
- `A-11` SVN fixture: `TestdataNG-AlgC/history-complex/scope-a/11/svn/default`
- `A-12` Git fixture: `TestdataNG-AlgC/history-complex/scope-a/12/git/default`
- `A-13` SVN fixture: `TestdataNG-AlgC/history-complex/scope-a/13/svn/default`

## What The Covered TDD Files Prove

- `A-06` proves the suite-level parity gate keeps the covered fast scenarios aligned at the repository `SUMMARY` level and rejects non-`26.04` protocol input.
- `A-01` proves Algorithm C can consume only `genCodeDescProtoV26.04` files, accumulate add/delete history, and compute the live changed source metric from embedded `blame.timestamp`.
- `A-08` proves Git-origin and SVN-origin produce the same observable `SUMMARY` contract for the same logical scenario.
- `A-08` also proves the current AlgC slice does not require `git` or `svn` binaries at runtime for these fixtures.
- `A-02` proves a later human rewrite removes prior AI attribution from the surviving line while preserving earlier AI ownership on the unchanged surviving lines.
- `A-03` proves a later AI rewrite replaces earlier human ownership on the surviving lines while unchanged surviving lines keep their earlier human attribution.
- `A-04` proves deleted AI lines do not appear in the final aggregate because Algorithm C counts only the surviving live snapshot.
- `A-05` proves a rename or move does not reset line ownership because Algorithm C keys surviving lines by embedded blame origin rather than final file path alone.
- `A-07` proves a merge commit does not flatten attribution to the merge revision because Algorithm C respects each surviving line's embedded blame origin.
- `A-09` proves larger end snapshots preserve the same per-line attribution semantics across many files.
- `A-10` proves deep history reduces to the same time-window filtering on `blame.timestamp`, regardless of origin depth.
- `A-11` proves many merged branches still preserve independent per-line attribution.
- `A-12` proves a branch-heavy Git-origin production-scale end snapshot still aggregates correctly.
- `A-13` proves a branch-heavy SVN-origin production-scale end snapshot still aggregates correctly.
