# USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08 Manual Instruction

## Purpose

This document explains the manual verification flow for the cross-VCS contract story
`USNG-ALGC-HISTORY-SIMPLE-SCOPE-A-08`.

The goal of this story is narrower than `A-01`:

- prove Git-origin and SVN-origin inputs produce the same observable `SUMMARY`
- prove Algorithm C consumes only embedded blame data at runtime

## Fixture Directories

- Git-origin: `TestdataNG-AlgC/history-simple/scope-a/08/git/default`
- SVN-origin: `TestdataNG-AlgC/history-simple/scope-a/08/svn/default`

## Scenario Summary

`A-08` intentionally reuses the same logical line-attribution scenario as `A-01`.
The difference is story ownership, not different metric math.

For both the Git-origin and SVN-origin fixture sets:

- one older revision is outside the requested window
- one later revision is inside the requested window
- the final surviving in-window set contains:
  - one full AI line
  - one partial AI line
  - one manual line

So both origins must produce the same final result:

- `totalCodeLines = 3`
- `fullGeneratedCodeLines = 1`
- `partialGeneratedCodeLines = 1`

## What Makes `A-08` Different From `A-01`

`A-01` proves core metric calculation.
`A-08` proves the result contract is invariant across VCS origins.

That means the manual check here is:

1. run Algorithm C against the Git-origin fixture set
2. run Algorithm C against the SVN-origin fixture set
3. confirm the two outputs have the same observable contract
4. optionally run with `PATH` stripped so no `git` or `svn` binary can be used

## Run The Git-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/algc-demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-simple/scope-a/08/git/default \
  --outputFile /tmp/algc-a08-git-out.json
```

## Run The SVN-Origin Fixture

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///example/svn/algc-demo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-simple/scope-a/08/svn/default \
  --outputFile /tmp/algc-a08-svn-out.json
```

## Compare The Observable Contract

For this story, compare only the observable contract fields:

- `protocolName`
- `protocolVersion`
- `SUMMARY`

Expected observable contract for both outputs:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.04",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  }
}
```

The `REPOSITORY` block is allowed to differ because it records origin metadata.
That difference is the point of the story: origin metadata may differ while result semantics stay identical.

## Optional Hermetic Runtime Check

This story also expects that AlgC does not need `git` or `svn` binaries at runtime.
You can check that manually by stripping `PATH`:

```bash
env PATH=/nonexistent python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/algc-demo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-simple/scope-a/08/git/default \
  --outputFile /tmp/algc-a08-git-hermetic-out.json
```

```bash
env PATH=/nonexistent python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///example/svn/algc-demo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm C \
  --scope A \
  --genCodeDescSetDir TestdataNG-AlgC/history-simple/scope-a/08/svn/default \
  --outputFile /tmp/algc-a08-svn-hermetic-out.json
```

If both commands still succeed and produce the same expected `SUMMARY`, the `A-08`
no-VCS-runtime boundary is satisfied.

## Fixture Provenance

The `A-08` fixture content intentionally mirrors the same logical scenario used by `A-01`.
That is acceptable because `A-08` is not introducing a new history shape; it is isolating
and proving the VCS-origin invariance contract as its own user story.
