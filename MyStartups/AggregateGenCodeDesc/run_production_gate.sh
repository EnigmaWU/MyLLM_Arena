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

python3 -m pytest -q -m "production_scale" \
  tests/test_us13_git_production_scale_local_repo_tdd.py \
  tests/test_us14_svn_production_scale_local_repo_tdd.py