from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Protocol

A2UI_VERSION = 1
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"

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


def validate_capabilities(capabilities: A2UICapabilities) -> None:
    if capabilities.a2ui_version != A2UI_VERSION:
        raise ValueError("Unsupported a2ui version")
    if not capabilities.client_name.strip():
        raise ValueError("client_name is required")
    if capabilities.max_payload_bytes <= 0:
        raise ValueError("max_payload_bytes must be positive")
    if not _PRIMITIVE_BLOCK_SET.issubset(set(capabilities.primitive_blocks_supported)):
        raise ValueError("Missing required primitive block support")
    for action_id in capabilities.actions_supported:
        if action_id not in _ALLOWED_ACTION_SET:
            raise ValueError(f"Unknown action in capabilities: {action_id}")


def engine_prepare_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card, strict_actions=False)
        return _filter_card_actions(card, capabilities)

    if card_type in set(capabilities.cards_supported):
        return _filter_card_actions(card, capabilities)

    # Safe fallback for unsupported specialized cards.
    return {
        "type": GENERIC_CARD_TYPE,
        "title": f"Fallback view for {card_type or 'Unknown'}",
        "subtitle": "Rendered as GenericCard because client does not support this specialized card.",
        "a2ui_version": A2UI_VERSION,
        "blocks": [
            {
                "type": "AlertBlock",
                "severity": "info",
                "title": "Card fallback",
                "message": "Rendered as GenericCard because client does not support this specialized card.",
            },
            {
                "type": "CodeBlock",
                "language": "json",
                "code": _render_payload_preview(card, max_payload_bytes=capabilities.max_payload_bytes),
            },
        ],
        "actions": [],
    }


def studio_materialize_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card, strict_actions=False)
        return _filter_card_actions(card, capabilities)
    if card_type in set(capabilities.cards_supported):
        return _filter_card_actions(card, capabilities)
    return build_unknown_card(card, max_payload_bytes=capabilities.max_payload_bytes)


def build_unknown_card(
    raw_card: dict[str, Any],
    *,
    max_payload_bytes: int | None = None,
) -> dict[str, Any]:
    type_name = str(raw_card.get("type", "<missing>"))
    nested_blocks = raw_card.get("blocks")
    blocks: list[dict[str, Any]] = []
    if isinstance(nested_blocks, list):
        for block in nested_blocks:
            if isinstance(block, dict) and str(block.get("type", "")) in _PRIMITIVE_BLOCK_SET:
                blocks.append(block)
    blocks.append(
        {
            "type": "CodeBlock",
            "language": "json",
            "code": _render_payload_preview(raw_card, max_payload_bytes=max_payload_bytes, pretty=True),
            "collapsed": True,
        }
    )
    return {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {type_name}",
        "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
        "a2ui_version": A2UI_VERSION,
        "blocks": blocks,
        "actions": [
            {
                "id": "copy_to_clipboard",
                "label": "Copy JSON",
                "payload": {"text": _render_payload_preview(raw_card, max_payload_bytes=None)},
            }
        ],
    }


def validate_generic_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    if card.get("type") != GENERIC_CARD_TYPE:
        raise ValueError("Card type must be GenericCard")
    version = card.get("a2ui_version")
    if version is not None:
        if not isinstance(version, int):
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
    if not isinstance(blocks, list):
        raise ValueError("GenericCard blocks must be a list")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError("GenericCard actions must be a list")
    if strict_actions:
        for action in actions:
            validate_action_ref(action)


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
    title = str(card.get("title", "<untitled>"))
    card_type = str(card.get("type", "Card"))
    lines = [f"[{card_type}] {title}"]
    subtitle = card.get("subtitle")
    if isinstance(subtitle, str) and subtitle.strip():
        lines.append(subtitle.strip())
    version = card.get("a2ui_version")
    if isinstance(version, int):
        lines.append(f"A2UI v{version}")
    for block in card.get("blocks", []):
        lines.extend(_render_terminal_block(block))
    rendered_actions = _render_terminal_actions(card.get("actions"))
    if rendered_actions:
        lines.append("Actions:")
        lines.extend(rendered_actions)
    return "\n".join(lines)


def _filter_card_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    actions = card.get("actions")
    if not isinstance(actions, list):
        return card
    supported = set(capabilities.actions_supported)
    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in actions:
        try:
            normalized = _normalize_action(action, supported_actions=supported)
        except ValueError:
            continue
        action_key = _canonical_json(normalized)
        if action_key in seen:
            continue
        seen.add(action_key)
        filtered.append(normalized)
    out = dict(card)
    out["actions"] = filtered
    return out


def _normalize_action(action: Any, *, supported_actions: set[str]) -> dict[str, Any]:
    if not isinstance(action, dict):
        raise ValueError("ActionRef must be an object")
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
    for action in actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        label = str(action["label"]).strip()
        action_id = str(action["id"]).strip()
        lines.append(f"- {label} ({action_id})")
    return lines


def _render_terminal_block(block: Any) -> list[str]:
    if not isinstance(block, dict):
        return ["[unsupported block: malformed]"]
    block_type = str(block.get("type", "")).strip()
    if not block_type:
        return ["[unsupported block: missing type]"]
    if block_type == "MarkdownBlock":
        return [str(block.get("markdown", ""))]
    if block_type == "AlertBlock":
        return [f"{block.get('severity', 'info').upper()}: {block.get('message', '')}"]
    if block_type == "CodeBlock":
        return [str(block.get("code", ""))]
    if block_type == "ProgressBlock":
        return [f"{block.get('title', 'progress')}: {block.get('status_text', '')}"]
    if block_type == "KeyValueBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[KeyValueBlock: invalid items]"]
        return [
            f"- {item.get('key', '')}: {item.get('value', '')}"
            for item in items
            if isinstance(item, dict)
        ] or ["[KeyValueBlock: empty]"]
    if block_type == "ListBlock":
        items = block.get("items", [])
        if not isinstance(items, list):
            return ["[ListBlock: invalid items]"]
        lines: list[str] = []
        for item in items:
            if isinstance(item, str):
                lines.append(f"- {item}")
            elif isinstance(item, dict):
                lines.append(f"- {item.get('label', '')}")
        return lines or ["[ListBlock: empty]"]
    if block_type == "TableBlock":
        return ["[table]"]
    return [f"[unsupported block: {block_type}]"]
