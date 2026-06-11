#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from export_public_source import DEFAULT_OUTPUT, _is_denied, copy_public_source, load_manifest

ROOT = Path(__file__).resolve().parents[2]


def verify_public_source(source_dir: Path = DEFAULT_OUTPUT) -> None:
    manifest = load_manifest()
    if not source_dir.exists():
        copy_public_source(source_dir)
    offenders = []
    for path in source_dir.rglob("*"):
        rel = path.relative_to(source_dir)
        if _is_denied(rel, manifest):
            offenders.append(str(rel))
    if offenders:
        raise SystemExit("Public source export contains denied files:\n" + "\n".join(offenders))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the public source export excludes internal material.")
    parser.add_argument("--source", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest-only", action="store_true", help="Validate manifest include paths without copying export output.")
    args = parser.parse_args()
    if args.manifest_only:
        from export_public_source import included_paths

        included_paths(load_manifest())
        print("public source manifest validated")
        return 0
    source = args.source.resolve()
    verify_public_source(source)
    print(f"verified {source.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
