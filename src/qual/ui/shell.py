from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Set
from typing import Any
import unicodedata

from src.qual.engine.service import EngineRuntime
from .a2ui import (
    ActionRef,
    SelectionRef,
    normalize_action_ref,
    normalize_selection_ref,
    resolve_terminal_artifact_render_target,
    _is_malformed_terminal_artifact_envelope,
    _infer_terminal_artifact_explicit_kind,
    _recover_terminal_artifact_leaf_kind,
    render_terminal_action,
    render_terminal_artifact,
    render_terminal_card,
    render_terminal_selection,
    _render_invalid_terminal_action,
    _render_invalid_terminal_card,
    _render_invalid_terminal_selection,
)


class ShellUI:
    """Minimal CLI shell used to verify bootstrap wiring."""

    def render_artifact(self, artifact: Any, *, kind: str | None = None) -> str:
        try:
            return render_terminal_artifact(artifact, kind=kind)
        except Exception:
            # Keep the CLI usable even if the structured artifact renderer fails unexpectedly.
            if self._normalize_fallback_kind(kind) == "card" and _is_malformed_terminal_artifact_envelope(artifact):
                payload = artifact.get("artifact") if isinstance(artifact, Mapping) else None
                payload_kind = _infer_terminal_artifact_explicit_kind(payload)
                if payload_kind not in {"action", "selection"}:
                    payload_kind = _recover_terminal_artifact_leaf_kind(payload)
                if payload_kind in {"action", "selection"}:
                    return _render_invalid_terminal_card(artifact)
            try:
                fallback_artifact, fallback_kind = self._resolve_fallback_artifact(artifact, kind=kind)
            except Exception:
                fallback_artifact = artifact
                fallback_kind = self._normalize_fallback_kind(kind)
                if fallback_kind is None:
                    fallback_kind = self._infer_fallback_kind(artifact)
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
                return _render_invalid_terminal_card(fallback_artifact)

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
    def _infer_fallback_kind(artifact: Any) -> str | None:
        if isinstance(artifact, ActionRef):
            return "action"
        if isinstance(artifact, SelectionRef):
            return "selection"
        if not isinstance(artifact, Mapping):
            return None

        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str):
            normalized_type = artifact_type.strip()
            if normalized_type == "ActionRef":
                return "action"
            if normalized_type == "SelectionRef":
                return "selection"
            if normalized_type and normalized_type != "TerminalArtifact":
                # Any other typed mapping should still render as a card even if
                # the surrounding envelope metadata is broken.
                return "card"

        if (not isinstance(artifact_type, str) or not artifact_type.strip()) and any(
            field in artifact for field in ("blocks", "actions")
        ):
            # Untyped card-shaped payloads should stay on the card path even if
            # they carry stray action/selection-style fields.
            return "card"

        has_required_fields = all(field in artifact for field in ("id", "label", "payload"))
        if not has_required_fields:
            return None

        has_action_hints = any(field in artifact for field in ("confirm", "policy_sensitive"))
        has_selection_hints = any(field in artifact for field in ("selected", "disabled"))
        if has_action_hints and not has_selection_hints:
            return "action"
        if has_selection_hints and not has_action_hints:
            return "selection"

        # Last-resort schema validation keeps raw leaf payloads recoverable if
        # the broader envelope resolver fails unexpectedly.
        inferred_action_kind = ShellUI._infer_action_payload_kind(artifact)
        if inferred_action_kind is not None:
            return inferred_action_kind
        inferred_selection_kind = ShellUI._infer_selection_payload_kind(artifact)
        if inferred_selection_kind is not None:
            return inferred_selection_kind
        inferred_partial_leaf_kind = ShellUI._infer_partial_leaf_fallback_kind(artifact)
        if inferred_partial_leaf_kind is not None:
            return inferred_partial_leaf_kind
        return None

    @staticmethod
    def _infer_action_payload_kind(artifact: Any) -> str | None:
        if not isinstance(artifact, Mapping):
            return None
        try:
            normalize_action_ref(artifact)
        except ValueError:
            return None
        return "action"

    @staticmethod
    def _infer_selection_payload_kind(artifact: Any) -> str | None:
        if not isinstance(artifact, Mapping):
            return None
        try:
            normalize_selection_ref(artifact)
        except ValueError:
            return None
        return "selection"

    @staticmethod
    def _infer_partial_leaf_fallback_kind(artifact: Any) -> str | None:
        if not isinstance(artifact, Mapping):
            return None

        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str):
            normalized_type = artifact_type.strip()
            if normalized_type == "ActionRef":
                return "action"
            if normalized_type == "SelectionRef":
                return "selection"
            if normalized_type and normalized_type != "TerminalArtifact":
                return None

        if any(field in artifact for field in ("blocks", "actions")):
            return None
        if not all(field in artifact for field in ("id", "payload")):
            return None

        has_action_hints = any(field in artifact for field in ("confirm", "policy_sensitive"))
        has_selection_hints = any(field in artifact for field in ("selected", "disabled"))
        if has_action_hints and not has_selection_hints:
            return "action"
        if has_selection_hints and not has_action_hints:
            return "selection"
        return None

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
        if normalized_kind in {"card", "action", "selection"}:
            return normalized_kind
        return None

    @staticmethod
    def _resolve_fallback_artifact(
        artifact: Any,
        *,
        kind: str | None,
    ) -> tuple[Any, str | None]:
        fallback_kind = ShellUI._normalize_fallback_kind(kind)
        try:
            fallback_artifact, resolved_kind = resolve_terminal_artifact_render_target(
                artifact,
                requested_kind=fallback_kind,
                allow_invalid_envelope_recovery=True,
            )
            if fallback_kind is None and resolved_kind == "card":
                # Prefer full schema recovery first, then recover partial leaf
                # hints so leaf payloads do not get trapped in the card path.
                inferred_kind = ShellUI._infer_fallback_kind(fallback_artifact)
                if inferred_kind is None:
                    inferred_kind = ShellUI._infer_partial_leaf_fallback_kind(fallback_artifact)
                if inferred_kind is not None:
                    return fallback_artifact, inferred_kind
            return fallback_artifact, resolved_kind
        except Exception:
            inferred_kind = ShellUI._infer_fallback_kind(artifact)
            if inferred_kind is not None:
                return artifact, inferred_kind
            return artifact, fallback_kind
