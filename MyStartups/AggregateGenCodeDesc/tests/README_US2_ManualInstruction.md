# US-2 Manual Instruction

## Purpose

This document describes how to verify `US-2` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- analyze a real temporary Git repository
- discover which surviving lines still belong to the earlier AI revision
- reset attribution for the line rewritten by a later human revision
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
- `testdata/us2_human_overwrites_ai_live_changed/query.json`
- `testdata/us2_human_overwrites_ai_live_changed/01_genCodeDesc.json`
- `testdata/us2_human_overwrites_ai_live_changed/02_genCodeDesc.json`
- `testdata/us2_human_overwrites_ai_live_changed/expected_result.json`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us2-manual/repo
mkdir -p /tmp/agg-us2-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us2-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The First AI-Attributed Revision

```bash
mkdir -p src
cat > src/normalize.py <<'EOF'
value = raw.strip()
value = value.lower()
result = value
EOF

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git commit -m "us2-r1"
```

## Step 4: Rewrite One Line In A Later Human Revision

```bash
cat > src/normalize.py <<'EOF'
value = raw.strip()
value = raw.casefold()
result = value
EOF

GIT_AUTHOR_DATE="2026-03-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-20T09:00:00Z" \
git commit -m "us2-r2"
```

## Step 5: Get The Real Revision IDs

```bash
cd /tmp/agg-us2-manual/repo
REVISION_ID_R2="$(git rev-parse HEAD)"
REVISION_ID_R1="$(git rev-parse HEAD~1)"
echo "$REVISION_ID_R1"
echo "$REVISION_ID_R2"
```

You will use these revision ids in the metadata filenames and inside the metadata `REPOSITORY` blocks.

## Step 6: Create The Revision-Level genCodeDesc Records

Create these two files under `--genCodeDescSetDir`:

```bash
cat > "/tmp/agg-us2-manual/genCodeDescSet/${REVISION_ID_R1}_genCodeDesc.json" <<EOF
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "codeAgent": "ExampleAgent",
  "SUMMARY": {
    "totalCodeLines": 3,
    "fullGeneratedCodeLines": 3,
    "partialGeneratedCodeLines": 0
  },
  "DETAIL": [
    {
      "fileName": "src/normalize.py",
      "codeLines": [
        {"lineLocation": 1, "genRatio": 100, "genMethod": "vibeCoding"},
        {"lineLocation": 2, "genRatio": 100, "genMethod": "vibeCoding"},
        {"lineLocation": 3, "genRatio": 100, "genMethod": "vibeCoding"}
      ]
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us2-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R1}"
  }
}
EOF

cat > "/tmp/agg-us2-manual/genCodeDescSet/${REVISION_ID_R2}_genCodeDesc.json" <<EOF
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
      "fileName": "src/normalize.py",
      "codeLines": []
    }
  ],
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us2-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_ID_R2}"
  }
}
EOF
```

## Step 7: Run The CLI

From the project root:

```bash
cd /Users/enigmawu/VSCode/MyLLM_Arena/MyStartups/AggregateGenCodeDesc

python3 aggregateGenCodeDesc.py \
  --repoURL /tmp/agg-us2-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --outputFile /tmp/agg-us2-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us2-manual/genCodeDescSet
```

## Step 8: Inspect The Output

```bash
cat /tmp/agg-us2-manual/out.json
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
    "repoURL": "/tmp/agg-us2-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for us2-r2>"
  }
}
```

## Step 9: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 3`
2. `SUMMARY.fullGeneratedCodeLines == 2`
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD`

## Why The Expected Result Is 3 / 2 / 0

At `endTime`, the file still has 3 live code lines.

- line 1 still blames to `us2-r1`, so it keeps `genRatio = 100`
- line 2 now blames to `us2-r2`, and that revision has no AI line metadata, so it contributes `0`
- line 3 still blames to `us2-r1`, so it keeps `genRatio = 100`

So the final summary is:

- total live changed lines = `3`
- full AI-generated lines = `2`
- partial AI-generated lines = `0`

## Important Consistency Rule

The current implementation validates metadata identity.

So the `REPOSITORY` block inside each `genCodeDesc` record must match the CLI query target for:

- `vcsType`
- `repoURL`
- `repoBranch`
- `revisionId`

If any of those values differ, the current CLI should fail instead of silently using mismatched metadata.