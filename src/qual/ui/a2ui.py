from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol

A2UI_VERSION = 1
A2UI_CONTRACT_VERSION = 2
A2UI_ACTION_SCHEMA_VERSION = 1
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"
DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES = 8_192
FALLBACK_COPY_ACTION_ID = "copy_to_clipboard"
GENERIC_FALLBACK_SUBTITLE = "Rendered as GenericCard because client does not support this specialized card."
UNKNOWN_FALLBACK_SUBTITLE = "Read-only fallback view with safe primitive blocks and raw JSON preview."
GENERIC_FALLBACK_TITLE_PREFIX = "Fallback view for "
_RESERVED_CARD_TYPES: tuple[str, ...] = (GENERIC_CARD_TYPE, UNKNOWN_CARD_TYPE)
_SPECIALIZED_CARD_TYPES: tuple[str, ...] = (
    "ProposedEditCard",
    "EvidenceCard",
    "QuestionsCard",
    "RunLogCard",
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


class PolicyGate(Protocol):
    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        ...


class A2UISessionStore:
    def __init__(self) -> None:
        self._by_session: dict[str, A2UICapabilities] = {}

    def register(self, session_id: str, capabilities: A2UICapabilities) -> None:
        validate_capabilities(capabilities)
        self._by_session[session_id] = capabilities

    def get(self, session_id: str) -> A2UICapabilities:
        if session_id not in self._by_session:
            raise KeyError(f"Unknown session: {session_id}")
        return self._by_session[session_id]


def describe_a2ui_contract() -> dict[str, Any]:
    """Return the stable, versioned A2UI contract manifest.

    The manifest is intentionally JSON-serializable so clients can fingerprint
    the contract they negotiated without having to mirror internal module state.
    """

    manifest = _build_a2ui_contract_manifest()
    manifest["contract_fingerprint"] = a2ui_contract_fingerprint()
    return manifest


def _build_a2ui_contract_manifest() -> dict[str, Any]:
    return {
        "contract_version": A2UI_CONTRACT_VERSION,
        "a2ui_version": A2UI_VERSION,
        "cards": {
            "generic": GENERIC_CARD_TYPE,
            "unknown": UNKNOWN_CARD_TYPE,
            "reserved": list(_RESERVED_CARD_TYPES),
            "specialized": list(_SPECIALIZED_CARD_TYPES),
        },
        "fallbacks": {
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
        },
        "schemas": _build_a2ui_schema_manifest(),
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


def _build_a2ui_schema_manifest() -> dict[str, Any]:
    return {
        "cards": [
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
        ],
        "actions": [
            {
                "type": "ActionRef",
                "version": A2UI_ACTION_SCHEMA_VERSION,
                "required_fields": ["id", "label", "payload"],
                "optional_fields": ["confirm", "policy_sensitive"],
                "payload_schemas": [
                    {
                        "id": action_id,
                        "version": A2UI_ACTION_SCHEMA_VERSION,
                        "fields": sorted(schema),
                    }
                    for action_id, schema in sorted(_ACTION_SCHEMAS.items())
                ],
            }
        ],
    }


def a2ui_contract_fingerprint() -> str:
    """Return a stable fingerprint for the current contract manifest."""

    manifest = _build_a2ui_contract_manifest()
    return hashlib.sha256(_canonical_json(manifest).encode("utf-8")).hexdigest()


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


def engine_prepare_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
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


def validate_unknown_card(card: dict[str, Any]) -> None:
    _validate_fallback_card(
        card,
        expected_type=UNKNOWN_CARD_TYPE,
        expected_fallback_kind="unknown",
    )


def studio_materialize_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
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
    raw_card: dict[str, Any],
    *,
    max_payload_bytes: int | None = DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES,
    supported_actions: tuple[str, ...] | None = None,
) -> dict[str, Any]:
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


def validate_generic_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
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
    blocks = card.get("blocks")
    if blocks is not None:
        if not isinstance(blocks, list):
            raise ValueError("GenericCard blocks must be a list when provided")
        for block in blocks:
            validate_primitive_block(block)
    actions = card.get("actions", [])
    if strict_actions:
        if not isinstance(actions, list):
            raise ValueError("GenericCard actions must be a list")
        seen_actions: set[str] = set()
        for action in actions:
            validate_action_ref(action)
            action_key = _canonical_json(action)
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
    if not isinstance(blocks, list):
        raise ValueError("Fallback card blocks must be a list")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions")
    if not isinstance(actions, list):
        raise ValueError("Fallback card actions must be a list")
    _validate_canonical_read_only_fallback_actions(actions)
    debug = card.get("debug")
    if not isinstance(debug, dict):
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
    if not isinstance(block, dict):
        raise ValueError("Primitive block must be an object")
    block_type = str(block.get("type", ""))
    if block_type not in _PRIMITIVE_BLOCK_SET:
        raise ValueError(f"Unsupported primitive block: {block_type}")
    _validate_primitive_block_fields(block_type, block)


def validate_action_ref(action: Any) -> None:
    _normalize_action(action, supported_actions=_ALLOWED_ACTION_SET)


def normalize_action_ref(action: ActionRef) -> ActionRef:
    action_dict: dict[str, Any] = {
        "id": action.id,
        "label": action.label,
        "payload": action.payload,
    }
    if action.confirm is not None:
        action_dict["confirm"] = action.confirm
    if action.policy_sensitive:
        action_dict["policy_sensitive"] = action.policy_sensitive
    normalized = _normalize_action(action_dict, supported_actions=_ALLOWED_ACTION_SET)
    return ActionRef(
        id=str(normalized["id"]),
        label=str(normalized["label"]),
        payload=dict(normalized["payload"]),
        confirm=dict(normalized["confirm"]) if "confirm" in normalized else None,
        policy_sensitive=bool(normalized.get("policy_sensitive", False)),
    )


def execute_action_with_policy_gate(
    *,
    action: ActionRef,
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


def render_terminal_card(card: dict[str, Any]) -> str:
    raw_title = _normalize_card_title(card)
    title = _render_terminal_inline_text(raw_title)
    card_type = _normalize_card_type(card)
    rendered_card_type = _render_terminal_inline_text(card_type)
    generic_fallback_source = _infer_generic_fallback_source(raw_title)
    lines = [f"[{rendered_card_type}] {title}"]
    subtitle = card.get("subtitle")
    if card_type == UNKNOWN_CARD_TYPE:
        lines.append(UNKNOWN_FALLBACK_SUBTITLE)
    elif card_type == GENERIC_CARD_TYPE and (
        _is_fallback_card_debug(card.get("debug")) or generic_fallback_source is not None
    ):
        lines.append(GENERIC_FALLBACK_SUBTITLE)
    elif isinstance(subtitle, str) and subtitle.strip():
        lines.append(_render_terminal_inline_text(subtitle.strip()))
    version = card.get("a2ui_version")
    if type(version) is int:
        lines.append(f"A2UI v{version}")
    rendered_fallback = _render_terminal_fallback_notice(
        card_type,
        title,
        debug=card.get("debug"),
    )
    if rendered_fallback:
        lines.extend(rendered_fallback)
    rendered_policy = _render_terminal_action_policy(
        card_type,
        title,
        debug=card.get("debug"),
    )
    if rendered_policy:
        lines.extend(rendered_policy)
    debug = card.get("debug")
    rendered_debug = _render_terminal_fallback_debug(card_type, title, debug)
    if not rendered_debug:
        rendered_debug = _render_terminal_debug(debug)
    if rendered_debug:
        lines.append("Debug:")
        lines.extend(rendered_debug)
    for block in _iter_card_entries(card.get("blocks")):
        lines.extend(_render_terminal_block(block))
    actions = card.get("actions")
    rendered_actions = _render_terminal_actions(
        actions,
        supported_actions={FALLBACK_COPY_ACTION_ID} if card_type == UNKNOWN_CARD_TYPE else _ALLOWED_ACTION_SET,
    )
    actions_present = actions is not None
    actions_are_list = isinstance(actions, (list, tuple))
    filtered_actions = actions_are_list and len(rendered_actions) < len(actions)
    if rendered_actions:
        lines.append("Actions:")
        lines.extend(rendered_actions)
        if filtered_actions:
            lines.append("Some actions filtered out by allowlist or validation")
    elif actions_present:
        lines.append("Actions: none available")
        if actions_are_list and actions:
            lines.append("Actions filtered out by allowlist or validation")
        elif not actions_are_list:
            lines.append("Actions filtered out by allowlist or validation")
    return "\n".join(lines)


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
    if not isinstance(actions, list):
        return []
    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in actions:
        try:
            normalized = _normalize_action(action, supported_actions=supported_actions)
        except ValueError:
            continue
        action_key = _canonical_json(normalized)
        if action_key in seen:
            continue
        seen.add(action_key)
        filtered.append(normalized)
    # Keep the materialized payload deterministic even when the model emits
    # supported actions in a different order.
    return sorted(filtered, key=_canonical_json)


def _validate_canonical_read_only_fallback_actions(actions: list[Any]) -> None:
    seen_actions: set[str] = set()
    for action in actions:
        validate_action_ref(action)
        if not isinstance(action, dict):
            raise ValueError("Fallback card actions must be copy_to_clipboard only")
        if action.get("id") != FALLBACK_COPY_ACTION_ID:
            raise ValueError("Fallback card actions must be copy_to_clipboard only")
        if action.get("label") != "Copy JSON":
            raise ValueError("Fallback card actions must use the canonical Copy JSON label")
        if "confirm" in action:
            raise ValueError("Fallback card actions must not require confirmation")
        if action.get("policy_sensitive") is True:
            raise ValueError("Fallback card actions must not be policy-sensitive")
        payload = action.get("payload")
        if not isinstance(payload, dict) or set(payload) != {"text"}:
            raise ValueError("Fallback card actions must use the canonical clipboard payload")
        if not isinstance(payload.get("text"), str):
            raise ValueError("Fallback card actions must use a string clipboard payload")
        action_key = _canonical_json(action)
        if action_key in seen_actions:
            raise ValueError("Fallback card actions must not contain duplicates")
        seen_actions.add(action_key)


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
    validate_generic_card(card, strict_actions=False)
    out = _canonicalize_card_top_level_fields(card)
    out["blocks"] = _extract_safe_primitive_blocks(out)
    actions = out.get("actions")
    if actions is None:
        out["actions"] = []
    elif not isinstance(actions, list):
        raise ValueError("GenericCard actions must be a list when provided")
    else:
        out["actions"] = _filter_supported_actions(actions, supported_actions=set(capabilities.actions_supported))
    out["title"] = _normalize_card_text(out.get("title"), fallback="<untitled>")
    subtitle = _normalize_card_text(out.get("subtitle"))
    if subtitle is None:
        out.pop("subtitle", None)
    else:
        out["subtitle"] = subtitle
    out["a2ui_version"] = A2UI_VERSION
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


def _normalize_action(action: Any, *, supported_actions: set[str]) -> dict[str, Any]:
    if not isinstance(action, dict):
        raise ValueError("ActionRef must be an object")
    extra_keys = set(action) - {"id", "label", "payload", "confirm", "policy_sensitive"}
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected action field(s): {extras}")
    action_id = str(action.get("id", "")).strip()
    if action_id not in supported_actions:
        raise ValueError(f"Unsupported action id: {action_id}")
    label = action.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Action label is required")
    payload = action.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Action payload must be an object")
    _validate_action_payload(action_id, payload)

    normalized: dict[str, Any] = {
        "id": action_id,
        "label": label.strip(),
        "payload": dict(payload),
    }
    confirm = action.get("confirm")
    if confirm is not None:
        normalized["confirm"] = _normalize_confirm(confirm)
    policy_sensitive = action.get("policy_sensitive", False)
    if not isinstance(policy_sensitive, bool):
        raise ValueError("Action policy_sensitive must be a bool")
    if policy_sensitive:
        normalized["policy_sensitive"] = True
    return normalized


def _normalize_confirm(confirm: Any) -> dict[str, str]:
    if not isinstance(confirm, dict):
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


def _validate_action_payload(action_id: str, payload: dict[str, Any]) -> None:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"No schema for action id: {action_id}")
    extra_keys = set(payload) - set(schema)
    if extra_keys:
        extras = ", ".join(sorted(extra_keys))
        raise ValueError(f"Unexpected payload field for {action_id}: {extras}")
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field for {action_id}: {key}")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Invalid payload type for {action_id}:{key}")


