# US-18 Manual Instruction

## Purpose

This document describes how to verify `US-18` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- handle a non-fast-forward merge under Algorithm B (`period_added_ai_ratio`)
- count AI lines from both the main branch and a merged feature branch
- resolve the merge commit correctly so both contributions survive
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
- `tests/test_us18_period_added_merge_aware_tdd.py`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us18-manual/repo
mkdir -p /tmp/agg-us18-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us18-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The Pre-Window Human Baseline (r0)

```bash
mkdir -p src
cat > src/base.py <<'EOF'
def base():
    return 0
EOF

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git commit -m "human-base"
```

## Step 4: AI Adds 1 Line On Main In-Window (r1)

```bash
cat > src/base.py <<'EOF'
def base():
    x = ai_init()
    return 0
EOF

GIT_AUTHOR_DATE="2026-03-05T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-05T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-05T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-05T09:00:00Z" \
git commit -m "ai-on-main"
```

## Step 5: Create Feature Branch From r0 And Add AI Line (r2)

```bash
git checkout -b feature HEAD~1

cat > src/base.py <<'EOF'
def base():
    return 0
    y = ai_enhance()
EOF

GIT_AUTHOR_DATE="2026-03-08T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-08T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-08T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-08T09:00:00Z" \
git commit -m "ai-on-feature"
```

## Step 6: Merge Feature Into Main With Manual Resolution (r3)

```bash
git checkout main
git merge --no-ff --no-commit feature || true

# Resolve the merge manually
cat > src/base.py <<'EOF'
def base():
    x = ai_init()
    return 0
    y = ai_enhance()
EOF

GIT_AUTHOR_DATE="2026-03-15T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-15T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-15T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-15T09:00:00Z" \
git commit -m "merge-feature"
```

## Step 7: Get The Real Revision IDs

```bash
cd /tmp/agg-us18-manual/repo
REVISION_R3="$(git rev-parse HEAD)"
REVISION_R1="$(git rev-parse HEAD~1)"
REVISION_R2="$(git log --all --oneline | grep 'ai-on-feature' | awk '{print $1}')"
REVISION_R2_FULL="$(git rev-parse $REVISION_R2)"
echo "r1 = $REVISION_R1"
echo "r2 = $REVISION_R2_FULL"
echo "r3 = $REVISION_R3"
```

## Step 8: Create The Revision-Level genCodeDesc Records

```bash
# r1: line 2 is AI (ai_init)
cat > "/tmp/agg-us18-manual/genCodeDescSet/${REVISION_R1}_genCodeDesc.json" <<EOF
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
    "repoURL": "/tmp/agg-us18-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R1}"
  },
  "DETAIL": [
    {
      "fileName": "src/base.py",
      "codeLines": [
        {"lineLocation": 2, "genRatio": 100}
      ]
    }
  ]
}
EOF

# r2: line 3 is AI (ai_enhance) — note the feature branch version had it at line 3
cat > "/tmp/agg-us18-manual/genCodeDescSet/${REVISION_R2_FULL}_genCodeDesc.json" <<EOF
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
    "repoURL": "/tmp/agg-us18-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R2_FULL}"
  },
  "DETAIL": [
    {
      "fileName": "src/base.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100}
      ]
    }
  ]
}
EOF

# r3: merge commit — both AI lines present
cat > "/tmp/agg-us18-manual/genCodeDescSet/${REVISION_R3}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 2,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us18-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R3}"
  },
  "DETAIL": [
    {
      "fileName": "src/base.py",
      "codeLines": [
        {"lineLocation": 2, "genRatio": 100},
        {"lineLocation": 4, "genRatio": 100}
      ]
    }
  ]
}
EOF
```

## Step 9: Run The CLI

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --repoURL /tmp/agg-us18-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --outputFile /tmp/agg-us18-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us18-manual/genCodeDescSet \
  --logLevel debug
```

## Step 10: Inspect The Output

```bash
cat /tmp/agg-us18-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 2,
    "fullGeneratedCodeLines": 2,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us18-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for r3 merge commit>"
  }
}
```

## Step 11: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 2` — both AI lines from main (r1) and feature (r2) survive the merge
2. `SUMMARY.fullGeneratedCodeLines == 2` — both lines are 100% AI-generated
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD` (r3 merge commit)
5. Pre-window lines (`def base():`, `return 0`) are NOT counted
6. The merge preserves contributions from both branches
