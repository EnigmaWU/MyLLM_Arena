# US-5 Manual Instruction

## Purpose

This document describes how to verify `US-5` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository
- keep line attribution stable across a pure file rename
- join surviving lines back to the historical path recorded in revision metadata
- produce the expected protocol-shaped aggregate output

## Current Scope

This manual flow matches the current implementation boundary:

- Git only
- `Model A` only
- `Scope A` only
- `metadataSource=genCodeDesc` only
- `--genCodeDescSetDir` as the current local metadata adapter

## Files Used As Reference

- `aggregateGenCodeDesc.py`
- `testdata/us5_rename_preserves_lineage/query.json`
- `testdata/us5_rename_preserves_lineage/01_genCodeDesc.json`
- `testdata/us5_rename_preserves_lineage/02_genCodeDesc.json`
- `testdata/us5_rename_preserves_lineage/expected_result.json`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us5-manual/repo
mkdir -p /tmp/agg-us5-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us5-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The First Revision Under The Old Path

```bash
mkdir -p src
cat > src/legacy_name.py <<'EOF'
def calc(x):
    value = x * 2
    return value
EOF

GIT_AUTHOR_DATE="2026-03-08T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-08T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-08T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-08T09:00:00Z" \
git commit -m "us5-r1"
```

## Step 4: Rename The File Without Changing Its Content

```bash
git mv src/legacy_name.py src/current_name.py

GIT_AUTHOR_DATE="2026-03-12T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-12T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-12T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-12T09:00:00Z" \
git commit -m "us5-r2"
```

## Step 5: Get The Real Revision IDs

```bash
cd /tmp/agg-us5-manual/repo
REVISION_ID_R2="$(git rev-parse HEAD)"
REVISION_ID_R1="$(git rev-parse HEAD~1)"
echo "$REVISION_ID_R1"
echo "$REVISION_ID_R2"
```

## Step 6: Create The Revision-Level genCodeDesc Records

```bash
cat > "/tmp/agg-us5-manual/genCodeDescSet/${REVISION_ID_R1}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/legacy_name.py",
      "codeLines": [
        {"lineLocation": 1, "genRatio": 100, "genMethod": "codeCompletion"},
        {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us5-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R1}"
  }
}
EOF

cat > "/tmp/agg-us5-manual/genCodeDescSet/${REVISION_ID_R2}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "HumanOnlyRevision",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 0,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/current_name.py",
      "codeLines": []
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us5-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R2}"
  }
}
EOF
```

## Step 7: Run The CLI

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --repoURL /tmp/agg-us5-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-us5-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us5-manual/genCodeDescSet \
  --logLevel debug
```

## Step 8: Inspect The Output

```bash
cat /tmp/agg-us5-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us5-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for us5-r2>"
  }
}
```

## Step 9: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 3`
2. `SUMMARY.fullGeneratedCodeLines == 2`
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD`

With `--logLevel debug`, also verify that the live lines are logged under `src/current_name.py` while the two AI lines still show `origin=src/legacy_name.py:...`.

## Why The Expected Result Is 3 / 2 / 0

The file path changed in the second revision, but the file content did not.

So the surviving lines still originate from the first revision for blame purposes.
That means the two AI-attributed lines from `src/legacy_name.py` must still count after the rename, even though the final snapshot file is `src/current_name.py`.