def _validate_primitive_block_fields(block_type: str, block: dict[str, Any]) -> None:
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
    return {key: card[key] for key in allowed_keys if key in card}


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
    return _normalize_action(
        {
            "id": FALLBACK_COPY_ACTION_ID,
            "label": "Copy JSON",
            "payload": {"text": text},
        },
        supported_actions={FALLBACK_COPY_ACTION_ID},
    )


def _sanitize_json_preview_value(value: Any, *, _seen_ids: set[int] | None = None) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if _seen_ids is None:
        _seen_ids = set()

    value_id = id(value)
    if value_id in _seen_ids:
        return f"<cycle:{type(value).__name__}>"

    if isinstance(value, dict):
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

    if isinstance(value, set):
        _seen_ids.add(value_id)
        try:
            sanitized_items = [_sanitize_json_preview_value(item, _seen_ids=_seen_ids) for item in value]
            return sorted(sanitized_items, key=_canonical_json_sort_key)
        finally:
            _seen_ids.remove(value_id)

    return f"<non-json:{type(value).__name__}>"


def _canonical_json_sort_key(value: Any) -> str:
    if isinstance(value, dict):
        return _canonical_json({str(key): value[key] for key in sorted(value, key=lambda item: str(item))})
    if isinstance(value, list):
        return _canonical_json({"items": value})
    return str(value)


