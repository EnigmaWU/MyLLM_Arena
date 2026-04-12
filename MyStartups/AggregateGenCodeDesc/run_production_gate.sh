#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required" >&2
  exit 1
}

command -v svn >/dev/null 2>&1 || {
  echo "svn is required for the production gate" >&2
  exit 1
}

command -v svnadmin >/dev/null 2>&1 || {
  echo "svnadmin is required for the production gate" >&2
  exit 1
}

echo "=== Stage 1: Full test suite (AlgA + AlgB legacy) ==="
python3 -m pytest -q tests/

echo ""
echo "=== Stage 2: AlgB NG (all scopes, all history tiers) ==="
python3 -m pytest -q TestsNG-AlgB/

echo ""
echo "=== Stage 3: AlgC NG (all scopes, all history tiers) ==="
python3 -m pytest -q TestsNG-AlgC/

echo ""
echo "=== Stage 4: Operator scenario NG ==="
python3 -m pytest -q TestsNG/

echo ""
echo "=== Production gate PASSED ==="