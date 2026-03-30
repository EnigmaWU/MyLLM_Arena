# US-3 Manual Instruction

## Purpose

This document describes how to verify `US-3` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository
- detect that later AI-written lines become the effective origin of surviving lines
- keep unchanged human lines as human-owned
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
- `testdata/us3_ai_overwrites_human_live_changed/query.json`
- `testdata/us3_ai_overwrites_human_live_changed/01_genCodeDesc.json`
- `testdata/us3_ai_overwrites_human_live_changed/02_genCodeDesc.json`
- `testdata/us3_ai_overwrites_human_live_changed/expected_result.json`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us3-manual/repo
mkdir -p /tmp/agg-us3-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us3-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The First Human Revision

```bash
mkdir -p src
cat > src/score.py <<'EOF'
score = base
score = score + 1
return score
EOF

GIT_AUTHOR_DATE="2026-03-05T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-05T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-05T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-05T09:00:00Z" \
git commit -m "us3-r1"
```

## Step 4: Rewrite Two Lines In A Later AI Revision

```bash
cat > src/score.py <<'EOF'
score = base
score = score * 2
return max(score, 0)
EOF

GIT_AUTHOR_DATE="2026-03-18T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-18T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-18T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-18T09:00:00Z" \
git commit -m "us3-r2"
```

## Step 5: Get The Real Revision IDs

```bash
cd /tmp/agg-us3-manual/repo
REVISION_ID_R2="$(git rev-parse HEAD)"
REVISION_ID_R1="$(git rev-parse HEAD~1)"
echo "$REVISION_ID_R1"
echo "$REVISION_ID_R2"
```

## Step 6: Create The Revision-Level genCodeDesc Records

```bash
cat > "/tmp/agg-us3-manual/genCodeDescSet/${REVISION_ID_R1}_genCodeDesc.json" <<EOF
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
      "fileName": "src/score.py",
      "codeLines": []
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us3-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R1}"
  }
}
EOF

cat > "/tmp/agg-us3-manual/genCodeDescSet/${REVISION_ID_R2}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "DETAIL": [
    {
      "fileName": "src/score.py",
      "codeLines": [
        {"lineLocation": 2, "genRatio": 100, "genMethod": "codeCompletion"},
        {"lineLocation": 3, "genRatio": 80, "genMethod": "codeCompletion"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us3-manual/repo",
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
  --repoURL /tmp/agg-us3-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-us3-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us3-manual/genCodeDescSet \
  --logLevel debug
```

## Step 8: Inspect The Output

```bash
cat /tmp/agg-us3-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 1,
    "partialGeneratedCodeLines": 1
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us3-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for us3-r2>"
  }
}
```

## Step 9: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 3`
2. `SUMMARY.fullGeneratedCodeLines == 1`
3. `SUMMARY.partialGeneratedCodeLines == 1`
4. `REPOSITORY.revisionId == git rev-parse HEAD`

## Why The Expected Result Is 3 / 1 / 1

At `endTime`, the file still has 3 live code lines.

- line 1 still blames to `us3-r1`, so it remains `human/unattributed`
- line 2 now blames to `us3-r2`, so it contributes `100%-ai`
- line 3 now blames to `us3-r2`, so it contributes `80%-ai`

So the final summary is:

- total live changed lines = `3`
- full AI-generated lines = `1`
- partial AI-generated lines = `1`