def _render_terminal_actions(actions: Any, *, supported_actions: set[str]) -> list[str]:
    normalized_actions = _canonicalize_supported_action_list(actions, supported_actions=supported_actions)
    normalized_actions = sorted(normalized_actions, key=_canonical_json)

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
    if isinstance(confirm, dict):
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
    if not isinstance(debug, dict):
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


def _render_terminal_fallback_debug(card_type: str, title: str, debug: Any) -> list[str]:
    fallback_debug = _extract_terminal_fallback_debug(debug)
    if fallback_debug is None:
        if card_type == UNKNOWN_CARD_TYPE:
            source_card_type = _infer_unknown_fallback_source(title)
            fallback_kind = "unknown"
        elif card_type == GENERIC_CARD_TYPE:
            source_card_type = _infer_generic_fallback_source(title)
            fallback_kind = "generic"
        else:
            return []
        if source_card_type is None:
            return []
    else:
        fallback_kind, source_card_type = fallback_debug

    lines: list[str] = []
    if isinstance(debug, dict):
        contract_version = debug.get("contract_version")
        if type(contract_version) is int:
            lines.append(f"- contract_version: {contract_version}")
    lines.append(f"- fallback_kind: {_render_terminal_inline_text(fallback_kind)}")
    lines.append(f"- source_card_type: {_render_terminal_inline_text(source_card_type)}")
    return lines


