from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from exegesis_shared.contracts.actions import (
    ALLOWED_ACTION_IDS,
    validate_complete_patch_review_capabilities,
    materialize_card_actions,
    materialize_cli_fallback_card,
    validate_action_ref,
)

A2UI_VERSION = 1
GENERIC_CARD_TYPE = "GenericCard"
UNKNOWN_CARD_TYPE = "UnknownCard"
PROPOSED_EDIT_CARD_TYPE = "ProposedEditCard"
RETRIEVAL_RESULTS_CARD_TYPE = "RetrievalResultsCard"
BASKET_CARD_TYPE = "BasketCard"
CONTEXT_SET_CARD_TYPE = "ContextSetCard"
KNOWN_CARD_TYPES: tuple[str, ...] = (
    GENERIC_CARD_TYPE,
    PROPOSED_EDIT_CARD_TYPE,
    RETRIEVAL_RESULTS_CARD_TYPE,
    BASKET_CARD_TYPE,
    CONTEXT_SET_CARD_TYPE,
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
_PRIMITIVE_BLOCK_REQUIRED_FIELDS: dict[str, dict[str, type | tuple[type, ...]]] = {
    "MarkdownBlock": {"markdown": str},
    "KeyValueBlock": {"items": list},
    "ListBlock": {"items": list},
    "TableBlock": {"columns": list, "rows": list},
    "AlertBlock": {"message": str},
    "ProgressBlock": {"title": str, "status_text": str},
    "CodeBlock": {"language": str, "code": str},
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


class A2UISessionStore:
    def __init__(self) -> None:
        self._by_session: dict[str, A2UICapabilities] = {}

    def register(self, session_id: str, capabilities: A2UICapabilities) -> None:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id is required")
        validate_capabilities(capabilities)
        self._by_session[session_id] = capabilities

    def get(self, session_id: str) -> A2UICapabilities:
        if session_id not in self._by_session:
            raise KeyError(f"Unknown session: {session_id}")
        return self._by_session[session_id]


def validate_capabilities(capabilities: A2UICapabilities) -> None:
    if not isinstance(capabilities.a2ui_version, int) or isinstance(capabilities.a2ui_version, bool):
        raise ValueError("a2ui_version must be a positive integer")
    if capabilities.a2ui_version < 1:
        raise ValueError("Unsupported a2ui version")
    if not isinstance(capabilities.client_name, str) or not capabilities.client_name.strip():
        raise ValueError("client_name is required")
    if not isinstance(capabilities.max_payload_bytes, int) or isinstance(capabilities.max_payload_bytes, bool):
        raise ValueError("max_payload_bytes must be a positive integer")
    if capabilities.max_payload_bytes <= 0:
        raise ValueError("max_payload_bytes must be positive")
    _validate_capability_names(capabilities.cards_supported, "cards_supported")
    _validate_capability_names(capabilities.primitive_blocks_supported, "primitive_blocks_supported")
    _validate_capability_names(capabilities.actions_supported, "actions_supported")
    if not isinstance(capabilities.supports_streaming, bool):
        raise ValueError("supports_streaming must be a boolean")
    if not _PRIMITIVE_BLOCK_SET.issubset(set(capabilities.primitive_blocks_supported)):
        raise ValueError("Missing required primitive block support")
    for action_id in capabilities.actions_supported:
        if action_id not in _ALLOWED_ACTION_SET:
            raise ValueError(f"Unknown action in capabilities: {action_id}")


def validate_complete_patch_review_card_capabilities(capabilities: A2UICapabilities) -> None:
    validate_capabilities(capabilities)
    if PROPOSED_EDIT_CARD_TYPE not in set(capabilities.cards_supported):
        raise ValueError("Complete patch review requires ProposedEditCard support")
    validate_complete_patch_review_capabilities(capabilities)


def _validate_capability_names(values: Any, field_name: str) -> None:
    if not isinstance(values, tuple):
        raise ValueError(f"{field_name} must be a tuple")
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")


def engine_prepare_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card)
        prepared = _engine_filter_actions(card, capabilities)
        prepared = materialize_cli_fallback_card(prepared)
        validate_card_payload_size(prepared, capabilities)
        return prepared
    if card_type == PROPOSED_EDIT_CARD_TYPE:
        prepared = materialize_proposed_edit_card(card)
        if card_type in set(capabilities.cards_supported):
            prepared = _engine_filter_actions(prepared, capabilities)
            prepared = materialize_cli_fallback_card(prepared)
            validate_card_payload_size(prepared, capabilities)
            return prepared
        card = prepared
    elif card_type in _VALIDATORS_BY_CARD_TYPE:
        validate_known_card(card)
    fallback_actions = _engine_fallback_actions(card, capabilities)
    fallback = {
        "type": GENERIC_CARD_TYPE,
        "title": f"Fallback view for {card_type or 'Unknown'}",
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
                "code": json.dumps(card, separators=(",", ":"), ensure_ascii=True),
            },
        ],
        "actions": fallback_actions,
    }
    patch_id = card.get("patch_id")
    if isinstance(patch_id, str) and patch_id.strip():
        fallback["patch_id"] = patch_id.strip()
    fallback = materialize_cli_fallback_card(fallback)
    validate_card_payload_size(fallback, capabilities)
    return fallback


