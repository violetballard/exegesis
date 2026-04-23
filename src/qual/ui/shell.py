from __future__ import annotations

import copy
import json
from functools import lru_cache
from itertools import count
from collections.abc import Iterable, Mapping, Set
from typing import Any
import unicodedata
from weakref import WeakKeyDictionary

from src.qual.engine.service import EngineRuntime
from .a2ui import (
    ActionRef,
    A2UI_CONTRACT_VERSION,
    A2UI_VERSION,
    SelectionRef,
    _add_contract_alias_fingerprints,
    normalize_action_ref,
    normalize_selection_ref,
    describe_terminal_artifact_cli_fallback_contract,
    describe_terminal_artifact_cli_fallback_entrypoint_contract,
    describe_terminal_artifact_cli_fallback_target_contract,
    describe_terminal_artifact_cli_fallback_route_contract,
    describe_terminal_artifact_renderer_entrypoints_contract,
    terminal_artifact_cli_fallback_contract_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint,
    terminal_artifact_cli_fallback_target_contract_fingerprint,
    terminal_artifact_cli_fallback_route_contract_fingerprint,
    terminal_artifact_renderer_entrypoints_contract_fingerprint,
    _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT,
    _fingerprint_manifest_section,
    _is_explicit_terminal_artifact_leaf,
    _normalize_terminal_artifact_kind_hint,
    _should_preserve_raw_leaf_card_default,
    refine_terminal_artifact_cli_fallback_target,
    resolve_terminal_artifact_cli_fallback_target,
    render_terminal_action,
    render_terminal_artifact,
    render_terminal_cli_fallback,
    render_terminal_card,
    render_terminal_selection,
    _render_invalid_terminal_action,
    _render_invalid_terminal_card,
    _render_invalid_terminal_selection,
    _is_malformed_terminal_artifact_envelope,
    _infer_terminal_artifact_kind_from_mapping,
    _normalize_terminal_artifact_envelope_kind,
    _infer_terminal_artifact_explicit_kind,
    _recover_terminal_artifact_leaf_kind,
)

SHELL_UI_CONTRACT_VERSION = 1
SHELL_UI_STARTUP_FIELDS: tuple[str, ...] = (
    "project",
    "vault",
    "locked",
    "context_items",
    "context_preview",
)
SHELL_UI_ENTRYPOINTS: tuple[tuple[str, str], ...] = (
    ("render_artifact", "ShellUI.render_artifact"),
    ("render_cli_fallback", "ShellUI.render_cli_fallback"),
    ("render_startup", "ShellUI.render_startup"),
)
SHELL_UI_STARTUP_PREVIEW_LIMIT = 3
SHELL_UI_STARTUP_EMPTY_PREVIEW = "<empty>"
_OPAQUE_OBJECT_SORT_TIEBREAKERS: WeakKeyDictionary[object, int] = WeakKeyDictionary()
_OPAQUE_OBJECT_SORT_TIEBREAKER_COUNTER = count()


def _build_shell_ui_entrypoints() -> dict[str, str]:
    return {entrypoint: renderer for entrypoint, renderer in SHELL_UI_ENTRYPOINTS}


