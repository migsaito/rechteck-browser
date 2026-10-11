#!/usr/bin/env bash
# Run inside the MozillaBuild shell, after bootstrapping the pinned source tree.
set -euo pipefail
if [[ $# -ne 1 ]]; then
  printf 'Usage: bash scripts/build-windows.sh /c/mozilla-source/firefox\n' >&2
  exit 2
fi
source_dir="$(cd "$1" && pwd)"
repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$source_dir" == *" "* ]]; then
  printf 'Firefox requires a source path without spaces.\n' >&2
  exit 2
fi
python3 "$repo_dir/scripts/prepare.py" "$source_dir"
python3 "$repo_dir/scripts/fix-build-telemetry.py" "$source_dir"
export PYTHONUNBUFFERED=1
cd "$source_dir"
./mach build
./mach package
./mach build installer
python3 "$repo_dir/scripts/collect.py" "$source_dir/obj-rechteck/dist" "$repo_dir/dist"