def _render_terminal_fallback_notice(card_type: str, title: str, *, debug: Any) -> list[str]:
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
        source_card_type = _infer_generic_fallback_source(title)
        if source_card_type is not None:
            return [f"Fallback: generic from {_render_terminal_inline_text(source_card_type)}"]
        return ["Fallback: generic card"]
    return []


def _extract_terminal_fallback_debug(debug: Any) -> tuple[str, str] | None:
    if not isinstance(debug, dict):
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


def _render_terminal_action_policy(card_type: str, title: str, debug: Any) -> list[str]:
    if card_type == UNKNOWN_CARD_TYPE:
        return ["Action policy: copy_to_clipboard_only"]
    if card_type == GENERIC_CARD_TYPE and (
        _is_fallback_card_debug(debug) or _infer_generic_fallback_source(title) is not None
    ):
        return ["Action policy: client_allowlist"]
    return []


def _is_fallback_card_debug(debug: Any) -> bool:
    if not isinstance(debug, dict):
        return False
    fallback_kind = debug.get("fallback_kind")
    source_card_type = debug.get("source_card_type")
    return isinstance(fallback_kind, str) and fallback_kind.strip() in {"generic", "unknown"} and isinstance(
        source_card_type, str
    )


def _infer_generic_fallback_source(title: str) -> str | None:
    if not title.startswith(GENERIC_FALLBACK_TITLE_PREFIX):
        return None
    source_card_type = title[len(GENERIC_FALLBACK_TITLE_PREFIX) :].strip()
    return source_card_type or None


def _infer_unknown_fallback_source(title: str) -> str | None:
    prefix = "Unsupported card type: "
    if not title.startswith(prefix):
        return None
    source_card_type = title[len(prefix) :].strip()
    return source_card_type or None


