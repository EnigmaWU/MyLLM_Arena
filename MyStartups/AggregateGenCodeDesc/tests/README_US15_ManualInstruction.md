# US-15 Manual Instruction

## Purpose

This document describes how to verify `US-15` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository using Algorithm B (`period_added_ai_ratio`)
- count only lines whose origin commit falls inside the requested time window
- exclude pre-window lines even though they survive to the final state
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
- `tests/test_us15_period_added_single_branch_baseline_tdd.py`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us15-manual/repo
mkdir -p /tmp/agg-us15-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us15-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The Pre-Window Human Baseline (r0)

This commit is **before** the window (Feb 20), so its lines must NOT be counted.

```bash
mkdir -p src
cat > src/calc.py <<'EOF'
def calc(x):
    value = x + 1
    return value
EOF

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git commit -m "human-base"
```

## Step 4: AI Adds 2 Lines In-Window (r1)

```bash
cat > src/calc.py <<'EOF'
def calc(x):
    value = x + 1
    norm = normalize(x)
    score = compute_score(norm)
    return value
EOF

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git commit -m "ai-add"
```

## Step 5: Human Adds 1 Line In-Window (r2)

```bash
cat > src/calc.py <<'EOF'
def calc(x):
    value = x + 1
    norm = normalize(x)
    score = compute_score(norm)
    total = value + score
    return value
EOF

GIT_AUTHOR_DATE="2026-03-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-20T09:00:00Z" \
git commit -m "human-add"
```

## Step 6: Get The Real Revision IDs

```bash
cd /tmp/agg-us15-manual/repo
REVISION_R2="$(git rev-parse HEAD)"
REVISION_R1="$(git rev-parse HEAD~1)"
echo "r1 = $REVISION_R1"
echo "r2 = $REVISION_R2"
```

## Step 7: Create The Revision-Level genCodeDesc Records

```bash
# r1: lines 3 and 4 are AI-generated (100%)
cat > "/tmp/agg-us15-manual/genCodeDescSet/${REVISION_R1}_genCodeDesc.json" <<EOF
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
    "repoURL": "/tmp/agg-us15-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R1}"
  },
  "DETAIL": [
    {
      "fileName": "src/calc.py",
      "codeLines": [
        {"lineLocation": 3, "genRatio": 100},
        {"lineLocation": 4, "genRatio": 100}
      ]
    }
  ]
}
EOF

# r2: no AI-generated lines
cat > "/tmp/agg-us15-manual/genCodeDescSet/${REVISION_R2}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 0,
    "fullGeneratedCodeLines": 0,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us15-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R2}"
  },
  "DETAIL": [
    {
      "fileName": "src/calc.py",
      "codeLines": []
    }
  ]
}
EOF
```

## Step 8: Run The CLI

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --repoURL /tmp/agg-us15-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --outputFile /tmp/agg-us15-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us15-manual/genCodeDescSet \
  --logLevel debug
```

## Step 9: Inspect The Output

```bash
cat /tmp/agg-us15-manual/out.json
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
    "repoURL": "/tmp/agg-us15-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for r2>"
  }
}
```

## Step 10: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 3` — only in-window lines (2 from r1 + 1 from r2)
2. `SUMMARY.fullGeneratedCodeLines == 2` — the 2 AI lines from r1
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD` (r2)
5. Pre-window lines (`def calc(x):`, `value = x + 1`, `return value`) are NOT counted even though they survive
