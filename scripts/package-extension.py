#!/usr/bin/env python3
"""Build the optional test extension as an unsigned XPI."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
source = root / "extensions/ordnung-start"
target = root / "dist/ordnung-start-0.1.0-unsigned.xpi"
target.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(target, "w", ZIP_DEFLATED) as archive:
    for path in sorted(source.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(source).as_posix())
print(target)
