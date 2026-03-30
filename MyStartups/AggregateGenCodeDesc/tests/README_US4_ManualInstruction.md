# US-4 Manual Instruction

## Purpose

This document describes how to verify `US-4` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository
- start from the final live snapshot at `endTime`
- exclude AI-attributed lines that were deleted before `endTime`
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
- `testdata/us4_deleted_lines_excluded/query.json`
- `testdata/us4_deleted_lines_excluded/01_genCodeDesc.json`
- `testdata/us4_deleted_lines_excluded/02_genCodeDesc.json`
- `testdata/us4_deleted_lines_excluded/expected_result.json`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us4-manual/repo
mkdir -p /tmp/agg-us4-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us4-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The First AI Revision With Four Lines

```bash
mkdir -p src
cat > src/temp_rules.py <<'EOF'
rule_one = 'allow'
rule_two = 'deny'
rule_three = 'audit'
rule_four = 'notify'
EOF

GIT_AUTHOR_DATE="2026-03-06T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-06T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-06T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-06T09:00:00Z" \
git commit -m "us4-r1"
```

## Step 4: Delete Two Of Those Lines In A Later Revision

```bash
cat > src/temp_rules.py <<'EOF'
rule_one = 'allow'
rule_two = 'deny'
EOF

GIT_AUTHOR_DATE="2026-03-21T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-21T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-21T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-21T09:00:00Z" \
git commit -m "us4-r2"
```

## Step 5: Get The Real Revision IDs

```bash
cd /tmp/agg-us4-manual/repo
REVISION_ID_R2="$(git rev-parse HEAD)"
REVISION_ID_R1="$(git rev-parse HEAD~1)"
echo "$REVISION_ID_R1"
echo "$REVISION_ID_R2"
```

## Step 6: Create The Revision-Level genCodeDesc Records

```bash
cat > "/tmp/agg-us4-manual/genCodeDescSet/${REVISION_ID_R1}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 4,
    "fullGeneratedCodeLines": 4,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/temp_rules.py",
      "codeLines": [
        {"lineLocation": 1, "genRatio": 100, "genMethod": "vibeCoding"},
        {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"},
        {"lineLocation": 3, "genRatio": 100, "genMethod": "vibeCoding"},
        {"lineLocation": 4, "genRatio": 100, "genMethod": "vibeCoding"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us4-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R1}"
  }
}
EOF

cat > "/tmp/agg-us4-manual/genCodeDescSet/${REVISION_ID_R2}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "HumanOnlyRevision",
  "SUMMARY": {
    "totalCodeLines": 2,
    "fullGeneratedCodeLines": 0,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/temp_rules.py",
      "codeLines": []
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us4-manual/repo",
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
  --repoURL /tmp/agg-us4-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-us4-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us4-manual/genCodeDescSet \
  --logLevel info
```

## Step 8: Inspect The Output

```bash
cat /tmp/agg-us4-manual/out.json
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
    "repoURL": "/tmp/agg-us4-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for us4-r2>"
  }
}
```

## Step 9: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 2`
2. `SUMMARY.fullGeneratedCodeLines == 2`
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD`

## Why The Expected Result Is 2 / 2 / 0

The first revision created four AI-attributed lines.
The later revision deleted two of them.

At `endTime`, only two live lines still exist, and both still blame to the first AI revision.

So the final summary is:

- total live changed lines = `2`
- full AI-generated lines = `2`
- partial AI-generated lines = `0`

The deleted lines do not count, because the metric is defined on the final live snapshot at `endTime`.
