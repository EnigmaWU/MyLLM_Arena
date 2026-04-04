# US-17 Manual Instruction

## Purpose

This document describes how to verify `US-17` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- handle a Git rename (file move) under Algorithm B (`period_added_ai_ratio`)
- count only lines whose origin commit falls inside the window, even after a rename
- exclude pre-window lines that survive the rename unchanged
- produce the expected protocol-shaped aggregate output

## Current Scope

This manual flow matches the current implementation boundary:

- Git only
- `Algorithm B` only (`--metric period_added_ai_ratio`)
- `Scope A` only
- `metadataSource=genCodeDesc` only
- `--genCodeDescSetDir` as the current local metadata adapter

## Files Used As Reference

- `aggregateGenCodeDesc.py`
- `tests/test_us17_period_added_git_rename_tdd.py`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us17-manual/repo
mkdir -p /tmp/agg-us17-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us17-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The Pre-Window File (r0)

3 human code lines under the old file name.

```bash
mkdir -p src
cat > src/old_name.py <<'EOF'
def helper(x):
    y = x * 2
    return y
EOF

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git commit -m "create-file"
```

## Step 4: Rename File And Add AI Line In-Window (r1)

```bash
git mv src/old_name.py src/new_name.py

cat > src/new_name.py <<'EOF'
def helper(x):
    y = x * 2
    z = ai_transform(y)
    return y
EOF

GIT_AUTHOR_DATE="2026-03-15T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-15T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-15T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-15T09:00:00Z" \
git commit -m "rename-and-ai-add"
```

## Step 5: Get The Real Revision ID

```bash
cd /tmp/agg-us17-manual/repo
REVISION_R1="$(git rev-parse HEAD)"
echo "r1 = $REVISION_R1"
```

## Step 6: Create The Revision-Level genCodeDesc Record

```bash
# r1: line 3 in new_name.py is AI-generated
cat > "/tmp/agg-us17-manual/genCodeDescSet/${REVISION_R1}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 1,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us17-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R1}"
  },
  "DETAIL": [
    {
      "fileName": "src/new_name.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100}
      ]
    }
  ]
}
EOF
```

## Step 7: Run The CLI

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --repoURL /tmp/agg-us17-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --outputFile /tmp/agg-us17-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us17-manual/genCodeDescSet \
  --logLevel debug
```

## Step 8: Inspect The Output

```bash
cat /tmp/agg-us17-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 1,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us17-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for r1>"
  }
}
```

## Step 9: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 1` — only the AI line added in r1 has an in-window origin
2. `SUMMARY.fullGeneratedCodeLines == 1` — that line is 100% AI-generated
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD` (r1)
5. Pre-window lines (`def helper(x):`, `y = x * 2`, `return y`) survive the rename but are NOT counted because their origin (r0) is before the window
