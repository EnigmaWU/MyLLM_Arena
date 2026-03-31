# Real Repository Tests

These tests are intended to validate real VCS behavior behind Algorithm A.

## Purpose

- `test_real_git_model_a_scenarios.py` uses temporary real Git repositories and actual `git blame`
- `test_real_svn_contract_parity.py` uses a temporary local SVN repository and runs only when `svn` and `svnadmin` are installed

## Scope

These are integration-style tests for VCS behavior, even if they are run under `unittest`.
They complement the scenario fixtures under `testdata/`, which are logic-level design fixtures.

For the current project direction, real repository tests are the preferred verification path for `Algorithm A` behavior.

## Real Repo Fixture Contract

For real repository tests, the required inputs are:

- real repository history created by actual Git or SVN commands inside the test
- one revision-level `genCodeDesc.json` artifact for each revision that participates in the attribution result
- one `query.json` artifact describing the requested input contract when end-to-end utility tests are added
- one `expected_result.json` artifact describing the golden protocol-shaped output when end-to-end utility tests are added

For this test layer, `*.diff` files are not required.
The real repository itself is the authoritative source of history, file evolution, and blame behavior.

## Relationship To `testdata/`

- `testdata/` remains useful for design discussion, fixture-level reasoning, and logic-oriented scenario examples
- `tests/` is the preferred place for validating real `Algorithm A` behavior against actual Git or SVN commands
- new real repository tests should not require `*.diff` files unless a diff is intentionally added as an explanatory artifact

## Manual Verification

For end-to-end `US-*` test cases, keep a matching manual verification guide so the same scenario can be checked by hand outside the automated test harness.

Current example:

- `US-1` automated test: `test_us1_live_changed_source_ratio_tdd.py`
- `US-1` manual guide: `README_US1_ManualInstruction.md`

Recommended convention for future cases:

- one `test_usX_*.py` file for the automated contract
- one `README_USX_ManualInstruction.md` file for hand verification steps

Current extended examples:

- `US-10` Git manual guide: `README_US10_ManualInstruction.md`
- `US-10` SVN manual guide: `README_US10_SVN_ManualInstruction.md`
- `US-11` Git manual guide: `README_US11_ManualInstruction.md`
- `US-11` SVN manual guide: `README_US11_SVN_ManualInstruction.md`
- `US-12` Git manual guide: `README_US12_ManualInstruction.md`
- `US-12` SVN manual guide: `README_US12_SVN_ManualInstruction.md`
- `US-13` Git manual guide: `README_US13_ManualInstruction.md`
- `US-14` SVN manual guide: `README_US14_SVN_ManualInstruction.md`
- `SVN lineage experiments`: `README_SVN_Lineage_Experiments.md`

## Current SVN Notes

- SVN US-10 and US-11 are close parity-style ports of the Git scenarios.
- SVN US-12 is intentionally branch-heavy but multi-file, because real `svn blame -g` does not preserve a literal same-file Git-style repeated-merge topology cleanly enough for a trustworthy parity claim.
- `test_real_svn_same_file_merge_limitation.py` captures that limitation directly against a real local SVN repository.

## Current Scalability Coverage

- `test_us10_large_snapshot_scalability_tdd.py` covers broad Git protocol-index reuse.
- `test_us11_deep_history_scalability_tdd.py` covers deep-history Git commit-time lookup reuse.
- `test_us12_svn_merged_branch_scalability_tdd.py` covers SVN reuse behavior for shared branch-origin revisions across merged-branch scenarios.

## Production-Readiness Target

- Production readiness for the current implementation means `Algorithm A + Scope A` must hold for both Git and SVN.
- Real local repositories are the preferred acceptance vehicle for production-like validation, because they exercise the same history, blame, rename, copy, and merge semantics as remote repositories without adding network variability.
- The target topology includes large branch counts, deep revision history, and hybrid merge fan-in toward a release branch or release path.
- Production-scale tests should verify both final-result correctness and at least one explicit scalability or reuse property so the suite guards against correctness-only regressions that hide pathological command growth.

## Production Gate

- The repository now has an explicit long-running production gate script at `run_production_gate.sh`.
- The production-scale acceptance tier is also selectable through pytest markers: `production_scale` and `long_running`.
- Current production-gate members are `test_us13_git_production_scale_local_repo_tdd.py` and `test_us14_svn_production_scale_local_repo_tdd.py`.

Recommended commands:

```bash
bash run_production_gate.sh
```

```bash
python3 -m pytest -q -m "production_scale" tests/test_us13_git_production_scale_local_repo_tdd.py tests/test_us14_svn_production_scale_local_repo_tdd.py
```

## Current Gap

- The repository now includes explicit US-13 and US-14 production-scale contracts and real-repository tests, but the broader full-suite runtime budget and release-gate expectations for those cases still need to be established explicitly.
- SVN production-scale validation is currently defined around stable trunk reintegration revisions, which is the strongest large-scale contract the current SVN blame semantics support without overclaiming same-file merge lineage.

## SVN Experimental Track

- Exploratory SVN lineage work now lives in `test_real_svn_lineage_experiments.py` and is marked with `experimental_svn`.
- That track is intentionally separate from the production gate so experimental same-file merge findings do not silently change the accepted US-14 contract.

## Run

```bash
python3 -m unittest discover tests
```
