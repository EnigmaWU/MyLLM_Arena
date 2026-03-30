# Real Repository Tests

These tests are intended to validate real VCS behavior behind Model A.

## Purpose

- `test_real_git_model_a_scenarios.py` uses temporary real Git repositories and actual `git blame`
- `test_real_svn_contract_parity.py` uses a temporary local SVN repository and runs only when `svn` and `svnadmin` are installed

## Scope

These are integration-style tests for VCS behavior, even if they are run under `unittest`.
They complement the scenario fixtures under `testdata/`, which are logic-level design fixtures.

For the current project direction, real repository tests are the preferred verification path for `Model A` behavior.

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
- `tests/` is the preferred place for validating real `Model A` behavior against actual Git or SVN commands
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

## Current SVN Notes

- SVN US-10 and US-11 are close parity-style ports of the Git scenarios.
- SVN US-12 is intentionally branch-heavy but multi-file, because real `svn blame -g` does not preserve a literal same-file Git-style repeated-merge topology cleanly enough for a trustworthy parity claim.
- `test_real_svn_same_file_merge_limitation.py` captures that limitation directly against a real local SVN repository.

## Current Scalability Coverage

- `test_us10_large_snapshot_scalability_tdd.py` covers broad Git protocol-index reuse.
- `test_us11_deep_history_scalability_tdd.py` covers deep-history Git commit-time lookup reuse.
- `test_us12_svn_merged_branch_scalability_tdd.py` covers SVN reuse behavior for shared branch-origin revisions across merged-branch scenarios.

## Run

```bash
python3 -m unittest discover tests
```