class ShellUI:
    """Minimal CLI shell used to verify bootstrap wiring."""

    def render_artifact(self, artifact: Any, *, kind: str | None = None) -> str:
        normalized_kind = self._normalize_fallback_kind(kind)
        if normalized_kind == "card" and isinstance(artifact, Mapping) and _is_malformed_terminal_artifact_envelope(artifact):
            payload = artifact.get("artifact")
            envelope_kind = _normalize_terminal_artifact_envelope_kind(artifact.get("kind"))
            if _should_preserve_raw_leaf_card_default(payload):
                if envelope_kind == "card":
                    return _render_invalid_terminal_card(artifact)
            else:
                payload_kind = _infer_terminal_artifact_explicit_kind(payload)
                if payload_kind not in {"action", "selection"}:
                    payload_kind = _recover_terminal_artifact_leaf_kind(payload)
                if payload_kind in {"action", "selection"}:
                    return _render_invalid_terminal_card(artifact)
        resolved_fallback: tuple[Any, str | None] | None = None
        if normalized_kind == "card":
            try:
                resolved_fallback = self._resolve_fallback_artifact(artifact, kind=kind)
            except Exception:
                resolved_fallback = None
            else:
                if (
                    resolved_fallback[1] in {"action", "selection"}
                    and not _should_preserve_raw_leaf_card_default(artifact)
                    and not _is_explicit_terminal_artifact_leaf(artifact)
                ):
                    return _render_invalid_terminal_card(artifact)
        fallback_artifact: Any = artifact
        fallback_kind: str | None = None
        if normalized_kind is None and _should_preserve_raw_leaf_card_default(artifact):
            # Raw leaves should stay on the card path when no valid leaf
            # hint was provided, but still flow through the explicit CLI
            # fallback entrypoint.
            fallback_kind = "card"
        elif resolved_fallback is not None:
            fallback_artifact, fallback_kind = resolved_fallback
        elif normalized_kind == "card":
            fallback_kind = "card"
        else:
            try:
                fallback_artifact, fallback_kind = self._resolve_fallback_artifact(
                    artifact,
                    kind=kind,
                )
            except Exception:
                fallback_artifact = artifact
                fallback_kind = normalized_kind
                if fallback_kind is None:
                    fallback_kind = self._infer_fallback_kind(artifact)
        if (
            kind is None
            and fallback_kind in {"action", "selection"}
            and _should_preserve_raw_leaf_card_default(artifact)
        ):
            fallback_artifact = artifact
            fallback_kind = "card"
        fallback_hint_token = _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.set(
            (fallback_artifact, fallback_kind),
        )
        try:
            return self._render_cli_fallback_with_recovery(fallback_artifact, fallback_kind)
        finally:
            if fallback_hint_token is not None:
                _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.reset(fallback_hint_token)

    def render_cli_fallback(self, artifact: Any, *, kind: str | None = None) -> str:
        """Render an A2UI artifact through the explicit CLI fallback entrypoint."""
        normalized_kind = self._normalize_fallback_kind(kind)
        if normalized_kind == "card":
            fallback_hint_token = _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.set((artifact, "card"))
            try:
                return self._render_cli_fallback_with_recovery(artifact, "card")
            finally:
                _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.reset(fallback_hint_token)
        fallback_hint_token = None
        try:
            fallback_target = resolve_terminal_artifact_cli_fallback_target(artifact, kind=kind)
        except Exception:
            fallback_target = None
        else:
            fallback_hint_token = _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.set(fallback_target)
        try:
            if fallback_target is not None:
                fallback_artifact, fallback_kind = fallback_target
                return self._render_cli_fallback_with_recovery(fallback_artifact, fallback_kind)
            return self._render_cli_fallback_with_recovery(artifact, kind)
        finally:
            if fallback_hint_token is not None:
                _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.reset(fallback_hint_token)

    def _render_cli_fallback_with_recovery(self, artifact: Any, kind: str | None) -> str:
        """Render through the shared CLI fallback path and recover on failure.

        The explicit CLI fallback entrypoint should stay usable even if the
        shared fallback renderer raises or returns an unexpected leaf shape.
        """

        leaf_specific_fallback = kind in {"action", "selection"}
        try:
            rendered_cli_fallback = render_terminal_cli_fallback(artifact, kind=kind)
        except Exception:
            rendered_cli_fallback = None
        else:
            if not leaf_specific_fallback or self._has_expected_leaf_renderer_prefix(
                rendered_cli_fallback,
                kind,
            ):
                return rendered_cli_fallback
        if kind == "action":
            try:
                return render_terminal_action(artifact)
            except Exception:
                return _render_invalid_terminal_action(artifact)
        if kind == "selection":
            try:
                return render_terminal_selection(artifact)
            except Exception:
                return _render_invalid_terminal_selection(artifact)
        if kind not in {"action", "selection"}:
            try:
                # Retry the shared renderer on the resolved fallback target so
                # we do not reprocess the original envelope after CLI fallback
                # resolution has already recovered a safer payload.
                return render_terminal_artifact(artifact, kind=kind)
            except Exception:
                pass
        try:
            return render_terminal_card(artifact)
        except Exception:
            return _render_invalid_terminal_card(artifact)

    def render_startup(self, runtime: EngineRuntime) -> str:
        item_ids = self._snapshot_item_ids(runtime.basket.item_ids)
        if item_ids:
            preview_items = [
                self._format_item_id(value) for value in item_ids[:SHELL_UI_STARTUP_PREVIEW_LIMIT]
            ]
            preview = ", ".join(preview_items)
            if len(item_ids) > SHELL_UI_STARTUP_PREVIEW_LIMIT:
                remaining = len(item_ids) - SHELL_UI_STARTUP_PREVIEW_LIMIT
                label = "item" if remaining == 1 else "items"
                preview = f"{preview}, +{remaining} more {label}"
        else:
            preview = SHELL_UI_STARTUP_EMPTY_PREVIEW
        return (
            "Qual Workstation bootstrap is running\n"
            f"- project: {self._render_startup_value(runtime.vault.project_name)}\n"
            f"- vault: {self._render_startup_value(runtime.vault.root_dir)}\n"
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
    def _snapshot_item_sort_key(value: object) -> tuple[str, str, str]:
        # Use the full normalized value so distinct items do not collapse
        # when their truncated preview strings happen to match. Opaque object
        # reprs reuse a redacted preview token, so keep a stable per-object
        # tiebreaker for deterministic set ordering.
        baseline = " ".join(str(value).split())
        escaped = ShellUI._escape_control_chars(baseline)
        if not isinstance(value, str) and ShellUI._looks_like_opaque_object_repr(escaped):
            return (
                type(value).__name__,
                ShellUI._format_item_id(value),
                ShellUI._opaque_object_sort_tiebreaker(value),
            )
        return (type(value).__name__, escaped, "")

    @staticmethod
    def _render_startup_value(value: object) -> str:
        if value is None:
            return "<blank>"
        rendered = ShellUI._escape_control_chars(str(value)).strip()
        if not rendered:
            return "<blank>"
        return rendered

    @staticmethod
    def _infer_fallback_kind(artifact: Any) -> str | None:
        if isinstance(artifact, ActionRef):
            return "action"
        if isinstance(artifact, SelectionRef):
            return "selection"
        if not isinstance(artifact, Mapping):
            return None

        if _should_preserve_raw_leaf_card_default(artifact):
            # Preserve the raw leaf card-default contract before schema-level
            # leaf inference can reinterpret the same payload as action or selection.
            return "card"

        # Keep the shell fallback classifier in lockstep with the shared
        # A2UI mapping classifier so card/action/selection detection stays
        # consistent between direct rendering and fallback recovery.
        shared_kind = _infer_terminal_artifact_kind_from_mapping(artifact)
        if shared_kind is not None:
            return shared_kind

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
    def _contains_action_or_selection_payload(
        artifact: Any,
        *,
        _seen_envelope_ids: set[int] | None = None,
    ) -> bool:
        if isinstance(artifact, (ActionRef, SelectionRef)):
            return True
        if not isinstance(artifact, Mapping):
            return False

        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str) and artifact_type.strip() == "TerminalArtifact":
            if _seen_envelope_ids is None:
                _seen_envelope_ids = set()
            artifact_id = id(artifact)
            if artifact_id in _seen_envelope_ids:
                return False
            _seen_envelope_ids.add(artifact_id)
            payload = artifact.get("artifact")
            if payload is None:
                return False
            return ShellUI._contains_action_or_selection_payload(
                payload,
                _seen_envelope_ids=_seen_envelope_ids,
            )

        if ShellUI._infer_action_payload_kind(artifact) is not None:
            return True
        if ShellUI._infer_selection_payload_kind(artifact) is not None:
            return True
        return ShellUI._infer_partial_leaf_fallback_kind(artifact) is not None

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
    def _opaque_object_sort_tiebreaker(value: object) -> str:
        try:
            token = _OPAQUE_OBJECT_SORT_TIEBREAKERS.get(value)
        except TypeError:
            return f"{type(value).__name__}:{id(value)}"
        if token is None:
            token = next(_OPAQUE_OBJECT_SORT_TIEBREAKER_COUNTER)
            try:
                _OPAQUE_OBJECT_SORT_TIEBREAKERS[value] = token
            except TypeError:
                return f"{type(value).__name__}:{id(value)}"
        return str(token)

    @staticmethod
    def _normalize_fallback_kind(kind: Any) -> str | None:
        return _normalize_terminal_artifact_kind_hint(kind)

    @staticmethod
    def _has_expected_leaf_renderer_prefix(rendered: Any, fallback_kind: str) -> bool:
        if not isinstance(rendered, str):
            return False
        if fallback_kind == "action":
            return rendered.startswith("[ActionRef]")
        if fallback_kind == "selection":
            return rendered.startswith("[SelectionRef]")
        return False

    @staticmethod
    def _resolve_fallback_artifact(
        artifact: Any,
        *,
        kind: str | None,
    ) -> tuple[Any, str | None]:
        requested_kind = ShellUI._normalize_fallback_kind(kind)
        try:
            fallback_artifact, fallback_kind = resolve_terminal_artifact_cli_fallback_target(artifact, kind=kind)
            fallback_artifact, fallback_kind = refine_terminal_artifact_cli_fallback_target(
                fallback_artifact,
                fallback_kind,
                requested_kind=requested_kind,
            )
            return fallback_artifact, fallback_kind
        except Exception:
            recovered = ShellUI._recover_terminal_artifact_envelope_fallback(artifact)
            if recovered is not None:
                return refine_terminal_artifact_cli_fallback_target(
                    recovered[0],
                    recovered[1],
                    requested_kind=requested_kind,
                )
            if _should_preserve_raw_leaf_card_default(artifact):
                return artifact, "card"
            inferred_kind = ShellUI._infer_fallback_kind(artifact)
            if inferred_kind is not None:
                return refine_terminal_artifact_cli_fallback_target(
                    artifact,
                    inferred_kind,
                    requested_kind=requested_kind,
                )
            # Keep the shell fallback path deterministic: if we could not
            # recover a specific kind, fall back to the default card view.
            return artifact, requested_kind or "card"

    @staticmethod
    def _recover_terminal_artifact_envelope_fallback(
        artifact: Any,
        *,
        _seen_envelope_ids: set[int] | None = None,
    ) -> tuple[Any, str] | None:
        if not isinstance(artifact, Mapping):
            return None
        artifact_type = artifact.get("type")
        if not isinstance(artifact_type, str) or artifact_type.strip() != "TerminalArtifact":
            return None

        if _seen_envelope_ids is None:
            _seen_envelope_ids = set()
        artifact_id = id(artifact)
        if artifact_id in _seen_envelope_ids:
            return None
        _seen_envelope_ids.add(artifact_id)

        payload = artifact.get("artifact")
        if payload is None:
            return None

        envelope_kind = ShellUI._normalize_fallback_kind(artifact.get("kind"))
        if isinstance(payload, Mapping):
            nested_type = payload.get("type")
            if isinstance(nested_type, str) and nested_type.strip() == "TerminalArtifact":
                # Keep peeling nested envelopes until we reach the concrete
                # leaf payload. Nested structured artifacts should never be
                # flattened back to the raw-leaf card default just because
                # an intermediate wrapper happened to use kind="card".
                recovered = ShellUI._recover_terminal_artifact_envelope_fallback(
                    payload,
                    _seen_envelope_ids=_seen_envelope_ids,
                )
                if recovered is not None:
                    return recovered

        if envelope_kind in {"action", "selection"}:
            return payload, envelope_kind

        if envelope_kind is None and _should_preserve_raw_leaf_card_default(payload):
            # When the envelope kind is unusable, keep ambiguous raw leaves on
            # the card path rather than guessing a structured leaf kind.
            return payload, "card"

        inferred_kind = ShellUI._infer_fallback_kind(payload)
        if inferred_kind is not None:
            return payload, inferred_kind

        return None


