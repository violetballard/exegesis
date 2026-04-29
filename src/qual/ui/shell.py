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
    describe_card_contract,
    card_contract_fingerprint,
    SelectionRef,
    _add_contract_alias_fingerprints,
    normalize_action_ref,
    normalize_selection_ref,
    describe_terminal_artifact_cli_fallback_contract,
    describe_terminal_artifact_cli_fallback_entrypoint_contract,
    describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract,
    describe_terminal_artifact_cli_fallback_target_contract,
    describe_terminal_artifact_cli_fallback_route_contract,
    describe_terminal_artifact_renderer_entrypoints_contract,
    describe_terminal_artifact_rendering_contract,
    describe_terminal_fallback_contract,
    terminal_fallback_contract_fingerprint,
    terminal_artifact_cli_fallback_contract_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint,
    terminal_artifact_cli_fallback_target_contract_fingerprint,
    terminal_artifact_cli_fallback_route_contract_fingerprint,
    terminal_artifact_renderer_entrypoints_contract_fingerprint,
    terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint,
    terminal_artifact_rendering_contract_fingerprint,
    _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT,
    _fingerprint_manifest_section,
    _has_expected_card_renderer_prefix,
    _is_nonempty_terminal_rendered_text,
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
    _should_force_invalid_terminal_card_for_card_hinted_leaf,
    _is_malformed_terminal_artifact_envelope,
    _extract_terminal_artifact_envelope,
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
        if normalized_kind == "card" and _is_explicit_terminal_artifact_leaf(artifact):
            # Card hints must not be able to smuggle typed leaf payloads back
            # through the shell fallback path if a downstream resolver fails.
            return _render_invalid_terminal_card(artifact)
        if normalized_kind == "card" and isinstance(artifact, Mapping) and _is_malformed_terminal_artifact_envelope(artifact):
            payload = artifact.get("artifact")
            envelope_kind = _normalize_terminal_artifact_envelope_kind(artifact.get("kind"))
            if _should_force_invalid_terminal_card_for_card_hinted_leaf(
                payload,
                envelope_kind=envelope_kind,
            ):
                return _render_invalid_terminal_card(artifact)
        explicit_leaf_render = self._render_explicit_raw_leaf_hint(artifact, normalized_kind)
        if explicit_leaf_render is not None:
            return explicit_leaf_render
        resolved_fallback: tuple[Any, str | None] | None = None
        if normalized_kind == "card":
            try:
                resolved_fallback = self._resolve_fallback_artifact(artifact, kind=normalized_kind)
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
                    kind=normalized_kind,
                )
            except Exception:
                fallback_artifact = artifact
                fallback_kind = normalized_kind
                if fallback_kind is None:
                    fallback_kind = self._infer_fallback_kind(artifact)
            else:
                if (
                    normalized_kind in {"action", "selection"}
                    and fallback_kind != normalized_kind
                    and not _should_preserve_raw_leaf_card_default(artifact)
                ):
                    fallback_artifact = artifact
                    fallback_kind = normalized_kind
            if (
                kind is None
                and fallback_kind == "card"
                and isinstance(artifact, Mapping)
                and _is_malformed_terminal_artifact_envelope(artifact)
                and _normalize_terminal_artifact_envelope_kind(artifact.get("kind")) == "card"
            ):
                recovered_payload = artifact.get("artifact")
                recovered_kind = _recover_terminal_artifact_leaf_kind(recovered_payload)
                if recovered_kind in {"action", "selection"}:
                    fallback_artifact = recovered_payload
                    fallback_kind = recovered_kind
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
            return self._render_cli_fallback_with_recovery(
                fallback_artifact,
                fallback_kind,
            )
        finally:
            if fallback_hint_token is not None:
                _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.reset(fallback_hint_token)

    def render_cli_fallback(self, artifact: Any, *, kind: str | None = None) -> str:
        """Render an A2UI artifact through the explicit CLI fallback entrypoint."""
        normalized_kind = self._normalize_fallback_kind(kind)
        fallback_hint_token = None
        fallback_target: tuple[Any, str] | None = None
        explicit_leaf_render = self._render_explicit_raw_leaf_hint(artifact, normalized_kind)
        if explicit_leaf_render is not None:
            return explicit_leaf_render
        if normalized_kind == "card" and _is_malformed_terminal_artifact_envelope(artifact):
            # Keep malformed card envelopes on the safe invalid-card path.
            # Everything else flows through the shell's canonical fallback
            # classifier so the shell and CLI entrypoints stay on the same
            # target-selection policy.
            fallback_target = (artifact, "card")
        else:
            fallback_target = self._resolve_fallback_artifact(artifact, kind=normalized_kind)
        if (
            normalized_kind in {"action", "selection"}
            and fallback_target is not None
            and fallback_target[1] != normalized_kind
            and not _should_preserve_raw_leaf_card_default(artifact)
        ):
            fallback_target = (artifact, normalized_kind)
        if (
            normalized_kind == "card"
            and fallback_target is not None
            and isinstance(artifact, Mapping)
        ):
            try:
                extracted_envelope = _extract_terminal_artifact_envelope(artifact)
            except ValueError:
                extracted_envelope = None
            if extracted_envelope is not None:
                _, envelope_kind = extracted_envelope
                if envelope_kind in {"action", "selection"}:
                    # Valid typed envelopes should still respect a card hint
                    # in the explicit CLI fallback entrypoint. Malformed
                    # envelopes keep their recovery path below.
                    fallback_target = (artifact, "card")
        if normalized_kind in {"action", "selection"} and not ShellUI._contains_action_or_selection_payload(artifact):
            # Keep the explicit CLI fallback entrypoint aligned with the
            # shared contract: plain cards under a leaf hint should fail as
            # leaf renders instead of silently downgrading back to card text.
            fallback_target = (artifact, normalized_kind)
        fallback_hint_token = _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.set(fallback_target)
        try:
            if fallback_target is not None:
                fallback_artifact, fallback_kind = fallback_target
                return self._render_cli_fallback_with_recovery(fallback_artifact, fallback_kind)
            return self._render_cli_fallback_with_recovery(artifact, normalized_kind)
        finally:
            if fallback_hint_token is not None:
                _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.reset(fallback_hint_token)

    def _render_cli_fallback_with_recovery(
        self,
        artifact: Any,
        kind: str | None,
    ) -> str:
        """Render through the shared CLI fallback path and recover on failure.

        The explicit CLI fallback entrypoint should stay usable even if the
        shared fallback renderer raises or returns an unexpected leaf shape.
        """

        leaf_specific_fallback = kind in {"action", "selection"}
        explicit_leaf_source = kind == "card" and _is_explicit_terminal_artifact_leaf(artifact)
        card_hint_leaf_kind: str | None = None
        if kind == "card" and not _should_preserve_raw_leaf_card_default(artifact):
            inferred_leaf_kind = _infer_terminal_artifact_explicit_kind(artifact)
            if inferred_leaf_kind not in {"action", "selection"} and isinstance(artifact, Mapping):
                artifact_type = artifact.get("type")
                if isinstance(artifact_type, str) and artifact_type.strip() == "TerminalArtifact":
                    inferred_payload_kind = _infer_terminal_artifact_explicit_kind(artifact.get("artifact"))
                    if inferred_payload_kind in {"action", "selection"}:
                        inferred_leaf_kind = inferred_payload_kind
            if inferred_leaf_kind in {"action", "selection"}:
                card_hint_leaf_kind = inferred_leaf_kind
        try:
            rendered_cli_fallback = render_terminal_cli_fallback(artifact, kind=kind)
        except Exception:
            rendered_cli_fallback = None
        else:
            if _is_nonempty_terminal_rendered_text(rendered_cli_fallback):
                if leaf_specific_fallback and self._has_expected_leaf_renderer_prefix(
                    rendered_cli_fallback,
                    kind,
                ):
                    return rendered_cli_fallback
                if kind == "card":
                    if _has_expected_card_renderer_prefix(rendered_cli_fallback):
                        return rendered_cli_fallback
                    if (
                        not _should_preserve_raw_leaf_card_default(artifact)
                        and card_hint_leaf_kind in {"action", "selection"}
                        and self._has_expected_leaf_renderer_prefix(
                            rendered_cli_fallback,
                            card_hint_leaf_kind,
                        )
                    ):
                        return rendered_cli_fallback
                if kind not in {"action", "selection", "card"}:
                    return rendered_cli_fallback
        if kind == "card" and card_hint_leaf_kind in {"action", "selection"}:
            if explicit_leaf_source:
                # Direct ActionRef/SelectionRef instances stay on the invalid
                # card path even when the shared CLI fallback renderer fails.
                return _render_invalid_terminal_card(artifact)
        if kind == "action":
            try:
                rendered_action = render_terminal_action(artifact)
            except Exception:
                return _render_invalid_terminal_action(artifact)
            if _is_nonempty_terminal_rendered_text(rendered_action):
                return rendered_action
            return _render_invalid_terminal_action(artifact)
        if kind == "selection":
            try:
                rendered_selection = render_terminal_selection(artifact)
            except Exception:
                return _render_invalid_terminal_selection(artifact)
            if _is_nonempty_terminal_rendered_text(rendered_selection):
                return rendered_selection
            return _render_invalid_terminal_selection(artifact)
        if kind == "card" and card_hint_leaf_kind in {"action", "selection"}:
            if card_hint_leaf_kind == "action":
                try:
                    rendered_action = render_terminal_action(artifact)
                except Exception:
                    pass
                else:
                    if _is_nonempty_terminal_rendered_text(rendered_action):
                        return rendered_action
            else:
                try:
                    rendered_selection = render_terminal_selection(artifact)
                except Exception:
                    pass
                else:
                    if _is_nonempty_terminal_rendered_text(rendered_selection):
                        return rendered_selection
        if kind not in {"action", "selection"}:
            try:
                # Retry the shared renderer on the resolved fallback target so
                # we do not reprocess the original envelope after CLI fallback
                # resolution has already recovered a safer payload.
                rendered_artifact = render_terminal_artifact(artifact, kind=kind)
            except Exception:
                pass
            else:
                if _is_nonempty_terminal_rendered_text(rendered_artifact):
                    if kind == "card":
                        if card_hint_leaf_kind in {"action", "selection"}:
                            if self._has_expected_leaf_renderer_prefix(rendered_artifact, card_hint_leaf_kind):
                                return rendered_artifact
                        elif _has_expected_card_renderer_prefix(rendered_artifact):
                            return rendered_artifact
                    else:
                        return rendered_artifact
        try:
            rendered_card = render_terminal_card(artifact)
        except Exception:
            return _render_invalid_terminal_card(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_card):
            return rendered_card
        return _render_invalid_terminal_card(artifact)

    def render_startup(self, runtime: EngineRuntime) -> str:
        item_ids = self._snapshot_item_ids(runtime.basket.item_ids)
        preview = self._render_startup_preview(item_ids)
        return (
            "Qual Workstation bootstrap is running\n"
            f"- project: {self._render_startup_value(runtime.vault.project_name)}\n"
            f"- vault: {self._render_startup_value(runtime.vault.root_dir)}\n"
            f"- locked: {self._render_startup_locked_value(runtime.vault.is_locked)}\n"
            f"- context_items: {len(item_ids)}\n"
            f"- context_preview: {preview}"
        )

    @staticmethod
    def _render_startup_preview(item_ids: list[object]) -> str:
        if not item_ids:
            return SHELL_UI_STARTUP_EMPTY_PREVIEW
        if SHELL_UI_STARTUP_PREVIEW_LIMIT <= 0:
            remaining = len(item_ids)
            label = "item" if remaining == 1 else "items"
            return f"+{remaining} more {label}"
        preview_items: list[str] = []
        seen_preview_keys: set[tuple[str, str, str]] = set()
        consumed_items = 0
        for value in item_ids:
            consumed_items += 1
            preview_key = ShellUI._snapshot_item_sort_key(value)
            if preview_key in seen_preview_keys:
                continue
            seen_preview_keys.add(preview_key)
            preview_items.append(ShellUI._format_item_id(value))
            if len(preview_items) >= SHELL_UI_STARTUP_PREVIEW_LIMIT:
                break
        preview = ", ".join(preview_items)
        remaining = len(item_ids) - consumed_items
        if remaining > 0:
            label = "item" if remaining == 1 else "items"
            overflow = f"+{remaining} more {label}"
            return f"{preview}, {overflow}" if preview else overflow
        return preview or SHELL_UI_STARTUP_EMPTY_PREVIEW

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
    def _render_startup_locked_value(value: object) -> str:
        if value is None:
            return "<blank>"
        if isinstance(value, bool):
            return "true" if value else "false"
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
    def _render_explicit_raw_leaf_hint(artifact: Any, normalized_kind: str | None) -> str | None:
        if normalized_kind not in {"action", "selection"}:
            return None
        if not _should_preserve_raw_leaf_card_default(artifact):
            return None
        # Explicit leaf hints should render as leaves even when the raw
        # payload would otherwise stay on the card default.
        if normalized_kind == "action":
            try:
                rendered_leaf = render_terminal_action(artifact)
            except Exception:
                return _render_invalid_terminal_action(artifact)
            if _is_nonempty_terminal_rendered_text(rendered_leaf):
                return rendered_leaf
            return _render_invalid_terminal_action(artifact)
        try:
            rendered_leaf = render_terminal_selection(artifact)
        except Exception:
            return _render_invalid_terminal_selection(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_leaf):
            return rendered_leaf
        return _render_invalid_terminal_selection(artifact)

    @staticmethod
    def _has_expected_leaf_renderer_prefix(rendered: Any, fallback_kind: str) -> bool:
        if not _is_nonempty_terminal_rendered_text(rendered):
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
    card_hint_recovery_policy_contract = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
    card_hint_recovery_policy_contract_fingerprint_value = card_hint_recovery_policy_contract["contract_fingerprint"]
    terminal_artifact_renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    card_contract_manifest = copy.deepcopy(describe_card_contract())
    terminal_artifact_cli_fallback_target_contract = copy.deepcopy(
        describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    )
    terminal_fallback_contract_manifest = copy.deepcopy(describe_terminal_fallback_contract())
    terminal_artifact_cli_fallback_route_contract = copy.deepcopy(
        describe_terminal_artifact_cli_fallback_route_contract()
    )
    terminal_artifact_rendering_contract = copy.deepcopy(describe_terminal_artifact_rendering_contract())
    entrypoints = _build_shell_ui_entrypoints()
    startup_fields = list(SHELL_UI_STARTUP_FIELDS)
    startup_preview = {
        "empty_value": SHELL_UI_STARTUP_EMPTY_PREVIEW,
        "limit": SHELL_UI_STARTUP_PREVIEW_LIMIT,
        "source_field": "basket.item_ids",
    }
    route_precedence_contract = describe_terminal_artifact_cli_fallback_route_contract()
    route_precedence = list(route_precedence_contract["route_precedence"])
    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "shell_ui_schema_version": SHELL_UI_CONTRACT_VERSION,
        "shell_ui_version": SHELL_UI_CONTRACT_VERSION,
        "shell_ui_contract_version": SHELL_UI_CONTRACT_VERSION,
        "type": "ShellUIContract",
        "entrypoints": entrypoints,
        "entrypoints_fingerprint": _fingerprint_manifest_section(entrypoints),
        "entrypoints_contract": dict(entrypoints),
        "entrypoints_contract_manifest": dict(entrypoints),
        "entrypoints_contract_fingerprint": _fingerprint_manifest_section(entrypoints),
        "entrypoints_contract_manifest_fingerprint": _fingerprint_manifest_section(entrypoints),
        "route_precedence": route_precedence,
        "route_precedence_contract": list(route_precedence),
        "route_precedence_contract_manifest": list(route_precedence),
        "route_precedence_fingerprint": _fingerprint_manifest_section(route_precedence),
        "route_precedence_contract_fingerprint": _fingerprint_manifest_section(route_precedence),
        "route_precedence_contract_manifest_fingerprint": _fingerprint_manifest_section(route_precedence),
        "startup_fields": startup_fields,
        "startup_fields_contract": list(startup_fields),
        "startup_fields_contract_manifest": list(startup_fields),
        "startup_fields_contract_fingerprint": _fingerprint_manifest_section(startup_fields),
        "startup_fields_contract_manifest_fingerprint": _fingerprint_manifest_section(startup_fields),
        "startup_preview": startup_preview,
        "startup_preview_contract": dict(startup_preview),
        "startup_preview_contract_manifest": dict(startup_preview),
        "startup_preview_contract_fingerprint": _fingerprint_manifest_section(startup_preview),
        "startup_preview_contract_manifest_fingerprint": _fingerprint_manifest_section(startup_preview),
        "terminal_artifact_cli_fallback_entrypoint": terminal_artifact_cli_fallback_entrypoint,
        "terminal_artifact_cli_fallback_entrypoint_contract": terminal_artifact_cli_fallback_entrypoint,
        "terminal_artifact_cli_fallback_entrypoint_fingerprint": _fingerprint_manifest_section(
            terminal_artifact_cli_fallback_entrypoint
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprint": _fingerprint_manifest_section(
            terminal_artifact_cli_fallback_entrypoint
        ),
        "terminal_artifact_cli_fallback_entrypoint_schema_version": (
            terminal_artifact_cli_fallback_entrypoint_contract_manifest[
                "terminal_artifact_cli_fallback_entrypoint_schema_version"
            ]
        ),
        "terminal_artifact_cli_fallback_entrypoint_version": (
            terminal_artifact_cli_fallback_entrypoint_contract_manifest[
                "terminal_artifact_cli_fallback_entrypoint_version"
            ]
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_manifest": copy.deepcopy(
            terminal_artifact_cli_fallback_entrypoint_contract_manifest
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint": (
            terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint()
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints": dict(
            terminal_artifact_cli_fallback_entrypoint_contract_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"]
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint()
        ),
        "card_hint_recovery_policy": copy.deepcopy(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_contract": copy.deepcopy(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_contract_manifest": copy.deepcopy(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_fingerprint": card_hint_recovery_policy_contract_fingerprint_value,
        "card_hint_recovery_policy_contract_fingerprint": card_hint_recovery_policy_contract_fingerprint_value,
        "card_hint_recovery_policy_contract_manifest_fingerprint": card_hint_recovery_policy_contract_fingerprint_value,
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
        "terminal_artifact_cli_fallback_target_contract_manifest_fingerprints": dict(
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints"]
        ),
        "terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_contract": describe_terminal_artifact_cli_fallback_contract(),
        "terminal_artifact_cli_fallback_contract_fingerprint": terminal_artifact_cli_fallback_contract_fingerprint(),
        "terminal_artifact_cli_fallback_contract_manifest": copy.deepcopy(
            describe_terminal_artifact_cli_fallback_contract()
        ),
        "terminal_artifact_cli_fallback_contract_manifest_fingerprint": (
            terminal_artifact_cli_fallback_contract_fingerprint()
        ),
        "terminal_artifact_renderer_entrypoints_contract": copy.deepcopy(
            terminal_artifact_renderer_entrypoints_contract
        ),
        "renderer_entrypoints_contract_manifest": copy.deepcopy(
            terminal_artifact_renderer_entrypoints_contract
        ),
        "renderer_entrypoints_contract_manifest_fingerprint": (
            terminal_artifact_renderer_entrypoints_contract_fingerprint()
        ),
        "terminal_artifact_renderer_entrypoints_contract_fingerprint": (
            terminal_artifact_renderer_entrypoints_contract_fingerprint()
        ),
        "terminal_artifact_renderer_entrypoints_contract_manifest": copy.deepcopy(
            terminal_artifact_renderer_entrypoints_contract
        ),
        "terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint": (
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        ),
        "terminal_artifact_rendering": copy.deepcopy(terminal_artifact_rendering_contract),
        "terminal_artifact_rendering_contract": copy.deepcopy(terminal_artifact_rendering_contract),
        "terminal_artifact_rendering_contract_manifest": copy.deepcopy(terminal_artifact_rendering_contract),
        "terminal_artifact_rendering_fingerprint": terminal_artifact_rendering_contract["contract_fingerprint"],
        "terminal_artifact_rendering_contract_fingerprint": terminal_artifact_rendering_contract["contract_fingerprint"],
        "terminal_artifact_rendering_contract_manifest_fingerprint": (
            terminal_artifact_rendering_contract["contract_fingerprint"]
        ),
    }
    if include_contract_aliases:
        # Surface the shared card and terminal-fallback contract slices so
        # shell-aware consumers can negotiate the same snapshots as the A2UI
        # fingerprint map without reconstructing them from the generic engine
        # contract.
        manifest["card_contract_manifest"] = copy.deepcopy(card_contract_manifest)
        manifest["card_contract_manifest_fingerprint"] = card_contract_manifest["contract_fingerprint"]
        manifest["terminal_fallback_contract_manifest"] = copy.deepcopy(terminal_fallback_contract_manifest)
        manifest["terminal_fallback_contract_manifest_fingerprint"] = terminal_fallback_contract_manifest[
            "contract_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_manifest"] = copy.deepcopy(
            terminal_artifact_cli_fallback_route_contract
        )
        manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_route_contract["contract_fingerprint"]
        )
        manifest["terminal_artifact_cli_fallback_contract_manifest"] = copy.deepcopy(
            describe_terminal_artifact_cli_fallback_contract()
        )
        manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_contract_fingerprint()
        )
    return manifest


