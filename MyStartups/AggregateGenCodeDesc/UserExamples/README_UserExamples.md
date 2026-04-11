# AggregateGenCodeDesc User Examples

## Purpose

Replayable user examples for running `aggregateGenCodeDesc.py`.

Each example in this document is intended to be real rather than illustrative:

- it uses concrete example data shipped under `UserExamples/`
- it gives an exact command to run
- it gives the expected result
- it gives a diagnosis or check step so the user can verify the result exactly

Use `README_UserGuide.md` for the full argument contract and support matrix.

## How To Use This Document

Run all commands from the project root:

```bash
cd /PATH/2/AggregateGenCodeDesc
```

All examples write output under `/tmp/` so you can replay them without changing repository files.
All example input data lives under `UserExamples/` so the examples do not depend on `testdata/` or the test harness.

## Example Index

1. Generic example: Git + Algorithm A (production)
2. Generic example: Git + Algorithm A with logical URL
3. Generic example: SVN + Algorithm A (production)
4. Generic example: Algorithm B + local Git replay
5. Generic example: Algorithm C + embedded blame offline analysis
6. Real example: Algorithm B + Git commit diff set replay with shipped user example data
7. Real example: Algorithm B + SVN commit diff set replay with shipped user example data
8. Real example: Algorithm B + SVN period-added subset replay with shipped user example data

## Generic Operator Examples

These examples show the standard command shapes operators use in production or production-like runs.
They are intentionally generic patterns, while the later sections are replayable examples with shipped data.

## 1. Generic Example: Git + Algorithm A (Production)

The most common case: analyze a local Git repository.

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

To count documentation lines instead of code lines, change `--scope A` to `--scope C`.
To count everything (source + docs), use `--scope D`.

## 2. Generic Example: Git + Algorithm A With Logical URL

When metadata uses a logical URL but Git commands run against a local checkout:

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/repo/demo.git \
  --workingDir /path/to/local/git/checkout \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

## 3. Generic Example: SVN + Algorithm A (Production)

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL file:///path/to/local/svn/repo \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

You can also use an SVN server URL such as `svn://host/repo` instead of `file:///`.

## 4. Generic Example: Algorithm B + Local Git Replay

Replay commit diffs from a live Git checkout.

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL /path/to/local/git/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-b-out.json \
  --genCodeDescSetDir /path/to/genCodeDescSet
```

Scopes B, C, and D are also supported. Change only `--scope`.

## 5. Generic Example: Algorithm C + Embedded Blame Offline Analysis

Run with only a v26.04 protocol set. In the current slice, Scope A is the supported path.

```bash
python3 aggregateGenCodeDesc.py \
  --algorithm C \
  --startTime 2026-03-10 \
  --endTime 2026-03-31 \
  --scope A \
  --outputFile /tmp/agg-c-out.json \
  --genCodeDescSetDir /path/to/algc-v26.04-set
```

If `/path/to/algc-v26.04-set/queryArgs.json` is present, or `--queryArgsFile` is passed, Algorithm C can derive `endRevisionId`, `repoURL`, `repoBranch`, and `vcsType` from that file plus the selected end protocol.

## Replayable Real Examples

Every replayable Algorithm B example below uses at least 5 serialized commits, so the replay chain is non-trivial and closer to real operator use.

## 6. Real Example: Algorithm B + Git Commit Diff Set Replay

### Example 1 Data

This example uses shipped user example data. The replay chain includes a multi-line add, a mixed delete-plus-add change, a multi-line code-range add, and a code-range delete before the final result.

- `UserExamples/example01-algb-git-commitdiffset/genCodeDescSet/ux1-r1_genCodeDesc.json` through `ux1-r5_genCodeDesc.json`
- `UserExamples/example01-algb-git-commitdiffset/commitDiffSet/0001_ux1-r1_commitDiff.patch` through `0005_ux1-r5_commitDiff.patch`
- `UserExamples/example01-algb-git-commitdiffset/expected_result.json`

### Example 1 Command

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType git \
  --repoURL https://example.local/userexamples/git-basic \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-1-out.json \
  --genCodeDescSetDir UserExamples/example01-algb-git-commitdiffset/genCodeDescSet \
  --commitDiffSetDir UserExamples/example01-algb-git-commitdiffset/commitDiffSet
```

### Example 1 Expected Output

Expected file: `UserExamples/example01-algb-git-commitdiffset/expected_result.json`

Expected JSON:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "https://example.local/userexamples/git-basic",
    "repoBranch": "main",
    "revisionId": "ux1-r5"
  }
}
```

### Example 1 Diagnosis And Check

Inspect output:

```bash
cat /tmp/agg-userexample-1-out.json
```

Exact comparison against the expected result:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-1-out.json').read_text())
expected = json.loads(Path('UserExamples/example01-algb-git-commitdiffset/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('Example 1 mismatch')

print('Example 1 OK: actual output exactly matches expected_result.json')
PY
```

What to check if it fails:

- confirm the command was run from the project root
- confirm `UserExamples/example01-algb-git-commitdiffset/commitDiffSet` exists
- confirm the directory contains 5 `NN_..._commitDiff.patch` files
- confirm the output file path is `/tmp/agg-userexample-1-out.json`

