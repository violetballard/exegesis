from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    ALLOWED_ACTION_IDS,
    PATCH_DECISION_CONTRACT_VERSION,
)
from exegesis_shared.contracts.cards import (
    A2UICapabilities,
    engine_prepare_card,
    materialize_cli_fallback_card,
    validate_card_payload_size,
)

A2UI_EVENT_CONTRACT_VERSION = 1
A2UI_STREAM_EVENT_TYPES: tuple[str, ...] = (
    "card_published",
    "action_selected",
    "action_resolved",
)
_A2UI_STREAM_EVENT_SET = set(A2UI_STREAM_EVENT_TYPES)
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)


def build_card_published_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    card: dict[str, Any],
    capabilities: A2UICapabilities,
) -> dict[str, Any]:
    prepared_card = materialize_cli_fallback_card(engine_prepare_card(card, capabilities))
    event = _base_event(event_id=event_id, run_id=run_id, sequence=sequence, event_type="card_published")
    event["card"] = prepared_card
    validate_stream_event(event, capabilities)
    return event


def build_action_selected_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    selection: dict[str, Any],
    action_id: str,
) -> dict[str, Any]:
    event = _base_event(event_id=event_id, run_id=run_id, sequence=sequence, event_type="action_selected")
    event["action_id"] = action_id
    event["selection"] = deepcopy(selection)
    validate_stream_event(event)
    return event


def build_action_resolved_event(
    *,
    event_id: str,
    run_id: str,
    sequence: int,
    action_id: str,
    status: str,
    message: str | None = None,
) -> dict[str, Any]:
    event = _base_event(event_id=event_id, run_id=run_id, sequence=sequence, event_type="action_resolved")
    event["action_id"] = action_id
    event["status"] = status
    if message is not None:
        event["message"] = message
    validate_stream_event(event)
    return event


def validate_stream_event(
    event: dict[str, Any],
    capabilities: A2UICapabilities | None = None,
) -> None:
    if not isinstance(event, dict):
        raise ValueError("A2UI stream event must be an object")
    if event.get("contract_version") != A2UI_EVENT_CONTRACT_VERSION:
        raise ValueError("Unsupported A2UI stream event contract version")
    event_type = event.get("event_type")
    if event_type not in _A2UI_STREAM_EVENT_SET:
        raise ValueError(f"Unsupported A2UI stream event type: {event_type}")
    _validate_required_text(event, "event_id")
    _validate_required_text(event, "run_id")
    sequence = event.get("sequence")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("A2UI stream event sequence must be a positive integer")
    if capabilities is not None and not capabilities.supports_streaming:
        raise ValueError("Client does not support A2UI streaming events")

    if event_type == "card_published":
        card = event.get("card")
        if not isinstance(card, dict):
            raise ValueError("card_published event requires a card object")
        if capabilities is not None:
            validate_card_payload_size(card, capabilities)
        return
    if event_type == "action_selected":
        _validate_required_text(event, "action_id")
        _validate_action_id(event, capabilities)
        selection = event.get("selection")
        if not isinstance(selection, dict):
            raise ValueError("action_selected event requires a selection object")
        if selection.get("contract_version") != ACTION_SELECTION_CONTRACT_VERSION:
            raise ValueError("Unsupported action selection contract version")
        return
    if event_type == "action_resolved":
        _validate_required_text(event, "action_id")
        _validate_action_id(event, capabilities)
        status = event.get("status")
        if status not in {"applied", "rejected", "blocked", "failed"}:
            raise ValueError("Unsupported action_resolved status")


def _base_event(*, event_id: str, run_id: str, sequence: int, event_type: str) -> dict[str, Any]:
    return {
        "contract_version": A2UI_EVENT_CONTRACT_VERSION,
        "event_id": event_id,
        "run_id": run_id,
        "sequence": sequence,
        "event_type": event_type,
    }


def _validate_required_text(event: dict[str, Any], key: str) -> None:
    value = event.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"A2UI stream event {key} is required")


def _validate_action_id(event: dict[str, Any], capabilities: A2UICapabilities | None) -> None:
    action_id = str(event.get("action_id", "")).strip()
    if action_id not in _ALLOWED_ACTION_SET:
        raise ValueError(f"Unsupported A2UI stream event action id: {action_id}")
    if capabilities is not None and action_id not in set(capabilities.actions_supported):
        raise ValueError(f"Client does not support A2UI stream event action id: {action_id}")


def stream_event_key(event: dict[str, Any]) -> str:
    validate_stream_event(event)
    return json.dumps(
        {
            "contract_version": event["contract_version"],
            "event_id": event["event_id"],
            "run_id": event["run_id"],
            "sequence": event["sequence"],
            "event_type": event["event_type"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
