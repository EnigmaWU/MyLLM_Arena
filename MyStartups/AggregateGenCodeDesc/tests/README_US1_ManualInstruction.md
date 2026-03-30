# US-1 Manual Instruction

## Purpose

This document describes how to verify `US-1` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository
- discover the final live changed lines inside the requested window
- load revision-level `genCodeDesc` metadata from `--genCodeDescSetDir`
- produce the expected protocol-shaped aggregate output

## Current Scope

This manual flow matches the current implementation boundary:

- Git only
- `Algorithm A` only
- `Scope A` only
- `metadataSource=genCodeDesc` only
- `--genCodeDescSetDir` as the current local metadata adapter

## Files Used As Reference

- `aggregateGenCodeDesc.py`
- `testdata/us1_live_changed_source_ratio/query.json`
- `testdata/us1_live_changed_source_ratio/01_genCodeDesc.json`
- `testdata/us1_live_changed_source_ratio/expected_result.json`

## Step 1: Create A Temporary Working Area

Use any temporary folder. Example:

```bash
mkdir -p /tmp/agg-us1-manual/repo
mkdir -p /tmp/agg-us1-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us1-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The Source File Used By US-1

```bash
mkdir -p src
cat > src/calc.py <<'EOF'
def calc(x):
    value = x + 1
    boosted = value * 2
    return boosted
EOF
```

## Step 4: Commit The File Inside The Requested Time Window

The current `US-1` fixture window is `2026-03-01` to `2026-03-31`.

```bash
GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git commit -m "us1-r1"
```

## Step 5: Get The Real Revision ID

```bash
cd /tmp/agg-us1-manual/repo
REVISION_ID="$(git rev-parse HEAD)"
echo "$REVISION_ID"
```

You will use this revision id in the metadata filename and inside the metadata `REPOSITORY` block.

## Step 6: Create The Revision-Level genCodeDesc Record

Create one file under `--genCodeDescSetDir` using the naming rule:

```text
<genCodeDescSetDir>/<revisionId>_genCodeDesc.json
```

Example:

```bash
cat > "/tmp/agg-us1-manual/genCodeDescSet/${REVISION_ID}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 1
  },
  "DETAIL": [
    {
      "fileName": "src/calc.py",
      "codeLines": [
        {"lineLocation": 1, "genRatio": 100, "genMethod": "codeCompletion"},
        {"lineLocation": 2, "genRatio": 50, "genMethod": "codeCompletion"},
        {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us1-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID}"
  }
}
EOF
```

## Step 7: Run The CLI

From the project root:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --repoURL /tmp/agg-us1-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-us1-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us1-manual/genCodeDescSet
```

## Step 8: Inspect The Output

```bash
cat /tmp/agg-us1-manual/out.json
```

Expected shape:

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
    "repoURL": "/tmp/agg-us1-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id>"
  }
}
```

## Step 9: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 4`
2. `SUMMARY.fullGeneratedCodeLines == 2`
3. `SUMMARY.partialGeneratedCodeLines == 1`
4. `REPOSITORY.revisionId == git rev-parse HEAD`

## Why The Expected Result Is 4 / 2 / 1

The file has 4 live source-code lines in the time window:

1. `def calc(x):` -> `genRatio = 100`
2. `value = x + 1` -> `genRatio = 50`
3. `boosted = value * 2` -> `genRatio = 100`
4. `return boosted` -> no matching metadata, treated as `0`

So the final summary is:

- total live changed lines = `4`
- full AI-generated lines = `2`
- partial AI-generated lines = `1`

## Important Consistency Rule

The current implementation validates metadata identity.

So the `REPOSITORY` block inside the `genCodeDesc` record must match the CLI query target for:

- `vcsType`
- `repoURL`
- `repoBranch`
- `revisionId`

If any of those values differ, the current CLI should fail instead of silently using mismatched metadata.

## macOS Note

Use the exact same repository path string consistently.

Do not mix different path spellings for the same directory such as:

- `/var/...`
- `/private/var/...`

If the metadata file stores one form and the CLI query uses the other, the current identity validation will treat that as a mismatch.
