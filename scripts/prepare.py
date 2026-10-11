#!/usr/bin/env python3
"""Apply the Rechteck layer to an explicit, pinned Firefox source checkout."""
import argparse
import json
import re
import shutil
import struct
import subprocess
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = "/* BEGIN RECHTECK */"
END = "/* END RECHTECK */"


def replace_assignment(text, key, value, separator="=", prefix=""):
    pattern = rf"(?m)^{re.escape(prefix + key)}\s*{re.escape(separator)}.*$"
    result, count = re.subn(pattern, lambda _: f"{prefix}{key}{separator}{value}", text)
    if count != 1:
        raise ValueError(f"Expected exactly one assignment for {key}, found {count}")
    return result


def block(text, addition):
    pattern = re.escape(START) + r".*?" + re.escape(END)
    text = re.sub(pattern, "", text, flags=re.S).rstrip()
    return f"{text}\n\n{START}\n{addition.rstrip()}\n{END}\n"


def pixels(size):
    """Original rectangular mark, independent of Mozilla artwork."""
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            inside = size // 8 <= x < size * 7 // 8 and size // 8 <= y < size * 7 // 8
            color = (0, 0, 0, 0)
            if inside:
                color = (24, 24, 28, 255) if y < size // 3 else (
                    (242, 242, 242, 255) if y < size * 2 // 3 else (213, 44, 54, 255))
            if inside and size * 5 // 12 <= y < size // 2 and (
                    size // 3 <= x < size * 5 // 12 or size * 7 // 12 <= x < size * 2 // 3):
                color = (24, 24, 28, 255)
            row.extend(color)
        rows.append(bytes(row))
    return rows


def png(size):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\0" + row for row in pixels(size))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def ico():
    sizes = (16, 32, 48, 64, 128, 256)
    images = [png(size) for size in sizes]
    offset = 6 + 16 * len(sizes)
    entries = []
    for size, data in zip(sizes, images):
        entries.append(struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset))
        offset += len(data)
    return struct.pack("<HHH", 0, 1, len(sizes)) + b"".join(entries) + b"".join(images)


def plan(source):
    source = source.resolve()
    if not (source / "mach").is_file():
        raise ValueError("The target must be a Firefox source tree containing mach")
    files = {}
    brand = source / "browser/branding/unofficial"
    custom = source / "browser/branding/rechteck"
    required = ("configure.sh", "branding.nsi", "moz.build", "locales/en-US/brand.ftl", "locales/en-US/brand.properties")
    for relative in required:
        if not (brand / relative).is_file():
            raise ValueError(f"Missing upstream branding input: {relative}")
    configure = (brand / "configure.sh").read_text(encoding="utf-8")
    files[custom / "configure.sh"] = replace_assignment(configure, "MOZ_APP_DISPLAYNAME", "'Rechteck Browser'")
    ftl = (brand / "locales/en-US/brand.ftl").read_text(encoding="utf-8")
    for key in ("-brand-shorter-name", "-brand-short-name", "-brand-shortcut-name", "-brand-full-name", "-brand-product-name"):
        ftl = replace_assignment(ftl, key, " Rechteck Browser")
    files[custom / "locales/en-US/brand.ftl"] = replace_assignment(ftl, "-vendor-short-name", " Rechteck")
    properties = (brand / "locales/en-US/brand.properties").read_text(encoding="utf-8")
    for key in ("brandShorterName", "brandShortName", "brandFullName"):
        properties = replace_assignment(properties, key, "Rechteck Browser")
    files[custom / "locales/en-US/brand.properties"] = properties
    nsi = (brand / "branding.nsi").read_text(encoding="utf-8")
    for key, value in {
        "BrandFullNameInternal": "Rechteck Browser", "BrandFullName": "Rechteck Browser",
        "CompanyName": "Rechteck", "URLInfoAbout": "https://github.com/migsaito/rechteck-browser",
        "HelpLink": "https://github.com/migsaito/rechteck-browser/issues",
        "URLManualDownload": "https://github.com/migsaito/rechteck-browser/releases",
    }.items():
        nsi = replace_assignment(nsi, key, f'"{value}"', separator=" ", prefix="!define ")
    files[custom / "branding.nsi"] = nsi
    prefs = source / "browser/app/profile/firefox.js"
    css = source / "browser/base/content/browser.css"
    files[prefs] = block(prefs.read_text(encoding="utf-8"), (ROOT / "browser/preferences.js").read_text(encoding="utf-8"))
    files[css] = block(css.read_text(encoding="utf-8"), (ROOT / "browser/rectangle.css").read_text(encoding="utf-8"))
    mozconfig = source / "mozconfig"
    config = (ROOT / "config/mozconfig.windows").read_text(encoding="utf-8")
    if mozconfig.exists() and mozconfig.read_text(encoding="utf-8") != config:
        raise ValueError("Existing mozconfig differs. Save it elsewhere before preparing this checkout")
    files[mozconfig] = config
    # Preflight all targets before any writes; do not follow links outside the checkout.
    for destination in files:
        if not destination.resolve().is_relative_to(source):
            raise ValueError(f"Target escapes the source checkout: {destination}")
    if custom.is_symlink():
        raise ValueError("Custom branding directory must not be a symlink")
    return brand, custom, files


def apply(source, dry_run=False):
    brand, custom, files = plan(source)
    # Check copied files too: reject links so no writes can escape via inherited assets.
    if brand.is_symlink() or any(p.is_symlink() for p in brand.rglob("*")) or (custom.exists() and any(p.is_symlink() for p in custom.rglob("*"))):
        raise ValueError("Branding directories must not contain symlinks")
    if dry_run:
        return list(files)
    shutil.copytree(brand, custom, dirs_exist_ok=True)
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    # Replace Windows/Linux application icons, including content/about artwork.
    for path in custom.rglob("*"):
        if path.suffix == ".ico":
            path.write_bytes(ico())
        elif path.suffix == ".png":
            header = path.read_bytes()[:24]
            if header[:8] == b"\x89PNG\r\n\x1a\n":
                width, height = struct.unpack(">II", header[16:24])
                if width == height and 0 < width <= 1024:
                    path.write_bytes(png(width))
    return list(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    lock = json.loads((ROOT / "upstream.json").read_text(encoding="utf-8"))
    head = subprocess.check_output(["git", "-C", str(args.source), "rev-parse", "HEAD"], text=True).strip()
    if head != lock["revision"]:
        parser.error(f"Upstream revision mismatch. Expected {lock['revision']}, found {head}")
    try:
        paths = apply(args.source, args.dry_run)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(f"{'Would prepare' if args.dry_run else 'Prepared'} {len(paths)} text files and original branding assets.")


if __name__ == "__main__":
    main()
