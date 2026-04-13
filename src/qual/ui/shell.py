from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Set
from typing import Any
import unicodedata

from src.qual.engine.service import EngineRuntime
from .a2ui import (
    render_terminal_action,
    render_terminal_artifact,
    render_terminal_card,
    render_terminal_selection,
    _render_invalid_terminal_action,
    _render_invalid_terminal_card,
    _render_invalid_terminal_selection,
    validate_terminal_artifact_envelope,
)


class ShellUI:
    """Minimal CLI shell used to verify bootstrap wiring."""

    def render_artifact(self, artifact: Any, *, kind: str | None = None) -> str:
        try:
            return render_terminal_artifact(artifact, kind=kind)
        except Exception:
            # Keep the CLI usable even if the structured artifact renderer fails unexpectedly.
            fallback_artifact, fallback_kind = self._resolve_fallback_artifact(artifact, kind=kind)
            if fallback_kind == "action":
                try:
                    return render_terminal_action(fallback_artifact)
                except Exception:
                    return _render_invalid_terminal_action(fallback_artifact)
            if fallback_kind == "selection":
                try:
                    return render_terminal_selection(fallback_artifact)
                except Exception:
                    return _render_invalid_terminal_selection(fallback_artifact)
            try:
                return render_terminal_card(fallback_artifact)
            except Exception:
                return _render_invalid_terminal_card()

    def render_startup(self, runtime: EngineRuntime) -> str:
        item_ids = self._snapshot_item_ids(runtime.basket.item_ids)
        if item_ids:
            preview_items = [self._format_item_id(value) for value in item_ids[:3]]
            preview = ", ".join(preview_items)
            if len(item_ids) > 3:
                remaining = len(item_ids) - 3
                label = "item" if remaining == 1 else "items"
                preview = f"{preview}, +{remaining} more {label}"
        else:
            preview = "<empty>"
        return (
            "Qual Workstation bootstrap is running\n"
            f"- project: {runtime.vault.project_name}\n"
            f"- vault: {runtime.vault.root_dir}\n"
            f"- locked: {runtime.vault.is_locked}\n"
            f"- context_items: {len(item_ids)}\n"
            f"- context_preview: {preview}"
        )

    @staticmethod
    def _snapshot_item_ids(item_ids: object) -> list[object]:
        if item_ids is None:
            return []
        if isinstance(item_ids, (str, bytes)):
            return [item_ids]
        if isinstance(item_ids, Mapping):
            return [item_ids]
        if isinstance(item_ids, Set):
            return sorted(item_ids, key=ShellUI._snapshot_item_sort_key)
        if isinstance(item_ids, Iterable):
            return list(item_ids)
        return [item_ids]

    @staticmethod
    def _snapshot_item_sort_key(value: object) -> tuple[str, str]:
        # Use the full normalized value so distinct items do not collapse
        # when their truncated preview strings happen to match.
        baseline = " ".join(str(value).split())
        escaped = ShellUI._escape_control_chars(baseline)
        if not isinstance(value, str) and ShellUI._looks_like_opaque_object_repr(escaped):
            return (type(value).__name__, ShellUI._format_item_id(value))
        return (type(value).__name__, escaped)

    @staticmethod
    def _format_item_id(value: object) -> str:
        if value is None:
            return "<blank>"
        is_string = isinstance(value, str)
        baseline = " ".join(str(value).split())
        if not baseline:
            return "<blank>"
        escaped = ShellUI._escape_control_chars(baseline)
        if not is_string and ShellUI._looks_like_opaque_object_repr(escaped):
            return f"<non-json:{type(value).__name__}>"
        rendered = ShellUI._truncate_for_preview(escaped, max_len=24)
        if is_string and not ShellUI._is_safe_preview_token(rendered):
            return json.dumps(rendered, ensure_ascii=False)
        if not is_string and ("," in rendered or '"' in rendered or "\\" in rendered):
            escaped = rendered.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return rendered

    @staticmethod
    def _escape_control_chars(value: str) -> str:
        parts: list[str] = []
        for char in value:
            code = ord(char)
            if code < 32 or code == 127:
                parts.append(f"\\x{code:02x}")
            elif unicodedata.category(char).startswith("C"):
                if code <= 0xFFFF:
                    parts.append(f"\\u{code:04x}")
                else:
                    parts.append(f"\\U{code:08x}")
            else:
                parts.append(char)
        return "".join(parts)

    @staticmethod
    def _truncate_for_preview(value: str, *, max_len: int) -> str:
        if len(value) <= max_len:
            return value

        prefix = value[: max_len - 3]
        while prefix:
            if prefix.endswith("\\"):
                prefix = prefix[:-1]
                continue
            escape_start = prefix.rfind("\\")
            if escape_start != -1 and escape_start < len(prefix) - 1:
                escape_type = prefix[escape_start + 1]
                escape_length = {
                    "x": 4,
                    "u": 6,
                    "U": 10,
                }.get(escape_type)
                if escape_length is not None and len(prefix) - escape_start < escape_length:
                    prefix = prefix[:escape_start]
                    continue
            break
        return f"{prefix}..."

    @staticmethod
    def _is_safe_preview_token(value: str) -> bool:
        if not value:
            return False
        return all(char.isalnum() or char in {".", "_", "-"} for char in value)

    @staticmethod
    def _looks_like_opaque_object_repr(value: str) -> bool:
        return value.startswith("<") and value.endswith(">") and " object at 0x" in value

    @staticmethod
    def _normalize_fallback_kind(kind: str | None) -> str | None:
        if not isinstance(kind, str):
            return None
        normalized_kind = kind.strip().lower()
        if normalized_kind in {"action", "selection"}:
            return normalized_kind
        return None

    @staticmethod
    def _resolve_fallback_artifact(artifact: Any, *, kind: str | None) -> tuple[Any, str | None]:
        fallback_kind = ShellUI._normalize_fallback_kind(kind)
        if not isinstance(artifact, Mapping):
            return artifact, fallback_kind

        artifact_type = artifact.get("type")
        if not isinstance(artifact_type, str) or artifact_type.strip() != "TerminalArtifact":
            return artifact, fallback_kind

        try:
            validate_terminal_artifact_envelope(artifact)
        except Exception:
            return artifact, fallback_kind

        payload = artifact.get("artifact")
        if fallback_kind is None:
            fallback_kind = ShellUI._normalize_fallback_kind(artifact.get("kind"))
        return payload, fallback_kind