def studio_materialize_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    validate_capabilities(capabilities)
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card, strict_actions=False)
        materialized = materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
        validate_card_payload_size(materialized, capabilities)
        return materialized
    if card_type == PROPOSED_EDIT_CARD_TYPE:
        card = materialize_proposed_edit_card(card)
        materialized = materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
        validate_card_payload_size(materialized, capabilities)
        return materialized
    if card_type in _VALIDATORS_BY_CARD_TYPE:
        validate_known_card(card, strict_actions=False)
        materialized = materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
        validate_card_payload_size(materialized, capabilities)
        return materialized
    materialized = materialize_cli_fallback_card(_studio_filter_actions(build_unknown_card(card), capabilities))
    validate_card_payload_size(materialized, capabilities)
    return materialized


def validate_card_payload_size(card: dict[str, Any], capabilities: A2UICapabilities) -> None:
    validate_capabilities(capabilities)
    encoded = json.dumps(card, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    if len(encoded) > capabilities.max_payload_bytes:
        raise ValueError(
            "A2UI card payload exceeds negotiated max_payload_bytes "
            f"({len(encoded)} > {capabilities.max_payload_bytes})"
        )


def build_unknown_card(raw_card: dict[str, Any]) -> dict[str, Any]:
    type_name = str(raw_card.get("type", "<missing>"))
    nested_blocks = raw_card.get("blocks")
    blocks: list[dict[str, Any]] = []
    if isinstance(nested_blocks, list):
        for block in nested_blocks:
            try:
                validate_primitive_block(block)
            except ValueError:
                continue
            blocks.append(block)
    blocks.append(
        {
            "type": "CodeBlock",
            "language": "json",
            "code": json.dumps(raw_card, indent=2, sort_keys=True, ensure_ascii=True),
            "collapsed": True,
        }
    )
    actions = materialize_card_actions(raw_card)
    actions.append({"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": json.dumps(raw_card)}})
    fallback = {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {type_name}",
        "blocks": blocks,
        "actions": actions,
    }
    patch_id = raw_card.get("patch_id")
    if isinstance(patch_id, str) and patch_id.strip():
        fallback["patch_id"] = patch_id.strip()
    return fallback


def validate_generic_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    if card.get("type") != GENERIC_CARD_TYPE:
        raise ValueError("Card type must be GenericCard")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("GenericCard title is required")
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


def materialize_proposed_edit_card(card: dict[str, Any]) -> dict[str, Any]:
    validate_proposed_edit_card(card, strict_actions=False)
    materialized = dict(card)
    patch_id = str(materialized["patch_id"]).strip()
    materialized["patch_id"] = patch_id
    actions = [
        action
        for action in materialize_card_actions(materialized)
        if not _is_same_patch_review_action(action, patch_id)
    ]
    actions.extend(_canonical_patch_review_actions(patch_id))
    materialized["actions"] = actions
    validate_proposed_edit_card(materialized)
    return materialized


