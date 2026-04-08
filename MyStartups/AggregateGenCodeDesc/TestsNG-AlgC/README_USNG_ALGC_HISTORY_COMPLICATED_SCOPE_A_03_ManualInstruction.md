# USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03 Manual Instruction

## Purpose

This document explains the manual verification flow for
`USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-03`.

The story proves that when a later AI revision overwrites a line that was
previously human-authored, the final AlgC result uses the later AI revision as the
surviving line's effective attribution source.

## Fixture Directories

- Git-origin: `TestdataNG-AlgC/history-complicated/scope-a/03/git/default`
- SVN-origin: `TestdataNG-AlgC/history-complicated/scope-a/03/svn/default`

## Scenario Summary

The scenario contains one file with three surviving lines.

- revision 1 adds three fully human-attributed lines inside the requested window
- revision 2 rewrites lines 2 and 3 inside the same requested window
- final line 1 still blames to the earlier human revision
- final line 2 now blames to the later AI revision with `genRatio=100`
- final line 3 now blames to the later AI revision with `genRatio=80`

So the final expected result is:

- `totalCodeLines = 3`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 1`

## Manual Meaning Of The Story

This is the mirror image of `A-02`.

The key manual check is:

1. lines 2 and 3 used to be human in the earlier revision
2. both survive in the final snapshot but now blame to the later AI revision
3. line 2 counts as full AI
4. line 3 counts as partial AI
5. line 1 remains human and still counts only in `totalCodeLines`

## Run The Git-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/algc-us03-demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-complicated/scope-a/03/git/default \
  --outputFile /tmp/algc-a03-git-out.json
```

## Run The SVN-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///example/svn/algc-us03-demo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-complicated/scope-a/03/svn/default \
  --outputFile /tmp/algc-a03-svn-out.json
```

## Expected Result

For both origins, the expected `SUMMARY` is:

```json
{
  "totalCodeLines": 3,
  "fullGeneratedCodeLines": 1,
  "partialGeneratedCodeLines": 1
}
```

## Real Blame Provenance Requirement

As with all AlgC stories, the embedded `blame` fields in these fixture files are only
in contract when they come from real `git blame` or `svn blame` output captured at
write time.

For this story, the final surviving lines 2 and 3 must point to the later AI revision
in the real VCS blame output. If they still point to the earlier human revision, then
this is not a valid `A-03` fixture.
