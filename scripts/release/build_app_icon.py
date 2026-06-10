#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ICONSET = ROOT / "packaging" / "macos" / "AppIcon.iconset"
ICNS = ROOT / "packaging" / "macos" / "AppIcon.icns"
REQUIRED_ICONSET_FILES = (
    "icon_16x16.png",
    "icon_16x16@2x.png",
    "icon_32x32.png",
    "icon_32x32@2x.png",
    "icon_128x128.png",
    "icon_128x128@2x.png",
    "icon_256x256.png",
    "icon_256x256@2x.png",
    "icon_512x512.png",
    "icon_512x512@2x.png",
)


def validate_iconset(iconset: Path = ICONSET) -> None:
    missing = [name for name in REQUIRED_ICONSET_FILES if not (iconset / name).is_file()]
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"AppIcon.iconset is missing required PNGs: {joined}")


def build_icon(iconset: Path = ICONSET, output: Path = ICNS) -> Path:
    validate_iconset(iconset)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["/usr/bin/iconutil", "--convert", "icns", "--output", str(output), str(iconset)],
        check=True,
        cwd=ROOT,
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build packaging/macos/AppIcon.icns from AppIcon.iconset.")
    parser.add_argument("--check", action="store_true", help="Only verify that the iconset has all required source PNGs.")
    args = parser.parse_args()
    if args.check:
        validate_iconset()
        print(f"validated {ICONSET.relative_to(ROOT)}")
        return 0
    output = build_icon()
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
