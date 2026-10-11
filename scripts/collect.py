#!/usr/bin/env python3
"""Collect a real completed installer; never rename the browser binary to setup.exe."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def collect(source, destination):
    candidates = sorted(p for p in source.glob("*.exe") if "installer" in p.name.lower())
    if len(candidates) != 1:
        raise ValueError(f"Expected one full installer in {source}, found {len(candidates)}")
    installer = candidates[0]
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "Rechteck-Browser-Setup.exe"
    shutil.copy2(installer, target)
    checksum = hashlib.sha256(target.read_bytes()).hexdigest()
    (destination / "SHA256SUMS").write_text(f"{checksum}  {target.name}\n", encoding="utf-8")
    root = Path(__file__).resolve().parents[1]
    lock = json.loads((root / "upstream.json").read_text(encoding="utf-8"))
    (destination / "build-info.json").write_text(json.dumps({
        "product": "Rechteck Browser", "upstream": lock,
        "installer": target.name, "sha256": checksum, "status": "development-unsigned",
    }, indent=2) + "\n", encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        print(collect(args.source, args.destination))
    except (ValueError, OSError) as error:
        parser.error(str(error))
