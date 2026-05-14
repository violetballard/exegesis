from __future__ import annotations

import ast
import copy
import hashlib
import json
import unicodedata
from functools import lru_cache
from contextvars import ContextVar
from collections.abc import Iterable, Mapping, Sequence, Set
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, Protocol

A2UI_VERSION = 1
A2UI_CONTRACT_VERSION = 2
A2UI_ACTION_SCHEMA_VERSION = 1
A2UI_CAPABILITIES_SCHEMA_VERSION = 1
A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION = 1
ENGINE_OUTPUT_SCHEMA_VERSION = 1
SELECTION_SCHEMA_VERSION = 1
A2UI_LEAF_CONTRACTS_SCHEMA_VERSION = 1
CARD_CONTRACT_VERSION = 1
TERMINAL_FALLBACK_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_RENDER_SEPARATOR = "\n\n"
TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ID_FINGERPRINT_PREFIX_CHARS = 16
TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION = 1
TERMINAL_ARTIFACT_KIND_CONTRACTS_SCHEMA_VERSION = 1
_TERMINAL_ARTIFACT_ENVELOPE_TYPE = "TerminalArtifact"
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"
DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES = 8_192
FALLBACK_COPY_ACTION_ID = "copy_to_clipboard"
GENERIC_FALLBACK_SUBTITLE = "Rendered as GenericCard because client does not support this specialized card."
UNKNOWN_FALLBACK_SUBTITLE = "Read-only fallback view with safe primitive blocks and raw JSON preview."
GENERIC_FALLBACK_TITLE_PREFIX = "Fallback view for "
UNKNOWN_FALLBACK_TITLE_PREFIX = "Unsupported card type: "
TERMINAL_ARTIFACT_SUPPORTED_KINDS: tuple[str, str, str] = ("card", "action", "selection")
TERMINAL_ARTIFACT_DEFAULT_KIND = "card"
_RESERVED_CARD_TYPES: tuple[str, ...] = (GENERIC_CARD_TYPE, UNKNOWN_CARD_TYPE)
_SPECIALIZED_CARD_TYPES: tuple[str, ...] = (
    "ProposedEditCard",
    "EvidenceCard",
    "QuestionsCard",
    "RunLogCard",
)

_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE: tuple[str, ...] = (
    "shared_target_resolver",
    "shell_refinement",
    "render_terminal_action",
    "render_terminal_selection",
    "render_terminal_card",
)
ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER: tuple[str, ...] = (
    "plan",
    "revise",
    "patch",
    "apply",
)

_TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT: ContextVar[tuple[Any, str] | None] = ContextVar(
    "qual_terminal_artifact_cli_fallback_target_hint",
    default=None,
)

_TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS: tuple[tuple[str, str], ...] = (
    ("terminal_artifact", "render_terminal_artifact"),
    ("card", "render_terminal_card"),
    ("action", "render_terminal_action"),
    ("selection", "render_terminal_selection"),
    ("cli_fallback", "render_terminal_cli_fallback"),
    ("cli_fallback_payload", "render_terminal_artifact_cli_fallback_payload"),
    ("engine_artifact_validation_report", "render_engine_artifact_validation_report"),
)

ALLOWED_ACTION_IDS: tuple[str, ...] = (
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "pin_to_context_set",
    "create_context_set",
    "run_agent",
    "refresh_license",
    "export_document",
    "copy_to_clipboard",
)

REQUIRED_PRIMITIVE_BLOCKS: tuple[str, ...] = (
    "MarkdownBlock",
    "KeyValueBlock",
    "ListBlock",
    "TableBlock",
    "AlertBlock",
    "ProgressBlock",
    "CodeBlock",
)

_PRIMITIVE_BLOCK_SET = set(REQUIRED_PRIMITIVE_BLOCKS)
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)
_TERMINAL_ARTIFACT_SUPPORTED_KIND_SET = set(TERMINAL_ARTIFACT_SUPPORTED_KINDS)
_TERMINAL_ARTIFACT_NON_CARD_KIND_SET = set(TERMINAL_ARTIFACT_SUPPORTED_KINDS) - {TERMINAL_ARTIFACT_DEFAULT_KIND}

_PRIMITIVE_BLOCK_SCHEMAS: dict[str, tuple[str, ...]] = {
    "MarkdownBlock": ("markdown",),
    "KeyValueBlock": ("items",),
    "ListBlock": ("items",),
    "TableBlock": ("rows",),
    "AlertBlock": ("severity", "title", "message"),
    "ProgressBlock": ("status_text", "title"),
    "CodeBlock": ("code", "language", "collapsed"),
}

_PRIMITIVE_BLOCK_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "MarkdownBlock": ("markdown",),
    "KeyValueBlock": ("items",),
    "ListBlock": ("items",),
    "TableBlock": ("rows",),
    "AlertBlock": ("message",),
    "ProgressBlock": ("status_text",),
    "CodeBlock": ("code",),
}

_ACTION_SCHEMAS: dict[str, dict[str, type]] = {
    "apply_patch": {"patch_id": str},
    "reject_patch": {"patch_id": str},
    "open_section": {"section_id": str},
    "open_corpus_item": {"item_id": str},
    "pin_to_context_set": {"item_id": str},
    "create_context_set": {"name": str},
    "run_agent": {"operation": str},
    "refresh_license": {},
    "export_document": {"format": str},
    "copy_to_clipboard": {"text": str},
}
_ACTION_PAYLOAD_FREE_TEXT_FIELDS: dict[str, tuple[str, ...]] = {
    "copy_to_clipboard": ("text",),
}
_ACTION_PAYLOAD_IDENTIFIER_FIELDS: dict[str, tuple[str, ...]] = {
    action_id: tuple(
        field
        for field, value_type in schema.items()
        if value_type is str and field not in _ACTION_PAYLOAD_FREE_TEXT_FIELDS.get(action_id, ())
    )
    for action_id, schema in _ACTION_SCHEMAS.items()
}

_CAPABILITIES_REQUIRED_FIELDS: tuple[str, ...] = (
    "a2ui_version",
    "client_name",
    "cards_supported",
    "primitive_blocks_supported",
    "actions_supported",
    "max_payload_bytes",
    "supports_streaming",
)

_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_REQUIRED_FIELDS: tuple[str, ...] = (
    "type",
    "schema_version",
    "contract_version",
    "a2ui_version",
    "artifact_count",
    "artifact_order",
    "artifact_order_fingerprint",
    "cli_fallback_fingerprint",
    "rendered_text",
    "rendered_text_fingerprint",
    "artifacts",
    "cli_fallback",
    "payload_fingerprint",
)
_ENGINE_ARTIFACT_VALIDATION_REPORT_REQUIRED_FIELDS: tuple[str, ...] = (
    "type",
    "schema_version",
    "contract_version",
    "a2ui_version",
    "input_shape",
    "artifact_count",
    "artifact_order",
    "artifact_order_fingerprint",
    "artifact_kind_counts",
    "artifact_kind_counts_fingerprint",
    "stage_coverage",
    "stage_coverage_fingerprint",
    "valid",
    "workflow_ready",
    "workflow_blocked_reason",
    "error_count",
    "error_codes",
    "errors",
    "error_fingerprint",
    "contract_fingerprint",
    "rendered_text",
    "rendered_text_fingerprint",
    "report_fingerprint",
)
_ENGINE_ARTIFACT_VALIDATION_ERROR_RECORD_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "index",
    "location",
    "path",
    "stage",
    "kind",
    "normalized_kind",
    "code",
    "message",
)
_ENGINE_ARTIFACT_VALIDATION_ORDER_RECORD_REQUIRED_FIELDS: tuple[str, ...] = (
    "index",
    "location",
    "path",
    "stage",
    "kind",
    "normalized_kind",
    "artifact_fingerprint",
)
_ENGINE_ARTIFACT_VALIDATION_ERROR_CODES: tuple[str, ...] = (
    "invalid_container",
    "invalid_stage",
    "invalid_pair",
    "invalid_kind",
    "invalid_envelope_kind",
    "invalid_payload",
)
_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_CLI_ENTRY_FIELDS: tuple[str, ...] = (
    "index",
    "artifact_id",
    "kind",
    "artifact_fingerprint",
    "text",
    "text_fingerprint",
)
_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ORDER_FIELDS: tuple[str, ...] = (
    "index",
    "artifact_id",
    "kind",
    "artifact_fingerprint",
)
_TERMINAL_ARTIFACT_ENVELOPE_REQUIRED_FIELDS: tuple[str, ...] = (
    "type",
    "kind",
    "artifact",
    "contract_version",
    "a2ui_version",
)


@dataclass(frozen=True)
class A2UICapabilities:
    a2ui_version: int
    client_name: str
    cards_supported: tuple[str, ...]
    primitive_blocks_supported: tuple[str, ...]
    actions_supported: tuple[str, ...]
    max_payload_bytes: int
    supports_streaming: bool


@dataclass(frozen=True)
class ActionRef:
    id: str
    label: str
    payload: dict[str, Any]
    confirm: dict[str, str] | None = None
    policy_sensitive: bool = False
    schema_version: int = A2UI_ACTION_SCHEMA_VERSION
    a2ui_version: int = A2UI_VERSION


@dataclass(frozen=True)
class SelectionRef:
    id: str
    label: str
    payload: dict[str, Any]
    selected: bool = False
    disabled: bool = False
    schema_version: int = SELECTION_SCHEMA_VERSION
    a2ui_version: int = A2UI_VERSION


@dataclass(frozen=True)
class EngineOutput:
    schema_version: int
    contract_version: int
    a2ui_version: int
    artifacts: tuple[tuple[str, Any], ...]
    valid: bool
    error_count: int
    errors: tuple[str, ...]
    stage_coverage: dict[str, Any]
    fingerprint: str


class PolicyGate(Protocol):
    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        ...


class A2UISessionStore:
    def __init__(self) -> None:
        self._by_session: dict[str, A2UICapabilities] = {}

    def register(self, session_id: str, capabilities: A2UICapabilities) -> None:
        self._by_session[session_id] = normalize_capabilities(capabilities)

    def get(self, session_id: str) -> A2UICapabilities:
        if session_id not in self._by_session:
            raise KeyError(f"Unknown session: {session_id}")
        return self._by_session[session_id]


def _snapshot_contract_value(value: Any, _seen: set[int] | None = None) -> Any:
    if value is None or type(value) in {bool, int, float, str}:
        return value
    if _seen is None:
        _seen = set()
    if isinstance(value, dict):
        value_id = id(value)
        if value_id in _seen:
            return "<cycle:dict>"
        _seen.add(value_id)
        try:
            return {
                _snapshot_contract_mapping_key(key, _seen): _snapshot_contract_value(item, _seen)
                for key, item in sorted(
                    value.items(),
                    key=lambda item: _snapshot_contract_mapping_key(item[0], _seen),
                )
            }
        finally:
            _seen.remove(value_id)
    if isinstance(value, list):
        value_id = id(value)
        if value_id in _seen:
            return "<cycle:list>"
        _seen.add(value_id)
        try:
            return [_snapshot_contract_value(item, _seen) for item in value]
        finally:
            _seen.remove(value_id)
    if isinstance(value, tuple):
        value_id = id(value)
        if value_id in _seen:
            return "<cycle:tuple>"
        _seen.add(value_id)
        try:
            return [_snapshot_contract_value(item, _seen) for item in value]
        finally:
            _seen.remove(value_id)
    if isinstance(value, Set):
        value_id = id(value)
        if value_id in _seen:
            return f"<cycle:{type(value).__name__}>"
        _seen.add(value_id)
        try:
            normalized_items = [_snapshot_contract_value(item, _seen) for item in value]
            return sorted(normalized_items, key=_canonical_json_sort_key)
        finally:
            _seen.remove(value_id)
    try:
        snapshot = copy.deepcopy(value)
    except Exception:
        return f"<non-json:{type(value).__name__}>"
    try:
        _canonical_json(snapshot)
    except (TypeError, ValueError):
        return f"<non-json:{type(value).__name__}>"
    return snapshot


def _snapshot_contract_mapping_key(key: Any, _seen: set[int]) -> str:
    if isinstance(key, str):
        return key
    key_snapshot = _snapshot_contract_value(key, _seen)
    try:
        key_preview = _canonical_json(key_snapshot)
    except (TypeError, ValueError):
        key_preview = f'"<non-json:{type(key).__name__}>"'
    return f"<key:{type(key).__name__}:{key_preview}>"


def _snapshot_contract_section(section: Any) -> Any:
    return _snapshot_contract_value(section)


def _snapshot_shell_ui_contract(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    from .shell import describe_shell_ui_contract

    return _snapshot_contract_section(
        describe_shell_ui_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
    )


def _a2ui_shell_ui_contract_manifest_fingerprint(
    shell_ui_contract: Mapping[str, Any],
    *,
    include_terminal_artifact_cli_fallback_route: bool,
    include_contract_aliases: bool,
) -> str:
    """Return the shell manifest fingerprint used by A2UI dispatch snapshots.

    When the A2UI dispatch snapshot opts into the route-aware shell contract
    and also expands contract aliases, keep the manifest fingerprint tied to
    the route-only shell contract. That preserves a stable shell-manifest
    hash for engine-facing dispatch consumers while still allowing the shell
    snapshot itself to expose alias-expanded fingerprints.
    """

    if include_terminal_artifact_cli_fallback_route and include_contract_aliases:
        from .shell import shell_ui_contract_fingerprint

        return shell_ui_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    fingerprint = shell_ui_contract.get("contract_fingerprint")
    if isinstance(fingerprint, str):
        return fingerprint
    from .shell import shell_ui_contract_fingerprint

    return shell_ui_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )


def _snapshot_terminal_artifact_cli_fallback_entrypoint_contract() -> dict[str, Any]:
    return _snapshot_contract_section(describe_terminal_artifact_cli_fallback_entrypoint_contract())


def _add_contract_alias_fingerprints(
    fingerprints: dict[str, str],
    *alias_fingerprints: tuple[str, str],
) -> None:
    """Add alias and alias_fingerprint entries for opt-in contract fingerprint maps."""

    for alias, fingerprint in alias_fingerprints:
        fingerprints[alias] = fingerprint
        fingerprint_alias = alias if alias.endswith("_fingerprint") else f"{alias}_fingerprint"
        fingerprints[fingerprint_alias] = fingerprint


def describe_a2ui_contract(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
    include_contract_fingerprints: bool = True,
) -> dict[str, Any]:
    """Return the stable, versioned A2UI contract manifest.

    The manifest is intentionally JSON-serializable so clients can fingerprint
    the contract they negotiated without having to mirror internal module state.
    Pass ``include_terminal_artifact_cli_fallback_entrypoint=True`` to opt into
    the explicit CLI fallback entrypoint contract slice without the full shell
    UI snapshot. That opt-in also exposes the renderer-entrypoints manifest
    alias so CLI consumers can recover the shared entrypoint map without
    depending on shell UI state.
    Pass ``include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True``
    to surface the CLI fallback card-hint recovery policy without pulling in
    the shell UI snapshot. Pass ``include_shell_ui_contract=True`` to opt into
    the CLI fallback adapter contract slice. The embedded shell snapshot is
    exposed with both ``shell_ui_contract_fingerprint`` and
    ``shell_ui_fingerprint`` aliases so callers can use the same naming as the
    shell contract itself. That opt-in also surfaces the explicit CLI fallback
    entrypoint aliases from the shell contract so engine-side payloads can
    negotiate the same renderer entrypoint name without depending on shell
    internals. The top-level manifest mirrors the shell contract alias set
    with ``shell_ui_contract_manifest`` and
    ``shell_ui_contract_manifest_fingerprint`` for consumers that prefer the
    shell-style manifest naming, and it also exposes
    ``terminal_artifact_renderer_entrypoints_contract_manifest`` for the
    renderer-entrypoints contract slice itself. The shared action/selection
    leaf bundle is also surfaced as ``leaf_contracts`` and
    ``leaf_contracts_contract_manifest`` so engine outputs can negotiate that
    stable contract slice without reassembling it from the separate leaf
    manifests.
    """

    manifest = _build_a2ui_contract_manifest(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
        include_contract_aliases=include_contract_aliases,
        include_contract_fingerprints=include_contract_fingerprints,
    )
    manifest["contract_fingerprint"] = a2ui_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
    )
    capabilities = _snapshot_contract_section(manifest["schemas"]["capabilities"])
    manifest["capabilities"] = capabilities
    manifest["capabilities_fingerprint"] = capabilities["contract_fingerprint"]
    manifest["capabilities_contract"] = _snapshot_contract_section(capabilities)
    manifest["capabilities_contract_fingerprint"] = manifest["capabilities_fingerprint"]
    card_contract = _snapshot_contract_section(manifest["schemas"]["card_contract"])
    manifest["card_contract"] = card_contract
    manifest["card_contract_fingerprint"] = card_contract["contract_fingerprint"]
    manifest["card_contract_manifest"] = _snapshot_contract_section(card_contract)
    manifest["card_contract_manifest_fingerprint"] = manifest["card_contract_fingerprint"]
    action_contract = _snapshot_contract_section(manifest["schemas"]["action"])
    manifest["action"] = action_contract
    manifest["action_fingerprint"] = action_contract["contract_fingerprint"]
    manifest["action_contract"] = _snapshot_contract_section(action_contract)
    manifest["action_contract_fingerprint"] = manifest["action_fingerprint"]
    manifest["action_contract_manifest"] = _snapshot_contract_section(action_contract)
    manifest["action_contract_manifest_fingerprint"] = manifest["action_fingerprint"]
    selection_contract = _snapshot_contract_section(manifest["schemas"]["selection"])
    manifest["selection"] = selection_contract
    manifest["selection_fingerprint"] = selection_contract["contract_fingerprint"]
    manifest["selection_contract"] = _snapshot_contract_section(selection_contract)
    manifest["selection_contract_fingerprint"] = manifest["selection_fingerprint"]
    manifest["selection_contract_manifest"] = _snapshot_contract_section(selection_contract)
    manifest["selection_contract_manifest_fingerprint"] = manifest["selection_fingerprint"]
    leaf_contracts = _snapshot_contract_section(manifest["schemas"]["leaf_contracts"])
    manifest["leaf_contracts"] = leaf_contracts
    manifest["leaf_contracts_fingerprint"] = leaf_contracts["contract_fingerprint"]
    manifest["leaf_contracts_contract"] = _snapshot_contract_section(leaf_contracts)
    manifest["leaf_contracts_contract_fingerprint"] = manifest["leaf_contracts_fingerprint"]
    manifest["leaf_contracts_contract_manifest"] = _snapshot_contract_section(leaf_contracts)
    manifest["leaf_contracts_contract_manifest_fingerprint"] = manifest["leaf_contracts_fingerprint"]
    manifest["leaf_contracts_manifest"] = _snapshot_contract_section(leaf_contracts)
    manifest["leaf_contracts_manifest_fingerprint"] = manifest["leaf_contracts_fingerprint"]
    terminal_artifact_contract = _snapshot_contract_section(manifest["terminal_artifact"])
    manifest["terminal_artifact_contract"] = _snapshot_contract_section(terminal_artifact_contract)
    manifest["terminal_artifact_contract_fingerprint"] = terminal_artifact_contract["contract_fingerprint"]
    terminal_artifact_supported_kinds = list(terminal_artifact_contract["supported_kinds"])
    manifest["terminal_artifact_supported_kinds"] = terminal_artifact_supported_kinds
    manifest["terminal_artifact_supported_kinds_contract"] = _snapshot_contract_section(
        terminal_artifact_supported_kinds
    )
    manifest["terminal_artifact_supported_kinds_fingerprint"] = _fingerprint_manifest_section(
        terminal_artifact_supported_kinds
    )
    manifest["terminal_artifact_supported_kinds_contract_fingerprint"] = manifest[
        "terminal_artifact_supported_kinds_fingerprint"
    ]
    manifest["card_fingerprint"] = card_contract_fingerprint()
    schema_versions = _snapshot_contract_section(
        _build_a2ui_schema_versions_manifest(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    )
    manifest["schema_versions"] = schema_versions
    manifest["schema_versions_contract"] = _snapshot_contract_section(schema_versions)
    manifest["schema_versions_fingerprint"] = _fingerprint_manifest_section(schema_versions)
    manifest["schema_versions_contract_fingerprint"] = manifest["schema_versions_fingerprint"]
    terminal_artifact_rendering = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_rendering"]
    )
    manifest["terminal_artifact_rendering"] = terminal_artifact_rendering
    manifest["terminal_artifact_rendering_fingerprint"] = terminal_artifact_rendering["contract_fingerprint"]
    terminal_artifact_render_target = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_render_target"]
    )
    manifest["terminal_artifact_render_target"] = terminal_artifact_render_target
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target[
        "contract_fingerprint"
    ]
    renderer_entrypoints = _snapshot_contract_section(manifest["schemas"]["terminal_artifact"]["renderer_entrypoints"])
    manifest["renderer_entrypoints"] = renderer_entrypoints
    manifest["renderer_entrypoints_fingerprint"] = _fingerprint_manifest_section(renderer_entrypoints)
    renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    manifest["renderer_entrypoints_contract"] = _snapshot_contract_section(renderer_entrypoints_contract)
    manifest["renderer_entrypoints_contract_fingerprint"] = renderer_entrypoints_contract["contract_fingerprint"]
    terminal_artifact_cli_fallback = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_cli_fallback"]
    )
    manifest["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback
    manifest["terminal_artifact_cli_fallback_fingerprint"] = terminal_artifact_cli_fallback[
        "contract_fingerprint"
    ]
    terminal_artifact_cli_fallback_payload = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_cli_fallback_payload"]
    )
    manifest["terminal_artifact_cli_fallback_payload"] = terminal_artifact_cli_fallback_payload
    manifest["terminal_artifact_cli_fallback_payload_fingerprint"] = (
        terminal_artifact_cli_fallback_payload["contract_fingerprint"]
    )
    manifest["terminal_artifact_cli_fallback_payload_contract"] = _snapshot_contract_section(
        terminal_artifact_cli_fallback_payload
    )
    manifest["terminal_artifact_cli_fallback_payload_contract_fingerprint"] = (
        manifest["terminal_artifact_cli_fallback_payload_fingerprint"]
    )
    manifest["terminal_artifact_cli_fallback_payload_contract_manifest"] = _snapshot_contract_section(
        terminal_artifact_cli_fallback_payload
    )
    manifest["terminal_artifact_cli_fallback_payload_contract_manifest_fingerprint"] = (
        manifest["terminal_artifact_cli_fallback_payload_fingerprint"]
    )
    terminal_artifact_cli_fallback_target = _snapshot_contract_section(
        manifest["schemas"]["terminal_artifact_cli_fallback_target"]
    )
    manifest["terminal_artifact_cli_fallback_target"] = terminal_artifact_cli_fallback_target
    manifest["terminal_artifact_cli_fallback_target_fingerprint"] = terminal_artifact_cli_fallback_target[
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_cli_fallback_target_contract"] = _snapshot_contract_section(
        terminal_artifact_cli_fallback_target
    )
    manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"] = manifest[
        "terminal_artifact_cli_fallback_target_fingerprint"
    ]
    manifest["terminal_artifact_cli_fallback_target_contract_manifest"] = (
        describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    )
    manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"] = manifest[
        "terminal_artifact_cli_fallback_target_fingerprint"
    ]
    if include_terminal_artifact_cli_fallback_route:
        terminal_artifact_cli_fallback_route = dict(manifest["terminal_artifact_cli_fallback_route"])
        manifest["terminal_artifact_cli_fallback_route"] = terminal_artifact_cli_fallback_route
        manifest["terminal_artifact_cli_fallback_route_contract"] = dict(terminal_artifact_cli_fallback_route)
        manifest["terminal_artifact_cli_fallback_route_fingerprint"] = terminal_artifact_cli_fallback_route[
            "contract_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = manifest[
            "terminal_artifact_cli_fallback_route_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_route["contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints"] = copy.deepcopy(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_route["contract_fingerprints_fingerprint"]
        )
    terminal_artifact_contract = _snapshot_contract_section(manifest["schemas"]["terminal_artifact"])
    manifest["terminal_artifact"] = terminal_artifact_contract
    manifest["terminal_artifact_contract"] = _snapshot_contract_section(terminal_artifact_contract)
    manifest["terminal_artifact_contract_fingerprint"] = manifest["terminal_artifact_fingerprint"]
    terminal_artifact_allowed_actions = list(terminal_artifact_contract["allowed_actions"])
    manifest["terminal_artifact_allowed_actions"] = terminal_artifact_allowed_actions
    manifest["terminal_artifact_allowed_actions_fingerprint"] = _fingerprint_manifest_section(
        terminal_artifact_allowed_actions
    )
    manifest["terminal_artifact_allowed_actions_contract"] = _snapshot_contract_section(
        terminal_artifact_allowed_actions
    )
    manifest["terminal_artifact_allowed_actions_contract_fingerprint"] = manifest[
        "terminal_artifact_allowed_actions_fingerprint"
    ]
    manifest["terminal_artifact_allowed_actions_contract_manifest"] = _snapshot_contract_section(
        terminal_artifact_allowed_actions
    )
    manifest["terminal_artifact_allowed_actions_contract_manifest_fingerprint"] = manifest[
        "terminal_artifact_allowed_actions_fingerprint"
    ]
    renderer_entrypoints = _snapshot_contract_section(terminal_artifact_contract["renderer_entrypoints"])
    manifest["renderer_entrypoints"] = renderer_entrypoints
    manifest["renderer_entrypoints_fingerprint"] = _fingerprint_manifest_section(renderer_entrypoints)
    renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    manifest["renderer_entrypoints_contract"] = _snapshot_contract_section(renderer_entrypoints_contract)
    manifest["renderer_entrypoints_contract_fingerprint"] = renderer_entrypoints_contract["contract_fingerprint"]
    manifest["terminal_artifact_render_target_contract"] = _snapshot_contract_section(
        terminal_artifact_render_target
    )
    manifest["terminal_artifact_render_target_contract_fingerprint"] = manifest["terminal_artifact_render_target_fingerprint"]
    manifest["terminal_fallback"] = _snapshot_contract_section(manifest["terminal_fallback"])
    manifest["terminal_fallback_contract"] = _snapshot_contract_section(manifest["terminal_fallback"])
    manifest["terminal_fallback_contract_fingerprint"] = manifest["terminal_fallback_fingerprint"]
    terminal_artifact_raw_leaf_card_default = _snapshot_contract_section(
        terminal_artifact_contract["raw_leaf_card_default_contract"]
    )
    manifest["terminal_artifact_raw_leaf_card_default"] = terminal_artifact_raw_leaf_card_default
    manifest["terminal_artifact_raw_leaf_card_default_fingerprint"] = terminal_artifact_raw_leaf_card_default[
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprints"] = _snapshot_contract_section(
        terminal_artifact_contract["raw_leaf_card_default_contract_fingerprints"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprints_fingerprint"] = _fingerprint_manifest_section(
        manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprints"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_contract"] = _snapshot_contract_section(
        terminal_artifact_raw_leaf_card_default
    )
    manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprint"] = manifest[
        "terminal_artifact_raw_leaf_card_default_fingerprint"
    ]
    terminal_artifact_raw_leaf_card_default_policy = _snapshot_contract_section(
        terminal_artifact_contract["terminal_artifact_raw_leaf_card_default_policy"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy"] = terminal_artifact_raw_leaf_card_default_policy
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = (
        terminal_artifact_raw_leaf_card_default_policy["contract_fingerprint"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract"] = _snapshot_contract_section(
        terminal_artifact_raw_leaf_card_default_policy
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"] = (
        manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints"] = _snapshot_contract_section(
        describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
            include_terminal_artifact_raw_leaf_card_default_policy=True,
        )
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints_fingerprint"] = (
        _fingerprint_manifest_section(manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints"])
    )
    terminal_artifact_envelope = _snapshot_contract_section(terminal_artifact_contract["terminal_artifact_envelope_contract"])
    manifest["terminal_artifact_envelope"] = terminal_artifact_envelope
    manifest["terminal_artifact_envelope_contract"] = _snapshot_contract_section(terminal_artifact_envelope)
    manifest["terminal_artifact_envelope_fingerprint"] = terminal_artifact_envelope["contract_fingerprint"]
    manifest["terminal_artifact_envelope_contract_fingerprint"] = manifest["terminal_artifact_envelope_fingerprint"]
    terminal_artifact_kind_contracts = _snapshot_contract_section(
        terminal_artifact_contract["terminal_artifact_kind_contracts"]
    )
    manifest["terminal_artifact_kind_contracts"] = _snapshot_contract_section(terminal_artifact_kind_contracts)
    manifest["terminal_artifact_kind_contracts_fingerprint"] = terminal_artifact_contract[
        "terminal_artifact_kind_contracts_fingerprint"
    ]
    manifest["terminal_artifact_rendering_contract"] = _snapshot_contract_section(terminal_artifact_rendering)
    manifest["terminal_artifact_rendering_contract_fingerprint"] = manifest["terminal_artifact_rendering_fingerprint"]
    manifest["terminal_artifact_cli_fallback_contract"] = _snapshot_contract_section(
        terminal_artifact_cli_fallback
    )
    manifest["terminal_artifact_cli_fallback_contract_fingerprint"] = manifest[
        "terminal_artifact_cli_fallback_fingerprint"
    ]
    if include_terminal_artifact_cli_fallback_entrypoint:
        manifest["terminal_artifact_cli_fallback_contract_manifest"] = _snapshot_contract_section(
            manifest["terminal_artifact_cli_fallback_contract"]
        )
        manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"] = manifest[
            "terminal_artifact_cli_fallback_contract_fingerprint"
        ]
    manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprints"] = copy.deepcopy(
        terminal_artifact_cli_fallback["contract_fingerprints"]
    )
    manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprints_fingerprint"] = (
        _fingerprint_manifest_section(manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprints"])
    )
    manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"] = _snapshot_contract_section(
        terminal_artifact_contract["terminal_artifact_cli_fallback_target_contract_fingerprints"]
    )
    manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"] = (
        _fingerprint_manifest_section(manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"])
    )
    if include_terminal_artifact_cli_fallback_route:
        # Keep the route contract opt-in so the default A2UI manifest stays
        # focused on the stable CLI fallback contract slice.
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        manifest["terminal_artifact_cli_fallback_route"] = dict(route_contract)
        manifest["terminal_artifact_cli_fallback_route_contract"] = dict(route_contract)
        manifest["terminal_artifact_cli_fallback_route_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = manifest[
            "terminal_artifact_cli_fallback_route_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
            route_contract["contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = route_contract[
            "contract_fingerprints_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints"] = copy.deepcopy(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint"] = route_contract[
            "contract_fingerprints_fingerprint"
        ]
    if include_contract_fingerprints:
        manifest["contract_fingerprints"] = _snapshot_a2ui_contract_fingerprints(
            _build_a2ui_contract_fingerprint_summary(
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
                include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
                include_shell_ui_contract=include_shell_ui_contract,
                include_contract_aliases=include_contract_aliases,
            )
        )
        manifest["contract_fingerprints_fingerprint"] = _fingerprint_manifest_section(
            manifest["contract_fingerprints"]
        )
        manifest["contract_fingerprints_contract"] = _snapshot_contract_section(
            manifest["contract_fingerprints"]
        )
        manifest["contract_fingerprints_contract_fingerprint"] = manifest["contract_fingerprints_fingerprint"]
    manifest["a2ui_contract_version"] = A2UI_CONTRACT_VERSION
    a2ui_contract_alias = {
        "a2ui_contract_version": A2UI_CONTRACT_VERSION,
        "contract_fingerprint": manifest["contract_fingerprint"],
        "capabilities": _snapshot_contract_section(manifest["capabilities"]),
    }
    if include_contract_fingerprints:
        a2ui_contract_alias["contract_fingerprints"] = _snapshot_a2ui_contract_fingerprints(
            manifest["contract_fingerprints"]
        )
    manifest["a2ui_contract"] = a2ui_contract_alias
    manifest["a2ui_contract_fingerprint"] = manifest["contract_fingerprint"]
    return manifest


def _canonicalize_capabilities(capabilities: A2UICapabilities) -> A2UICapabilities:
    """Snapshot a validated handshake into immutable, canonical fields.

    ``validate_capabilities`` accepts either lists or tuples so callers can
    build the payload naturally, but the session store should retain a stable
    immutable copy once the handshake is negotiated. Supported sequences are
    reordered into the contract's canonical sequence so equivalent handshakes
    collapse to the same stored snapshot.
    """

    return A2UICapabilities(
        a2ui_version=capabilities.a2ui_version,
        client_name=capabilities.client_name.strip(),
        cards_supported=_canonicalize_supported_sequence(
            capabilities.cards_supported,
            canonical_order=_SPECIALIZED_CARD_TYPES,
        ),
        primitive_blocks_supported=_canonicalize_supported_sequence(
            capabilities.primitive_blocks_supported,
            canonical_order=REQUIRED_PRIMITIVE_BLOCKS,
        ),
        actions_supported=_canonicalize_supported_sequence(
            capabilities.actions_supported,
            canonical_order=ALLOWED_ACTION_IDS,
        ),
        max_payload_bytes=capabilities.max_payload_bytes,
        supports_streaming=capabilities.supports_streaming,
    )


def normalize_capabilities(capabilities: A2UICapabilities) -> A2UICapabilities:
    """Return the canonical, immutable snapshot for an A2UI capability handshake."""

    validate_capabilities(capabilities)
    return _canonicalize_capabilities(capabilities)


@lru_cache(maxsize=None)
def _describe_a2ui_contract_fingerprints_cached(
    include_terminal_artifact: bool = False,
    include_action: bool = False,
    include_terminal_artifact_render_target: bool = False,
    include_terminal_artifact_rendering: bool = False,
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_target: bool = False,
    include_terminal_artifact_raw_leaf_card_default: bool = False,
    include_terminal_artifact_raw_leaf_card_default_policy: bool = False,
    include_contract_aliases: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
) -> dict[str, Any]:
    """Return stable fingerprints for the contract sections and embedded contracts.

    The default key set stays lean for existing callers while still exposing
    the shared leaf bundle fingerprint and the raw-leaf card-default recovery
    contract that engine consumers need. Opt-in flags expose the embedded
    dispatch fingerprints and contract aliases that the full manifest already
    surfaces so lightweight callers can negotiate the same contract slice
    without pulling the entire manifest. The top-level `contract_fingerprint`
    alias is included only when alias expansion is requested, mirroring the
    manifest surface. Pass
    ``include_terminal_artifact_cli_fallback_entrypoint=True`` to expose the
    explicit CLI fallback entrypoint contract slice without pulling in the
    shell UI snapshot. Pass
    ``include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True``
    to expose the CLI fallback card-hint policy without pulling in the shell
    UI snapshot. Pass
    ``include_shell_ui_contract=True`` to opt into the shell adapter contract
    fingerprint used by the CLI fallback path. That opt-in also exposes the
    canonical ``shell_ui_contract_fingerprint``, ``shell_ui_fingerprint``,
    and ``shell_ui_contract_fingerprints_fingerprint`` keys so the fingerprint
    map mirrors the embedded shell manifest more closely. Because the shell
    snapshot always carries the CLI fallback route slice, that opt-in also
    surfaces the route fingerprint aliases for the embedded fallback route
    contract and the explicit CLI fallback entrypoint aliases used by the
    shell adapter, plus the card-hint recovery policy aliases for callers that
    prefer the shell-shaped surface, plus
    ``terminal_artifact_renderer_entrypoints_contract_manifest`` for the
    renderer-entrypoints contract slice itself.
    """

    fingerprints = {
        "contract": a2ui_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
            include_shell_ui_contract=include_shell_ui_contract,
        ),
        "capabilities": a2ui_capabilities_contract_fingerprint(),
        "cards": _fingerprint_manifest_section(
            {
                "generic": GENERIC_CARD_TYPE,
                "unknown": UNKNOWN_CARD_TYPE,
                "reserved": list(_RESERVED_CARD_TYPES),
                "specialized": list(_SPECIALIZED_CARD_TYPES),
            }
        ),
        "fallbacks": _fingerprint_manifest_section(_build_card_fallback_manifest()),
        "leaf_contracts": a2ui_leaf_contracts_fingerprint(),
        "selection": selection_contract_fingerprint(),
        "primitive_blocks": _fingerprint_manifest_section(
            [
                {
                    "type": block_type,
                    "fields": list(_PRIMITIVE_BLOCK_SCHEMAS[block_type]),
                }
                for block_type in REQUIRED_PRIMITIVE_BLOCKS
            ]
        ),
        "actions": _fingerprint_manifest_section(
            [
                {
                    "id": action_id,
                    "version": A2UI_ACTION_SCHEMA_VERSION,
                    "payload_fields": sorted(schema),
                }
                for action_id, schema in sorted(_ACTION_SCHEMAS.items())
            ]
        ),
        "schemas": _fingerprint_manifest_section(
            _build_a2ui_schema_versions_manifest(
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            )
        ),
        "card_contract": card_contract_fingerprint(),
        "terminal_fallback": terminal_fallback_contract_fingerprint(),
    }
    card_hint_recovery_policy_contract_fingerprint_value = _fingerprint_manifest_section(
        _build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest()
    )
    if include_action:
        fingerprints["action"] = action_contract_fingerprint()
    if include_terminal_artifact:
        terminal_artifact_supported_kinds_fingerprint = _fingerprint_manifest_section(
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)
        )
        fingerprints["terminal_artifact"] = terminal_artifact_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
        fingerprints["terminal_artifact_supported_kinds"] = terminal_artifact_supported_kinds_fingerprint
        fingerprints["terminal_artifact_allowed_actions"] = _fingerprint_manifest_section(
            sorted(ALLOWED_ACTION_IDS)
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_supported_kinds_contract",
                terminal_artifact_supported_kinds_fingerprint,
            ),
            (
                "terminal_artifact_supported_kinds_contract_fingerprint",
                terminal_artifact_supported_kinds_fingerprint,
            ),
            (
                "terminal_artifact_allowed_actions_contract",
                _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
            ),
            (
                "terminal_artifact_allowed_actions_contract_manifest",
                _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
            ),
        )
    if include_terminal_artifact_render_target:
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
    if include_terminal_artifact_rendering:
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
    if include_terminal_artifact_cli_fallback:
        terminal_artifact_cli_fallback_fingerprint_value = terminal_artifact_cli_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_fingerprint_value
        fingerprints["terminal_artifact_cli_fallback_fingerprint"] = terminal_artifact_cli_fallback_fingerprint_value
        fingerprints["terminal_artifact_cli_fallback_contract"] = terminal_artifact_cli_fallback_fingerprint_value
        fingerprints["terminal_artifact_cli_fallback_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_contract_manifest"] = (
            terminal_artifact_cli_fallback_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_fingerprint_value
        )
    if (
        include_terminal_artifact_cli_fallback
        or include_terminal_artifact_cli_fallback_entrypoint
        or include_terminal_artifact_cli_fallback_card_hint_recovery_policy
        or include_shell_ui_contract
    ):
        fingerprints["card_hint_recovery_policy"] = card_hint_recovery_policy_contract_fingerprint_value
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "card_hint_recovery_policy_contract",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
            (
                "card_hint_recovery_policy_contract_manifest",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
        )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            ("action_contract", action_contract_fingerprint()),
            ("action_contract_manifest", action_contract_fingerprint()),
            ("selection_contract", selection_contract_fingerprint()),
            ("selection_contract_manifest", selection_contract_fingerprint()),
            ("card_contract_manifest", card_contract_fingerprint()),
            ("terminal_fallback_contract_manifest", terminal_fallback_contract_fingerprint()),
            ("terminal_artifact_allowed_actions", _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS))),
            (
                "terminal_artifact_allowed_actions_contract",
                _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
            ),
            (
                "terminal_artifact_allowed_actions_contract_manifest",
                _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
            ),
            (
                "terminal_artifact_renderer_entrypoints_contract",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
            (
                "terminal_artifact_renderer_entrypoints_contract_manifest",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
        )
    if include_terminal_artifact_cli_fallback_target:
        terminal_artifact_cli_fallback_target_fingerprint_value = (
            terminal_artifact_cli_fallback_target_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_target_fingerprint"] = (
            terminal_artifact_cli_fallback_target_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract"] = (
            terminal_artifact_cli_fallback_target_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_target_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"] = (
            terminal_artifact_cli_fallback_target_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_target_fingerprint_value
        )
    if include_terminal_artifact_cli_fallback_route:
        terminal_artifact_cli_fallback_route_contract_fingerprint_value = (
            terminal_artifact_cli_fallback_route_contract_fingerprint()
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_route",
                terminal_artifact_cli_fallback_route_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_route_contract",
                terminal_artifact_cli_fallback_route_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_route_contract_manifest",
                terminal_artifact_cli_fallback_route_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_route_contract_fingerprints",
                terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
            ),
        )
    if include_terminal_artifact_cli_fallback_entrypoint:
        terminal_artifact_cli_fallback_entrypoint_contract = _snapshot_terminal_artifact_cli_fallback_entrypoint_contract()
        terminal_artifact_renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
        terminal_artifact_cli_fallback_contract_fingerprint_value = terminal_artifact_cli_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback_entrypoint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract["terminal_artifact_cli_fallback_entrypoint_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_entrypoint_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract["terminal_artifact_cli_fallback_entrypoint_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_contract_fingerprint_value
        fingerprints["terminal_artifact_cli_fallback_fingerprint"] = (
            terminal_artifact_cli_fallback_contract_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_contract"] = (
            terminal_artifact_cli_fallback_contract_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_contract_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_contract_manifest"] = (
            terminal_artifact_cli_fallback_contract_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_contract_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"] = (
            terminal_artifact_cli_fallback_entrypoint_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"] = (
            terminal_artifact_cli_fallback_entrypoint_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"
            ]
        )
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"
            ]
        )
        fingerprints["terminal_artifact_renderer_entrypoints_contract"] = (
            terminal_artifact_renderer_entrypoints_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_renderer_entrypoints_contract_fingerprint"] = (
            terminal_artifact_renderer_entrypoints_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"] = (
            terminal_artifact_renderer_entrypoints_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"] = (
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        )
        terminal_artifact_cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
        fingerprints["terminal_artifact_cli_fallback_target"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_target_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        fingerprints["shell_refinement_policy"] = terminal_artifact_cli_fallback_entrypoint_contract[
            "terminal_artifact_cli_fallback_shell_refinement_policy_fingerprint"
        ]
        fingerprints["shell_refinement_policy_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_shell_refinement_policy_fingerprint"
            ]
        )
        fingerprints["shell_refinement_policy_contract"] = terminal_artifact_cli_fallback_entrypoint_contract[
            "terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint"
        ]
        fingerprints["shell_refinement_policy_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint"
            ]
        )
        fingerprints["shell_refinement_policy_contract_manifest"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest_fingerprint"
            ]
        )
        fingerprints["shell_refinement_policy_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest_fingerprint"
            ]
        )
        fingerprints["resolver_failure_policy"] = terminal_artifact_cli_fallback_entrypoint_contract[
            "terminal_artifact_cli_fallback_resolver_failure_policy_fingerprint"
        ]
        fingerprints["resolver_failure_policy_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_resolver_failure_policy_fingerprint"
            ]
        )
        fingerprints["resolver_failure_policy_contract"] = terminal_artifact_cli_fallback_entrypoint_contract[
            "terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint"
        ]
        fingerprints["resolver_failure_policy_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint"
            ]
        )
        fingerprints["resolver_failure_policy_contract_manifest"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint"
            ]
        )
        fingerprints["resolver_failure_policy_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint"
            ]
        )
        fingerprints["card_hint_recovery_policy"] = card_hint_recovery_policy_contract_fingerprint_value
    if include_terminal_artifact_raw_leaf_card_default:
        fingerprints["terminal_artifact_raw_leaf_card_default"] = (
            terminal_artifact_raw_leaf_card_default_contract_fingerprint()
        )
    if include_terminal_artifact_raw_leaf_card_default_policy:
        fingerprints["terminal_artifact_raw_leaf_card_default_policy"] = (
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
        )
    if include_shell_ui_contract:
        from .shell import describe_shell_ui_contract_fingerprints, shell_ui_contract_fingerprint

        shell_ui_contract_fingerprints = describe_shell_ui_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        shell_ui_contract_fingerprint_value = shell_ui_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
        shell_ui_contract_manifest_fingerprint = shell_ui_contract_fingerprint_value
        if include_terminal_artifact_cli_fallback_route and include_contract_aliases:
            shell_ui_contract_manifest_fingerprint = shell_ui_contract_fingerprint(
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            )
        shell_ui_contract_fingerprints_fingerprint = _fingerprint_manifest_section(shell_ui_contract_fingerprints)
        fingerprints["shell_ui_contract"] = shell_ui_contract_fingerprint_value
        fingerprints["shell_ui_contract_fingerprint"] = shell_ui_contract_fingerprint_value
        fingerprints["shell_ui_fingerprint"] = shell_ui_contract_fingerprint_value
        fingerprints["shell_ui_contract_fingerprints"] = shell_ui_contract_fingerprints_fingerprint
        fingerprints["shell_ui_contract_fingerprints_fingerprint"] = shell_ui_contract_fingerprints_fingerprint
        fingerprints["shell_ui_contract_manifest_fingerprints"] = shell_ui_contract_fingerprints_fingerprint
        fingerprints["shell_ui_contract_manifest_fingerprints_fingerprint"] = (
            shell_ui_contract_fingerprints_fingerprint
        )
        fingerprints["shell_ui_contract_manifest"] = shell_ui_contract_manifest_fingerprint
        fingerprints["shell_ui_contract_manifest_fingerprint"] = shell_ui_contract_manifest_fingerprint
        fingerprints["card_hint_recovery_policy"] = card_hint_recovery_policy_contract_fingerprint_value
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "card_hint_recovery_policy_contract",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
            (
                "card_hint_recovery_policy_contract_manifest",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
        )
        # Mirror the shell entrypoint bundle as well so shell-aware engine
        # consumers can fingerprint the explicit CLI fallback entrypoint
        # without opting into the standalone slice separately.
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_entrypoint",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            ),
        )
        if include_contract_aliases:
            _add_contract_alias_fingerprints(
                fingerprints,
                (
                    "terminal_artifact_cli_fallback_contract_manifest",
                    shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_contract_manifest"],
                ),
            )
        fingerprints["terminal_artifact_renderer_entrypoints"] = shell_ui_contract_fingerprints[
            "terminal_artifact_renderer_entrypoints_contract_fingerprint"
        ]
        fingerprints["terminal_artifact_renderer_entrypoints_contract"] = shell_ui_contract_fingerprints[
            "terminal_artifact_renderer_entrypoints_contract_fingerprint"
        ]
        terminal_artifact_renderer_entrypoints_contract_fingerprint_value = (
            terminal_artifact_renderer_entrypoints_contract_fingerprint()
        )
        fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"] = (
            terminal_artifact_renderer_entrypoints_contract_fingerprint_value
        )
        fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"] = (
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "renderer_entrypoints_contract_manifest",
                terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
            ),
        )
        # Surface the target-selection manifest alongside the shell snapshot so
        # engine consumers can fingerprint the exact CLI fallback policy without
        # reaching back through shell internals.
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_target_contract_manifest",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            ),
        )
        fingerprints["terminal_artifact_cli_fallback_route"] = route_contract["contract_fingerprint"]
        fingerprints["terminal_artifact_cli_fallback_route_contract"] = route_contract["contract_fingerprint"]
        fingerprints["terminal_artifact_cli_fallback_route_fingerprint"] = route_contract["contract_fingerprint"]
        fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprint"] = route_contract["contract_fingerprint"]
        fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"] = route_contract["contract_fingerprint"]
        fingerprints["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"] = route_contract[
            "contract_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"] = route_contract[
            "contract_fingerprints_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = route_contract[
            "contract_fingerprints_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_entrypoint"] = shell_ui_contract_fingerprints[
            "terminal_artifact_cli_fallback_entrypoint_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_entrypoint_fingerprint"] = shell_ui_contract_fingerprints[
            "terminal_artifact_cli_fallback_entrypoint_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"] = shell_ui_contract_fingerprints[
            "terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"] = shell_ui_contract_fingerprints[
            "terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"] = shell_ui_contract_fingerprints[
            "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"
        ]
        fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"] = (
            shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"]
        )
        terminal_artifact_cli_fallback_contract_fingerprint_value = terminal_artifact_cli_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback_contract_manifest"] = (
            terminal_artifact_cli_fallback_contract_fingerprint_value
        )
        fingerprints["terminal_artifact_cli_fallback_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_contract_fingerprint_value
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
            ),
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_route",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_route"],
            ),
            (
                "terminal_artifact_cli_fallback_route_contract",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_route_contract"],
            ),
            (
                "terminal_artifact_cli_fallback_route_contract_manifest",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            ),
            (
                "terminal_artifact_cli_fallback_route_contract_fingerprints",
                shell_ui_contract_fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            ),
        )
    if include_contract_aliases:
        engine_contract_fingerprint_value = a2ui_engine_contract_fingerprint(
            include_shell_ui_contract=include_shell_ui_contract,
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "a2ui_contract",
                a2ui_contract_fingerprint(
                    include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                    include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
                    include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
                    include_shell_ui_contract=include_shell_ui_contract,
                ),
            ),
            ("a2ui_engine_contract", engine_contract_fingerprint_value),
            ("a2ui_engine_contract_manifest", engine_contract_fingerprint_value),
            (
                "contract_fingerprint",
                a2ui_contract_fingerprint(
                    include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                    include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
                    include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
                    include_shell_ui_contract=include_shell_ui_contract,
                ),
            ),
            ("capabilities_contract", a2ui_capabilities_contract_fingerprint()),
            ("card_fingerprint", card_contract_fingerprint()),
            ("card_contract_fingerprint", card_contract_fingerprint()),
            ("leaf_contracts_contract", a2ui_leaf_contracts_fingerprint()),
            ("leaf_contracts_contract_manifest", a2ui_leaf_contracts_fingerprint()),
            ("leaf_contracts_manifest", a2ui_leaf_contracts_fingerprint()),
            ("action_contract", action_contract_fingerprint()),
            ("selection_contract", selection_contract_fingerprint()),
            ("terminal_fallback_contract", terminal_fallback_contract_fingerprint()),
            ("terminal_artifact_kind_contracts", terminal_artifact_kind_contracts_fingerprint()),
            ("terminal_artifact_contract", terminal_artifact_contract_fingerprint()),
            ("terminal_artifact_envelope", terminal_artifact_envelope_contract_fingerprint()),
            ("terminal_artifact_envelope_contract", terminal_artifact_envelope_contract_fingerprint()),
            ("terminal_artifact_render_target", terminal_artifact_render_target_contract_fingerprint()),
            ("terminal_artifact_rendering", terminal_artifact_rendering_contract_fingerprint()),
            ("terminal_artifact_cli_fallback", terminal_artifact_cli_fallback_contract_fingerprint()),
            (
                "terminal_artifact_cli_fallback_payload",
                terminal_artifact_cli_fallback_payload_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_payload_contract",
                terminal_artifact_cli_fallback_payload_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_payload_contract_manifest",
                terminal_artifact_cli_fallback_payload_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
            ),
            (
                "card_hint_recovery_policy_contract",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
            (
                "card_hint_recovery_policy_contract_manifest",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_renderer_entrypoints",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
            ("renderer_entrypoints", terminal_artifact_renderer_entrypoints_contract_fingerprint()),
            (
                "renderer_entrypoints_contract",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
            (
                "terminal_artifact_renderer_entrypoints_contract_manifest",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_render_target_contract",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_render_target_contract_manifest",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            ("terminal_artifact_rendering_contract", terminal_artifact_rendering_contract_fingerprint()),
            (
                "terminal_artifact_rendering_contract_manifest",
                terminal_artifact_rendering_contract_fingerprint(),
            ),
            ("terminal_artifact_cli_fallback_contract", terminal_artifact_cli_fallback_contract_fingerprint()),
            (
                "terminal_artifact_cli_fallback_target_contract",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract_manifest",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract_fingerprints",
                _fingerprint_manifest_section(describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints()),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract_fingerprints_fingerprint",
                _fingerprint_manifest_section(describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints()),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract_fingerprints",
                terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(
                    include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                ),
            ),
        )
        if include_shell_ui_contract:
            _add_contract_alias_fingerprints(
                fingerprints,
                ("shell_ui_contract", fingerprints["shell_ui_contract"]),
                ("shell_ui_contract_fingerprint", fingerprints["shell_ui_contract_fingerprint"]),
            )
        if include_terminal_artifact_cli_fallback_route:
            _add_contract_alias_fingerprints(
                fingerprints,
                (
                    "terminal_artifact_cli_fallback_route",
                    terminal_artifact_cli_fallback_route_contract_fingerprint(),
                ),
                (
                    "terminal_artifact_cli_fallback_route_contract",
                    terminal_artifact_cli_fallback_route_contract_fingerprint(),
                ),
                (
                    "terminal_artifact_cli_fallback_route_contract_fingerprints",
                    _fingerprint_manifest_section(
                        _build_terminal_artifact_cli_fallback_route_contract_fingerprints(),
                    ),
                ),
            )
        fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"] = (
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                include_contract_aliases=True,
            )
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            )
        )
    return fingerprints


def describe_a2ui_contract_fingerprints(
    include_terminal_artifact: bool = False,
    include_action: bool = False,
    include_terminal_artifact_render_target: bool = False,
    include_terminal_artifact_rendering: bool = False,
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_target: bool = False,
    include_terminal_artifact_raw_leaf_card_default: bool = False,
    include_terminal_artifact_raw_leaf_card_default_policy: bool = False,
    include_contract_aliases: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
) -> dict[str, Any]:
    """Return stable fingerprints for the contract sections and embedded contracts.

    The public helper returns a fresh snapshot so callers cannot mutate the
    cached fingerprint map that backs contract negotiation.
    """

    return _snapshot_a2ui_contract_fingerprints(
        _describe_a2ui_contract_fingerprints_cached(
            include_terminal_artifact=include_terminal_artifact,
            include_action=include_action,
            include_terminal_artifact_render_target=include_terminal_artifact_render_target,
            include_terminal_artifact_rendering=include_terminal_artifact_rendering,
            include_terminal_artifact_cli_fallback=include_terminal_artifact_cli_fallback,
            include_terminal_artifact_cli_fallback_target=include_terminal_artifact_cli_fallback_target,
            include_terminal_artifact_raw_leaf_card_default=include_terminal_artifact_raw_leaf_card_default,
            include_terminal_artifact_raw_leaf_card_default_policy=include_terminal_artifact_raw_leaf_card_default_policy,
            include_contract_aliases=include_contract_aliases,
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
            include_shell_ui_contract=include_shell_ui_contract,
        )
    )


def _build_a2ui_contract_fingerprint_summary(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    return _snapshot_a2ui_contract_fingerprints(
        _describe_a2ui_contract_fingerprints_cached(
            include_terminal_artifact=True,
            include_action=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_target=True,
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
            include_shell_ui_contract=include_shell_ui_contract,
            include_contract_aliases=include_contract_aliases,
        )
    )


def _snapshot_a2ui_contract_fingerprints(fingerprints: Mapping[str, Any]) -> dict[str, Any]:
    return _snapshot_contract_section(fingerprints)


def _build_a2ui_schema_versions_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "type": "A2UISchemaVersions",
        "capabilities_schema_version": A2UI_CAPABILITIES_SCHEMA_VERSION,
        "selection_schema_version": SELECTION_SCHEMA_VERSION,
        "selection_contract_version": SELECTION_SCHEMA_VERSION,
        "action_schema_version": A2UI_ACTION_SCHEMA_VERSION,
        "action_contract_version": A2UI_ACTION_SCHEMA_VERSION,
        "card_contract_version": CARD_CONTRACT_VERSION,
        "terminal_fallback_schema_version": TERMINAL_FALLBACK_SCHEMA_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_render_target_schema_version": TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
        "terminal_artifact_renderer_entrypoints_schema_version": (
            TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION
        ),
        "terminal_artifact_rendering_schema_version": TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_payload_schema_version": (
            TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_SCHEMA_VERSION
        ),
        "terminal_artifact_cli_fallback_entrypoint_schema_version": (
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION
        ),
        "terminal_artifact_cli_fallback_target_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_schema_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
    }
    if include_terminal_artifact_cli_fallback_route:
        manifest["terminal_artifact_cli_fallback_route_schema_version"] = (
            TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION
        )
    return manifest


def describe_a2ui_dispatch_contract_fingerprints(
    *,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    """Return the full route-aware A2UI dispatch fingerprint summary.

    Pass ``include_terminal_artifact_cli_fallback_entrypoint=True`` to include
    the explicit CLI fallback entrypoint slice without the shell snapshot.
    Pass ``include_contract_aliases=True`` to expose the same self-describing
    alias keys that the base A2UI fingerprint helper already supports.
    """

    return describe_a2ui_contract_fingerprints(
        include_action=True,
        include_terminal_artifact=True,
        include_terminal_artifact_render_target=True,
        include_terminal_artifact_rendering=True,
        include_terminal_artifact_cli_fallback=True,
        include_terminal_artifact_cli_fallback_target=True,
        include_terminal_artifact_cli_fallback_route=True,
        include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
        include_contract_aliases=include_contract_aliases,
    )


def describe_a2ui_dispatch_contract(
    *,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    """Return the full route-aware A2UI dispatch manifest.

    This wrapper keeps the engine-facing dispatch surface explicit: it always
    includes the terminal artifact, render-target, rendering, CLI fallback,
    target-selection, route, and CLI fallback entrypoint slices that the
    engine loop needs while leaving the shell UI snapshot opt-in. Pass
    ``include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True``
    to expose the standalone card-hint recovery policy slice too.
    """

    manifest = describe_a2ui_contract(
        include_terminal_artifact_cli_fallback_route=True,
        include_terminal_artifact_cli_fallback_entrypoint=True,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
        include_contract_aliases=include_contract_aliases,
    )
    dispatch_contract_fingerprints = describe_a2ui_dispatch_contract_fingerprints(
        include_terminal_artifact_cli_fallback_entrypoint=True,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
        include_contract_aliases=include_contract_aliases,
    )
    dispatch_contract_fingerprints = _snapshot_a2ui_contract_fingerprints(dispatch_contract_fingerprints)
    manifest["dispatch_contract_fingerprints"] = dispatch_contract_fingerprints
    manifest["dispatch_contract_fingerprints_fingerprint"] = _fingerprint_manifest_section(
        dispatch_contract_fingerprints
    )
    manifest["dispatch_contract_fingerprint"] = a2ui_dispatch_contract_fingerprint(
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
        include_contract_aliases=include_contract_aliases,
    )
    return manifest


def a2ui_dispatch_contract_fingerprint(
    *,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
) -> str:
    """Return a stable fingerprint for the full A2UI dispatch manifest."""

    return _fingerprint_manifest_section(
        _build_a2ui_contract_manifest(
            include_terminal_artifact_cli_fallback_route=True,
            include_terminal_artifact_cli_fallback_entrypoint=True,
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
            include_shell_ui_contract=include_shell_ui_contract,
            include_contract_aliases=include_contract_aliases,
            include_contract_fingerprints=False,
        )
    )


@lru_cache(maxsize=None)
def _describe_selection_contract_manifest() -> dict[str, Any]:
    manifest = _build_selection_contract_manifest()
    fingerprint = selection_contract_fingerprint()
    manifest["selection_fingerprint"] = fingerprint
    manifest["selection_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["contract_manifest_fingerprint"] = fingerprint
    return manifest


def describe_selection_contract() -> dict[str, Any]:
    """Return the stable, versioned SelectionRef contract manifest."""

    return _snapshot_contract_section(_describe_selection_contract_manifest())


def describe_selection_contract_manifest() -> dict[str, Any]:
    """Return the stable SelectionRef contract manifest alias."""

    return describe_selection_contract()


@lru_cache(maxsize=None)
def _describe_action_contract_manifest() -> dict[str, Any]:
    manifest = _build_action_contract_manifest()
    fingerprint = action_contract_fingerprint()
    manifest["action_fingerprint"] = fingerprint
    manifest["action_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["contract_manifest_fingerprint"] = fingerprint
    return manifest


def describe_action_contract() -> dict[str, Any]:
    """Return the stable, versioned ActionRef contract manifest."""

    return _snapshot_contract_section(_describe_action_contract_manifest())


def describe_action_contract_manifest() -> dict[str, Any]:
    """Return the stable ActionRef contract manifest alias."""

    return describe_action_contract()


@lru_cache(maxsize=None)
def _describe_card_contract_manifest() -> dict[str, Any]:
    manifest = _build_card_contract_manifest()
    fingerprint = card_contract_fingerprint()
    manifest["card_fingerprint"] = fingerprint
    manifest["card_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["contract_manifest_fingerprint"] = fingerprint
    return manifest


def describe_card_contract() -> dict[str, Any]:
    """Return the stable, versioned card contract manifest."""

    return _snapshot_contract_section(_describe_card_contract_manifest())


def describe_card_contract_manifest() -> dict[str, Any]:
    """Return the stable card contract manifest alias."""

    return describe_card_contract()


@lru_cache(maxsize=None)
def _describe_a2ui_leaf_contracts_manifest() -> dict[str, Any]:
    manifest = _snapshot_contract_section(_build_a2ui_leaf_contracts_manifest())
    fingerprint = a2ui_leaf_contracts_fingerprint()
    manifest["action_fingerprint"] = manifest["action"]["contract_fingerprint"]
    manifest["action_contract_fingerprint"] = manifest["action_fingerprint"]
    manifest["action_contract_manifest"] = _snapshot_contract_section(manifest["action"])
    manifest["action_contract_manifest_fingerprint"] = manifest["action_fingerprint"]
    manifest["selection_fingerprint"] = manifest["selection"]["contract_fingerprint"]
    manifest["selection_contract_fingerprint"] = manifest["selection_fingerprint"]
    manifest["selection_contract_manifest"] = _snapshot_contract_section(manifest["selection"])
    manifest["selection_contract_manifest_fingerprint"] = manifest["selection_fingerprint"]
    manifest["leaf_contracts_fingerprint"] = fingerprint
    manifest["leaf_contracts_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["leaf_contracts_contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["leaf_contracts_contract_manifest_fingerprint"] = fingerprint
    manifest["leaf_contracts_manifest"] = _snapshot_contract_section(manifest)
    manifest["leaf_contracts_manifest_fingerprint"] = fingerprint
    return manifest


def describe_a2ui_leaf_contracts() -> dict[str, Any]:
    """Return the stable shared ActionRef and SelectionRef contract bundle."""

    return _snapshot_contract_section(_describe_a2ui_leaf_contracts_manifest())


def describe_a2ui_capabilities_contract() -> dict[str, Any]:
    """Return the stable, versioned A2UI capabilities handshake manifest."""

    manifest = _build_a2ui_capabilities_contract_manifest()
    fingerprint = a2ui_capabilities_contract_fingerprint()
    manifest["capabilities_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_fallback_contract() -> dict[str, Any]:
    """Return the stable terminal fallback contract manifest."""

    manifest = _build_terminal_fallback_contract_manifest()
    fingerprint = terminal_fallback_contract_fingerprint()
    manifest["terminal_fallback_fingerprint"] = fingerprint
    manifest["terminal_fallback_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["contract_manifest_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_raw_leaf_card_default_contract() -> dict[str, Any]:
    """Return the stable raw-leaf card default contract manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_contract_manifest()
    fingerprint = terminal_artifact_raw_leaf_card_default_contract_fingerprint()
    manifest["raw_leaf_card_default_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_contract_fingerprints"] = describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints()
    return manifest


def describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
    include_terminal_artifact_raw_leaf_card_default_policy: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the raw-leaf card-default policy contract section."""

    return _build_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
        include_terminal_artifact_raw_leaf_card_default_policy=include_terminal_artifact_raw_leaf_card_default_policy,
    )


def describe_terminal_artifact_raw_leaf_card_default_policy_contract() -> dict[str, Any]:
    """Return the stable raw-leaf card default policy contract manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_policy_contract_manifest()
    fingerprint = terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
    manifest["raw_leaf_card_default_policy_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_policy_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_policy_contract_fingerprints"] = (
        describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints()
    )
    return manifest


def describe_terminal_artifact_envelope_contract() -> dict[str, Any]:
    """Return the stable TerminalArtifact envelope contract manifest."""

    manifest = _build_terminal_artifact_envelope_manifest()
    fingerprint = terminal_artifact_envelope_contract_fingerprint()
    manifest["terminal_artifact_envelope_fingerprint"] = fingerprint
    manifest["terminal_artifact_envelope_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(
    include_terminal_artifact_raw_leaf_card_default: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the raw-leaf card-default contract section."""

    return _build_terminal_artifact_raw_leaf_card_default_contract_fingerprints(
        include_terminal_artifact_raw_leaf_card_default=include_terminal_artifact_raw_leaf_card_default,
    )


def describe_terminal_artifact_contract(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the stable terminal artifact dispatch contract manifest."""

    manifest = _build_terminal_artifact_contract_manifest(
        include_contract_fingerprints=False,
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    fingerprint = terminal_artifact_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    manifest["terminal_artifact_fingerprint"] = fingerprint
    manifest["terminal_artifact_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target"] = _snapshot_contract_section(
        manifest["render_target_contract"]
    )
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target_contract_fingerprint()
    manifest["allowed_actions_fingerprint"] = _fingerprint_manifest_section(manifest["allowed_actions"])
    manifest["allowed_actions_contract"] = _snapshot_contract_section(manifest["allowed_actions"])
    manifest["allowed_actions_contract_fingerprint"] = manifest["allowed_actions_fingerprint"]
    manifest["allowed_actions_contract_manifest"] = _snapshot_contract_section(manifest["allowed_actions"])
    manifest["allowed_actions_contract_manifest_fingerprint"] = manifest["allowed_actions_fingerprint"]
    contract_fingerprints = describe_terminal_artifact_contract_fingerprints(
        include_terminal_artifact=True,
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    manifest["contract_fingerprints"] = _snapshot_contract_section(contract_fingerprints)
    manifest["contract_fingerprints_fingerprint"] = _fingerprint_manifest_section(contract_fingerprints)
    manifest["contract_fingerprints_contract"] = _snapshot_contract_section(manifest["contract_fingerprints"])
    manifest["contract_fingerprints_contract_fingerprint"] = manifest["contract_fingerprints_fingerprint"]
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    terminal_artifact_raw_leaf_card_default_policy = _snapshot_contract_section(
        manifest["terminal_artifact_raw_leaf_card_default_policy_contract"]
    )
    manifest["terminal_artifact_raw_leaf_card_default_policy"] = terminal_artifact_raw_leaf_card_default_policy
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = (
        terminal_artifact_raw_leaf_card_default_policy["contract_fingerprint"]
    )
    terminal_artifact_envelope = _snapshot_contract_section(manifest["envelope"])
    manifest["terminal_artifact_envelope"] = terminal_artifact_envelope
    manifest["terminal_artifact_envelope_contract"] = _snapshot_contract_section(terminal_artifact_envelope)
    manifest["terminal_artifact_envelope_fingerprint"] = terminal_artifact_envelope["contract_fingerprint"]
    manifest["terminal_artifact_envelope_contract_fingerprint"] = manifest["terminal_artifact_envelope_fingerprint"]
    manifest["terminal_artifact_kind_contracts"] = _snapshot_contract_section(manifest["kind_contracts"])
    manifest["terminal_artifact_kind_contracts_fingerprint"] = terminal_artifact_kind_contracts_fingerprint()
    card_contract = _snapshot_contract_section(manifest["kind_contracts"]["card"])
    action_contract = _snapshot_contract_section(manifest["kind_contracts"]["action"])
    selection_contract = _snapshot_contract_section(manifest["kind_contracts"]["selection"])
    manifest["card_contract"] = card_contract
    manifest["action_contract"] = action_contract
    manifest["selection_contract"] = selection_contract
    manifest["card_contract_fingerprint"] = card_contract["contract_fingerprint"]
    manifest["action_contract_fingerprint"] = action_contract["contract_fingerprint"]
    manifest["selection_contract_fingerprint"] = selection_contract["contract_fingerprint"]
    renderer_entrypoints = _snapshot_contract_section(
        manifest["terminal_artifact_cli_fallback_target_contract"]["renderer_entrypoints"]
    )
    manifest["renderer_entrypoints"] = renderer_entrypoints
    manifest["renderer_entrypoints_fingerprint"] = _fingerprint_manifest_section(renderer_entrypoints)
    renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    manifest["renderer_entrypoints_contract"] = _snapshot_contract_section(renderer_entrypoints_contract)
    manifest["renderer_entrypoints_contract_fingerprint"] = renderer_entrypoints_contract["contract_fingerprint"]
    if include_terminal_artifact_cli_fallback_route and "terminal_artifact_cli_fallback_route" in manifest:
        terminal_artifact_cli_fallback_route = _snapshot_contract_section(
            manifest["terminal_artifact_cli_fallback_route"]
        )
        manifest["terminal_artifact_cli_fallback_route"] = terminal_artifact_cli_fallback_route
        manifest["terminal_artifact_cli_fallback_route_contract"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_route
        )
        manifest["terminal_artifact_cli_fallback_route_fingerprint"] = terminal_artifact_cli_fallback_route[
            "contract_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = manifest[
            "terminal_artifact_cli_fallback_route_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_route["contract_fingerprints"]
        )
    return manifest


def describe_terminal_artifact_render_target_contract() -> dict[str, Any]:
    """Return the stable terminal artifact render-target contract manifest."""

    manifest = _build_terminal_artifact_render_target_contract_manifest()
    fingerprint = terminal_artifact_render_target_contract_fingerprint()
    manifest["terminal_artifact_render_target_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target_contract"] = _snapshot_contract_section(manifest)
    manifest["terminal_artifact_render_target_contract_manifest"] = _snapshot_contract_section(
        manifest["terminal_artifact_render_target_contract"]
    )
    manifest["terminal_artifact_render_target_contract_manifest_fingerprint"] = fingerprint
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    manifest["raw_leaf_card_default_policy_contract_fingerprint"] = manifest["raw_leaf_card_default_policy_contract"][
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    return manifest


def describe_terminal_artifact_render_target_contract_manifest() -> dict[str, Any]:
    """Return the render-target contract under a manifest-specific name."""

    return describe_terminal_artifact_render_target_contract()


def describe_terminal_artifact_render_target_contract_fingerprints(
    include_terminal_artifact_render_target: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the render-target contract sections.

    Pass ``include_terminal_artifact_render_target=True`` to include the
    wrapper contract fingerprint itself alongside the nested section
    fingerprints. Pass ``include_contract_aliases=True`` to include alias keys
    that mirror the manifest field names.
    """

    fingerprints = _build_terminal_artifact_render_target_contract_fingerprints(
        include_terminal_artifact_render_target=include_terminal_artifact_render_target,
    )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            ("terminal_artifact_kind_contracts", terminal_artifact_kind_contracts_fingerprint()),
            ("terminal_artifact_render_target", terminal_artifact_render_target_contract_fingerprint()),
            (
                "terminal_artifact_render_target_contract",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_render_target_contract_manifest",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            ("terminal_fallback_contract", terminal_fallback_contract_fingerprint()),
            ("raw_leaf_card_default_contract", terminal_artifact_raw_leaf_card_default_contract_fingerprint()),
            (
                "raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            ("terminal_fallback_fingerprint", terminal_fallback_contract_fingerprint()),
            ("raw_leaf_card_default_fingerprint", terminal_artifact_raw_leaf_card_default_contract_fingerprint()),
            (
                "raw_leaf_card_default_policy_fingerprint",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
        )
    return fingerprints


def describe_terminal_artifact_kind_resolution_contract() -> dict[str, Any]:
    """Return the stable terminal-artifact kind-resolution contract section."""

    manifest = _build_terminal_artifact_kind_resolution_manifest()
    fingerprint = terminal_artifact_kind_resolution_fingerprint()
    manifest["kind_resolution_fingerprint"] = fingerprint
    manifest["kind_resolution_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_fallback_recovery_contract() -> dict[str, Any]:
    """Return the stable terminal-artifact fallback-recovery contract section."""

    manifest = _build_terminal_artifact_fallback_recovery_manifest()
    fingerprint = terminal_artifact_fallback_recovery_fingerprint()
    manifest["fallback_recovery_fingerprint"] = fingerprint
    manifest["fallback_recovery_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_rendering_contract() -> dict[str, Any]:
    """Return the stable terminal artifact rendering contract manifest."""

    manifest = _build_terminal_artifact_rendering_contract_manifest()
    fingerprint = terminal_artifact_rendering_contract_fingerprint()
    manifest["terminal_artifact_rendering_fingerprint"] = fingerprint
    manifest["terminal_artifact_rendering_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_rendering"] = _snapshot_contract_section(manifest)
    manifest["terminal_artifact_rendering_contract"] = _snapshot_contract_section(
        manifest["terminal_artifact_rendering"]
    )
    manifest["terminal_artifact_rendering_contract_manifest"] = _snapshot_contract_section(
        manifest["terminal_artifact_rendering_contract"]
    )
    manifest["terminal_artifact_rendering_contract_manifest_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target"] = manifest["render_target_contract"]
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target_contract_fingerprint()
    manifest["terminal_artifact_render_target_contract"] = _snapshot_contract_section(
        manifest["render_target_contract"]
    )
    manifest["terminal_artifact_render_target_contract_fingerprint"] = (
        terminal_artifact_render_target_contract_fingerprint()
    )
    manifest["renderer_entrypoints_fingerprint"] = _fingerprint_manifest_section(manifest["renderer_entrypoints"])
    renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    manifest["renderer_entrypoints_contract"] = _snapshot_contract_section(renderer_entrypoints_contract)
    manifest["renderer_entrypoints_contract_fingerprint"] = renderer_entrypoints_contract["contract_fingerprint"]
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    manifest["raw_leaf_card_default_policy_contract_fingerprint"] = manifest["raw_leaf_card_default_policy_contract"][
        "contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"] = manifest[
        "raw_leaf_card_default_policy_contract_fingerprint"
    ]
    manifest["terminal_fallback_contract_fingerprint"] = manifest["terminal_fallback_contract"][
        "contract_fingerprint"
    ]
    return manifest


def describe_terminal_artifact_rendering_contract_manifest() -> dict[str, Any]:
    """Return the rendering contract under a manifest-specific name."""

    return describe_terminal_artifact_rendering_contract()


def describe_terminal_artifact_renderer_entrypoints_contract() -> dict[str, Any]:
    """Return the stable terminal artifact renderer-entrypoints contract manifest."""

    manifest = _build_terminal_artifact_renderer_entrypoints_contract_manifest()
    fingerprint = terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
    manifest["renderer_entrypoints_contract"] = _snapshot_contract_section(manifest["renderer_entrypoints"])
    manifest["renderer_entrypoints_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprints"] = describe_terminal_artifact_renderer_entrypoints_contract_fingerprints()
    manifest["contract_fingerprints_fingerprint"] = _fingerprint_manifest_section(
        manifest["contract_fingerprints"]
    )
    manifest["contract_fingerprint"] = fingerprint
    manifest["renderer_entrypoints_contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["renderer_entrypoints_contract_manifest_fingerprint"] = fingerprint
    manifest["terminal_artifact_renderer_entrypoints_contract"] = _snapshot_contract_section(manifest)
    manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_renderer_entrypoints_contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_renderer_entrypoints_contract_manifest() -> dict[str, Any]:
    """Return the renderer-entrypoints manifest under a manifest-specific name."""

    return describe_terminal_artifact_renderer_entrypoints_contract()


@lru_cache(maxsize=None)
def describe_terminal_artifact_renderer_entrypoints_contract_fingerprints(
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the renderer-entrypoints contract slice.

    Pass ``include_contract_aliases=True`` to add self-describing aliases for
    the manifest name and its fingerprint.
    """

    fingerprints = _build_terminal_artifact_renderer_entrypoints_contract_fingerprints(
        include_contract_aliases=include_contract_aliases,
    )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "renderer_entrypoints_contract_manifest",
                fingerprints["renderer_entrypoints_contract"],
            ),
        )
    return fingerprints


def describe_terminal_artifact_cli_fallback_entrypoint_contract() -> dict[str, Any]:
    """Return the stable explicit CLI fallback entrypoint contract manifest."""

    manifest = _build_terminal_artifact_cli_fallback_entrypoint_contract_manifest()
    contract_fingerprint = terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
    manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"] = contract_fingerprint
    manifest["contract_fingerprint"] = contract_fingerprint
    manifest["contract_fingerprints_fingerprint"] = _fingerprint_manifest_section(
        manifest["contract_fingerprints"]
    )
    manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"] = _snapshot_contract_section(
        manifest
    )
    manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"] = contract_fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"]
    )
    manifest["contract_manifest_fingerprint"] = contract_fingerprint
    manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"] = (
        manifest["contract_fingerprints_fingerprint"]
    )
    return manifest


def describe_terminal_artifact_cli_fallback_entrypoint_contract_manifest() -> dict[str, Any]:
    """Return the explicit CLI fallback entrypoint contract under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_entrypoint_contract()


def describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract() -> dict[str, Any]:
    """Return the stable shell refinement policy used by the CLI fallback path."""

    manifest = _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()
    fingerprint = terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint()
    manifest["shell_refinement_policy_fingerprint"] = fingerprint
    manifest["shell_refinement_policy_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint() -> str:
    """Return a stable fingerprint for the shell refinement policy contract."""

    return _fingerprint_manifest_section(_build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest())


def describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract() -> dict[str, Any]:
    """Return the stable resolver failure policy used by the CLI fallback path."""

    manifest = _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
    fingerprint = terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint()
    manifest["resolver_failure_policy_fingerprint"] = fingerprint
    manifest["resolver_failure_policy_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest() -> dict[str, Any]:
    """Return the resolver failure policy under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract()


def describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract() -> dict[str, Any]:
    """Return the stable card-hint recovery policy used by the CLI fallback path."""

    manifest = _build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest()
    fingerprint = terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint()
    manifest["card_hint_recovery_policy_fingerprint"] = fingerprint
    manifest["card_hint_recovery_policy_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_manifest() -> dict[str, Any]:
    """Return the card-hint recovery policy under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()


def terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint() -> str:
    """Return a stable fingerprint for the resolver failure policy contract."""

    return _fingerprint_manifest_section(_build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest())


def terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint() -> str:
    """Return the resolver failure policy manifest fingerprint under a manifest-specific name."""

    return terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint()


def terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint() -> str:
    """Return a stable fingerprint for the card-hint recovery policy contract."""

    return _fingerprint_manifest_section(_build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest())


def terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_manifest_fingerprint() -> str:
    """Return the card-hint recovery policy manifest fingerprint under a manifest-specific name."""

    return terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint()


def terminal_artifact_cli_fallback_entrypoint_contract_fingerprint() -> str:
    """Return a stable fingerprint for the explicit CLI fallback entrypoint manifest."""

    manifest = _build_terminal_artifact_cli_fallback_entrypoint_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint() -> str:
    """Return the explicit CLI fallback entrypoint manifest fingerprint under a manifest-specific name."""

    return terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()


def describe_terminal_artifact_rendering_contract_fingerprints(
    include_terminal_artifact_rendering: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the rendering-contract sections.

    Pass ``include_terminal_artifact_rendering=True`` to include the wrapper
    contract fingerprint itself alongside the nested section fingerprints.
    Pass ``include_contract_aliases=True`` to include alias keys that mirror
    the manifest field names.
    """

    fingerprints = _build_terminal_artifact_rendering_contract_fingerprints(
        include_terminal_artifact_rendering=include_terminal_artifact_rendering,
    )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            ("terminal_artifact_kind_contracts", terminal_artifact_kind_contracts_fingerprint()),
            ("terminal_artifact_rendering", terminal_artifact_rendering_contract_fingerprint()),
            (
                "terminal_artifact_render_target_contract",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            ("terminal_artifact_render_target", terminal_artifact_render_target_contract_fingerprint()),
            ("terminal_artifact_rendering_contract", terminal_artifact_rendering_contract_fingerprint()),
            (
                "terminal_artifact_rendering_contract_manifest",
                terminal_artifact_rendering_contract_fingerprint(),
            ),
            (
                "renderer_entrypoints_contract",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            ("terminal_fallback_contract", terminal_fallback_contract_fingerprint()),
            ("raw_leaf_card_default_contract", terminal_artifact_raw_leaf_card_default_contract_fingerprint()),
            (
                "raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            ("terminal_fallback_fingerprint", terminal_fallback_contract_fingerprint()),
            ("raw_leaf_card_default_fingerprint", terminal_artifact_raw_leaf_card_default_contract_fingerprint()),
            (
                "raw_leaf_card_default_policy_fingerprint",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
        )
    return fingerprints


def describe_terminal_artifact_cli_fallback_contract(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the stable CLI fallback wrapper contract manifest."""

    manifest = _build_terminal_artifact_cli_fallback_contract_manifest(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    fingerprint = terminal_artifact_cli_fallback_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    manifest["terminal_artifact_cli_fallback_fingerprint"] = fingerprint
    manifest["terminal_artifact_cli_fallback_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"] = fingerprint
    manifest["terminal_artifact_render_target"] = manifest["render_target_contract"]
    manifest["terminal_artifact_render_target_fingerprint"] = terminal_artifact_render_target_contract_fingerprint()
    manifest["terminal_artifact_render_target_contract"] = _snapshot_contract_section(
        manifest["render_target_contract"]
    )
    manifest["terminal_artifact_render_target_contract_fingerprint"] = (
        terminal_artifact_render_target_contract_fingerprint()
    )
    manifest["contract_manifest"] = dict(manifest["terminal_artifact_cli_fallback_contract_manifest"])
    manifest["contract_manifest_fingerprint"] = fingerprint
    manifest["allowed_actions_fingerprint"] = _fingerprint_manifest_section(manifest["allowed_actions"])
    manifest["renderer_entrypoints_fingerprint"] = _fingerprint_manifest_section(manifest["renderer_entrypoints"])
    renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    manifest["renderer_entrypoints_contract"] = _snapshot_contract_section(renderer_entrypoints_contract)
    manifest["renderer_entrypoints_contract_fingerprint"] = renderer_entrypoints_contract["contract_fingerprint"]
    manifest["kind_policy_fingerprint"] = _fingerprint_manifest_section(manifest["kind_policy"])
    manifest["kind_policy_contract"] = _snapshot_contract_section(manifest["kind_policy"])
    manifest["kind_policy_contract_fingerprint"] = manifest["kind_policy_fingerprint"]
    manifest["kind_policy_contract_manifest"] = _snapshot_contract_section(manifest["kind_policy"])
    manifest["kind_policy_contract_manifest_fingerprint"] = manifest["kind_policy_fingerprint"]
    manifest["terminal_fallback_contract_fingerprint"] = manifest["terminal_fallback_contract"][
        "contract_fingerprint"
    ]
    manifest["raw_leaf_card_default_contract_fingerprint"] = manifest["raw_leaf_card_default_contract"][
        "contract_fingerprint"
    ]
    return manifest


def describe_terminal_artifact_cli_fallback_contract_manifest(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the CLI fallback wrapper contract under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )


def describe_terminal_artifact_cli_fallback_contract_manifest_fingerprints(
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return the CLI fallback wrapper fingerprints under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_contract_fingerprints(
        include_terminal_artifact_cli_fallback=include_terminal_artifact_cli_fallback,
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )


def describe_terminal_artifact_cli_fallback_target_contract(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the stable CLI fallback target-selection contract manifest."""

    manifest = _build_terminal_artifact_cli_fallback_target_contract_manifest(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    fingerprint = terminal_artifact_cli_fallback_target_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    manifest["terminal_artifact_cli_fallback_target_fingerprint"] = fingerprint
    manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"] = fingerprint
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_fingerprints"] = describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints"] = copy.deepcopy(
        manifest["contract_fingerprints"]
    )
    manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint"] = (
        _fingerprint_manifest_section(manifest["contract_fingerprints"])
    )
    manifest["renderer_entrypoints_fingerprint"] = _fingerprint_manifest_section(
        manifest["renderer_entrypoints"]
    )
    renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    manifest["renderer_entrypoints_contract"] = _snapshot_contract_section(renderer_entrypoints_contract)
    manifest["renderer_entrypoints_contract_fingerprint"] = renderer_entrypoints_contract["contract_fingerprint"]
    manifest["terminal_artifact_renderer_entrypoints_contract_manifest"] = _snapshot_contract_section(
        renderer_entrypoints_contract
    )
    manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"] = (
        terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
    )
    manifest["leaf_renderers_fingerprint"] = _fingerprint_manifest_section(manifest["leaf_renderers"])
    manifest["leaf_renderers_contract_fingerprint"] = manifest["leaf_renderers_fingerprint"]
    manifest["leaf_renderers_contract"] = _snapshot_contract_section(manifest["leaf_renderers"])
    manifest["leaf_renderers_contract_manifest"] = _snapshot_contract_section(manifest["leaf_renderers"])
    manifest["leaf_renderers_contract_manifest_fingerprint"] = manifest["leaf_renderers_fingerprint"]
    manifest["terminal_artifact_cli_fallback_target_contract_manifest"] = dict(manifest)
    manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"] = fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(
        manifest["terminal_artifact_cli_fallback_target_contract_manifest"]
    )
    manifest["contract_manifest_fingerprint"] = fingerprint
    manifest["contract_manifest_fingerprints"] = copy.deepcopy(
        manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints"]
    )
    manifest["contract_manifest_fingerprints_fingerprint"] = (
        manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint"]
    )
    return manifest


def describe_terminal_artifact_cli_fallback_target_contract_manifest(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the CLI fallback target contract under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_target_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )


def describe_terminal_artifact_cli_fallback_target_contract_manifest_fingerprints(
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return the CLI fallback target fingerprints under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_contract_aliases=include_contract_aliases,
    )


def _build_terminal_artifact_cli_fallback_route_contract() -> dict[str, Any]:
    """Return the stable CLI fallback route contract manifest."""

    manifest = _build_terminal_artifact_cli_fallback_route_contract_manifest()
    fingerprint = terminal_artifact_cli_fallback_route_contract_fingerprint()
    manifest["terminal_artifact_cli_fallback_route_fingerprint"] = fingerprint
    manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = fingerprint
    manifest["route_precedence_contract_fingerprint"] = _fingerprint_manifest_section(
        manifest["route_precedence"]
    )
    manifest["leaf_renderers_contract_fingerprint"] = _fingerprint_manifest_section(manifest["leaf_renderers"])
    manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = manifest[
        "contract_fingerprints_fingerprint"
    ]
    manifest["route_precedence_fingerprint"] = manifest["route_precedence_contract_fingerprint"]
    manifest["leaf_renderers_fingerprint"] = manifest["leaf_renderers_contract_fingerprint"]
    manifest["route_precedence_contract"] = _snapshot_contract_section(manifest["route_precedence"])
    manifest["leaf_renderers_contract"] = _snapshot_contract_section(manifest["leaf_renderers"])
    manifest["contract_fingerprint"] = fingerprint
    manifest["terminal_artifact_cli_fallback_route_contract_manifest"] = copy.deepcopy(manifest)
    manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"] = fingerprint
    manifest["contract_manifest"] = copy.deepcopy(
        manifest["terminal_artifact_cli_fallback_route_contract_manifest"]
    )
    manifest["contract_manifest_fingerprint"] = fingerprint
    return manifest


@lru_cache(maxsize=None)
def _terminal_artifact_cli_fallback_route_contract_snapshot() -> tuple[tuple[str, Any], ...]:
    return tuple(_build_terminal_artifact_cli_fallback_route_contract().items())


def describe_terminal_artifact_cli_fallback_route_contract() -> dict[str, Any]:
    """Return the stable CLI fallback route contract manifest."""

    return copy.deepcopy(dict(_terminal_artifact_cli_fallback_route_contract_snapshot()))


def describe_terminal_artifact_cli_fallback_route_contract_manifest() -> dict[str, Any]:
    """Return the CLI fallback route contract under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_route_contract()


def describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints(
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return the CLI fallback route fingerprints under a manifest-specific name."""

    return describe_terminal_artifact_cli_fallback_route_contract_fingerprints(
        include_contract_aliases=include_contract_aliases,
    )


def describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
    include_terminal_artifact_cli_fallback_target: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the CLI fallback target-selection contract.

    The default key set stays focused on the shared render-target and raw-leaf
    recovery contracts plus the shared action/selection leaf bundle and the
    explicit CLI fallback entrypoint manifest the target contract negotiates
    directly. Opt in to include the wrapper contract fingerprint or alias keys
    when a caller needs the full negotiated contract slice.
    """

    fingerprints = _build_terminal_artifact_cli_fallback_target_contract_fingerprints(
        include_terminal_artifact_cli_fallback_target=include_terminal_artifact_cli_fallback_target,
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            ("contract_manifest", terminal_artifact_cli_fallback_target_contract_fingerprint()),
            ("contract_manifest_fingerprint", terminal_artifact_cli_fallback_target_contract_fingerprint()),
            (
                "terminal_artifact_cli_fallback_entrypoint",
                _fingerprint_manifest_section("render_terminal_cli_fallback"),
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract",
                _fingerprint_manifest_section("render_terminal_cli_fallback"),
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
            ),
            ("terminal_artifact_render_target", terminal_artifact_render_target_contract_fingerprint()),
            (
                "terminal_artifact_render_target_contract",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_render_target_contract_manifest",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract_manifest",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract_fingerprints",
                terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(
                    include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                ),
            ),
            (
                "renderer_entrypoints_contract",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
        )
    if include_terminal_artifact_cli_fallback_route:
        terminal_artifact_cli_fallback_route_contract_fingerprint_value = (
            terminal_artifact_cli_fallback_route_contract_fingerprint()
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_route",
                terminal_artifact_cli_fallback_route_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_route_contract",
                terminal_artifact_cli_fallback_route_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_route_contract_fingerprints",
                terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
            )
        )
    return fingerprints


def terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return a stable fingerprint for the CLI fallback target fingerprint map."""

    fingerprints = describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    return _fingerprint_manifest_section(fingerprints)


def terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return the CLI fallback target fingerprint-map fingerprint under a manifest-specific name."""

    return terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )


@lru_cache(maxsize=None)
def terminal_artifact_cli_fallback_route_contract_fingerprint() -> str:
    """Return a stable fingerprint for the CLI fallback route manifest."""

    manifest = _build_terminal_artifact_cli_fallback_route_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_cli_fallback_route_contract_manifest_fingerprint() -> str:
    """Return the CLI fallback route manifest fingerprint under a manifest-specific name."""

    return terminal_artifact_cli_fallback_route_contract_fingerprint()


def terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint(
    include_contract_aliases: bool = False,
) -> str:
    """Return the CLI fallback route fingerprint map under a manifest-specific name."""

    return _fingerprint_manifest_section(
        describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints(
            include_contract_aliases=include_contract_aliases,
        )
    )


def terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint() -> str:
    """Return a stable fingerprint for the CLI fallback route fingerprint map."""

    fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints()
    return _fingerprint_manifest_section(fingerprints)


def describe_terminal_artifact_kind_contracts() -> dict[str, dict[str, str]]:
    """Return the stable kind contract map shared by terminal artifact manifests."""

    return _build_terminal_artifact_kind_contracts()


def _build_terminal_artifact_kind_contracts_manifest() -> dict[str, Any]:
    kind_contracts = _build_terminal_artifact_kind_contracts()
    kind_contracts_fingerprint = terminal_artifact_kind_contracts_fingerprint()
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_kind_contracts_schema_version": TERMINAL_ARTIFACT_KIND_CONTRACTS_SCHEMA_VERSION,
        "terminal_artifact_kind_contracts_version": TERMINAL_ARTIFACT_KIND_CONTRACTS_SCHEMA_VERSION,
        "type": "TerminalArtifactKindContractsContract",
        "kind_contracts": _snapshot_contract_section(kind_contracts),
        "terminal_artifact_kind_contracts": _snapshot_contract_section(kind_contracts),
        "kind_contracts_fingerprint": kind_contracts_fingerprint,
        "terminal_artifact_kind_contracts_fingerprint": kind_contracts_fingerprint,
        "contract_fingerprints": {
            "kind_contracts": kind_contracts_fingerprint,
        },
    }


def describe_terminal_artifact_kind_contracts_manifest() -> dict[str, Any]:
    """Return the versioned manifest wrapper for the shared kind contracts."""

    manifest = _build_terminal_artifact_kind_contracts_manifest()
    fingerprint = terminal_artifact_kind_contracts_manifest_fingerprint()
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["contract_manifest_fingerprint"] = fingerprint
    return manifest


def describe_terminal_artifact_contract_fingerprints(
    include_terminal_artifact: bool = False,
    include_kind_contracts: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the terminal artifact contract and subcontracts.

    Pass ``include_contract_aliases=True`` to include alias keys that mirror
    the manifest field names. Pass
    ``include_terminal_artifact_cli_fallback_route=True`` to include the CLI
    fallback route contract fingerprint itself alongside the terminal artifact
    dispatch contract fingerprints.
    """

    fingerprints = {
        "card_contract": card_contract_fingerprint(),
        "action_contract": action_contract_fingerprint(),
        "selection_contract": selection_contract_fingerprint(),
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
        "cli_fallback_contract": terminal_artifact_cli_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "allowed_actions": _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
    }
    card_contract_fingerprint_value = fingerprints["card_contract"]
    action_contract_fingerprint_value = fingerprints["action_contract"]
    selection_contract_fingerprint_value = fingerprints["selection_contract"]
    terminal_artifact_kind_contracts_fingerprint_value = terminal_artifact_kind_contracts_fingerprint()
    terminal_artifact_contract_fingerprint_value = terminal_artifact_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    terminal_artifact_envelope_contract_fingerprint_value = terminal_artifact_envelope_contract_fingerprint()
    terminal_artifact_render_target_contract_fingerprint_value = terminal_artifact_render_target_contract_fingerprint()
    terminal_artifact_rendering_contract_fingerprint_value = terminal_artifact_rendering_contract_fingerprint()
    terminal_artifact_cli_fallback_contract_fingerprint_value = terminal_artifact_cli_fallback_contract_fingerprint()
    terminal_artifact_renderer_entrypoints_contract_fingerprint_value = (
        terminal_artifact_renderer_entrypoints_contract_fingerprint()
    )
    terminal_artifact_cli_fallback_target_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_target_contract_fingerprint()
    )
    terminal_artifact_raw_leaf_card_default_contract_fingerprint_value = (
        terminal_artifact_raw_leaf_card_default_contract_fingerprint()
    )
    terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint_value = (
        terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
    )
    if include_terminal_artifact:
        fingerprints["terminal_artifact"] = terminal_artifact_contract_fingerprint_value
    if include_kind_contracts:
        fingerprints["kind_contracts"] = terminal_artifact_kind_contracts_fingerprint_value
    if include_terminal_artifact_cli_fallback_route:
        fingerprints["terminal_artifact_cli_fallback_route"] = (
            terminal_artifact_cli_fallback_route_contract_fingerprint()
        )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            ("card_contract_fingerprint", card_contract_fingerprint_value),
            ("action_contract_fingerprint", action_contract_fingerprint_value),
            ("selection_contract_fingerprint", selection_contract_fingerprint_value),
            ("terminal_artifact_kind_contracts", terminal_artifact_kind_contracts_fingerprint_value),
            (
                "terminal_artifact_contract",
                terminal_artifact_contract_fingerprint_value,
            ),
            ("allowed_actions", _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS))),
            ("terminal_artifact_envelope", terminal_artifact_envelope_contract_fingerprint_value),
            ("terminal_artifact_envelope_contract", terminal_artifact_envelope_contract_fingerprint_value),
            ("terminal_artifact_render_target", terminal_artifact_render_target_contract_fingerprint_value),
            ("terminal_artifact_render_target_contract", terminal_artifact_render_target_contract_fingerprint_value),
            ("terminal_artifact_rendering", terminal_artifact_rendering_contract_fingerprint_value),
            ("terminal_artifact_rendering_contract", terminal_artifact_rendering_contract_fingerprint_value),
            (
                "terminal_artifact_rendering_contract_manifest",
                terminal_artifact_rendering_contract_fingerprint_value,
            ),
            ("terminal_artifact_cli_fallback", terminal_artifact_cli_fallback_contract_fingerprint_value),
            (
                "terminal_artifact_cli_fallback_contract",
                terminal_artifact_cli_fallback_contract_fingerprint_value,
            ),
            (
                "renderer_entrypoints_contract",
                terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_target",
                terminal_artifact_cli_fallback_target_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_target_contract",
                terminal_artifact_cli_fallback_target_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_target_contract_manifest",
                terminal_artifact_cli_fallback_target_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint_value,
            ),
        )
        if include_terminal_artifact_cli_fallback_route:
            _add_contract_alias_fingerprints(
                fingerprints,
                (
                    "terminal_artifact_cli_fallback_route",
                    terminal_artifact_cli_fallback_route_contract_fingerprint(),
                ),
                (
                    "terminal_artifact_cli_fallback_route_contract",
                    terminal_artifact_cli_fallback_route_contract_fingerprint(),
                ),
                (
                    "terminal_artifact_cli_fallback_route_contract_fingerprints",
                    terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
                ),
            )
    return fingerprints


@lru_cache(maxsize=None)
def _terminal_artifact_cli_fallback_contract_fingerprints_snapshot(
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> tuple[tuple[str, str], ...]:
    """Return stable fingerprints for the CLI fallback wrapper contract sections.

    The default fingerprint map always includes the kind-policy slice because
    it is part of the stable CLI fallback contract surface. Pass
    ``include_terminal_artifact_cli_fallback=True`` to include the wrapper
    contract fingerprint itself alongside the nested section fingerprints.
    Pass ``include_terminal_artifact_cli_fallback_route=True`` to include the
    CLI fallback route contract fingerprint itself alongside the nested
    section fingerprints.
    Pass ``include_contract_aliases=True`` to include alias keys that mirror
    the manifest field names.
    """

    fingerprints = _TerminalArtifactCliFallbackContractFingerprints(
        _build_terminal_artifact_cli_fallback_contract_fingerprints(
            include_terminal_artifact_cli_fallback=include_terminal_artifact_cli_fallback,
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    )
    kind_policy_contract_fingerprint_value = _fingerprint_manifest_section(
        _build_terminal_artifact_cli_fallback_kind_policy_manifest()
    )
    fingerprints["kind_policy"] = kind_policy_contract_fingerprint_value
    if include_terminal_artifact_cli_fallback:
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_contract_manifest",
                terminal_artifact_cli_fallback_contract_fingerprint(),
            ),
        )
    if include_contract_aliases:
        card_hint_recovery_policy_contract_fingerprint_value = _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest()
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            ("contract_manifest", terminal_artifact_cli_fallback_contract_fingerprint()),
            ("contract_manifest_fingerprint", terminal_artifact_cli_fallback_contract_fingerprint()),
            ("allowed_actions", _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS))),
            ("terminal_fallback", terminal_fallback_contract_fingerprint()),
            ("terminal_fallback_contract", terminal_fallback_contract_fingerprint()),
            (
                "terminal_artifact_cli_fallback_contract_manifest",
                terminal_artifact_cli_fallback_contract_fingerprint(),
            ),
            (
                "shell_refinement_policy",
                _fingerprint_manifest_section(_build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()),
            ),
            (
                "resolver_failure_policy",
                _fingerprint_manifest_section(_build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()),
            ),
            (
                "card_hint_recovery_policy",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
            (
                "kind_policy",
                kind_policy_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_target",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "card_hint_recovery_policy_contract",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
            (
                "card_hint_recovery_policy_contract_manifest",
                card_hint_recovery_policy_contract_fingerprint_value,
            ),
            (
                "kind_policy_contract",
                kind_policy_contract_fingerprint_value,
            ),
            (
                "kind_policy_contract_manifest",
                kind_policy_contract_fingerprint_value,
            ),
            ("terminal_artifact_kind_contracts", terminal_artifact_kind_contracts_fingerprint()),
            ("terminal_artifact_cli_fallback", terminal_artifact_cli_fallback_contract_fingerprint()),
            ("terminal_artifact_rendering", terminal_artifact_rendering_contract_fingerprint()),
            (
                "terminal_artifact_render_target_contract",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_render_target_contract_manifest",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            ("terminal_artifact_render_target", terminal_artifact_render_target_contract_fingerprint()),
            ("terminal_artifact_rendering_contract", terminal_artifact_rendering_contract_fingerprint()),
            (
                "terminal_artifact_rendering_contract_manifest",
                terminal_artifact_rendering_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_contract",
                terminal_artifact_cli_fallback_contract_fingerprint(),
            ),
            (
                "renderer_entrypoints_contract",
                terminal_artifact_renderer_entrypoints_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract_manifest",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract_fingerprints",
                terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"] = (
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                include_contract_aliases=True,
            )
        )
        fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            )
        )
        if include_terminal_artifact_cli_fallback_route:
            _add_contract_alias_fingerprints(
                fingerprints,
                (
                    "terminal_artifact_cli_fallback_route",
                    terminal_artifact_cli_fallback_route_contract_fingerprint(),
                ),
                (
                    "terminal_artifact_cli_fallback_route_contract",
                    terminal_artifact_cli_fallback_route_contract_fingerprint(),
                ),
                (
                    "terminal_artifact_cli_fallback_route_contract_fingerprints",
                    terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
                ),
            )
    return tuple(fingerprints.items())


def describe_terminal_artifact_cli_fallback_contract_fingerprints(
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the CLI fallback wrapper contract sections.

    The default fingerprint map always includes the kind-policy slice because
    it is part of the stable CLI fallback contract surface. Pass
    ``include_terminal_artifact_cli_fallback=True`` to include the wrapper
    contract fingerprint itself alongside the nested section fingerprints.
    Pass ``include_terminal_artifact_cli_fallback_route=True`` to include the
    CLI fallback route contract fingerprint itself alongside the nested
    section fingerprints.
    Pass ``include_contract_aliases=True`` to include alias keys that mirror
    the manifest field names.
    """

    return _TerminalArtifactCliFallbackContractFingerprints(
        dict(
            _terminal_artifact_cli_fallback_contract_fingerprints_snapshot(
                include_terminal_artifact_cli_fallback=include_terminal_artifact_cli_fallback,
                include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
                include_contract_aliases=include_contract_aliases,
            )
        )
    )


class _TerminalArtifactCliFallbackContractFingerprints(dict[str, str]):
    """Dict-like fingerprint map with lean-manifest equality compatibility."""

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            self_view = dict(self)
            other_view = dict(other)
            if "card_hint_recovery_policy" not in self_view or "card_hint_recovery_policy" not in other_view:
                self_view.pop("card_hint_recovery_policy", None)
                other_view.pop("card_hint_recovery_policy", None)
                return self_view == other_view
        return super().__eq__(other)


@lru_cache(maxsize=None)
def _terminal_artifact_cli_fallback_route_contract_fingerprints_snapshot(
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> tuple[tuple[str, str], ...]:
    fingerprints = _build_terminal_artifact_cli_fallback_route_contract_fingerprints()
    if include_terminal_artifact_cli_fallback_route:
        fingerprints["terminal_artifact_cli_fallback_route"] = (
            terminal_artifact_cli_fallback_route_contract_fingerprint()
        )
        fingerprints["terminal_artifact_cli_fallback_route_contract"] = (
            terminal_artifact_cli_fallback_route_contract_fingerprint()
        )
    if include_contract_aliases:
        _add_contract_alias_fingerprints(
            fingerprints,
            ("contract_manifest", terminal_artifact_cli_fallback_route_contract_fingerprint()),
            ("contract_manifest_fingerprint", terminal_artifact_cli_fallback_route_contract_fingerprint()),
            ("terminal_fallback", terminal_fallback_contract_fingerprint()),
            ("terminal_fallback_contract", terminal_fallback_contract_fingerprint()),
            (
                "shell_refinement_policy",
                _fingerprint_manifest_section(_build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()),
            ),
            (
                "resolver_failure_policy",
                _fingerprint_manifest_section(_build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()),
            ),
            (
                "route_precedence",
                _fingerprint_manifest_section(list(_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE)),
            ),
            (
                "route_precedence_contract",
                _fingerprint_manifest_section(list(_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE)),
            ),
            (
                "leaf_renderers",
                _fingerprint_manifest_section(
                    _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()["leaf_renderers"]
                ),
            ),
            (
                "leaf_renderers_contract",
                _fingerprint_manifest_section(
                    _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()["leaf_renderers"]
                ),
            ),
            (
                "terminal_artifact_cli_fallback_target",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_target_contract",
                terminal_artifact_cli_fallback_target_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default_contract",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default_policy",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "raw_leaf_card_default_policy_contract",
                terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_route",
                terminal_artifact_cli_fallback_route_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_route_contract",
                terminal_artifact_cli_fallback_route_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback_route_contract_manifest",
                terminal_artifact_cli_fallback_route_contract_fingerprint(),
            ),
        )
    return tuple(fingerprints.items())


def describe_terminal_artifact_cli_fallback_route_contract_fingerprints(
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the CLI fallback route contract sections."""

    return dict(
        _terminal_artifact_cli_fallback_route_contract_fingerprints_snapshot(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
    )


def _build_terminal_artifact_rendering_contract_fingerprints(
    *,
    include_terminal_artifact_rendering: bool = False,
) -> dict[str, str]:
    fingerprints = {
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
    }
    if include_terminal_artifact_rendering:
        fingerprints["terminal_artifact_rendering"] = terminal_artifact_rendering_contract_fingerprint()
    return fingerprints


def _build_terminal_artifact_cli_fallback_contract_fingerprints(
    *,
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, str]:
    card_hint_recovery_policy_contract_fingerprint_value = _fingerprint_manifest_section(
        _build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest()
    )
    fingerprints = {
        "allowed_actions": _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "terminal_artifact_cli_fallback_entrypoint": _fingerprint_manifest_section(
            "render_terminal_cli_fallback"
        ),
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "shell_refinement_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()
        ),
        "resolver_failure_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
        ),
        "card_hint_recovery_policy": card_hint_recovery_policy_contract_fingerprint_value,
        "payload": terminal_artifact_cli_fallback_payload_contract_fingerprint(),
    }
    if include_terminal_artifact_cli_fallback:
        fingerprints["terminal_artifact_cli_fallback"] = terminal_artifact_cli_fallback_contract_fingerprint()
        fingerprints["terminal_artifact_cli_fallback_payload"] = (
            terminal_artifact_cli_fallback_payload_contract_fingerprint()
        )
    if include_terminal_artifact_cli_fallback_route:
        fingerprints["terminal_artifact_cli_fallback_route"] = (
            terminal_artifact_cli_fallback_route_contract_fingerprint()
        )
    return fingerprints


def _build_terminal_artifact_cli_fallback_target_contract_fingerprints(
    *,
    include_terminal_artifact_cli_fallback_target: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, str]:
    terminal_artifact_renderer_entrypoints_contract_fingerprint_value = (
        terminal_artifact_renderer_entrypoints_contract_fingerprint()
    )
    terminal_artifact_cli_fallback_entrypoint_fingerprint = _fingerprint_manifest_section(
        "render_terminal_cli_fallback"
    )
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
    )
    kind_policy_contract_fingerprint_value = _fingerprint_manifest_section(
        _build_terminal_artifact_cli_fallback_kind_policy_manifest()
    )
    fingerprints = {
        "terminal_artifact_cli_fallback_entrypoint": terminal_artifact_cli_fallback_entrypoint_fingerprint,
        "terminal_artifact_cli_fallback_entrypoint_contract": (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_manifest": (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value
        ),
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "leaf_contracts": a2ui_leaf_contracts_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "kind_resolution": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": terminal_artifact_fallback_recovery_fingerprint(),
        "leaf_renderers": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()["leaf_renderers"]
        ),
        "kind_policy": kind_policy_contract_fingerprint_value,
    }
    _add_contract_alias_fingerprints(
        fingerprints,
        (
            "renderer_entrypoints_contract",
            terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_renderer_entrypoints_contract_manifest",
            terminal_artifact_renderer_entrypoints_contract_fingerprint_value,
        ),
        ("leaf_contracts", a2ui_leaf_contracts_fingerprint()),
        ("leaf_contracts_contract", a2ui_leaf_contracts_fingerprint()),
        ("leaf_contracts_contract_manifest", a2ui_leaf_contracts_fingerprint()),
        (
            "terminal_artifact_cli_fallback_entrypoint_contract_manifest",
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value,
        ),
        (
            "kind_policy_contract",
            kind_policy_contract_fingerprint_value,
        ),
        (
            "kind_policy_contract_manifest",
            kind_policy_contract_fingerprint_value,
        ),
        (
            "leaf_renderers_contract",
            _fingerprint_manifest_section(
                _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()["leaf_renderers"]
            ),
        ),
        (
            "leaf_renderers_contract_manifest",
            _fingerprint_manifest_section(
                _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()["leaf_renderers"]
            ),
        ),
    )
    if include_terminal_artifact_cli_fallback_target:
        fingerprints["terminal_artifact_cli_fallback_target"] = _fingerprint_manifest_section(fingerprints)
    if include_terminal_artifact_cli_fallback_route:
        fingerprints["terminal_artifact_cli_fallback_route"] = (
            terminal_artifact_cli_fallback_route_contract_fingerprint()
        )
    return fingerprints


def _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest() -> dict[str, Any]:
    return {
        "preserve_raw_leaf_card_default": True,
        "invalid_kind_treated_as_absent": True,
        "refine_card_underflow": True,
    }


def _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest() -> dict[str, Any]:
    return {
        "retry_resolver": "resolve_terminal_artifact_render_target",
        "raw_leaf_card_default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "leaf_renderers": {
            "card": "render_terminal_card",
            "action": "render_terminal_action",
            "selection": "render_terminal_selection",
        },
    }


def _build_terminal_artifact_cli_fallback_kind_policy_manifest() -> dict[str, str]:
    return {
        "card": "defer to terminal artifact dispatch and keep card as the default recovery path",
        "action": "recover action payloads with render_terminal_action",
        "selection": "recover selection payloads with render_terminal_selection",
    }


def _build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest() -> dict[str, Any]:
    # Keep the legacy broad field for compatibility, but also expose the more
    # precise mapping-specific name so the manifest matches the actual
    # recovery behavior: typed mapping payloads may recover, while explicit
    # leaf instances stay on the invalid-card path under card hints.
    return {
        "recover_typed_leaf_mappings": True,
        "recover_typed_leaf_payloads": True,
        "explicit_leaf_instances_rejected_under_card_hints": True,
        "preserve_raw_leaf_card_default": True,
    }


def _build_terminal_artifact_cli_fallback_payload_contract_manifest() -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    return {
        "type": "TerminalArtifactCliFallbackPayloadContract",
        "schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_SCHEMA_VERSION,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "payload_type": "TerminalArtifactCliFallbackPayload",
        "renderer_entrypoint": "render_terminal_artifact_cli_fallback_payload",
        "shell_renderer_entrypoint": "ShellUI.render_cli_fallback_payload",
        "required_fields": list(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_REQUIRED_FIELDS),
        "artifact_input_shape": "ordered replayable sequence of explicit two-item sequences: kind, artifact",
        "artifact_input_order_policy": (
            "artifact containers must be replayable ordered sequences; named mapping inputs use the engine stage "
            "order before falling back to sorted names; unordered set-like and one-shot iterable containers are rejected"
        ),
        "named_artifact_order_policy": (
            "named engine artifacts render in plan, revise, patch, apply order when those stage names are present; "
            "other stage names render after known stages in case-insensitive lexical order"
        ),
        "known_engine_stage_order": list(ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER),
        "artifact_entry_contract": "TerminalArtifact",
        "artifact_entry_fields": list(_TERMINAL_ARTIFACT_ENVELOPE_REQUIRED_FIELDS),
        "artifact_entry_version_policy": (
            "embedded artifacts must be complete versioned TerminalArtifact envelopes"
        ),
        "artifact_entry_fingerprint_policy": (
            "artifact fingerprints cover the complete TerminalArtifact envelope including version fields"
        ),
        "artifact_order_policy": (
            "artifact_order exposes the same deterministic references used by cli_fallback so engine clients can "
            "address artifacts without parsing rendered text"
        ),
        "cli_fallback_entry_fields": list(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_CLI_ENTRY_FIELDS),
        "artifact_order_entry_fields": list(
            _TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ORDER_FIELDS
        ),
        "artifact_id_policy": (
            "artifact_id is deterministic from artifact order, kind, and envelope fingerprint for unique "
            "client-neutral references"
        ),
        "artifact_id_format_policy": "artifact_id format is <zero-based-index>:<kind>:<artifact-fingerprint-prefix>",
        "artifact_id_fingerprint_prefix_chars": (
            TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ID_FINGERPRINT_PREFIX_CHARS
        ),
        "artifact_id_uniqueness_policy": "artifact_id values must be unique within each CLI fallback payload",
        "artifact_count_policy": "artifact_count must equal both artifacts and cli_fallback lengths",
        "artifact_order_fingerprint_policy": (
            "artifact_order_fingerprint covers the ordered artifact_id, kind, and artifact_fingerprint entries"
        ),
        "min_artifact_count": 1,
        "empty_payload_policy": "payloads must contain at least one artifact so CLI fallback text is non-empty",
        "alignment_policy": "cli_fallback entries align by index, artifact_id, and kind with artifacts",
        "index_policy": "cli_fallback indexes must be the contiguous artifact order starting at zero",
        "artifact_fingerprint_policy": "cli_fallback artifact_fingerprint must match the aligned artifact envelope",
        "staleness_policy": "cli_fallback text must re-render from the matching artifact envelope",
        "text_policy": "cli_fallback text must be non-empty terminal-rendered text",
        "text_fingerprint_policy": "cli_fallback text_fingerprint must match the rendered text",
        "cli_fallback_fingerprint_policy": "cli_fallback_fingerprint covers the ordered rendered fallback entries",
        "rendered_text_policy": "rendered_text is the canonical joined CLI fallback output",
        "rendered_text_fingerprint_policy": (
            "rendered_text_fingerprint covers the final CLI fallback text after separator joining"
        ),
        "render_separator": TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_RENDER_SEPARATOR,
        "render_separator_policy": "CLI fallback payload entries render with one blank line between entries",
        "engine_authority_policy": (
            "payload carries typed action refs for display only; action execution remains engine PolicyGate authority"
        ),
        "fingerprint_policy": "payload_fingerprint covers all payload fields except itself",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
    }


def _build_engine_artifacts_contract_manifest() -> dict[str, Any]:
    return {
        "type": "A2UIEngineArtifactsContract",
        "schema_version": A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "validator_entrypoint": "validate_engine_artifacts",
        "validation_errors_entrypoint": "collect_engine_artifact_validation_errors",
        "validation_error_records_entrypoint": "collect_engine_artifact_validation_error_records",
        "validation_report_entrypoint": "build_engine_artifact_validation_report",
        "validation_report_validator_entrypoint": "validate_engine_artifact_validation_report",
        "builder_entrypoint": "build_engine_a2ui_cli_fallback_payload",
        "output_contract": "TerminalArtifactCliFallbackPayload",
        "output_renderer_entrypoint": "render_terminal_artifact_cli_fallback_payload",
        "accepted_input_shapes": [
            "stage-name mapping to explicit (kind, artifact) pairs",
            "ordered replayable sequence of explicit (kind, artifact) pairs",
        ],
        "rejected_input_shapes": [
            "empty artifact containers",
            "string or bytes containers",
            "unordered set-like containers",
            "one-shot iterables",
        ],
        "stage_name_policy": (
            "mapping stage names are normalized, must be non-empty, must not contain control characters, "
            "and must be unique after casefolded normalization"
        ),
        "named_artifact_order_policy": (
            "named artifacts render in plan, revise, patch, apply order when those stage names are present; "
            "unknown stage names render after known stages in case-insensitive lexical order"
        ),
        "known_engine_stage_order": list(ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER),
        "ordered_artifact_policy": "sequence inputs preserve caller order exactly",
        "artifact_pair_policy": "each entry must be an explicit two-item kind, artifact pair",
        "validation_error_policy": (
            "collect_engine_artifact_validation_errors returns a stable tuple of rendered ValueError messages "
            "without building or rendering CLI fallback payloads; mapping errors follow the same deterministic "
            "plan, revise, patch, apply stage ordering as CLI fallback rendering"
        ),
        "validation_error_record_policy": (
            "collect_engine_artifact_validation_error_records returns client-neutral records with stable "
            "schema_version, index, location, path, kind, normalized_kind, code, and message fields so "
            "engine callers do not parse rendered error text"
        ),
        "validation_report_policy": (
            "build_engine_artifact_validation_report returns a versioned preflight envelope with valid, "
            "workflow_ready, workflow_blocked_reason, input_shape, artifact_count, artifact_order, "
            "artifact_kind_counts, stage_coverage, error_count, error_codes, errors, error_fingerprint, "
            "contract_fingerprint, and rendered CLI report fields for engine workflow checkpoints"
        ),
        "validation_report_renderer_entrypoint": "render_engine_artifact_validation_report",
        "validation_report_validator_policy": (
            "validate_engine_artifact_validation_report verifies the report envelope, count fields, "
            "artifact_order record shape, artifact_order fingerprint, stage coverage fingerprint, "
            "error fingerprint, contract fingerprint, rendered report fingerprint, and report fingerprint"
        ),
        "validation_report_order_policy": (
            "artifact_order records the deterministic order that build_engine_a2ui_cli_fallback_payload "
            "will use, with a deterministic per-artifact fingerprint, without rendering terminal fallback text"
        ),
        "validation_report_kind_counts_policy": (
            "artifact_kind_counts records normalized artifact kind totals in lexical key order so engine "
            "callers can preflight workflow coverage without parsing CLI text"
        ),
        "validation_report_stage_coverage_policy": (
            "stage_coverage records present and missing known engine workflow stages in the stable "
            "plan, revise, patch, apply order so engine callers can check loop completeness without "
            "rendering CLI fallback text; present_count is the number of completed known checkpoints, "
            "missing_count is the number of absent known checkpoints, next_missing_stage is the first "
            "absent workflow checkpoint in that order, progress_label is the deterministic present/total "
            "checkpoint string, and complete is true only when every known stage is present"
        ),
        "validation_report_workflow_ready_policy": (
            "workflow_ready is true only when the report is valid and every known engine workflow stage is "
            "present, so CLI fallback consumers can gate demo-loop handoff without parsing rendered text"
        ),
        "validation_report_workflow_blocked_reason_policy": (
            "workflow_blocked_reason is null only when workflow_ready is true; otherwise it is a stable "
            "machine-readable reason of validation_errors, missing_stages, or validation_errors_and_missing_stages "
            "so engine and CLI fallback consumers can explain why a handoff is blocked without parsing rendered text"
        ),
        "validation_report_present_count_policy": (
            "present_count always equals the length of present so CLI fallback and engine callers can "
            "display workflow progress without recounting stage names"
        ),
        "validation_report_missing_count_policy": (
            "missing_count always equals the length of missing so CLI fallback and engine callers can "
            "display progress without recounting stage names"
        ),
        "validation_report_next_missing_stage_policy": (
            "next_missing_stage is null only when stage coverage is complete; otherwise it is the "
            "first value from missing so CLI fallback can show the next engine-loop checkpoint"
        ),
        "validation_report_progress_label_policy": (
            "progress_label always renders as present_count/known_stage_count so CLI fallback consumers can "
            "display engine-loop progress without recomputing totals"
        ),
        "validation_report_artifact_order_fields": [
            "index",
            "location",
            "path",
            "stage",
            "kind",
            "normalized_kind",
            "artifact_fingerprint",
        ],
        "validation_error_record_schema_version": A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION,
        "validation_report_stage_coverage_fields": [
            "known_stage_order",
            "present",
            "present_count",
            "missing",
            "missing_count",
            "next_missing_stage",
            "progress_label",
            "complete",
        ],
        "validation_error_record_fields": [
            "schema_version",
            "index",
            "location",
            "path",
            "stage",
            "kind",
            "normalized_kind",
            "code",
            "message",
        ],
        "validation_error_codes": list(_ENGINE_ARTIFACT_VALIDATION_ERROR_CODES),
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "kind_validation_entrypoints": {
            "action": "validate_action_ref",
            "selection": "validate_selection_ref",
            "card": "validate_terminal_artifact_render_target",
        },
        "terminal_artifact_envelope_policy": (
            "complete TerminalArtifact envelopes are accepted when the embedded kind matches the declared pair kind"
        ),
        "cli_fallback_policy": "CLI renders the same validated artifact payload future A2UI clients consume",
        "engine_authority_policy": (
            "payload actions are display artifacts only; execution remains typed, allowlisted, and engine PolicyGate authoritative"
        ),
        "ui_assumption_policy": "contract does not require Textual, web, or Studio-specific renderer assumptions",
        "fingerprint_policy": "contract_fingerprint covers the complete engine artifact contract manifest",
        "terminal_artifact_cli_fallback_payload_contract_fingerprint": (
            terminal_artifact_cli_fallback_payload_contract_fingerprint()
        ),
    }


def _build_terminal_artifact_renderer_entrypoints() -> dict[str, str]:
    """Return the canonical renderer-entrypoint map shared by A2UI manifests."""

    return {entrypoint: renderer for entrypoint, renderer in _TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS}


def _build_terminal_artifact_renderer_entrypoints_contract_fingerprints(
    *,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    renderer_entrypoints = _build_terminal_artifact_renderer_entrypoints()
    renderer_entrypoints_fingerprint = _fingerprint_manifest_section(renderer_entrypoints)
    fingerprints = {
        "renderer_entrypoints": renderer_entrypoints_fingerprint,
    }
    if include_contract_aliases:
        renderer_entrypoints_contract_fingerprint_value = terminal_artifact_renderer_entrypoints_contract_fingerprint()
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "renderer_entrypoints_contract",
                renderer_entrypoints_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_renderer_entrypoints_contract",
                renderer_entrypoints_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_renderer_entrypoints_contract_manifest",
                renderer_entrypoints_contract_fingerprint_value,
            ),
        )
    return fingerprints


def _build_terminal_artifact_renderer_entrypoints_contract_manifest() -> dict[str, Any]:
    renderer_entrypoints = _build_terminal_artifact_renderer_entrypoints()
    renderer_entrypoints_fingerprint = _fingerprint_manifest_section(renderer_entrypoints)
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_renderer_entrypoints_schema_version": TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
        "terminal_artifact_renderer_entrypoints_version": TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
        "type": "TerminalArtifactRendererEntrypointsContract",
        "renderer_entrypoints": renderer_entrypoints,
        "renderer_entrypoints_fingerprint": renderer_entrypoints_fingerprint,
        "contract_fingerprints": {
            "renderer_entrypoints": renderer_entrypoints_fingerprint,
        },
    }


def _build_terminal_artifact_cli_fallback_entrypoint_contract_manifest() -> dict[str, Any]:
    renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
    shell_refinement_policy_contract = describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract()
    resolver_failure_policy_contract = describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract()
    card_hint_recovery_policy = _build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest()
    card_hint_recovery_policy_contract = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
    terminal_artifact_cli_fallback_entrypoint = "render_terminal_cli_fallback"
    contract_fingerprints = describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints()
    terminal_artifact_cli_fallback_entrypoint_fingerprint = _fingerprint_manifest_section(
        terminal_artifact_cli_fallback_entrypoint
    )
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        "version": TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_entrypoint_schema_version": (
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION
        ),
        "terminal_artifact_renderer_entrypoints_schema_version": TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
        "type": "TerminalArtifactCliFallbackEntrypointContract",
        "terminal_artifact_cli_fallback_entrypoint": terminal_artifact_cli_fallback_entrypoint,
        "terminal_artifact_cli_fallback_entrypoint_contract": terminal_artifact_cli_fallback_entrypoint,
        "terminal_artifact_cli_fallback_entrypoint_fingerprint": terminal_artifact_cli_fallback_entrypoint_fingerprint,
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprint": (
            terminal_artifact_cli_fallback_entrypoint_fingerprint
        ),
        "terminal_artifact_cli_fallback_entrypoint_version": (
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION
        ),
        "renderer_entrypoints": _snapshot_contract_section(renderer_entrypoints_contract["renderer_entrypoints"]),
        "renderer_entrypoints_contract": _snapshot_contract_section(renderer_entrypoints_contract),
        "renderer_entrypoints_contract_manifest": _snapshot_contract_section(renderer_entrypoints_contract),
        "renderer_entrypoints_contract_manifest_fingerprint": terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint(),
        "renderer_entrypoints_contract_fingerprint": renderer_entrypoints_contract["contract_fingerprint"],
        "terminal_artifact_renderer_entrypoints_contract_manifest": _snapshot_contract_section(
            renderer_entrypoints_contract
        ),
        "terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint": (
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        ),
        "terminal_artifact_cli_fallback_shell_refinement_policy": _snapshot_contract_section(
            shell_refinement_policy_contract
        ),
        "terminal_artifact_cli_fallback_shell_refinement_policy_fingerprint": shell_refinement_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_shell_refinement_policy_contract": _snapshot_contract_section(
            shell_refinement_policy_contract
        ),
        "terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint": (
            shell_refinement_policy_contract["contract_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest": _snapshot_contract_section(
            shell_refinement_policy_contract
        ),
        "terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest_fingerprint": (
            shell_refinement_policy_contract["contract_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_resolver_failure_policy": _snapshot_contract_section(
            resolver_failure_policy_contract
        ),
        "terminal_artifact_cli_fallback_resolver_failure_policy_fingerprint": resolver_failure_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_resolver_failure_policy_contract": _snapshot_contract_section(
            resolver_failure_policy_contract
        ),
        "terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint": (
            resolver_failure_policy_contract["contract_fingerprint"]
        ),
        "terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest": _snapshot_contract_section(
            resolver_failure_policy_contract
        ),
        "terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint": (
            resolver_failure_policy_contract["contract_fingerprint"]
        ),
        "card_hint_recovery_policy": _snapshot_contract_section(card_hint_recovery_policy),
        "card_hint_recovery_policy_fingerprint": _fingerprint_manifest_section(card_hint_recovery_policy),
        "card_hint_recovery_policy_contract": _snapshot_contract_section(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_contract_fingerprint": card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ],
        "card_hint_recovery_policy_contract_manifest": _snapshot_contract_section(
            card_hint_recovery_policy_contract
        ),
        "card_hint_recovery_policy_contract_manifest_fingerprint": card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints": _snapshot_contract_section(
            contract_fingerprints
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint()
        ),
        "contract_fingerprints": contract_fingerprints,
    }


def _build_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints(
    *,
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    renderer_entrypoints_contract_fingerprint_value = terminal_artifact_renderer_entrypoints_contract_fingerprint()
    shell_refinement_policy_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint()
    )
    resolver_failure_policy_contract_fingerprint_value = (
        terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint()
    )
    card_hint_recovery_policy_contract_fingerprint_value = _fingerprint_manifest_section(
        _build_terminal_artifact_cli_fallback_card_hint_recovery_policy_manifest()
    )
    fingerprints = {
        "terminal_artifact_cli_fallback_entrypoint": _fingerprint_manifest_section(
            "render_terminal_cli_fallback"
        ),
        "renderer_entrypoints": renderer_entrypoints_contract_fingerprint_value,
        "renderer_entrypoints_contract_manifest": renderer_entrypoints_contract_fingerprint_value,
        "shell_refinement_policy": shell_refinement_policy_contract_fingerprint_value,
        "resolver_failure_policy": resolver_failure_policy_contract_fingerprint_value,
        "card_hint_recovery_policy": card_hint_recovery_policy_contract_fingerprint_value,
    }
    _add_contract_alias_fingerprints(
        fingerprints,
        (
            "renderer_entrypoints_contract",
            renderer_entrypoints_contract_fingerprint_value,
        ),
        (
            "terminal_artifact_renderer_entrypoints_contract_manifest",
            renderer_entrypoints_contract_fingerprint_value,
        ),
        (
            "shell_refinement_policy_contract",
            shell_refinement_policy_contract_fingerprint_value,
        ),
        (
            "shell_refinement_policy_contract_manifest",
            shell_refinement_policy_contract_fingerprint_value,
        ),
        (
            "resolver_failure_policy_contract",
            resolver_failure_policy_contract_fingerprint_value,
        ),
        (
            "resolver_failure_policy_contract_manifest",
            resolver_failure_policy_contract_fingerprint_value,
        ),
        (
            "card_hint_recovery_policy_contract",
            card_hint_recovery_policy_contract_fingerprint_value,
        ),
        (
            "card_hint_recovery_policy_contract_manifest",
            card_hint_recovery_policy_contract_fingerprint_value,
        ),
    )
    if include_contract_aliases:
        terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value = (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
        )
        terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint_value = (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint()
        )
        _add_contract_alias_fingerprints(
            fingerprints,
            (
                "terminal_artifact_cli_fallback_entrypoint_contract",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint_value,
            ),
            (
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint",
                terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint_value,
            ),
        )
    return fingerprints


@lru_cache(maxsize=None)
def _terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_snapshot(
    include_contract_aliases: bool = False,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        _build_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints(
            include_contract_aliases=include_contract_aliases,
        ).items()
    )


def describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints(
    include_contract_aliases: bool = False,
) -> dict[str, str]:
    """Return stable fingerprints for the explicit CLI fallback entrypoint contract."""

    return dict(
        _terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_snapshot(
            include_contract_aliases=include_contract_aliases,
        )
    )


def terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(
    include_contract_aliases: bool = False,
) -> str:
    """Return a stable fingerprint for the explicit CLI fallback entrypoint fingerprint map."""

    return _fingerprint_manifest_section(
        describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints(
            include_contract_aliases=include_contract_aliases,
        )
    )


def _build_terminal_artifact_cli_fallback_route_contract_fingerprints() -> dict[str, str]:
    return {
        "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_artifact_cli_fallback_target_contract": terminal_artifact_cli_fallback_target_contract_fingerprint(),
        "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "kind_resolution": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": terminal_artifact_fallback_recovery_fingerprint(),
        "shell_refinement_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()
        ),
        "resolver_failure_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
        ),
        "route_precedence": _fingerprint_manifest_section(list(_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE)),
        "leaf_renderers": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()["leaf_renderers"]
        ),
    }


def _build_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
    *,
    include_terminal_artifact_raw_leaf_card_default_policy: bool = False,
) -> dict[str, str]:
    fingerprint = terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint()
    fingerprints = {
        "raw_leaf_card_default_policy_contract": fingerprint,
    }
    if include_terminal_artifact_raw_leaf_card_default_policy:
        fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"] = fingerprint
    return fingerprints


def _build_terminal_artifact_raw_leaf_card_default_contract_fingerprints(
    *,
    include_terminal_artifact_raw_leaf_card_default: bool = False,
) -> dict[str, str]:
    fingerprint = terminal_artifact_raw_leaf_card_default_contract_fingerprint()
    fingerprints = {
        "raw_leaf_card_default_contract": fingerprint,
    }
    if include_terminal_artifact_raw_leaf_card_default:
        fingerprints["terminal_artifact_raw_leaf_card_default_contract"] = fingerprint
    return fingerprints


def build_terminal_artifact_envelope(artifact: Any, *, kind: str) -> dict[str, Any]:
    """Build a canonical ``TerminalArtifact`` envelope for structured CLI payloads.

    The envelope keeps the kind explicit so engine callers can emit stable
    artifacts now and future UI clients can consume the same payload shape
    later without guessing. The helper rejects mismatched kind/payload pairs
    so the engine cannot accidentally label an action as a card or vice versa.
    TerminalArtifact payloads are normalized to plain dictionary snapshots so
    the contract stays predictable even when callers pass dataclass instances.
    """

    normalized_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    artifact = _unwrap_terminal_artifact_for_kind(artifact, kind=normalized_kind)
    artifact_snapshot = normalize_terminal_artifact_payload(artifact, kind=normalized_kind)
    envelope = {
        "type": _TERMINAL_ARTIFACT_ENVELOPE_TYPE,
        "kind": normalized_kind,
        "artifact": artifact_snapshot,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
    }
    validate_terminal_artifact_envelope(envelope)
    return envelope


def build_terminal_artifact_cli_fallback_payload(
    artifacts: Sequence[Sequence[Any]],
) -> dict[str, Any]:
    """Build the shared engine-to-client payload plus deterministic CLI text.

    Engine flows can emit this small bundle when they need to hand multiple
    structured artifacts to a CLI today and a richer client later. Each item is
    still a normal ``TerminalArtifact`` envelope, and the fallback text is
    rendered from that same envelope so the CLI path cannot drift from the
    shared contract payload.
    """

    if (
        isinstance(artifacts, (str, bytes, Mapping, Set))
        or not isinstance(artifacts, Sequence)
    ):
        raise ValueError("TerminalArtifact fallback payload artifacts must be a replayable ordered sequence")

    envelope_items: list[dict[str, Any]] = []
    rendered_items: list[dict[str, Any]] = []
    for index, item in enumerate(artifacts):
        if isinstance(item, (str, bytes)) or not isinstance(item, Sequence) or len(item) != 2:
            raise ValueError("TerminalArtifact fallback payload items must be (kind, artifact) pairs")
        kind, artifact = item
        envelope = build_terminal_artifact_envelope(artifact, kind=kind)
        envelope_items.append(envelope)
        artifact_fingerprint = _fingerprint_manifest_section(envelope)
        rendered_text = render_terminal_cli_fallback(envelope, kind=envelope["kind"])
        rendered_items.append(
            {
                "index": index,
                "artifact_id": _terminal_artifact_cli_fallback_payload_artifact_id(
                    envelope,
                    index=index,
                    artifact_fingerprint=artifact_fingerprint,
                ),
                "kind": envelope["kind"],
                "artifact_fingerprint": artifact_fingerprint,
                "text": rendered_text,
                "text_fingerprint": _fingerprint_manifest_section(rendered_text),
            }
        )
    rendered_text = _render_terminal_artifact_cli_fallback_payload_text(rendered_items)
    artifact_order = [
        _terminal_artifact_cli_fallback_payload_artifact_order_entry(envelope, index=index)
        for index, envelope in enumerate(envelope_items)
    ]
    payload = {
        "type": "TerminalArtifactCliFallbackPayload",
        "schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_SCHEMA_VERSION,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "artifact_count": len(envelope_items),
        "artifact_order": artifact_order,
        "artifact_order_fingerprint": _fingerprint_manifest_section(artifact_order),
        "artifacts": envelope_items,
        "cli_fallback": rendered_items,
    }
    payload["cli_fallback_fingerprint"] = _fingerprint_manifest_section(rendered_items)
    payload["rendered_text"] = rendered_text
    payload["rendered_text_fingerprint"] = _fingerprint_manifest_section(rendered_text)
    payload["payload_fingerprint"] = _fingerprint_manifest_section(dict(payload))
    validate_terminal_artifact_cli_fallback_payload(payload)
    return payload


def build_named_terminal_artifact_cli_fallback_payload(
    artifacts: Mapping[str, Sequence[Any]],
) -> dict[str, Any]:
    """Build a CLI fallback payload from stable engine artifact names.

    Engine workflows often accumulate artifacts by stage name before they are
    rendered. This helper keeps those stage names out of the client payload
    while using them to impose a deterministic order, so equivalent engine
    outputs render the same CLI fallback regardless of insertion order.
    """

    if not isinstance(artifacts, Mapping):
        raise ValueError("Named TerminalArtifact fallback artifacts must be a mapping")
    if not artifacts:
        raise ValueError("Named TerminalArtifact fallback artifacts must contain at least one artifact")

    ordered_artifacts: list[tuple[str, Any]] = []
    normalized_names: set[str] = set()
    for name, item in artifacts.items():
        normalized_name = _normalize_terminal_artifact_cli_fallback_payload_artifact_name(name)
        normalized_unique_key = normalized_name.casefold()
        if normalized_unique_key in normalized_names:
            raise ValueError("Named TerminalArtifact fallback artifact names must be unique after normalization")
        normalized_names.add(normalized_unique_key)
        if isinstance(item, (str, bytes)) or not isinstance(item, Sequence) or len(item) != 2:
            raise ValueError("Named TerminalArtifact fallback artifacts must map names to (kind, artifact) pairs")
        kind, artifact = item
        ordered_artifacts.append((normalized_name, (kind, artifact)))

    return build_terminal_artifact_cli_fallback_payload(
        [
            item
            for _, item in sorted(
                ordered_artifacts,
                key=lambda entry: _engine_a2ui_cli_fallback_stage_sort_key(entry[0]),
            )
        ]
    )


def build_engine_a2ui_cli_fallback_payload(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> dict[str, Any]:
    """Build the engine-facing A2UI payload with shared CLI fallback text.

    Engine runs can accumulate artifacts as either stage-name mappings or as
    an already ordered list of ``(kind, artifact)`` pairs. This entrypoint keeps
    that choice out of callers while still returning the same
    ``TerminalArtifactCliFallbackPayload`` contract consumed by CLI rendering
    and future A2UI clients.
    """

    validate_engine_artifacts(artifacts)
    if isinstance(artifacts, Mapping):
        return build_named_terminal_artifact_cli_fallback_payload(artifacts)
    return build_terminal_artifact_cli_fallback_payload(artifacts)


def build_engine_output(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> EngineOutput:
    """Build a typed, versionable engine output from validated artifacts.

    Accepts the same input shapes as ``build_engine_a2ui_cli_fallback_payload``
    and returns a frozen ``EngineOutput`` dataclass suitable for direct engine
    consumption, serialization, and future A2UI client handoff.
    """

    pairs = _collect_engine_artifact_pairs(artifacts)
    _, artifact_order_records = _collect_engine_artifact_validation_report_order(artifacts)
    stage_coverage = _collect_engine_artifact_validation_report_stage_coverage(artifact_order_records)
    error_records = _collect_engine_artifact_validation_error_records(
        artifacts, include_payload_after_pair_errors=True
    )
    error_messages = tuple(record["message"] for record in error_records)
    ordered_artifacts = tuple((kind, artifact) for _, kind, artifact in pairs)
    fingerprint = _fingerprint_manifest_section({
        "schema_version": ENGINE_OUTPUT_SCHEMA_VERSION,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "artifacts": ordered_artifacts,
        "valid": not error_records,
        "error_count": len(error_records),
        "stage_coverage": stage_coverage,
    })
    return EngineOutput(
        schema_version=ENGINE_OUTPUT_SCHEMA_VERSION,
        contract_version=A2UI_CONTRACT_VERSION,
        a2ui_version=A2UI_VERSION,
        artifacts=ordered_artifacts,
        valid=not error_records,
        error_count=len(error_records),
        errors=error_messages,
        stage_coverage=stage_coverage,
        fingerprint=fingerprint,
    )


def validate_engine_artifacts(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> None:
    """Validate a batch of engine artifacts against the A2UI contract.

    This pre-flight check allows the engine to verify that its accumulated
    artifacts conform to the contract before committing to the expensive
    render+build step. It accepts the same input shapes as
    ``build_engine_a2ui_cli_fallback_payload`` so callers can validate first
    and build only when the contract is satisfied.

    Raises ``ValueError`` with a clear message on the first violation
    encountered. Each artifact is validated by its declared kind:
    - ``"action"``: validated through ``validate_action_ref``
    - ``"selection"``: validated through ``validate_selection_ref``
    - ``"card"``: validated as a terminal card payload
    """

    for location, kind, artifact in _collect_engine_artifact_pairs(artifacts):
        _validate_engine_artifact_kind(kind, location)
        _validate_engine_artifact_payload(kind, artifact, location)


def collect_engine_artifact_validation_errors(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> tuple[str, ...]:
    """Return stable validation errors for engine artifact preflight checks."""

    return tuple(record["message"] for record in collect_engine_artifact_validation_error_records(artifacts))


def collect_engine_artifact_validation_error_records(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> tuple[dict[str, Any], ...]:
    """Return stable, structured validation errors for engine artifact preflight checks."""

    return _collect_engine_artifact_validation_error_records(artifacts, include_payload_after_pair_errors=False)


def _collect_engine_artifact_validation_error_records(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
    *,
    include_payload_after_pair_errors: bool,
) -> tuple[dict[str, Any], ...]:
    """Return stable validation records, optionally aggregating payload errors too."""

    if isinstance(artifacts, Mapping):
        stage_errors = _collect_engine_artifact_stage_validation_error_records(artifacts)
        pair_errors = _collect_engine_artifact_pair_shape_error_records(artifacts)
        if stage_errors or pair_errors:
            if include_payload_after_pair_errors:
                return tuple(
                    stage_errors
                    + pair_errors
                    + _collect_engine_artifact_mapping_validation_error_records(artifacts)
                )
            return tuple(stage_errors + pair_errors)
        mapping_errors = _collect_engine_artifact_mapping_validation_error_records(artifacts)
        if mapping_errors:
            return tuple(mapping_errors)
    try:
        pairs = _collect_engine_artifact_pairs(artifacts)
    except ValueError as exc:
        pair_errors = _collect_engine_artifact_pair_shape_error_records(artifacts)
        if pair_errors:
            if include_payload_after_pair_errors:
                return tuple(pair_errors + _collect_engine_artifact_sequence_validation_error_records(artifacts))
            return tuple(pair_errors)
        return (
            {
                "schema_version": A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION,
                "index": 0,
                "location": "<container>",
                "path": "$",
                "stage": None,
                "kind": None,
                "normalized_kind": None,
                "code": "invalid_container",
                "message": str(exc),
            },
        )
    errors: list[dict[str, Any]] = []
    for index, (location, kind, artifact) in enumerate(pairs):
        try:
            _validate_engine_artifact_kind(kind, location)
            _validate_engine_artifact_payload(kind, artifact, location)
        except ValueError as exc:
            errors.append(
                {
                    "schema_version": A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION,
                    "index": index,
                    "location": location,
                    "path": _engine_artifact_validation_record_path(location),
                    "stage": _engine_artifact_validation_record_stage(location),
                    "kind": kind if isinstance(kind, str) else None,
                    "normalized_kind": _normalize_engine_artifact_record_kind(kind),
                    "code": _engine_artifact_validation_error_code(kind, exc),
                    "message": str(exc),
                }
            )
    return tuple(errors)


def build_engine_artifact_validation_report(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> dict[str, Any]:
    """Return a versioned engine artifact validation report without rendering CLI text."""

    input_shape, artifact_order = _collect_engine_artifact_validation_report_order(artifacts)
    errors = _collect_engine_artifact_validation_error_records(artifacts, include_payload_after_pair_errors=True)
    artifact_kind_counts = _collect_engine_artifact_validation_report_kind_counts(artifact_order)
    stage_coverage = _collect_engine_artifact_validation_report_stage_coverage(artifact_order)
    workflow_blocked_reason = _engine_artifact_validation_report_workflow_blocked_reason(errors, stage_coverage)
    report = {
        "type": "A2UIEngineArtifactValidationReport",
        "schema_version": A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "input_shape": input_shape,
        "artifact_count": len(artifact_order),
        "artifact_order": artifact_order,
        "artifact_order_fingerprint": _fingerprint_manifest_section(artifact_order),
        "artifact_kind_counts": artifact_kind_counts,
        "artifact_kind_counts_fingerprint": _fingerprint_manifest_section(artifact_kind_counts),
        "stage_coverage": stage_coverage,
        "stage_coverage_fingerprint": _fingerprint_manifest_section(stage_coverage),
        "valid": not errors,
        "workflow_ready": workflow_blocked_reason is None,
        "workflow_blocked_reason": workflow_blocked_reason,
        "error_count": len(errors),
        "error_codes": _collect_engine_artifact_validation_report_error_codes(errors),
        "errors": list(errors),
        "error_fingerprint": _fingerprint_manifest_section(errors),
        "contract_fingerprint": engine_artifacts_contract_fingerprint(),
    }
    report["rendered_text"] = _render_engine_artifact_validation_report_text(report)
    report["rendered_text_fingerprint"] = _fingerprint_manifest_section(report["rendered_text"])
    report["report_fingerprint"] = _fingerprint_manifest_section(report)
    return report


def render_engine_artifact_validation_report(report: Mapping[str, Any]) -> str:
    """Render a validated engine artifact preflight report as deterministic CLI text."""

    validate_engine_artifact_validation_report(report)
    return report["rendered_text"]


def validate_engine_artifact_validation_report(report: Mapping[str, Any]) -> None:
    """Validate a generated engine artifact validation report envelope."""

    if not isinstance(report, Mapping):
        raise ValueError("Engine artifact validation report must be an object")
    missing = sorted(set(_ENGINE_ARTIFACT_VALIDATION_REPORT_REQUIRED_FIELDS) - set(report))
    if missing:
        raise ValueError(f"Missing engine artifact validation report field(s): {missing}")
    extras = sorted(set(report) - set(_ENGINE_ARTIFACT_VALIDATION_REPORT_REQUIRED_FIELDS))
    if extras:
        raise ValueError(f"Unexpected engine artifact validation report field(s): {extras}")
    if report.get("type") != "A2UIEngineArtifactValidationReport":
        raise ValueError("Engine artifact validation report type is invalid")
    if report.get("schema_version") != A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION:
        raise ValueError("Engine artifact validation report schema_version is invalid")
    if report.get("contract_version") != A2UI_CONTRACT_VERSION:
        raise ValueError("Engine artifact validation report contract_version is invalid")
    if report.get("a2ui_version") != A2UI_VERSION:
        raise ValueError("Engine artifact validation report a2ui_version is invalid")
    if report.get("input_shape") not in {"stage_mapping", "ordered_sequence", "invalid"}:
        raise ValueError("Engine artifact validation report input_shape is invalid")
    artifact_order = report.get("artifact_order")
    if not isinstance(artifact_order, list):
        raise ValueError("Engine artifact validation report artifact_order must be a list")
    for artifact_order_record in artifact_order:
        _validate_engine_artifact_validation_order_record(artifact_order_record)
    artifact_count = report.get("artifact_count")
    if type(artifact_count) is not int or artifact_count != len(artifact_order):
        raise ValueError("Engine artifact validation report artifact_count is invalid")
    artifact_order_fingerprint = report.get("artifact_order_fingerprint")
    if (
        type(artifact_order_fingerprint) is not str
        or artifact_order_fingerprint != _fingerprint_manifest_section(artifact_order)
    ):
        raise ValueError("Engine artifact validation report artifact_order_fingerprint is stale")
    artifact_kind_counts = report.get("artifact_kind_counts")
    if (
        not isinstance(artifact_kind_counts, dict)
        or any(not isinstance(kind, str) or not kind for kind in artifact_kind_counts)
        or any(type(count) is not int or count < 1 for count in artifact_kind_counts.values())
        or artifact_kind_counts != _collect_engine_artifact_validation_report_kind_counts(artifact_order)
        or list(artifact_kind_counts) != sorted(artifact_kind_counts)
    ):
        raise ValueError("Engine artifact validation report artifact_kind_counts is invalid")
    artifact_kind_counts_fingerprint = report.get("artifact_kind_counts_fingerprint")
    if (
        type(artifact_kind_counts_fingerprint) is not str
        or artifact_kind_counts_fingerprint != _fingerprint_manifest_section(artifact_kind_counts)
    ):
        raise ValueError("Engine artifact validation report artifact_kind_counts_fingerprint is stale")
    stage_coverage = report.get("stage_coverage")
    if (
        not isinstance(stage_coverage, dict)
        or stage_coverage != _collect_engine_artifact_validation_report_stage_coverage(artifact_order)
        or not isinstance(stage_coverage.get("known_stage_order"), list)
        or stage_coverage["known_stage_order"] != list(ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER)
        or not isinstance(stage_coverage.get("present"), list)
        or type(stage_coverage.get("present_count")) is not int
        or stage_coverage.get("present_count") != len(stage_coverage["present"])
        or not isinstance(stage_coverage.get("missing"), list)
        or type(stage_coverage.get("missing_count")) is not int
        or stage_coverage.get("missing_count") != len(stage_coverage["missing"])
        or stage_coverage.get("next_missing_stage")
        != (stage_coverage["missing"][0] if stage_coverage["missing"] else None)
        or (
            stage_coverage.get("next_missing_stage") is not None
            and not isinstance(stage_coverage.get("next_missing_stage"), str)
        )
        or any(stage not in ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER for stage in stage_coverage["present"])
        or any(stage not in ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER for stage in stage_coverage["missing"])
        or type(stage_coverage.get("progress_label")) is not str
        or stage_coverage.get("progress_label")
        != f"{stage_coverage['present_count']}/{len(stage_coverage['known_stage_order'])}"
        or type(stage_coverage.get("complete")) is not bool
        or stage_coverage.get("complete") != (not stage_coverage["missing"])
    ):
        raise ValueError("Engine artifact validation report stage_coverage is invalid")
    stage_coverage_fingerprint = report.get("stage_coverage_fingerprint")
    if (
        type(stage_coverage_fingerprint) is not str
        or stage_coverage_fingerprint != _fingerprint_manifest_section(stage_coverage)
    ):
        raise ValueError("Engine artifact validation report stage_coverage_fingerprint is stale")
    errors = report.get("errors")
    if not isinstance(errors, list):
        raise ValueError("Engine artifact validation report errors must be a list")
    for error in errors:
        _validate_engine_artifact_validation_error_record(error)
    error_count = report.get("error_count")
    if type(error_count) is not int or error_count != len(errors):
        raise ValueError("Engine artifact validation report error_count is invalid")
    error_codes = report.get("error_codes")
    if (
        not isinstance(error_codes, list)
        or any(not isinstance(code, str) or not code for code in error_codes)
        or error_codes != _collect_engine_artifact_validation_report_error_codes(errors)
    ):
        raise ValueError("Engine artifact validation report error_codes is invalid")
    valid = report.get("valid")
    if type(valid) is not bool or valid != (not errors):
        raise ValueError("Engine artifact validation report valid flag is invalid")
    workflow_ready = report.get("workflow_ready")
    if type(workflow_ready) is not bool or workflow_ready != (valid and bool(stage_coverage["complete"])):
        raise ValueError("Engine artifact validation report workflow_ready flag is invalid")
    workflow_blocked_reason = report.get("workflow_blocked_reason")
    expected_workflow_blocked_reason = _engine_artifact_validation_report_workflow_blocked_reason(
        errors,
        stage_coverage,
    )
    if workflow_blocked_reason != expected_workflow_blocked_reason:
        raise ValueError("Engine artifact validation report workflow_blocked_reason is invalid")
    error_fingerprint = report.get("error_fingerprint")
    if type(error_fingerprint) is not str or error_fingerprint != _fingerprint_manifest_section(errors):
        raise ValueError("Engine artifact validation report error_fingerprint is stale")
    if report.get("contract_fingerprint") != engine_artifacts_contract_fingerprint():
        raise ValueError("Engine artifact validation report contract_fingerprint is stale")
    rendered_text = report.get("rendered_text")
    if type(rendered_text) is not str or not rendered_text:
        raise ValueError("Engine artifact validation report rendered_text is invalid")
    if rendered_text != _render_engine_artifact_validation_report_text(report):
        raise ValueError("Engine artifact validation report rendered_text is stale")
    rendered_text_fingerprint = report.get("rendered_text_fingerprint")
    if (
        type(rendered_text_fingerprint) is not str
        or rendered_text_fingerprint != _fingerprint_manifest_section(rendered_text)
    ):
        raise ValueError("Engine artifact validation report rendered_text_fingerprint is stale")
    expected_report_fingerprint = _fingerprint_manifest_section(
        {key: value for key, value in report.items() if key != "report_fingerprint"}
    )
    if report.get("report_fingerprint") != expected_report_fingerprint:
        raise ValueError("Engine artifact validation report report_fingerprint is stale")


def _render_engine_artifact_validation_report_text(report: Mapping[str, Any]) -> str:
    lines = [
        "[A2UIEngineArtifactValidationReport]",
        f"Status: {'valid' if report['valid'] else 'invalid'}",
        f"Workflow ready: {'yes' if report['workflow_ready'] else 'no'}",
        f"Workflow handoff: {'ready' if report['workflow_ready'] else 'blocked'}",
        f"Workflow blocked reason: {report['workflow_blocked_reason'] or '-'}",
        f"Input shape: {report['input_shape']}",
        f"Artifacts: {report['artifact_count']}",
        f"Errors: {report['error_count']}",
    ]
    if report["error_codes"]:
        lines.append(f"Error codes: {', '.join(report['error_codes'])}")
    if report["artifact_order"]:
        lines.append("Artifact order:")
        for record in report["artifact_order"]:
            stage = record["stage"] if record["stage"] is not None else "-"
            kind = record["normalized_kind"] if record["normalized_kind"] is not None else "-"
            lines.append(f"- {record['path']}: kind={kind} stage={stage}")
    if report["artifact_kind_counts"]:
        rendered_counts = ", ".join(
            f"{kind}={count}" for kind, count in report["artifact_kind_counts"].items()
        )
        lines.append(f"Artifact kinds: {rendered_counts}")
    stage_coverage = report["stage_coverage"]
    lines.append(f"Stages present: {', '.join(stage_coverage['present']) or '-'}")
    lines.append(f"Present stage count: {stage_coverage['present_count']}")
    lines.append(f"Stages missing: {', '.join(stage_coverage['missing']) or '-'}")
    lines.append(f"Missing stage count: {stage_coverage['missing_count']}")
    lines.append(f"Next missing stage: {stage_coverage['next_missing_stage'] or '-'}")
    lines.append(f"Stage progress: {stage_coverage['progress_label']}")
    lines.append(f"Stages complete: {'yes' if stage_coverage['complete'] else 'no'}")
    if report["errors"]:
        lines.append("Validation errors:")
        for error in report["errors"]:
            kind = error["normalized_kind"] if error["normalized_kind"] is not None else "-"
            lines.append(f"- {error['path']}: {error['code']} ({kind}) {error['message']}")
    lines.append(f"Contract fingerprint: {report['contract_fingerprint']}")
    lines.append(f"Error fingerprint: {report['error_fingerprint']}")
    return "\n".join(lines)


def _validate_engine_artifact_validation_error_record(error: Any) -> None:
    if not isinstance(error, Mapping):
        raise ValueError("Engine artifact validation report errors entries must be objects")
    missing = sorted(set(_ENGINE_ARTIFACT_VALIDATION_ERROR_RECORD_REQUIRED_FIELDS) - set(error))
    if missing:
        raise ValueError(f"Missing engine artifact validation error field(s): {missing}")
    extras = sorted(set(error) - set(_ENGINE_ARTIFACT_VALIDATION_ERROR_RECORD_REQUIRED_FIELDS))
    if extras:
        raise ValueError(f"Unexpected engine artifact validation error field(s): {extras}")
    if error.get("schema_version") != A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION:
        raise ValueError("Engine artifact validation error schema_version is invalid")
    if type(error.get("index")) is not int:
        raise ValueError("Engine artifact validation error index is invalid")
    for field_name in ("location", "path", "code", "message"):
        if not isinstance(error.get(field_name), str) or not error[field_name]:
            raise ValueError(f"Engine artifact validation error {field_name} is invalid")
    if error["code"] not in _ENGINE_ARTIFACT_VALIDATION_ERROR_CODES:
        raise ValueError("Engine artifact validation error code is not allowlisted")
    for field_name in ("stage", "kind", "normalized_kind"):
        value = error.get(field_name)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"Engine artifact validation error {field_name} is invalid")


def _validate_engine_artifact_validation_order_record(record: Any) -> None:
    if not isinstance(record, Mapping):
        raise ValueError("Engine artifact validation report artifact_order entries must be objects")
    missing = sorted(set(_ENGINE_ARTIFACT_VALIDATION_ORDER_RECORD_REQUIRED_FIELDS) - set(record))
    if missing:
        raise ValueError(f"Missing engine artifact validation order field(s): {missing}")
    extras = sorted(set(record) - set(_ENGINE_ARTIFACT_VALIDATION_ORDER_RECORD_REQUIRED_FIELDS))
    if extras:
        raise ValueError(f"Unexpected engine artifact validation order field(s): {extras}")
    if type(record.get("index")) is not int:
        raise ValueError("Engine artifact validation order index is invalid")
    for field_name in ("location", "path"):
        if not isinstance(record.get(field_name), str) or not record[field_name]:
            raise ValueError(f"Engine artifact validation order {field_name} is invalid")
    for field_name in ("stage", "kind", "normalized_kind"):
        value = record.get(field_name)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"Engine artifact validation order {field_name} is invalid")
    artifact_fingerprint = record.get("artifact_fingerprint")
    if not isinstance(artifact_fingerprint, str) or not artifact_fingerprint:
        raise ValueError("Engine artifact validation order artifact_fingerprint is invalid")


def _engine_artifact_fingerprint(artifact: Any) -> str:
    return _fingerprint_manifest_section(_snapshot_contract_value(artifact))


def _collect_engine_artifact_validation_report_order(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> tuple[str, list[dict[str, Any]]]:
    if isinstance(artifacts, Mapping):
        return "stage_mapping", _collect_engine_artifact_validation_report_mapping_order(artifacts)
    elif isinstance(artifacts, (str, bytes, Mapping, Set)) or not isinstance(artifacts, Sequence):
        input_shape = "invalid"
    else:
        return "ordered_sequence", _collect_engine_artifact_validation_report_sequence_order(artifacts)

    return input_shape, []


def _collect_engine_artifact_validation_report_mapping_order(
    artifacts: Mapping[str, Sequence[Any]],
) -> list[dict[str, Any]]:
    normalized_names: set[str] = set()
    named_pairs: list[tuple[str, str, Any, Any]] = []
    for name, item in artifacts.items():
        try:
            normalized_name = _normalize_terminal_artifact_cli_fallback_payload_artifact_name(name)
        except ValueError:
            continue
        normalized_unique_key = normalized_name.casefold()
        if normalized_unique_key in normalized_names:
            continue
        normalized_names.add(normalized_unique_key)
        if not _is_engine_artifact_pair(item):
            continue
        kind, artifact = item
        named_pairs.append((normalized_name, f"stage {normalized_name!r}", kind, artifact))

    artifact_order: list[dict[str, Any]] = []
    for index, (stage_name, location, kind, artifact) in enumerate(
        sorted(named_pairs, key=lambda pair: _engine_a2ui_cli_fallback_stage_sort_key(pair[0]))
    ):
        artifact_order.append(
            {
                "index": index,
                "location": location,
                "path": _engine_artifact_stage_path(stage_name),
                "stage": stage_name,
                "kind": kind if isinstance(kind, str) else None,
                "normalized_kind": _normalize_engine_artifact_record_kind(kind),
                "artifact_fingerprint": _engine_artifact_fingerprint(artifact),
            }
        )
    return artifact_order


def _collect_engine_artifact_validation_report_sequence_order(
    artifacts: Sequence[Sequence[Any]],
) -> list[dict[str, Any]]:
    artifact_order: list[dict[str, Any]] = []
    for index, item in enumerate(artifacts):
        if not _is_engine_artifact_pair(item):
            continue
        kind, artifact = item
        location = f"index {index}"
        artifact_order.append(
            {
                "index": index,
                "location": location,
                "path": f"$[{index}]",
                "stage": None,
                "kind": kind if isinstance(kind, str) else None,
                "normalized_kind": _normalize_engine_artifact_record_kind(kind),
                "artifact_fingerprint": _engine_artifact_fingerprint(artifact),
            }
        )
    return artifact_order


def _collect_engine_artifact_validation_report_error_codes(
    errors: Sequence[Mapping[str, Any]],
) -> list[str]:
    return sorted(
        {error["code"] for error in errors if isinstance(error.get("code"), str) and error["code"]}
    )


def _collect_engine_artifact_validation_report_kind_counts(
    artifact_order: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in artifact_order:
        kind = record.get("normalized_kind")
        if not isinstance(kind, str) or not kind:
            continue
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def _collect_engine_artifact_validation_report_stage_coverage(
    artifact_order: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    known_stage_order = list(ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER)
    present_stage_names = {
        stage
        for record in artifact_order
        if isinstance((stage := record.get("stage")), str) and stage in known_stage_order
    }
    missing_stage_names = [stage for stage in known_stage_order if stage not in present_stage_names]
    return {
        "known_stage_order": known_stage_order,
        "present": [stage for stage in known_stage_order if stage in present_stage_names],
        "present_count": len(present_stage_names),
        "missing": missing_stage_names,
        "missing_count": len(missing_stage_names),
        "next_missing_stage": missing_stage_names[0] if missing_stage_names else None,
        "progress_label": f"{len(present_stage_names)}/{len(known_stage_order)}",
        "complete": not missing_stage_names,
    }


def _engine_artifact_validation_report_workflow_blocked_reason(
    errors: Sequence[Mapping[str, Any]],
    stage_coverage: Mapping[str, Any],
) -> str | None:
    has_errors = bool(errors)
    missing_stages = not bool(stage_coverage.get("complete"))
    if has_errors and missing_stages:
        return "validation_errors_and_missing_stages"
    if has_errors:
        return "validation_errors"
    if missing_stages:
        return "missing_stages"
    return None


def _collect_engine_artifact_mapping_validation_error_records(
    artifacts: Mapping[str, Sequence[Any]],
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    seen_normalized_names: set[str] = set()
    named_pairs: list[tuple[str, str, Any, Any]] = []
    for name, item in artifacts.items():
        try:
            normalized_name = _normalize_terminal_artifact_cli_fallback_payload_artifact_name(name)
        except ValueError:
            continue
        normalized_unique_key = normalized_name.casefold()
        if normalized_unique_key in seen_normalized_names:
            continue
        seen_normalized_names.add(normalized_unique_key)
        if not _is_engine_artifact_pair(item):
            errors.append(
                _build_engine_artifact_validation_error_record(
                    index=len(errors),
                    location=f"stage {normalized_name!r}",
                    path=_engine_artifact_stage_path(normalized_name),
                    stage=normalized_name,
                    kind=None,
                    normalized_kind=None,
                    code="invalid_pair",
                    message=f"Engine artifact for stage {name!r} must be a (kind, artifact) pair",
                )
            )
            continue
        kind, artifact = item
        named_pairs.append((normalized_name, f"stage {normalized_name!r}", kind, artifact))

    for normalized_name, location, kind, artifact in sorted(
        named_pairs,
        key=lambda pair: _engine_a2ui_cli_fallback_stage_sort_key(pair[0]),
    ):
        try:
            _validate_engine_artifact_kind(kind, location)
            _validate_engine_artifact_payload(kind, artifact, location)
        except ValueError as exc:
            errors.append(
                _build_engine_artifact_validation_error_record(
                    index=len(errors),
                    location=location,
                    path=_engine_artifact_stage_path(normalized_name),
                    stage=normalized_name,
                    kind=kind if isinstance(kind, str) else None,
                    normalized_kind=_normalize_engine_artifact_record_kind(kind),
                    code=_engine_artifact_validation_error_code(kind, exc),
                    message=str(exc),
                )
            )
    return errors


def _collect_engine_artifact_pair_shape_error_records(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if isinstance(artifacts, Mapping):
        named_items: list[tuple[str, Any, Any]] = []
        for name, item in artifacts.items():
            try:
                normalized_name = _normalize_terminal_artifact_cli_fallback_payload_artifact_name(name)
            except ValueError:
                continue
            named_items.append((normalized_name, name, item))
        for normalized_name, original_name, item in sorted(
            named_items,
            key=lambda entry: _engine_a2ui_cli_fallback_stage_sort_key(entry[0]),
        ):
            if _is_engine_artifact_pair(item):
                continue
            errors.append(
                _build_engine_artifact_validation_error_record(
                    index=len(errors),
                    location=f"stage {normalized_name!r}",
                    path=_engine_artifact_stage_path(normalized_name),
                    stage=normalized_name,
                    kind=None,
                    normalized_kind=None,
                    code="invalid_pair",
                    message=f"Engine artifact for stage {original_name!r} must be a (kind, artifact) pair",
                )
            )
        return errors
    if (
        isinstance(artifacts, (str, bytes, Mapping, Set))
        or not isinstance(artifacts, Sequence)
        or not artifacts
    ):
        return errors
    for index, item in enumerate(artifacts):
        if _is_engine_artifact_pair(item):
            continue
        errors.append(
            _build_engine_artifact_validation_error_record(
                index=index,
                location=f"index {index}",
                path=f"$[{index}]",
                stage=None,
                kind=None,
                normalized_kind=None,
                code="invalid_pair",
                message=f"Engine artifact at index {index} must be a (kind, artifact) pair",
            )
        )
    return errors


def _collect_engine_artifact_sequence_validation_error_records(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> list[dict[str, Any]]:
    if (
        isinstance(artifacts, (str, bytes, Mapping, Set))
        or not isinstance(artifacts, Sequence)
        or not artifacts
    ):
        return []
    errors: list[dict[str, Any]] = []
    for index, item in enumerate(artifacts):
        if not _is_engine_artifact_pair(item):
            continue
        kind, artifact = item
        location = f"index {index}"
        try:
            _validate_engine_artifact_kind(kind, location)
            _validate_engine_artifact_payload(kind, artifact, location)
        except ValueError as exc:
            errors.append(
                _build_engine_artifact_validation_error_record(
                    index=index,
                    location=location,
                    path=f"$[{index}]",
                    stage=None,
                    kind=kind if isinstance(kind, str) else None,
                    normalized_kind=_normalize_engine_artifact_record_kind(kind),
                    code=_engine_artifact_validation_error_code(kind, exc),
                    message=str(exc),
                )
            )
    return errors


def _is_engine_artifact_pair(item: Any) -> bool:
    return not isinstance(item, (str, bytes)) and isinstance(item, Sequence) and len(item) == 2


def _collect_engine_artifact_stage_validation_error_records(
    artifacts: Mapping[str, Sequence[Any]],
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    normalized_names: set[str] = set()
    for index, name in enumerate(artifacts):
        try:
            normalized_name = _normalize_terminal_artifact_cli_fallback_payload_artifact_name(name)
        except ValueError as exc:
            errors.append(
                _build_engine_artifact_validation_error_record(
                    index=index,
                    location=f"stage {name!r}",
                    path=_engine_artifact_stage_path(name),
                    stage=None,
                    kind=None,
                    normalized_kind=None,
                    code="invalid_stage",
                    message=f"Engine artifact stage name {name!r} is invalid: {exc}",
                )
            )
            continue
        normalized_unique_key = normalized_name.casefold()
        if normalized_unique_key in normalized_names:
            errors.append(
                _build_engine_artifact_validation_error_record(
                    index=index,
                    location=f"stage {normalized_name!r}",
                    path=_engine_artifact_stage_path(normalized_name),
                    stage=normalized_name,
                    kind=None,
                    normalized_kind=None,
                    code="invalid_stage",
                    message="Engine artifact stage names must be unique after normalization",
                )
            )
        normalized_names.add(normalized_unique_key)
    return errors


def _build_engine_artifact_validation_error_record(
    *,
    index: int,
    location: str,
    path: str,
    stage: str | None,
    kind: str | None,
    normalized_kind: str | None,
    code: str,
    message: str,
) -> dict[str, Any]:
    return {
        "schema_version": A2UI_ENGINE_ARTIFACTS_SCHEMA_VERSION,
        "index": index,
        "location": location,
        "path": path,
        "stage": stage,
        "kind": kind,
        "normalized_kind": normalized_kind,
        "code": code,
        "message": message,
    }


def _engine_artifact_validation_record_path(location: str) -> str:
    if location.startswith("stage "):
        stage_name = _parse_engine_artifact_validation_location_stage(location)
        if stage_name is not None:
            return _engine_artifact_stage_path(stage_name)
    if location.startswith("index "):
        index = location.removeprefix("index ")
        if index.isdigit():
            return f"$[{index}]"
    return "$"


def _engine_artifact_validation_record_stage(location: str) -> str | None:
    if not location.startswith("stage "):
        return None
    return _parse_engine_artifact_validation_location_stage(location)


def _parse_engine_artifact_validation_location_stage(location: str) -> str | None:
    stage_repr = location.removeprefix("stage ")
    try:
        parsed_stage = ast.literal_eval(stage_repr)
    except (SyntaxError, ValueError):
        return None
    if isinstance(parsed_stage, str):
        return parsed_stage
    return None


def _engine_artifact_stage_path(stage_name: Any) -> str:
    rendered_stage_name = _render_terminal_inline_text(stage_name)
    return "$[" + json.dumps(rendered_stage_name, sort_keys=True) + "]"


def _engine_artifact_validation_error_code(kind: Any, exc: ValueError) -> str:
    if not isinstance(kind, str) or "unsupported kind" in str(exc):
        return "invalid_kind"
    if "kind does not match TerminalArtifact envelope" in str(exc):
        return "invalid_envelope_kind"
    return "invalid_payload"


def _normalize_engine_artifact_record_kind(kind: Any) -> str | None:
    if not isinstance(kind, str) or not kind.strip():
        return None
    return kind.strip().lower()


def _collect_engine_artifact_pairs(
    artifacts: Mapping[str, Sequence[Any]] | Sequence[Sequence[Any]],
) -> list[tuple[str, Any, Any]]:
    pairs: list[tuple[str, Any, Any]] = []

    if isinstance(artifacts, Mapping):
        if not artifacts:
            raise ValueError("Engine artifacts must contain at least one artifact")
        normalized_names: set[str] = set()
        named_pairs: list[tuple[str, str, Any, Any]] = []
        for name, item in artifacts.items():
            try:
                normalized_name = _normalize_terminal_artifact_cli_fallback_payload_artifact_name(name)
            except ValueError as exc:
                raise ValueError(f"Engine artifact stage name {name!r} is invalid: {exc}") from exc
            normalized_unique_key = normalized_name.casefold()
            if normalized_unique_key in normalized_names:
                raise ValueError("Engine artifact stage names must be unique after normalization")
            normalized_names.add(normalized_unique_key)
            if isinstance(item, (str, bytes)) or not isinstance(item, Sequence) or len(item) != 2:
                raise ValueError(
                    f"Engine artifact for stage {name!r} must be a (kind, artifact) pair"
                )
            kind, artifact = item
            named_pairs.append((normalized_name, f"stage {normalized_name!r}", kind, artifact))
        pairs.extend(
            (location, kind, artifact)
            for _, location, kind, artifact in sorted(
                named_pairs,
                key=lambda pair: _engine_a2ui_cli_fallback_stage_sort_key(pair[0]),
            )
        )
    elif (
        isinstance(artifacts, (str, bytes, Mapping, Set))
        or not isinstance(artifacts, Sequence)
    ):
        raise ValueError("Engine artifacts must be a mapping or ordered sequence")
    else:
        if not artifacts:
            raise ValueError("Engine artifacts must contain at least one artifact")
        for index, item in enumerate(artifacts):
            if isinstance(item, (str, bytes)) or not isinstance(item, Sequence) or len(item) != 2:
                raise ValueError(f"Engine artifact at index {index} must be a (kind, artifact) pair")
            kind, artifact = item
            pairs.append((f"index {index}", kind, artifact))
    return pairs


def _validate_engine_artifact_kind(kind: Any, location: str) -> None:
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError(f"Engine artifact at {location} must declare a non-empty string kind")
    normalized = kind.strip().lower()
    if normalized not in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        raise ValueError(
            f"Engine artifact at {location} has unsupported kind {kind!r}; "
            f"must be one of {sorted(_TERMINAL_ARTIFACT_SUPPORTED_KIND_SET)}"
        )


def _validate_engine_artifact_payload(kind: str, artifact: Any, location: str) -> None:
    normalized_kind = kind.strip().lower()
    try:
        artifact = _unwrap_terminal_artifact_for_kind(artifact, kind=normalized_kind)
        if normalized_kind == "action":
            validate_action_ref(artifact)
        elif normalized_kind == "selection":
            validate_selection_ref(artifact)
        elif normalized_kind == "card":
            _validate_terminal_artifact_card_payload(artifact)
    except ValueError as exc:
        raise ValueError(
            f"Engine artifact at {location} (kind={kind!r}) is invalid: {exc}"
        ) from exc


def _normalize_terminal_artifact_cli_fallback_payload_artifact_name(name: Any) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Named TerminalArtifact fallback artifact names must be non-empty strings")
    normalized_name = unicodedata.normalize("NFC", name.strip())
    if any(unicodedata.category(char).startswith("C") for char in normalized_name):
        raise ValueError("Named TerminalArtifact fallback artifact names must not contain control characters")
    return normalized_name


def _engine_a2ui_cli_fallback_stage_sort_key(name: str) -> tuple[int, int, str]:
    stage_order = {
        stage_name: index
        for index, stage_name in enumerate(ENGINE_A2UI_CLI_FALLBACK_STAGE_ORDER)
    }
    normalized_name = name.casefold()
    if normalized_name in stage_order:
        return (0, stage_order[normalized_name], normalized_name)
    return (1, len(stage_order), normalized_name)


def _render_terminal_artifact_cli_fallback_payload_text(cli_fallback: Sequence[Mapping[str, Any]]) -> str:
    return TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_RENDER_SEPARATOR.join(
        entry["text"] for entry in cli_fallback
    )


def _terminal_artifact_cli_fallback_payload_artifact_id(
    envelope: Mapping[str, Any],
    *,
    index: int,
    artifact_fingerprint: str | None = None,
) -> str:
    fingerprint = artifact_fingerprint
    if fingerprint is None:
        fingerprint = _fingerprint_manifest_section(envelope)
    fingerprint_prefix = fingerprint[
        :TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ID_FINGERPRINT_PREFIX_CHARS
    ]
    return f"{index}:{envelope['kind']}:{fingerprint_prefix}"


def _terminal_artifact_cli_fallback_payload_artifact_order_entry(
    envelope: Mapping[str, Any],
    *,
    index: int,
    artifact_fingerprint: str | None = None,
) -> dict[str, Any]:
    fingerprint = artifact_fingerprint
    if fingerprint is None:
        fingerprint = _fingerprint_manifest_section(envelope)
    return {
        "index": index,
        "artifact_id": _terminal_artifact_cli_fallback_payload_artifact_id(
            envelope,
            index=index,
            artifact_fingerprint=fingerprint,
        ),
        "kind": envelope["kind"],
        "artifact_fingerprint": fingerprint,
    }


def _is_terminal_artifact_cli_fallback_payload_artifact_id_shape(
    artifact_id: str,
    *,
    index: int,
    kind: str,
    artifact_fingerprint: str,
) -> bool:
    prefix, separator, fingerprint_prefix = artifact_id.rpartition(":")
    expected_fingerprint_prefix = artifact_fingerprint[
        :TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ID_FINGERPRINT_PREFIX_CHARS
    ]
    if not separator or fingerprint_prefix != expected_fingerprint_prefix:
        return False
    index_text, separator, artifact_kind = prefix.partition(":")
    if not separator or artifact_kind != kind:
        return False
    return index_text == str(index)


def _validate_terminal_artifact_cli_fallback_payload_artifact_id_uniqueness(
    cli_fallback: Sequence[Any],
) -> None:
    artifact_ids: set[str] = set()
    for fallback in cli_fallback:
        if not isinstance(fallback, Mapping):
            continue
        artifact_id = fallback.get("artifact_id")
        if type(artifact_id) is not str:
            continue
        if artifact_id in artifact_ids:
            raise ValueError("TerminalArtifactCliFallbackPayload artifact_id values must be unique")
        artifact_ids.add(artifact_id)


def render_terminal_artifact_cli_fallback_payload(payload: Any) -> str:
    """Render a validated shared fallback payload as deterministic CLI text."""

    validate_terminal_artifact_cli_fallback_payload(payload)
    return payload["rendered_text"]


def resolve_terminal_artifact_cli_fallback_payload_artifact(
    payload: Any,
    artifact_id: str,
) -> dict[str, Any]:
    """Return the versioned artifact envelope addressed by a CLI fallback payload id."""

    validate_terminal_artifact_cli_fallback_payload(payload)
    if type(artifact_id) is not str or not artifact_id.strip():
        raise ValueError("TerminalArtifactCliFallbackPayload artifact_id must be a non-empty string")
    for order_entry in payload["artifact_order"]:
        if order_entry["artifact_id"] == artifact_id:
            return copy.deepcopy(payload["artifacts"][order_entry["index"]])
    raise ValueError("TerminalArtifactCliFallbackPayload artifact_id is unknown")


def _is_terminal_artifact_cli_fallback_payload(payload: Any) -> bool:
    return (
        isinstance(payload, Mapping)
        and payload.get("type") == "TerminalArtifactCliFallbackPayload"
    )


def describe_terminal_artifact_cli_fallback_payload_contract() -> dict[str, Any]:
    """Return the stable shared payload contract for terminal artifact CLI fallback."""

    manifest = _build_terminal_artifact_cli_fallback_payload_contract_manifest()
    fingerprint = _fingerprint_manifest_section(manifest)
    manifest["contract_fingerprint"] = fingerprint
    manifest["contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["contract_manifest_fingerprint"] = fingerprint
    return manifest


def _unwrap_terminal_artifact_for_kind(artifact: Any, *, kind: str) -> Any:
    if not isinstance(artifact, Mapping):
        return artifact
    extracted = _extract_terminal_artifact_envelope(artifact)
    if extracted is None:
        return artifact
    _, envelope_kind = extracted
    if envelope_kind != kind:
        raise ValueError("kind does not match TerminalArtifact envelope")
    unwrapped_artifact, _ = _unwrap_terminal_artifact_payload(artifact)
    return unwrapped_artifact


def normalize_terminal_artifact_payload(artifact: Any, *, kind: str | None = None) -> dict[str, Any]:
    """Return the canonical payload snapshot for a structured terminal artifact.

    Action and selection payloads are normalized through the public ref
    validators before being converted to plain dictionaries. Canonical
    ``ActionRef`` and ``SelectionRef`` mappings may include a ``type`` hint
    when they arrive from the renderer path, and that hint is stripped before
    validation so the stored envelope stays on the canonical leaf shape. Card
    payloads are copied as mappings or dataclass snapshots so the envelope does
    not retain references to mutable source objects. Card action lists are
    canonicalized into a deterministic order so equivalent payloads produce the
    same envelope snapshot. Same-kind ``TerminalArtifact`` envelopes are
    unwrapped before snapshotting so the builder stays idempotent across
    repeated wrapping. Unordered set-like values are converted to sorted lists
    so the snapshot stays deterministic and JSON-safe.
    """

    normalized_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    artifact = _unwrap_terminal_artifact_for_kind(artifact, kind=normalized_kind)
    if normalized_kind == "action":
        if isinstance(artifact, Mapping):
            artifact = _strip_terminal_type_hint(artifact, expected_type="ActionRef")
        return _action_ref_to_dict(normalize_action_ref(artifact))
    if normalized_kind == "selection":
        if isinstance(artifact, Mapping):
            artifact = _strip_terminal_type_hint(artifact, expected_type="SelectionRef")
        return _selection_ref_to_dict(normalize_selection_ref(artifact))
    _validate_terminal_artifact_card_payload(artifact)
    card_snapshot = _coerce_terminal_card(artifact)
    if card_snapshot is None:
        raise ValueError("TerminalArtifact card artifact must be a mapping or card-like object")
    if _should_preserve_raw_leaf_card_default(card_snapshot):
        return _copy_terminal_artifact_payload(card_snapshot)
    card_snapshot = _canonicalize_card_top_level_fields(card_snapshot)
    card_snapshot = _copy_terminal_artifact_payload(card_snapshot)
    return _canonicalize_terminal_artifact_card_actions(card_snapshot)


def validate_terminal_artifact_envelope(envelope: Any) -> None:
    if not isinstance(envelope, Mapping):
        raise ValueError("TerminalArtifact must be an object")
    extra_keys = set(envelope) - {
        "type",
        "kind",
        "artifact",
        "contract_version",
        "a2ui_version",
    }
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected TerminalArtifact field(s): {extras}")
    artifact_type = envelope.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        raise ValueError("TerminalArtifact type must be TerminalArtifact")
    if "kind" not in envelope:
        raise ValueError("TerminalArtifact kind is required")
    kind = envelope.get("kind")
    if not isinstance(kind, str):
        raise ValueError("TerminalArtifact kind must be a string")
    normalized_kind = kind.strip().lower()
    if normalized_kind not in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        raise ValueError("TerminalArtifact kind must be one of: card, action, selection")
    if kind != normalized_kind:
        raise ValueError("TerminalArtifact kind must be canonical")
    if "artifact" not in envelope:
        raise ValueError("TerminalArtifact artifact is required")
    if envelope.get("artifact") is None:
        raise ValueError("TerminalArtifact artifact is required")
    contract_version = envelope.get("contract_version")
    if contract_version is not None and (
        type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION
    ):
        raise ValueError("TerminalArtifact contract_version is invalid")
    a2ui_version = envelope.get("a2ui_version")
    if a2ui_version is not None and type(a2ui_version) is not int:
        raise ValueError("TerminalArtifact a2ui_version is invalid")
    if a2ui_version is not None and a2ui_version != A2UI_VERSION:
        raise ValueError("TerminalArtifact a2ui_version is invalid")
    _validate_terminal_artifact_payload_kind(envelope["artifact"], normalized_kind)


def _validate_versioned_terminal_artifact_envelope(envelope: Any) -> None:
    if not isinstance(envelope, Mapping):
        raise ValueError("TerminalArtifactCliFallbackPayload artifacts entries must be objects")
    missing_keys = set(_TERMINAL_ARTIFACT_ENVELOPE_REQUIRED_FIELDS) - set(envelope)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing TerminalArtifactCliFallbackPayload artifact field(s): {missing}")
    validate_terminal_artifact_envelope(envelope)


def _validate_terminal_artifact_cli_fallback_payload_artifact_entries(
    artifacts: Sequence[Any],
) -> None:
    for envelope in artifacts:
        if not isinstance(envelope, Mapping):
            raise ValueError("TerminalArtifactCliFallbackPayload artifacts entries must be objects")
        missing_keys = set(_TERMINAL_ARTIFACT_ENVELOPE_REQUIRED_FIELDS) - set(envelope)
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ValueError(f"Missing TerminalArtifactCliFallbackPayload artifact field(s): {missing}")


def validate_terminal_artifact_cli_fallback_payload(payload: Any) -> None:
    if not isinstance(payload, Mapping):
        raise ValueError("TerminalArtifactCliFallbackPayload must be an object")
    missing_keys = set(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_REQUIRED_FIELDS) - set(payload)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing TerminalArtifactCliFallbackPayload field(s): {missing}")
    extra_keys = set(payload) - set(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_REQUIRED_FIELDS)
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected TerminalArtifactCliFallbackPayload field(s): {extras}")
    if payload.get("type") != "TerminalArtifactCliFallbackPayload":
        raise ValueError("TerminalArtifactCliFallbackPayload type is invalid")
    schema_version = payload.get("schema_version")
    if (
        type(schema_version) is not int
        or schema_version != TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_SCHEMA_VERSION
    ):
        raise ValueError("TerminalArtifactCliFallbackPayload schema_version is invalid")
    contract_version = payload.get("contract_version")
    if type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION:
        raise ValueError("TerminalArtifactCliFallbackPayload contract_version is invalid")
    a2ui_version = payload.get("a2ui_version")
    if type(a2ui_version) is not int or a2ui_version != A2UI_VERSION:
        raise ValueError("TerminalArtifactCliFallbackPayload a2ui_version is invalid")
    artifact_count = payload.get("artifact_count")
    if type(artifact_count) is not int:
        raise ValueError("TerminalArtifactCliFallbackPayload artifact_count must be an integer")
    if artifact_count < 1:
        raise ValueError("TerminalArtifactCliFallbackPayload must contain at least one artifact")
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("TerminalArtifactCliFallbackPayload artifacts must be a list")
    cli_fallback = payload.get("cli_fallback")
    if not isinstance(cli_fallback, list):
        raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback must be a list")
    if artifact_count != len(artifacts) or artifact_count != len(cli_fallback):
        raise ValueError("TerminalArtifactCliFallbackPayload artifact_count is invalid")
    if len(artifacts) != len(cli_fallback):
        raise ValueError("TerminalArtifactCliFallbackPayload artifacts and cli_fallback must align")
    _validate_terminal_artifact_cli_fallback_payload_artifact_entries(artifacts)
    _validate_terminal_artifact_cli_fallback_payload_artifact_id_uniqueness(cli_fallback)
    artifact_order = payload.get("artifact_order")
    if not isinstance(artifact_order, list):
        raise ValueError("TerminalArtifactCliFallbackPayload artifact_order must be a list")
    if len(artifact_order) != artifact_count:
        raise ValueError("TerminalArtifactCliFallbackPayload artifact_order length is invalid")
    expected_artifact_order = [
        _terminal_artifact_cli_fallback_payload_artifact_order_entry(envelope, index=index)
        if isinstance(envelope, Mapping) and isinstance(envelope.get("kind"), str)
        else {
            "index": index,
            "artifact_id": None,
            "kind": envelope.get("kind") if isinstance(envelope, Mapping) else None,
            "artifact_fingerprint": _fingerprint_manifest_section(envelope),
        }
        for index, envelope in enumerate(artifacts)
    ]
    for index, order_entry in enumerate(artifact_order):
        if not isinstance(order_entry, Mapping):
            raise ValueError("TerminalArtifactCliFallbackPayload artifact_order entries must be objects")
        order_missing_keys = set(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ORDER_FIELDS) - set(order_entry)
        if order_missing_keys:
            missing = ", ".join(sorted(order_missing_keys))
            raise ValueError(f"Missing TerminalArtifactCliFallbackPayload artifact_order field(s): {missing}")
        order_extra_keys = set(order_entry) - set(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_ARTIFACT_ORDER_FIELDS)
        if order_extra_keys:
            extras = ", ".join(sorted(order_extra_keys))
            raise ValueError(f"Unexpected TerminalArtifactCliFallbackPayload artifact_order field(s): {extras}")
        if dict(order_entry) != expected_artifact_order[index]:
            raise ValueError("TerminalArtifactCliFallbackPayload artifact_order is stale")
    artifact_order_fingerprint = payload.get("artifact_order_fingerprint")
    if (
        type(artifact_order_fingerprint) is not str
        or artifact_order_fingerprint != _fingerprint_manifest_section(artifact_order)
    ):
        raise ValueError("TerminalArtifactCliFallbackPayload artifact_order_fingerprint is stale")
    for index, envelope in enumerate(artifacts):
        _validate_versioned_terminal_artifact_envelope(envelope)
        fallback = cli_fallback[index]
        if not isinstance(fallback, Mapping):
            raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback entries must be objects")
        fallback_missing_keys = set(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_CLI_ENTRY_FIELDS) - set(fallback)
        if fallback_missing_keys:
            missing = ", ".join(sorted(fallback_missing_keys))
            raise ValueError(f"Missing TerminalArtifactCliFallbackPayload cli_fallback field(s): {missing}")
        fallback_extra_keys = set(fallback) - set(_TERMINAL_ARTIFACT_CLI_FALLBACK_PAYLOAD_CLI_ENTRY_FIELDS)
        if fallback_extra_keys:
            extras = ", ".join(sorted(fallback_extra_keys))
            raise ValueError(f"Unexpected TerminalArtifactCliFallbackPayload cli_fallback field(s): {extras}")
        fallback_index = fallback.get("index")
        if type(fallback_index) is not int or fallback_index != index:
            raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback index is invalid")
        fallback_kind = fallback.get("kind")
        if type(fallback_kind) is not str or fallback_kind != envelope["kind"]:
            raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback kind must match artifact kind")
        artifact_fingerprint = fallback.get("artifact_fingerprint")
        if (
            type(artifact_fingerprint) is not str
            or artifact_fingerprint != _fingerprint_manifest_section(envelope)
        ):
            raise ValueError("TerminalArtifactCliFallbackPayload artifact_fingerprint is stale")
        artifact_id = fallback.get("artifact_id")
        if (
            type(artifact_id) is not str
            or not _is_terminal_artifact_cli_fallback_payload_artifact_id_shape(
                artifact_id,
                index=index,
                kind=envelope["kind"],
                artifact_fingerprint=artifact_fingerprint,
            )
            or artifact_id
            != _terminal_artifact_cli_fallback_payload_artifact_id(
                envelope,
                index=index,
                artifact_fingerprint=artifact_fingerprint,
            )
        ):
            raise ValueError("TerminalArtifactCliFallbackPayload artifact_id is stale")
        fallback_text = fallback.get("text")
        expected_text = render_terminal_cli_fallback(envelope, kind=envelope["kind"])
        if type(fallback_text) is not str or fallback_text != expected_text:
            raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback text is stale")
        if not _is_nonempty_terminal_rendered_text(fallback_text):
            raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback text must be non-empty")
        text_fingerprint = fallback.get("text_fingerprint")
        if (
            type(text_fingerprint) is not str
            or text_fingerprint != _fingerprint_manifest_section(fallback_text)
        ):
            raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback text_fingerprint is stale")
    cli_fallback_fingerprint = payload.get("cli_fallback_fingerprint")
    if (
        type(cli_fallback_fingerprint) is not str
        or cli_fallback_fingerprint != _fingerprint_manifest_section(cli_fallback)
    ):
        raise ValueError("TerminalArtifactCliFallbackPayload cli_fallback_fingerprint is stale")
    rendered_text = payload.get("rendered_text")
    expected_rendered_text = _render_terminal_artifact_cli_fallback_payload_text(cli_fallback)
    if type(rendered_text) is not str or rendered_text != expected_rendered_text:
        raise ValueError("TerminalArtifactCliFallbackPayload rendered_text is stale")
    if not _is_nonempty_terminal_rendered_text(rendered_text):
        raise ValueError("TerminalArtifactCliFallbackPayload rendered_text must be non-empty")
    rendered_text_fingerprint = payload.get("rendered_text_fingerprint")
    if (
        type(rendered_text_fingerprint) is not str
        or rendered_text_fingerprint != _fingerprint_manifest_section(rendered_text)
    ):
        raise ValueError("TerminalArtifactCliFallbackPayload rendered_text_fingerprint is stale")
    payload_fingerprint = payload.get("payload_fingerprint")
    fingerprint_input = dict(payload)
    fingerprint_input.pop("payload_fingerprint", None)
    if type(payload_fingerprint) is not str or payload_fingerprint != _fingerprint_manifest_section(
        fingerprint_input
    ):
        raise ValueError("TerminalArtifactCliFallbackPayload payload_fingerprint is stale")


@lru_cache(maxsize=None)
def _build_a2ui_contract_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
    include_contract_fingerprints: bool = True,
) -> dict[str, Any]:
    terminal_artifact_contract = describe_terminal_artifact_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    card_hint_recovery_policy_contract = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "capabilities": describe_a2ui_capabilities_contract(),
        "card_contract": describe_card_contract(),
        "terminal_fallback": describe_terminal_fallback_contract(),
        "terminal_artifact": terminal_artifact_contract,
        "terminal_fallback_fingerprint": terminal_fallback_contract_fingerprint(),
        "terminal_artifact_fingerprint": terminal_artifact_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "terminal_artifact_supported_kinds": list(terminal_artifact_contract["supported_kinds"]),
        "terminal_artifact_supported_kinds_fingerprint": _fingerprint_manifest_section(
            terminal_artifact_contract["supported_kinds"]
        ),
        "cards": {
            "generic": GENERIC_CARD_TYPE,
            "unknown": UNKNOWN_CARD_TYPE,
            "reserved": list(_RESERVED_CARD_TYPES),
            "specialized": list(_SPECIALIZED_CARD_TYPES),
        },
        "selection": describe_selection_contract(),
        "action": describe_action_contract(),
        "terminal_artifact_envelope": describe_terminal_artifact_envelope_contract(),
        "fallbacks": _build_card_fallback_manifest(),
        "schemas": _build_a2ui_schema_manifest(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "primitive_blocks": [
            {
                "type": block_type,
                "fields": list(_PRIMITIVE_BLOCK_SCHEMAS[block_type]),
            }
            for block_type in REQUIRED_PRIMITIVE_BLOCKS
        ],
        "actions": [
            {
                "id": action_id,
                "version": A2UI_ACTION_SCHEMA_VERSION,
                "payload_fields": sorted(schema),
            }
            for action_id, schema in sorted(_ACTION_SCHEMAS.items())
        ],
    }
    if (
        include_terminal_artifact_cli_fallback_entrypoint
        or include_terminal_artifact_cli_fallback_card_hint_recovery_policy
        or include_shell_ui_contract
    ):
        manifest["card_hint_recovery_policy"] = _snapshot_contract_section(card_hint_recovery_policy_contract)
        manifest["card_hint_recovery_policy_fingerprint"] = card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ]
        manifest["card_hint_recovery_policy_contract"] = _snapshot_contract_section(
            card_hint_recovery_policy_contract
        )
        manifest["card_hint_recovery_policy_contract_fingerprint"] = card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ]
        manifest["card_hint_recovery_policy_contract_manifest"] = _snapshot_contract_section(
            card_hint_recovery_policy_contract
        )
        manifest["card_hint_recovery_policy_contract_manifest_fingerprint"] = card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ]
    if include_shell_ui_contract:
        shell_ui_contract = _snapshot_shell_ui_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
        shell_ui_contract_manifest_fingerprint = _a2ui_shell_ui_contract_manifest_fingerprint(
            shell_ui_contract,
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
        manifest["shell_ui_contract"] = shell_ui_contract
        manifest["shell_ui_contract_fingerprint"] = shell_ui_contract["contract_fingerprint"]
        manifest["shell_ui_fingerprint"] = shell_ui_contract["contract_fingerprint"]
        shell_ui_contract_manifest = _snapshot_contract_section(shell_ui_contract)
        shell_ui_contract_manifest["contract_fingerprint"] = shell_ui_contract_manifest_fingerprint
        shell_ui_contract_manifest["shell_ui_contract_manifest_fingerprint"] = (
            shell_ui_contract_manifest_fingerprint
        )
        manifest["shell_ui_contract_manifest"] = shell_ui_contract_manifest
        manifest["shell_ui_contract_manifest_fingerprint"] = shell_ui_contract_manifest_fingerprint
        manifest["shell_ui_contract_fingerprints"] = _snapshot_contract_section(
            shell_ui_contract["contract_fingerprints"]
        )
        manifest["shell_ui_contract_fingerprints_fingerprint"] = shell_ui_contract[
            "contract_fingerprints_fingerprint"
        ]
        manifest["shell_ui_contract_manifest_fingerprints"] = _snapshot_contract_section(
            shell_ui_contract["shell_ui_contract_manifest_fingerprints"]
        )
        manifest["shell_ui_contract_manifest_fingerprints_fingerprint"] = shell_ui_contract[
            "shell_ui_contract_manifest_fingerprints_fingerprint"
        ]
        # Mirror the shell's renderer-entrypoint alias so shell-aware
        # consumers can negotiate the same renderer contract names.
        manifest["terminal_artifact_renderer_entrypoints_contract"] = _snapshot_contract_section(
            shell_ui_contract["terminal_artifact_renderer_entrypoints_contract"]
        )
        manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"] = shell_ui_contract[
            "terminal_artifact_renderer_entrypoints_contract_fingerprint"
        ]
        terminal_artifact_renderer_entrypoints_contract_fingerprint_value = (
            terminal_artifact_renderer_entrypoints_contract_fingerprint()
        )
        manifest["terminal_artifact_renderer_entrypoints_contract_manifest"] = (
            describe_terminal_artifact_renderer_entrypoints_contract()
        )
        manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"] = (
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        )
        manifest["terminal_artifact_cli_fallback_entrypoint"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_entrypoint"
        ]
        manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_entrypoint_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_entrypoint_schema_version"] = (
            shell_ui_contract["terminal_artifact_cli_fallback_entrypoint_contract_manifest"][
                "terminal_artifact_cli_fallback_entrypoint_schema_version"
            ]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_version"] = (
            shell_ui_contract["terminal_artifact_cli_fallback_entrypoint_contract_manifest"][
                "terminal_artifact_cli_fallback_entrypoint_version"
            ]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_entrypoint_contract"
        ]
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"] = (
            describe_terminal_artifact_cli_fallback_entrypoint_contract()
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"
        ]
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_target_contract_fingerprints"
        ]
        manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"] = shell_ui_contract[
            "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"
        ]
        if include_shell_ui_contract:
            manifest["terminal_artifact_cli_fallback_route"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route"]
            )
            manifest["terminal_artifact_cli_fallback_route_contract"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route_contract"]
            )
            manifest["terminal_artifact_cli_fallback_route_contract_manifest"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route_contract_manifest"]
            )
            manifest["terminal_artifact_cli_fallback_route_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_fingerprint"
            ]
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_contract_fingerprint"
            ]
            manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"
            ]
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route_contract_fingerprints"]
            )
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"
            ]
        terminal_artifact_cli_fallback_contract = _snapshot_contract_section(
            describe_terminal_artifact_cli_fallback_contract()
        )
        manifest["terminal_artifact_cli_fallback_contract_manifest"] = terminal_artifact_cli_fallback_contract
        manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_contract["contract_fingerprint"]
        )
    if include_terminal_artifact_cli_fallback_entrypoint:
        engine_artifacts_contract = describe_engine_artifacts_contract()
        manifest["engine_artifacts_contract"] = _snapshot_contract_section(engine_artifacts_contract)
        manifest["engine_artifacts_contract_fingerprint"] = engine_artifacts_contract[
            "contract_fingerprint"
        ]
        terminal_artifact_cli_fallback_entrypoint_contract = _snapshot_terminal_artifact_cli_fallback_entrypoint_contract()
        terminal_artifact_renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
        manifest["terminal_artifact_cli_fallback_entrypoint"] = terminal_artifact_cli_fallback_entrypoint_contract[
            "terminal_artifact_cli_fallback_entrypoint"
        ]
        manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract["terminal_artifact_cli_fallback_entrypoint_fingerprint"]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_schema_version"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_entrypoint_schema_version"
            ]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_version"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_entrypoint_version"
            ]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_entrypoint_contract
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract["contract_fingerprint"]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"] = (
            terminal_artifact_cli_fallback_entrypoint_contract
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"] = (
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"
            ]
        )
        manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"
            ]
        )
        manifest["terminal_artifact_renderer_entrypoints_contract"] = _snapshot_contract_section(
            terminal_artifact_renderer_entrypoints_contract
        )
        manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"] = (
            terminal_artifact_renderer_entrypoints_contract["contract_fingerprint"]
        )
        manifest["terminal_artifact_renderer_entrypoints_contract_manifest"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_entrypoint_contract[
                "terminal_artifact_renderer_entrypoints_contract_manifest"
            ]
        )
        manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"] = (
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        )
        terminal_artifact_cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
        manifest["terminal_artifact_cli_fallback_target"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract
        )
        manifest["terminal_artifact_cli_fallback_target_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        manifest["terminal_artifact_cli_fallback_target_contract"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract
        )
        manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        manifest["terminal_artifact_cli_fallback_target_contract_manifest"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract
        )
        manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprint"]
        )
        manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"] = _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints_fingerprint"]
        )
        if include_shell_ui_contract:
            manifest["terminal_artifact_cli_fallback_route"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route"]
            )
            manifest["terminal_artifact_cli_fallback_route_contract"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route_contract"]
            )
            manifest["terminal_artifact_cli_fallback_route_contract_manifest"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route_contract_manifest"]
            )
            manifest["terminal_artifact_cli_fallback_route_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_fingerprint"
            ]
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_contract_fingerprint"
            ]
            manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"
            ]
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
                shell_ui_contract["terminal_artifact_cli_fallback_route_contract_fingerprints"]
            )
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = shell_ui_contract[
                "terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"
            ]
    if include_terminal_artifact_cli_fallback_route:
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        route_contract_snapshot = _snapshot_contract_section(route_contract)
        route_contract_manifest = _snapshot_contract_section(route_contract)
        manifest["terminal_artifact_cli_fallback_route"] = route_contract_snapshot
        manifest["terminal_artifact_cli_fallback_route_contract"] = _snapshot_contract_section(route_contract)
        manifest["terminal_artifact_cli_fallback_route_contract_manifest"] = route_contract_manifest
        manifest["terminal_artifact_cli_fallback_route_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = manifest[
            "terminal_artifact_cli_fallback_route_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"] = manifest[
            "terminal_artifact_cli_fallback_route_fingerprint"
        ]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
            route_contract["contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = route_contract[
            "contract_fingerprints_fingerprint"
        ]
    return manifest


def _build_a2ui_capabilities_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_version": A2UI_CAPABILITIES_SCHEMA_VERSION,
        "capabilities_schema_version": A2UI_CAPABILITIES_SCHEMA_VERSION,
        "capabilities_version": A2UI_CAPABILITIES_SCHEMA_VERSION,
        "type": "A2UICapabilities",
        "message_type": "A2UI_CAPABILITIES",
        "session_scope": "per-session",
        "required_fields": list(_CAPABILITIES_REQUIRED_FIELDS),
        "optional_fields": [],
        "field_contracts": _build_a2ui_capabilities_field_contracts(),
    }


def _validate_terminal_artifact_payload_kind(artifact: Any, kind: str) -> None:
    if kind == "card":
        card_artifact = _coerce_terminal_card(artifact)
        if card_artifact is None:
            raise ValueError("TerminalArtifact card artifact must be a mapping or card-like object")
        card_type = _normalize_card_type(card_artifact)
        if card_type in {_TERMINAL_ARTIFACT_ENVELOPE_TYPE, "ActionRef", "SelectionRef"}:
            raise ValueError("TerminalArtifact card artifact must be a typed card")
        if card_type == "<missing>" and not _should_preserve_raw_leaf_card_default(card_artifact):
            raise ValueError("TerminalArtifact card artifact must be a typed card")
        if _infer_terminal_artifact_kind_from_mapping(card_artifact) in {"action", "selection"}:
            raise ValueError("TerminalArtifact card artifact must not use action or selection payload shape")
        return
    if kind == "action":
        try:
            if isinstance(artifact, Mapping):
                artifact = _strip_terminal_type_hint(artifact, expected_type="ActionRef")
            normalize_action_ref(artifact)
        except ValueError as exc:
            raise ValueError("TerminalArtifact action artifact is invalid") from exc
        return
    if kind == "selection":
        try:
            if isinstance(artifact, Mapping):
                artifact = _strip_terminal_type_hint(artifact, expected_type="SelectionRef")
            normalize_selection_ref(artifact)
        except ValueError as exc:
            raise ValueError("TerminalArtifact selection artifact is invalid") from exc
        return
    raise ValueError("TerminalArtifact kind must be one of: card, action, selection")


def _validate_terminal_artifact_card_payload(artifact: Any) -> None:
    if _is_explicit_terminal_artifact_leaf_mapping(artifact):
        raise ValueError("TerminalArtifact card artifact must not use action or selection payload shape")
    inferred_kind = _normalize_terminal_artifact_kind(artifact, kind=None)
    if inferred_kind in {"action", "selection"}:
        raise ValueError("TerminalArtifact card artifact must not use action or selection payload shape")
    if isinstance(artifact, Mapping):
        if all(field in artifact for field in ("id", "label", "payload")) and not any(
            field in artifact for field in ("blocks", "actions")
        ):
            raise ValueError("TerminalArtifact card artifact must not use action or selection payload shape")


def _build_selection_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_version": SELECTION_SCHEMA_VERSION,
        "selection_schema_version": SELECTION_SCHEMA_VERSION,
        "selection_version": SELECTION_SCHEMA_VERSION,
        "selection_contract_version": SELECTION_SCHEMA_VERSION,
        "type": "SelectionRef",
        "required_fields": ["id", "label", "payload"],
        "optional_fields": ["selected", "disabled"],
        "normalization": {
            "id": "trimmed non-empty string",
            "label": "trimmed non-empty string",
            "payload": "object copy",
            "selected": "bool default false",
            "disabled": "bool default false",
        },
    }


def _build_action_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_version": A2UI_ACTION_SCHEMA_VERSION,
        "action_schema_version": A2UI_ACTION_SCHEMA_VERSION,
        "action_version": A2UI_ACTION_SCHEMA_VERSION,
        "action_contract_version": A2UI_ACTION_SCHEMA_VERSION,
        "type": "ActionRef",
        "required_fields": ["id", "label", "payload"],
        "optional_fields": ["confirm", "policy_sensitive"],
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "payload_schemas": _build_action_payload_schema_manifest(include_string_policy_fields=True),
        "payload_string_policy": _build_action_payload_string_policy_manifest(),
    }


def _build_action_payload_string_policy_manifest() -> dict[str, Any]:
    free_text_fields = {
        action_id: sorted(fields)
        for action_id, fields in sorted(_ACTION_PAYLOAD_FREE_TEXT_FIELDS.items())
    }
    identifier_fields = {
        action_id: sorted(fields)
        for action_id, fields in sorted(_ACTION_PAYLOAD_IDENTIFIER_FIELDS.items())
        if fields
    }
    return {
        "canonical_fields": "string payload fields are stripped and must be non-empty unless marked free_text",
        "identifier_fields": identifier_fields,
        "free_text_fields": free_text_fields,
    }


def _build_card_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_version": CARD_CONTRACT_VERSION,
        "card_contract_version": CARD_CONTRACT_VERSION,
        "card_version": CARD_CONTRACT_VERSION,
        "type": "CardContract",
        "card_schemas": _build_card_schema_manifest(),
        "fallbacks": _build_card_fallback_manifest(),
    }


def _build_terminal_fallback_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_version": TERMINAL_FALLBACK_SCHEMA_VERSION,
        "terminal_fallback_schema_version": TERMINAL_FALLBACK_SCHEMA_VERSION,
        "terminal_fallback_version": TERMINAL_FALLBACK_SCHEMA_VERSION,
        "type": "TerminalFallbackContract",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "read_only_action": _build_read_only_fallback_action_manifest()[0],
        "card_fallbacks": _build_card_fallback_manifest(),
    }


def _build_terminal_artifact_contract_manifest(
    *,
    include_contract_fingerprints: bool = True,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    rendering_contract = describe_terminal_artifact_rendering_contract()
    cli_fallback_contract = describe_terminal_artifact_cli_fallback_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "type": "TerminalArtifactContract",
        "envelope": describe_terminal_artifact_envelope_contract(),
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "render_target_contract": render_target_contract,
        "rendering": rendering_contract,
        "terminal_artifact_rendering": _snapshot_contract_section(rendering_contract),
        "terminal_artifact_render_target_contract": _snapshot_contract_section(render_target_contract),
        "terminal_artifact_rendering_contract": _snapshot_contract_section(rendering_contract),
        "kind_contracts": _build_terminal_artifact_kind_contracts(),
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(
            cli_fallback_target_contract["raw_leaf_card_default_policy"]
        ),
        "resolver_failure_policy": copy.deepcopy(
            cli_fallback_contract["resolver_failure_policy"]
        ),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        ),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "terminal_fallback_contract": {
            "kind": "card",
            "contract_fingerprint": terminal_fallback_contract_fingerprint(),
        },
        "terminal_fallback_fingerprint": terminal_fallback_contract_fingerprint(),
        "cli_fallback": _snapshot_contract_section(cli_fallback_contract),
        "terminal_artifact_cli_fallback": _snapshot_contract_section(cli_fallback_contract),
        "cli_fallback_contract": _snapshot_contract_section(cli_fallback_contract),
        "terminal_artifact_cli_fallback_contract": _snapshot_contract_section(cli_fallback_contract),
        "terminal_artifact_cli_fallback_target": _snapshot_contract_section(cli_fallback_target_contract),
        "terminal_artifact_cli_fallback_target_contract": _snapshot_contract_section(cli_fallback_target_contract),
        "terminal_artifact_cli_fallback_target_fingerprint": cli_fallback_target_contract["contract_fingerprint"],
        "terminal_artifact_cli_fallback_target_contract_fingerprint": cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_fingerprints": _snapshot_contract_section(
            cli_fallback_target_contract["contract_fingerprints"]
        ),
        "terminal_artifact_render_target_fingerprint": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_artifact_rendering_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "raw_leaf_card_default_contract_fingerprint": raw_leaf_card_default_contract["contract_fingerprint"],
        "rendering_contract": {
            "kind": "card",
            "contract_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        },
        "terminal_artifact_cli_fallback_fingerprint": terminal_artifact_cli_fallback_contract_fingerprint(),
        "terminal_artifact_render_target_contract_fingerprint": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_artifact_rendering_contract_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback_contract_fingerprint": terminal_fallback_contract_fingerprint(),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
    }
    if include_terminal_artifact_cli_fallback_route:
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        manifest["terminal_artifact_cli_fallback_route"] = route_contract
        manifest["terminal_artifact_cli_fallback_route_contract"] = _snapshot_contract_section(route_contract)
        manifest["terminal_artifact_cli_fallback_route_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
            route_contract["contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = route_contract[
            "contract_fingerprints_fingerprint"
        ]
    if include_contract_fingerprints:
        manifest["contract_fingerprints"] = describe_terminal_artifact_contract_fingerprints(
            include_terminal_artifact=True,
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    return manifest


def _build_terminal_artifact_rendering_contract_manifest() -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    kind_contracts = _build_terminal_artifact_kind_contracts()
    terminal_artifact_kind_contracts = _snapshot_contract_section(kind_contracts)
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_rendering_schema_version": TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
        "terminal_artifact_rendering_version": TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
        "type": "TerminalArtifactRenderingContract",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "envelope": describe_terminal_artifact_envelope_contract(),
        "kind_contracts": kind_contracts,
        "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts,
        "render_target_contract": render_target_contract,
        "terminal_artifact_render_target_contract": _snapshot_contract_section(render_target_contract),
        "terminal_artifact_kind_contracts_fingerprint": terminal_artifact_kind_contracts_fingerprint(),
        "renderer_entrypoints": _build_terminal_artifact_renderer_entrypoints(),
        "render_target_resolver": "resolve_terminal_artifact_render_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(_build_terminal_artifact_raw_leaf_card_default_policy_manifest()),
        "raw_leaf_card_default_policy_contract": describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        ),
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "terminal_fallback_contract": describe_terminal_fallback_contract(),
        "terminal_fallback_fingerprint": terminal_fallback_contract_fingerprint(),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
        "contract_fingerprints": describe_terminal_artifact_rendering_contract_fingerprints(),
    }


def _build_terminal_artifact_cli_fallback_contract_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    rendering_contract = describe_terminal_artifact_rendering_contract()
    terminal_fallback_contract = describe_terminal_fallback_contract()
    terminal_artifact_cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    payload_contract = describe_terminal_artifact_cli_fallback_payload_contract()
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    raw_leaf_card_default_policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()
    card_hint_recovery_policy_contract = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
    shell_refinement_policy = _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()
    resolver_failure_policy = _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
    kind_contracts = _build_terminal_artifact_kind_contracts()
    terminal_artifact_kind_contracts = _snapshot_contract_section(kind_contracts)
    renderer_entrypoints = _build_terminal_artifact_renderer_entrypoints()

    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        "type": "TerminalArtifactCliFallbackContract",
        "fallback_target_resolver": "resolve_terminal_artifact_cli_fallback_target",
        "render_target_resolver": "resolve_terminal_artifact_render_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "terminal_artifact_cli_fallback_entrypoint": "render_terminal_cli_fallback",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "terminal_artifact_supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "envelope": describe_terminal_artifact_envelope_contract(),
        "kind_contracts": kind_contracts,
        "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts,
        "terminal_artifact_kind_contracts_fingerprint": terminal_artifact_kind_contracts_fingerprint(),
        "render_target_contract": render_target_contract,
        "terminal_artifact_render_target_contract": _snapshot_contract_section(render_target_contract),
        "renderer_entrypoints": renderer_entrypoints,
        "renderer_entrypoints_fingerprint": _fingerprint_manifest_section(renderer_entrypoints),
        "route_precedence": list(_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE),
        "rendering": rendering_contract,
        "terminal_artifact_rendering": _snapshot_contract_section(rendering_contract),
        "terminal_artifact_rendering_contract": _snapshot_contract_section(rendering_contract),
        "rendering_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_artifact_cli_fallback_payload_contract": _snapshot_contract_section(payload_contract),
        "terminal_artifact_cli_fallback_payload_contract_fingerprint": payload_contract["contract_fingerprint"],
        "terminal_artifact_cli_fallback_payload_contract_manifest": _snapshot_contract_section(payload_contract),
        "terminal_artifact_cli_fallback_payload_contract_manifest_fingerprint": payload_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target": terminal_artifact_cli_fallback_target_contract,
        "terminal_artifact_cli_fallback_target_contract": _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract
        ),
        "terminal_artifact_cli_fallback_target_contract_manifest": _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract
        ),
        "terminal_artifact_cli_fallback_target_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_manifest_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_fingerprints": _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints"]
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"
        ],
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(
            terminal_artifact_cli_fallback_target_contract["raw_leaf_card_default_policy"]
        ),
        "raw_leaf_card_default_policy_contract": raw_leaf_card_default_policy_contract,
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            raw_leaf_card_default_policy_contract
        ),
        "raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "terminal_artifact_cli_fallback_entrypoint_fingerprint": _fingerprint_manifest_section(
            "render_terminal_cli_fallback"
        ),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
        "shell_refinement_policy": shell_refinement_policy,
        "shell_refinement_policy_fingerprint": _fingerprint_manifest_section(shell_refinement_policy),
        "kind_policy": {
            "card": "defer to terminal artifact dispatch and keep card as the default recovery path",
            "action": "recover action payloads with render_terminal_action",
            "selection": "recover selection payloads with render_terminal_selection",
        },
        "resolver_failure_policy": resolver_failure_policy,
        "resolver_failure_policy_fingerprint": _fingerprint_manifest_section(resolver_failure_policy),
        "card_hint_recovery_policy": _snapshot_contract_section(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_fingerprint": card_hint_recovery_policy_contract["contract_fingerprint"],
        "card_hint_recovery_policy_contract": _snapshot_contract_section(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_contract_fingerprint": card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ],
        "card_hint_recovery_policy_contract_manifest": _snapshot_contract_section(
            card_hint_recovery_policy_contract
        ),
        "card_hint_recovery_policy_contract_manifest_fingerprint": card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_fallback_contract": terminal_fallback_contract,
        "terminal_artifact_render_target_contract_fingerprint": terminal_artifact_render_target_contract_fingerprint(),
        "terminal_artifact_rendering_contract_fingerprint": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback_contract_fingerprint": terminal_fallback_contract_fingerprint(),
        "terminal_artifact_supported_kinds_contract": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "terminal_artifact_supported_kinds_contract_fingerprint": _fingerprint_manifest_section(
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)
        ),
    }
    if include_terminal_artifact_cli_fallback_route:
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        manifest["terminal_artifact_cli_fallback_route"] = dict(route_contract)
        manifest["terminal_artifact_cli_fallback_route_contract"] = dict(route_contract)
        manifest["terminal_artifact_cli_fallback_route_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
            route_contract["contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint()
        )
        contract_fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True
        )
    else:
        contract_fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints()
    manifest["contract_fingerprints"] = _TerminalArtifactCliFallbackContractFingerprints(contract_fingerprints)
    manifest["terminal_artifact_cli_fallback_contract_manifest"] = dict(manifest)
    return manifest


def _build_terminal_artifact_cli_fallback_target_contract_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    terminal_artifact_render_target_contract = _snapshot_contract_section(render_target_contract)
    terminal_fallback_contract = describe_terminal_fallback_contract()
    leaf_contracts_contract = describe_a2ui_leaf_contracts()
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    raw_leaf_card_default_policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()
    card_hint_recovery_policy_contract = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
    resolver_failure_policy = _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
    terminal_artifact_cli_fallback_entrypoint = "render_terminal_cli_fallback"
    terminal_artifact_cli_fallback_entrypoint_contract = (
        describe_terminal_artifact_cli_fallback_entrypoint_contract()
    )
    kind_policy = _build_terminal_artifact_cli_fallback_kind_policy_manifest()
    contract_fingerprints = describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    manifest = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_target_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_target_version": TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
        "type": "TerminalArtifactCliFallbackTargetContract",
        "fallback_target_resolver": "resolve_terminal_artifact_cli_fallback_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "terminal_artifact_supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "route_precedence": list(_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE),
        "terminal_artifact_cli_fallback_entrypoint": terminal_artifact_cli_fallback_entrypoint,
        "terminal_artifact_cli_fallback_entrypoint_contract": _snapshot_contract_section(
            terminal_artifact_cli_fallback_entrypoint_contract
        ),
        "terminal_artifact_cli_fallback_entrypoint_fingerprint": _fingerprint_manifest_section(
            terminal_artifact_cli_fallback_entrypoint
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_fingerprint": _fingerprint_manifest_section(
            terminal_artifact_cli_fallback_entrypoint
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_manifest": _snapshot_contract_section(
            terminal_artifact_cli_fallback_entrypoint_contract
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint": (
            terminal_artifact_cli_fallback_entrypoint_contract["contract_fingerprint"]
        ),
        "render_target_contract": _snapshot_contract_section(render_target_contract),
        "terminal_artifact_render_target": terminal_artifact_render_target_contract,
        "terminal_artifact_render_target_contract": _snapshot_contract_section(
            terminal_artifact_render_target_contract
        ),
        "terminal_artifact_render_target_fingerprint": terminal_artifact_render_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_render_target_contract_fingerprint": terminal_artifact_render_target_contract[
            "contract_fingerprint"
        ],
        "renderer_entrypoints": _build_terminal_artifact_renderer_entrypoints(),
        "preserve_raw_leaf_card_default": True,
        "raw_leaf_required_fields": ["id", "label", "payload"],
        "raw_leaf_hint_fields": {
            "action": ["confirm", "policy_sensitive"],
            "selection": ["selected", "disabled"],
        },
        "raw_leaf_card_default_policy": _snapshot_contract_section(
            _build_terminal_artifact_raw_leaf_card_default_policy_manifest()
        ),
        "kind_resolution": copy.deepcopy(render_target_contract["kind_resolution"]),
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": copy.deepcopy(render_target_contract["fallback_recovery"]),
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
        "shell_refinement_policy": {
            "preserve_raw_leaf_card_default": True,
            "invalid_kind_treated_as_absent": True,
            "refine_card_underflow": True,
        },
        "leaf_renderers": copy.deepcopy(resolver_failure_policy["leaf_renderers"]),
        "card_hint_recovery_policy": _snapshot_contract_section(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_fingerprint": card_hint_recovery_policy_contract["contract_fingerprint"],
        "card_hint_recovery_policy_contract": _snapshot_contract_section(card_hint_recovery_policy_contract),
        "card_hint_recovery_policy_contract_fingerprint": card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ],
        "card_hint_recovery_policy_contract_manifest": _snapshot_contract_section(
            card_hint_recovery_policy_contract
        ),
        "card_hint_recovery_policy_contract_manifest_fingerprint": card_hint_recovery_policy_contract[
            "contract_fingerprint"
        ],
        "kind_policy": kind_policy,
        "kind_policy_fingerprint": _fingerprint_manifest_section(kind_policy),
        "kind_policy_contract": _snapshot_contract_section(kind_policy),
        "kind_policy_contract_fingerprint": _fingerprint_manifest_section(kind_policy),
        "kind_policy_contract_manifest": _snapshot_contract_section(kind_policy),
        "kind_policy_contract_manifest_fingerprint": _fingerprint_manifest_section(kind_policy),
        "terminal_fallback_contract": _snapshot_contract_section(terminal_fallback_contract),
        "terminal_fallback_fingerprint": terminal_fallback_contract["contract_fingerprint"],
        "terminal_fallback_contract_fingerprint": terminal_fallback_contract["contract_fingerprint"],
        "raw_leaf_card_default_contract": _snapshot_contract_section(raw_leaf_card_default_contract),
        "raw_leaf_card_default_contract_fingerprint": raw_leaf_card_default_contract["contract_fingerprint"],
        "raw_leaf_card_default_policy_contract": _snapshot_contract_section(raw_leaf_card_default_policy_contract),
        "raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            raw_leaf_card_default_policy_contract
        ),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints": contract_fingerprints,
        "contract_fingerprints": contract_fingerprints,
        "contract_fingerprints_fingerprint": terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(),
        "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint": (
            terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint()
        ),
        "terminal_artifact_supported_kinds_contract": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "terminal_artifact_supported_kinds_contract_fingerprint": _fingerprint_manifest_section(
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)
        ),
        "leaf_contracts": _snapshot_contract_section(leaf_contracts_contract),
        "leaf_contracts_fingerprint": leaf_contracts_contract["contract_fingerprint"],
        "leaf_contracts_contract": _snapshot_contract_section(leaf_contracts_contract),
        "leaf_contracts_contract_fingerprint": leaf_contracts_contract["contract_fingerprint"],
        "leaf_contracts_contract_manifest": _snapshot_contract_section(leaf_contracts_contract),
        "leaf_contracts_contract_manifest_fingerprint": leaf_contracts_contract["contract_fingerprint"],
        "leaf_contracts_manifest": _snapshot_contract_section(leaf_contracts_contract),
        "leaf_contracts_manifest_fingerprint": leaf_contracts_contract["contract_fingerprint"],
    }
    if include_terminal_artifact_cli_fallback_route:
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        manifest["terminal_artifact_cli_fallback_route"] = _snapshot_contract_section(route_contract)
        manifest["terminal_artifact_cli_fallback_route_contract"] = _snapshot_contract_section(route_contract)
        manifest["terminal_artifact_cli_fallback_route_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"] = route_contract["contract_fingerprint"]
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"] = _snapshot_contract_section(
            route_contract["contract_fingerprints"]
        )
        manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"] = (
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint()
        )
    return manifest


def _build_terminal_artifact_cli_fallback_route_contract_manifest() -> dict[str, Any]:
    render_target_contract = describe_terminal_artifact_render_target_contract()
    terminal_fallback_contract = describe_terminal_fallback_contract()
    terminal_artifact_cli_fallback_target_contract = describe_terminal_artifact_cli_fallback_target_contract()
    raw_leaf_card_default_policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()
    kind_resolution = copy.deepcopy(render_target_contract["kind_resolution"])
    fallback_recovery = copy.deepcopy(render_target_contract["fallback_recovery"])
    shell_refinement_policy = _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()
    resolver_failure_policy = _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
    contract_fingerprints = _build_terminal_artifact_cli_fallback_route_contract_fingerprints()
    contract_fingerprints_fingerprint = terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint()
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_route_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_route_version": TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION,
        "type": "TerminalArtifactCliFallbackRouteContract",
        "fallback_target_resolver": "resolve_terminal_artifact_cli_fallback_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "terminal_artifact_supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "route_precedence": list(_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE),
        "render_target_contract": render_target_contract,
        "render_target_contract_fingerprint": render_target_contract["contract_fingerprint"],
        "terminal_artifact_render_target_contract": _snapshot_contract_section(render_target_contract),
        "terminal_artifact_render_target_contract_fingerprint": render_target_contract["contract_fingerprint"],
        "terminal_artifact_cli_fallback_target_contract_fingerprint": terminal_artifact_cli_fallback_target_contract_fingerprint(),
        "terminal_artifact_cli_fallback_target_contract": _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "contract_fingerprint"
        ],
        "terminal_artifact_cli_fallback_target_contract_fingerprints": _snapshot_contract_section(
            terminal_artifact_cli_fallback_target_contract["contract_fingerprints"]
        ),
        "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint": terminal_artifact_cli_fallback_target_contract[
            "terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"
        ],
        "terminal_fallback_contract": terminal_fallback_contract,
        "terminal_fallback_contract_fingerprint": terminal_fallback_contract["contract_fingerprint"],
        "raw_leaf_card_default_policy": copy.deepcopy(_build_terminal_artifact_raw_leaf_card_default_policy_manifest()),
        "raw_leaf_card_default_policy_contract": raw_leaf_card_default_policy_contract,
        "raw_leaf_card_default_policy_contract_fingerprint": raw_leaf_card_default_policy_contract[
            "contract_fingerprint"
        ],
        "kind_resolution": kind_resolution,
        "kind_resolution_fingerprint": render_target_contract["kind_resolution_fingerprint"],
        "fallback_recovery": fallback_recovery,
        "fallback_recovery_fingerprint": render_target_contract["fallback_recovery_fingerprint"],
        "leaf_renderers": {
            "card": "render_terminal_card",
            "action": "render_terminal_action",
            "selection": "render_terminal_selection",
        },
        "shell_refinement_policy": shell_refinement_policy,
        "shell_refinement_policy_fingerprint": _fingerprint_manifest_section(shell_refinement_policy),
        "resolver_failure_policy": resolver_failure_policy,
        "resolver_failure_policy_fingerprint": _fingerprint_manifest_section(resolver_failure_policy),
        "contract_fingerprints": contract_fingerprints,
        "contract_fingerprints_fingerprint": contract_fingerprints_fingerprint,
        "terminal_artifact_cli_fallback_route_contract_fingerprints": _snapshot_contract_section(
            contract_fingerprints
        ),
        "terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint": contract_fingerprints_fingerprint,
        "terminal_artifact_supported_kinds_contract": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "terminal_artifact_supported_kinds_contract_fingerprint": _fingerprint_manifest_section(
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)
        ),
    }


def _build_terminal_artifact_envelope_manifest() -> dict[str, Any]:
    return {
        "type": _TERMINAL_ARTIFACT_ENVELOPE_TYPE,
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "required_fields": ["kind", "artifact"],
        "optional_fields": ["contract_version", "a2ui_version"],
        "kind_field": "kind",
        "artifact_field": "artifact",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
    }


def _build_terminal_artifact_kind_resolution_manifest() -> dict[str, Any]:
    return {
        "precedence": [
            "validated envelope kind",
            "typed payload kind",
            "explicit caller kind hint",
            "partial leaf hint recovery",
            "schema-valid leaf payload recovery",
            "card default",
        ],
        "card_payloads_override_conflicting_action_or_selection_hints": True,
        "caller_kind_hint_policy": {
            "invalid_kind_treated_as_absent": True,
            "typed_payload_kind_is_authoritative": True,
            "explicit_card_kind_blocks_leaf_recovery": True,
        },
        "partial_leaf_recovery": {
            "required_fields": ["id", "payload"],
            "action_hints": ["confirm", "policy_sensitive"],
            "selection_hints": ["selected", "disabled"],
        },
        "leaf_recovery": _build_terminal_artifact_leaf_recovery_manifest(),
    }


def _build_terminal_artifact_fallback_recovery_manifest() -> dict[str, Any]:
    return {
        "malformed_card_envelopes": {
            "action": "normalize_action_ref",
            "selection": "normalize_selection_ref",
        }
    }


def _build_terminal_artifact_leaf_recovery_manifest() -> dict[str, Any]:
    return {
        "malformed_card_envelopes": {
            "action": "normalize_action_ref",
            "selection": "normalize_selection_ref",
        }
    }


def _build_terminal_artifact_raw_leaf_card_default_manifest() -> dict[str, Any]:
    return {
        "preserve_when_kind_is_unset": True,
        "required_fields": ["id", "label", "payload"],
        "excluded_fields": ["type", "blocks", "actions", "confirm", "policy_sensitive", "selected", "disabled"],
    }


def _build_terminal_artifact_raw_leaf_card_default_policy_manifest() -> dict[str, Any]:
    return {
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "preserve_when_kind_is_unset": True,
        "invalid_kind_treated_as_absent": True,
    }


def _build_terminal_artifact_raw_leaf_card_default_policy_contract_manifest() -> dict[str, Any]:
    raw_leaf_card_default_policy = _build_terminal_artifact_raw_leaf_card_default_policy_manifest()
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_schema_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_policy_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "type": "TerminalArtifactRawLeafCardDefaultPolicyContract",
        "default_kind": raw_leaf_card_default_policy["default_kind"],
        "preserve_when_kind_is_unset": raw_leaf_card_default_policy["preserve_when_kind_is_unset"],
        "invalid_kind_treated_as_absent": raw_leaf_card_default_policy["invalid_kind_treated_as_absent"],
    }


def _build_terminal_artifact_raw_leaf_card_default_contract_manifest() -> dict[str, Any]:
    raw_leaf_card_default = _build_terminal_artifact_raw_leaf_card_default_manifest()
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_schema_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "terminal_artifact_raw_leaf_card_default_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        "type": "TerminalArtifactRawLeafCardDefaultContract",
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "preserve_when_kind_is_unset": raw_leaf_card_default["preserve_when_kind_is_unset"],
        "required_fields": list(raw_leaf_card_default["required_fields"]),
        "excluded_fields": list(raw_leaf_card_default["excluded_fields"]),
    }


def _build_terminal_artifact_kind_contracts() -> dict[str, dict[str, str]]:
    return {
        "card": {
            "kind": "card",
            "contract_fingerprint": card_contract_fingerprint(),
        },
        "action": {
            "kind": "action",
            "contract_fingerprint": action_contract_fingerprint(),
        },
        "selection": {
            "kind": "selection",
            "contract_fingerprint": selection_contract_fingerprint(),
        },
    }


def _build_terminal_artifact_render_target_contract_manifest() -> dict[str, Any]:
    raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
    kind_contracts = _build_terminal_artifact_kind_contracts()
    terminal_artifact_kind_contracts = _snapshot_contract_section(kind_contracts)
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_render_target_schema_version": TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
        "terminal_artifact_render_target_version": TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
        "type": "TerminalArtifactRenderTargetContract",
        "render_target_resolver": "resolve_terminal_artifact_render_target",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "envelope": describe_terminal_artifact_envelope_contract(),
        "kind_contracts": kind_contracts,
        "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts,
        "terminal_artifact_kind_contracts_fingerprint": terminal_artifact_kind_contracts_fingerprint(),
        "raw_leaf_card_default": _build_terminal_artifact_raw_leaf_card_default_manifest(),
        "raw_leaf_card_default_contract": raw_leaf_card_default_contract,
        "terminal_artifact_raw_leaf_card_default_contract": _snapshot_contract_section(
            raw_leaf_card_default_contract
        ),
        "raw_leaf_card_default_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        "raw_leaf_card_default_policy": copy.deepcopy(_build_terminal_artifact_raw_leaf_card_default_policy_manifest()),
        "raw_leaf_card_default_policy_contract": describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        "terminal_artifact_raw_leaf_card_default_policy_contract": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        ),
        "raw_leaf_card_default_policy_contract_fingerprints": describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints": _snapshot_contract_section(
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            )
        ),
        "kind_resolution": _build_terminal_artifact_kind_resolution_manifest(),
        "kind_resolution_fingerprint": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": _build_terminal_artifact_fallback_recovery_manifest(),
        "fallback_recovery_fingerprint": terminal_artifact_fallback_recovery_fingerprint(),
        "contract_fingerprints": describe_terminal_artifact_render_target_contract_fingerprints(),
    }


def _build_terminal_artifact_render_target_contract_fingerprints(
    *,
    include_terminal_artifact_render_target: bool = False,
) -> dict[str, str]:
    fingerprints = {
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "kind_resolution": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": terminal_artifact_fallback_recovery_fingerprint(),
    }
    if include_terminal_artifact_render_target:
        fingerprints["terminal_artifact_render_target"] = terminal_artifact_render_target_contract_fingerprint()
    return fingerprints


def terminal_artifact_kind_contracts_fingerprint() -> str:
    """Return a stable fingerprint for the shared terminal artifact kind contracts."""

    manifest = describe_terminal_artifact_kind_contracts()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_kind_contracts_manifest_fingerprint() -> str:
    """Return a stable fingerprint for the versioned kind-contract manifest."""

    return _fingerprint_manifest_section(_build_terminal_artifact_kind_contracts_manifest())


def _build_read_only_fallback_action_manifest() -> list[dict[str, Any]]:
    return [
        {
            "id": FALLBACK_COPY_ACTION_ID,
            "label": "Copy JSON",
            "version": A2UI_ACTION_SCHEMA_VERSION,
            "payload_fields": ["text"],
        }
    ]


def _build_read_only_json_preview_block(payload: dict[str, Any], *, max_payload_bytes: int) -> dict[str, Any]:
    return {
        "type": "CodeBlock",
        "language": "json",
        "code": _render_payload_preview(payload, max_payload_bytes=max_payload_bytes, pretty=True),
        "collapsed": True,
    }


def _build_action_payload_schema_manifest(*, include_string_policy_fields: bool = False) -> list[dict[str, Any]]:
    payload_schemas: list[dict[str, Any]] = []
    for action_id, schema in sorted(_ACTION_SCHEMAS.items()):
        payload_schema: dict[str, Any] = {
            "id": action_id,
            "version": A2UI_ACTION_SCHEMA_VERSION,
            "fields": sorted(schema),
        }
        if include_string_policy_fields:
            payload_schema["identifier_fields"] = list(_ACTION_PAYLOAD_IDENTIFIER_FIELDS.get(action_id, ()))
            payload_schema["free_text_fields"] = list(_ACTION_PAYLOAD_FREE_TEXT_FIELDS.get(action_id, ()))
        payload_schemas.append(payload_schema)
    return payload_schemas


def _build_card_schema_manifest() -> list[dict[str, Any]]:
    return [
        {
            "type": GENERIC_CARD_TYPE,
            "version": A2UI_VERSION,
            "required_fields": ["type", "title", "a2ui_version", "blocks", "actions"],
            "optional_fields": ["subtitle", "debug"],
            "allowed_actions": sorted(ALLOWED_ACTION_IDS),
            "action_policy": "client_allowlist",
        },
        {
            "type": UNKNOWN_CARD_TYPE,
            "version": A2UI_VERSION,
            "required_fields": ["type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions"],
            "optional_fields": [],
            "allowed_actions": [FALLBACK_COPY_ACTION_ID],
            "action_policy": "copy_to_clipboard_only",
        },
    ]


def _build_card_fallback_manifest() -> dict[str, Any]:
    return {
        "generic_card": {
            "type": GENERIC_CARD_TYPE,
            "action_policy": "client_allowlist",
            "allowed_actions": [FALLBACK_COPY_ACTION_ID],
            "actions": _build_read_only_fallback_action_manifest(),
        },
        "unknown_card": {
            "type": UNKNOWN_CARD_TYPE,
            "action_policy": "copy_to_clipboard_only",
            "allowed_actions": [FALLBACK_COPY_ACTION_ID],
            "default_preview_bytes": DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES,
            "actions": _build_read_only_fallback_action_manifest(),
        },
    }


def _build_a2ui_schema_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    return {
        "capabilities": describe_a2ui_capabilities_contract(),
        "card_contract": describe_card_contract(),
        "cards": _build_card_schema_manifest(),
        "leaf_contracts": describe_a2ui_leaf_contracts(),
        "selection": describe_selection_contract(),
        "action": describe_action_contract(),
        "terminal_artifact_envelope": describe_terminal_artifact_envelope_contract(),
        "terminal_artifact_render_target": describe_terminal_artifact_render_target_contract(),
        "actions": [
            {
                "type": "ActionRef",
                "version": A2UI_ACTION_SCHEMA_VERSION,
                "required_fields": ["id", "label", "payload"],
                "optional_fields": ["confirm", "policy_sensitive"],
                "payload_schemas": _build_action_payload_schema_manifest(),
            }
        ],
        "terminal_fallback": describe_terminal_fallback_contract(),
        "terminal_artifact": describe_terminal_artifact_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "terminal_artifact_rendering": describe_terminal_artifact_rendering_contract(),
        "terminal_artifact_cli_fallback": describe_terminal_artifact_cli_fallback_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "terminal_artifact_cli_fallback_payload": describe_terminal_artifact_cli_fallback_payload_contract(),
        "terminal_artifact_cli_fallback_target": describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        **(
            {
                "terminal_artifact_cli_fallback_route": describe_terminal_artifact_cli_fallback_route_contract(),
            }
            if include_terminal_artifact_cli_fallback_route
            else {}
        ),
    }


def _build_a2ui_leaf_contracts_manifest() -> dict[str, Any]:
    action_contract = describe_action_contract()
    selection_contract = describe_selection_contract()
    contract_fingerprints = {
        "action": action_contract["contract_fingerprint"],
        "selection": selection_contract["contract_fingerprint"],
    }
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_version": A2UI_LEAF_CONTRACTS_SCHEMA_VERSION,
        "leaf_contracts_schema_version": A2UI_LEAF_CONTRACTS_SCHEMA_VERSION,
        "leaf_contracts_version": A2UI_LEAF_CONTRACTS_SCHEMA_VERSION,
        "type": "A2UILeafContracts",
        "leaf_contracts": {
            "action": _snapshot_contract_section(action_contract),
            "selection": _snapshot_contract_section(selection_contract),
        },
        "action": _snapshot_contract_section(action_contract),
        "selection": _snapshot_contract_section(selection_contract),
        "action_contract": _snapshot_contract_section(action_contract),
        "selection_contract": _snapshot_contract_section(selection_contract),
        "contract_fingerprints": contract_fingerprints,
        "contract_fingerprints_fingerprint": _fingerprint_manifest_section(contract_fingerprints),
        "contract_fingerprints_contract": _snapshot_contract_section(contract_fingerprints),
    }


def _build_a2ui_capabilities_field_contracts() -> list[dict[str, Any]]:
    return [
        {
            "field": "a2ui_version",
            "type": "int",
            "description": f"must equal {A2UI_VERSION}",
        },
        {
            "field": "client_name",
            "type": "str",
            "description": "trimmed non-empty string",
        },
        {
            "field": "cards_supported",
            "type": "tuple[str, ...]",
            "description": "canonical unique card types excluding reserved card names",
            "reserved_values": list(_RESERVED_CARD_TYPES),
        },
        {
            "field": "primitive_blocks_supported",
            "type": "tuple[str, ...]",
            "description": "canonical unique primitive block types",
            "required_values": list(REQUIRED_PRIMITIVE_BLOCKS),
        },
        {
            "field": "actions_supported",
            "type": "tuple[str, ...]",
            "description": "canonical unique allowlisted action ids",
            "allowed_values": sorted(ALLOWED_ACTION_IDS),
        },
        {
            "field": "max_payload_bytes",
            "type": "int",
            "description": "positive payload byte ceiling",
        },
        {
            "field": "supports_streaming",
            "type": "bool",
            "description": "streaming support flag",
        },
    ]


def _canonicalize_supported_sequence(
    values: tuple[str, ...],
    *,
    canonical_order: tuple[str, ...],
) -> tuple[str, ...]:
    order_index = {value: index for index, value in enumerate(canonical_order)}
    return tuple(
        sorted(
            values,
            key=lambda value: (
                order_index.get(value, len(order_index)),
                value,
            ),
        )
    )


@lru_cache(maxsize=None)
def a2ui_contract_fingerprint(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
) -> str:
    """Return a stable fingerprint for the current contract manifest."""

    manifest = _build_a2ui_contract_fingerprint_manifest(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        include_terminal_artifact_cli_fallback_entrypoint=include_terminal_artifact_cli_fallback_entrypoint,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
    )
    return _fingerprint_manifest_section(manifest)


def _build_a2ui_contract_fingerprint_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_terminal_artifact_cli_fallback_entrypoint: bool = False,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
) -> dict[str, Any]:
    """Return the compact manifest used for top-level A2UI fingerprinting."""

    manifest: dict[str, Any] = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "schema_versions": _build_a2ui_schema_versions_manifest(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "capabilities": a2ui_capabilities_contract_fingerprint(),
        "leaf_contracts": a2ui_leaf_contracts_fingerprint(),
        "card_contract": card_contract_fingerprint(),
        "action": action_contract_fingerprint(),
        "selection": selection_contract_fingerprint(),
        "terminal_fallback": terminal_fallback_contract_fingerprint(),
        "terminal_artifact": terminal_artifact_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "terminal_artifact_cli_fallback": terminal_artifact_cli_fallback_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "terminal_artifact_cli_fallback_payload": terminal_artifact_cli_fallback_payload_contract_fingerprint(),
        "cards": _fingerprint_manifest_section(
            {
                "generic": GENERIC_CARD_TYPE,
                "unknown": UNKNOWN_CARD_TYPE,
                "reserved": list(_RESERVED_CARD_TYPES),
                "specialized": list(_SPECIALIZED_CARD_TYPES),
            }
        ),
        "fallbacks": _fingerprint_manifest_section(_build_card_fallback_manifest()),
        "primitive_blocks": _fingerprint_manifest_section(
            [
                {
                    "type": block_type,
                    "fields": list(_PRIMITIVE_BLOCK_SCHEMAS[block_type]),
                }
                for block_type in REQUIRED_PRIMITIVE_BLOCKS
            ]
        ),
        "actions": _fingerprint_manifest_section(
            [
                {
                    "id": action_id,
                    "version": A2UI_ACTION_SCHEMA_VERSION,
                    "payload_fields": sorted(schema),
                }
                for action_id, schema in sorted(_ACTION_SCHEMAS.items())
            ]
        ),
    }
    if include_terminal_artifact_cli_fallback_entrypoint:
        manifest["terminal_artifact_cli_fallback_entrypoint"] = (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
        )
        manifest["engine_artifacts_contract"] = engine_artifacts_contract_fingerprint()
    if include_terminal_artifact_cli_fallback_card_hint_recovery_policy:
        manifest["card_hint_recovery_policy"] = (
            terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint()
        )
    if include_shell_ui_contract:
        from .shell import shell_ui_contract_fingerprint

        manifest["shell_ui_contract"] = shell_ui_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        )
    return manifest


@lru_cache(maxsize=None)
def _build_a2ui_engine_contract_manifest(
    *,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    """Return the engine-facing A2UI contract snapshot.

    This wrapper keeps the engine contract explicit: it always includes the
    CLI fallback route, entrypoint, and wrapper contract slices that the
    engine loop needs while leaving the shell UI snapshot opt-in.
    """

    manifest = describe_a2ui_contract(
        include_terminal_artifact_cli_fallback_route=True,
        include_terminal_artifact_cli_fallback_entrypoint=True,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
        include_contract_aliases=include_contract_aliases,
    )
    return manifest


def describe_a2ui_engine_contract(
    *,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
    include_contract_aliases: bool = False,
) -> dict[str, Any]:
    """Return the engine-facing A2UI contract snapshot.

    This wrapper keeps the engine contract explicit: it always includes the
    CLI fallback route, entrypoint, and wrapper contract slices that the
    engine loop needs while leaving the shell UI snapshot opt-in.
    """

    return _snapshot_contract_section(
        _build_a2ui_engine_contract_manifest(
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
            include_shell_ui_contract=include_shell_ui_contract,
            include_contract_aliases=include_contract_aliases,
        )
    )


@lru_cache(maxsize=None)
def a2ui_engine_contract_fingerprint(
    *,
    include_terminal_artifact_cli_fallback_card_hint_recovery_policy: bool = False,
    include_shell_ui_contract: bool = False,
) -> str:
    """Return a stable fingerprint for the engine-facing A2UI manifest."""

    return a2ui_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=True,
        include_terminal_artifact_cli_fallback_entrypoint=True,
        include_terminal_artifact_cli_fallback_card_hint_recovery_policy=include_terminal_artifact_cli_fallback_card_hint_recovery_policy,
        include_shell_ui_contract=include_shell_ui_contract,
    )


def describe_engine_artifacts_contract() -> dict[str, Any]:
    """Return the engine artifact input contract shared by engine and CLI fallback."""

    manifest = _build_engine_artifacts_contract_manifest()
    manifest["contract_fingerprint"] = engine_artifacts_contract_fingerprint()
    manifest["engine_artifacts_contract_fingerprint"] = manifest["contract_fingerprint"]
    manifest["contract_manifest"] = _snapshot_contract_section(manifest)
    manifest["contract_manifest_fingerprint"] = manifest["contract_fingerprint"]
    return _snapshot_contract_section(manifest)


def describe_engine_artifacts_contract_manifest() -> dict[str, Any]:
    """Return the stable engine artifacts contract manifest alias."""

    return describe_engine_artifacts_contract()


@lru_cache(maxsize=None)
def engine_artifacts_contract_fingerprint() -> str:
    """Return a stable fingerprint for engine artifact input validation."""

    return _fingerprint_manifest_section(_build_engine_artifacts_contract_manifest())


def selection_contract_fingerprint() -> str:
    """Return a stable fingerprint for the SelectionRef contract manifest."""

    manifest = _build_selection_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def action_contract_fingerprint() -> str:
    """Return a stable fingerprint for the ActionRef contract manifest."""

    manifest = _build_action_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def card_contract_fingerprint() -> str:
    """Return a stable fingerprint for the card contract manifest."""

    manifest = _build_card_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def a2ui_leaf_contracts_fingerprint() -> str:
    """Return a stable fingerprint for the shared ActionRef and SelectionRef bundle."""

    manifest = _build_a2ui_leaf_contracts_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_fallback_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal fallback contract manifest."""

    manifest = _build_terminal_fallback_contract_manifest()
    return _fingerprint_manifest_section(manifest)


@lru_cache(maxsize=None)
def terminal_artifact_contract_fingerprint(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return a stable fingerprint for the terminal artifact dispatch manifest."""

    manifest = _build_terminal_artifact_contract_fingerprint_manifest(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    return _fingerprint_manifest_section(manifest)


def _build_terminal_artifact_contract_fingerprint_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the compact manifest used for terminal artifact fingerprinting."""

    manifest: dict[str, Any] = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "type": "TerminalArtifactContract",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "envelope": terminal_artifact_envelope_contract_fingerprint(),
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "render_target": terminal_artifact_render_target_contract_fingerprint(),
        "rendering": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback": terminal_fallback_contract_fingerprint(),
        "cli_fallback": terminal_artifact_cli_fallback_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "cli_fallback_target": terminal_artifact_cli_fallback_target_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "raw_leaf_card_default": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "renderer_entrypoints": terminal_artifact_renderer_entrypoints_contract_fingerprint(),
    }
    if include_terminal_artifact_cli_fallback_route:
        manifest["cli_fallback_route"] = terminal_artifact_cli_fallback_route_contract_fingerprint()
    return manifest


def terminal_artifact_envelope_contract_fingerprint() -> str:
    """Return a stable fingerprint for the TerminalArtifact envelope manifest."""

    manifest = _build_terminal_artifact_envelope_manifest()
    return _fingerprint_manifest_section(manifest)


@lru_cache(maxsize=None)
def terminal_artifact_rendering_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact rendering manifest."""

    manifest = _build_terminal_artifact_rendering_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_rendering_contract_manifest_fingerprint() -> str:
    """Return the rendering manifest fingerprint under a manifest-specific name."""

    return terminal_artifact_rendering_contract_fingerprint()


@lru_cache(maxsize=None)
def terminal_artifact_renderer_entrypoints_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact renderer-entrypoints manifest."""

    manifest = _build_terminal_artifact_renderer_entrypoints_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint() -> str:
    """Return the renderer-entrypoints manifest fingerprint under a manifest-specific name."""

    return terminal_artifact_renderer_entrypoints_contract_fingerprint()


def terminal_artifact_renderer_entrypoints_contract_fingerprints_fingerprint(
    include_contract_aliases: bool = False,
) -> str:
    """Return a stable fingerprint for the renderer-entrypoints fingerprint map."""

    return _fingerprint_manifest_section(
        describe_terminal_artifact_renderer_entrypoints_contract_fingerprints(
            include_contract_aliases=include_contract_aliases,
        )
    )


@lru_cache(maxsize=None)
def terminal_artifact_cli_fallback_contract_fingerprint(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return a stable fingerprint for the terminal artifact CLI fallback manifest."""

    manifest = _build_terminal_artifact_cli_fallback_contract_fingerprint_manifest(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    return _fingerprint_manifest_section(manifest)


def _build_terminal_artifact_cli_fallback_contract_fingerprint_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the compact manifest used for CLI fallback wrapper fingerprinting."""

    manifest: dict[str, Any] = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        "type": "TerminalArtifactCliFallbackContract",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "envelope": terminal_artifact_envelope_contract_fingerprint(),
        "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
        "render_target": terminal_artifact_render_target_contract_fingerprint(),
        "rendering": terminal_artifact_rendering_contract_fingerprint(),
        "terminal_fallback": terminal_fallback_contract_fingerprint(),
        "payload": terminal_artifact_cli_fallback_payload_contract_fingerprint(),
        "target": terminal_artifact_cli_fallback_target_contract_fingerprint(
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
        ),
        "raw_leaf_card_default": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "card_hint_recovery_policy": terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint(),
        "renderer_entrypoints": terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        "shell_refinement_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()
        ),
        "resolver_failure_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
        ),
    }
    if include_terminal_artifact_cli_fallback_route:
        manifest["route"] = terminal_artifact_cli_fallback_route_contract_fingerprint()
    return manifest


def terminal_artifact_cli_fallback_contract_manifest_fingerprint(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return the CLI fallback wrapper fingerprint under a manifest-specific name."""

    return terminal_artifact_cli_fallback_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )


def terminal_artifact_cli_fallback_contract_manifest_fingerprints_fingerprint(
    include_terminal_artifact_cli_fallback: bool = False,
    include_terminal_artifact_cli_fallback_route: bool = False,
    include_contract_aliases: bool = False,
) -> str:
    """Return the CLI fallback wrapper fingerprint map under a manifest-specific name."""

    return _fingerprint_manifest_section(
        describe_terminal_artifact_cli_fallback_contract_manifest_fingerprints(
            include_terminal_artifact_cli_fallback=include_terminal_artifact_cli_fallback,
            include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
            include_contract_aliases=include_contract_aliases,
        )
    )


@lru_cache(maxsize=None)
def terminal_artifact_cli_fallback_payload_contract_fingerprint() -> str:
    """Return a stable fingerprint for the shared CLI fallback payload manifest."""

    manifest = _build_terminal_artifact_cli_fallback_payload_contract_manifest()
    return _fingerprint_manifest_section(manifest)


@lru_cache(maxsize=None)
def terminal_artifact_cli_fallback_target_contract_fingerprint(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return a stable fingerprint for the CLI fallback target-selection manifest."""

    manifest = _build_terminal_artifact_cli_fallback_target_contract_fingerprint_manifest(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )
    return _fingerprint_manifest_section(manifest)


def _build_terminal_artifact_cli_fallback_target_contract_fingerprint_manifest(
    *,
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> dict[str, Any]:
    """Return the compact manifest used for target-selection fingerprinting."""

    manifest: dict[str, Any] = {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
        "terminal_artifact_cli_fallback_target_schema_version": (
            TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION
        ),
        "type": "TerminalArtifactCliFallbackTargetContract",
        "supported_kinds": list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
        "allowed_actions": sorted(ALLOWED_ACTION_IDS),
        "fallback_target_resolver": "resolve_terminal_artifact_cli_fallback_target",
        "fallback_renderer": "ShellUI.render_artifact",
        "terminal_artifact_cli_fallback_entrypoint": _fingerprint_manifest_section(
            "render_terminal_cli_fallback"
        ),
        "terminal_artifact_cli_fallback_entrypoint_contract": (
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
        ),
        "terminal_artifact_render_target": terminal_artifact_render_target_contract_fingerprint(),
        "renderer_entrypoints": terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        "leaf_contracts": a2ui_leaf_contracts_fingerprint(),
        "terminal_fallback": terminal_fallback_contract_fingerprint(),
        "raw_leaf_card_default": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        "raw_leaf_card_default_policy": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        "kind_resolution": terminal_artifact_kind_resolution_fingerprint(),
        "fallback_recovery": terminal_artifact_fallback_recovery_fingerprint(),
        "shell_refinement_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_shell_refinement_policy_manifest()
        ),
        "resolver_failure_policy": _fingerprint_manifest_section(
            _build_terminal_artifact_cli_fallback_resolver_failure_policy_manifest()
        ),
        "card_hint_recovery_policy": terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint(),
    }
    if include_terminal_artifact_cli_fallback_route:
        manifest["route_precedence"] = _fingerprint_manifest_section(
            list(_TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_PRECEDENCE)
        )
        manifest["route_fingerprints"] = terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint()
    return manifest


def terminal_artifact_cli_fallback_target_contract_manifest_fingerprint(
    include_terminal_artifact_cli_fallback_route: bool = False,
) -> str:
    """Return the CLI fallback target fingerprint under a manifest-specific name."""

    return terminal_artifact_cli_fallback_target_contract_fingerprint(
        include_terminal_artifact_cli_fallback_route=include_terminal_artifact_cli_fallback_route,
    )


@lru_cache(maxsize=None)
def terminal_artifact_raw_leaf_card_default_contract_fingerprint() -> str:
    """Return a stable fingerprint for the raw-leaf card default contract manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_contract_manifest()
    return _fingerprint_manifest_section(manifest)


@lru_cache(maxsize=None)
def terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint() -> str:
    """Return a stable fingerprint for the raw-leaf card default policy manifest."""

    manifest = _build_terminal_artifact_raw_leaf_card_default_policy_contract_manifest()
    return _fingerprint_manifest_section(manifest)


@lru_cache(maxsize=None)
def terminal_artifact_render_target_contract_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact render-target manifest."""

    manifest = _build_terminal_artifact_render_target_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_render_target_contract_manifest_fingerprint() -> str:
    """Return the render-target manifest fingerprint under a manifest-specific name."""

    return terminal_artifact_render_target_contract_fingerprint()


def terminal_artifact_kind_resolution_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact kind-resolution manifest."""

    manifest = _build_terminal_artifact_kind_resolution_manifest()
    return _fingerprint_manifest_section(manifest)


def terminal_artifact_fallback_recovery_fingerprint() -> str:
    """Return a stable fingerprint for the terminal artifact fallback-recovery manifest."""

    manifest = _build_terminal_artifact_fallback_recovery_manifest()
    return _fingerprint_manifest_section(manifest)


def a2ui_capabilities_contract_fingerprint() -> str:
    """Return a stable fingerprint for the A2UI capabilities handshake manifest."""

    manifest = _build_a2ui_capabilities_contract_manifest()
    return _fingerprint_manifest_section(manifest)


def _fingerprint_manifest_section(section: Any) -> str:
    return hashlib.sha256(_canonical_json(section).encode("utf-8")).hexdigest()


def validate_capabilities(capabilities: A2UICapabilities) -> None:
    if type(capabilities.a2ui_version) is not int or capabilities.a2ui_version != A2UI_VERSION:
        raise ValueError("Unsupported a2ui version")
    if not isinstance(capabilities.client_name, str) or not capabilities.client_name.strip():
        raise ValueError("client_name is required")
    if type(capabilities.max_payload_bytes) is not int or capabilities.max_payload_bytes <= 0:
        raise ValueError("max_payload_bytes must be positive")
    if not isinstance(capabilities.supports_streaming, bool):
        raise ValueError("supports_streaming must be a bool")
    cards_supported = _validate_supported_string_sequence(
        capabilities.cards_supported,
        field_name="cards_supported",
    )
    seen_cards: set[str] = set()
    for card_type in cards_supported:
        if not card_type.strip():
            raise ValueError("Supported card types must be non-empty strings")
        if card_type != card_type.strip():
            raise ValueError(f"Supported card types must be canonical, got: {card_type!r}")
        canonical_card_type = card_type
        if canonical_card_type in _RESERVED_CARD_TYPES:
            raise ValueError(f"Reserved card type cannot be advertised as supported: {canonical_card_type}")
        if canonical_card_type in seen_cards:
            raise ValueError(f"Duplicate supported card type: {canonical_card_type}")
        seen_cards.add(canonical_card_type)
    primitive_blocks_supported = _validate_supported_string_sequence(
        capabilities.primitive_blocks_supported,
        field_name="primitive_blocks_supported",
    )
    seen_blocks: set[str] = set()
    for block_type in primitive_blocks_supported:
        if not block_type.strip():
            raise ValueError("Supported primitive block types must be non-empty strings")
        if block_type != block_type.strip():
            raise ValueError(f"Supported primitive block types must be canonical, got: {block_type!r}")
        canonical_block_type = block_type
        if canonical_block_type in seen_blocks:
            raise ValueError(f"Duplicate supported primitive block type: {canonical_block_type}")
        seen_blocks.add(canonical_block_type)
    if not _PRIMITIVE_BLOCK_SET.issubset(seen_blocks):
        raise ValueError("Missing required primitive block support")
    actions_supported = _validate_supported_string_sequence(
        capabilities.actions_supported,
        field_name="actions_supported",
    )
    seen_actions: set[str] = set()
    for action_id in actions_supported:
        if not action_id.strip():
            raise ValueError("Supported action ids must be non-empty strings")
        if action_id != action_id.strip():
            raise ValueError(f"Supported action ids must be canonical, got: {action_id!r}")
        canonical_action_id = action_id
        if canonical_action_id not in _ALLOWED_ACTION_SET:
            raise ValueError(f"Unknown action in capabilities: {canonical_action_id}")
        if canonical_action_id in seen_actions:
            raise ValueError(f"Duplicate supported action id: {canonical_action_id}")
        seen_actions.add(canonical_action_id)


def engine_prepare_card(card: Any, capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    card_type = _normalize_card_type(card)
    if card_type == GENERIC_CARD_TYPE:
        return _materialize_generic_card(card, capabilities)
    if card_type == UNKNOWN_CARD_TYPE:
        return _materialize_unknown_card(card, capabilities)

    if card_type in set(capabilities.cards_supported):
        _validate_card_version(card)
        return _materialize_versioned_card(card, capabilities)

    # Safe fallback for unsupported specialized cards.
    read_only_actions = _build_read_only_fallback_actions(
        card,
        supported_actions=set(capabilities.actions_supported),
        max_payload_bytes=capabilities.max_payload_bytes,
    )
    fallback_card = {
        "type": GENERIC_CARD_TYPE,
        "title": _build_fallback_title(GENERIC_CARD_TYPE, source_card_type=card_type),
        "subtitle": GENERIC_FALLBACK_SUBTITLE,
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(card_type, fallback_kind="generic"),
        "blocks": [
            {
                "type": "AlertBlock",
                "severity": "info",
                "title": "Card fallback",
                "message": "Rendered as GenericCard because client does not support this specialized card.",
            },
            *_extract_safe_primitive_blocks(card, allow_code_block=False),
            _build_read_only_json_preview_block(card, max_payload_bytes=capabilities.max_payload_bytes),
        ],
        "actions": read_only_actions,
    }
    _validate_fallback_card(
        fallback_card,
        expected_type=GENERIC_CARD_TYPE,
        expected_fallback_kind="generic",
    )
    return fallback_card


def validate_unknown_card(card: Any) -> None:
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    _validate_fallback_card(
        card,
        expected_type=UNKNOWN_CARD_TYPE,
        expected_fallback_kind="unknown",
    )


def studio_materialize_card(card: Any, capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    card_type = _normalize_card_type(card)
    if card_type == GENERIC_CARD_TYPE:
        return _materialize_generic_card(card, capabilities)
    if card_type == UNKNOWN_CARD_TYPE:
        return _materialize_unknown_card(card, capabilities)
    if card_type in set(capabilities.cards_supported):
        _validate_card_version(card)
        return _materialize_versioned_card(card, capabilities)
    fallback_card = build_unknown_card(
        card,
        max_payload_bytes=capabilities.max_payload_bytes,
        supported_actions=capabilities.actions_supported,
    )
    return fallback_card


def build_unknown_card(
    raw_card: Any,
    *,
    max_payload_bytes: int | None = DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES,
    supported_actions: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    coerced_card = _coerce_card_payload(raw_card)
    if coerced_card is not None:
        raw_card = coerced_card
    type_name = _normalize_card_type(raw_card)
    effective_max_payload_bytes = _normalize_preview_budget(max_payload_bytes)
    blocks = _extract_safe_primitive_blocks(raw_card, allow_code_block=False)
    blocks.append(_build_read_only_json_preview_block(raw_card, max_payload_bytes=effective_max_payload_bytes))
    actions = _build_unknown_card_actions(
        raw_card,
        supported_actions=supported_actions,
        max_payload_bytes=effective_max_payload_bytes,
    )
    _validate_canonical_read_only_fallback_actions(actions)
    card = {
        "type": UNKNOWN_CARD_TYPE,
        "title": _build_fallback_title(UNKNOWN_CARD_TYPE, source_card_type=type_name),
        "subtitle": UNKNOWN_FALLBACK_SUBTITLE,
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(type_name, fallback_kind="unknown"),
        "blocks": blocks,
        "actions": actions,
    }
    _validate_fallback_card(card, expected_type=UNKNOWN_CARD_TYPE, expected_fallback_kind="unknown")
    return card


def validate_generic_card(card: Any, *, strict_actions: bool = True) -> None:
    coerced_card = _coerce_card_payload(card)
    if coerced_card is not None:
        card = coerced_card
    if card.get("type") != GENERIC_CARD_TYPE:
        raise ValueError("Card type must be GenericCard")
    version = card.get("a2ui_version")
    if version is not None:
        if type(version) is not int:
            raise ValueError("GenericCard a2ui_version must be an int")
        if version != A2UI_VERSION:
            raise ValueError("Unsupported GenericCard a2ui_version")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("GenericCard title is required")
    subtitle = card.get("subtitle")
    if subtitle is not None and not isinstance(subtitle, str):
        raise ValueError("GenericCard subtitle must be a string when provided")
    if "blocks" not in card:
        raise ValueError("GenericCard blocks are required")
    blocks = card.get("blocks")
    if not isinstance(blocks, (list, tuple)):
        raise ValueError("GenericCard blocks must be a list or tuple")
    for block in blocks:
        validate_primitive_block(block)
    if "actions" not in card:
        raise ValueError("GenericCard actions are required")
    actions = card.get("actions")
    if not isinstance(actions, (list, tuple)):
        raise ValueError("GenericCard actions must be a list or tuple")
    if strict_actions:
        seen_actions: set[str] = set()
        for action in actions:
            normalized_action = _normalize_action(_action_ref_to_dict(action), supported_actions=_ALLOWED_ACTION_SET)
            action_key = _canonical_json(normalized_action)
            if action_key in seen_actions:
                raise ValueError("GenericCard actions must not contain duplicates")
            seen_actions.add(action_key)


def _validate_fallback_card(
    card: dict[str, Any],
    *,
    expected_type: str,
    expected_fallback_kind: str,
) -> None:
    extra_keys = set(card) - {"type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions"}
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Fallback card contains unexpected field(s): {extras}")
    if card.get("type") != expected_type:
        raise ValueError(f"Fallback card type must be {expected_type}")
    version = card.get("a2ui_version")
    if type(version) is not int:
        raise ValueError("Fallback card a2ui_version must be an int")
    if version != A2UI_VERSION:
        raise ValueError("Unsupported fallback card a2ui_version")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Fallback card title is required")
    subtitle = card.get("subtitle")
    if not isinstance(subtitle, str) or not subtitle.strip():
        raise ValueError("Fallback card subtitle is required")
    blocks = card.get("blocks")
    if not isinstance(blocks, (list, tuple)):
        raise ValueError("Fallback card blocks must be a list or tuple")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions")
    if not isinstance(actions, (list, tuple)):
        raise ValueError("Fallback card actions must be a list or tuple")
    _validate_canonical_read_only_fallback_actions(actions)
    debug = card.get("debug")
    if not isinstance(debug, Mapping):
        raise ValueError("Fallback card debug is required")
    extra_debug_keys = set(debug) - {"contract_version", "fallback_kind", "source_card_type"}
    if extra_debug_keys:
        extras = ", ".join(sorted(extra_debug_keys))
        raise ValueError(f"Fallback card debug contains unexpected field(s): {extras}")
    contract_version = debug.get("contract_version")
    if type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION:
        raise ValueError("Fallback card debug contract_version is invalid")
    fallback_kind = debug.get("fallback_kind")
    source_card_type = debug.get("source_card_type")
    if not isinstance(fallback_kind, str) or fallback_kind.strip() != expected_fallback_kind:
        raise ValueError("Fallback card debug fallback_kind is invalid")
    if not isinstance(source_card_type, str) or source_card_type.strip() != source_card_type or not source_card_type.strip():
        raise ValueError("Fallback card debug source_card_type is required")
    expected_title = _build_fallback_title(expected_type, source_card_type=source_card_type)
    if title.strip() != expected_title:
        raise ValueError("Fallback card title is invalid")
    expected_subtitle = _fallback_subtitle(expected_fallback_kind)
    if subtitle.strip() != expected_subtitle:
        raise ValueError("Fallback card subtitle is invalid")


def _validate_card_version(card: dict[str, Any]) -> None:
    version = card.get("a2ui_version")
    if version is None:
        return
    if type(version) is not int:
        raise ValueError("Card a2ui_version must be an int")
    if version != A2UI_VERSION:
        raise ValueError("Unsupported card a2ui_version")


def validate_primitive_block(block: Any) -> None:
    if not isinstance(block, Mapping):
        raise ValueError("Primitive block must be an object")
    block_type = str(block.get("type", ""))
    if block_type not in _PRIMITIVE_BLOCK_SET:
        raise ValueError(f"Unsupported primitive block: {block_type}")
    _validate_primitive_block_fields(block_type, block)


def validate_action_ref(action: Any) -> None:
    action = _action_ref_to_dict(action)
    _normalize_action(action, supported_actions=_ALLOWED_ACTION_SET)


def validate_selection_ref(selection: Any) -> None:
    selection = _selection_ref_to_dict(selection)
    _normalize_selection(selection)


def normalize_action_ref(action: ActionRef | Mapping[str, Any]) -> ActionRef:
    normalized = _normalize_action(_action_ref_to_dict(action), supported_actions=_ALLOWED_ACTION_SET)
    return ActionRef(
        id=str(normalized["id"]),
        label=str(normalized["label"]),
        payload=_copy_action_payload(normalized["payload"]),
        confirm=dict(normalized["confirm"]) if "confirm" in normalized else None,
        policy_sensitive=bool(normalized.get("policy_sensitive", False)),
        schema_version=int(normalized["schema_version"]),
        a2ui_version=int(normalized["a2ui_version"]),
    )


def normalize_selection_ref(selection: SelectionRef | Mapping[str, Any]) -> SelectionRef:
    normalized = _normalize_selection(_selection_ref_to_dict(selection))
    return SelectionRef(
        id=str(normalized["id"]),
        label=str(normalized["label"]),
        payload=_copy_selection_payload(normalized["payload"]),
        selected=bool(normalized.get("selected", False)),
        disabled=bool(normalized.get("disabled", False)),
        schema_version=int(normalized["schema_version"]),
        a2ui_version=int(normalized["a2ui_version"]),
    )


def execute_action_with_policy_gate(
    *,
    action: ActionRef | Mapping[str, Any],
    capabilities: A2UICapabilities,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_capabilities(capabilities)
    normalized_action = normalize_action_ref(action)
    if normalized_action.id not in set(capabilities.actions_supported):
        raise ValueError("Action not supported by client")
    if not policy_gate.allow_action(
        normalized_action.id,
        normalized_action.payload,
        policy_sensitive=normalized_action.policy_sensitive,
    ):
        raise PermissionError("PolicyGate blocked action")
    return executor(normalized_action)


def render_terminal_card(card: Any) -> str:
    """Render a card payload, or unwrap a valid TerminalArtifact envelope.

    The shared CLI still calls this helper directly, so recoverable envelopes
    are accepted here as a compatibility bridge to the generic artifact
    renderer.
    """

    normalized_card = _coerce_terminal_card(card)
    if normalized_card is None:
        return _render_invalid_terminal_card(card)

    try:
        card_type = _normalize_card_type(normalized_card)
        if card_type == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            try:
                rendered_artifact = render_terminal_artifact(normalized_card)
            except Exception:
                rendered_artifact = None
            else:
                if _is_nonempty_terminal_rendered_text(rendered_artifact):
                    return rendered_artifact
            try:
                recovered_artifact, recovered_kind = _resolve_terminal_artifact_render_target(
                    normalized_card,
                    allow_invalid_envelope_recovery=True,
                )
            except Exception:
                recovered_artifact = None
                recovered_kind = None
            else:
                if recovered_kind == "action":
                    try:
                        rendered_action = render_terminal_action(recovered_artifact)
                    except Exception:
                        return _render_invalid_terminal_action(recovered_artifact)
                    if _is_nonempty_terminal_rendered_text(rendered_action):
                        return rendered_action
                    return _render_invalid_terminal_action(recovered_artifact)
                if recovered_kind == "selection":
                    try:
                        rendered_selection = render_terminal_selection(recovered_artifact)
                    except Exception:
                        return _render_invalid_terminal_selection(recovered_artifact)
                    if _is_nonempty_terminal_rendered_text(rendered_selection):
                        return rendered_selection
                    return _render_invalid_terminal_selection(recovered_artifact)
                if recovered_kind == "card":
                    try:
                        rendered_card = render_terminal_card(recovered_artifact)
                    except Exception:
                        pass
                    else:
                        if _is_nonempty_terminal_rendered_text(rendered_card):
                            return rendered_card
                recovered_card = _resolve_terminal_artifact_card_fallback(normalized_card)
                if recovered_card is not None:
                    try:
                        rendered_card = render_terminal_card(recovered_card)
                    except Exception:
                        pass
                    else:
                        if _is_nonempty_terminal_rendered_text(rendered_card):
                            return rendered_card
                return _render_invalid_terminal_artifact(normalized_card)
        # Keep the card leaf renderer card-only so explicit action/selection
        # payloads do not masquerade as cards when a caller bypasses dispatch.
        if _infer_terminal_artifact_kind_from_mapping(normalized_card) in {"action", "selection"}:
            return _render_invalid_terminal_card(normalized_card)
        raw_title = _normalize_card_title(normalized_card)
        title = _render_terminal_inline_text(raw_title)
        rendered_card_type = _render_terminal_inline_text(card_type)
        raw_actions = normalized_card.get("actions")
        actions, incomplete_actions = _materialize_action_iterable(raw_actions)
        malformed_actions_container = (
            raw_actions is not None
            and not isinstance(raw_actions, (list, tuple))
            and (
                not isinstance(raw_actions, Iterable)
                or isinstance(raw_actions, (str, bytes, bytearray, Mapping))
            )
        )
        subtitle = normalized_card.get("subtitle")
        generic_fallback_source = _resolve_generic_fallback_source(
            raw_title,
            actions,
            normalized_card.get("debug"),
        )
        generic_fallback_hint = _is_canonical_generic_fallback_signal(subtitle, actions)
        lines = [f"[{rendered_card_type}] {title}"]
        if raw_title == "<untitled>" and _should_preserve_raw_leaf_card_default(normalized_card):
            # Surface the leaf label without changing the card title contract.
            raw_label = _normalize_card_text(normalized_card.get("label"))
            if raw_label is not None:
                rendered_label = _render_terminal_inline_text(raw_label)
                if rendered_label:
                    lines.append(f"- label: {rendered_label}")
        if card_type == UNKNOWN_CARD_TYPE:
            lines.append(UNKNOWN_FALLBACK_SUBTITLE)
        elif card_type == GENERIC_CARD_TYPE and (
            generic_fallback_source is not None or generic_fallback_hint
        ):
            lines.append(GENERIC_FALLBACK_SUBTITLE)
        elif isinstance(subtitle, str) and subtitle.strip():
            lines.append(_render_terminal_inline_text(subtitle.strip()))
        version = normalized_card.get("a2ui_version")
        if type(version) is int:
            lines.append(f"A2UI v{version}")
        rendered_fallback = _render_terminal_fallback_notice(
            card_type,
            title,
            debug=normalized_card.get("debug"),
            generic_fallback_source=generic_fallback_source,
            generic_fallback_hint=generic_fallback_hint,
        )
        if rendered_fallback:
            lines.extend(rendered_fallback)
        rendered_policy = _render_terminal_action_policy(
            card_type,
            title,
            debug=normalized_card.get("debug"),
            generic_fallback_source=generic_fallback_source,
            generic_fallback_hint=generic_fallback_hint,
        )
        if rendered_policy:
            lines.extend(rendered_policy)
        debug = normalized_card.get("debug")
        rendered_debug = _render_terminal_fallback_debug(
            card_type,
            title,
            debug,
            generic_fallback_source=generic_fallback_source,
        )
        if not rendered_debug:
            rendered_debug = _render_terminal_debug(debug)
        if rendered_debug:
            lines.append("Debug:")
            lines.extend(rendered_debug)
        blocks, incomplete_blocks = _materialize_card_entry_iterable(normalized_card.get("blocks"))
        for block in blocks:
            lines.extend(_render_terminal_block(block))
        if incomplete_blocks:
            lines.append("Some blocks unavailable after fallback recovery")
        rendered_actions = _render_terminal_actions(
            actions,
            supported_actions={FALLBACK_COPY_ACTION_ID} if card_type == UNKNOWN_CARD_TYPE else _ALLOWED_ACTION_SET,
        )
        actions_present = raw_actions is not None
        filtered_actions = actions_present and (incomplete_actions or len(rendered_actions) < len(actions))
        if rendered_actions:
            lines.append("Actions:")
            lines.extend(rendered_actions)
            if filtered_actions:
                lines.append("Some actions filtered out by allowlist or validation")
        elif actions_present:
            lines.append("Actions: none available")
            if actions or incomplete_actions or malformed_actions_container:
                lines.append("Actions filtered out by allowlist or validation")
        return "\n".join(lines)
    except Exception:
        return _render_invalid_terminal_card(normalized_card)


def render_terminal_selection(selection: Any) -> str:
    if isinstance(selection, SelectionRef):
        selection = _selection_ref_to_dict(selection)
    elif isinstance(selection, Mapping):
        selection = _strip_terminal_type_hint(selection, expected_type="SelectionRef")
        selection = _unwrap_terminal_artifact_leaf_payload(selection, expected_kind="selection")

    try:
        normalized = _normalize_selection(selection)
    except ValueError:
        return _render_invalid_terminal_selection(selection)

    lines = [
        f"[SelectionRef] {_render_terminal_inline_text(normalized['label'])}",
        f"Selection schema v{SELECTION_SCHEMA_VERSION}",
        f"A2UI v{A2UI_VERSION}",
        f"- id: {_render_terminal_inline_text(normalized['id'])}",
        f"- selected: {'true' if bool(normalized.get('selected', False)) else 'false'}",
        f"- disabled: {'true' if bool(normalized.get('disabled', False)) else 'false'}",
    ]
    payload = normalized.get("payload")
    if isinstance(payload, Mapping):
        lines.append(f"- payload: {_render_payload_preview(payload, max_payload_bytes=256)}")
    return "\n".join(lines)


def render_terminal_action(action: Any) -> str:
    if isinstance(action, ActionRef):
        action = _action_ref_to_dict(action)
    elif isinstance(action, Mapping):
        action = _strip_terminal_type_hint(action, expected_type="ActionRef")
        action = _unwrap_terminal_artifact_leaf_payload(action, expected_kind="action")

    try:
        normalized = normalize_action_ref(action)
    except ValueError:
        return _render_invalid_terminal_action(action)

    lines = [
        f"[ActionRef] {_render_terminal_inline_text(normalized.label)}",
        f"Action schema v{A2UI_ACTION_SCHEMA_VERSION}",
        f"A2UI v{A2UI_VERSION}",
        f"- id: {_render_terminal_inline_text(normalized.id)}",
        f"- payload: {_render_payload_preview(normalized.payload, max_payload_bytes=256)}",
    ]
    payload_policy = _action_payload_field_policy_label(normalized.id)
    if payload_policy is not None:
        lines.append(f"- payload_policy: {payload_policy}")
    if normalized.confirm is not None:
        lines.append(f"- confirm: {_render_payload_preview(normalized.confirm, max_payload_bytes=256)}")
    if normalized.policy_sensitive:
        lines.append("- policy_sensitive: true")
    return "\n".join(lines)


def _resolve_terminal_artifact_render_target(
    artifact: Any,
    *,
    requested_kind: str | None = None,
    allow_invalid_envelope_recovery: bool = False,
) -> tuple[Any, str]:
    """Resolve the concrete payload and render kind for a terminal artifact.

    The renderer and CLI fallback path both use this helper so they stay in
    lockstep when terminal envelopes are malformed but still recoverable.
    """

    envelope_kind_hint = None
    envelope_validated = False
    saw_terminal_artifact_envelope = False
    if isinstance(artifact, Mapping):
        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            saw_terminal_artifact_envelope = True
            envelope_kind_hint = _normalize_terminal_artifact_envelope_kind(artifact.get("kind"))
            envelope_validated = True

    try:
        artifact, envelope_kind = _unwrap_terminal_artifact_payload(artifact)
    except ValueError:
        envelope_validated = False
        if not allow_invalid_envelope_recovery and envelope_kind_hint is not None:
            raise
        recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
            artifact,
            requested_kind=requested_kind,
            envelope_kind_hint=envelope_kind_hint,
            allow_invalid_metadata=allow_invalid_envelope_recovery,
        )
        if recovered is None:
            raise
        artifact, envelope_kind = recovered

    typed_kind = _infer_terminal_artifact_explicit_kind(artifact)
    kind = requested_kind
    if envelope_kind is not None:
        if (
            requested_kind is not None
            and requested_kind != envelope_kind
            and not allow_invalid_envelope_recovery
        ):
            raise ValueError("kind does not match TerminalArtifact envelope")
        kind = envelope_kind
    elif typed_kind in {"action", "selection"}:
        if requested_kind == "card":
            _validate_terminal_artifact_card_payload(artifact)
            kind = typed_kind
        elif requested_kind in {"action", "selection"} and requested_kind != typed_kind:
            # The explicit caller hint stays authoritative for leaf renders so
            # a typed payload cannot silently retarget to the opposite leaf
            # renderer and leak the wrong presentation contract.
            kind = requested_kind
        else:
            kind = typed_kind
    elif typed_kind == "card":
        # Preserve typed card payloads as cards even if a caller passes a
        # conflicting action/selection hint.
        kind = "card"
    elif requested_kind is not None:
        kind = requested_kind
    if allow_invalid_envelope_recovery and typed_kind is None and kind == "card" and requested_kind != "card":
        if not _should_preserve_raw_leaf_card_default(artifact):
            # Only promote structured leaf payloads during malformed-envelope
            # recovery. Ambiguous raw-leaf cards should remain cards so the
            # generic renderer stays aligned with the explicit CLI fallback.
            recovered_kind = _recover_terminal_artifact_leaf_kind(artifact)
            if recovered_kind is not None:
                kind = recovered_kind

    resolved_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    if requested_kind is None and resolved_kind == "card" and not envelope_validated:
        # Preserve explicit action/selection hints even when the payload is not
        # wrapped in a malformed envelope, so partial leaf artifacts do not get
        # flattened into the card default.
        recovered_partial_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
        if recovered_partial_kind is not None:
            resolved_kind = recovered_partial_kind
    if allow_invalid_envelope_recovery and requested_kind is None and resolved_kind == "card":
        if saw_terminal_artifact_envelope:
            if envelope_kind_hint is None:
                # Malformed envelopes with an unusable kind stay on the card
                # path so explicit kind errors do not get reinterpreted as a
                # structured leaf recovery.
                return artifact, "card"
            # Card envelopes with invalid metadata may still wrap a concrete
            # action or selection leaf, so recover the leaf kind before
            # falling back to the generic card render.
            recovered_leaf_kind = _recover_terminal_artifact_leaf_kind(artifact)
            if recovered_leaf_kind is not None:
                resolved_kind = recovered_leaf_kind
        else:
            # Raw leaf payloads can still be recovered in fallback mode when
            # the resolver is called directly, but the shell keeps the
            # explicit raw-leaf card-default shortcut before this entrypoint.
            recovered_leaf_kind = _recover_terminal_artifact_leaf_kind(artifact)
            if recovered_leaf_kind is not None:
                resolved_kind = recovered_leaf_kind
    return artifact, resolved_kind


def render_terminal_artifact(artifact: Any, *, kind: str | None = None) -> str:
    """Render a structured A2UI artifact through the terminal fallback path.

    Raw card dictionaries remain the default because they are the common CLI
    payload shape. Callers that already know the artifact kind can pass
    ``kind="action"`` or ``kind="selection"`` to render those payloads
    without ambiguity. A typed ``TerminalArtifact`` envelope with ``kind`` and
    ``artifact`` fields is also accepted so engine payloads can stay explicit
    without forcing heuristic kind detection.
    """

    if kind is None and _is_terminal_artifact_cli_fallback_payload(artifact):
        return render_terminal_artifact_cli_fallback_payload(artifact)
    requested_kind = None
    if kind is not None:
        requested_kind = _normalize_terminal_artifact_kind(artifact, kind=kind)
    if requested_kind == "card" and _is_explicit_terminal_artifact_leaf(artifact):
        raise ValueError("Explicit typed leaf payloads cannot be rendered as cards")
    if requested_kind is None and _should_preserve_raw_leaf_card_default(artifact):
        try:
            rendered_card = render_terminal_card(artifact)
        except Exception:
            return _render_invalid_terminal_card(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_card):
            return rendered_card
        return _render_invalid_terminal_card(artifact)
    malformed_envelope = _is_malformed_terminal_artifact_envelope(artifact)
    allow_invalid_envelope_recovery = malformed_envelope
    if requested_kind == "card" and malformed_envelope and isinstance(artifact, Mapping):
        payload = artifact.get("artifact")
        envelope_kind = _normalize_terminal_artifact_envelope_kind(artifact.get("kind"))
        if _should_preserve_raw_leaf_card_default(payload):
            if envelope_kind == "card":
                return _render_invalid_terminal_card(artifact)
        else:
            payload_kind = _infer_terminal_artifact_explicit_kind(payload)
            if payload_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
                payload_kind = _recover_terminal_artifact_leaf_kind(payload)
            if payload_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
                return _render_invalid_terminal_card(artifact)
    artifact, resolved_kind = _resolve_terminal_artifact_render_target(
        artifact,
        requested_kind=requested_kind,
        allow_invalid_envelope_recovery=allow_invalid_envelope_recovery,
    )
    if resolved_kind == "action":
        rendered_action = render_terminal_action(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_action):
            return rendered_action
        return _render_invalid_terminal_action(artifact)
    if resolved_kind == "selection":
        rendered_selection = render_terminal_selection(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_selection):
            return rendered_selection
        return _render_invalid_terminal_selection(artifact)
    if requested_kind != "card":
        _validate_terminal_artifact_card_payload(artifact)
    rendered_card = render_terminal_card(artifact)
    if _is_nonempty_terminal_rendered_text(rendered_card):
        return rendered_card
    return _render_invalid_terminal_card(artifact)


def render_terminal_cli_fallback(artifact: Any, *, kind: str | None = None) -> str:
    """Render a structured A2UI artifact through the explicit CLI fallback entrypoint.

    The CLI fallback path stays independent from the generic artifact renderer
    so terminal recovery can still work if the main dispatch path is broken.
    Invalid kind hints are treated as absent so the fallback entrypoint stays
    resilient when upstream callers drift.
    """

    if kind is None and _is_terminal_artifact_cli_fallback_payload(artifact):
        return render_terminal_artifact_cli_fallback_payload(artifact)
    requested_kind = _normalize_terminal_artifact_kind_hint(kind)
    preserve_raw_leaf_card_default = _should_preserve_raw_leaf_card_default(artifact)
    if requested_kind == "card" and isinstance(artifact, (ActionRef, SelectionRef)):
        # Keep direct leaf objects on the safe invalid-card path when the
        # caller explicitly asked for card rendering. Typed mapping payloads
        # still recover through the shared fallback resolver below.
        return _render_invalid_terminal_card(artifact)
    if requested_kind == "action":
        return _render_terminal_cli_fallback_leaf(
            artifact,
            requested_kind=requested_kind,
            preserve_raw_leaf_card_default=preserve_raw_leaf_card_default,
        )
    if requested_kind == "selection":
        return _render_terminal_cli_fallback_leaf(
            artifact,
            requested_kind=requested_kind,
            preserve_raw_leaf_card_default=preserve_raw_leaf_card_default,
        )
    malformed_envelope = _is_malformed_terminal_artifact_envelope(artifact)
    envelope_kind = None
    if isinstance(artifact, Mapping):
        envelope_kind = _normalize_terminal_artifact_envelope_kind(artifact.get("kind"))
    if requested_kind == "card" and isinstance(artifact, Mapping) and malformed_envelope:
        payload = artifact.get("artifact")
        if _should_force_invalid_terminal_card_for_card_hinted_leaf(
            payload,
            envelope_kind=envelope_kind,
        ):
            return _render_invalid_terminal_card(artifact)
    if requested_kind == "card" and malformed_envelope and isinstance(artifact, Mapping):
        kind_value = artifact.get("kind")
        if not isinstance(kind_value, str) or not kind_value.strip():
            payload = artifact.get("artifact")
            if not _should_preserve_raw_leaf_card_default(payload):
                payload_kind = _infer_terminal_artifact_explicit_kind(payload)
                if payload_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
                    payload_kind = _recover_terminal_artifact_leaf_kind(payload)
                if payload_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
                    return _render_invalid_terminal_card(artifact)
    if (
        requested_kind == "card"
        and not malformed_envelope
        and isinstance(artifact, Mapping)
        and _infer_terminal_artifact_explicit_kind(artifact) in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET
    ):
        # Explicit leaf mappings should not leak leaf-shaped output through the
        # card-hint fallback path. Malformed envelopes still get a recovery
        # chance below so engine flows can unwrap bad wrappers safely.
        return _render_invalid_terminal_card(artifact)
    if requested_kind == "card" and isinstance(artifact, Mapping):
        try:
            extracted_envelope = _extract_terminal_artifact_envelope(artifact)
        except ValueError:
            extracted_envelope = None
        if extracted_envelope is not None:
            _, envelope_kind = extracted_envelope
            if (
                envelope_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET
                and not _has_nested_terminal_artifact_envelope(artifact)
            ):
                # Authoritative action/selection envelopes stay on the
                # invalid-card path when the caller explicitly asked for card
                # rendering.
                return _render_invalid_terminal_card(artifact)
    if (
        requested_kind == "card"
        and not malformed_envelope
        and isinstance(artifact, Mapping)
        and not _should_preserve_raw_leaf_card_default(artifact)
        and not _is_explicit_terminal_artifact_leaf(artifact)
    ):
        partial_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
        if partial_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            return _render_invalid_terminal_card(artifact)
    fallback_target = _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.get()
    if not _is_current_terminal_artifact_cli_fallback_hint(artifact, fallback_target):
        fallback_target = None
    resolved_fallback_target: tuple[Any, str] | None = None
    if fallback_target is None:
        try:
            fallback_target = resolve_terminal_artifact_cli_fallback_target(
                artifact,
                kind=kind,
            )
        except Exception:
            # Keep the explicit CLI fallback path usable even if the shared
            # resolver breaks by retrying the local target resolver before giving
            # up. This preserves action/selection recovery for demo flows.
            fallback_target = None
        else:
            if (
                requested_kind == "card"
                and fallback_target[1] in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET
                and not _is_explicit_terminal_artifact_leaf(artifact)
                and envelope_kind == "card"
                and not _has_nested_terminal_artifact_envelope(artifact)
            ):
                return _render_invalid_terminal_card(artifact)
    elif (
        requested_kind == "card"
        and fallback_target[1] in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET
        and not _is_explicit_terminal_artifact_leaf(artifact)
        and envelope_kind == "card"
        and not _has_nested_terminal_artifact_envelope(artifact)
    ):
        return _render_invalid_terminal_card(artifact)
    else:
        resolved_fallback_target = fallback_target

    if requested_kind == "card" and malformed_envelope and isinstance(artifact, Mapping):
        payload = artifact.get("artifact")
        if _should_preserve_raw_leaf_card_default(payload):
            if envelope_kind == "card":
                return _render_invalid_terminal_card(artifact)
        else:
            payload_kind = _infer_terminal_artifact_explicit_kind(payload)
            if payload_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
                payload_kind = _recover_terminal_artifact_leaf_kind(payload)
            if payload_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET and envelope_kind == "card":
                return _render_invalid_terminal_card(artifact)
    if fallback_target is None:
        # Keep the explicit CLI fallback path usable even if the shared
        # resolver breaks by retrying the local target resolver before giving
        # up. This preserves action/selection recovery for demo flows.
        if _should_preserve_raw_leaf_card_default(artifact):
            fallback_artifact, fallback_kind = artifact, "card"
        else:
            try:
                fallback_artifact, fallback_kind = _resolve_terminal_artifact_render_target(
                    artifact,
                    requested_kind=requested_kind,
                    allow_invalid_envelope_recovery=True,
                )
            except Exception:
                return _render_terminal_artifact_cli_fallback_failure(artifact, requested_kind=requested_kind)
            fallback_artifact, fallback_kind = refine_terminal_artifact_cli_fallback_target(
                fallback_artifact,
                fallback_kind,
                requested_kind=requested_kind,
            )
    else:
        fallback_artifact, fallback_kind = fallback_target
        fallback_artifact, fallback_kind = refine_terminal_artifact_cli_fallback_target(
            fallback_artifact,
            fallback_kind,
            requested_kind=requested_kind,
        )
        if (
            requested_kind == "card"
            and fallback_kind == "card"
            and resolved_fallback_target is not None
            and resolved_fallback_target[1] in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET
            and _has_nested_terminal_artifact_envelope(artifact)
        ):
            fallback_artifact, fallback_kind = resolved_fallback_target
    if (
        requested_kind == "card"
        and fallback_kind == "card"
        and not malformed_envelope
        and _is_explicit_terminal_artifact_leaf(fallback_artifact)
        and not _should_preserve_raw_leaf_card_default(fallback_artifact)
    ):
        recovered_kind = _infer_terminal_artifact_explicit_kind(fallback_artifact)
        if recovered_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            recovered_kind = _recover_terminal_artifact_leaf_kind(fallback_artifact)
        if recovered_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
            fallback_kind = recovered_kind
    try:
        rendered_artifact = _render_terminal_artifact_resolved(
            fallback_artifact,
            fallback_kind,
            requested_kind=requested_kind,
        )
    except Exception:
        return _render_terminal_artifact_cli_fallback_failure(artifact, requested_kind=requested_kind)
    if (
        requested_kind == "card"
        and fallback_kind == "card"
        and not _has_expected_card_renderer_prefix(rendered_artifact)
    ):
        # Card-hint fallback output must stay card-shaped. If a resolver or
        # renderer drift returns leaf text here, force the safer card fallback
        # instead of leaking action or selection presentation through the card
        # contract.
        return _render_terminal_artifact_cli_fallback_failure(artifact, requested_kind=requested_kind)
    if _is_nonempty_terminal_rendered_text(rendered_artifact):
        return rendered_artifact
    return _render_terminal_artifact_cli_fallback_failure(artifact, requested_kind=requested_kind)


def _render_terminal_cli_fallback_leaf(
    artifact: Any,
    *,
    requested_kind: str,
    preserve_raw_leaf_card_default: bool,
) -> str:
    """Render an explicit action/selection fallback target or fail safely.

    Raw leaf card-default payloads stay on the direct leaf render path so the
    explicit CLI fallback can still honor a valid leaf hint. For everything
    else, only a matching recovered target may render as the requested leaf
    kind; cross-kind recovery falls back to the invalid leaf view.
    """

    fallback_artifact = artifact
    if not preserve_raw_leaf_card_default:
        try:
            fallback_artifact, fallback_kind = resolve_terminal_artifact_cli_fallback_target(
                artifact,
                kind=requested_kind,
            )
        except Exception:
            fallback_kind = None
        else:
            if fallback_kind != requested_kind:
                if requested_kind == "action":
                    return _render_invalid_terminal_action(artifact)
                return _render_invalid_terminal_selection(artifact)
    if requested_kind == "action":
        try:
            rendered_action = render_terminal_action(fallback_artifact)
        except Exception:
            return _render_invalid_terminal_action(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_action):
            return rendered_action
        return _render_invalid_terminal_action(artifact)
    try:
        rendered_selection = render_terminal_selection(fallback_artifact)
    except Exception:
        return _render_invalid_terminal_selection(artifact)
    if _is_nonempty_terminal_rendered_text(rendered_selection):
        return rendered_selection
    return _render_invalid_terminal_selection(artifact)


def _is_current_terminal_artifact_cli_fallback_hint(
    artifact: Any,
    fallback_target: tuple[Any, str] | None,
) -> bool:
    """Return True when a CLI fallback hint matches the current artifact object.

    The shell sets the hint immediately before calling the explicit fallback
    entrypoint, so an identity check is enough to accept the intended hint
    while ignoring stale context from other renders.
    """

    if fallback_target is None:
        return False
    hinted_artifact, hinted_kind = fallback_target
    if hinted_artifact is not artifact:
        return False
    if not isinstance(hinted_kind, str):
        return False
    return hinted_kind.strip().lower() in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET


render_terminal_a2ui = render_terminal_artifact


def resolve_terminal_artifact_render_target(
    artifact: Any,
    *,
    requested_kind: str | None = None,
    allow_invalid_envelope_recovery: bool = False,
) -> tuple[Any, str]:
    """Resolve the concrete payload and render kind for a terminal artifact."""

    return _resolve_terminal_artifact_render_target(
        artifact,
        requested_kind=requested_kind,
        allow_invalid_envelope_recovery=allow_invalid_envelope_recovery,
    )


def resolve_terminal_artifact_cli_fallback_target(
    artifact: Any,
    *,
    kind: str | None = None,
) -> tuple[Any, str]:
    """Resolve the payload and render kind for the explicit CLI fallback path.

    Raw leaf card defaults stay on the card path even when a caller supplies a
    leaf kind hint, so the shell and CLI fallback can share the same
    target-selection contract without promoting an untyped payload on their
    own. If the shared render-target resolver fails on a malformed envelope,
    recover a nested leaf payload before falling back to the card default.
    """

    requested_kind = _normalize_terminal_artifact_kind_hint(kind)
    if _should_preserve_raw_leaf_card_default(artifact):
        return artifact, "card"
    if requested_kind == "card" and _is_explicit_terminal_artifact_leaf(artifact):
        # Explicit leaf payloads should stay on the card path so the CLI
        # fallback can surface the safe invalid-card renderer instead of
        # reinterpreting typed leaf JSON as a structured action or selection.
        return artifact, "card"
    if (
        requested_kind == "card"
        and isinstance(artifact, Mapping)
        and _normalize_terminal_artifact_envelope_kind(artifact.get("kind")) in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET
        and not _has_nested_terminal_artifact_envelope(artifact)
        and not _should_preserve_raw_leaf_card_default(artifact.get("artifact"))
    ):
        # A direct action/selection envelope under a card hint should not be
        # promoted to a leaf renderer on its own. Keep it on the safe invalid
        # card path and let nested envelopes opt back into leaf recovery.
        return artifact, "card"
    if requested_kind == "card" and isinstance(artifact, Mapping):
        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            # Malformed envelopes with no usable kind metadata should remain
            # on the safe card path when the caller explicitly asked for a
            # card render. Invalid string kinds still get a chance to recover
            # structured leaves below, which keeps the demo-loop fallback
            # permissive for the existing dialog-style recovery cases.
            envelope_kind = artifact.get("kind")
            if not isinstance(envelope_kind, str) or not envelope_kind.strip():
                payload = artifact.get("artifact")
                if not _should_preserve_raw_leaf_card_default(payload):
                    payload_kind = _infer_terminal_artifact_explicit_kind(payload)
                    if payload_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
                        payload_kind = _recover_terminal_artifact_leaf_kind(payload)
                    if payload_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
                        return payload, "card"
    if requested_kind is None and isinstance(artifact, Mapping):
        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            envelope_kind = _normalize_terminal_artifact_envelope_kind(artifact.get("kind"))
            if envelope_kind in {None, "card"}:
                payload = artifact.get("artifact")
                if _should_preserve_raw_leaf_card_default(payload):
                    # Keep valid card envelopes and malformed envelopes with
                    # ambiguous raw leaves on the card default when no
                    # explicit kind hint was supplied.
                    return payload, "card"

    try:
        return _resolve_terminal_artifact_render_target(
            artifact,
            requested_kind=requested_kind,
            allow_invalid_envelope_recovery=True,
        )
    except Exception:
        if requested_kind is None and isinstance(artifact, Mapping):
            artifact_type = artifact.get("type")
            if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
                recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
                    artifact,
                    requested_kind=requested_kind,
                    envelope_kind_hint=_normalize_terminal_artifact_envelope_kind(artifact.get("kind")),
                    allow_invalid_metadata=True,
                )
                if recovered is not None:
                    recovered_artifact, recovered_kind = recovered
                    while recovered_kind == "card" and isinstance(recovered_artifact, Mapping):
                        nested_recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
                            recovered_artifact,
                            requested_kind=None,
                            envelope_kind_hint=_normalize_terminal_artifact_envelope_kind(
                                recovered_artifact.get("kind")
                            ),
                            allow_invalid_metadata=True,
                        )
                        if nested_recovered is None:
                            break
                        if nested_recovered == (recovered_artifact, recovered_kind):
                            break
                        recovered_artifact, recovered_kind = nested_recovered
                    return recovered_artifact, recovered_kind
        fallback_kind = requested_kind
        if fallback_kind is None:
            fallback_kind = _infer_terminal_artifact_explicit_kind(artifact)
        if fallback_kind is None and isinstance(artifact, Mapping):
            fallback_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
        if fallback_kind is None:
            fallback_kind = "card"
        return artifact, fallback_kind


def _render_terminal_artifact_resolved(
    artifact: Any,
    resolved_kind: str,
    *,
    requested_kind: str | None = None,
) -> str:
    if resolved_kind == "action":
        try:
            rendered_action = render_terminal_action(artifact)
        except Exception:
            return _render_invalid_terminal_action(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_action):
            return rendered_action
        return _render_invalid_terminal_action(artifact)
    if resolved_kind == "selection":
        try:
            rendered_selection = render_terminal_selection(artifact)
        except Exception:
            return _render_invalid_terminal_selection(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_selection):
            return rendered_selection
        return _render_invalid_terminal_selection(artifact)
    if requested_kind != "card":
        _validate_terminal_artifact_card_payload(artifact)
    try:
        rendered_card = render_terminal_card(artifact)
    except Exception:
        return _render_invalid_terminal_card(artifact)
    if _is_nonempty_terminal_rendered_text(rendered_card):
        return rendered_card
    return _render_invalid_terminal_card(artifact)


def _has_expected_card_renderer_prefix(rendered: Any) -> bool:
    if not _is_nonempty_terminal_rendered_text(rendered):
        return False
    return not rendered.startswith(("[ActionRef]", "[SelectionRef]", "[TerminalArtifact]"))


def _render_terminal_artifact_cli_fallback_failure(
    artifact: Any,
    *,
    requested_kind: str | None,
) -> str:
    if _should_preserve_raw_leaf_card_default(artifact):
        try:
            rendered_card = render_terminal_card(artifact)
        except Exception:
            return _render_invalid_terminal_card(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_card):
            return rendered_card
        return _render_invalid_terminal_card(artifact)
    fallback_kind = requested_kind
    if fallback_kind is None:
        fallback_kind = _infer_terminal_artifact_explicit_kind(artifact)
    if fallback_kind is None and isinstance(artifact, Mapping):
        fallback_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
    if fallback_kind == "action":
        try:
            rendered_action = render_terminal_action(artifact)
        except Exception:
            return _render_invalid_terminal_action(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_action):
            return rendered_action
        return _render_invalid_terminal_action(artifact)
    if fallback_kind == "selection":
        try:
            rendered_selection = render_terminal_selection(artifact)
        except Exception:
            return _render_invalid_terminal_selection(artifact)
        if _is_nonempty_terminal_rendered_text(rendered_selection):
            return rendered_selection
        return _render_invalid_terminal_selection(artifact)
    try:
        if fallback_kind != "card":
            _validate_terminal_artifact_card_payload(artifact)
        rendered_card = render_terminal_card(artifact)
    except Exception:
        return _render_invalid_terminal_card(artifact)
    if _is_nonempty_terminal_rendered_text(rendered_card):
        return rendered_card
    return _render_invalid_terminal_card(artifact)


def _refine_terminal_artifact_cli_fallback_target(
    artifact: Any,
    resolved_kind: str | None,
    *,
    requested_kind: str | None,
) -> tuple[Any, str | None]:
    """Recover a specific leaf kind when CLI fallback underflows to a card.

    The explicit CLI fallback entrypoint should mirror the shell path closely:
    if a shared resolver returns ``card`` for a payload that is still
    recognizably an action or selection, recover that leaf kind before the
    generic card renderer runs. Raw leaf card defaults remain on the card path.
    """

    if resolved_kind != "card":
        return artifact, resolved_kind
    if requested_kind == "card":
        return artifact, resolved_kind
    if _should_preserve_raw_leaf_card_default(artifact):
        return artifact, "card"
    inferred_kind = _infer_terminal_artifact_explicit_kind(artifact)
    if inferred_kind in {"action", "selection"}:
        return artifact, inferred_kind
    partial_kind = _infer_terminal_artifact_partial_leaf_kind(artifact)
    if partial_kind in {"action", "selection"}:
        return artifact, partial_kind
    return artifact, resolved_kind


def refine_terminal_artifact_cli_fallback_target(
    artifact: Any,
    resolved_kind: str | None,
    *,
    requested_kind: str | None,
) -> tuple[Any, str | None]:
    """Public wrapper for the CLI fallback target refinement policy.

    The shell and explicit CLI fallback entrypoints share this helper so they
    recover the same leaf kinds when the shared resolver underflows to a
    generic card.
    """

    return _refine_terminal_artifact_cli_fallback_target(
        artifact,
        resolved_kind,
        requested_kind=requested_kind,
    )


def _resolve_terminal_artifact_card_fallback(
    artifact: Any,
    *,
    _seen_envelope_ids: set[int] | None = None,
) -> dict[str, Any] | None:
    if not isinstance(artifact, Mapping):
        return None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return None

    if _seen_envelope_ids is None:
        _seen_envelope_ids = set()
    artifact_id = id(artifact)
    if artifact_id in _seen_envelope_ids:
        return None
    _seen_envelope_ids.add(artifact_id)

    payload = artifact.get("artifact")
    if isinstance(payload, Mapping):
        payload_type = payload.get("type")
        if isinstance(payload_type, str) and payload_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            recovered_card = _resolve_terminal_artifact_card_fallback(
                payload,
                _seen_envelope_ids=_seen_envelope_ids,
            )
            if recovered_card is not None:
                return recovered_card
        card_payload = _coerce_terminal_card(payload)
        if card_payload is None:
            return None
        if _infer_terminal_artifact_kind_from_mapping(card_payload) in {"action", "selection"}:
            return None
        return card_payload
    return None


def _render_invalid_terminal_selection(selection: Any) -> str:
    selection = _prepare_terminal_artifact_invalid_preview(selection, expected_kind="selection")
    lines = [
        "[SelectionRef] <invalid selection>",
        f"Selection schema v{SELECTION_SCHEMA_VERSION}",
        f"A2UI v{A2UI_VERSION}",
        f"- raw: {_render_payload_preview(selection, max_payload_bytes=256)}",
    ]
    return "\n".join(lines)


def _render_invalid_terminal_action(action: Any) -> str:
    action = _prepare_terminal_artifact_invalid_preview(action, expected_kind="action")
    lines = [
        "[ActionRef] <invalid action>",
        f"Action schema v{A2UI_ACTION_SCHEMA_VERSION}",
        f"A2UI v{A2UI_VERSION}",
        f"- raw: {_render_payload_preview(action, max_payload_bytes=256)}",
    ]
    return "\n".join(lines)


def _prepare_terminal_artifact_invalid_preview(artifact: Any, *, expected_kind: str) -> Any:
    """Return a preview-safe snapshot for invalid leaf renders.

    Invalid action and selection renders should avoid echoing recoverable
    terminal-envelope wrappers so the raw preview stays focused on the leaf
    payload that actually failed validation.
    """

    if isinstance(artifact, ActionRef):
        artifact = _action_ref_to_dict(artifact)
    elif isinstance(artifact, SelectionRef):
        artifact = _selection_ref_to_dict(artifact)
    if not isinstance(artifact, Mapping):
        return artifact

    expected_type = "ActionRef" if expected_kind == "action" else "SelectionRef"
    artifact = _strip_terminal_type_hint(artifact, expected_type=expected_type)
    recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
        artifact,
        requested_kind=expected_kind,
        allow_invalid_metadata=True,
    )
    if recovered is not None:
        artifact, _ = recovered
        return artifact
    return artifact


def _normalize_terminal_artifact_kind_hint(kind: Any) -> str | None:
    """Return the canonical terminal-artifact kind hint, if any."""

    if not isinstance(kind, str):
        return None
    normalized_kind = kind.strip().lower()
    if normalized_kind in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        return normalized_kind
    return None


def _normalize_terminal_artifact_kind(artifact: Any, *, kind: str | None) -> str:
    if kind is None:
        if isinstance(artifact, ActionRef):
            return "action"
        if isinstance(artifact, SelectionRef):
            return "selection"
        if isinstance(artifact, Mapping):
            inferred_kind = _infer_terminal_artifact_kind_from_mapping(artifact)
            if inferred_kind is not None:
                return inferred_kind
        return "card"

    normalized_kind = _normalize_terminal_artifact_kind_hint(kind)
    if normalized_kind is None:
        raise ValueError("kind must be a string")
    return normalized_kind


def _extract_terminal_artifact_envelope(artifact: Any) -> tuple[Any, str] | None:
    if not isinstance(artifact, Mapping):
        return None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return None
    validate_terminal_artifact_envelope(artifact)
    kind = artifact["kind"]
    normalized_kind = kind.strip().lower()
    payload = artifact["artifact"]
    return payload, normalized_kind


def _unwrap_terminal_artifact_payload(
    artifact: Any,
    *,
    _seen_envelope_ids: set[int] | None = None,
) -> tuple[Any, str | None]:
    """Peel nested TerminalArtifact envelopes down to the concrete payload."""

    if not isinstance(artifact, Mapping):
        return artifact, None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return artifact, None

    if _seen_envelope_ids is None:
        _seen_envelope_ids = set()
    artifact_id = id(artifact)
    if artifact_id in _seen_envelope_ids:
        raise ValueError("TerminalArtifact envelope cycle detected")
    _seen_envelope_ids.add(artifact_id)

    payload = artifact.get("artifact")
    if isinstance(payload, Mapping):
        payload_type = payload.get("type")
        if isinstance(payload_type, str) and payload_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            return _unwrap_terminal_artifact_payload(payload, _seen_envelope_ids=_seen_envelope_ids)

    validate_terminal_artifact_envelope(artifact)
    kind = artifact["kind"]
    normalized_kind = kind.strip().lower()
    return payload, normalized_kind


def _recover_terminal_artifact_payload_from_invalid_envelope(
    artifact: Any,
    *,
    requested_kind: str | None,
    envelope_kind_hint: str | None = None,
    allow_invalid_metadata: bool = False,
    _seen_envelope_ids: set[int] | None = None,
) -> tuple[Any, str] | None:
    """Recover a render target from an otherwise-shaped TerminalArtifact envelope."""

    if not isinstance(artifact, Mapping):
        return None
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return None
    if not allow_invalid_metadata:
        extra_keys = set(artifact) - {"type", "kind", "artifact", "contract_version", "a2ui_version"}
        if extra_keys:
            return None
        contract_version = artifact.get("contract_version")
        if contract_version is not None and (
            type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION
        ):
            return None
        a2ui_version = artifact.get("a2ui_version")
        if a2ui_version is not None and (type(a2ui_version) is not int or a2ui_version != A2UI_VERSION):
            return None
    if "artifact" not in artifact or artifact.get("artifact") is None:
        return None

    if _seen_envelope_ids is None:
        _seen_envelope_ids = set()
    artifact_id = id(artifact)
    if artifact_id in _seen_envelope_ids:
        return None
    _seen_envelope_ids.add(artifact_id)

    payload = artifact.get("artifact")
    if isinstance(payload, Mapping):
        payload_type = payload.get("type")
        if isinstance(payload_type, str) and payload_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
            recovered = _recover_terminal_artifact_payload_from_invalid_envelope(
                payload,
                requested_kind=requested_kind,
                _seen_envelope_ids=_seen_envelope_ids,
            )
            if recovered is not None:
                return recovered

    payload_kind = _infer_terminal_artifact_explicit_kind(payload)
    if payload_kind is not None:
        return payload, payload_kind
    if requested_kind == "card":
        return payload, "card"
    if envelope_kind_hint in {"action", "selection"}:
        return payload, envelope_kind_hint
    if requested_kind in {"action", "selection"}:
        return payload, requested_kind
    if isinstance(payload, Mapping) or _coerce_terminal_card(payload) is not None:
        return payload, "card"
    return None


def _normalize_terminal_artifact_envelope_kind(kind: Any) -> str | None:
    if not isinstance(kind, str):
        return None
    normalized_kind = kind.strip().lower()
    if normalized_kind in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        return normalized_kind
    return None


def _is_malformed_terminal_artifact_envelope(artifact: Any) -> bool:
    if not isinstance(artifact, Mapping):
        return False
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return False
    try:
        validate_terminal_artifact_envelope(artifact)
    except ValueError:
        return True
    return False


def _has_nested_terminal_artifact_envelope(artifact: Any) -> bool:
    """Return True when a TerminalArtifact envelope wraps another envelope."""

    if not isinstance(artifact, Mapping):
        return False
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return False
    payload = artifact.get("artifact")
    if not isinstance(payload, Mapping):
        return False
    payload_type = payload.get("type")
    return isinstance(payload_type, str) and payload_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE


def _is_valid_terminal_artifact_envelope_metadata(artifact: Any) -> bool:
    if not isinstance(artifact, Mapping):
        return False
    extra_keys = set(artifact) - {
        "type",
        "kind",
        "artifact",
        "contract_version",
        "a2ui_version",
    }
    if extra_keys:
        return False
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return False
    if "kind" not in artifact:
        return False
    kind = artifact.get("kind")
    if not isinstance(kind, str):
        return False
    if kind.strip().lower() not in _TERMINAL_ARTIFACT_SUPPORTED_KIND_SET:
        return False
    if "artifact" not in artifact or artifact.get("artifact") is None:
        return False
    contract_version = artifact.get("contract_version")
    if contract_version is not None and (
        type(contract_version) is not int or contract_version != A2UI_CONTRACT_VERSION
    ):
        return False
    a2ui_version = artifact.get("a2ui_version")
    if a2ui_version is not None and type(a2ui_version) is not int:
        return False
    if a2ui_version is not None and a2ui_version != A2UI_VERSION:
        return False
    return True


def _is_malformed_terminal_artifact_raw_leaf_card_default_envelope(artifact: Any) -> bool:
    """Return True when a malformed envelope wraps an ambiguous raw-leaf card."""

    if not isinstance(artifact, Mapping):
        return False
    if not _is_malformed_terminal_artifact_envelope(artifact):
        return False
    return _should_preserve_raw_leaf_card_default(artifact.get("artifact"))


def _unwrap_terminal_artifact_leaf_payload(artifact: Any, *, expected_kind: str) -> Any:
    if not isinstance(artifact, Mapping):
        return artifact
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        return artifact
    try:
        payload, envelope_kind = _unwrap_terminal_artifact_payload(artifact)
    except ValueError:
        return artifact
    if envelope_kind == expected_kind:
        return payload
    return artifact


def _infer_terminal_artifact_kind_from_mapping(artifact: Mapping[str, Any]) -> str | None:
    artifact_type = artifact.get("type")
    if isinstance(artifact_type, str):
        normalized_type = artifact_type.strip()
        if normalized_type == "ActionRef":
            return "action"
        if normalized_type == "SelectionRef":
            return "selection"
        if normalized_type and normalized_type != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
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
    return None


def _infer_terminal_artifact_explicit_kind(artifact: Any) -> str | None:
    if isinstance(artifact, ActionRef):
        return "action"
    if isinstance(artifact, SelectionRef):
        return "selection"
    if isinstance(artifact, Mapping):
        artifact_type = artifact.get("type")
        if isinstance(artifact_type, str):
            normalized_type = artifact_type.strip()
            if normalized_type == "ActionRef":
                return "action"
            if normalized_type == "SelectionRef":
                return "selection"
            if normalized_type and normalized_type != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
                return "card"
        return _infer_terminal_artifact_kind_from_mapping(artifact)
    return None


def _recover_terminal_artifact_leaf_kind(artifact: Any) -> str | None:
    """Recover the most specific leaf kind from a schema-valid payload."""

    try:
        normalize_action_ref(artifact)
    except Exception:
        try:
            normalize_selection_ref(artifact)
        except Exception:
            return None
        return "selection"
    return "action"


def _infer_terminal_artifact_partial_leaf_kind(artifact: Any) -> str | None:
    """Infer a leaf kind from a partial payload that still carries action hints."""

    if not isinstance(artifact, Mapping):
        return None

    artifact_type = artifact.get("type")
    if isinstance(artifact_type, str):
        normalized_type = artifact_type.strip()
        if normalized_type == "ActionRef":
            return "action"
        if normalized_type == "SelectionRef":
            return "selection"
        if normalized_type and normalized_type != _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
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


def _should_preserve_raw_leaf_card_default(artifact: Any) -> bool:
    """Return True when an untyped raw leaf should stay on the card path."""

    if isinstance(artifact, (ActionRef, SelectionRef)):
        return False
    if not isinstance(artifact, Mapping):
        return False

    artifact_type = artifact.get("type")
    if isinstance(artifact_type, str) and artifact_type.strip():
        return False
    if any(field in artifact for field in ("confirm", "policy_sensitive", "selected", "disabled")):
        return False
    if any(field in artifact for field in ("blocks", "actions")):
        return False
    return all(field in artifact for field in ("id", "label", "payload"))


def _should_force_invalid_terminal_card_for_card_hinted_leaf(
    artifact: Any,
    *,
    envelope_kind: str | None,
) -> bool:
    """Return True when a card-hinted envelope must stay on the invalid-card path."""

    if envelope_kind != "card":
        return False
    if _should_preserve_raw_leaf_card_default(artifact):
        return False
    payload_kind = _infer_terminal_artifact_explicit_kind(artifact)
    if payload_kind not in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET:
        payload_kind = _recover_terminal_artifact_leaf_kind(artifact)
    return payload_kind in _TERMINAL_ARTIFACT_NON_CARD_KIND_SET


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
    if isinstance(artifact_type, str) and artifact_type.strip() == _TERMINAL_ARTIFACT_ENVELOPE_TYPE:
        if _seen_envelope_ids is None:
            _seen_envelope_ids = set()
        artifact_id = id(artifact)
        if artifact_id in _seen_envelope_ids:
            return False
        _seen_envelope_ids.add(artifact_id)
        payload = artifact.get("artifact")
        if payload is None:
            return False
        return _contains_action_or_selection_payload(
            payload,
            _seen_envelope_ids=_seen_envelope_ids,
        )

    if _infer_terminal_artifact_explicit_kind(artifact) in {"action", "selection"}:
        return True
    return _infer_terminal_artifact_partial_leaf_kind(artifact) is not None


def _is_explicit_terminal_artifact_leaf(artifact: Any) -> bool:
    if isinstance(artifact, (ActionRef, SelectionRef)):
        return True
    if not isinstance(artifact, Mapping):
        return False
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str):
        return False
    return artifact_type.strip() in {"ActionRef", "SelectionRef"}


def _is_explicit_terminal_artifact_leaf_mapping(artifact: Any) -> bool:
    if not isinstance(artifact, Mapping):
        return False
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str):
        return False
    return artifact_type.strip() in {"ActionRef", "SelectionRef"}


def _strip_terminal_type_hint(artifact: Mapping[str, Any], *, expected_type: str) -> dict[str, Any]:
    artifact_type = artifact.get("type")
    if not isinstance(artifact_type, str) or artifact_type.strip() != expected_type:
        return dict(artifact)

    stripped = dict(artifact)
    stripped.pop("type", None)
    return stripped


def _filter_card_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    filtered = _filter_supported_actions(card.get("actions"), supported_actions=set(capabilities.actions_supported))
    out = dict(card)
    out["actions"] = filtered
    return out


def _filter_read_only_fallback_actions(
    raw_card: dict[str, Any],
    *,
    supported_actions: set[str],
    max_payload_bytes: int,
) -> list[dict[str, Any]]:
    """Return the canonical copy action for a read-only fallback card."""

    if FALLBACK_COPY_ACTION_ID not in supported_actions:
        return []
    return [
        _build_copy_to_clipboard_action(
            _render_payload_preview(raw_card, max_payload_bytes=max_payload_bytes, pretty=True),
        )
    ]


def _build_unknown_card_actions(
    raw_card: dict[str, Any],
    *,
    supported_actions: tuple[str, ...] | set[str] | None,
    max_payload_bytes: int,
) -> list[dict[str, Any]]:
    if isinstance(supported_actions, set):
        canonical_supported_actions = supported_actions
    else:
        canonical_supported_actions = _canonicalize_supported_actions(supported_actions)
    return _filter_read_only_fallback_actions(
        raw_card,
        supported_actions=canonical_supported_actions,
        max_payload_bytes=max_payload_bytes,
    )


def _build_read_only_fallback_actions(
    raw_card: dict[str, Any],
    *,
    supported_actions: set[str],
    max_payload_bytes: int,
) -> list[dict[str, Any]]:
    return _filter_read_only_fallback_actions(
        raw_card,
        supported_actions=supported_actions,
        max_payload_bytes=max_payload_bytes,
    )


def _filter_supported_actions(actions: Any, *, supported_actions: set[str]) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in _iter_materialized_actions(actions):
        try:
            normalized = _normalize_action(action, supported_actions=supported_actions)
        except ValueError:
            continue
        normalized = _strip_action_contract_metadata(normalized)
        action_key = _canonical_action_snapshot_key(normalized)
        if action_key in seen:
            continue
        seen.add(action_key)
        filtered.append(normalized)
    # Keep tuple-shaped or reordered action containers deterministic once
    # they are materialized back into the canonical list form.
    return sorted(filtered, key=_canonical_action_snapshot_key)


def _validate_canonical_read_only_fallback_actions(
    actions: list[Any] | tuple[Any, ...],
) -> None:
    seen_actions: set[str] = set()
    for action in actions:
        validate_action_ref(action)
        action_dict = _action_ref_to_dict(action)
        if action_dict.get("id") != FALLBACK_COPY_ACTION_ID:
            raise ValueError("Fallback card actions must be copy_to_clipboard only")
        if action_dict.get("label") != "Copy JSON":
            raise ValueError("Fallback card actions must use the canonical Copy JSON label")
        if "confirm" in action_dict:
            raise ValueError("Fallback card actions must not require confirmation")
        if action_dict.get("policy_sensitive") is True:
            raise ValueError("Fallback card actions must not be policy-sensitive")
        payload = action_dict.get("payload")
        if not isinstance(payload, Mapping) or set(payload) != {"text"}:
            raise ValueError("Fallback card actions must use the canonical clipboard payload")
        if not isinstance(payload.get("text"), str):
            raise ValueError("Fallback card actions must use a string clipboard payload")
        action_key = _canonical_json(action_dict)
        if action_key in seen_actions:
            raise ValueError("Fallback card actions must not contain duplicates")
        seen_actions.add(action_key)


def _is_canonical_read_only_fallback_actions(actions: Any) -> bool:
    if actions is None:
        return True
    if not isinstance(actions, (list, tuple)):
        return False
    if not actions:
        return True
    try:
        _validate_canonical_read_only_fallback_actions(actions)
    except ValueError:
        return False
    return True


def _materialize_versioned_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    out = _canonicalize_card_top_level_fields(card)
    out["blocks"] = _extract_safe_primitive_blocks(out)
    out = _filter_card_actions(out, capabilities)
    out["title"] = _normalize_card_text(out.get("title"), fallback="<untitled>")
    subtitle = _normalize_card_text(out.get("subtitle"))
    if subtitle is None:
        out.pop("subtitle", None)
    else:
        out["subtitle"] = subtitle
    out["a2ui_version"] = A2UI_VERSION
    return out


def _materialize_generic_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    _validate_card_version(card)
    out = _canonicalize_card_top_level_fields(card)
    out["blocks"] = _extract_safe_primitive_blocks(out)
    actions = out.get("actions")
    if actions is None:
        out["actions"] = []
    else:
        # Generic cards should keep the safe subset of content instead of
        # aborting on malformed nested payloads.
        out["actions"] = _filter_supported_actions(actions, supported_actions=set(capabilities.actions_supported))
    out["title"] = _normalize_card_text(out.get("title"), fallback="<untitled>")
    subtitle = _normalize_card_text(out.get("subtitle"))
    if subtitle is None:
        out.pop("subtitle", None)
    else:
        out["subtitle"] = subtitle
    out["a2ui_version"] = A2UI_VERSION
    validate_generic_card(out)
    return out


def _materialize_unknown_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    safe_card = _canonicalize_card_top_level_fields(card)
    source_card_type = _extract_unknown_card_source_type(safe_card)
    preview_card = {
        "type": source_card_type,
        "title": _build_fallback_title(UNKNOWN_CARD_TYPE, source_card_type=source_card_type),
        "subtitle": UNKNOWN_FALLBACK_SUBTITLE,
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(source_card_type, fallback_kind="unknown"),
        "blocks": _extract_safe_primitive_blocks(safe_card, allow_code_block=False),
        "actions": [],
    }
    return build_unknown_card(
        preview_card,
        max_payload_bytes=capabilities.max_payload_bytes,
        supported_actions=set(capabilities.actions_supported),
    )


def _normalize_action(action: ActionRef | Mapping[str, Any], *, supported_actions: set[str]) -> dict[str, Any]:
    action = _action_ref_to_dict(action)
    if not isinstance(action, Mapping):
        raise ValueError("ActionRef must be an object")
    extra_keys = set(action) - {
        "id",
        "label",
        "payload",
        "confirm",
        "policy_sensitive",
        "schema_version",
        "a2ui_version",
    }
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected action field(s): {extras}")
    action_id = action.get("id")
    if not isinstance(action_id, str):
        raise ValueError("Action id is required")
    action_id = action_id.strip()
    if not action_id:
        raise ValueError("Action id is required")
    if action_id not in supported_actions:
        raise ValueError(f"Unsupported action id: {action_id}")
    label = action.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Action label is required")
    payload = action.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("Action payload must be an object")
    payload = _normalize_action_payload(action_id, payload)

    normalized: dict[str, Any] = {
        "id": action_id,
        "label": label.strip(),
        "payload": _copy_action_payload(payload),
    }
    confirm = action.get("confirm")
    if confirm is not None:
        normalized["confirm"] = _normalize_confirm(confirm)
    policy_sensitive = action.get("policy_sensitive", False)
    if not isinstance(policy_sensitive, bool):
        raise ValueError("Action policy_sensitive must be a bool")
    if policy_sensitive:
        normalized["policy_sensitive"] = True
    schema_version = action.get("schema_version", A2UI_ACTION_SCHEMA_VERSION)
    if type(schema_version) is not int:
        raise ValueError("Action schema_version must be an int")
    if schema_version != A2UI_ACTION_SCHEMA_VERSION:
        raise ValueError("Unsupported ActionRef schema_version")
    normalized["schema_version"] = schema_version
    a2ui_version = action.get("a2ui_version", A2UI_VERSION)
    if type(a2ui_version) is not int:
        raise ValueError("Action a2ui_version must be an int")
    if a2ui_version != A2UI_VERSION:
        raise ValueError("Unsupported ActionRef a2ui_version")
    normalized["a2ui_version"] = a2ui_version
    return normalized


def _normalize_selection(selection: Any) -> dict[str, Any]:
    if not isinstance(selection, Mapping):
        raise ValueError("SelectionRef must be an object")
    extra_keys = set(selection) - {
        "id",
        "label",
        "payload",
        "selected",
        "disabled",
        "schema_version",
        "a2ui_version",
    }
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected selection field(s): {extras}")
    selection_id = selection.get("id")
    if not isinstance(selection_id, str):
        raise ValueError("Selection id is required")
    selection_id = selection_id.strip()
    if not selection_id:
        raise ValueError("Selection id is required")
    label = selection.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Selection label is required")
    payload = selection.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("Selection payload must be an object")

    normalized: dict[str, Any] = {
        "id": selection_id,
        "label": label.strip(),
        "payload": _copy_selection_payload(payload),
    }
    selected = selection.get("selected", False)
    if not isinstance(selected, bool):
        raise ValueError("Selection selected must be a bool")
    if selected:
        normalized["selected"] = True
    disabled = selection.get("disabled", False)
    if not isinstance(disabled, bool):
        raise ValueError("Selection disabled must be a bool")
    if disabled:
        normalized["disabled"] = True
    schema_version = selection.get("schema_version", SELECTION_SCHEMA_VERSION)
    if type(schema_version) is not int:
        raise ValueError("Selection schema_version must be an int")
    if schema_version != SELECTION_SCHEMA_VERSION:
        raise ValueError("Unsupported SelectionRef schema_version")
    normalized["schema_version"] = schema_version
    a2ui_version = selection.get("a2ui_version", A2UI_VERSION)
    if type(a2ui_version) is not int:
        raise ValueError("Selection a2ui_version must be an int")
    if a2ui_version != A2UI_VERSION:
        raise ValueError("Unsupported SelectionRef a2ui_version")
    normalized["a2ui_version"] = a2ui_version
    return normalized


def _selection_ref_to_dict(selection: SelectionRef | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(selection, SelectionRef):
        selection_dict: dict[str, Any] = {
            "id": selection.id,
            "label": selection.label,
            "payload": _copy_selection_payload(selection.payload),
        }
        if selection.selected:
            selection_dict["selected"] = selection.selected
        if selection.disabled:
            selection_dict["disabled"] = selection.disabled
        selection_dict["schema_version"] = selection.schema_version
        selection_dict["a2ui_version"] = selection.a2ui_version
        return selection_dict
    if isinstance(selection, Mapping):
        selection_dict = dict(selection)
        selection_type = selection_dict.get("type")
        if isinstance(selection_type, str) and selection_type.strip() == "SelectionRef":
            selection_dict.pop("type", None)
        return selection_dict
    raise ValueError("SelectionRef must be an object")


def _action_ref_to_dict(action: ActionRef | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(action, ActionRef):
        action_dict: dict[str, Any] = {
            "id": action.id,
            "label": action.label,
            "payload": _copy_action_payload(action.payload),
        }
        if action.confirm is not None:
            action_dict["confirm"] = action.confirm
        if action.policy_sensitive:
            action_dict["policy_sensitive"] = action.policy_sensitive
        action_dict["schema_version"] = action.schema_version
        action_dict["a2ui_version"] = action.a2ui_version
        return action_dict
    if isinstance(action, Mapping):
        action_dict = dict(action)
        action_type = action_dict.get("type")
        if isinstance(action_type, str) and action_type.strip() == "ActionRef":
            action_dict.pop("type", None)
        return action_dict
    raise ValueError("ActionRef must be an object")


def _strip_action_contract_metadata(action: dict[str, Any]) -> dict[str, Any]:
    stripped = dict(action)
    stripped.pop("schema_version", None)
    stripped.pop("a2ui_version", None)
    return stripped


def _normalize_confirm(confirm: Any) -> dict[str, str]:
    if not isinstance(confirm, Mapping):
        raise ValueError("Action confirm must be an object")
    title = confirm.get("title")
    message = confirm.get("message")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Action confirm title is required")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Action confirm message is required")
    extra_keys = set(confirm) - {"title", "message"}
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected confirm field(s): {extras}")
    return {"title": title.strip(), "message": message.strip()}


def _copy_selection_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _copy_terminal_artifact_payload(payload)


def _copy_action_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _copy_terminal_artifact_payload(payload)


def _copy_terminal_artifact_payload(artifact: Any) -> Any:
    """Return an isolated snapshot for a terminal artifact payload.

    The terminal artifact envelope is a public contract boundary. Snapshotting
    the payload keeps engine-produced envelopes deterministic even if the
    original object is mutated after the wrapper is built. Nested A2UI
    dataclasses are converted to plain dictionaries so the snapshot stays
    client-friendly for CLI fallback rendering.
    """

    return _snapshot_terminal_artifact_value(artifact)


def _snapshot_terminal_artifact_value(value: Any, *, _seen_ids: set[int] | None = None) -> Any:
    if _seen_ids is None:
        _seen_ids = set()

    if isinstance(value, ActionRef):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            return _snapshot_terminal_artifact_value(_action_ref_to_dict(value), _seen_ids=_seen_ids)
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, SelectionRef):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            return _snapshot_terminal_artifact_value(_selection_ref_to_dict(value), _seen_ids=_seen_ids)
        finally:
            _seen_ids.remove(value_id)

    if is_dataclass(value) and not isinstance(value, type):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            try:
                snapshot = {field.name: getattr(value, field.name) for field in fields(value)}
            except Exception:
                try:
                    return copy.deepcopy(value)
                except Exception:
                    return f"<non-json:{type(value).__name__}>"
            return {
                key: _snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids)
                for key, item in snapshot.items()
            }
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, Mapping):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            sanitized_items = [
                (
                    _terminal_artifact_mapping_key_label(key, _seen_ids=_seen_ids),
                    _snapshot_terminal_artifact_value(value[key], _seen_ids=_seen_ids),
                )
                for key in value
            ]
            return {
                key: sanitized_value
                for key, sanitized_value in sorted(sanitized_items, key=lambda item: item[0])
            }
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, list):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            return [_snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, tuple):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            # Normalize tuple-shaped snapshots to JSON-native lists so
            # terminal artifact envelopes stay language-agnostic.
            return [_snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, Set):
        value_id = id(value)
        if value_id in _seen_ids:
            return f"<cycle:{type(value).__name__}>"
        _seen_ids.add(value_id)
        try:
            # Unordered set-like containers need a deterministic JSON-safe representation.
            normalized_items = [
                _snapshot_terminal_artifact_value(item, _seen_ids=_seen_ids) for item in value
            ]
            return sorted(normalized_items, key=_canonical_json_sort_key)
        finally:
            _seen_ids.remove(value_id)

    try:
        snapshot = copy.deepcopy(value)
    except Exception:
        return f"<non-json:{type(value).__name__}>"
    return _json_safe_terminal_artifact_value(snapshot, source_type=type(value).__name__)


def _terminal_artifact_mapping_key_label(key: Any, *, _seen_ids: set[int]) -> str:
    if isinstance(key, str):
        return key
    key_snapshot = _snapshot_terminal_artifact_value(key, _seen_ids=_seen_ids)
    try:
        key_preview = _canonical_json(key_snapshot)
    except (TypeError, ValueError):
        key_preview = f'"<non-json:{type(key).__name__}>"'
    return f"<key:{type(key).__name__}:{key_preview}>"


def _json_safe_terminal_artifact_value(value: Any, *, source_type: str) -> Any:
    try:
        _canonical_json(value)
    except (TypeError, ValueError):
        return f"<non-json:{source_type}>"
    return value


def _validate_action_payload(action_id: str, payload: Mapping[str, Any]) -> None:
    _normalize_action_payload(action_id, payload)


def _normalize_action_payload(action_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"No schema for action id: {action_id}")
    extra_keys = set(payload) - set(schema)
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected payload field for {action_id}: {extras}")
    normalized: dict[str, Any] = {}
    identifier_fields = set(_ACTION_PAYLOAD_IDENTIFIER_FIELDS.get(action_id, ()))
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field for {action_id}: {key}")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Invalid payload type for {action_id}:{key}")
        value = payload[key]
        if value_type is str and isinstance(value, str):
            normalized[key] = (
                _normalize_action_payload_identifier(action_id, key, value)
                if key in identifier_fields
                else value
            )
            continue
        normalized[key] = _snapshot_terminal_artifact_value(value)
    return normalized


def _normalize_action_payload_identifier(action_id: str, key: str, value: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f"Action payload field for {action_id}:{key} must be non-empty")
    if any(unicodedata.category(char).startswith("C") for char in normalized_value):
        raise ValueError(f"Action payload field for {action_id}:{key} must not contain control characters")
    return normalized_value


def _action_payload_field_policy_label(action_id: str) -> str | None:
    identifier_fields = tuple(_ACTION_PAYLOAD_IDENTIFIER_FIELDS.get(action_id, ()))
    free_text_fields = tuple(_ACTION_PAYLOAD_FREE_TEXT_FIELDS.get(action_id, ()))
    parts: list[str] = []
    if identifier_fields:
        parts.append(f"identifier={','.join(identifier_fields)}")
    if free_text_fields:
        parts.append(f"free_text={','.join(free_text_fields)}")
    if not parts:
        return None
    return "; ".join(parts)


def _validate_primitive_block_fields(block_type: str, block: Mapping[str, Any]) -> None:
    schema_fields = set(_PRIMITIVE_BLOCK_SCHEMAS[block_type])
    required_fields = set(_PRIMITIVE_BLOCK_REQUIRED_FIELDS[block_type])
    extra_keys = set(block) - ({"type"} | schema_fields)
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected primitive block field(s) for {block_type}: {extras}")
    for field_name in required_fields:
        if field_name not in block:
            raise ValueError(f"Missing primitive block field for {block_type}: {field_name}")
    if block_type == "MarkdownBlock":
        if not isinstance(block["markdown"], str):
            raise ValueError("Invalid primitive block field for MarkdownBlock: markdown")
        return
    if block_type == "KeyValueBlock":
        if not isinstance(block["items"], list):
            raise ValueError("Invalid primitive block field for KeyValueBlock: items")
        return
    if block_type == "ListBlock":
        if not isinstance(block["items"], list):
            raise ValueError("Invalid primitive block field for ListBlock: items")
        return
    if block_type == "TableBlock":
        if not isinstance(block["rows"], list):
            raise ValueError("Invalid primitive block field for TableBlock: rows")
        return
    if block_type == "AlertBlock":
        if not isinstance(block["message"], str):
            raise ValueError("Invalid primitive block field for AlertBlock: message")
        severity = block.get("severity")
        if severity is not None and not isinstance(severity, str):
            raise ValueError("Invalid primitive block field for AlertBlock: severity")
        title = block.get("title")
        if title is not None and not isinstance(title, str):
            raise ValueError("Invalid primitive block field for AlertBlock: title")
        return
    if block_type == "ProgressBlock":
        if not isinstance(block["status_text"], str):
            raise ValueError("Invalid primitive block field for ProgressBlock: status_text")
        title = block.get("title")
        if title is not None and not isinstance(title, str):
            raise ValueError("Invalid primitive block field for ProgressBlock: title")
        return
    if block_type == "CodeBlock":
        if not isinstance(block["code"], str):
            raise ValueError("Invalid primitive block field for CodeBlock: code")
        language = block.get("language")
        if language is not None and not isinstance(language, str):
            raise ValueError("Invalid primitive block field for CodeBlock: language")
        collapsed = block.get("collapsed")
        if collapsed is not None and not isinstance(collapsed, bool):
            raise ValueError("Invalid primitive block field for CodeBlock: collapsed")
        return


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _canonicalize_card_top_level_fields(card: dict[str, Any]) -> dict[str, Any]:
    allowed_keys = ("type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions")
    out = {key: card[key] for key in allowed_keys if key in card}
    if "debug" in out:
        try:
            out["debug"] = copy.deepcopy(out["debug"])
        except Exception:
            pass
    return out


def _canonicalize_terminal_artifact_card_actions(card: dict[str, Any]) -> dict[str, Any]:
    actions = card.get("actions")
    if not isinstance(actions, list):
        return card

    canonical_actions: list[Any] = []
    seen: set[str] = set()
    for action in actions:
        snapshot = _snapshot_terminal_artifact_value(action)
        action_key = _canonical_action_snapshot_key(snapshot)
        if action_key in seen:
            continue
        seen.add(action_key)
        canonical_actions.append(snapshot)

    return {
        **card,
        "actions": sorted(canonical_actions, key=_canonical_action_snapshot_key),
    }


def _canonical_action_snapshot_key(action: Any) -> str:
    if isinstance(action, Mapping):
        return _canonical_json(action)
    return _canonical_json({"type": type(action).__name__, "value": action})


def _render_payload_preview(
    payload: dict[str, Any],
    *,
    max_payload_bytes: int | None,
    pretty: bool = False,
) -> str:
    sanitized_payload = _sanitize_json_preview_value(payload)
    rendered = json.dumps(
        sanitized_payload,
        indent=2 if pretty else None,
        sort_keys=True,
        separators=None if pretty else (",", ":"),
        ensure_ascii=True,
    )
    if max_payload_bytes is None or len(rendered.encode("utf-8")) <= max_payload_bytes:
        return rendered
    if max_payload_bytes <= 0:
        return ""

    budget = max_payload_bytes
    suffix = f"\n...[truncated to {max_payload_bytes} bytes]" if pretty else f"...[truncated to {max_payload_bytes} bytes]"
    suffix_bytes = len(suffix.encode("utf-8"))
    if suffix_bytes >= budget:
        return suffix[:budget]

    prefix = rendered.encode("utf-8")[: budget - suffix_bytes].decode("utf-8", errors="ignore")
    return f"{prefix}{suffix}"


def _build_copy_to_clipboard_action(text: str) -> dict[str, Any]:
    return _strip_action_contract_metadata(
        _normalize_action(
            {
                "id": FALLBACK_COPY_ACTION_ID,
                "label": "Copy JSON",
                "payload": {"text": text},
            },
            supported_actions={FALLBACK_COPY_ACTION_ID},
        )
    )


def _sanitize_json_preview_value(value: Any, *, _seen_ids: set[int] | None = None) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if _seen_ids is None:
        _seen_ids = set()

    value_id = id(value)
    if value_id in _seen_ids:
        return f"<cycle:{type(value).__name__}>"

    if isinstance(value, Mapping):
        _seen_ids.add(value_id)
        try:
            sanitized_items = [
                (str(key), _sanitize_json_preview_value(value[key], _seen_ids=_seen_ids))
                for key in sorted(value, key=lambda item: str(item))
            ]
            return {key: sanitized_value for key, sanitized_value in sanitized_items}
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, list):
        _seen_ids.add(value_id)
        try:
            return [_sanitize_json_preview_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, tuple):
        _seen_ids.add(value_id)
        try:
            return [_sanitize_json_preview_value(item, _seen_ids=_seen_ids) for item in value]
        finally:
            _seen_ids.remove(value_id)

    if isinstance(value, Set):
        _seen_ids.add(value_id)
        try:
            sanitized_items = [_sanitize_json_preview_value(item, _seen_ids=_seen_ids) for item in value]
            return sorted(sanitized_items, key=_canonical_json_sort_key)
        finally:
            _seen_ids.remove(value_id)

    return f"<non-json:{type(value).__name__}>"


def _is_safe_scalar_value(value: Any) -> bool:
    return value is None or isinstance(value, (bool, int, float, str))


def _canonical_json_sort_key(value: Any) -> str:
    if isinstance(value, Mapping):
        return _canonical_json({str(key): value[key] for key in sorted(value, key=lambda item: str(item))})
    if isinstance(value, list):
        return _canonical_json({"items": value})
    return str(value)


def _render_terminal_actions(actions: Any, *, supported_actions: set[str]) -> list[str]:
    normalized_actions = _canonicalize_supported_action_list(actions, supported_actions=supported_actions)

    identity_counts: dict[str, int] = {}
    for action in normalized_actions:
        identity_key = _canonical_json(
            {
                "id": _render_terminal_inline_text(action["id"]),
                "label": _render_terminal_inline_text(action["label"]),
            }
        )
        identity_counts[identity_key] = identity_counts.get(identity_key, 0) + 1

    lines: list[str] = []
    for action in normalized_actions:
        label = _render_terminal_inline_text(action["label"])
        action_id = _render_terminal_inline_text(action["id"])
        identity_key = _canonical_json({"id": action_id, "label": label})
        if identity_counts.get(identity_key, 0) > 1:
            payload_preview = _render_payload_preview(action["payload"], max_payload_bytes=96)
            lines.append(
                f"- {label} ({action_id}{_render_action_variant_suffix(action)}; payload: {payload_preview})"
            )
            continue
        lines.append(f"- {label} ({action_id}{_render_action_variant_suffix(action)})")
    return lines


def _render_action_variant_suffix(action: dict[str, Any]) -> str:
    suffix_parts: list[str] = []
    confirm = action.get("confirm")
    if isinstance(confirm, Mapping):
        confirm_title = confirm.get("title")
        if isinstance(confirm_title, str) and confirm_title.strip():
            suffix_parts.append(f"confirm: {_render_terminal_inline_text(confirm_title.strip())}")
        else:
            suffix_parts.append("confirm")
    if action.get("policy_sensitive") is True:
        suffix_parts.append("policy-sensitive")
    if not suffix_parts:
        return ""
    return "; " + "; ".join(suffix_parts)


def _render_terminal_debug(debug: Any) -> list[str]:
    if not isinstance(debug, Mapping):
        return []
    lines: list[str] = []
    for key in sorted(debug):
        value = debug[key]
        if isinstance(value, bool):
            rendered_value = "true" if value else "false"
        elif isinstance(value, (str, int)):
            rendered_value = _render_terminal_inline_text(value)
        else:
            continue
        lines.append(f"- {key}: {rendered_value}")
    return lines


def _render_terminal_fallback_debug(
    card_type: str,
    title: str,
    debug: Any,
    *,
    generic_fallback_source: str | None = None,
) -> list[str]:
    fallback_debug = _extract_terminal_fallback_debug(debug)
    if fallback_debug is None:
        if card_type == UNKNOWN_CARD_TYPE:
            source_card_type = _infer_unknown_fallback_source(title)
            fallback_kind = "unknown"
        elif card_type == GENERIC_CARD_TYPE:
            source_card_type = generic_fallback_source
            fallback_kind = "generic"
        else:
            return []
        if source_card_type is None:
            return []
    else:
        fallback_kind, source_card_type = fallback_debug

    lines: list[str] = []
    contract_version = None
    if isinstance(debug, Mapping):
        contract_version = debug.get("contract_version")
    if type(contract_version) is not int:
        contract_version = A2UI_CONTRACT_VERSION
    lines.append(f"- contract_version: {contract_version}")
    lines.append(f"- fallback_kind: {_render_terminal_inline_text(fallback_kind)}")
    lines.append(f"- source_card_type: {_render_terminal_inline_text(source_card_type)}")
    return lines


def _render_terminal_fallback_notice(
    card_type: str,
    title: str,
    *,
    debug: Any,
    generic_fallback_source: str | None = None,
    generic_fallback_hint: bool = False,
) -> list[str]:
    fallback_debug = _extract_terminal_fallback_debug(debug)
    if fallback_debug is not None:
        fallback_kind, source_card_type = fallback_debug
        return [
            f"Fallback: {_render_terminal_inline_text(fallback_kind)} from {_render_terminal_inline_text(source_card_type)}"
        ]
    if card_type == UNKNOWN_CARD_TYPE:
        source_card_type = _infer_unknown_fallback_source(title)
        if source_card_type is not None:
            return [f"Fallback: unknown from {_render_terminal_inline_text(source_card_type)}"]
        return ["Fallback: unknown card"]
    if card_type == GENERIC_CARD_TYPE:
        if generic_fallback_source is not None:
            return [f"Fallback: generic from {_render_terminal_inline_text(generic_fallback_source)}"]
        if generic_fallback_hint:
            return ["Fallback: generic card"]
    return []


def _extract_terminal_fallback_debug(debug: Any) -> tuple[str, str] | None:
    if not isinstance(debug, Mapping):
        return None
    fallback_kind = debug.get("fallback_kind")
    source_card_type = debug.get("source_card_type")
    if not isinstance(fallback_kind, str) or not isinstance(source_card_type, str):
        return None
    normalized_fallback_kind = fallback_kind.strip()
    normalized_source_card_type = source_card_type.strip()
    if normalized_fallback_kind not in {"generic", "unknown"}:
        return None
    if not normalized_source_card_type:
        return None
    return normalized_fallback_kind, normalized_source_card_type


def _render_terminal_action_policy(
    card_type: str,
    title: str,
    debug: Any,
    *,
    generic_fallback_source: str | None = None,
    generic_fallback_hint: bool = False,
) -> list[str]:
    if card_type == UNKNOWN_CARD_TYPE:
        return ["Action policy: copy_to_clipboard_only"]
    if card_type == GENERIC_CARD_TYPE and (
        _is_fallback_card_debug(debug)
        or generic_fallback_source is not None
        or generic_fallback_hint
    ):
        return ["Action policy: client_allowlist"]
    return []


def _is_fallback_card_debug(debug: Any) -> bool:
    return _extract_terminal_fallback_debug(debug) is not None


def _resolve_generic_fallback_source(title: str, actions: Any, debug: Any) -> str | None:
    fallback_debug = _extract_terminal_fallback_debug(debug)
    if fallback_debug is not None:
        fallback_kind, source_card_type = fallback_debug
        if fallback_kind == "generic":
            return source_card_type
        return None

    source_card_type = _infer_generic_fallback_source(title)
    if source_card_type is None:
        return None
    if actions is None:
        return source_card_type
    if not _is_canonical_read_only_fallback_actions(actions):
        return None
    return source_card_type


def _is_canonical_generic_fallback_signal(subtitle: Any, actions: Any) -> bool:
    if not isinstance(subtitle, str) or subtitle.strip() != GENERIC_FALLBACK_SUBTITLE:
        return False
    return actions is None or _is_canonical_read_only_fallback_actions(actions)


def _infer_generic_fallback_source(title: str) -> str | None:
    if not title.startswith(GENERIC_FALLBACK_TITLE_PREFIX):
        return None
    source_card_type = title[len(GENERIC_FALLBACK_TITLE_PREFIX) :].strip()
    return source_card_type or None


def _infer_unknown_fallback_source(title: str) -> str | None:
    if not title.startswith(UNKNOWN_FALLBACK_TITLE_PREFIX):
        return None
    source_card_type = title[len(UNKNOWN_FALLBACK_TITLE_PREFIX) :].strip()
    return source_card_type or None


def _iter_card_entries(entries: Any) -> list[Any]:
    materialized, _incomplete = _materialize_card_entry_iterable(entries)
    return materialized


def _materialize_card_entry_iterable(entries: Any) -> tuple[list[Any], bool]:
    if not isinstance(entries, Iterable) or isinstance(entries, (str, bytes, bytearray, Mapping)):
        return [], False
    materialized: list[Any] = []
    try:
        for entry in entries:
            materialized.append(entry)
    except Exception:
        return materialized, True
    return materialized, False


def _materialize_card_actions(actions: Any) -> list[Any]:
    materialized, _incomplete = _materialize_action_iterable(actions)
    return materialized


def _iter_materialized_actions(actions: Any) -> list[Any]:
    materialized, _incomplete = _materialize_action_iterable(actions)
    return materialized


def _materialize_action_iterable(actions: Any) -> tuple[list[Any], bool]:
    if not isinstance(actions, Iterable) or isinstance(actions, (str, bytes, bytearray, Mapping)):
        return [], False
    materialized: list[Any] = []
    try:
        for action in actions:
            materialized.append(action)
    except Exception:
        return materialized, True
    return materialized, False


def _normalize_card_type(card: dict[str, Any]) -> str:
    raw_type = card.get("type")
    if not isinstance(raw_type, str):
        return "<missing>"
    card_type = raw_type.strip()
    return card_type if card_type else "<missing>"


def _normalize_card_title(card: dict[str, Any]) -> str:
    raw_title = card.get("title")
    if not isinstance(raw_title, str):
        return "<untitled>"
    title = raw_title.strip()
    return title if title else "<untitled>"


def _normalize_card_text(value: Any, *, fallback: str | None = None) -> str | None:
    if value is None:
        return fallback
    if not isinstance(value, str):
        return fallback
    normalized = value.strip()
    if normalized:
        return normalized
    return fallback


def _build_fallback_debug(source_card_type: str, *, fallback_kind: str) -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "fallback_kind": fallback_kind,
        "source_card_type": source_card_type,
    }


def _extract_unknown_card_source_type(card: dict[str, Any]) -> str:
    debug = card.get("debug")
    if isinstance(debug, Mapping):
        source_card_type = debug.get("source_card_type")
        if isinstance(source_card_type, str):
            normalized_source_card_type = source_card_type.strip()
            if normalized_source_card_type:
                return normalized_source_card_type
    normalized_type = _normalize_card_type(card)
    return normalized_type if normalized_type != "<missing>" else UNKNOWN_CARD_TYPE


def _normalize_preview_budget(max_payload_bytes: int | None) -> int:
    if max_payload_bytes is None:
        return DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES
    if type(max_payload_bytes) is not int:
        raise ValueError("max_payload_bytes must be an int or None")
    if max_payload_bytes < 0:
        raise ValueError("max_payload_bytes must be non-negative")
    return max_payload_bytes


def _build_fallback_title(expected_type: str, *, source_card_type: str) -> str:
    if expected_type == GENERIC_CARD_TYPE:
        return f"Fallback view for {source_card_type}"
    if expected_type == UNKNOWN_CARD_TYPE:
        return f"{UNKNOWN_FALLBACK_TITLE_PREFIX}{source_card_type}"
    raise ValueError(f"Unsupported fallback card type: {expected_type}")


def _fallback_subtitle(fallback_kind: str) -> str:
    if fallback_kind == "generic":
        return GENERIC_FALLBACK_SUBTITLE
    if fallback_kind == "unknown":
        return UNKNOWN_FALLBACK_SUBTITLE
    raise ValueError(f"Unsupported fallback kind: {fallback_kind}")


def _extract_safe_primitive_blocks(card: dict[str, Any], *, allow_code_block: bool = True) -> list[dict[str, Any]]:
    safe_blocks: list[dict[str, Any]] = []
    for block in _iter_card_entries(card.get("blocks")):
        sanitized_block = _sanitize_safe_primitive_block(block, allow_code_block=allow_code_block)
        if sanitized_block is not None:
            safe_blocks.append(sanitized_block)
    return safe_blocks


def _sanitize_safe_primitive_block(block: Any, *, allow_code_block: bool = True) -> dict[str, Any] | None:
    if not isinstance(block, Mapping):
        return None
    block_type = str(block.get("type", "")).strip()
    if block_type not in _PRIMITIVE_BLOCK_SET:
        return None
    if block_type == "MarkdownBlock":
        markdown = block.get("markdown")
        if not isinstance(markdown, str):
            return None
        return {"type": block_type, "markdown": markdown}
    if block_type == "AlertBlock":
        message = block.get("message")
        if not isinstance(message, str):
            return None
        sanitized: dict[str, Any] = {
            "type": block_type,
            "severity": _normalize_card_text(block.get("severity"), fallback="info") or "info",
            "message": message,
        }
        title = _normalize_card_text(block.get("title"))
        if title is not None:
            sanitized["title"] = title
        return sanitized
    if block_type == "CodeBlock":
        if not allow_code_block:
            return None
        code = block.get("code")
        if not isinstance(code, str):
            return None
        sanitized = {"type": block_type, "code": code}
        language = block.get("language")
        if language is not None:
            if not isinstance(language, str):
                return None
            sanitized["language"] = language
        collapsed = block.get("collapsed")
        if collapsed is not None:
            if not isinstance(collapsed, bool):
                return None
            sanitized["collapsed"] = collapsed
        return sanitized
    if block_type == "ProgressBlock":
        status_text = block.get("status_text")
        if not isinstance(status_text, str):
            return None
        sanitized = {
            "type": block_type,
            "status_text": status_text,
        }
        title = block.get("title")
        if title is not None:
            if not isinstance(title, str):
                return None
            sanitized["title"] = title
        return sanitized
    if block_type == "KeyValueBlock":
        items = block.get("items")
        if not isinstance(items, list):
            return None
        sanitized_items: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            key = item.get("key")
            if not isinstance(key, str) or not key.strip():
                continue
            value = item.get("value")
            if not _is_safe_scalar_value(value):
                continue
            sanitized_items.append({"key": key.strip(), "value": value})
        if not sanitized_items:
            return None
        return {"type": block_type, "items": sanitized_items}
    if block_type == "ListBlock":
        items = block.get("items")
        if not isinstance(items, list):
            return None
        sanitized_items: list[Any] = []
        for item in items:
            if isinstance(item, str):
                rendered_item = item.strip()
                if rendered_item:
                    sanitized_items.append(rendered_item)
            elif isinstance(item, Mapping):
                label = item.get("label")
                if isinstance(label, str) and label.strip():
                    sanitized_items.append({"label": label.strip()})
        if not sanitized_items:
            return None
        return {"type": block_type, "items": sanitized_items}
    if block_type == "TableBlock":
        rows = block.get("rows")
        if not isinstance(rows, list):
            return None
        sanitized_rows: list[list[Any]] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            sanitized_row: list[Any] = []
            for cell in row:
                if isinstance(cell, (str, int, float, bool)) or cell is None:
                    sanitized_row.append(cell)
            if sanitized_row:
                sanitized_rows.append(sanitized_row)
        if not sanitized_rows:
            return None
        return {"type": block_type, "rows": sanitized_rows}
    return None


def _canonicalize_supported_actions(supported_actions: tuple[str, ...] | None) -> set[str]:
    if supported_actions is None:
        return set(_ALLOWED_ACTION_SET)

    canonical_actions: set[str] = set()
    for action_id in supported_actions:
        if not isinstance(action_id, str):
            continue
        normalized_action_id = action_id.strip()
        if normalized_action_id in _ALLOWED_ACTION_SET:
            canonical_actions.add(normalized_action_id)
    return canonical_actions


def _canonicalize_supported_action_list(
    actions: Any,
    *,
    supported_actions: set[str],
) -> list[dict[str, Any]]:
    """Return a deterministic, deduplicated action snapshot for rendering.

    The terminal fallback path consumes this helper directly, so the
    canonical order needs to be stable even when callers supply list or tuple
    inputs in different orders. Sorting here keeps the helper itself
    contract-safe instead of relying on downstream renderers to normalize it.
    """

    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in _iter_materialized_actions(actions):
        try:
            normalized = _normalize_action(action, supported_actions=supported_actions)
        except ValueError:
            continue
        action_key = _canonical_action_snapshot_key(normalized)
        if action_key in seen:
            continue
        seen.add(action_key)
        filtered.append(normalized)
    return sorted(filtered, key=_canonical_action_snapshot_key)


def _validate_supported_string_sequence(values: Any, *, field_name: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"{field_name} must be a list or tuple of strings")
    validated: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must contain only strings")
        validated.append(value)
    return tuple(validated)


def _render_terminal_block(block: Any) -> list[str]:
    if not isinstance(block, Mapping):
        return ["[unsupported block: malformed]"]
    block_type = str(block.get("type", "")).strip()
    if not block_type:
        return ["[unsupported block: missing type]"]
    if block_type == "MarkdownBlock":
        markdown = block.get("markdown")
        if not isinstance(markdown, str):
            return _render_terminal_invalid_primitive_block(block_type, "markdown")
        return [_render_terminal_text(markdown)]
    if block_type == "AlertBlock":
        message = block.get("message")
        if not isinstance(message, str):
            return _render_terminal_invalid_primitive_block(block_type, "message")
        severity_value = block.get("severity", "info")
        if isinstance(severity_value, str):
            severity = _render_terminal_inline_text(severity_value.strip()).upper() or "INFO"
        else:
            severity = "INFO"
        message = _render_terminal_inline_text(message)
        return [f"{severity}: {message}"]
    if block_type == "CodeBlock":
        code = block.get("code")
        if not isinstance(code, str):
            return _render_terminal_invalid_primitive_block(block_type, "code")
        return [_render_terminal_text(code)]
    if block_type == "ProgressBlock":
        status_text = block.get("status_text")
        if not isinstance(status_text, str):
            return _render_terminal_invalid_primitive_block(block_type, "status_text")
        title_value = block.get("title", "progress")
        if isinstance(title_value, str):
            title = _render_terminal_inline_text(title_value) or "progress"
        else:
            title = "progress"
        status_text = _render_terminal_inline_text(status_text)
        return [f"{title}: {status_text}"]
    if block_type == "KeyValueBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[KeyValueBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if not isinstance(item, Mapping):
                continue
            key = _render_terminal_inline_text(item.get("key", ""))
            if not key:
                continue
            value = item.get("value", None)
            if not _is_safe_scalar_value(value):
                continue
            if isinstance(value, bool):
                value = "true" if value else "false"
            value = _render_terminal_inline_text(value) or "<blank>"
            lines.append(f"- {key}: {value}")
        return lines or ["[KeyValueBlock: empty]"]
    if block_type == "ListBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[ListBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if isinstance(item, str):
                rendered_item = _render_terminal_inline_text(item)
                if rendered_item:
                    lines.append(f"- {rendered_item}")
            elif isinstance(item, Mapping):
                label = item.get("label", "")
                if isinstance(label, str):
                    rendered_label = _render_terminal_inline_text(label)
                    if rendered_label:
                        lines.append(f"- {rendered_label}")
        return lines or ["[ListBlock: empty]"]
    if block_type == "TableBlock":
        rows = block.get("rows", [])
        if not isinstance(rows, list):
            return ["[table: invalid rows]"]
        lines = ["[table]"]
        for row in rows:
            if not isinstance(row, list):
                continue
            rendered_cells: list[str] = []
            for cell in row:
                if cell is None:
                    rendered_cells.append("<blank>")
                elif isinstance(cell, bool):
                    rendered_cells.append("true" if cell else "false")
                elif isinstance(cell, (str, int, float)):
                    rendered_cells.append(_render_terminal_inline_text(cell))
                else:
                    rendered_cells.append(f"<non-json:{type(cell).__name__}>")
            if rendered_cells:
                lines.append(f"- {' | '.join(rendered_cells)}")
        return lines if len(lines) > 1 else ["[table: empty]"]
    return [f"[unsupported block: {_render_terminal_inline_text(block_type)}]"]


def _render_terminal_invalid_primitive_block(block_type: str, field_name: str) -> list[str]:
    return [f"[{block_type}: invalid {field_name}]"]


def _coerce_card_payload(card: Any) -> dict[str, Any] | None:
    if isinstance(card, dict):
        return card
    if isinstance(card, Mapping):
        try:
            return dict(card)
        except Exception:
            return None
    if is_dataclass(card) and not isinstance(card, type):
        try:
            snapshot = _snapshot_terminal_artifact_value(card)
        except Exception:
            return None
        if isinstance(snapshot, Mapping):
            return dict(snapshot)
        return None
    if not any(hasattr(card, attr) for attr in ("type", "title", "subtitle", "blocks", "actions", "debug", "a2ui_version")):
        return None
    try:
        snapshot = dict(vars(card))
    except Exception:
        return None
    if isinstance(snapshot, Mapping):
        return dict(snapshot)
    return None


def _coerce_terminal_card(card: Any) -> dict[str, Any] | None:
    if isinstance(card, dict):
        return card
    if isinstance(card, Mapping):
        try:
            return dict(card)
        except Exception:
            return None
    required_attrs = ("type", "title", "blocks", "actions")
    if not all(hasattr(card, attr) for attr in required_attrs):
        return None
    card_type = getattr(card, "type")
    if not isinstance(card_type, str):
        return None
    normalized_card_type = card_type.strip()
    if not normalized_card_type or normalized_card_type in {"ActionRef", "SelectionRef", _TERMINAL_ARTIFACT_ENVELOPE_TYPE}:
        return None
    if is_dataclass(card):
        try:
            snapshot = _snapshot_terminal_artifact_value(card)
        except Exception:
            return None
        if isinstance(snapshot, Mapping):
            return dict(snapshot)
        return None
    try:
        snapshot = dict(vars(card))
    except Exception:
        return None
    if isinstance(snapshot, Mapping):
        return dict(snapshot)
    return None


def _render_invalid_terminal_card(card: Any | None = None) -> str:
    lines = [
        "[UnknownCard] <invalid card>",
        "Fallback: unknown card",
        "Action policy: copy_to_clipboard_only",
    ]
    if card is not None:
        card = _canonicalize_terminal_artifact_invalid_preview(card)
        lines.append(f"- raw: {_render_payload_preview(card, max_payload_bytes=256)}")
    return "\n".join(lines)


def _render_invalid_terminal_artifact(artifact: Any) -> str:
    artifact = _canonicalize_terminal_artifact_invalid_preview(artifact)
    return "\n".join(
        [
            "[TerminalArtifact] <invalid artifact>",
            f"TerminalArtifact schema v{TERMINAL_ARTIFACT_SCHEMA_VERSION}",
            f"- raw: {_render_payload_preview(artifact, max_payload_bytes=256)}",
        ]
    )


def _render_terminal_text(value: Any) -> str:
    if value is None:
        return ""
    return _escape_terminal_text(str(value))


def _render_terminal_inline_text(value: Any) -> str:
    rendered = _render_terminal_text(value)
    if not rendered:
        return ""
    return " ".join(rendered.replace("\n", " ").split())


def _is_nonempty_terminal_rendered_text(rendered: Any) -> bool:
    return isinstance(rendered, str) and bool(rendered.strip())


def _escape_terminal_text(value: str) -> str:
    parts: list[str] = []
    for char in value:
        code = ord(char)
        if char == "\n":
            parts.append(char)
        elif code < 32 or code == 127:
            parts.append(f"\\x{code:02x}")
        elif unicodedata.category(char).startswith("C"):
            if code <= 0xFFFF:
                parts.append(f"\\u{code:04x}")
            else:
                parts.append(f"\\U{code:08x}")
        else:
            parts.append(char)
    return "".join(parts)


def _canonicalize_terminal_artifact_invalid_preview(value: Any) -> Any:
    """Return a stable preview snapshot for invalid card/artifact renders.

    Invalid terminal previews should stay deterministic even when the source
    payload contains equivalent action lists in a different order. The
    canonicalization is intentionally limited to the preview path so the
    underlying payload contract remains untouched.
    """

    snapshot = _snapshot_terminal_artifact_value(value)
    if not isinstance(snapshot, Mapping):
        return snapshot
    actions = snapshot.get("actions")
    if not isinstance(actions, list):
        return snapshot
    canonical_snapshot = dict(snapshot)
    canonical_snapshot["actions"] = sorted(actions, key=_canonical_action_snapshot_key)
    return canonical_snapshot
