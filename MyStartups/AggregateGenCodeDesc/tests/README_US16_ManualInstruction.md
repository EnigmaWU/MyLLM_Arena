# US-16 Manual Instruction

## Purpose

This document describes how to verify `US-16` manually in standalone mode, outside the automated test harness.

The current goal is to prove that `aggregateGenCodeDesc.py` can:

- handle deletions and rewrites within a single measurement window under Algorithm B (`period_added_ai_ratio`)
- NOT count a line that was added then deleted within the same window
- correctly shift line origin when a line is rewritten in-window (the rewriting commit becomes the origin)
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
- `tests/test_us16_period_added_deletions_and_rewrites_tdd.py`

## Step 1: Create A Temporary Working Area

```bash
mkdir -p /tmp/agg-us16-manual/repo
mkdir -p /tmp/agg-us16-manual/genCodeDescSet
```

## Step 2: Initialize A Real Git Repository

```bash
cd /tmp/agg-us16-manual/repo
git init -b main
git config user.name "AggregateGenCodeDesc Manual"
git config user.email "manual@example.local"
```

## Step 3: Create The Pre-Window Human Baseline (r0)

4 human code lines, all before the window.

```bash
mkdir -p src
cat > src/report.py <<'EOF'
def report(data):
    result = process(data)
    output = format(result)
    return output
EOF

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-02-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-02-20T09:00:00Z" \
git commit -m "human-base"
```

## Step 4: AI Rewrites Line 2 And Adds Line 4 In-Window (r1)

```bash
cat > src/report.py <<'EOF'
def report(data):
    result = ai_process(data)
    output = format(result)
    ai_extra = enhance(output)
    return output
EOF

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-10T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-10T09:00:00Z" \
git commit -m "ai-rewrite-and-add"
```

## Step 5: Human Rewrites Line 2 Back, Removes AI Extra, Adds Human Line (r2)

```bash
cat > src/report.py <<'EOF'
def report(data):
    result = manual_process(data)
    output = format(result)
    checked = validate(output)
    return output
EOF

GIT_AUTHOR_DATE="2026-03-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-20T09:00:00Z" \
git add -A

GIT_AUTHOR_DATE="2026-03-20T09:00:00Z" \
GIT_COMMITTER_DATE="2026-03-20T09:00:00Z" \
git commit -m "human-rewrite-and-fix"
```

## Step 6: Get The Real Revision IDs

```bash
cd /tmp/agg-us16-manual/repo
REVISION_R2="$(git rev-parse HEAD)"
REVISION_R1="$(git rev-parse HEAD~1)"
echo "r1 = $REVISION_R1"
echo "r2 = $REVISION_R2"
```

## Step 7: Create The Revision-Level genCodeDesc Records

```bash
# r1: line 2 AI rewrite + line 4 AI addition
cat > "/tmp/agg-us16-manual/genCodeDescSet/${REVISION_R1}_genCodeDesc.json" <<EOF
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
    "repoURL": "/tmp/agg-us16-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R1}"
  },
  "DETAIL": [
    {
      "fileName": "src/report.py",
      "codeLines": [
        {"lineLocation": 2, "genRatio": 100},
        {"lineLocation": 4, "genRatio": 100}
      ]
    }
  ]
}
EOF

# r2: no AI-generated lines
cat > "/tmp/agg-us16-manual/genCodeDescSet/${REVISION_R2}_genCodeDesc.json" <<EOF
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
    "repoURL": "/tmp/agg-us16-manual/repo",
    "repoBranch": "main",
    "revisionId": "${REVISION_R2}"
  },
  "DETAIL": [
    {
      "fileName": "src/report.py",
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
  --repoURL /tmp/agg-us16-manual/repo \
  --repoBranch main \
  --startTime 2026-03-01 \
  --endTime 2026-03-31 \
  --algorithm B \
  --metric period_added_ai_ratio \
  --outputFile /tmp/agg-us16-manual/out.json \
  --genCodeDescSetDir /tmp/agg-us16-manual/genCodeDescSet \
  --logLevel debug
```

## Step 9: Inspect The Output

```bash
cat /tmp/agg-us16-manual/out.json
```

Expected shape:

```json
{
  "protocolName": "generatedTextDesc",
  "protocolVersion": "26.03",
  "SUMMARY": {
    "totalCodeLines": 2,
    "fullGeneratedCodeLines": 0,
    "partialGeneratedCodeLines": 0
  },
  "REPOSITORY": {
    "vcsType": "git",
    "repoURL": "/tmp/agg-us16-manual/repo",
    "repoBranch": "main",
    "revisionId": "<your real revision id for r2>"
  }
}
```

## Step 10: What To Check

Verify these values:

1. `SUMMARY.totalCodeLines == 2` — only 2 lines have in-window origin (line 2 rewritten by r2 + line 4 added by r2)
2. `SUMMARY.fullGeneratedCodeLines == 0` — the AI line from r1 was replaced by human in r2; the other AI line was deleted/replaced
3. `SUMMARY.partialGeneratedCodeLines == 0`
4. `REPOSITORY.revisionId == git rev-parse HEAD` (r2)
5. Pre-window lines (`def report(data):`, `output = format(result)`, `return output`) are NOT counted
6. The AI `ai_extra` line from r1 was deleted in r2 — it does NOT appear in the count