def validate_proposed_edit_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    if card.get("type") != PROPOSED_EDIT_CARD_TYPE:
        raise ValueError("Card type must be ProposedEditCard")
    patch_id = card.get("patch_id")
    if not isinstance(patch_id, str) or not patch_id.strip():
        raise ValueError("ProposedEditCard patch_id is required")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("ProposedEditCard title is required")
    blocks = card.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("ProposedEditCard blocks must be a list")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError("ProposedEditCard actions must be a list")
    expected_patch_id = patch_id.strip()
    for action in actions:
        if not isinstance(action, dict):
            if strict_actions:
                validate_action_ref(action)
            continue
        action_id = action.get("id")
        if action_id in {"preview_patch", "apply_patch", "reject_patch"}:
            payload = action.get("payload")
            action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
            if action_patch_id != expected_patch_id:
                raise ValueError(f"{action_id} payload patch_id must match ProposedEditCard patch_id")
        if strict_actions:
            validate_action_ref(action)


def validate_known_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    card_type = str(card.get("type", "")).strip()
    validator = _VALIDATORS_BY_CARD_TYPE.get(card_type)
    if validator is None:
        raise ValueError(f"Unsupported known A2UI card type: {card_type}")
    validator(card, strict_actions=strict_actions)


def validate_retrieval_results_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_title(card, RETRIEVAL_RESULTS_CARD_TYPE)
    query = card.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("RetrievalResultsCard query is required")
    results = card.get("results")
    if not isinstance(results, list):
        raise ValueError("RetrievalResultsCard results must be a list")
    for result in results:
        _validate_typed_mapping(
            result,
            "RetrievalResultsCard result",
            required_fields={"item_id": str, "title": str, "snippet": str},
        )
    _validate_optional_card_actions(card, strict_actions=strict_actions)
    _validate_item_scoped_actions(card, results, "RetrievalResultsCard result")


def validate_basket_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_title(card, BASKET_CARD_TYPE)
    items = card.get("items")
    if not isinstance(items, list):
        raise ValueError("BasketCard items must be a list")
    for item in items:
        _validate_typed_mapping(
            item,
            "BasketCard item",
            required_fields={"item_id": str, "title": str},
        )
    _validate_optional_card_actions(card, strict_actions=strict_actions)
    _validate_item_scoped_actions(card, items, "BasketCard item")


def validate_context_set_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_title(card, CONTEXT_SET_CARD_TYPE)
    context_set_id = card.get("context_set_id")
    if not isinstance(context_set_id, str) or not context_set_id.strip():
        raise ValueError("ContextSetCard context_set_id is required")
    items = card.get("items")
    if not isinstance(items, list):
        raise ValueError("ContextSetCard items must be a list")
    for item in items:
        _validate_typed_mapping(
            item,
            "ContextSetCard item",
            required_fields={"item_id": str, "title": str},
        )
    _validate_optional_card_actions(card, strict_actions=strict_actions)
    _validate_item_scoped_actions(card, items, "ContextSetCard item")


def validate_primitive_block(block: Any) -> None:
    if not isinstance(block, dict):
        raise ValueError("Primitive block must be an object")
    block_type = str(block.get("type", ""))
    if block_type not in _PRIMITIVE_BLOCK_SET:
        raise ValueError(f"Unsupported primitive block: {block_type}")
    required_fields = _PRIMITIVE_BLOCK_REQUIRED_FIELDS[block_type]
    for field_name, field_type in required_fields.items():
        if field_name not in block:
            raise ValueError(f"{block_type} requires '{field_name}'")
        value = block[field_name]
        if not isinstance(value, field_type):
            if isinstance(field_type, tuple):
                type_names = " or ".join(value_type.__name__ for value_type in field_type)
            else:
                type_names = field_type.__name__
            raise ValueError(f"{block_type} field '{field_name}' must be {type_names}")
        if field_type is str and not value.strip():
            raise ValueError(f"{block_type} field '{field_name}' is required")


