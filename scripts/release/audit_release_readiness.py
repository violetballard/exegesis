#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE_VERSION = "0.1.0.dev2"
APP_ZIP_NAME = f"Exegesis-{RELEASE_VERSION}-macos-arm64-developer-preview.app.zip"


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _extract_assigned_version(text: str, variable_name: str) -> str | None:
    pattern = rf'^{re.escape(variable_name)}\s*=\s*"([^"]+)"'
    match = re.search(pattern, text, flags=re.MULTILINE)
    return match.group(1) if match else None


def _check(condition: bool, failures: list[str], message: str) -> None:
    if not condition:
        failures.append(message)


def _check_text_contains(text: str, failures: list[str], needle: str, path: str) -> None:
    _check(needle in text, failures, f"{path} must contain: {needle}")


def _check_text_absent(text: str, failures: list[str], needle: str, path: str) -> None:
    _check(needle not in text, failures, f"{path} still contains stale text: {needle}")


def _audit_versions(failures: list[str]) -> None:
    pyproject = _read("pyproject.toml")
    build_script = _read("scripts/release/build_macos_developer_preview.sh")
    manifest = json.loads(_read("client-textual/src/exegesis_textual/workflow/prompts/writer_system_prompt.manifest.json"))

    _check(_extract_assigned_version(pyproject, "version") == RELEASE_VERSION, failures, "pyproject.toml version must match release version.")
    _check(f'VERSION="{RELEASE_VERSION}"' in build_script, failures, "build_macos_developer_preview.sh VERSION must match release version.")
    _check(manifest.get("version") == RELEASE_VERSION, failures, "writer system prompt manifest version must match release version.")


def _audit_public_docs(failures: list[str]) -> None:
    readme_path = "packaging/public/README.md"
    notes_path = "packaging/public/RELEASE_NOTES.md"
    readme = _read(readme_path)
    notes = _read(notes_path)

    for path, text in ((readme_path, readme), (notes_path, notes)):
        _check_text_absent(text, failures, "0.1.0.dev1", path)

    _check_text_contains(readme, failures, APP_ZIP_NAME, readme_path)
    _check_text_contains(readme, failures, "local OpenAI-compatible endpoints", readme_path)
    _check_text_contains(readme, failures, "Project-level local confidential mode", readme_path)
    _check_text_contains(readme, failures, "App action registry support", readme_path)
    _check_text_contains(readme, failures, "local_openai", readme_path)

    _check_text_absent(readme, failures, "Custom OpenAI-compatible endpoints and local confidential projects are planned follow-ups.", readme_path)
    _check_text_absent(readme, failures, "Only Mistral is supported", readme_path)
    _check_text_absent(readme, failures, "Mistral-backed model actions", readme_path)

    _check_text_contains(notes, failures, f"# Exegesis {RELEASE_VERSION} Release Notes", notes_path)
    _check_text_contains(notes, failures, "local OpenAI-compatible endpoints", notes_path)
    _check_text_contains(notes, failures, "Local confidential project mode", notes_path)
    _check_text_contains(notes, failures, "App action registry support", notes_path)
    _check_text_absent(notes, failures, "Custom OpenAI-compatible endpoints and local confidential projects are not included yet.", notes_path)


def _audit_public_source_manifest(failures: list[str]) -> None:
    manifest_path = ROOT / "packaging" / "release" / "public_source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    include_paths = set(str(path) for path in manifest.get("include_paths", []))
    deny_fragments = set(str(path) for path in manifest.get("deny_fragments", []))

    for required in (
        "client-textual/src",
        "client-textual/tests",
        "engine/src",
        "shared/src",
        "scripts/release",
        "packaging/public/README.md",
        "packaging/public/RELEASE_NOTES.md",
    ):
        _check(required in include_paths, failures, f"public source manifest must include {required}.")

    for forbidden in (".codex", ".agents", "packet_garden", "milestone", "logs", "cache"):
        _check(forbidden in deny_fragments, failures, f"public source manifest must deny {forbidden}.")

    result = subprocess.run(
        [sys.executable, "scripts/release/verify_public_source.py", "--manifest-only"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode:
        failures.append("public source manifest validation failed:\n" + result.stdout.strip())


def _audit_secret_markers(failures: list[str]) -> None:
    public_text = "\n".join(
        _read(path)
        for path in (
            "packaging/public/README.md",
            "packaging/public/RELEASE_NOTES.md",
            "client-textual/src/exegesis_textual/workflow/prompts/writer_system_prompt.manifest.json",
        )
    )
    suspicious_patterns = (
        r"sk-[A-Za-z0-9_-]{20,}",
        r"xai-[A-Za-z0-9_-]{20,}",
        r"AIza[A-Za-z0-9_-]{20,}",
        r"mistral_[A-Za-z0-9_-]{20,}",
    )
    for pattern in suspicious_patterns:
        _check(re.search(pattern, public_text) is None, failures, f"public release text appears to contain a secret matching {pattern}.")


def audit_release_readiness() -> None:
    failures: list[str] = []
    _audit_versions(failures)
    _audit_public_docs(failures)
    _audit_public_source_manifest(failures)
    _audit_secret_markers(failures)
    if failures:
        raise SystemExit("Release readiness audit failed:\n- " + "\n- ".join(failures))


def main() -> int:
    audit_release_readiness()
    print("release readiness audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
