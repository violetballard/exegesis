from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Literal

from exegesis_shared.contracts.actions import (
    ALLOWED_ACTION_IDS,
    ActionRef,
    PATCH_REVIEW_CLI_COMMAND_ALIASES,
    PolicyGate,
    advance_patch_review_state,
    execute_action_with_policy_gate,
    execute_complete_patch_review_action_with_policy_gate,
    validate_complete_patch_review_capabilities,
    materialize_action_selection_contract,
    materialize_card_actions,
    materialize_cli_fallback_card,
    resolve_complete_patch_review_cli_command_execution,
    resolve_complete_patch_review_control_execution,
    resolve_complete_patch_review_decision_cli_command_execution,
    validate_action_ref,
    validate_patch_review_execution_state,
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
_ALLOWED_BLOCK_FIELDS: dict[str, frozenset[str]] = {
    "MarkdownBlock": frozenset({"type", "markdown"}),
    "KeyValueBlock": frozenset({"type", "items"}),
    "ListBlock": frozenset({"type", "items"}),
    "TableBlock": frozenset({"type", "columns", "rows"}),
    "AlertBlock": frozenset({"type", "message", "severity"}),
    "ProgressBlock": frozenset({"type", "title", "status_text", "percentage"}),
    "CodeBlock": frozenset({"type", "language", "code", "collapsed"}),
}
_RETRIEVAL_RESULTS_CARD_FIELDS = frozenset({"type", "title", "query", "results", "actions", "action_selection"})
_BASKET_CARD_FIELDS = frozenset(
    {"type", "title", "basket_id", "items", "actions", "action_selection"}
)
_CONTEXT_SET_CARD_FIELDS = frozenset(
    {"type", "title", "context_set_id", "items", "actions", "action_selection"}
)
_PROPOSED_EDIT_CARD_FIELDS = frozenset(
    {"type", "title", "patch_id", "blocks", "actions", "action_selection", "patch_review"}
)
_GENERIC_CARD_FIELDS = frozenset(
    {"type", "title", "subtitle", "blocks", "actions", "action_selection", "debug"}
)
_UNKNOWN_CARD_FIELDS = frozenset(
    {
        "type",
        "title",
        "blocks",
        "actions",
        "patch_id",
        "action_selection",
        "patch_preview",
        "patch_decision",
        "patch_review",
        "patch_review_controls",
        "complete_patch_review_actions",
    }
)
DEMO_CONTEXT_CARD_TYPES: tuple[str, ...] = (
    RETRIEVAL_RESULTS_CARD_TYPE,
    BASKET_CARD_TYPE,
    CONTEXT_SET_CARD_TYPE,
)
DEMO_CONTEXT_ACTION_IDS: tuple[str, ...] = (
    "open_corpus_item",
    "promote_to_basket",
    "pin_to_context_set",
    "create_context_set",
    "gather_context",
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

    def supports_card(self, card_type: str) -> bool:
        """Return True if the client supports the given card type."""
        try:
            return str(card_type).strip() in self.cards_supported
        except (ValueError, TypeError, AttributeError):
            return False

    def supports_block(self, block_type: str) -> bool:
        """Return True if the client supports the given primitive block type."""
        try:
            return str(block_type).strip() in self.primitive_blocks_supported
        except (ValueError, TypeError, AttributeError):
            return False

    def supports_action(self, action_id: str) -> bool:
        """Return True if the client supports the given action ID."""
        try:
            return str(action_id).strip() in self.actions_supported
        except (ValueError, TypeError, AttributeError):
            return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> A2UICapabilities:
        """Construct an A2UICapabilities from a dictionary representation."""
        if not isinstance(data, dict):
            raise ValueError("A2UICapabilities data must be a dict")
        unexpected_keys = set(data) - {
            "a2ui_version",
            "client_name",
            "cards_supported",
            "primitive_blocks_supported",
            "actions_supported",
            "max_payload_bytes",
            "supports_streaming",
        }
        if unexpected_keys:
            field_list = ", ".join(sorted(unexpected_keys))
            raise ValueError(f"Unsupported A2UICapabilities field(s): {field_list}")
        for key in (
            "a2ui_version",
            "client_name",
            "cards_supported",
            "primitive_blocks_supported",
            "actions_supported",
            "max_payload_bytes",
            "supports_streaming",
        ):
            if key not in data:
                raise ValueError(f"A2UICapabilities data missing required key: {key}")

        cards_sup = data["cards_supported"]
        if not isinstance(cards_sup, (list, tuple)):
            raise ValueError("A2UICapabilities.cards_supported must be a list or tuple")
        blocks_sup = data["primitive_blocks_supported"]
        if not isinstance(blocks_sup, (list, tuple)):
            raise ValueError("A2UICapabilities.primitive_blocks_supported must be a list or tuple")
        actions_sup = data["actions_supported"]
        if not isinstance(actions_sup, (list, tuple)):
            raise ValueError("A2UICapabilities.actions_supported must be a list or tuple")

        return cls(
            a2ui_version=data["a2ui_version"],
            client_name=data["client_name"],
            cards_supported=tuple(cards_sup),
            primitive_blocks_supported=tuple(blocks_sup),
            actions_supported=tuple(actions_sup),
            max_payload_bytes=data["max_payload_bytes"],
            supports_streaming=bool(data["supports_streaming"]),
        )

    def as_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of these capabilities."""
        return {
            "a2ui_version": self.a2ui_version,
            "client_name": self.client_name,
            "cards_supported": list(self.cards_supported),
            "primitive_blocks_supported": list(self.primitive_blocks_supported),
            "actions_supported": list(self.actions_supported),
            "max_payload_bytes": self.max_payload_bytes,
            "supports_streaming": self.supports_streaming,
        }



class A2UISessionStore:
    def __init__(self) -> None:
        self._by_session: dict[str, A2UICapabilities] = {}

    def register(self, session_id: str, capabilities: A2UICapabilities) -> None:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id is required")
        if session_id != session_id.strip():
            raise ValueError("session_id must be normalized")
        validate_capabilities(capabilities)
        self._by_session[session_id] = capabilities

    def get(self, session_id: str) -> A2UICapabilities:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id is required")
        if session_id != session_id.strip():
            raise ValueError("session_id must be normalized")
        if session_id not in self._by_session:
            raise KeyError(f"Unknown session: {session_id}")
        return self._by_session[session_id]

    def unregister(self, session_id: str) -> None:
        """Release a session's capabilities when the session ends.

        Silently ignores unknown session IDs so callers can call this
        unconditionally in cleanup paths without guarding against double-release.
        """
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id is required")
        if session_id != session_id.strip():
            raise ValueError("session_id must be normalized")
        self._by_session.pop(session_id, None)

    def active_sessions(self) -> frozenset[str]:
        """Return the set of currently registered session IDs."""
        return frozenset(self._by_session)


def validate_capabilities(capabilities: A2UICapabilities) -> None:
    if not isinstance(capabilities, A2UICapabilities):
        raise ValueError("capabilities must be an A2UICapabilities instance")
    if not isinstance(capabilities.a2ui_version, int) or isinstance(capabilities.a2ui_version, bool):
        raise ValueError("a2ui_version must be a positive integer")
    if capabilities.a2ui_version != A2UI_VERSION:
        raise ValueError("Unsupported a2ui version")
    if not isinstance(capabilities.client_name, str) or not capabilities.client_name.strip():
        raise ValueError("client_name is required")
    if capabilities.client_name != capabilities.client_name.strip():
        raise ValueError("client_name must be normalized")
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
    if not capabilities.supports_card(PROPOSED_EDIT_CARD_TYPE):
        raise ValueError("Complete patch review requires ProposedEditCard support")
    validate_complete_patch_review_capabilities(capabilities)


def resolve_complete_patch_review_card_control_execution(
    card: dict[str, Any],
    *,
    patch_id: str,
    control: str,
    capabilities: A2UICapabilities,
) -> dict[str, Any]:
    validate_complete_patch_review_card_capabilities(capabilities)
    return resolve_complete_patch_review_control_execution(
        card,
        patch_id=patch_id,
        control=control,
        capabilities=capabilities,
    )


def resolve_complete_patch_review_card_cli_command_execution(
    card: dict[str, Any],
    *,
    patch_id: str,
    command: str,
    capabilities: A2UICapabilities,
) -> dict[str, Any]:
    validate_complete_patch_review_card_capabilities(capabilities)
    return resolve_complete_patch_review_cli_command_execution(
        card,
        patch_id=patch_id,
        command=command,
        capabilities=capabilities,
    )


def resolve_complete_patch_review_card_decision_cli_command_execution(
    card: dict[str, Any],
    *,
    patch_id: str,
    command: str,
    capabilities: A2UICapabilities,
) -> dict[str, Any]:
    validate_complete_patch_review_card_capabilities(capabilities)
    return resolve_complete_patch_review_decision_cli_command_execution(
        card,
        patch_id=patch_id,
        command=command,
        capabilities=capabilities,
    )


def validate_demo_context_card_capabilities(capabilities: A2UICapabilities) -> None:
    validate_capabilities(capabilities)
    missing_cards = [
        card_type
        for card_type in DEMO_CONTEXT_CARD_TYPES
        if not capabilities.supports_card(card_type)
    ]
    if missing_cards:
        raise ValueError(
            "Demo context flow requires card support: "
            + ", ".join(missing_cards)
        )
    missing_actions = [
        action_id
        for action_id in DEMO_CONTEXT_ACTION_IDS
        if not capabilities.supports_action(action_id)
    ]
    if missing_actions:
        raise ValueError(
            "Demo context flow requires action support: "
            + ", ".join(missing_actions)
        )


def validate_engine_demo_path_capabilities(capabilities: A2UICapabilities) -> None:
    validate_demo_context_card_capabilities(capabilities)
    validate_complete_patch_review_card_capabilities(capabilities)


def supports_engine_demo_path(capabilities: A2UICapabilities) -> bool:
    """Return True if capabilities support the complete engine demo path.

    Checks if retrieval, basket, context cards, and complete patch review actions are supported.
    """
    try:
        validate_engine_demo_path_capabilities(capabilities)
        return True
    except ValueError:
        return False


def _validate_capability_names(values: Any, field_name: str) -> None:
    if not isinstance(values, tuple):
        raise ValueError(f"{field_name} must be a tuple")
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} entries must be non-empty strings")
        normalized = value.strip()
        if value != normalized:
            raise ValueError(f"{field_name} entries must be normalized: {normalized}")
        if normalized in seen:
            raise ValueError(f"{field_name} entries must be unique: {normalized}")
        seen.add(normalized)


def engine_prepare_card(card: dict[str, Any], capabilities: A2UICapabilities) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
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
        if capabilities.supports_card(card_type):
            prepared = _engine_filter_actions(prepared, capabilities)
            prepared = materialize_cli_fallback_card(prepared)
            validate_card_payload_size(prepared, capabilities)
            return prepared
        card = prepared
    elif card_type in _VALIDATORS_BY_CARD_TYPE:
        validate_known_card(card)
        if capabilities.supports_card(card_type):
            prepared = _engine_filter_actions(card, capabilities)
            prepared = materialize_cli_fallback_card(prepared)
            validate_card_payload_size(prepared, capabilities)
            return prepared
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
                "code": json.dumps(card, indent=2, sort_keys=True, ensure_ascii=True, default=str),
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
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    validate_capabilities(capabilities)
    card_type = str(card.get("type", "")).strip()
    if card_type == GENERIC_CARD_TYPE:
        validate_generic_card(card, strict_actions=False)
        materialized = materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
        materialized = _prune_incomplete_unknown_patch_review(materialized)
        validate_card_payload_size(materialized, capabilities)
        return materialized
    if card_type == PROPOSED_EDIT_CARD_TYPE:
        if not capabilities.supports_card(card_type):
            validate_proposed_edit_card(card, strict_actions=False)
            card = build_unknown_card(materialize_proposed_edit_card(card))
        else:
            card = materialize_proposed_edit_card(card)
        materialized = materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
        materialized = _prune_incomplete_unknown_patch_review(materialized)
        validate_card_payload_size(materialized, capabilities)
        return materialized
    if card_type in _VALIDATORS_BY_CARD_TYPE:
        validate_known_card(card, strict_actions=False)
        if not capabilities.supports_card(card_type):
            card = build_unknown_card(card)
        materialized = materialize_cli_fallback_card(_studio_filter_actions(card, capabilities))
        materialized = _prune_incomplete_unknown_patch_review(materialized)
        validate_card_payload_size(materialized, capabilities)
        return materialized
    materialized = materialize_cli_fallback_card(_studio_filter_actions(build_unknown_card(card), capabilities))
    materialized = _prune_incomplete_unknown_patch_review(materialized)
    validate_card_payload_size(materialized, capabilities)
    return materialized


def _prune_incomplete_unknown_patch_review(card: dict[str, Any]) -> dict[str, Any]:
    if card.get("type") != UNKNOWN_CARD_TYPE:
        return card
    patch_review = card.get("patch_review")
    if not isinstance(patch_review, dict):
        return card
    availability = patch_review.get("availability")
    if isinstance(availability, dict) and availability.get("is_complete") is True:
        return card
    patch_decision = card.get("patch_decision")
    decisions = patch_decision.get("decisions") if isinstance(patch_decision, dict) else None
    if isinstance(decisions, list) and decisions:
        return card
    pruned = dict(card)
    pruned.pop("patch_review", None)
    pruned.pop("patch_review_controls", None)
    pruned.pop("complete_patch_review_actions", None)
    return pruned


def validate_card_payload_size(card: dict[str, Any], capabilities: A2UICapabilities) -> None:
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    validate_capabilities(capabilities)
    try:
        encoded = json.dumps(card, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    except TypeError as e:
        raise ValueError(f"A2UI card is not JSON-serializable: {e}") from e
    if len(encoded) > capabilities.max_payload_bytes:
        raise ValueError(
            "A2UI card payload exceeds negotiated max_payload_bytes "
            f"({len(encoded)} > {capabilities.max_payload_bytes})"
        )


def build_unknown_card(
    raw_card: dict[str, Any],
    capabilities: A2UICapabilities | None = None,
) -> dict[str, Any]:
    if not isinstance(raw_card, dict):
        raise ValueError("Card must be a dictionary")
    type_name = str(raw_card.get("type", "<missing>"))
    nested_blocks = raw_card.get("blocks")
    blocks: list[dict[str, Any]] = []
    if isinstance(nested_blocks, list):
        for block in nested_blocks:
            try:
                validate_primitive_block(block)
            except ValueError:
                continue
            if capabilities is not None:
                block_type = block.get("type")
                if not capabilities.supports_block(block_type):
                    continue
            blocks.append(block)
    blocks.append(_unknown_card_support_summary(raw_card))
    try:
        raw_card_json = json.dumps(raw_card, indent=2, sort_keys=True, ensure_ascii=True, default=str)
    except (ValueError, TypeError) as e:
        try:
            raw_repr = str(raw_card)
        except Exception as str_err:
            raw_repr = f"<Failed to get raw representation: {str_err}>"
        raw_card_json = f"<Unserializable card payload: {e}>\n\nRaw representation: {raw_repr}"

    blocks.append(
        {
            "type": "CodeBlock",
            "language": "json",
            "code": raw_card_json,
            "collapsed": True,
        }
    )
    patch_id = raw_card.get("patch_id")
    actions = _unknown_card_safe_actions(raw_card, patch_id)

    try:
        copy_text = json.dumps(raw_card, default=str)
    except (ValueError, TypeError) as e:
        try:
            raw_repr = str(raw_card)
        except Exception as str_err:
            raw_repr = f"<Failed to get raw representation: {str_err}>"
        copy_text = f"<Unserializable card payload: {e}>\n\nRaw representation: {raw_repr}"

    actions.append({"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": copy_text}})
    actions = materialize_card_actions({"actions": actions})
    if capabilities is not None:
        validate_capabilities(capabilities)
        actions = [
            action
            for action in actions
            if capabilities.supports_action(action.get("id"))
        ]
    fallback = {
        "type": UNKNOWN_CARD_TYPE,
        "title": f"Unsupported card type: {type_name}",
        "blocks": blocks,
        "actions": actions,
    }
    if isinstance(patch_id, str) and patch_id.strip():
        fallback["patch_id"] = patch_id.strip()
    return fallback


def _unknown_card_safe_actions(raw_card: dict[str, Any], patch_id: Any) -> list[dict[str, Any]]:
    """Keep unsupported cards inspectable without trusting future-card actions."""
    if raw_card.get("type") in KNOWN_CARD_TYPES:
        return materialize_card_actions(raw_card)
    if not isinstance(patch_id, str) or not patch_id.strip():
        return []
    expected_patch_id = patch_id.strip()
    safe_actions: list[dict[str, Any]] = []
    for action in materialize_card_actions(raw_card):
        if action.get("id") not in {"preview_patch", "apply_patch", "reject_patch"}:
            continue
        payload = action.get("payload")
        action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
        if isinstance(action_patch_id, str) and action_patch_id.strip() == expected_patch_id:
            safe_actions.append(action)
    return safe_actions


def materialize_action_slots(card: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    slots: list[dict[str, Any]] = []
    for slot, action in enumerate(materialize_card_actions(card), start=1):
        slots.append(
            {
                "slot": slot,
                "command": str(slot),
                "action": action,
                "aliases": _action_selection_aliases(action),
            }
        )
    return tuple(slots)


def resolve_action_selection(card: dict[str, Any], selection: str | int) -> ActionRef:
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    token = str(selection).strip()
    for slot in materialize_action_slots(card):
        aliases = {slot["command"], *slot["aliases"]}
        if token not in aliases:
            continue
        action = slot["action"]
        return ActionRef(
            id=str(action["id"]),
            label=str(action["label"]),
            payload=dict(action["payload"]),
            confirm=action.get("confirm") if isinstance(action.get("confirm"), dict) else None,
            policy_sensitive=bool(action.get("policy_sensitive", False)),
        )
    raise KeyError(f"Unknown action selection: {selection}")


def resolve_action_from_selection_model(
    card: dict[str, Any],
    selection: Any,
) -> ActionRef:
    """Resolve an ActionRef from a typed Selection model against a card.

    Only ``workflow_card`` selections can drive card action dispatch — any other
    ``Selection.type`` raises ``ValueError`` so callers cannot accidentally route
    inspector or basket selections into the card action path.

    The ``selection.id`` is treated as the action command or alias token and is
    forwarded to ``resolve_action_selection``.  ``KeyError`` is propagated if no
    matching action is found on the card.

    Raises:
        AttributeError: if ``selection`` is not a Selection-like object.
        ValueError: if ``selection.type`` is not ``"workflow_card"``.
        KeyError: if ``selection.id`` does not match any action slot on the card.
    """
    if isinstance(selection, dict):
        sel_type = selection.get("type")
        sel_id = selection.get("id")
    else:
        try:
            sel_type = selection.type
            sel_id = selection.id
        except AttributeError as exc:
            raise AttributeError(
                "selection must be a Selection instance or a dict with 'type' and 'id'"
            ) from exc

    if sel_type != "workflow_card":
        raise ValueError(
            f"Only workflow_card selections can drive card action dispatch; got {sel_type!r}"
        )
    if sel_id is None:
        raise ValueError("Selection is missing 'id'")
    return resolve_action_selection(card, sel_id)



def execute_patch_review_from_typed_selection_with_policy_gate(
    *,
    card: dict[str, Any],
    selection: Any,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    """Execute a patch review action from a typed Selection model through a policy gate.

    Bridges ``resolve_action_from_selection_model`` (workflow_card guard) directly
    to ``execute_action_with_policy_gate``, closing the typed Selection →
    engine action dispatch loop for the canonical patch review demo path.

    Raises:
        ValueError: if ``selection.type`` is not ``"workflow_card"``.
        KeyError: if ``selection.id`` does not match any action slot on the card.
        PermissionError: if the policy gate denies the action.
    """
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    action_ref = resolve_action_from_selection_model(card, selection)
    return execute_action_with_policy_gate(
        action=action_ref,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_card_action_from_typed_selection_with_policy_gate(
    *,
    card: dict[str, Any],
    selection: Any,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    """Execute any card action from a typed Selection model through a policy gate.

    Generic companion to ``execute_patch_review_from_typed_selection_with_policy_gate``
    that works for any card type — basket, retrieval, context, or patch review —
    without patch-state advancement.  Callers that need state tracking after a
    patch review decision should use
    ``execute_patch_review_from_typed_selection_and_advance_state`` instead.

    Raises:
        ValueError: if ``selection.type`` is not ``"workflow_card"``.
        KeyError: if ``selection.id`` does not match any action slot on the card.
        PermissionError: if the policy gate denies the action.
    """
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    action_ref = resolve_action_from_selection_model(card, selection)
    return execute_action_with_policy_gate(
        action=action_ref,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_patch_review_from_typed_selection_and_advance_state(
    *,
    card: dict[str, Any],
    selection: Any,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
    review_state: Any = None,
) -> "PatchReviewExecutionOutcome":
    """Execute a patch review action from a typed Selection model and return a typed outcome.

    Combines ``execute_patch_review_from_typed_selection_with_policy_gate`` and
    ``advance_patch_review_state`` into a single authoritative entry point for the
    canonical demo path: typed Selection → policy-gated engine action →
    ``PatchReviewExecutionOutcome`` with updated review state.

    Accepts ``review_state`` as a plain dict, a typed ``PatchReviewState`` object
    (as returned by ``PatchReviewState.from_engine_loop_outcome``), or None so
    that callers on the EngineLoopOutcome → PatchReviewState path do not have to
    call ``.as_dict()`` manually before entering this entry point.

    Callers that only need the executor return value and do not need state
    advancement should use ``execute_patch_review_from_typed_selection_with_policy_gate``
    instead.

    Raises:
        ValueError: if ``selection.type`` is not ``"workflow_card"``, or if the
            resolved action is not a patch review action, or if a decision is
            attempted without a prior preview.
        KeyError: if ``selection.id`` does not match any action slot on the card.
        PermissionError: if the policy gate denies the action.
        TypeError: if ``review_state`` is not a dict, PatchReviewState, or None.
    """
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    state_dict = _coerce_review_state(review_state)
    action_ref = resolve_action_from_selection_model(card, selection)
    _PATCH_ACTION_TO_CONTROL = {
        "preview_patch": "preview",
        "apply_patch": "apply",
        "reject_patch": "reject",
    }
    control = _PATCH_ACTION_TO_CONTROL.get(action_ref.id)
    if control is None:
        raise ValueError(
            f"Typed Selection resolved to non-patch-review action {action_ref.id!r}; "
            "execute_patch_review_from_typed_selection_and_advance_state requires a "
            "preview_patch, apply_patch, or reject_patch action"
        )
    if control in {"apply", "reject"}:
        if state_dict is None:
            raise PermissionError("Patch review decision requires preview")
        validate_patch_review_execution_state(
            control=control,
            patch_id=action_ref.payload.get("patch_id", ""),
            review_state=state_dict,
        )
    executor_result = execute_action_with_policy_gate(
        action=action_ref,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )
    patch_id = str(action_ref.payload.get("patch_id", "")).strip()
    if not patch_id:
        raise ValueError("Patch review action payload must include patch_id")
    new_state = advance_patch_review_state(
        patch_id=patch_id,
        control=control,
        current_state=state_dict,
    )
    return PatchReviewExecutionOutcome(
        executor_result=executor_result,
        review_state=new_state,
        control=control,
        patch_id=patch_id,
    )


def materialize_patch_selection_envelope(card: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    preview_slots = []
    decision_slots = []
    patch_ids: set[str] = set()
    for slot in materialize_action_slots(card):
        action = slot["action"]
        action_id = action.get("id")
        if action_id == "preview_patch":
            preview_slots.append(slot)
        elif action_id in {"apply_patch", "reject_patch"}:
            decision_slots.append(slot)
        else:
            continue
        patch_id = action.get("payload", {}).get("patch_id")
        if isinstance(patch_id, str):
            patch_ids.add(patch_id)
    if not preview_slots and not decision_slots:
        raise ValueError("Patch selection requires preview_patch, apply_patch, or reject_patch actions")
    if len(patch_ids) != 1:
        raise ValueError("Patch selection requires actions for exactly one patch_id")
    return {
        "type": "PatchActionSelection",
        "patch_id": next(iter(patch_ids)),
        "preview": {
            "command": "preview",
            "actions": [slot["command"] for slot in preview_slots],
        },
        "decision": {
            "actions": [slot["command"] for slot in decision_slots],
        },
        "actions": [*preview_slots, *decision_slots],
    }


def execute_patch_review_action(
    *,
    card: dict[str, Any],
    selection: str | int,
    capabilities: A2UICapabilities,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
    review_state: dict[str, Any] | None = None,
) -> Any:
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    envelope = materialize_patch_selection_envelope(card)
    action = resolve_action_selection(card, selection)
    if action.id not in {"preview_patch", "apply_patch", "reject_patch"}:
        raise ValueError("Patch review selection must resolve to a patch action")
    if action.payload.get("patch_id") != envelope["patch_id"]:
        raise ValueError("Patch review action does not match envelope patch_id")
    control = {
        "preview_patch": "preview",
        "apply_patch": "apply",
        "reject_patch": "reject",
    }[action.id]
    execution = resolve_complete_patch_review_control_execution(
        card,
        patch_id=str(envelope["patch_id"]),
        control=control,
        capabilities=capabilities,
    )
    if control in {"apply", "reject"}:
        if review_state is None:
            raise PermissionError("Patch review decision requires preview")
        validate_patch_review_execution_state(
            control=control,
            patch_id=str(envelope["patch_id"]),
            review_state=review_state,
        )
    action_contract = execution["action_contract"]
    action = ActionRef(
        id=str(action_contract["id"]),
        label=str(action_contract["label"]),
        payload=dict(action_contract["payload"]),
        confirm=action_contract.get("confirm")
        if isinstance(action_contract.get("confirm"), dict)
        else None,
        policy_sensitive=bool(action_contract.get("policy_sensitive", False)),
    )
    return execute_action_with_policy_gate(
        action=action,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


@dataclass(frozen=True)
class PatchReviewExecutionOutcome:
    """Typed result from execute_patch_review_action_and_advance_state.

    ``executor_result`` is whatever the caller's executor returned.
    ``review_state`` is the new patch review state after the control executed.
    ``control`` is the normalized control that was executed: 'preview', 'apply', or 'reject'.
    ``patch_id`` is the patch identifier from the card envelope.
    """

    executor_result: Any
    review_state: dict[str, Any]
    control: str
    patch_id: str

    _VALID_CONTROLS: ClassVar[frozenset[str]] = frozenset({"preview", "apply", "reject"})

    def __post_init__(self) -> None:
        if self.control not in self._VALID_CONTROLS:
            raise ValueError(
                f"PatchReviewExecutionOutcome.control must be one of "
                f"{sorted(self._VALID_CONTROLS)!r}, got {self.control!r}"
            )
        if not isinstance(self.patch_id, str) or not self.patch_id.strip():
            raise ValueError("PatchReviewExecutionOutcome.patch_id must be a non-empty string")
        if self.patch_id != self.patch_id.strip():
            raise ValueError("PatchReviewExecutionOutcome.patch_id must be normalized")
        if not isinstance(self.review_state, dict):
            raise ValueError("PatchReviewExecutionOutcome.review_state must be a dict")

    @property
    def is_resolved(self) -> bool:
        """True when the patch has been given a final decision (apply or reject)."""
        return self.review_state.get("resolved") is True

    @property
    def is_applied(self) -> bool:
        """True when the patch review has resolved as applied."""
        return self.is_resolved and self.resolved_as == "apply"

    @property
    def is_rejected(self) -> bool:
        """True when the patch review has resolved as rejected."""
        return self.is_resolved and self.resolved_as == "reject"

    @property
    def resolved_as(self) -> str | None:
        """The decision control ('apply' or 'reject'), or None if not yet resolved."""
        return self.review_state.get("resolved_as") if self.is_resolved else None

    @property
    def is_previewed(self) -> bool:
        """True when the patch content has been previewed."""
        return self.review_state.get("previewed") is True

    @property
    def is_pending(self) -> bool:
        """True when no control has been executed yet (not previewed and not resolved)."""
        return not self.is_previewed and not self.is_resolved

    @property
    def status(self) -> str:
        """Canonical resolved-status string for this outcome.

        Maps directly to the event-level status: 'previewed', 'applied', or 'rejected'.
        Equivalent to PATCH_REVIEW_RESOLVED_STATUSES[self.control] without requiring
        the caller to import that mapping.
        """
        _status_map = {"preview": "previewed", "apply": "applied", "reject": "rejected"}
        return _status_map[self.control]

    @property
    def typed_review_state(self) -> Any:
        """Typed accessor: return review_state as a PatchReviewState domain object.

        Convenience for engine and future Textual consumers that prefer typed state
        over raw dict access.  Equivalent to PatchReviewState.from_dict(self.review_state).
        """
        from exegesis_shared.models.patch_review_state import PatchReviewState

        return PatchReviewState.from_dict(self.review_state)

    @property
    def next_controls(self) -> tuple[str, ...]:
        """Controls the engine loop may offer next, derived from the post-action state.

        Shortcut for ``outcome.typed_review_state.available_controls()``.  Returns
        ``("apply", "reject")`` after a successful preview, ``()`` after a decision,
        and ``("preview",)`` if the outcome left the patch in a pending state (unusual
        but possible in error-recovery paths).
        """
        return self.typed_review_state.available_controls()

    def can_advance(self, control: str) -> bool:
        """Return True if the post-action state can be transitioned using *control*.

        Accepts: "preview", "apply", "reject".
        Shortcut for ``outcome.typed_review_state.can_advance(control)``.
        """
        return self.typed_review_state.can_advance(control)

    def resolved_control(self) -> str | None:
        """The decision control ('apply' or 'reject'), or None if not yet resolved.

        Shortcut for ``outcome.typed_review_state.resolved_control()``.
        """
        return self.typed_review_state.resolved_control()

    def available_action_ids(self) -> tuple[str, ...]:
        """Return action IDs corresponding to available_controls(), in canonical order.

        Shortcut for ``outcome.typed_review_state.available_action_ids()``.
        """
        return self.typed_review_state.available_action_ids()

    @property
    def patch_outcome(self) -> Literal["previewed", "applied", "rejected"] | None:
        """Return the patch outcome status corresponding to this state.

        Shortcut for ``outcome.typed_review_state.patch_outcome``.
        """
        return self.typed_review_state.patch_outcome

    @property
    def engine_status(self) -> Literal["pending", "waiting_for_action", "complete"]:
        """Return the engine-vocabulary status string for this state.

        Shortcut for ``outcome.typed_review_state.engine_status``.
        """
        return self.typed_review_state.engine_status

    def next_action_hints(self) -> list[dict[str, Any]]:
        """Return structured next-action hints for this state, in canonical order.

        Shortcut for ``outcome.typed_review_state.next_action_hints()``.
        """
        return self.typed_review_state.next_action_hints()

    def as_contract(self) -> dict[str, Any]:
        """Serialize to a stable contract dict for engine-loop logging and event payloads.

        Keys: ``patch_id``, ``control``, ``status``, ``is_resolved``, ``is_previewed``,
        ``resolved_as``, ``next_controls``, ``review_state``.
        """
        return {
            "patch_id": self.patch_id,
            "control": self.control,
            "status": self.status,
            "is_resolved": self.is_resolved,
            "is_previewed": self.is_previewed,
            "resolved_as": self.resolved_as,
            "next_controls": list(self.next_controls),
            "review_state": dict(self.review_state),
        }

    @classmethod
    def from_contract(
        cls,
        contract: dict[str, Any],
        *,
        executor_result: Any = None,
    ) -> "PatchReviewExecutionOutcome":
        """Reconstruct from a contract dict produced by ``as_contract()``.

        ``executor_result`` defaults to ``None`` because it is not serialized into
        the contract (it is caller-owned).  Pass it explicitly when the original
        result is still in scope.

        Raises ``ValueError`` if the contract is malformed or missing required keys.
        """
        if not isinstance(contract, dict):
            raise ValueError("PatchReviewExecutionOutcome contract must be a dict")
        unexpected_keys = set(contract) - {
            "patch_id",
            "control",
            "status",
            "is_resolved",
            "is_previewed",
            "resolved_as",
            "next_controls",
            "review_state",
        }
        if unexpected_keys:
            field_list = ", ".join(sorted(unexpected_keys))
            raise ValueError(f"Unsupported PatchReviewExecutionOutcome field(s): {field_list}")
        patch_id = contract.get("patch_id")
        if not isinstance(patch_id, str) or not patch_id.strip():
            raise ValueError("PatchReviewExecutionOutcome contract patch_id is required")
        control = contract.get("control")
        if control not in cls._VALID_CONTROLS:
            raise ValueError(
                f"PatchReviewExecutionOutcome contract control must be one of "
                f"{sorted(cls._VALID_CONTROLS)!r}, got {control!r}"
            )
        review_state = contract.get("review_state")
        if not isinstance(review_state, dict):
            raise ValueError("PatchReviewExecutionOutcome contract review_state must be a dict")
        return cls(
            executor_result=executor_result,
            review_state=dict(review_state),
            control=str(control),
            patch_id=patch_id,
        )

    def as_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of this outcome."""
        return self.as_contract()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatchReviewExecutionOutcome:
        """Construct a PatchReviewExecutionOutcome from a dictionary representation."""
        return cls.from_contract(data)


def execute_patch_review_action_and_advance_state(
    *,
    card: dict[str, Any],
    selection: str | int,
    capabilities: A2UICapabilities,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
    review_state: Any = None,
) -> PatchReviewExecutionOutcome:
    """Execute a patch review action and return a typed PatchReviewExecutionOutcome.

    Wraps execute_patch_review_action and advance_patch_review_state into a single
    authoritative call for the engine demo path, so callers don't need to advance
    state separately after a successful execution.
    """
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    envelope = materialize_patch_selection_envelope(card)
    patch_id = str(envelope["patch_id"])
    action_obj = resolve_action_selection(card, selection)
    control = {
        "preview_patch": "preview",
        "apply_patch": "apply",
        "reject_patch": "reject",
    }.get(action_obj.id)
    if control is None:
        raise ValueError("Patch review selection must resolve to a patch action")
    state_dict = _coerce_review_state(review_state)
    result = execute_patch_review_action(
        card=card,
        selection=selection,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
        review_state=state_dict,
    )
    new_state = advance_patch_review_state(
        patch_id=patch_id,
        control=control,
        current_state=state_dict,
    )
    return PatchReviewExecutionOutcome(
        executor_result=result,
        review_state=new_state,
        control=control,
        patch_id=patch_id,
    )


def _coerce_review_state(review_state: Any) -> dict[str, Any] | None:
    """Normalize review_state to a plain dict (or None) accepted by actions layer.

    Accepts a typed PatchReviewState dataclass, a plain dict, or None so that
    callers who hold a PatchReviewState object from from_engine_loop_outcome() do
    not have to call .as_dict() manually before entering the execute-and-advance path.
    """
    if review_state is None:
        return None
    if isinstance(review_state, dict):
        return review_state
    # Accept PatchReviewState without importing it at module level (avoids circular deps).
    as_dict = getattr(review_state, "as_dict", None)
    if callable(as_dict):
        return as_dict()
    raise TypeError(
        f"review_state must be a dict, PatchReviewState, or None; got {type(review_state).__name__!r}"
    )


def execute_complete_patch_review_action_and_advance_state(
    *,
    card: dict[str, Any],
    patch_id: str,
    control: str,
    capabilities: A2UICapabilities,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
    review_state: Any = None,
) -> PatchReviewExecutionOutcome:
    """Execute a complete-patch-review action and return a typed PatchReviewExecutionOutcome.

    Validates complete-patch-review capabilities, executes the action through the
    policy gate, and advances the review state in one authoritative call.  Use this
    as the engine demo-path entry point when the card carries a full
    ``complete_patch_review_actions`` contract.
    """
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("patch_id is required")
    normalized_control = control.strip().lower()
    state_dict = _coerce_review_state(review_state)
    result = execute_complete_patch_review_action_with_policy_gate(
        card=card,
        patch_id=expected_patch_id,
        control=normalized_control,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
        review_state=state_dict,
    )
    new_state = advance_patch_review_state(
        patch_id=expected_patch_id,
        control=normalized_control,
        current_state=state_dict,
    )
    return PatchReviewExecutionOutcome(
        executor_result=result,
        review_state=new_state,
        control=normalized_control,
        patch_id=expected_patch_id,
    )


def execute_complete_patch_review_cli_command_and_advance_state(
    *,
    card: dict[str, Any],
    patch_id: str,
    command: str,
    capabilities: "A2UICapabilities",
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
    review_state: Any = None,
) -> PatchReviewExecutionOutcome:
    """Execute a complete-patch-review CLI command and return a typed PatchReviewExecutionOutcome.

    CLI companion to ``execute_complete_patch_review_action_and_advance_state``.
    Accepts human-readable command strings ('preview', 'apply', 'reject', 'apply_patch', etc.)
    and routes them through the complete-patch-review capability contract before
    executing and advancing the review state in one authoritative call.

    This closes the CLI fallback surface for the canonical demo path: callers can
    track state across preview → apply/reject without calling advance_patch_review_state
    separately.

    Raises:
        ValueError: if ``patch_id`` is empty or the command does not map to a valid control.
        PermissionError: if the policy gate denies the action or a decision is attempted
            without a prior preview.
    """
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    execution = resolve_complete_patch_review_cli_command_execution(
        card,
        patch_id=patch_id,
        command=command,
        capabilities=capabilities,
    )
    control = str(execution["control"])
    return execute_complete_patch_review_action_and_advance_state(
        card=card,
        patch_id=patch_id,
        control=control,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
        review_state=review_state,
    )


def _action_selection_aliases(action: dict[str, Any]) -> tuple[str, ...]:
    action_id = str(action.get("id", ""))
    aliases = [action_id]
    for control, control_aliases in PATCH_REVIEW_CLI_COMMAND_ALIASES.items():
        expected_action_id = "preview_patch" if control == "preview" else f"{control}_patch"
        if action_id == expected_action_id:
            aliases.extend(alias for alias in control_aliases if alias not in aliases)
    return tuple(aliases)


def _unknown_card_support_summary(raw_card: dict[str, Any]) -> dict[str, Any]:
    raw_actions = raw_card.get("actions", [])
    raw_action_count = len(raw_actions) if isinstance(raw_actions, list) else 0
    materialized_actions = materialize_card_actions(raw_card)
    return {
        "type": "KeyValueBlock",
        "items": [
            {"key": "original_type", "value": str(raw_card.get("type", "<missing>"))},
            {"key": "fallback", "value": "UnknownCard"},
            {"key": "typed_action_candidates", "value": str(len(materialized_actions))},
            {"key": "invalid_actions_filtered", "value": str(raw_action_count - len(materialized_actions))},
            {"key": "raw_payload_available", "value": "true"},
        ],
    }


def validate_unknown_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_fields(card, UNKNOWN_CARD_TYPE, _UNKNOWN_CARD_FIELDS)
    if card.get("type") != UNKNOWN_CARD_TYPE:
        raise ValueError("Card type must be UnknownCard")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("UnknownCard title is required")
    if title != title.strip():
        raise ValueError("UnknownCard title must be normalized")
    if "patch_id" in card:
        patch_id = card["patch_id"]
        if not isinstance(patch_id, str) or not patch_id.strip():
            raise ValueError("UnknownCard patch_id must be a non-empty string")
        if patch_id != patch_id.strip():
            raise ValueError("UnknownCard patch_id must be normalized")
    blocks = card.get("blocks")
    if blocks is not None:
        if not isinstance(blocks, list):
            raise ValueError("UnknownCard blocks must be a list")
        for block in blocks:
            validate_primitive_block(block)
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError("UnknownCard actions must be a list")
    if strict_actions:
        for action in actions:
            validate_action_ref(action)
    _validate_optional_action_selection(card, strict_actions=strict_actions)


def validate_generic_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_fields(card, GENERIC_CARD_TYPE, _GENERIC_CARD_FIELDS)
    if card.get("type") != GENERIC_CARD_TYPE:
        raise ValueError("Card type must be GenericCard")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("GenericCard title is required")
    if title != title.strip():
        raise ValueError("GenericCard title must be normalized")
    if "subtitle" in card:
        subtitle = card["subtitle"]
        if not isinstance(subtitle, str) or not subtitle.strip():
            raise ValueError("GenericCard subtitle must be a non-empty string")
        if subtitle != subtitle.strip():
            raise ValueError("GenericCard subtitle must be normalized")
    blocks = card.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("GenericCard blocks must be a list")
    if not blocks:
        raise ValueError("GenericCard blocks must not be empty")
    for block in blocks:
        validate_primitive_block(block)
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError("GenericCard actions must be a list")
    if strict_actions:
        for action in actions:
            validate_action_ref(action)
    _validate_optional_action_selection(card, strict_actions=strict_actions)


def build_generic_card(
    *,
    title: str,
    blocks: list[dict[str, Any]],
    subtitle: str | None = None,
    actions: list[dict[str, Any]] | None = None,
    debug: Any = None,
) -> dict[str, Any]:
    """Construct and validate a GenericCard from engine-provided content blocks.

    Provides a typed builder symmetrical with ``build_retrieval_results_card``,
    ``build_basket_card``, ``build_context_set_card``, and ``build_proposed_edit_card``
    so that engine code and the future Textual client have a single authoritative
    construction path for GenericCard payloads.

    ``blocks`` must be a non-empty list of validated primitive block dicts
    (e.g. ``{"type": "MarkdownBlock", "markdown": "..."}``).
    Raises ValueError if the constructed card fails validation.
    """
    card: dict[str, Any] = {
        "type": GENERIC_CARD_TYPE,
        "title": title,
        "blocks": list(blocks),
    }
    if subtitle is not None:
        card["subtitle"] = subtitle
    if actions is not None:
        card["actions"] = list(actions)
    if debug is not None:
        card["debug"] = debug
    validate_generic_card(card)
    return card


def build_retrieval_results_card(
    *,
    title: str,
    query: str,
    results: list[dict[str, Any]],
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Construct and validate a RetrievalResultsCard from engine-provided FTS results.

    Each result must have at minimum ``item_id``, ``title``, and ``snippet``.
    Optional fields ``score`` (int or float) and ``source_ref`` (str) are forwarded as-is.
    Raises ValueError if the constructed card fails validation.
    """
    card: dict[str, Any] = {
        "type": RETRIEVAL_RESULTS_CARD_TYPE,
        "title": title,
        "query": query,
        "results": list(results),
    }
    if actions is not None:
        card["actions"] = list(actions)
    validate_retrieval_results_card(card)
    return card


def build_basket_card(
    *,
    title: str,
    items: list[dict[str, Any]],
    basket_id: str | None = None,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Construct and validate a BasketCard from engine-provided basket items.

    Each item must have at minimum ``item_id`` and ``title``.
    Raises ValueError if the constructed card fails validation.
    """
    card: dict[str, Any] = {
        "type": BASKET_CARD_TYPE,
        "title": title,
        "items": list(items),
    }
    if basket_id is not None:
        card["basket_id"] = basket_id
    if actions is not None:
        card["actions"] = list(actions)
    validate_basket_card(card)
    return card


def build_context_set_card(
    *,
    title: str,
    context_set_id: str,
    items: list[dict[str, Any]],
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Construct and validate a ContextSetCard from engine-provided context items.

    Each item must have at minimum ``item_id`` and ``title``.
    Raises ValueError if the constructed card fails validation.
    """
    card: dict[str, Any] = {
        "type": CONTEXT_SET_CARD_TYPE,
        "title": title,
        "context_set_id": context_set_id,
        "items": list(items),
    }
    if actions is not None:
        card["actions"] = list(actions)
    validate_context_set_card(card)
    return card


def build_proposed_edit_card(
    *,
    patch_id: str,
    title: str,
    blocks: list[dict[str, Any]],
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Construct and validate a ProposedEditCard from engine-provided patch data.

    Canonical patch-review actions (preview, apply, reject) are always injected
    by materialize_proposed_edit_card; callers should pass raw engine actions here
    and let the materializer canonicalize the action set before rendering.
    Raises ValueError if the constructed card fails validation.
    """
    if not isinstance(patch_id, str) or patch_id != patch_id.strip():
        raise ValueError("ProposedEditCard patch_id must be normalized (no leading/trailing whitespace)")
    card: dict[str, Any] = {
        "type": PROPOSED_EDIT_CARD_TYPE,
        "patch_id": patch_id,
        "title": title,
        "blocks": list(blocks),
    }
    if actions is not None:
        card["actions"] = list(actions)
    validate_proposed_edit_card(card, strict_actions=False)
    return card


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
    _validate_card_fields(card, PROPOSED_EDIT_CARD_TYPE, _PROPOSED_EDIT_CARD_FIELDS)
    if card.get("type") != PROPOSED_EDIT_CARD_TYPE:
        raise ValueError("Card type must be ProposedEditCard")
    patch_id = card.get("patch_id")
    if not isinstance(patch_id, str) or not patch_id.strip():
        raise ValueError("ProposedEditCard patch_id is required")
    if strict_actions:
        _validate_card_identifier(patch_id, "patch_id", PROPOSED_EDIT_CARD_TYPE)
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("ProposedEditCard title is required")
    if title != title.strip():
        raise ValueError("ProposedEditCard title must be normalized")
    blocks = card.get("blocks")
    if not isinstance(blocks, list):
        raise ValueError("ProposedEditCard blocks must be a list")
    if not blocks:
        raise ValueError("ProposedEditCard blocks must not be empty")
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
            if not isinstance(action_patch_id, str) or action_patch_id.strip() != expected_patch_id:
                raise ValueError(f"{action_id} payload patch_id must match ProposedEditCard patch_id")
        if strict_actions:
            validate_action_ref(action)
    _validate_optional_action_selection(card, strict_actions=strict_actions)


def validate_known_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    if not isinstance(card, dict):
        raise ValueError("Card must be a dictionary")
    card_type = str(card.get("type", "")).strip()
    validator = _VALIDATORS_BY_CARD_TYPE.get(card_type)
    if validator is None:
        raise ValueError(f"Unsupported known A2UI card type: {card_type}")
    validator(card, strict_actions=strict_actions)



def validate_retrieval_results_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_fields(card, RETRIEVAL_RESULTS_CARD_TYPE, _RETRIEVAL_RESULTS_CARD_FIELDS)
    _validate_card_title(card, RETRIEVAL_RESULTS_CARD_TYPE)
    query = card.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("RetrievalResultsCard query is required")
    if query != query.strip():
        raise ValueError("RetrievalResultsCard query must be normalized")
    results = card.get("results")
    if not isinstance(results, list):
        raise ValueError("RetrievalResultsCard results must be a list")
    for result in results:
        _validate_typed_mapping(
            result,
            "RetrievalResultsCard result",
            required_fields={"item_id": str, "title": str, "snippet": str},
            optional_fields={"score": (int, float), "source_ref": str},
        )
        _validate_item_identifier(result, "RetrievalResultsCard result")
        _validate_item_title(result, "RetrievalResultsCard result")
        if "source_ref" in result:
            source_ref = result["source_ref"]
            if source_ref != source_ref.strip():
                raise ValueError("RetrievalResultsCard result source_ref must be normalized")
    _validate_unique_item_ids(results, "RetrievalResultsCard result")
    _validate_optional_card_actions(card, strict_actions=strict_actions)
    _validate_item_scoped_actions(card, results, "RetrievalResultsCard result")


def validate_basket_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_fields(card, BASKET_CARD_TYPE, _BASKET_CARD_FIELDS)
    _validate_card_title(card, BASKET_CARD_TYPE)
    _validate_optional_card_identifier(card, "basket_id", BASKET_CARD_TYPE)
    items = card.get("items")
    if not isinstance(items, list):
        raise ValueError("BasketCard items must be a list")
    for item in items:
        _validate_typed_mapping(
            item,
            "BasketCard item",
            required_fields={"item_id": str, "title": str},
        )
        _validate_item_identifier(item, "BasketCard item")
        _validate_item_title(item, "BasketCard item")
    _validate_unique_item_ids(items, "BasketCard item")
    _validate_optional_card_actions(card, strict_actions=strict_actions)
    _validate_item_scoped_actions(card, items, "BasketCard item")
    _validate_basket_scoped_actions(card)


def validate_context_set_card(card: dict[str, Any], *, strict_actions: bool = True) -> None:
    _validate_card_fields(card, CONTEXT_SET_CARD_TYPE, _CONTEXT_SET_CARD_FIELDS)
    _validate_card_title(card, CONTEXT_SET_CARD_TYPE)
    context_set_id = card.get("context_set_id")
    if not isinstance(context_set_id, str) or not context_set_id.strip():
        raise ValueError("ContextSetCard context_set_id is required")
    _validate_card_identifier(context_set_id, "context_set_id", CONTEXT_SET_CARD_TYPE)
    items = card.get("items")
    if not isinstance(items, list):
        raise ValueError("ContextSetCard items must be a list")
    for item in items:
        _validate_typed_mapping(
            item,
            "ContextSetCard item",
            required_fields={"item_id": str, "title": str},
        )
        _validate_item_identifier(item, "ContextSetCard item")
        _validate_item_title(item, "ContextSetCard item")
    _validate_unique_item_ids(items, "ContextSetCard item")
    _validate_optional_card_actions(card, strict_actions=strict_actions)
    _validate_item_scoped_actions(card, items, "ContextSetCard item")
    _validate_context_set_scoped_actions(card, context_set_id.strip())


def validate_primitive_block(block: Any) -> None:
    if not isinstance(block, dict):
        raise ValueError("Primitive block must be an object")
    block_type = str(block.get("type", ""))
    if block_type not in _PRIMITIVE_BLOCK_SET:
        raise ValueError(f"Unsupported primitive block: {block_type}")
    required_fields = _PRIMITIVE_BLOCK_REQUIRED_FIELDS[block_type]
    allowed_fields = _ALLOWED_BLOCK_FIELDS[block_type]
    unexpected_fields = set(block) - allowed_fields
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported field(s) for primitive block '{block_type}': {field_list}")
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

    if block_type == "KeyValueBlock":
        items = block["items"]
        seen_keys = set()
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"KeyValueBlock item at index {idx} must be an object")
            if "key" not in item:
                raise ValueError(f"KeyValueBlock item at index {idx} must contain 'key'")
            key = item["key"]
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"KeyValueBlock item at index {idx} 'key' must be a non-empty string")
            if key != key.strip():
                raise ValueError(f"KeyValueBlock item at index {idx} 'key' must be normalized")
            normalized_key = key.strip()
            if normalized_key in seen_keys:
                raise ValueError(f"KeyValueBlock contains duplicate key: {normalized_key}")
            seen_keys.add(normalized_key)
            if "value" in item:
                val = item["value"]
                if not isinstance(val, (str, int, float, bool, type(None))):
                    raise ValueError(f"KeyValueBlock item at index {idx} 'value' must be primitive or null")

    elif block_type == "ListBlock":
        items = block["items"]
        for idx, item in enumerate(items):
            if not isinstance(item, (str, dict)):
                raise ValueError(f"ListBlock item at index {idx} must be a string or object")
            if isinstance(item, dict):
                if "label" not in item:
                    raise ValueError(f"ListBlock object item at index {idx} must contain 'label'")
                label = item["label"]
                if not isinstance(label, str) or not label.strip():
                    raise ValueError(f"ListBlock object item at index {idx} 'label' must be a non-empty string")
                if label != label.strip():
                    raise ValueError(f"ListBlock object item at index {idx} 'label' must be normalized")
            else:
                if not item.strip():
                    raise ValueError(f"ListBlock item at index {idx} must be a non-empty string")
                if item != item.strip():
                    raise ValueError(f"ListBlock item at index {idx} must be normalized")

    elif block_type == "TableBlock":
        columns = block["columns"]
        if not columns:
            raise ValueError("TableBlock columns list cannot be empty")
        for idx, col in enumerate(columns):
            if not isinstance(col, (str, int, float, bool)):
                raise ValueError(f"TableBlock column at index {idx} must be a primitive value")
            if isinstance(col, str):
                if not col.strip():
                    raise ValueError(f"TableBlock column at index {idx} must be a non-empty string")
                if col != col.strip():
                    raise ValueError(f"TableBlock column at index {idx} must be normalized")
        rows = block["rows"]
        for r_idx, row in enumerate(rows):
            if not isinstance(row, list):
                raise ValueError(f"TableBlock row at index {r_idx} must be a list")
            if len(row) != len(columns):
                raise ValueError(f"TableBlock row at index {r_idx} length {len(row)} must match columns length {len(columns)}")
            for c_idx, val in enumerate(row):
                if not isinstance(val, (str, int, float, bool, type(None))):
                    raise ValueError(f"TableBlock row {r_idx} value at index {c_idx} must be primitive or null")
                if isinstance(val, str):
                    if val != val.strip():
                        raise ValueError(f"TableBlock row {r_idx} value at index {c_idx} must be normalized")

    elif block_type == "AlertBlock":
        message = block["message"]
        if message != message.strip():
            raise ValueError("AlertBlock field 'message' must be normalized")
        if "severity" in block:
            severity = block["severity"]
            if not isinstance(severity, str) or not severity.strip():
                raise ValueError("AlertBlock field 'severity' must be a non-empty string")
            if severity != severity.strip():
                raise ValueError("AlertBlock field 'severity' must be normalized")
            if severity not in {"info", "warning", "error", "success"}:
                raise ValueError("AlertBlock field 'severity' must be one of 'info', 'warning', 'error', 'success'")

    elif block_type == "ProgressBlock":
        title = block["title"]
        if title != title.strip():
            raise ValueError("ProgressBlock field 'title' must be normalized")
        status_text = block["status_text"]
        if status_text != status_text.strip():
            raise ValueError("ProgressBlock field 'status_text' must be normalized")
        if "percentage" in block:
            percentage = block["percentage"]
            if isinstance(percentage, bool) or not isinstance(percentage, (int, float)):
                raise ValueError("ProgressBlock field 'percentage' must be an integer or float")
            if not (0.0 <= percentage <= 100.0):
                raise ValueError("ProgressBlock field 'percentage' must be between 0.0 and 100.0")

    elif block_type == "CodeBlock":
        language = block["language"]
        if language != language.strip():
            raise ValueError("CodeBlock field 'language' must be normalized")
        if "collapsed" in block:
            collapsed = block["collapsed"]
            if not isinstance(collapsed, bool):
                raise ValueError("CodeBlock field 'collapsed' must be a boolean")



def _validate_card_title(card: dict[str, Any], card_type: str) -> None:
    if card.get("type") != card_type:
        raise ValueError(f"Card type must be {card_type}")
    title = card.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"{card_type} title is required")
    if title != title.strip():
        raise ValueError(f"{card_type} title must be normalized")


def _validate_card_fields(card: dict[str, Any], card_type: str, allowed_fields: frozenset[str]) -> None:
    if not isinstance(card, dict):
        raise ValueError(f"{card_type} must be a dictionary")
    unexpected_fields = set(card) - allowed_fields
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported {card_type} field(s): {field_list}")



def _validate_optional_card_identifier(card: dict[str, Any], field_name: str, card_type: str) -> None:
    if field_name not in card:
        return
    value = card[field_name]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{card_type} {field_name} is required")
    _validate_card_identifier(value, field_name, card_type)


def _validate_card_identifier(value: str, field_name: str, card_type: str) -> None:
    if value != value.strip():
        raise ValueError(f"{card_type} {field_name} must be normalized")


def _validate_typed_mapping(
    value: Any,
    label: str,
    *,
    required_fields: dict[str, type],
    optional_fields: dict[str, type | tuple[type, ...]] | None = None,
) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    allowed = set(required_fields) | set(optional_fields or {})
    unexpected_fields = set(value) - allowed
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported {label} field(s): {field_list}")
    for field_name, field_type in required_fields.items():
        field_value = value.get(field_name)
        allowed_types = field_type if isinstance(field_type, tuple) else (field_type,)
        if isinstance(field_value, bool) and bool not in allowed_types:
            raise ValueError(f"{label} field '{field_name}' must be {field_type.__name__}")
        if not isinstance(field_value, field_type):
            raise ValueError(f"{label} field '{field_name}' must be {field_type.__name__}")
        if field_type is str and not field_value.strip():
            raise ValueError(f"{label} field '{field_name}' is required")
    for field_name, field_type in (optional_fields or {}).items():
        if field_name not in value:
            continue
        field_value = value[field_name]
        allowed_types = field_type if isinstance(field_type, tuple) else (field_type,)
        type_name = field_type.__name__ if isinstance(field_type, type) else " or ".join(t.__name__ for t in field_type)
        if isinstance(field_value, bool) and bool not in allowed_types:
            raise ValueError(f"{label} optional field '{field_name}' must be {type_name}")
        if not isinstance(field_value, field_type):
            raise ValueError(f"{label} optional field '{field_name}' must be {type_name}")



def _validate_unique_item_ids(items: list[Any], item_label: str) -> None:
    seen_item_ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("item_id")
        if not isinstance(item_id, str):
            continue
        normalized_item_id = item_id.strip()
        if normalized_item_id in seen_item_ids:
            raise ValueError(f"{item_label} item_id entries must be unique: {normalized_item_id}")
        seen_item_ids.add(normalized_item_id)


def _validate_item_identifier(item: dict[str, Any], item_label: str) -> None:
    item_id = item["item_id"]
    if item_id != item_id.strip():
        raise ValueError(f"{item_label} item_id must be normalized")


def _validate_item_title(item: dict[str, Any], item_label: str) -> None:
    title = item["title"]
    if title != title.strip():
        raise ValueError(f"{item_label} title must be normalized")


def _validate_optional_card_actions(card: dict[str, Any], *, strict_actions: bool) -> None:
    actions = card.get("actions", [])
    if not isinstance(actions, list):
        raise ValueError(f"{card.get('type')} actions must be a list")
    if strict_actions:
        for action in actions:
            validate_action_ref(action)
    _validate_optional_action_selection(card, strict_actions=strict_actions)


def _validate_optional_action_selection(card: dict[str, Any], *, strict_actions: bool) -> None:
    if not strict_actions or "action_selection" not in card:
        return
    selection = card["action_selection"]
    if not isinstance(selection, dict):
        raise ValueError(f"{card.get('type')} action_selection must be an object")
    expected = materialize_action_selection_contract(card)
    if selection != expected:
        raise ValueError(f"{card.get('type')} action_selection must match materialized actions")


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


def _validate_basket_scoped_actions(card: dict[str, Any]) -> None:
    basket_id = card.get("basket_id")
    for action in card.get("actions", []):
        if not isinstance(action, dict) or action.get("id") != "gather_context":
            continue
        payload = action.get("payload")
        action_basket_id = payload.get("basket_id") if isinstance(payload, dict) else None
        if not isinstance(action_basket_id, str) or not action_basket_id.strip():
            continue
        if not isinstance(basket_id, str) or not basket_id.strip():
            raise ValueError("gather_context requires BasketCard basket_id")
        if action_basket_id.strip() != basket_id.strip():
            raise ValueError("gather_context basket_id must match BasketCard basket_id")


def _validate_context_set_scoped_actions(card: dict[str, Any], context_set_id: str) -> None:
    for action in card.get("actions", []):
        if not isinstance(action, dict) or action.get("id") != "pin_to_context_set":
            continue
        payload = action.get("payload")
        action_context_set_id = payload.get("context_set_id") if isinstance(payload, dict) else None
        if not isinstance(action_context_set_id, str) or not action_context_set_id.strip():
            continue
        if action_context_set_id.strip() != context_set_id:
            raise ValueError("pin_to_context_set context_set_id must match ContextSetCard context_set_id")


def _is_same_patch_review_action(action: dict[str, Any], patch_id: str) -> bool:
    if action.get("id") not in {"preview_patch", "apply_patch", "reject_patch"}:
        return False
    payload = action.get("payload")
    action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
    return isinstance(action_patch_id, str) and action_patch_id.strip() == patch_id


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
        if not capabilities.supports_action(action.get("id")):
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
    filtered["actions"] = [
        action
        for action in materialize_card_actions(card)
        if capabilities.supports_action(action.get("id"))
    ]
    return filtered


def _engine_fallback_actions(
    card: dict[str, Any],
    capabilities: A2UICapabilities,
) -> list[dict[str, Any]]:
    return _engine_filter_actions(card, capabilities)["actions"]