def _validate_card_title(card: dict[str, Any], card_type: str) -> None:
    if card.get("type") != card_type:
        raise ValueError(f"Card type must be {card_type}")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"{card_type} title is required")


def _validate_typed_mapping(
    value: Any,
    label: str,
    *,
    required_fields: dict[str, type],
) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    for field_name, field_type in required_fields.items():
        field_value = value.get(field_name)
        if not isinstance(field_value, field_type):
            raise ValueError(f"{label} field '{field_name}' must be {field_type.__name__}")
        if field_type is str and not field_value.strip():
            raise ValueError(f"{label} field '{field_name}' is required")


def _validate_optional_card_actions(card: dict[str, Any], *, strict_actions: bool) -> None:
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError(f"{card.get('type')} actions must be a list")
    if strict_actions:
        for action in actions:
            validate_action_ref(action)


def _validate_item_scoped_actions(card: dict[str, Any], items: list[Any], item_label: str) -> None:
    known_item_ids = {
        item["item_id"].strip()
        for item in items
        if isinstance(item, dict) and isinstance(item.get("item_id"), str) and item["item_id"].strip()
    }
    for action in card.get("actions", []):
        if not isinstance(action, dict):
            continue
        action_id = action.get("id")
        if action_id not in {"open_corpus_item", "promote_to_basket", "pin_to_context_set"}:
            continue
        payload = action.get("payload")
        item_id = payload.get("item_id") if isinstance(payload, dict) else None
        if not isinstance(item_id, str) or not item_id.strip():
            continue
        if item_id.strip() not in known_item_ids:
            raise ValueError(f"{action_id} item_id must reference a {item_label}")


def _is_same_patch_review_action(action: dict[str, Any], patch_id: str) -> bool:
    if action.get("id") not in {"preview_patch", "apply_patch", "reject_patch"}:
        return False
    payload = action.get("payload")
    return isinstance(payload, dict) and payload.get("patch_id") == patch_id


def _canonical_patch_review_actions(patch_id: str) -> list[dict[str, Any]]:
    return [
        {"id": "preview_patch", "label": "Preview patch", "payload": {"patch_id": patch_id}},
        {
            "id": "apply_patch",
            "label": "Apply patch",
            "payload": {"patch_id": patch_id},
            "confirm": {"title": "Apply patch?"},
            "policy_sensitive": True,
        },
        {
            "id": "reject_patch",
            "label": "Reject patch",
            "payload": {"patch_id": patch_id},
            "confirm": {"title": "Reject patch?"},
            "policy_sensitive": True,
        },
    ]


_VALIDATORS_BY_CARD_TYPE = {
    GENERIC_CARD_TYPE: validate_generic_card,
    PROPOSED_EDIT_CARD_TYPE: validate_proposed_edit_card,
    RETRIEVAL_RESULTS_CARD_TYPE: validate_retrieval_results_card,
    BASKET_CARD_TYPE: validate_basket_card,
    CONTEXT_SET_CARD_TYPE: validate_context_set_card,
}


def _studio_filter_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    filtered = dict(card)
    actions = []
    seen_actions: set[str] = set()
    for action in card.get("actions", []):
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        if action.get("id") not in set(capabilities.actions_supported):
            continue
        action_key = json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        if action_key in seen_actions:
            continue
        seen_actions.add(action_key)
        actions.append(action)
    filtered["actions"] = sorted(
        actions,
        key=lambda action: json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
    )
    return filtered


def _engine_filter_actions(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    filtered = dict(card)
    supported_actions = set(capabilities.actions_supported)
    filtered["actions"] = [
        action
        for action in materialize_card_actions(card)
        if action.get("id") in supported_actions
    ]
    return filtered


def _engine_fallback_actions(
    card: dict[str, Any],
    capabilities: A2UICapabilities,
) -> list[dict[str, Any]]:
    return _engine_filter_actions(card, capabilities)["actions"]