def _iter_card_entries(entries: Any) -> list[Any]:
    if not isinstance(entries, (list, tuple)):
        return []
    return list(entries)


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
    if isinstance(debug, dict):
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
        return f"Unsupported card type: {source_card_type}"
    raise ValueError(f"Unsupported fallback card type: {expected_type}")


def _fallback_subtitle(fallback_kind: str) -> str:
    if fallback_kind == "generic":
        return GENERIC_FALLBACK_SUBTITLE
    if fallback_kind == "unknown":
        return UNKNOWN_FALLBACK_SUBTITLE
    raise ValueError(f"Unsupported fallback kind: {fallback_kind}")


def _extract_safe_primitive_blocks(card: dict[str, Any], *, allow_code_block: bool = True) -> list[dict[str, Any]]:
    nested_blocks = card.get("blocks")
    if not isinstance(nested_blocks, (list, tuple)):
        return []

    safe_blocks: list[dict[str, Any]] = []
    for block in nested_blocks:
        sanitized_block = _sanitize_safe_primitive_block(block, allow_code_block=allow_code_block)
        if sanitized_block is not None:
            safe_blocks.append(sanitized_block)
    return safe_blocks


def _sanitize_safe_primitive_block(block: Any, *, allow_code_block: bool = True) -> dict[str, Any] | None:
    if not isinstance(block, dict):
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
            "severity": str(block.get("severity", "info")).strip() or "info",
            "message": message,
        }
        title = block.get("title")
        if title is not None:
            if not isinstance(title, str):
                return None
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
            if not isinstance(item, dict):
                continue
            key = item.get("key")
            if not isinstance(key, str) or not key.strip():
                continue
            value = item.get("value")
            if isinstance(value, (dict, list)):
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
            elif isinstance(item, dict):
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
    if not isinstance(actions, (list, tuple)):
        return []

    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in actions:
        try:
            normalized = _normalize_action(action, supported_actions=supported_actions)
        except ValueError:
            continue
        action_key = _canonical_json(normalized)
        if action_key in seen:
            continue
        seen.add(action_key)
        filtered.append(normalized)
    return filtered


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
    if not isinstance(block, dict):
        return ["[unsupported block: malformed]"]
    block_type = str(block.get("type", "")).strip()
    if not block_type:
        return ["[unsupported block: missing type]"]
    if block_type == "MarkdownBlock":
        return [_render_terminal_text(block.get("markdown", ""))]
    if block_type == "AlertBlock":
        severity_value = block.get("severity", "info")
        if isinstance(severity_value, str):
            severity = _render_terminal_inline_text(severity_value.strip()).upper() or "INFO"
        else:
            severity = "INFO"
        message = _render_terminal_inline_text(block.get("message", ""))
        return [f"{severity}: {message}"]
    if block_type == "CodeBlock":
        return [_render_terminal_text(block.get("code", ""))]
    if block_type == "ProgressBlock":
        title = _render_terminal_inline_text(block.get("title", "progress"))
        status_text = _render_terminal_inline_text(block.get("status_text", ""))
        return [f"{title}: {status_text}"]
    if block_type == "KeyValueBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[KeyValueBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            key = _render_terminal_inline_text(item.get("key", ""))
            if not key:
                continue
            value = _render_terminal_inline_text(item.get("value", "")) or "<blank>"
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
            elif isinstance(item, dict):
                label = _render_terminal_inline_text(item.get("label", ""))
                if label:
                    lines.append(f"- {label}")
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
                else:
                    rendered_cells.append(_render_terminal_inline_text(cell))
            if rendered_cells:
                lines.append(f"- {' | '.join(rendered_cells)}")
        return lines if len(lines) > 1 else ["[table: empty]"]
    return [f"[unsupported block: {_render_terminal_inline_text(block_type)}]"]


def _render_terminal_text(value: Any) -> str:
    if value is None:
        return ""
    return _escape_terminal_text(str(value))


def _render_terminal_inline_text(value: Any) -> str:
    rendered = _render_terminal_text(value)
    if not rendered:
        return ""
    return " ".join(rendered.replace("\n", " ").split())


def _escape_terminal_text(value: str) -> str:
    parts: list[str] = []
    for char in value:
        code = ord(char)
        if char == "\n":
            parts.append(char)
        elif code < 32 or code == 127:
            parts.append(f"\\x{code:02x}")
        else:
            parts.append(char)
    return "".join(parts)
