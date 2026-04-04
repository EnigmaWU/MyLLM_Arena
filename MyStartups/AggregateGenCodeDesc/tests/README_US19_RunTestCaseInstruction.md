# US-19 Run Test Case Instruction

## Story Summary

US-19 proves Algorithm B `period_added_ai_ratio` works for SVN repositories through the offline patch replay path (`--commitDiffSetDir`). Also proves `--repoURL` and `--repoBranch` are optional when `--commitDiffSetDir` is provided.

## Run All US-19 Tests

```bash
python3 -m pytest -q tests/test_us19_period_added_svn_subset_tdd.py -v
```

## Test Files

### test_us19_period_added_svn_subset_tdd.py

```bash
python3 -m pytest -q tests/test_us19_period_added_svn_subset_tdd.py -v
```

| TC | What It Verifies | Expected |
|----|-----------------|----------|
| `test_svn_period_added_via_offline_fixtures` | SVN patches replayed offline produce correct period-added SUMMARY | total=3, full=2, partial=0; vcsType=svn; revisionId="3" |
| `test_svn_period_added_works_without_repoURL_and_repoBranch` | Same result **without** `--repoURL` and `--repoBranch` — `--commitDiffSetDir` is sufficient | total=3, full=2; exit code=0 |

## Scenario Shape

```
Patch 2 (revision 2): creates trunk/src/report.py with 2 lines (1 AI, 1 human)
Patch 3 (revision 3): adds 1 AI line to trunk/src/report.py
query.json: includedRevisionIds=["2","3"], endRevisionId="3"
No real SVN repo needed — pure offline fixture replay
```

## Run Single TC

```bash
python3 -m pytest -q "tests/test_us19_period_added_svn_subset_tdd.py::TestUS19PeriodAddedSvnSubset::test_svn_period_added_via_offline_fixtures" -v
```
