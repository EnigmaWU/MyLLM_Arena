# USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02 Manual Instruction

## Purpose

This document explains the manual verification flow for
`USNG-ALGC-HISTORY-COMPLICATED-SCOPE-A-02`.

The story proves that when a later human revision overwrites a line that was
previously attributed to AI, the final AlgC result resets that surviving line to
Manual and does not keep stale AI ownership.

## Fixture Directories

- Git-origin: `TestdataNG-AlgC/history-complicated/scope-a/02/git/default`
- SVN-origin: `TestdataNG-AlgC/history-complicated/scope-a/02/svn/default`

## Scenario Summary

The scenario contains one file with three surviving lines.

- revision 1 adds three fully AI-attributed lines inside the requested window
- revision 2 rewrites only line 2 as a human line inside the same requested window
- lines 1 and 3 still blame to the earlier AI revision
- line 2 now blames to the later human revision

So the final expected result is:

- `totalCodeLines = 3`
- `fullGeneratedCodeLines = 2`
- `partialGeneratedCodeLines = 0`

## Manual Meaning Of The Story

This is not a deletion story and not a partial-AI story.
It is a rewrite-ownership story.

The key manual check is:

1. line 2 used to be AI in the earlier revision
2. line 2 survives in the final snapshot but now blames to the later human revision
3. therefore line 2 counts in `totalCodeLines` only
4. only lines 1 and 3 still count as AI-attributed surviving lines

## Run The Git-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/algc-us02-demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-complicated/scope-a/02/git/default \
  --outputFile /tmp/algc-a02-git-out.json
```

## Run The SVN-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///example/svn/algc-us02-demo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-complicated/scope-a/02/svn/default \
  --outputFile /tmp/algc-a02-svn-out.json
```

## Expected Result

For both origins, the expected `SUMMARY` is:

```json
{
  "totalCodeLines": 3,
  "fullGeneratedCodeLines": 2,
  "partialGeneratedCodeLines": 0
}
```

## Real Blame Provenance Requirement

As with all AlgC stories, the embedded `blame` fields in these fixture files are only
in contract when they come from real `git blame` or `svn blame` output captured at
write time.

For this story, that means the final surviving line 2 must point to the later human
revision in the real VCS blame output. If the final blame still points to the earlier
AI revision, then the scenario is not a valid `A-02` fixture.
