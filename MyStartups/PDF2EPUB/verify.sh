#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_PDF="$ROOT_DIR/tstBuk/LLMOps.pdf"
TOOL="$ROOT_DIR/myPdf2Epub.py"
OUT_DIR="$ROOT_DIR/tstBuk/out"

mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR"/*.epub || true

echo "[1/4] Pre-checks"
[[ -f "$INPUT_PDF" ]] || { echo "Missing input PDF: $INPUT_PDF"; exit 1; }
[[ -f "$TOOL" ]] || { echo "Missing tool script: $TOOL"; exit 1; }

echo "[2/4] Run default mode"
python3 "$TOOL" --input "$INPUT_PDF" --output "$OUT_DIR/LLMOps_default.epub"

echo "[3/4] Run keepIndex mode"
python3 "$TOOL" --input "$INPUT_PDF" --output "$OUT_DIR/LLMOps_keepIndex.epub" --keepIndex

echo "[3.5/4] Run chapter-by-chapter mode"
python3 "$TOOL" --input "$INPUT_PDF" --output "$OUT_DIR/LLMOps_split.epub" --chapter-by-chapter

echo "[4/4] Validate EPUB outputs"
OUT_DIR="$OUT_DIR" python3 - <<'PY'
import os
import sys
import zipfile

root = os.environ["OUT_DIR"]
files = [
    os.path.join(root, "LLMOps_default.epub"),
    os.path.join(root, "LLMOps_keepIndex.epub"),
]

split_files = [
    os.path.join(root, name)
    for name in os.listdir(root)
    if name.startswith("LLMOps_split_") and name.endswith(".epub")
]
if not split_files:
    print("No chapter-by-chapter outputs were generated.")
    sys.exit(7)
files.extend(split_files)

for f in files:
    if not os.path.exists(f):
        print(f"Missing output: {f}")
        sys.exit(2)
    if os.path.getsize(f) < 1024:
        print(f"Output too small, likely invalid: {f}")
        sys.exit(3)
    with zipfile.ZipFile(f, "r") as zf:
        names = zf.namelist()
        if not names:
            print(f"Empty EPUB archive: {f}")
            sys.exit(4)
        if "mimetype" not in names:
            print(f"Invalid EPUB (missing mimetype): {f}")
            sys.exit(5)
        if "META-INF/container.xml" not in names:
            print(f"Invalid EPUB (missing container.xml): {f}")
            sys.exit(6)
print("All verification checks passed.")
PY

echo "Done. Outputs are in: $OUT_DIR"
