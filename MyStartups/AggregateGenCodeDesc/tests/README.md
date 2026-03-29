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

## Run

```bash
python3 -m unittest discover tests
```