## 7. Real Example: Algorithm B + SVN Commit Diff Set Replay

### Example 2 Data

This example uses shipped user example data. The replay chain includes a multi-line add, a mixed delete-plus-add change, a multi-line code-range add, and a code-range delete before the final result.

- `UserExamples/example02-algb-svn-commitdiffset/genCodeDescSet/17_genCodeDesc.json` through `21_genCodeDesc.json`
- `UserExamples/example02-algb-svn-commitdiffset/commitDiffSet/0001_17_commitDiff.patch` through `0005_21_commitDiff.patch`
- `UserExamples/example02-algb-svn-commitdiffset/expected_result.json`

### Example 2 Command

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --repoURL https://example.local/userexamples/svn-basic \
  --repoBranch trunk \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --scope A \
  --outputFile /tmp/agg-userexample-2-out.json \
  --genCodeDescSetDir UserExamples/example02-algb-svn-commitdiffset/genCodeDescSet \
  --commitDiffSetDir UserExamples/example02-algb-svn-commitdiffset/commitDiffSet
```

### Example 2 Expected Output

Expected file: `UserExamples/example02-algb-svn-commitdiffset/expected_result.json`

Expected JSON:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "svn",
    "repoURL": "https://example.local/userexamples/svn-basic",
    "repoBranch": "trunk",
    "revisionId": "21"
  }
}
```

### Example 2 Diagnosis And Check

Inspect output:

```bash
cat /tmp/agg-userexample-2-out.json
```

Exact comparison against the expected result:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-2-out.json').read_text())
expected = json.loads(Path('UserExamples/example02-algb-svn-commitdiffset/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('Example 2 mismatch')

print('Example 2 OK: actual output exactly matches expected_result.json')
PY
```

What to check if it fails:

- confirm `--vcsType svn` was used
- confirm the SVN example directory is `UserExamples/example02-algb-svn-commitdiffset`
- confirm the directory contains 5 `NN_..._commitDiff.patch` files
- confirm the output file path is `/tmp/agg-userexample-2-out.json`

## 8. Real Example: Algorithm B + SVN Period-Added Subset Replay

This example uses shipped user example data, replays 5 revisions, demonstrates the special use of `includedRevisionIds` through `queryArgs.json`, and includes multi-line adds plus both single-line and range deletions.

### Example 3 Data

- `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/2_genCodeDesc.json`
- `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/3_genCodeDesc.json`
- `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/4_genCodeDesc.json`
- `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/5_genCodeDesc.json`
- `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/6_genCodeDesc.json`
- `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/queryArgs.json`
- `UserExamples/example03-algb-svn-period-added-subset/commitDiffSet/0001_2_commitDiff.patch`
- `UserExamples/example03-algb-svn-period-added-subset/commitDiffSet/0002_3_commitDiff.patch`
- `UserExamples/example03-algb-svn-period-added-subset/commitDiffSet/0003_4_commitDiff.patch`
- `UserExamples/example03-algb-svn-period-added-subset/commitDiffSet/0004_5_commitDiff.patch`
- `UserExamples/example03-algb-svn-period-added-subset/commitDiffSet/0005_6_commitDiff.patch`
- `UserExamples/example03-algb-svn-period-added-subset/expected_result.json`

### Example 3 Command

```bash
python3 aggregateGenCodeDesc.py \
  --vcsType svn \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --scope A \
  --outputFile /tmp/agg-userexample-3-out.json \
  --genCodeDescSetDir UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet \
  --commitDiffSetDir UserExamples/example03-algb-svn-period-added-subset/commitDiffSet
```

### Example 3 Expected Output

Expected file: `UserExamples/example03-algb-svn-period-added-subset/expected_result.json`

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 6,
    "fullGeneratedCodeLines": 3,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "svn",
    "repoURL": "",
    "repoBranch": "",
    "revisionId": "6"
  }
}
```

### Example 3 Diagnosis And Check

Inspect output:

```bash
cat /tmp/agg-userexample-3-out.json
```

Exact check:

```bash
python3 - <<'PY'
import json
from pathlib import Path

actual = json.loads(Path('/tmp/agg-userexample-3-out.json').read_text())
expected = json.loads(Path('UserExamples/example03-algb-svn-period-added-subset/expected_result.json').read_text())

if actual != expected:
    raise SystemExit('Example 3 mismatch')

print('Example 3 OK: actual output exactly matches the expected JSON')
PY
```

What to check if it fails:

- confirm both patch files were created
- confirm the directory contains 5 `NN_..._commitDiff.patch` files
- confirm `UserExamples/example03-algb-svn-period-added-subset/genCodeDescSet/queryArgs.json` contains `includedRevisionIds` `["2", "3", "4", "5", "6"]`
- confirm `--metric period_added_ai_ratio` was included
- confirm the output file path is `/tmp/agg-userexample-3-out.json`

## Data Layout

The shipped user example data lives here:

- `UserExamples/example01-algb-git-commitdiffset`
- `UserExamples/example02-algb-svn-commitdiffset`
- `UserExamples/example03-algb-svn-period-added-subset`

## Related Docs

- `README_UserGuide.md`: operator contract, argument meanings, and support matrix
- `README_RunTestCase.md`: test commands
- `README.md`: product scope and measurement definitions
