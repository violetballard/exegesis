from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol

A2UI_VERSION = 1
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"
DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES = 8_192
_RESERVED_CARD_TYPES: tuple[str, ...] = (GENERIC_CARD_TYPE, UNKNOWN_CARD_TYPE)

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
        "a2ui_version": A2UI_VERSION,
        "cards": {
            "generic": GENERIC_CARD_TYPE,
            "unknown": UNKNOWN_CARD_TYPE,
            "reserved": list(_RESERVED_CARD_TYPES),
        },
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
                "payload_fields": sorted(schema),
            }
            for action_id, schema in sorted(_ACTION_SCHEMAS.items())
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

    if card_type in set(capabilities.cards_supported):
        _validate_card_version(card)
        return _materialize_versioned_card(card, capabilities)

    # Safe fallback for unsupported specialized cards.
    return {
        "type": GENERIC_CARD_TYPE,
        "title": f"Fallback view for {card_type or 'Unknown'}",
        "subtitle": "Rendered as GenericCard because client does not support this specialized card.",
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(card_type, fallback_kind="generic"),
        "blocks": [
            {
                "type": "AlertBlock",
                "severity": "info",
                "title": "Card fallback",
                "message": "Rendered as GenericCard because client does not support this specialized card.",
            },
            *_extract_safe_primitive_blocks(card),
            {
                "type": "CodeBlock",
                "language": "json",
                "code": _render_payload_preview(card, max_payload_bytes=capabilities.max_payload_bytes),
            },
        ],
        "actions": _filter_supported_actions(card.get("actions"), supported_actions=set(capabilities.actions_supported)),
    }


def studio_materialize_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    card_type = _normalize_card_type(card)
    if card_type == GENERIC_CARD_TYPE:
        return _materialize_generic_card(card, capabilities)
    if card_type in set(capabilities.cards_supported):
        _validate_card_version(card)
        return _materialize_versioned_card(card, capabilities)
    return build_unknown_card(
        card,
        max_payload_bytes=capabilities.max_payload_bytes,
        supported_actions=capabilities.actions_supported,
    )


