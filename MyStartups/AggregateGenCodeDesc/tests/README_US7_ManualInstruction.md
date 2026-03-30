# US-7 Manual Instruction

## Purpose

This document describes how to verify `US-7` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository across several commits in one query window
- keep older full-AI ownership when those lines still survive unchanged
- drop AI ownership after later human cleanup
- count a newer partial-AI rewrite independently from older full-AI lines

## Current Scope

This manual flow matches the current implementation boundary:

- Git only
- `Algorithm A` only
- `Scope A` only
- `metadataSource=genCodeDesc` only
- `--genCodeDescSetDir` as the current local metadata adapter

## Files Used As Reference

- `aggregateGenCodeDesc.py`
- `testdata/us7_mixed_multi_commit_window/query.json`
- `testdata/us7_mixed_multi_commit_window/01_genCodeDesc.json`
- `testdata/us7_mixed_multi_commit_window/02_genCodeDesc.json`
- `testdata/us7_mixed_multi_commit_window/03_genCodeDesc.json`
- `testdata/us7_mixed_multi_commit_window/04_genCodeDesc.json`
- `testdata/us7_mixed_multi_commit_window/expected_result.json`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us7-manual/repo
mkdir -p /tmp/agg-us7-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us7-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The Human Baseline Revision

```bash
mkdir -p src
cat > src/mixed.py <<'EOF'
first = seed
second = seed + 1
third = seed + 2
fourth = seed + 3
fifth = seed + 4
EOF

GIT_AUTHOR_DATE="2026-03-03T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-03T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-03T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-03T09:00:00Z" \
git commit -m "us7-r1"
```

## Step 4: Add Several Full-AI Lines

```bash
cat > src/mixed.py <<'EOF'
first = seed
second = seed + 1
third = seed * 2
fourth = seed * 3
helper = seed * 4
fifth = seed + 4
EOF

GIT_AUTHOR_DATE="2026-03-08T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-08T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-08T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-08T09:00:00Z" \
git commit -m "us7-r2"
```

## Step 5: Clean Up Part Of The AI Output By Hand

```bash
cat > src/mixed.py <<'EOF'
first = seed
second = seed + 1
third = seed * 2
fourth = normalize(seed)
fifth = seed + 4
EOF

GIT_AUTHOR_DATE="2026-03-15T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-15T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-15T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-15T09:00:00Z" \
git commit -m "us7-r3"
```

## Step 6: Partially Rewrite The Final Line With AI Assistance

```bash
cat > src/mixed.py <<'EOF'
first = seed
second = seed + 1
third = seed * 2
fourth = normalize(seed)
fifth = seed + helper(seed)
EOF

GIT_AUTHOR_DATE="2026-03-23T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-23T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-23T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-23T09:00:00Z" \
git commit -m "us7-r4"
```

## Step 7: Get The Real Revision IDs

```bash
cd /tmp/agg-us7-manual/repo
REVISION_ID_R4="$(git rev-parse HEAD)"
REVISION_ID_R3="$(git rev-parse HEAD~1)"
REVISION_ID_R2="$(git rev-parse HEAD~2)"
REVISION_ID_R1="$(git rev-parse HEAD~3)"
echo "$REVISION_ID_R1"
echo "$REVISION_ID_R2"
echo "$REVISION_ID_R3"
echo "$REVISION_ID_R4"
```

## Step 8: Create The Revision-Level genCodeDesc Records

```bash
cat > "/tmp/agg-us7-manual/genCodeDescSet/${REVISION_ID_R1}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "HumanOnlyRevision",
  "SUMMARY": {
    "totalCodeLines": 5,
    "fullGeneratedCodeLines": 0,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/mixed.py",
      "codeLines": []
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us7-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R1}"
  }
}
EOF

cat > "/tmp/agg-us7-manual/genCodeDescSet/${REVISION_ID_R2}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 6,
    "fullGeneratedCodeLines": 3,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/mixed.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"},
        {"lineLocation": 4, "genRatio": 100, "genMethod": "codeCompletion"},
        {"lineLocation": 5, "genRatio": 100, "genMethod": "codeCompletion"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us7-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R2}"
  }
}
EOF

cat > "/tmp/agg-us7-manual/genCodeDescSet/${REVISION_ID_R3}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "HumanRewriteRevision",
  "SUMMARY": {
    "totalCodeLines": 5,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/mixed.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us7-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R3}"
  }
}
EOF

cat > "/tmp/agg-us7-manual/genCodeDescSet/${REVISION_ID_R4}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 5,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "DETAIL": [
    {
      "fileName": "src/mixed.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100, "genMethod": "codeCompletion"},
        {"lineLocation": 5, "genRatio": 60, "genMethod": "vibeCoding"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us7-manual/repo",
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
  --repoURL /tmp/agg-us7-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-us7-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us7-manual/genCodeDescSet \
  --logLevel debug
```

## Step 10: Inspect The Output

```bash
cat /tmp/agg-us7-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 5,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us7-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for us7-r4>"
  }
}
```

## Step 11: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 5`
2. `SUMMARY.fullGeneratedCodeLines == 1`
3. `SUMMARY.partialGeneratedCodeLines == 1`
4. `REPOSITORY.revisionId == git rev-parse HEAD`

With `--logLevel debug`, also verify that line 3 still points to the older full-AI revision while line 5 points to the later partial-AI revision.

## Why The Expected Result Is 5 / 1 / 1

This scenario mixes several within-window transitions:

- older human lines that remain human
- a full-AI line that survives unchanged
- AI output that was later rewritten or removed by a human
- a later partial-AI line introduced near the end of the window

So the final live snapshot contains:

- `5` live code lines total
- `1` surviving full-AI line
- `1` surviving partial-AI line