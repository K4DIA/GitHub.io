#!/usr/bin/env bash
# Rebuild fieldrecord.zip from src/.
#
# The browser loads this zip into Pyodide and unpacks it into the working
# directory, so the layout inside is flat: modules at the root, with radios/
# and assets/ beside them.
#
# src/ is the source. Before this script existed the only copy of the
# generator lived inside the zip, which made it unreviewable in git and
# impossible to diff. Edit src/, run this, commit both.
set -euo pipefail
cd "$(dirname "$0")"

[ -d src ] || { echo "no src/ here" >&2; exit 1; }
[ -f src/webapi.py ] || { echo "src/ does not look like the package" >&2; exit 1; }

find src -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find src -name '*.pyc' -delete 2>/dev/null || true

python3 - <<'PY'
import pathlib, zipfile
src = pathlib.Path("src")
out = pathlib.Path("fieldrecord.zip")
# README.md documents the source for whoever edits it; it is not part of the
# package and every visitor would otherwise download it.
SKIP = {"README.md"}
files = sorted(p for p in src.rglob("*")
               if p.is_file() and "__pycache__" not in p.parts
               and p.name not in SKIP)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, p.relative_to(src).as_posix())
kb = out.stat().st_size / 1024
print("fieldrecord.zip  %d files  %.0f KB" % (len(files), kb))
PY
