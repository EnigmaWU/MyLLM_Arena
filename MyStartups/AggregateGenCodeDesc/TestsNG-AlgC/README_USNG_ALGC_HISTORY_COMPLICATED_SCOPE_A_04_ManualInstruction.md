# USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04 Manual Instruction

## Purpose

This document explains the manual verification flow for
`USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-04`.

The story proves that AI-attributed lines which existed earlier in the window but are
no longer present in the live snapshot at `endTime` must not count in the final AlgC result.

## Fixture Directories

- Git-origin: `TestdataNG-AlgC/history-complicated/scope-a/04/git/default`
- SVN-origin: `TestdataNG-AlgC/history-complicated/scope-a/04/svn/default`

## Scenario Summary

The scenario contains one file.

- revision 1 has four fully AI-attributed lines
- revision 2 deletes lines 3 and 4 before `endTime`
- only lines 1 and 2 survive in the final snapshot

So the final expected result is:

- `totalCodeLines = 2`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 0`

## Manual Meaning Of The Story

This is a live-snapshot exclusion story.

The key manual check is:

1. lines 3 and 4 existed earlier and were AI-attributed
2. they do not survive to the final snapshot
3. therefore they must not appear in the final aggregate at all
4. only surviving lines 1 and 2 are counted

## Run The Git-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/algc-us04-demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-complicated/scope-a/04/git/default \
  --outputFile /tmp/algc-a04-git-out.json
```

## Run The SVN-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///example/svn/algc-us04-demo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-complicated/scope-a/04/svn/default \
  --outputFile /tmp/algc-a04-svn-out.json
```

## Expected Result

For both origins, the expected `SUMMARY` is:

```json
{
  "totalCodeLines": 2,
  "fullGeneratedCodeLines": 2,
  "partialGeneratedCodeLines": 0
}
```

## Real Blame Provenance Requirement

As with all AlgC stories, the embedded `blame` fields in these fixture files are only
in contract when they come from real `git blame` or `svn blame` output captured at
write time.

For this story, the deleted lines still need stable origin identities so the deletion
entries can remove the correct previously-surviving lines from the accumulated state.
