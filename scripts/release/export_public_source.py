#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "packaging" / "release" / "public_source_manifest.json"
DEFAULT_OUTPUT = ROOT / "packaging" / "release" / "public-source" / "exegesis-developer-preview-source"


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_denied(relative_path: Path, manifest: dict[str, object]) -> bool:
    parts = relative_path.parts
    exclude_names = set(manifest.get("exclude_names", []))
    if any(part in exclude_names for part in parts):
        return True
    lowered = str(relative_path).casefold()
    for fragment in manifest.get("deny_fragments", []):
        if str(fragment).casefold() in lowered:
            return True
    if relative_path.suffix in {".pyc", ".pyo"}:
        return True
    return False


def included_paths(manifest: dict[str, object]) -> list[Path]:
    paths = []
    for raw in manifest.get("include_paths", []):
        rel = Path(str(raw))
        if _is_denied(rel, manifest):
            raise SystemExit(f"Public manifest includes a denied path: {rel}")
        source = ROOT / rel
        if not source.exists():
            raise SystemExit(f"Public manifest path does not exist: {rel}")
        paths.append(rel)
    return paths


def copy_public_source(output_dir: Path = DEFAULT_OUTPUT, *, clean: bool = True) -> Path:
    manifest = load_manifest()
    if clean:
        shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    mappings = {Path(src): Path(dst) for src, dst in dict(manifest.get("root_file_mappings", {})).items()}
    for rel in included_paths(manifest):
        source = ROOT / rel
        destination_rel = mappings.get(rel, rel)
        destination = output_dir / destination_rel
        if source.is_dir():
            for path in source.rglob("*"):
                item_rel = path.relative_to(ROOT)
                if _is_denied(item_rel, manifest) or not path.is_file():
                    continue
                item_destination = output_dir / mappings.get(rel, rel) / path.relative_to(source)
                item_destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, item_destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    return output_dir


def make_zip(source_dir: Path) -> Path:
    archive = source_dir.with_suffix(".zip")
    archive.unlink(missing_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_handle:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                zip_handle.write(path, path.relative_to(source_dir.parent))
    return archive


def main() -> int:
    parser = argparse.ArgumentParser(description="Export source files allowed for the public Developer preview branch.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-zip", action="store_true")
    args = parser.parse_args()
    output = copy_public_source(args.output)
    print(output.relative_to(ROOT))
    if not args.no_zip:
        archive = make_zip(output)
        print(archive.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