@lru_cache(maxsize=None)
def _build_shell_ui_contract_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    terminal_artifact_cli_fallback_route_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_route_contract_fingerprint()
    )
    terminal_artifact_cli_fallback_entrypoint = "render_terminal_cli_fallback"
    terminal_artifact_cli_fallback_entrypoint_contract_manifest = (
        describe_terminal_artifact_cli_fallback_entrypoint_contract()
    )
    terminal_artifact_cli_fallback_target_contract = copy.deepcopy(
        describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    )
    terminal_artifact_cli_fallback_route_contract = copy.deepcopy(
        describe_terminal_artifact_cli_fallback_route_contract()
    )
    entrypoints = _build_shell_ui_entrypoints()
    startup_fields = list(SHELL_UI_STARTUP_FIELDS)
    startup_preview = {
        "empty_value": SHELL_UI_STARTUP_EMPTY_PREVIEW,
        "limit": SHELL_UI_STARTUP_PREVIEW_LIMIT,
        "source_field": "basket.item_ids",
    }
    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "shell_ui_schema_version": SHELL_UI_CONTRACT_VERSION,
        "shell_ui_version": SHELL_UI_CONTRACT_VERSION,
        "type": "ShellUIContract",
        "entrypoints": entrypoints,
        "entrypoints_fingerprint": _fingerprint_manifest_section(entrypoints),
        "entrypoints_contract": dict(entrypoints),
        "entrypoints_contract_fingerprint": _fingerprint_manifest_section(entrypoints),
        "startup_fields": startup_fields,
        "startup_fields_contract": list(startup_fields),
        "startup_fields_contract_fingerprint": _fingerprint_manifest_section(startup_fields),
        "startup_preview": startup_preview,
        "startup_preview_contract": dict(startup_preview),
        "startup_preview_contract_fingerprint": _fingerprint_manifest_section(startup_preview),
        "terminal_artifact_cli_fallback_entrypoint": terminal_artifact_cli_fallback_entrypoint,
        "terminal_artifact_cli_fallback_entrypoint_contract": terminal_artifact_cli_fallback_entrypoint,
        "terminal_artifact_cli_fallback_entrypoint_fingerprint": _fingerprint_manifest_section(
            terminal_artifact_cli_fallback_entrypoint
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprint": _fingerprint_manifest_section(
            terminal_artifact_cli_fallback_entrypoint
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_manifest": copy.deepcopy(
            terminal_artifact_cli_fallback_entrypoint_contract_manifest
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint": (
            terminal_artifact_cli_fallback_entrypoint_contract_manifest["contract_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints": dict(
            terminal_artifact_cli_fallback_entrypoint_contract_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"]
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint()
        ),
        "terminal_artifact_cli_fallback_target": copy.deepcopy(
            terminal_artifact_cli_fallback_target_contract
        ),
        "terminal_artifact_cli_fallback_target_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract": copy.deepcopy(
            terminal_artifact_cli_fallback_target_contract
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_manifest": copy.deepcopy(
            terminal_artifact_cli_fallback_target_contract
        ),
        "terminal_artifact_cli_fallback_target_contract_manifest_fingerprint": (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_route_fingerprint": terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_route_contract_fingerprint": terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_route": copy.deepcopy(
            terminal_artifact_cli_fallback_route_contract
        ),
        "terminal_artifact_cli_fallback_route_contract": copy.deepcopy(
            terminal_artifact_cli_fallback_route_contract
        ),
        "terminal_artifact_cli_fallback_route_contract_manifest": copy.deepcopy(
            terminal_artifact_cli_fallback_route_contract
        ),
        "terminal_artifact_cli_fallback_route_contract_manifest_fingerprint": (
            terminal_artifact_cli_fallback_route_contract["contract_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_route_contract_fingerprints": dict(
            terminal_artifact_cli_fallback_route_contract["contract_fingerprints"]
        ),
        "terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_route_contract["contract_fingerprints_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints": dict(
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints"]
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_contract": describe_terminal_artifact_cli_fallback_contract(),
        "terminal_artifact_cli_fallback_contract_fingerprint": terminal_artifact_cli_fallback_contract_fingerprint(),
        "terminal_artifact_renderer_entrypoints_contract": describe_terminal_artifact_renderer_entrypoints_contract(),
        "terminal_artifact_renderer_entrypoints_contract_fingerprint": (
            terminal_artifact_renderer_entrypoints_contract_fingerprint()
        ),
    }
    if include_contract_aliases:
        manifest["terminal_artifact_renderer_entrypoints_contract_manifest"] = copy.deepcopy(
            manifest["terminal_artifact_renderer_entrypoints_contract"]
        )
        manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"] = manifest[
            "terminal_artifact_renderer_entrypoints_contract_fingerprint"
        ]
    return manifest


def describe_shell_ui_contract_fingerprints(
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the shell UI contract sections."""

    entrypoints = _build_shell_ui_entrypoints()
    startup_fields = list(SHELL_UI_STARTUP_FIELDS)
    startup_preview = {
        "empty_value": SHELL_UI_STARTUP_EMPTY_PREVIEW,
        "limit": SHELL_UI_STARTUP_PREVIEW_LIMIT,
        "source_field": "basket.item_ids",
    }
    terminal_artifact_cli_fallback_entrypoint = "render_terminal_cli_fallback"
    terminal_artifact_cli_fallback_entrypoint_fingerprint = _fingerprint_manifest_section(
        terminal_artifact_cli_fallback_entrypoint
    )
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
    )
    terminal_artifact_cli_fallback_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_contract_fingerprint()
    )
    terminal_artifact_cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    terminal_artifact_cli_fallback_target_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_target_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    )
    terminal_artifact_cli_fallback_route_contract = describe_terminal_artifact_cli_fallback_route_contract()
    terminal_artifact_cli_fallback_route_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_route_contract_fingerprint()
    )
    terminal_artifact_renderer_entrypoints_contract_fingerprint_value = (
        terminal_artifact_renderer_entrypoints_contract_fingerprint()
    )
    shell_ui_contract_fingerprint_value = shell_ui_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    fingerprints = {
        "shell_ui_contract_fingerprint": shell_ui_contract_fingerprint_value,
        "shell_ui_fingerprint": shell_ui_contract_fingerprint_value,
        "shell_ui_contract_manifest": shell_ui_contract_fingerprint_value,
        "shell_ui_contract_manifest_fingerprint": shell_ui_contract_fingerprint_value,
        "entrypoints": _fingerprint_manifest_section(entrypoints),
        "entrypoints_contract": _fingerprint_manifest_section(entrypoints),
        "startup_fields": _fingerprint_manifest_section(startup_fields),
        "startup_fields_contract": _fingerprint_manifest_section(startup_fields),
        "startup_preview": _fingerprint_manifest_section(startup_preview),
        "startup_preview_contract": _fingerprint_manifest_section(startup_preview),
        "terminal_artifact_cli_fallback_entrypoint": (
            terminal_artifact_cli_fallback_entrypoint_fingerprint
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract": (
            terminal_artifact_cli_fallback_entrypoint_fingerprint
        ),
        "terminal_artifact_cli_fallback_target": terminal_artifact_cli_fallback_target_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_target_contract": (
            terminal_artifact_cli_fallback_target_contract_fingerprint_value
        ),
        "terminal_artifact_cli_fallback_route": terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_route_contract": (
            terminal_artifact_cli_fallback_route_contract_fingerprint_value
        ),
        "terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_route_contract["contract_fingerprints_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_route_contract_fingerprints": (
            terminal_artifact_cli_fallback_route_contract["contract_fingerprints_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints": (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"]
        ),
        "terminal_artifact_cli_fallback": terminal_artifact_cli_fallback_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_contract": terminal_artifact_cli_fallback_contract_fingerprint_value,
        "terminal_artifact_renderer_entrypoints": terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        "terminal_artifact_renderer_entrypoints_contract": (
            terminal_artifact_renderer_entrypoints_contract_fingerprint_value
        ),
    }
    _add_contract_alias_fingerprints(
        fingerprints,
        ("entrypoints", fingerprints["entrypoints"]),
        ("entrypoints_contract", fingerprints["entrypoints_contract"]),
        ("startup_fields", fingerprints["startup_fields"]),
        ("startup_fields_contract", fingerprints["startup_fields_contract"]),
        ("startup_preview", fingerprints["startup_preview"]),
        ("startup_preview_contract", fingerprints["startup_preview_contract"]),
        (
            "terminal_artifact_cli_fallback_entrypoint",
            fingerprints["terminal_artifact_cli_fallback_entrypoint"],
        ),
        (
            "terminal_artifact_cli_fallback_entrypoint_contract",
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
        ),
        (
            "terminal_artifact_cli_fallback_entrypoint_contract_manifest",
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints",
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        ),
        (
            "terminal_artifact_cli_fallback_route_contract_manifest",
            terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_cli_fallback_route_contract_manifest_fingerprint",
            terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_cli_fallback_contract",
            fingerprints["terminal_artifact_cli_fallback_contract"],
        ),
        (
            "terminal_artifact_renderer_entrypoints_contract",
            fingerprints["terminal_artifact_renderer_entrypoints_contract"],
        ),
        (
            "terminal_artifact_renderer_entrypoints_contract_manifest",
            terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        ),
    )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            ("contract", shell_ui_contract_fingerprint_value),
            ("shell_ui_contract", shell_ui_contract_fingerprint_value),
            (
                "terminal_artifact_cli_fallback_target_contract_manifest",
                terminal_artifact_cli_fallback_target_contract_fingerprint_value,
            ),
        )
    return fingerprints


def describe_shell_ui_contract(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    """Return the stable shell UI contract manifest."""

    manifest = copy.deepcopy(
        _build_shell_ui_contract_manifest(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
    )
    contract_fingerprints = describe_shell_ui_contract_fingerprints(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )
    fingerprint = _fingerprint_manifest_section(manifest)
    manifest["contract_fingerprints"] = dict(contract_fingerprints)
    manifest["contract_fingerprints_fingerprint"] = _fingerprint_manifest_section(contract_fingerprints)
    manifest["contract_fingerprints_contract"] = copy.deepcopy(manifest["contract_fingerprints"])
    manifest["contract_fingerprints_contract_fingerprint"] = manifest["contract_fingerprints_fingerprint"]
    manifest["shell_ui_contract_fingerprints"] = copy.deepcopy(manifest["contract_fingerprints"])
    manifest["shell_ui_contract_fingerprints_fingerprint"] = manifest["contract_fingerprints_fingerprint"]
    # Snapshot the manifest deeply so embedded contract views do not alias the
    # live manifest's nested entrypoint and preview structures.
    manifest["shell_ui_contract"] = copy.deepcopy(manifest)
    manifest["shell_ui_contract_fingerprint"] = fingerprint
    manifest["startup_fields_fingerprint"] = contract_fingerprints["startup_fields_fingerprint"]
    manifest["startup_preview_fingerprint"] = contract_fingerprints["startup_preview_fingerprint"]
    manifest["shell_ui_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def shell_ui_contract_fingerprint(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return a stable fingerprint for the shell UI contract manifest."""

    return _fingerprint_manifest_section(
        _build_shell_ui_contract_manifest(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    )
