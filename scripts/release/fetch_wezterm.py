#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import urllib.request
import zipfile
import hashlib

ROOT = Path(__file__).resolve().parents[2]
WEZTERM_TAG = "20240203-110809-5046fc22"
WEZTERM_ARCHIVE = f"WezTerm-macos-{WEZTERM_TAG}.zip"
WEZTERM_BASE_URL = f"https://github.com/wezterm/wezterm/releases/download/{WEZTERM_TAG}"
WEZTERM_URL = f"{WEZTERM_BASE_URL}/{WEZTERM_ARCHIVE}"
WEZTERM_SHA256_URL = f"{WEZTERM_URL}.sha256"
VENDOR_DIR = ROOT / "packaging" / "macos" / "vendor"
DOWNLOADS_DIR = VENDOR_DIR / "downloads"
BUNDLED_APP = VENDOR_DIR / "WezTerm.app"
WEZTERM_EXECUTABLES = ("strip-ansi-escapes", "wezterm", "wezterm-gui", "wezterm-mux-server")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return destination
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    return destination


def expected_archive_hash(sha_file: Path) -> str:
    first = sha_file.read_text(encoding="utf-8").split()[0]
    if len(first) != 64:
        raise SystemExit(f"Unexpected WezTerm SHA256 file format: {sha_file}")
    return first.lower()


def fetch_wezterm(*, force: bool = False) -> Path:
    archive = DOWNLOADS_DIR / WEZTERM_ARCHIVE
    sha_file = DOWNLOADS_DIR / f"{WEZTERM_ARCHIVE}.sha256"
    if force:
        archive.unlink(missing_ok=True)
        sha_file.unlink(missing_ok=True)
        shutil.rmtree(BUNDLED_APP, ignore_errors=True)
    download(WEZTERM_URL, archive)
    download(WEZTERM_SHA256_URL, sha_file)
    expected = expected_archive_hash(sha_file)
    actual = sha256(archive)
    if actual != expected:
        raise SystemExit(f"WezTerm SHA256 mismatch: expected {expected}, got {actual}")
    if not BUNDLED_APP.exists():
        temp_extract = VENDOR_DIR / "extract"
        shutil.rmtree(temp_extract, ignore_errors=True)
        temp_extract.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zip_handle:
            zip_handle.extractall(temp_extract)
        found = next(temp_extract.glob("**/WezTerm.app"), None)
        if found is None:
            raise SystemExit("Downloaded WezTerm archive did not contain WezTerm.app")
        shutil.move(str(found), BUNDLED_APP)
        shutil.rmtree(temp_extract, ignore_errors=True)
    repair_wezterm_permissions(BUNDLED_APP)
    return BUNDLED_APP


def repair_wezterm_permissions(app_bundle: Path) -> None:
    macos_dir = app_bundle / "Contents" / "MacOS"
    for executable in WEZTERM_EXECUTABLES:
        path = macos_dir / executable
        if path.exists():
            path.chmod(path.stat().st_mode | 0o755)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and verify pinned WezTerm for Exegesis packaging.")
    parser.add_argument("--force", action="store_true", help="Redownload and re-extract the pinned WezTerm archive.")
    args = parser.parse_args()
    print(fetch_wezterm(force=args.force).relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
