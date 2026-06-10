from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path


class PromptIntegrityError(RuntimeError):
    """Raised when a packaged prompt fails identity or integrity checks."""


@dataclass(frozen=True)
class PromptIdentity:
    prompt_id: str
    version: str
    sha256: str
    path: str

    def diagnostic_label(self) -> str:
        return f"{self.prompt_id}@{self.version} ({self.sha256[:12]})"


def prompt_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_prompt_manifest(manifest_path: Path) -> PromptIdentity:
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PromptIntegrityError("Packaged system prompt manifest is missing.") from exc
    except json.JSONDecodeError as exc:
        raise PromptIntegrityError("Packaged system prompt manifest is invalid.") from exc

    prompt_id = raw.get("prompt_id")
    version = raw.get("version")
    sha256 = raw.get("sha256")
    prompt_path = raw.get("path")
    if not all(isinstance(value, str) and value for value in (prompt_id, version, sha256, prompt_path)):
        raise PromptIntegrityError("Packaged system prompt manifest is incomplete.")
    return PromptIdentity(prompt_id=prompt_id, version=version, sha256=sha256, path=prompt_path)


def load_verified_prompt(prompt_path: Path, manifest_path: Path, *, require_manifest: bool = True) -> tuple[str, PromptIdentity | None]:
    try:
        prompt = prompt_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise PromptIntegrityError("Packaged system prompt is unavailable.") from exc
    if not prompt:
        raise PromptIntegrityError("Packaged system prompt is empty.")

    try:
        identity = load_prompt_manifest(manifest_path)
    except PromptIntegrityError:
        if require_manifest:
            raise
        return prompt, None

    if Path(identity.path).name != prompt_path.name:
        raise PromptIntegrityError("Packaged system prompt manifest points at the wrong prompt file.")
    actual_hash = prompt_sha256(prompt_path)
    if actual_hash != identity.sha256:
        raise PromptIntegrityError(
            f"Packaged system prompt hash mismatch for {identity.prompt_id}@{identity.version}."
        )
    return prompt, identity


__all__ = [
    "PromptIdentity",
    "PromptIntegrityError",
    "load_prompt_manifest",
    "load_verified_prompt",
    "prompt_sha256",
]