@lru_cache(maxsize=None)
def _describe_shell_ui_contract_fingerprints_cached(
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
    card_hint_recovery_policy_contract = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
    card_hint_recovery_policy_contract_fingerprint_value = card_hint_recovery_policy_contract["contract_fingerprint"]
    terminal_artifact_cli_fallback_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_contract_fingerprint()
    )
    terminal_artifact_cli_fallback_entrypoint_contract = (
        describe_terminal_artifact_cli_fallback_entrypoint_contract()
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
    terminal_artifact_rendering_contract_fingerprint_value = terminal_artifact_rendering_contract_fingerprint()
    route_precedence = list(describe_terminal_artifact_cli_fallback_route_contract()["route_precedence"])
    shell_ui_contract_fingerprint_value = shell_ui_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )
    fingerprints = {
        "shell_ui_contract_fingerprint": shell_ui_contract_fingerprint_value,
        "shell_ui_fingerprint": shell_ui_contract_fingerprint_value,
        "shell_ui_contract_manifest": shell_ui_contract_fingerprint_value,
        "shell_ui_contract_manifest_fingerprint": shell_ui_contract_fingerprint_value,
        "entrypoints": _fingerprint_manifest_section(entrypoints),
        "entrypoints_contract": _fingerprint_manifest_section(entrypoints),
        "entrypoints_contract_manifest": _fingerprint_manifest_section(entrypoints),
        "entrypoints_contract_manifest_fingerprint": _fingerprint_manifest_section(entrypoints),
        "route_precedence": _fingerprint_manifest_section(route_precedence),
        "route_precedence_contract": _fingerprint_manifest_section(route_precedence),
        "route_precedence_contract_manifest": _fingerprint_manifest_section(route_precedence),
        "route_precedence_contract_manifest_fingerprint": _fingerprint_manifest_section(route_precedence),
        "startup_fields": _fingerprint_manifest_section(startup_fields),
        "startup_fields_contract": _fingerprint_manifest_section(startup_fields),
        "startup_fields_contract_manifest": _fingerprint_manifest_section(startup_fields),
        "startup_fields_contract_manifest_fingerprint": _fingerprint_manifest_section(startup_fields),
        "startup_preview": _fingerprint_manifest_section(startup_preview),
        "startup_preview_contract": _fingerprint_manifest_section(startup_preview),
        "startup_preview_contract_manifest": _fingerprint_manifest_section(startup_preview),
        "startup_preview_contract_manifest_fingerprint": _fingerprint_manifest_section(startup_preview),
        "terminal_artifact_cli_fallback_entrypoint": terminal_artifact_cli_fallback_entrypoint_fingerprint,
        "terminal_artifact_cli_fallback_entrypoint_contract": terminal_artifact_cli_fallback_entrypoint_fingerprint,
        "card_hint_recovery_policy": card_hint_recovery_policy_contract_fingerprint_value,
        "card_hint_recovery_policy_contract": card_hint_recovery_policy_contract_fingerprint_value,
        "card_hint_recovery_policy_contract_manifest": card_hint_recovery_policy_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_target": terminal_artifact_cli_fallback_target_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_target_contract": terminal_artifact_cli_fallback_target_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_target_contract_fingerprint": terminal_artifact_cli_fallback_target_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_target_contract_manifest_fingerprint": terminal_artifact_cli_fallback_target_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_route": terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_route_contract": terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint": terminal_artifact_cli_fallback_route_contract["contract_fingerprints_fingerprint"],
        "terminal_artifact_cli_fallback_route_contract_fingerprints": terminal_artifact_cli_fallback_route_contract["contract_fingerprints_fingerprint"],
        "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint": terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"],
        "terminal_artifact_cli_fallback_target_contract_fingerprints": terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"],
        "terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint": terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"],
        "terminal_artifact_cli_fallback_target_contract_manifest_fingerprints": terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"],
        "terminal_artifact_cli_fallback": terminal_artifact_cli_fallback_contract_fingerprint_value,
        "terminal_artifact_cli_fallback_contract": terminal_artifact_cli_fallback_contract_fingerprint_value,
        "terminal_artifact_renderer_entrypoints": terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        "terminal_artifact_renderer_entrypoints_contract": terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        "renderer_entrypoints_contract_manifest": terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        "renderer_entrypoints_contract_manifest_fingerprint": terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        "terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint": (
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        ),
        "terminal_artifact_rendering": terminal_artifact_rendering_contract_fingerprint_value,
        "terminal_artifact_rendering_contract": terminal_artifact_rendering_contract_fingerprint_value,
        "terminal_artifact_rendering_contract_manifest": terminal_artifact_rendering_contract_fingerprint_value,
        "terminal_artifact_rendering_fingerprint": terminal_artifact_rendering_contract_fingerprint_value,
        "terminal_artifact_rendering_contract_fingerprint": terminal_artifact_rendering_contract_fingerprint_value,
        "terminal_artifact_rendering_contract_manifest_fingerprint": terminal_artifact_rendering_contract_fingerprint_value,
    }
    _add_contract_alias_fingerprints(
        fingerprints,
        ("entrypoints", fingerprints["entrypoints"]),
        ("entrypoints_contract", fingerprints["entrypoints_contract"]),
        ("entrypoints_contract_manifest", fingerprints["entrypoints_contract_manifest"]),
        ("route_precedence", fingerprints["route_precedence"]),
        ("route_precedence_contract", fingerprints["route_precedence_contract"]),
        ("route_precedence_contract_manifest", fingerprints["route_precedence_contract_manifest"]),
        ("startup_fields", fingerprints["startup_fields"]),
        ("startup_fields_contract", fingerprints["startup_fields_contract"]),
        ("startup_fields_contract_manifest", fingerprints["startup_fields_contract_manifest"]),
        ("startup_preview", fingerprints["startup_preview"]),
        ("startup_preview_contract", fingerprints["startup_preview_contract"]),
        ("startup_preview_contract_manifest", fingerprints["startup_preview_contract_manifest"]),
        ("terminal_artifact_cli_fallback_entrypoint", fingerprints["terminal_artifact_cli_fallback_entrypoint"]),
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
        ("card_hint_recovery_policy_contract", card_hint_recovery_policy_contract_fingerprint_value),
        ("card_hint_recovery_policy_contract_manifest", card_hint_recovery_policy_contract_fingerprint_value),
        (
            "terminal_artifact_cli_fallback_target_contract_manifest",
            terminal_artifact_cli_fallback_target_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_cli_fallback_target_contract_manifest_fingerprints",
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"],
        ),
        (
            "terminal_artifact_cli_fallback_route_contract_manifest",
            terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_cli_fallback_contract_manifest",
            terminal_artifact_cli_fallback_contract_fingerprint(),
        ),
        (
            "terminal_artifact_cli_fallback_route_contract_manifest_fingerprint",
            terminal_artifact_cli_fallback_route_contract_fingerprint_value,
        ),
        ("terminal_artifact_cli_fallback_contract", fingerprints["terminal_artifact_cli_fallback_contract"]),
        (
            "terminal_artifact_renderer_entrypoints_contract",
            fingerprints["terminal_artifact_renderer_entrypoints_contract"],
        ),
        (
            "terminal_artifact_renderer_entrypoints_contract_manifest",
            terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_rendering_contract_manifest",
            terminal_artifact_rendering_contract_fingerprint_value,
        ),
        ("card_contract_manifest", card_contract_fingerprint()),
        ("terminal_fallback_contract_manifest", terminal_fallback_contract_fingerprint()),
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
            (
                "terminal_artifact_rendering_contract_manifest",
                terminal_artifact_rendering_contract_fingerprint_value,
            ),
        )
    return fingerprints


