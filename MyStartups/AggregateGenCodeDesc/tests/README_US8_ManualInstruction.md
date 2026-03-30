# US-8 Manual Instruction

## Purpose

This document describes how to verify `US-8` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository with a non-fast-forward merge
- preserve each surviving line's effective origin after the merge commit
- count only the feature-side AI line as AI in the final aggregate
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
- `testdata/us8_merge_commit_preserves_attribution/query.json`
- `testdata/us8_merge_commit_preserves_attribution/01_genCodeDesc.json`
- `testdata/us8_merge_commit_preserves_attribution/02_genCodeDesc.json`
- `testdata/us8_merge_commit_preserves_attribution/03_genCodeDesc.json`
- `testdata/us8_merge_commit_preserves_attribution/04_genCodeDesc.json`
- `testdata/us8_merge_commit_preserves_attribution/expected_result.json`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us8-manual/repo
mkdir -p /tmp/agg-us8-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us8-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The Base Revision On Main

```bash
mkdir -p src
cat > src/merge_case.py <<'EOF'
base = x
spacer = x
value = x + 1
return base + value + spacer
EOF

GIT_AUTHOR_DATE="2026-03-01T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-01T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-01T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-01T09:00:00Z" \
git commit -m "us8-r1"
```

## Step 4: Create The Feature Branch AI Change

```bash
git checkout -b feature-ai

cat > src/merge_case.py <<'EOF'
base = x
spacer = x
value = x * 2
return base + value + spacer
EOF

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git commit -m "us8-r2"
```

## Step 5: Return To Main And Make The Human Change

```bash
git checkout main

cat > src/merge_case.py <<'EOF'
base = max(x, 0)
spacer = x
value = x + 1
return base + value + spacer
EOF

GIT_AUTHOR_DATE="2026-03-12T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-12T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-12T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-12T09:00:00Z" \
git commit -m "us8-r3"
```

## Step 6: Merge The Feature Branch

```bash
GIT_AUTHOR_DATE="2026-03-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-20T09:00:00Z" \
git merge --no-ff feature-ai -m "us8-r4"
```

## Step 7: Get The Real Revision IDs

```bash
cd /tmp/agg-us8-manual/repo
REVISION_ID_R4="$(git rev-parse HEAD)"
REVISION_ID_R3="$(git rev-parse HEAD~1)"
REVISION_ID_R2="$(git rev-parse feature-ai)"
REVISION_ID_R1="$(git rev-parse main~2)"
echo "$REVISION_ID_R1"
echo "$REVISION_ID_R2"
echo "$REVISION_ID_R3"
echo "$REVISION_ID_R4"
```

## Step 8: Create The Revision-Level genCodeDesc Records

```bash
cat > "/tmp/agg-us8-manual/genCodeDescSet/${REVISION_ID_R1}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "HumanOnlyRevision",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 0,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/merge_case.py",
      "codeLines": []
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us8-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R1}"
  }
}
EOF

cat > "/tmp/agg-us8-manual/genCodeDescSet/${REVISION_ID_R2}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/merge_case.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us8-manual/repo",
    "repoBranch": "feature-ai",
    "revisionId": "${REVISION_ID_R2}"
  }
}
EOF

cat > "/tmp/agg-us8-manual/genCodeDescSet/${REVISION_ID_R3}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "HumanOnlyRevision",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 0,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/merge_case.py",
      "codeLines": []
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us8-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R3}"
  }
}
EOF

cat > "/tmp/agg-us8-manual/genCodeDescSet/${REVISION_ID_R4}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "MergeRevision",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/merge_case.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us8-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R4}"
  }
}
EOF
```

## Step 9: Run The CLI

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --repoURL /tmp/agg-us8-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-us8-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us8-manual/genCodeDescSet \
  --logLevel debug
```

## Step 10: Inspect The Output

```bash
cat /tmp/agg-us8-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us8-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for us8-r4>"
  }
}
```

## Step 11: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 4`
2. `SUMMARY.fullGeneratedCodeLines == 1`
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD`

With `--logLevel debug`, also verify that the merged live lines still point to their effective origin revisions rather than to the merge commit itself.

## Why The Expected Result Is 4 / 1 / 0

The merge commit combines a human mainline edit with an AI feature-branch edit.

In the final snapshot, one surviving line still effectively originates from the AI feature revision, while the other surviving lines blame to human revisions.

So the final aggregate remains:

- total live changed lines = `4`
- full AI-generated lines = `1`
- partial AI-generated lines = `0`
