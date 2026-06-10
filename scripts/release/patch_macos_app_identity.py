#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import plistlib
import shutil

ROOT = Path(__file__).resolve().parents[2]
APP_NAME = "Exegesis"
BUNDLE_ID = "studio.exegesis.developer"
ICON_SOURCE = ROOT / "packaging" / "macos" / "AppIcon.icns"
WEZTERM_VENDOR_APP = ROOT / "packaging" / "macos" / "vendor" / "WezTerm.app"
WEZTERM_EXECUTABLES = ("strip-ansi-escapes", "wezterm", "wezterm-gui", "wezterm-mux-server")
VISIBLE_PLIST_KEYS = (
    "CFBundleName",
    "CFBundleDisplayName",
    "CFBundleGetInfoString",
    "NSHumanReadableCopyright",
)


def read_plist(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return plistlib.load(handle)


def write_plist(path: Path, payload: dict[str, object]) -> None:
    with path.open("wb") as handle:
        plistlib.dump(payload, handle, sort_keys=False)


def patch_info_plist(
    plist_path: Path,
    *,
    app_name: str = APP_NAME,
    bundle_id: str | None = None,
    icon_file: str = "AppIcon",
) -> None:
    payload = read_plist(plist_path)
    payload["CFBundleName"] = app_name
    payload["CFBundleDisplayName"] = app_name
    payload["CFBundleIconFile"] = icon_file
    if bundle_id:
        payload["CFBundleIdentifier"] = bundle_id
    if "NSHumanReadableCopyright" in payload:
        payload["NSHumanReadableCopyright"] = "Copyright Violet Ballard"
    write_plist(plist_path, payload)


def copy_wezterm_runtime(app_bundle: Path, wezterm_app: Path = WEZTERM_VENDOR_APP) -> Path:
    if not wezterm_app.is_dir():
        raise SystemExit(f"Pinned WezTerm runtime is missing: {wezterm_app}")
    resources = app_bundle / "Contents" / "Resources"
    resources.mkdir(parents=True, exist_ok=True)
    destination = resources / "WezTerm.app"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(wezterm_app, destination, symlinks=True)
    repair_wezterm_permissions(destination)
    return destination


def repair_wezterm_permissions(wezterm_app: Path) -> None:
    macos_dir = wezterm_app / "Contents" / "MacOS"
    for executable in WEZTERM_EXECUTABLES:
        path = macos_dir / executable
        if path.exists():
            path.chmod(path.stat().st_mode | 0o755)


def copy_icon_resources(app_bundle: Path, icon_source: Path = ICON_SOURCE) -> None:
    if not icon_source.is_file():
        raise SystemExit(f"Generated app icon is missing: {icon_source}")
    resources = app_bundle / "Contents" / "Resources"
    resources.mkdir(parents=True, exist_ok=True)
    shutil.copy2(icon_source, resources / "AppIcon.icns")
    nested_resources = app_bundle / "Contents" / "Resources" / "WezTerm.app" / "Contents" / "Resources"
    if nested_resources.is_dir():
        shutil.copy2(icon_source, nested_resources / "AppIcon.icns")


def patch_app_bundle(app_bundle: Path) -> None:
    top_plist = app_bundle / "Contents" / "Info.plist"
    if not top_plist.is_file():
        raise SystemExit(f"Not an app bundle: {app_bundle}")
    patch_info_plist(top_plist, bundle_id=BUNDLE_ID)
    nested_plist = app_bundle / "Contents" / "Resources" / "WezTerm.app" / "Contents" / "Info.plist"
    if nested_plist.is_file():
        patch_info_plist(nested_plist, bundle_id=f"{BUNDLE_ID}.terminal")


def assert_no_visible_wezterm_identity(app_bundle: Path) -> None:
    offenders: list[str] = []
    for plist_path in app_bundle.glob("Contents/**/Info.plist"):
        try:
            payload = read_plist(plist_path)
        except Exception:
            continue
        for key in VISIBLE_PLIST_KEYS:
            value = payload.get(key)
            if isinstance(value, str) and "wezterm" in value.casefold():
                offenders.append(f"{plist_path.relative_to(app_bundle)}:{key}={value}")
    if offenders:
        joined = "\n".join(offenders)
        raise SystemExit(f"Visible WezTerm identity remains in packaged app:\n{joined}")


def find_app_bundle() -> Path:
    candidates = sorted(ROOT.glob("build/**/Exegesis.app"))
    if not candidates:
        raise SystemExit("Could not find build/**/Exegesis.app after Briefcase build.")
    return candidates[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch packaged macOS app identity to Exegesis.")
    parser.add_argument("app_bundle", nargs="?", type=Path, help="Path to Exegesis.app; defaults to build/**/Exegesis.app")
    parser.add_argument("--copy-wezterm", action="store_true", help="Copy pinned WezTerm.app into Contents/Resources first.")
    args = parser.parse_args()
    app_bundle = (args.app_bundle or find_app_bundle()).resolve()
    if args.copy_wezterm:
        copy_wezterm_runtime(app_bundle)
    copy_icon_resources(app_bundle)
    patch_app_bundle(app_bundle)
    assert_no_visible_wezterm_identity(app_bundle)
    print(app_bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