def describe_shell_ui_contract_fingerprints(
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the shell UI contract sections.

    The public helper returns a fresh snapshot so callers cannot mutate the
    cached fingerprint map that backs contract negotiation.
    """

    return dict(
        _describe_shell_ui_contract_fingerprints_cached(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
    )


def describe_shell_ui_contract_manifest_fingerprints(
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return the shell UI contract fingerprints under a manifest-specific name."""

    return describe_shell_ui_contract_fingerprints(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )


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
    manifest["shell_ui_contract_manifest_fingerprints"] = copy.deepcopy(manifest["contract_fingerprints"])
    manifest["shell_ui_contract_manifest_fingerprints_fingerprint"] = manifest["contract_fingerprints_fingerprint"]
    # Snapshot the manifest deeply so embedded contract views do not alias the
    # live manifest's nested entrypoint and preview structures.
    manifest["shell_ui_contract"] = copy.deepcopy(manifest)
    manifest["shell_ui_contract_manifest"] = copy.deepcopy(manifest["shell_ui_contract"])
    manifest["shell_ui_contract_manifest_fingerprint"] = fingerprint
    manifest["shell_ui_contract_fingerprint"] = fingerprint
    manifest["contract_manifest"] = copy.deepcopy(manifest["shell_ui_contract"])
    manifest["contract_manifest_fingerprint"] = fingerprint
    manifest["startup_fields_fingerprint"] = contract_fingerprints["startup_fields_fingerprint"]
    manifest["startup_preview_fingerprint"] = contract_fingerprints["startup_preview_fingerprint"]
    manifest["shell_ui_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_shell_ui_contract_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    """Return the shell UI contract under a manifest-specific name."""

    return describe_shell_ui_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )


def shell_ui_contract_fingerprint(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> str:
    """Return a stable fingerprint for the shell UI contract manifest."""

    return _fingerprint_manifest_section(
        _build_shell_ui_contract_manifest(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
    )


def shell_ui_contract_manifest_fingerprint(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> str:
    """Return the shell UI contract fingerprint under a manifest-specific name."""

    return shell_ui_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )


def shell_ui_contract_manifest_fingerprints_fingerprint(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> str:
    """Return the fingerprint for the shell UI contract fingerprint manifest."""

    return _fingerprint_manifest_section(
        describe_shell_ui_contract_manifest_fingerprints(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
    )