def build_unknown_card(
    raw_card: dict[str, Any],
    *,
    max_payload_bytes: int | None = DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES,
    supported_actions: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    type_name = _normalize_card_type(raw_card)
    effective_max_payload_bytes = (
        DEFAULT_UNKNOWN_CARD_PREVIEW_BYTES if max_payload_bytes is None else max_payload_bytes
    )
    rendered_preview = _render_payload_preview(
        raw_card,
        max_payload_bytes=effective_max_payload_bytes,
        pretty=True,
    )
    clipboard_preview = _render_payload_preview(raw_card, max_payload_bytes=effective_max_payload_bytes)
    blocks = _extract_safe_primitive_blocks(raw_card)
    blocks.append(
        {
            "type": "CodeBlock",
            "language": "json",
            "code": rendered_preview,
            "collapsed": True,
        }
    )
    supported_action_set = _canonicalize_supported_actions(supported_actions)
    actions: list[dict[str, Any]] = []
    if "copy_to_clipboard" in supported_action_set:
        copy_action = {
            "id": "copy_to_clipboard",
            "label": "Copy JSON",
            "payload": {"text": clipboard_preview},
        }
        actions.append(copy_action)
    return {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {type_name}",
        "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
        "a2ui_version": A2UI_VERSION,
        "debug": _build_fallback_debug(type_name, fallback_kind="unknown"),
        "blocks": blocks,
        "actions": actions,
    }


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
    if subtitle is not None and (not isinstance(subtitle, str) or not subtitle.strip()):
        raise ValueError("GenericCard subtitle must be a non-empty string when provided")
    blocks = card.get("blocks")
    if strict_actions:
        if not isinstance(blocks, list):
            raise ValueError("GenericCard blocks must be a list")
        for block in blocks:
            validate_primitive_block(block)
    actions = card.get("actions", [])
    if strict_actions:
        if not isinstance(actions, list):
            raise ValueError("GenericCard actions must be a list")
        for action in actions:
            validate_action_ref(action)


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
    title = _normalize_card_title(card)
    card_type = _normalize_card_type(card)
    lines = [f"[{card_type}] {title}"]
    subtitle = card.get("subtitle")
    if isinstance(subtitle, str) and subtitle.strip():
        lines.append(subtitle.strip())
    version = card.get("a2ui_version")
    if type(version) is int:
        lines.append(f"A2UI v{version}")
    rendered_fallback = _render_terminal_fallback_notice(card.get("debug"))
    if not rendered_fallback and card_type == UNKNOWN_CARD_TYPE:
        rendered_fallback = ["Fallback: unknown card"]
    if rendered_fallback:
        lines.extend(rendered_fallback)
    rendered_debug = _render_terminal_debug(card.get("debug"))
    if rendered_debug:
        lines.append("Debug:")
        lines.extend(rendered_debug)
    for block in _iter_card_entries(card.get("blocks")):
        lines.extend(_render_terminal_block(block))
    rendered_actions = _render_terminal_actions(card.get("actions"))
    if rendered_actions:
        lines.append("Actions:")
        lines.extend(rendered_actions)
    return "\n".join(lines)


def _filter_card_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    filtered = _filter_supported_actions(card.get("actions"), supported_actions=set(capabilities.actions_supported))
    out = dict(card)
    out["actions"] = filtered
    return out


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
    return filtered


def _materialize_versioned_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    out = dict(card)
    out["blocks"] = _extract_safe_primitive_blocks(out)
    out = _filter_card_actions(out, capabilities)
    out["a2ui_version"] = A2UI_VERSION
    return out


def _materialize_generic_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_generic_card(card, strict_actions=False)
    out = dict(card)
    out["blocks"] = _extract_safe_primitive_blocks(out)
    out["actions"] = _filter_supported_actions(out.get("actions"), supported_actions=set(capabilities.actions_supported))
    out["a2ui_version"] = A2UI_VERSION
    return out


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


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _render_payload_preview(
    payload: dict[str, Any],
    *,
    max_payload_bytes: int | None,
    pretty: bool = False,
) -> str:
    rendered = json.dumps(
        payload,
        indent=2 if pretty else None,
        sort_keys=True,
        separators=None if pretty else (",", ":"),
        ensure_ascii=True,
    )
    if max_payload_bytes is None or len(rendered.encode("utf-8")) <= max_payload_bytes:
        return rendered
    if max_payload_bytes <= 0:
        return "[payload omitted: max_payload_bytes <= 0]"

    budget = max_payload_bytes
    suffix = f"\n...[truncated to {max_payload_bytes} bytes]" if pretty else f"...[truncated to {max_payload_bytes} bytes]"
    suffix_bytes = len(suffix.encode("utf-8"))
    if suffix_bytes >= budget:
        return suffix[:budget]

    prefix = rendered.encode("utf-8")[: budget - suffix_bytes].decode("utf-8", errors="ignore")
    return f"{prefix}{suffix}"


def _render_terminal_actions(actions: Any) -> list[str]:
    if not isinstance(actions, list):
        return []
    lines: list[str] = []
    seen: set[str] = set()
    for action in actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        action_key = _canonical_json(
            {
                "id": str(action["id"]).strip(),
                "label": str(action["label"]).strip(),
            }
        )
        if action_key in seen:
            continue
        seen.add(action_key)
        label = str(action["label"]).strip()
        action_id = str(action["id"]).strip()
        lines.append(f"- {label} ({action_id})")
    return lines


def _render_terminal_debug(debug: Any) -> list[str]:
    if not isinstance(debug, dict):
        return []
    lines: list[str] = []
    for key in sorted(debug):
        value = debug[key]
        if isinstance(value, bool):
            rendered_value = "true" if value else "false"
        elif isinstance(value, (str, int)):
            rendered_value = str(value)
        else:
            continue
        lines.append(f"- {key}: {rendered_value}")
    return lines


def _render_terminal_fallback_notice(debug: Any) -> list[str]:
    if not isinstance(debug, dict):
        return []
    fallback_kind = debug.get("fallback_kind")
    source_card_type = debug.get("source_card_type")
    if not isinstance(fallback_kind, str) or not fallback_kind.strip():
        return []
    if not isinstance(source_card_type, str) or not source_card_type.strip():
        return []
    return [f"Fallback: {fallback_kind.strip()} from {source_card_type.strip()}"]


def _iter_card_entries(entries: Any) -> list[Any]:
    if not isinstance(entries, list):
        return []
    return entries


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


def _build_fallback_debug(source_card_type: str, *, fallback_kind: str) -> dict[str, str]:
    return {
        "fallback_kind": fallback_kind,
        "source_card_type": source_card_type,
    }


def _extract_safe_primitive_blocks(card: dict[str, Any]) -> list[dict[str, Any]]:
    nested_blocks = card.get("blocks")
    if not isinstance(nested_blocks, list):
        return []

    safe_blocks: list[dict[str, Any]] = []
    for block in nested_blocks:
        sanitized_block = _sanitize_safe_primitive_block(block)
        if sanitized_block is not None:
            safe_blocks.append(sanitized_block)
    return safe_blocks


def _sanitize_safe_primitive_block(block: Any) -> dict[str, Any] | None:
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
            severity = severity_value.strip().upper() or "INFO"
        else:
            severity = "INFO"
        message = _render_terminal_text(block.get("message", ""))
        return [f"{severity}: {message}"]
    if block_type == "CodeBlock":
        return [_render_terminal_text(block.get("code", ""))]
    if block_type == "ProgressBlock":
        title = _render_terminal_text(block.get("title", "progress"))
        status_text = _render_terminal_text(block.get("status_text", ""))
        return [f"{title}: {status_text}"]
    if block_type == "KeyValueBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[KeyValueBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key", "")).strip()
            if not key:
                continue
            value = str(item.get("value", "")).strip() or "<blank>"
            lines.append(f"- {key}: {value}")
        return lines or ["[KeyValueBlock: empty]"]
    if block_type == "ListBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[ListBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if isinstance(item, str):
                rendered_item = item.strip()
                if rendered_item:
                    lines.append(f"- {rendered_item}")
            elif isinstance(item, dict):
                label = str(item.get("label", "")).strip()
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
                    rendered_cells.append(str(cell))
            if rendered_cells:
                lines.append(f"- {' | '.join(rendered_cells)}")
        return lines if len(lines) > 1 else ["[table: empty]"]
    return [f"[unsupported block: {block_type}]"]


def _render_terminal_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)
