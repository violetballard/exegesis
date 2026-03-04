from __future__ import annotations

from typing import Any

from src.qual.ui.a2ui import A2UICapabilities, ActionRef, validate_capabilities


def require_object(payload: Any, *, field: str = "body") -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"{field} must be an object")
    return payload


def parse_a2ui_capabilities(payload: Any) -> A2UICapabilities:
    body = require_object(payload)
    capabilities = A2UICapabilities(
        a2ui_version=_require_int(body, "a2ui_version"),
        client_name=_require_non_empty_str(body, "client_name"),
        cards_supported=_require_str_tuple(body, "cards_supported"),
        primitive_blocks_supported=_require_str_tuple(body, "primitive_blocks_supported"),
        actions_supported=_require_str_tuple(body, "actions_supported"),
        max_payload_bytes=_require_int(body, "max_payload_bytes"),
        supports_streaming=_require_bool(body, "supports_streaming"),
    )
    validate_capabilities(capabilities)
    return capabilities


def parse_action_ref(payload: Any) -> ActionRef:
    body = require_object(payload)
    action_id = _require_non_empty_str(body, "id")
    label = _require_non_empty_str(body, "label")
    action_payload = require_object(body.get("payload"), field="payload")
    confirm_value = body.get("confirm")
    if confirm_value is not None:
        confirm_value = require_object(confirm_value, field="confirm")
    policy_sensitive = body.get("policy_sensitive", False)
    if not isinstance(policy_sensitive, bool):
        raise ValueError("policy_sensitive must be a boolean")
    return ActionRef(
        id=action_id,
        label=label,
        payload=action_payload,
        confirm=confirm_value,
        policy_sensitive=policy_sensitive,
    )


def _require_non_empty_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _require_int(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _require_bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean")
    return value


def _require_str_tuple(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list of strings")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{key} must be a list of strings")
        items.append(item)
    return tuple(items)
