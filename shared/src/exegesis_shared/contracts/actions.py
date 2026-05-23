from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import json
from typing import Any, Callable, Protocol

ACTION_SELECTION_CONTRACT_VERSION = 1
PATCH_DECISION_CONTRACT_VERSION = 1
PATCH_REVIEW_CONTRACT_VERSION = 1
ALLOWED_ACTION_IDS: tuple[str, ...] = (
    "preview_patch",
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "promote_to_basket",
    "pin_to_context_set",
    "create_context_set",
    "gather_context",
    "run_agent",
    "refresh_license",
    "export_document",
    "copy_to_clipboard",
)
PATCH_DECISION_ACTION_IDS: tuple[str, ...] = ("apply_patch", "reject_patch")
PATCH_DECISION_BY_ACTION_ID: dict[str, str] = {
    "apply_patch": "apply",
    "reject_patch": "reject",
}
PATCH_PREVIEW_CONTRACT_VERSION = 1
PATCH_REVIEW_FLOW = "preview_then_decide"
PATCH_REVIEW_DECISION_POLICY = "apply_or_reject"
PATCH_REVIEW_DECISION_GROUP = "patch_terminal_decision"
PATCH_REVIEW_ACTION_AUTHORITY = "engine_revalidated"
PATCH_REVIEW_DEMO_PATH_STEP = "preview_apply_or_reject_patch"
PATCH_REVIEW_EXECUTION_POLICY: dict[str, dict[str, Any]] = {
    "preview": {
        "policy_gate": "optional",
        "requires_confirmation": False,
        "requires_preview": False,
        "mutates_patch": False,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
    },
    "apply": {
        "policy_gate": "required",
        "requires_confirmation": True,
        "requires_preview": True,
        "mutates_patch": True,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
    },
    "reject": {
        "policy_gate": "required",
        "requires_confirmation": True,
        "requires_preview": True,
        "mutates_patch": True,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
    },
}
PATCH_REVIEW_EXECUTION_PRECONDITIONS: dict[str, dict[str, bool]] = {
    control: {
        "requires_preview": bool(policy["requires_preview"]),
        "requires_confirmation": bool(policy["requires_confirmation"]),
        "requires_policy_gate": policy["policy_gate"] == "required",
    }
    for control, policy in PATCH_REVIEW_EXECUTION_POLICY.items()
}
PATCH_REVIEW_CONFIRMATION_TITLES: dict[str, str] = {
    "apply_patch": "Apply patch?",
    "reject_patch": "Reject patch?",
}
PATCH_REVIEW_REQUIRED_PARTS: tuple[str, ...] = ("preview", "apply", "reject")
PATCH_REVIEW_CLI_COMMAND_ALIASES: dict[str, tuple[str, ...]] = {
    "preview": ("preview", "preview_patch"),
    "apply": ("apply", "apply_patch"),
    "reject": ("reject", "reject_patch"),
}
PATCH_REVIEW_CONTROL_KINDS: dict[str, str] = {
    "preview": "preview",
    "apply": "decision",
    "reject": "decision",
}
PATCH_REVIEW_RESOLVED_STATUSES: dict[str, str] = {
    "preview": "previewed",
    "apply": "applied",
    "reject": "rejected",
}
ENGINE_NORMALIZED_ACTION_PAYLOAD_FIELDS: dict[str, tuple[str, ...]] = {
    "preview_patch": ("patch_id",),
    "apply_patch": ("patch_id",),
    "reject_patch": ("patch_id",),
    "open_section": ("section_id",),
    "open_corpus_item": ("item_id",),
    "promote_to_basket": ("item_id",),
    "pin_to_context_set": ("item_id", "context_set_id"),
    "create_context_set": ("name",),
    "gather_context": ("basket_id", "context_set_id"),
    "run_agent": ("operation",),
    "export_document": ("format",),
}

CANONICAL_ACTION_ORDER: tuple[str, ...] = (
    "preview_patch",
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "promote_to_basket",
    "pin_to_context_set",
    "create_context_set",
    "gather_context",
    "copy_to_clipboard",
    "export_document",
    "refresh_license",
    "run_agent",
)
CANONICAL_ACTION_PRIORITY: dict[str, int] = {
    action_id: index for index, action_id in enumerate(CANONICAL_ACTION_ORDER)
}
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)
POLICY_SENSITIVE_ACTION_IDS: tuple[str, ...] = (
    "apply_patch",
    "reject_patch",
    "run_agent",
    "refresh_license",
    "export_document",
)
_POLICY_SENSITIVE_ACTION_SET = set(POLICY_SENSITIVE_ACTION_IDS)
if set(CANONICAL_ACTION_ORDER) != _ALLOWED_ACTION_SET:
    raise RuntimeError("A2UI canonical action order must match allowed action IDs")

_ACTION_SCHEMAS: dict[str, dict[str, type]] = {
    "preview_patch": {"patch_id": str},
    "apply_patch": {"patch_id": str},
    "reject_patch": {"patch_id": str},
    "open_section": {"section_id": str},
    "open_corpus_item": {"item_id": str},
    "promote_to_basket": {"item_id": str},
    "pin_to_context_set": {"item_id": str, "context_set_id": str},
    "create_context_set": {"name": str},
    "gather_context": {"basket_id": str, "context_set_id": str},
    "run_agent": {"operation": str},
    "refresh_license": {},
    "export_document": {"format": str},
    "copy_to_clipboard": {"text": str},
}
_ACTION_REF_FIELDS: frozenset[str] = frozenset(
    {"id", "label", "payload", "confirm", "policy_sensitive"}
)
_ACTION_SELECTION_FIELDS: frozenset[str] = frozenset(
    {"contract_version", "selection_model", "slot", "action_identity"}
)
_PATCH_PREVIEW_SELECTION_FIELDS: frozenset[str] = _ACTION_SELECTION_FIELDS | frozenset(
    {
        "action_authority",
        "demo_path_step",
        "execution_policy",
        "patch_preview_contract_version",
        "patch_id",
    }
)
_PATCH_DECISION_SELECTION_FIELDS: frozenset[str] = _ACTION_SELECTION_FIELDS | frozenset(
    {
        "action_authority",
        "demo_path_step",
        "execution_policy",
        "patch_decision_contract_version",
        "decision_group",
        "patch_decision",
        "patch_id",
    }
)
_PATCH_REVIEW_SELECTION_FIELDS: frozenset[str] = (
    _PATCH_PREVIEW_SELECTION_FIELDS | _PATCH_DECISION_SELECTION_FIELDS
)
_PATCH_REVIEW_CONTRACT_FIELDS: frozenset[str] = frozenset(
    {
        "contract_version",
        "patch_id",
        "flow",
        "decision_policy",
        "action_authority",
        "demo_path_step",
        "execution_policy",
        "preview",
        "decisions",
        "availability",
    }
)
_PATCH_REVIEW_DECISION_ENTRY_FIELDS: frozenset[str] = frozenset(
    {"decision", "slot", "action_id", "action_identity", "selection"}
)
_PATCH_REVIEW_AVAILABILITY_FIELDS: frozenset[str] = frozenset(
    {
        "contract_version",
        "patch_id",
        "flow",
        "decision_policy",
        "action_authority",
        "demo_path_step",
        "required",
        "available",
        "missing",
        "next_required",
        "is_complete",
    }
)


@dataclass(frozen=True)
class ActionRef:
    id: str
    label: str
    payload: dict[str, Any]
    confirm: dict[str, str] | None = None
    policy_sensitive: bool = False

    def __post_init__(self) -> None:
        validate_action_ref(self.as_contract())

    def as_contract(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "label": self.label,
            "payload": deepcopy(self.payload),
        }
        if self.confirm is not None:
            payload["confirm"] = deepcopy(self.confirm)
        if self.policy_sensitive:
            payload["policy_sensitive"] = True
        return payload


@dataclass(frozen=True)
class PatchReviewActionSelection:
    kind: str
    patch_id: str
    action: ActionRef
    decision: str | None = None

    def __post_init__(self) -> None:
        expected_patch_id = self.patch_id.strip()
        if not expected_patch_id:
            raise ValueError("Patch review patch_id is required")
        if expected_patch_id != self.patch_id:
            raise ValueError("Patch review patch_id must be normalized")
        if self.kind == "preview":
            if self.decision is not None:
                raise ValueError("Patch preview selection must not include a decision")
            if self.action.id != "preview_patch":
                raise ValueError("Patch preview selection must use preview_patch")
        elif self.kind == "decision":
            if self.decision not in {"apply", "reject"}:
                raise ValueError("Patch review decision must be 'apply' or 'reject'")
            expected_action_id = "apply_patch" if self.decision == "apply" else "reject_patch"
            if self.action.id != expected_action_id:
                raise ValueError("Patch review decision does not match the selected action")
        else:
            raise ValueError("Patch review kind must be 'preview' or 'decision'")
        if self.action.payload.get("patch_id") != expected_patch_id:
            raise ValueError("Patch review action does not match the current patch")

    def as_contract(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
            "kind": self.kind,
            "patch_id": self.patch_id,
            "flow": PATCH_REVIEW_FLOW,
            "decision_policy": PATCH_REVIEW_DECISION_POLICY,
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "action": self.action.as_contract(),
        }
        if self.kind == "decision":
            payload["decision"] = self.decision
        return payload


@dataclass(frozen=True)
class CompletePatchReviewActions:
    patch_id: str
    preview: ActionRef
    apply: ActionRef
    reject: ActionRef

    def __post_init__(self) -> None:
        expected_patch_id = self.patch_id.strip()
        if not expected_patch_id:
            raise ValueError("Patch review patch_id is required")
        if expected_patch_id != self.patch_id:
            raise ValueError("Patch review patch_id must be normalized")
        object.__setattr__(
            self,
            "preview",
            _validate_patch_review_control_action(
                "preview",
                self.preview,
                expected_patch_id,
                expected_action_id="preview_patch",
            ),
        )
        object.__setattr__(
            self,
            "apply",
            _validate_patch_review_control_action(
                "apply",
                self.apply,
                expected_patch_id,
                expected_action_id="apply_patch",
            ),
        )
        object.__setattr__(
            self,
            "reject",
            _validate_patch_review_control_action(
                "reject",
                self.reject,
                expected_patch_id,
                expected_action_id="reject_patch",
            ),
        )

    def as_contract(self) -> dict[str, Any]:
        return {
            "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
            "patch_id": self.patch_id,
            "flow": PATCH_REVIEW_FLOW,
            "decision_policy": PATCH_REVIEW_DECISION_POLICY,
            "decision_group": PATCH_REVIEW_DECISION_GROUP,
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY),
            "preview": self.preview.as_contract(),
            "decisions": {
                "apply": self.apply.as_contract(),
                "reject": self.reject.as_contract(),
            },
        }


class PolicyGate(Protocol):
    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        ...


def validate_action_capabilities(capabilities: Any) -> None:
    actions_supported = getattr(capabilities, "actions_supported", None)
    if not isinstance(actions_supported, tuple):
        raise ValueError("actions_supported must be a tuple")
    seen: set[str] = set()
    for action_id in actions_supported:
        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError("actions_supported entries must be non-empty strings")
        if action_id not in _ALLOWED_ACTION_SET:
            raise ValueError(f"Unknown action in capabilities: {action_id}")
        if action_id in seen:
            raise ValueError(f"actions_supported entries must be unique: {action_id}")
        seen.add(action_id)


def validate_complete_patch_review_capabilities(capabilities: Any) -> None:
    validate_action_capabilities(capabilities)
    supported_actions = set(capabilities.actions_supported)
    missing = [
        control
        for control in PATCH_REVIEW_REQUIRED_PARTS
        for action_id in PATCH_REVIEW_CLI_COMMAND_ALIASES[control]
        if action_id.endswith("_patch") and action_id not in supported_actions
    ]
    if missing:
        raise ValueError(f"Complete patch review client support is missing: {', '.join(missing)}")


def patch_review_execution_preconditions(control: str) -> dict[str, bool]:
    normalized_control = control.strip().lower()
    if normalized_control not in set(PATCH_REVIEW_REQUIRED_PARTS):
        raise ValueError("Patch review control must be 'preview', 'apply', or 'reject'")
    return deepcopy(PATCH_REVIEW_EXECUTION_PRECONDITIONS[normalized_control])


def patch_review_resolved_status(control: str) -> str:
    normalized_control = control.strip().lower()
    if normalized_control not in set(PATCH_REVIEW_REQUIRED_PARTS):
        raise ValueError("Patch review control must be 'preview', 'apply', or 'reject'")
    return PATCH_REVIEW_RESOLVED_STATUSES[normalized_control]


def canonical_action_key(action: dict[str, Any]) -> str:
    return json.dumps(action, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def canonical_action_identity_key(action: dict[str, Any]) -> str:
    identity = {
        "confirm": action.get("confirm"),
        "id": action.get("id"),
        "payload": action.get("payload"),
        "policy_sensitive": action.get("policy_sensitive", False),
    }
    return json.dumps(identity, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def action_priority(action: dict[str, Any]) -> tuple[int, str, str, str]:
    action_id = str(action.get("id", ""))
    priority = CANONICAL_ACTION_PRIORITY.get(action_id, len(CANONICAL_ACTION_ORDER))
    return (priority, action_id, canonical_action_identity_key(action), canonical_action_key(action))


def canonicalize_action_order(actions: list[Any]) -> list[dict[str, Any]]:
    valid_actions: list[dict[str, Any]] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        valid_actions.append(action)
    return [deepcopy(action) for action in sorted(valid_actions, key=action_priority)]


def materialize_card_actions(card: dict[str, Any]) -> list[dict[str, Any]]:
    raw_actions = card.get("actions", [])
    if not isinstance(raw_actions, list):
        return []

    by_identity: dict[str, dict[str, Any]] = {}
    for action in raw_actions:
        if not isinstance(action, dict):
            continue
        try:
            validate_action_ref(action)
        except ValueError:
            continue
        action = _materialize_engine_authoritative_action(action)
        identity_key = canonical_action_identity_key(action)
        current = by_identity.get(identity_key)
        if current is None or canonical_action_key(action) < canonical_action_key(current):
            by_identity[identity_key] = deepcopy(action)
    return canonicalize_action_order(list(by_identity.values()))


def _materialize_engine_authoritative_action(action: dict[str, Any]) -> dict[str, Any]:
    confirm = action.get("confirm")
    action_ref = ActionRef(
        id=str(action["id"]),
        label=str(action["label"]),
        payload=deepcopy(action["payload"]),
        confirm=deepcopy(confirm) if isinstance(confirm, dict) else None,
        policy_sensitive=action.get("policy_sensitive", False),
    )
    return engine_authoritative_action_ref(action_ref).as_contract()


def _validate_patch_review_control_action(
    control: str,
    action: ActionRef,
    expected_patch_id: str,
    *,
    expected_action_id: str,
) -> ActionRef:
    action = engine_authoritative_action_ref(action)
    if action.id != expected_action_id:
        raise ValueError(f"Patch review {control} control must use {expected_action_id}")
    if action.payload.get("patch_id") != expected_patch_id:
        raise ValueError(f"Patch review {control} control must match the current patch")
    if control in {"apply", "reject"}:
        expected_confirm = {"title": PATCH_REVIEW_CONFIRMATION_TITLES[expected_action_id]}
        if action.confirm != expected_confirm or action.policy_sensitive is not True:
            raise ValueError(
                f"Patch review {control} control must be engine-authoritative and policy-gated"
            )
    return action


def materialize_action_selection_contract(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
        "selection_model": "one_based_action_slot",
        "order": [
            {
                "slot": slot,
                "action_id": str(action["id"]),
                "action_identity": canonical_action_identity_key(action),
            }
            for slot, action in enumerate(materialize_card_actions(card), start=1)
        ],
    }


def materialize_patch_decision_contract(card: dict[str, Any], patch_id: str) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch decision patch_id is required")

    decisions: list[dict[str, Any]] = []
    for slot, action in enumerate(materialize_card_actions(card), start=1):
        action_id = action.get("id")
        if action_id not in PATCH_DECISION_ACTION_IDS:
            continue
        payload = action.get("payload")
        action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
        if action_patch_id != expected_patch_id:
            continue
        decision = "apply" if action_id == "apply_patch" else "reject"
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": slot,
            "action_identity": canonical_action_identity_key(action),
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY[decision]),
            "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
            "decision_group": PATCH_REVIEW_DECISION_GROUP,
            "patch_decision": decision,
            "patch_id": expected_patch_id,
        }
        decisions.append(
            {
                "decision": decision,
                "slot": slot,
                "action_id": str(action_id),
                "action_identity": canonical_action_identity_key(action),
                "selection": selection,
            }
        )

    return {
        "contract_version": PATCH_DECISION_CONTRACT_VERSION,
        "patch_id": expected_patch_id,
        "decisions": decisions,
    }


def materialize_patch_preview_contract(card: dict[str, Any], patch_id: str) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch preview patch_id is required")

    previews: list[dict[str, Any]] = []
    for slot, action in enumerate(materialize_card_actions(card), start=1):
        if action.get("id") != "preview_patch":
            continue
        payload = action.get("payload")
        action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
        if action_patch_id != expected_patch_id:
            continue
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": slot,
            "action_identity": canonical_action_identity_key(action),
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY["preview"]),
            "patch_preview_contract_version": PATCH_PREVIEW_CONTRACT_VERSION,
            "patch_id": expected_patch_id,
        }
        previews.append(
            {
                "slot": slot,
                "action_id": "preview_patch",
                "action_identity": canonical_action_identity_key(action),
                "selection": selection,
            }
        )

    return {
        "contract_version": PATCH_PREVIEW_CONTRACT_VERSION,
        "patch_id": expected_patch_id,
        "previews": previews,
    }


def materialize_cli_fallback_card(card: dict[str, Any]) -> dict[str, Any]:
    materialized = deepcopy(card)
    materialized["actions"] = materialize_card_actions(card)
    materialized["action_selection"] = materialize_action_selection_contract(card)
    patch_id = card.get("patch_id")
    if isinstance(patch_id, str) and patch_id.strip():
        patch_preview = materialize_patch_preview_contract(materialized, patch_id)
        if patch_preview["previews"]:
            materialized["patch_preview"] = patch_preview
        patch_decision = materialize_patch_decision_contract(materialized, patch_id)
        if patch_decision["decisions"]:
            materialized["patch_decision"] = patch_decision
        try:
            materialized["patch_review"] = build_patch_review_contract(materialized, patch_id=patch_id)
        except ValueError as exc:
            if "not available" not in str(exc):
                raise
        else:
            materialized["patch_review_controls"] = patch_review_control_plan_from_contract(
                materialized,
                materialized["patch_review"],
                patch_id=patch_id,
            )
            try:
                materialized["complete_patch_review_actions"] = complete_patch_review_actions_from_contract(
                    materialized,
                    materialized["patch_review"],
                    patch_id=patch_id,
                ).as_contract()
            except ValueError as exc:
                if "missing" not in str(exc):
                    raise
    return materialized


def build_patch_review_contract(card: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")

    review: dict[str, Any] = {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": expected_patch_id,
        "flow": PATCH_REVIEW_FLOW,
        "decision_policy": PATCH_REVIEW_DECISION_POLICY,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY),
        "preview": None,
        "decisions": [],
    }
    try:
        review["preview"] = build_patch_preview_selection(card, patch_id=expected_patch_id)
    except ValueError as exc:
        if "not available" not in str(exc):
            raise

    for decision in ("apply", "reject"):
        try:
            selection = build_patch_decision_selection(
                card,
                patch_id=expected_patch_id,
                decision=decision,
            )
        except ValueError as exc:
            if "not available" not in str(exc):
                raise
            continue
        review["decisions"].append(
            {
                "decision": decision,
                "slot": selection["slot"],
                "action_id": "apply_patch" if decision == "apply" else "reject_patch",
                "action_identity": selection["action_identity"],
                "selection": selection,
            }
        )

    if review["preview"] is None and not review["decisions"]:
        raise ValueError("Patch review is not available for the current patch")
    review["availability"] = patch_review_availability_from_contract(review)
    return review


def build_complete_patch_review_contract(card: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    review = build_patch_review_contract(card, patch_id=patch_id)
    availability = patch_review_availability_from_contract(review)
    missing = availability["missing"]
    if missing:
        raise ValueError(f"Complete patch review is missing: {', '.join(missing)}")
    return review


def patch_review_availability_from_contract(review: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(review, dict):
        raise ValueError("Patch review contract must be an object")
    _validate_selection_fields(review, _PATCH_REVIEW_CONTRACT_FIELDS, "patch review contract")
    if review.get("contract_version") != PATCH_REVIEW_CONTRACT_VERSION:
        raise ValueError("Unsupported patch review contract version")
    patch_id = review.get("patch_id")
    if not isinstance(patch_id, str) or not patch_id.strip():
        raise ValueError("Patch review patch_id is required")
    if review.get("flow") != PATCH_REVIEW_FLOW:
        raise ValueError("Unsupported patch review flow")
    if review.get("decision_policy") != PATCH_REVIEW_DECISION_POLICY:
        raise ValueError("Unsupported patch review decision policy")
    authority = review.get("action_authority", PATCH_REVIEW_ACTION_AUTHORITY)
    if authority != PATCH_REVIEW_ACTION_AUTHORITY:
        raise ValueError("Unsupported patch review action authority")
    if review.get("demo_path_step") != PATCH_REVIEW_DEMO_PATH_STEP:
        raise ValueError("Unsupported patch review demo path step")
    if review.get("execution_policy") != PATCH_REVIEW_EXECUTION_POLICY:
        raise ValueError("Unsupported patch review execution policy")

    available: list[str] = []
    preview = review.get("preview")
    if (
        isinstance(preview, dict)
        and preview.get("contract_version") == ACTION_SELECTION_CONTRACT_VERSION
        and preview.get("selection_model") == "one_based_action_slot"
        and preview.get("patch_id") == patch_id.strip()
        and preview.get("action_authority") == PATCH_REVIEW_ACTION_AUTHORITY
        and preview.get("demo_path_step") == PATCH_REVIEW_DEMO_PATH_STEP
        and preview.get("execution_policy") == PATCH_REVIEW_EXECUTION_POLICY["preview"]
        and preview.get("patch_preview_contract_version") == PATCH_PREVIEW_CONTRACT_VERSION
    ):
        available.append("preview")

    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("Patch review decisions must be a list")
    decision_names = set()
    for entry in decisions:
        if not isinstance(entry, dict):
            raise ValueError("Patch review decision entry must be an object")
        _validate_selection_fields(
            entry,
            _PATCH_REVIEW_DECISION_ENTRY_FIELDS,
            "patch review decision entry",
        )
        decision = str(entry.get("decision", "")).strip().lower()
        if decision in decision_names:
            raise ValueError("Patch review decision is duplicated")
        selection = entry.get("selection")
        expected_action_id = {"apply": "apply_patch", "reject": "reject_patch"}.get(decision)
        if (
            expected_action_id is not None
            and entry.get("action_id") == expected_action_id
            and isinstance(selection, dict)
            and selection.get("contract_version") == ACTION_SELECTION_CONTRACT_VERSION
            and selection.get("selection_model") == "one_based_action_slot"
            and selection.get("patch_id") == patch_id.strip()
            and selection.get("action_authority") == PATCH_REVIEW_ACTION_AUTHORITY
            and selection.get("demo_path_step") == PATCH_REVIEW_DEMO_PATH_STEP
            and selection.get("execution_policy") == PATCH_REVIEW_EXECUTION_POLICY[decision]
            and selection.get("decision_group", PATCH_REVIEW_DECISION_GROUP) == PATCH_REVIEW_DECISION_GROUP
            and selection.get("patch_decision") == decision
            and selection.get("patch_decision_contract_version") == PATCH_DECISION_CONTRACT_VERSION
            and selection.get("slot") == entry.get("slot")
            and selection.get("action_identity") == entry.get("action_identity")
        ):
            decision_names.add(decision)
    for decision in ("apply", "reject"):
        if decision in decision_names:
            available.append(decision)

    missing = [part for part in PATCH_REVIEW_REQUIRED_PARTS if part not in set(available)]
    next_required = missing[0] if missing else None
    expected = {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": patch_id.strip(),
        "flow": PATCH_REVIEW_FLOW,
        "decision_policy": PATCH_REVIEW_DECISION_POLICY,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "required": list(PATCH_REVIEW_REQUIRED_PARTS),
        "available": available,
        "missing": missing,
        "next_required": next_required,
        "is_complete": not missing,
    }
    return expected


def _validate_patch_review_availability(availability: Any, expected: dict[str, Any]) -> None:
    if not isinstance(availability, dict):
        raise ValueError("Patch review availability must be an object")
    _validate_selection_fields(
        availability,
        _PATCH_REVIEW_AVAILABILITY_FIELDS,
        "patch review availability",
    )
    if availability != expected:
        raise ValueError("Patch review availability does not match the current contract")


def build_patch_review_availability(card: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    review = build_patch_review_contract(card, patch_id=patch_id)
    return patch_review_availability_from_contract(review)


def resolve_patch_review_contract(card: dict[str, Any], review: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    if not isinstance(review, dict):
        raise ValueError("Patch review contract must be an object")
    _validate_selection_fields(review, _PATCH_REVIEW_CONTRACT_FIELDS, "patch review contract")
    if review.get("contract_version") != PATCH_REVIEW_CONTRACT_VERSION:
        raise ValueError("Unsupported patch review contract version")
    if review.get("patch_id") != expected_patch_id:
        raise ValueError("Patch review contract does not match the current patch")
    if review.get("flow") != PATCH_REVIEW_FLOW:
        raise ValueError("Unsupported patch review flow")
    if review.get("decision_policy") != PATCH_REVIEW_DECISION_POLICY:
        raise ValueError("Unsupported patch review decision policy")
    authority = review.get("action_authority", PATCH_REVIEW_ACTION_AUTHORITY)
    if authority != PATCH_REVIEW_ACTION_AUTHORITY:
        raise ValueError("Unsupported patch review action authority")
    if review.get("demo_path_step") != PATCH_REVIEW_DEMO_PATH_STEP:
        raise ValueError("Unsupported patch review demo path step")
    if review.get("execution_policy") != PATCH_REVIEW_EXECUTION_POLICY:
        raise ValueError("Unsupported patch review execution policy")
    resolved: dict[str, Any] = {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": expected_patch_id,
        "flow": PATCH_REVIEW_FLOW,
        "decision_policy": PATCH_REVIEW_DECISION_POLICY,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY),
        "preview": None,
        "decisions": [],
    }
    preview_selection = review.get("preview")
    if preview_selection is not None:
        if not isinstance(preview_selection, dict):
            raise ValueError("Patch review preview selection must be an object")
        resolved["preview"] = resolve_patch_preview_selection(
            card,
            preview_selection,
            patch_id=expected_patch_id,
        )

    seen_decisions: set[str] = set()
    for entry in review.get("decisions", []):
        if not isinstance(entry, dict):
            raise ValueError("Patch review decision entry must be an object")
        _validate_selection_fields(
            entry,
            _PATCH_REVIEW_DECISION_ENTRY_FIELDS,
            "patch review decision entry",
        )
        decision = str(entry.get("decision", "")).strip().lower()
        if decision not in {"apply", "reject"}:
            raise ValueError("Patch review decision must be 'apply' or 'reject'")
        if decision in seen_decisions:
            raise ValueError("Patch review decision is duplicated")
        selection = entry.get("selection")
        if not isinstance(selection, dict):
            raise ValueError("Patch review decision selection must be an object")
        if entry.get("slot") != selection.get("slot"):
            raise ValueError("Patch review decision slot does not match the selection")
        if entry.get("action_identity") != selection.get("action_identity"):
            raise ValueError("Patch review decision action_identity does not match the selection")
        action = resolve_patch_decision_selection(card, selection, patch_id=expected_patch_id)
        if entry.get("action_id") != action.get("id"):
            raise ValueError("Patch review decision action_id does not match the selected action")
        if PATCH_DECISION_BY_ACTION_ID[str(action["id"])] != decision:
            raise ValueError("Patch review decision does not match the selected action")
        seen_decisions.add(decision)
        resolved["decisions"].append({"decision": decision, "action": action})

    if resolved["preview"] is None and not resolved["decisions"]:
        raise ValueError("Patch review is not available for the current patch")
    expected_availability = patch_review_availability_from_contract(review)
    availability = review.get("availability")
    if availability is not None:
        _validate_patch_review_availability(availability, expected_availability)
    return resolved


def validate_patch_review_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
    capabilities: Any | None = None,
    require_complete: bool = False,
) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    if capabilities is not None:
        if require_complete:
            validate_complete_patch_review_capabilities(capabilities)
        else:
            validate_action_capabilities(capabilities)
    resolve_patch_review_contract(card, review, patch_id=expected_patch_id)
    availability = patch_review_availability_from_contract(review)
    if require_complete and availability["missing"]:
        raise ValueError(f"Complete patch review is missing: {', '.join(availability['missing'])}")
    if capabilities is not None:
        supported_actions = set(capabilities.actions_supported)
        controls = patch_review_control_actions_from_contract(
            card,
            review,
            patch_id=expected_patch_id,
        )
        for control, action_payload in controls.items():
            action_id = action_payload.get("action_id")
            if action_id not in supported_actions:
                raise ValueError(f"Patch review {control} action is not supported by client")
    return availability


def patch_review_action_refs_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, ActionRef | None | dict[str, ActionRef]]:
    resolved = resolve_patch_review_contract(card, review, patch_id=patch_id)
    refs: dict[str, ActionRef | None | dict[str, ActionRef]] = {
        "preview": None,
        "decisions": {},
    }
    preview_selection = review.get("preview")
    if resolved["preview"] is not None:
        if not isinstance(preview_selection, dict):
            raise ValueError("Patch review preview selection must be an object")
        refs["preview"] = patch_preview_action_ref_from_selection(
            card,
            preview_selection,
            patch_id=patch_id,
        )

    decision_refs: dict[str, ActionRef] = {}
    review_decisions = review.get("decisions", [])
    if not isinstance(review_decisions, list):
        raise ValueError("Patch review decisions must be a list")
    for entry in review_decisions:
        if not isinstance(entry, dict):
            raise ValueError("Patch review decision entry must be an object")
        decision = str(entry.get("decision", "")).strip().lower()
        selection = entry.get("selection")
        if not isinstance(selection, dict):
            raise ValueError("Patch review decision selection must be an object")
        if decision in {item["decision"] for item in resolved["decisions"]}:
            decision_refs[decision] = patch_decision_action_ref_from_selection(
                card,
                selection,
                patch_id=patch_id,
            )
    refs["decisions"] = decision_refs
    return refs


def patch_review_control_slots_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, dict[str, Any]]:
    resolve_patch_review_contract(card, review, patch_id=patch_id)
    slots: dict[str, dict[str, Any]] = {}
    preview = review.get("preview")
    if isinstance(preview, dict):
        slots["preview"] = {
            "slot": preview["slot"],
            "action_id": "preview_patch",
            "action_identity": preview["action_identity"],
        }

    decisions = review.get("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("Patch review decisions must be a list")
    for entry in decisions:
        if not isinstance(entry, dict):
            raise ValueError("Patch review decision entry must be an object")
        decision = str(entry.get("decision", "")).strip().lower()
        if decision in {"apply", "reject"}:
            slots[decision] = {
                "slot": entry["slot"],
                "action_id": entry["action_id"],
                "action_identity": entry["action_identity"],
            }
    return slots


def patch_review_control_actions_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, dict[str, Any]]:
    slots = patch_review_control_slots_from_contract(card, review, patch_id=patch_id)
    refs = patch_review_action_refs_from_contract(card, review, patch_id=patch_id)
    preview_ref = refs["preview"]
    decision_refs = refs["decisions"]
    if not isinstance(decision_refs, dict):
        raise ValueError("Patch review decisions must be available")

    controls: dict[str, dict[str, Any]] = {}
    selection_by_control: dict[str, dict[str, Any]] = {}
    preview_selection = review.get("preview")
    if isinstance(preview_selection, dict):
        selection_by_control["preview"] = preview_selection
    review_decisions = review.get("decisions", [])
    if not isinstance(review_decisions, list):
        raise ValueError("Patch review decisions must be a list")
    for entry in review_decisions:
        if not isinstance(entry, dict):
            raise ValueError("Patch review decision entry must be an object")
        decision = str(entry.get("decision", "")).strip().lower()
        selection = entry.get("selection")
        if decision in {"apply", "reject"} and isinstance(selection, dict):
            selection_by_control[decision] = selection

    ref_by_control: dict[str, ActionRef | None] = {
        "preview": preview_ref if isinstance(preview_ref, ActionRef) else None,
        "apply": decision_refs.get("apply"),
        "reject": decision_refs.get("reject"),
    }
    for control in ("preview", "apply", "reject"):
        slot = slots.get(control)
        action_ref = ref_by_control.get(control)
        if slot is None or not isinstance(action_ref, ActionRef):
            continue
        action_ref = engine_authoritative_action_ref(action_ref)
        controls[control] = {
            **slot,
            "label": action_ref.label,
            "payload": deepcopy(action_ref.payload),
            "action_contract": action_ref.as_contract(),
            "selection": deepcopy(selection_by_control[control]),
            "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY[control]),
            "confirm": deepcopy(action_ref.confirm),
            "policy_sensitive": action_ref.policy_sensitive,
        }
    return controls


def resolve_patch_review_control_execution(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
    control: str,
    capabilities: Any | None = None,
) -> dict[str, Any]:
    normalized_control = control.strip().lower()
    if normalized_control not in set(PATCH_REVIEW_REQUIRED_PARTS):
        raise ValueError("Patch review control must be 'preview', 'apply', or 'reject'")
    controls = patch_review_control_actions_from_contract(card, review, patch_id=patch_id)
    action_payload = controls.get(normalized_control)
    if not isinstance(action_payload, dict):
        raise ValueError(f"Patch review {normalized_control} is not available for the current patch")
    execution_policy = action_payload.get("execution_policy")
    if execution_policy != PATCH_REVIEW_EXECUTION_POLICY[normalized_control]:
        raise ValueError("Patch review control execution policy does not match engine policy")
    action_contract = action_payload.get("action_contract")
    if not isinstance(action_contract, dict):
        raise ValueError("Patch review control action contract must be an object")
    validate_action_ref(action_contract)
    if capabilities is not None:
        validate_action_capabilities(capabilities)
        action_id = str(action_payload["action_id"])
        if action_id not in set(capabilities.actions_supported):
            raise ValueError(f"Patch review {normalized_control} action is not supported by client")
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": patch_id.strip(),
        "control": normalized_control,
        "slot": action_payload["slot"],
        "action_id": action_payload["action_id"],
        "action_identity": action_payload["action_identity"],
        "payload": deepcopy(action_payload["payload"]),
        "action_contract": deepcopy(action_contract),
        "selection": deepcopy(action_payload["selection"]),
        "execution_policy": deepcopy(execution_policy),
        "preconditions": patch_review_execution_preconditions(normalized_control),
        "requires_confirmation": bool(execution_policy.get("requires_confirmation")),
        "requires_preview": bool(execution_policy.get("requires_preview")),
        "policy_gate": execution_policy.get("policy_gate"),
        "policy_sensitive": action_payload["policy_sensitive"],
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
    }


def _complete_patch_review_execution_contract(review: dict[str, Any]) -> dict[str, Any]:
    availability = patch_review_availability_from_contract(review)
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": availability["patch_id"],
        "flow": PATCH_REVIEW_FLOW,
        "decision_policy": PATCH_REVIEW_DECISION_POLICY,
        "decision_group": PATCH_REVIEW_DECISION_GROUP,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY),
        "required": list(PATCH_REVIEW_REQUIRED_PARTS),
        "available": deepcopy(availability["available"]),
        "missing": deepcopy(availability["missing"]),
        "next_required": availability["next_required"],
        "is_complete": availability["is_complete"],
    }


def resolve_patch_review_cli_command_execution(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
    command: str,
    capabilities: Any | None = None,
) -> dict[str, Any]:
    command_text = command.strip()
    if not command_text:
        raise ValueError("Patch review CLI command is required")
    normalized_command = command_text.lower()
    command_lookup = patch_review_cli_command_lookup_from_contract(card, review, patch_id=patch_id)
    entry = command_lookup["commands"].get(normalized_command)
    if not isinstance(entry, dict):
        raise ValueError(f"Unsupported patch review CLI command: {command_text}")
    control = str(entry.get("control", "")).strip().lower()
    execution = resolve_patch_review_control_execution(
        card,
        review,
        patch_id=patch_id,
        control=control,
        capabilities=capabilities,
    )
    if execution["selection"] != entry.get("selection"):
        raise ValueError("Patch review CLI command selection does not match the current control")
    return {
        **execution,
        "command": command_text,
        "normalized_command": normalized_command,
    }


def resolve_complete_patch_review_control_execution(
    card: dict[str, Any],
    *,
    patch_id: str,
    control: str,
    capabilities: Any | None = None,
) -> dict[str, Any]:
    if capabilities is not None:
        validate_complete_patch_review_capabilities(capabilities)
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    complete_patch_review_actions_from_card(card, patch_id=expected_patch_id)
    review = _complete_patch_review_contract_from_card(card, patch_id=expected_patch_id)
    execution = resolve_patch_review_control_execution(
        card,
        review,
        patch_id=expected_patch_id,
        control=control,
        capabilities=capabilities,
    )
    execution["complete_patch_review"] = _complete_patch_review_execution_contract(review)
    return execution


def resolve_complete_patch_review_cli_command_execution(
    card: dict[str, Any],
    *,
    patch_id: str,
    command: str,
    capabilities: Any | None = None,
) -> dict[str, Any]:
    if capabilities is not None:
        validate_complete_patch_review_capabilities(capabilities)
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    complete_patch_review_actions_from_card(card, patch_id=expected_patch_id)
    review = _complete_patch_review_contract_from_card(card, patch_id=expected_patch_id)
    execution = resolve_patch_review_cli_command_execution(
        card,
        review,
        patch_id=expected_patch_id,
        command=command,
        capabilities=capabilities,
    )
    execution["complete_patch_review"] = _complete_patch_review_execution_contract(review)
    return execution


def resolve_complete_patch_review_decision_cli_command_execution(
    card: dict[str, Any],
    *,
    patch_id: str,
    command: str,
    capabilities: Any | None = None,
) -> dict[str, Any]:
    if capabilities is not None:
        validate_complete_patch_review_capabilities(capabilities)
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    complete_patch_review_actions_from_card(card, patch_id=expected_patch_id)
    review = _complete_patch_review_contract_from_card(card, patch_id=expected_patch_id)
    execution = resolve_patch_review_decision_cli_command_execution(
        card,
        review,
        patch_id=expected_patch_id,
        command=command,
        capabilities=capabilities,
    )
    execution["complete_patch_review"] = _complete_patch_review_execution_contract(review)
    return execution


def _complete_patch_review_contract_from_card(card: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    embedded_review = card.get("patch_review")
    if embedded_review is not None:
        if not isinstance(embedded_review, dict):
            raise ValueError("Patch review contract must be an object")
        review = embedded_review
    else:
        review = build_complete_patch_review_contract(card, patch_id=patch_id)
    validate_patch_review_contract(card, review, patch_id=patch_id, require_complete=True)
    return review


def patch_review_control_summary_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    controls = patch_review_control_actions_from_contract(card, review, patch_id=patch_id)
    availability = patch_review_availability_from_contract(review)
    control_plan = patch_review_control_plan_from_contract(card, review, patch_id=patch_id)
    next_required = availability["next_required"]
    next_required_aliases = (
        list(PATCH_REVIEW_CLI_COMMAND_ALIASES.get(next_required, ()))
        if isinstance(next_required, str)
        else []
    )
    ordered_controls = [
        {"control": control, **deepcopy(controls[control])}
        for control in PATCH_REVIEW_REQUIRED_PARTS
        if control in controls
    ]
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": availability["patch_id"],
        "flow": availability["flow"],
        "decision_policy": availability["decision_policy"],
        "action_authority": availability["action_authority"],
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "required": deepcopy(availability["required"]),
        "available": deepcopy(availability["available"]),
        "missing": deepcopy(availability["missing"]),
        "next_required": next_required,
        "next_required_command_aliases": next_required_aliases,
        "is_complete": availability["is_complete"],
        "controls": deepcopy(controls),
        "control_plan": control_plan,
        "order": ordered_controls,
    }


def patch_review_next_control_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any] | None:
    summary = patch_review_control_summary_from_contract(card, review, patch_id=patch_id)
    next_required = summary["next_required"]
    if not isinstance(next_required, str):
        return None
    control = summary["controls"].get(next_required)
    if not isinstance(control, dict):
        return {
            "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
            "patch_id": summary["patch_id"],
            "control": next_required,
            "status": "missing",
            "command_aliases": deepcopy(summary["next_required_command_aliases"]),
            "action_authority": summary["action_authority"],
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        }
    slot = control["slot"]
    execution_policy = control["execution_policy"]
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": summary["patch_id"],
        "control": next_required,
        "status": "available",
        "command": str(slot),
        "command_aliases": deepcopy(summary["next_required_command_aliases"]),
        "slot": slot,
        "action_id": control["action_id"],
        "action_identity": control["action_identity"],
        "label": control["label"],
        "payload": deepcopy(control["payload"]),
        "action_contract": deepcopy(control["action_contract"]),
        "selection": deepcopy(control["selection"]),
        "requires_confirmation": bool(
            isinstance(execution_policy, dict)
            and execution_policy.get("requires_confirmation") is True
        ),
        "policy_gate": (
            execution_policy.get("policy_gate")
            if isinstance(execution_policy, dict)
            else None
        ),
        "policy_sensitive": control["policy_sensitive"],
        "action_authority": summary["action_authority"],
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
    }


def patch_review_cli_control_map_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    summary = patch_review_control_summary_from_contract(card, review, patch_id=patch_id)
    controls: list[dict[str, Any]] = []
    for entry in summary["order"]:
        if not isinstance(entry, dict):
            continue
        slot = entry.get("slot")
        if not isinstance(slot, int):
            continue
        execution_policy = entry.get("execution_policy", {})
        controls.append(
            {
                "control": entry["control"],
                "command": str(slot),
                "command_aliases": list(
                    PATCH_REVIEW_CLI_COMMAND_ALIASES.get(str(entry["control"]), ())
                ),
                "slot": slot,
                "action_id": entry["action_id"],
                "action_identity": entry["action_identity"],
                "label": entry["label"],
                "payload": deepcopy(entry["payload"]),
                "action_contract": deepcopy(entry["action_contract"]),
                "requires_confirmation": bool(
                    isinstance(execution_policy, dict)
                    and execution_policy.get("requires_confirmation") is True
                ),
                "policy_gate": (
                    execution_policy.get("policy_gate")
                    if isinstance(execution_policy, dict)
                    else None
                ),
                "policy_sensitive": entry["policy_sensitive"],
                "selection": deepcopy(entry["selection"]),
            }
        )
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": summary["patch_id"],
        "flow": summary["flow"],
        "decision_policy": summary["decision_policy"],
        "action_authority": summary["action_authority"],
        "selection_model": "one_based_action_slot",
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "required": deepcopy(summary["required"]),
        "available": deepcopy(summary["available"]),
        "is_complete": summary["is_complete"],
        "missing": deepcopy(summary["missing"]),
        "next_required": summary["next_required"],
        "next_required_command_aliases": deepcopy(summary["next_required_command_aliases"]),
        "controls": controls,
    }


def patch_review_cli_command_lookup_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    command_map = patch_review_cli_control_map_from_contract(card, review, patch_id=patch_id)
    lookup: dict[str, dict[str, Any]] = {}
    for entry in command_map["controls"]:
        if not isinstance(entry, dict):
            continue
        command = entry.get("command")
        aliases = entry.get("command_aliases", [])
        terms = [command] if isinstance(command, str) and command else []
        if isinstance(aliases, list):
            terms.extend(str(alias) for alias in aliases if str(alias).strip())
        for term in terms:
            normalized = str(term).strip().lower()
            if not normalized:
                continue
            if normalized in lookup:
                raise ValueError(f"Duplicate patch review CLI command: {normalized}")
            lookup[normalized] = {
                "control": entry["control"],
                "command": entry["command"],
                "slot": entry["slot"],
                "action_id": entry["action_id"],
                "action_identity": entry["action_identity"],
                "payload": deepcopy(entry["payload"]),
                "action_contract": deepcopy(entry["action_contract"]),
                "requires_confirmation": entry["requires_confirmation"],
                "policy_gate": entry["policy_gate"],
                "policy_sensitive": entry["policy_sensitive"],
                "selection": deepcopy(entry["selection"]),
            }
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": command_map["patch_id"],
        "flow": command_map["flow"],
        "decision_policy": command_map["decision_policy"],
        "decision_group": PATCH_REVIEW_DECISION_GROUP,
        "action_authority": command_map["action_authority"],
        "selection_model": command_map["selection_model"],
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "commands": lookup,
    }


def patch_review_decision_controls_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    command_map = patch_review_cli_control_map_from_contract(card, review, patch_id=patch_id)
    controls = [
        deepcopy(entry)
        for entry in command_map["controls"]
        if isinstance(entry, dict) and entry.get("control") in {"apply", "reject"}
    ]
    available = [entry["control"] for entry in controls]
    missing = [control for control in ("apply", "reject") if control not in set(available)]
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": command_map["patch_id"],
        "flow": command_map["flow"],
        "decision_policy": command_map["decision_policy"],
        "decision_group": PATCH_REVIEW_DECISION_GROUP,
        "action_authority": command_map["action_authority"],
        "selection_model": command_map["selection_model"],
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "required": ["apply", "reject"],
        "available": available,
        "missing": missing,
        "is_complete": not missing,
        "controls": controls,
    }


def patch_review_decision_cli_command_lookup_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    decisions = patch_review_decision_controls_from_contract(
        card,
        review,
        patch_id=patch_id,
    )
    lookup: dict[str, dict[str, Any]] = {}
    for entry in decisions["controls"]:
        if not isinstance(entry, dict):
            continue
        command = entry.get("command")
        aliases = entry.get("command_aliases", [])
        terms = [command] if isinstance(command, str) and command else []
        if isinstance(aliases, list):
            terms.extend(str(alias) for alias in aliases if str(alias).strip())
        for term in terms:
            normalized = str(term).strip().lower()
            if not normalized:
                continue
            if normalized in lookup:
                raise ValueError(f"Duplicate patch decision CLI command: {normalized}")
            lookup[normalized] = {
                "control": entry["control"],
                "command": entry["command"],
                "slot": entry["slot"],
                "action_id": entry["action_id"],
                "action_identity": entry["action_identity"],
                "payload": deepcopy(entry["payload"]),
                "action_contract": deepcopy(entry["action_contract"]),
                "requires_confirmation": entry["requires_confirmation"],
                "policy_gate": entry["policy_gate"],
                "policy_sensitive": entry["policy_sensitive"],
                "selection": deepcopy(entry["selection"]),
            }
    return {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": decisions["patch_id"],
        "flow": decisions["flow"],
        "decision_policy": decisions["decision_policy"],
        "decision_group": PATCH_REVIEW_DECISION_GROUP,
        "action_authority": decisions["action_authority"],
        "selection_model": decisions["selection_model"],
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "required": deepcopy(decisions["required"]),
        "available": deepcopy(decisions["available"]),
        "missing": deepcopy(decisions["missing"]),
        "is_complete": decisions["is_complete"],
        "commands": lookup,
    }


def resolve_patch_review_decision_cli_command_execution(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
    command: str,
    capabilities: Any | None = None,
) -> dict[str, Any]:
    command_text = command.strip()
    if not command_text:
        raise ValueError("Patch review decision CLI command is required")
    normalized_command = command_text.lower()
    command_lookup = patch_review_decision_cli_command_lookup_from_contract(
        card,
        review,
        patch_id=patch_id,
    )
    entry = command_lookup["commands"].get(normalized_command)
    if not isinstance(entry, dict):
        raise ValueError(f"Unsupported patch review decision CLI command: {command_text}")
    control = str(entry.get("control", "")).strip().lower()
    if control not in {"apply", "reject"}:
        raise ValueError("Patch review decision CLI command must resolve to apply or reject")
    execution = resolve_patch_review_control_execution(
        card,
        review,
        patch_id=patch_id,
        control=control,
        capabilities=capabilities,
    )
    if execution["selection"] != entry.get("selection"):
        raise ValueError("Patch review decision CLI command selection does not match the current control")
    return {
        **execution,
        "command": command_text,
        "normalized_command": normalized_command,
        "decision_group": PATCH_REVIEW_DECISION_GROUP,
    }


def patch_review_selection_from_cli_command(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
    command: str,
) -> dict[str, Any]:
    command_text = command.strip()
    if not command_text:
        raise ValueError("Patch review CLI command is required")
    normalized_command = command_text.lower()

    command_lookup = patch_review_cli_command_lookup_from_contract(card, review, patch_id=patch_id)
    entry = command_lookup["commands"].get(normalized_command)
    if isinstance(entry, dict):
        selection = entry.get("selection")
        if not isinstance(selection, dict):
            raise ValueError("Patch review CLI command selection must be an object")
        patch_review_action_selection_from_selection(
            card,
            review,
            selection,
            patch_id=patch_id,
        )
        return deepcopy(selection)
    raise ValueError(f"Unsupported patch review CLI command: {command_text}")


def patch_review_action_ref_from_cli_command(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
    command: str,
) -> ActionRef:
    selection = patch_review_selection_from_cli_command(
        card,
        review,
        patch_id=patch_id,
        command=command,
    )
    return patch_review_action_selection_from_selection(
        card,
        review,
        selection,
        patch_id=patch_id,
    ).action


def patch_review_control_plan_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> list[dict[str, Any]]:
    controls = patch_review_control_actions_from_contract(card, review, patch_id=patch_id)
    availability = patch_review_availability_from_contract(review)
    missing = set(availability["missing"])
    plan: list[dict[str, Any]] = []
    for control in PATCH_REVIEW_REQUIRED_PARTS:
        entry: dict[str, Any] = {
            "control": control,
            "kind": PATCH_REVIEW_CONTROL_KINDS[control],
            "status": "missing" if control in missing else "available",
            "command_aliases": list(PATCH_REVIEW_CLI_COMMAND_ALIASES.get(control, ())),
            "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY[control]),
            "preconditions": patch_review_execution_preconditions(control),
            "resolved_status": patch_review_resolved_status(control),
        }
        if entry["kind"] == "decision":
            entry["decision_group"] = PATCH_REVIEW_DECISION_GROUP
            entry["decision"] = control
        control_payload = controls.get(control)
        if control_payload is not None:
            entry.update(
                {
                    "slot": control_payload["slot"],
                    "action_id": control_payload["action_id"],
                    "action_identity": control_payload["action_identity"],
                    "label": control_payload["label"],
                    "payload": deepcopy(control_payload["payload"]),
                    "action_contract": deepcopy(control_payload["action_contract"]),
                    "confirm": deepcopy(control_payload["confirm"]),
                    "policy_sensitive": control_payload["policy_sensitive"],
                }
            )
        plan.append(entry)
    return plan


def complete_patch_review_action_refs_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, ActionRef | dict[str, ActionRef]]:
    availability = patch_review_availability_from_contract(review)
    missing = availability["missing"]
    if missing:
        raise ValueError(f"Complete patch review is missing: {', '.join(missing)}")

    refs = patch_review_action_refs_from_contract(card, review, patch_id=patch_id)
    preview_ref = refs["preview"]
    decision_refs = refs["decisions"]
    if not isinstance(preview_ref, ActionRef):
        raise ValueError("Complete patch review is missing: preview")
    if not isinstance(decision_refs, dict):
        raise ValueError("Complete patch review decisions must be available")
    missing_refs = [
        part
        for part in ("apply", "reject")
        if not isinstance(decision_refs.get(part), ActionRef)
    ]
    if missing_refs:
        raise ValueError(f"Complete patch review is missing: {', '.join(missing_refs)}")
    return {
        "preview": preview_ref,
        "decisions": {
            "apply": decision_refs["apply"],
            "reject": decision_refs["reject"],
        },
    }


def complete_patch_review_actions_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> CompletePatchReviewActions:
    refs = complete_patch_review_action_refs_from_contract(card, review, patch_id=patch_id)
    preview_ref = refs["preview"]
    decision_refs = refs["decisions"]
    if not isinstance(preview_ref, ActionRef):
        raise ValueError("Complete patch review is missing: preview")
    if not isinstance(decision_refs, dict):
        raise ValueError("Complete patch review decisions must be available")
    apply_ref = decision_refs.get("apply")
    reject_ref = decision_refs.get("reject")
    if not isinstance(apply_ref, ActionRef):
        raise ValueError("Complete patch review is missing: apply")
    if not isinstance(reject_ref, ActionRef):
        raise ValueError("Complete patch review is missing: reject")
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    return CompletePatchReviewActions(
        patch_id=expected_patch_id,
        preview=preview_ref,
        apply=apply_ref,
        reject=reject_ref,
    )


def complete_patch_review_actions_from_card(
    card: dict[str, Any],
    *,
    patch_id: str,
) -> CompletePatchReviewActions:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")

    embedded_review = card.get("patch_review")
    if embedded_review is not None:
        if not isinstance(embedded_review, dict):
            raise ValueError("Patch review contract must be an object")
        review = embedded_review
    else:
        review = build_complete_patch_review_contract(card, patch_id=expected_patch_id)
    resolve_patch_review_contract(card, review, patch_id=expected_patch_id)
    actions = complete_patch_review_actions_from_contract(
        card,
        review,
        patch_id=expected_patch_id,
    )
    embedded_actions = card.get("complete_patch_review_actions")
    if embedded_actions is not None:
        if not isinstance(embedded_actions, dict):
            raise ValueError("Complete patch review actions contract must be an object")
        if embedded_actions != actions.as_contract():
            raise ValueError("Complete patch review actions do not match engine-resolved actions")
    return actions


def complete_patch_review_action_from_card(
    card: dict[str, Any],
    *,
    patch_id: str,
    control: str,
) -> ActionRef:
    actions = complete_patch_review_actions_from_card(card, patch_id=patch_id)
    normalized_control = control.strip().lower()
    if normalized_control == "preview":
        return actions.preview
    if normalized_control == "apply":
        return actions.apply
    if normalized_control == "reject":
        return actions.reject
    raise ValueError("Patch review control must be 'preview', 'apply', or 'reject'")


def complete_patch_review_action_ref_from_cli_command(
    card: dict[str, Any],
    *,
    patch_id: str,
    command: str,
) -> ActionRef:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    complete_patch_review_actions_from_card(
        card,
        patch_id=expected_patch_id,
    )
    review = _complete_patch_review_contract_from_card(card, patch_id=expected_patch_id)
    return patch_review_action_ref_from_cli_command(
        card,
        review,
        patch_id=expected_patch_id,
        command=command,
    )


def complete_patch_review_decision_action_ref_from_cli_command(
    card: dict[str, Any],
    *,
    patch_id: str,
    command: str,
) -> ActionRef:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    complete_patch_review_actions_from_card(
        card,
        patch_id=expected_patch_id,
    )
    review = _complete_patch_review_contract_from_card(card, patch_id=expected_patch_id)
    execution = resolve_patch_review_decision_cli_command_execution(
        card,
        review,
        patch_id=expected_patch_id,
        command=command,
    )
    return _action_ref_from_contract(execution["action_contract"])


def build_patch_review_selection(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
    control: str,
) -> dict[str, Any]:
    resolved = resolve_patch_review_contract(card, review, patch_id=patch_id)
    normalized_control = control.strip().lower()
    if normalized_control == "preview":
        if resolved["preview"] is None or not isinstance(review.get("preview"), dict):
            raise ValueError("Patch review preview is not available for the current patch")
        return deepcopy(review["preview"])
    if normalized_control not in {"apply", "reject"}:
        raise ValueError("Patch review control must be 'preview', 'apply', or 'reject'")

    decisions = review.get("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("Patch review decisions must be a list")
    resolved_decisions = {
        entry["decision"]
        for entry in resolved["decisions"]
        if isinstance(entry, dict)
    }
    if normalized_control not in resolved_decisions:
        raise ValueError(f"Patch review {normalized_control} is not available for the current patch")
    for entry in decisions:
        if not isinstance(entry, dict):
            raise ValueError("Patch review decision entry must be an object")
        if entry.get("decision") == normalized_control and isinstance(entry.get("selection"), dict):
            return deepcopy(entry["selection"])
    raise ValueError(f"Patch review {normalized_control} is not available for the current patch")


def patch_review_action_ref_from_selection(
    card: dict[str, Any],
    review: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    return patch_review_action_selection_from_selection(
        card,
        review,
        selection,
        patch_id=patch_id,
    ).as_contract()


def patch_review_action_selection_from_selection(
    card: dict[str, Any],
    review: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> PatchReviewActionSelection:
    resolved = resolve_patch_review_selection(card, review, selection, patch_id=patch_id)
    action_ref = action_ref_from_selection(card, selection)
    if action_ref.id != resolved["action"].get("id"):
        raise ValueError("Patch review selection does not match the resolved action")

    decision = resolved.get("decision") if resolved["kind"] == "decision" else None
    if resolved["kind"] == "decision":
        if decision not in {"apply", "reject"}:
            raise ValueError("Patch review decision must be 'apply' or 'reject'")
    return PatchReviewActionSelection(
        kind=resolved["kind"],
        patch_id=resolved["patch_id"],
        action=action_ref,
        decision=decision,
    )


def resolve_patch_review_selection(
    card: dict[str, Any],
    review: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    resolved = resolve_patch_review_contract(card, review, patch_id=patch_id)
    if not isinstance(selection, dict):
        raise ValueError("Patch review selection must be an object")

    preview_selection = review.get("preview")
    if (
        isinstance(preview_selection, dict)
        and selection == preview_selection
        and resolved["preview"] is not None
    ):
        return {
            "kind": "preview",
            "patch_id": patch_id.strip(),
            "action": resolved["preview"],
        }

    review_decisions = review.get("decisions", [])
    if not isinstance(review_decisions, list):
        raise ValueError("Patch review decisions must be a list")
    resolved_decisions = {
        entry["decision"]: entry["action"]
        for entry in resolved["decisions"]
        if isinstance(entry, dict)
    }
    for entry in review_decisions:
        if not isinstance(entry, dict):
            raise ValueError("Patch review decision entry must be an object")
        decision = str(entry.get("decision", "")).strip().lower()
        if entry.get("selection") == selection and decision in resolved_decisions:
            return {
                "kind": "decision",
                "patch_id": patch_id.strip(),
                "decision": decision,
                "action": resolved_decisions[decision],
            }

    raise ValueError("Patch review selection is not part of the current review contract")


def resolve_card_selection(card: dict[str, Any], selected_action_id: str) -> dict[str, Any]:
    actions = materialize_card_actions(card)
    matches = [action for action in actions if action.get("id") == selected_action_id]
    if len(matches) == 1:
        action = matches[0]
        validate_action_ref(action)
        return action
    if len(matches) > 1:
        raise ValueError(
            f"Action '{selected_action_id}' is ambiguous on card. "
            "Use one-based action selection for duplicate action IDs."
        )
    action_ids = [a.get("id", "<unknown>") for a in actions]
    raise ValueError(f"Action '{selected_action_id}' not found on card. Available: {action_ids}")


def resolve_card_selection_by_index(card: dict[str, Any], selected_action_index: int) -> dict[str, Any]:
    if not isinstance(selected_action_index, int) or isinstance(selected_action_index, bool):
        raise TypeError("Action selection index must be an integer")
    if selected_action_index < 1:
        raise ValueError("Action selection index must be one-based")

    action_sequence = materialize_card_actions(card)
    try:
        action = action_sequence[selected_action_index - 1]
    except IndexError as exc:
        raise ValueError(
            f"Action selection index {selected_action_index} not found. "
            f"Available range: 1..{len(action_sequence)}"
        ) from exc
    validate_action_ref(action)
    return action


def resolve_card_selection_contract(card: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    return _resolve_card_selection_contract(
        card,
        selection,
        allowed_fields=_ACTION_SELECTION_FIELDS,
        contract_name="action selection",
    )


def resolve_card_selection_execution(
    card: dict[str, Any],
    selection: dict[str, Any],
    *,
    capabilities: Any,
) -> dict[str, Any]:
    validate_action_capabilities(capabilities)
    action = resolve_card_selection_contract(card, selection)
    action_ref = engine_authoritative_action_ref(_action_ref_from_contract(action))
    if action_ref.id not in set(capabilities.actions_supported):
        raise ValueError("Action not supported by client")
    return {
        "selection": deepcopy(selection),
        "action_contract": action_ref.as_contract(),
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "execution_policy": {
            "policy_gate": "required" if action_ref.policy_sensitive else "optional",
            "requires_confirmation": action_ref.confirm is not None,
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        },
    }


def _validate_patch_review_selection_metadata(selection: dict[str, Any]) -> None:
    if selection.get("action_authority") != PATCH_REVIEW_ACTION_AUTHORITY:
        raise ValueError("Patch review selection must be engine-authoritative")
    if selection.get("demo_path_step") != PATCH_REVIEW_DEMO_PATH_STEP:
        raise ValueError("Patch review selection does not match the demo path step")
    execution_policy = selection.get("execution_policy")
    if not isinstance(execution_policy, dict):
        raise ValueError("Patch review selection must include execution_policy")
    patch_decision = selection.get("patch_decision")
    if patch_decision in {"apply", "reject"}:
        expected_policy = PATCH_REVIEW_EXECUTION_POLICY[patch_decision]
        if selection.get("decision_group") != PATCH_REVIEW_DECISION_GROUP:
            raise ValueError("Patch review selection decision group does not match engine policy")
    elif selection.get("patch_preview_contract_version") == PATCH_PREVIEW_CONTRACT_VERSION:
        expected_policy = PATCH_REVIEW_EXECUTION_POLICY["preview"]
    else:
        raise ValueError("Patch review selection must identify preview or decision policy")
    if execution_policy != expected_policy:
        raise ValueError("Patch review selection execution policy does not match engine policy")


def _validate_selection_fields(
    selection: dict[str, Any],
    allowed_fields: frozenset[str],
    contract_name: str,
) -> None:
    unexpected_fields = set(selection) - allowed_fields
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported {contract_name} field(s): {field_list}")


def action_ref_from_selection(card: dict[str, Any], selection: dict[str, Any]) -> ActionRef:
    allowed_fields = (
        _PATCH_REVIEW_SELECTION_FIELDS
        if {
            "action_authority",
            "demo_path_step",
            "patch_id",
        }.issubset(selection)
        else _ACTION_SELECTION_FIELDS
    )
    action = _resolve_card_selection_contract(
        card,
        selection,
        allowed_fields=allowed_fields,
        contract_name="action selection",
    )
    validate_action_ref(action)
    confirm = action.get("confirm")
    if isinstance(confirm, dict):
        confirm = deepcopy(confirm)
    return ActionRef(
        id=str(action["id"]),
        label=str(action["label"]).strip(),
        payload=deepcopy(action["payload"]),
        confirm=confirm,
        policy_sensitive=action.get("policy_sensitive", False),
    )


def resolve_patch_decision_selection(
    card: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    action = _resolve_card_selection_contract(
        card,
        selection,
        allowed_fields=_PATCH_REVIEW_SELECTION_FIELDS,
        contract_name="patch decision selection",
    )
    if action.get("id") not in {"apply_patch", "reject_patch"}:
        raise ValueError("Action selection is not a patch decision")
    _validate_selection_fields(
        selection,
        _PATCH_DECISION_SELECTION_FIELDS,
        "patch decision selection",
    )
    payload = action.get("payload")
    action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch decision patch_id is required")
    if selection.get("patch_id") != expected_patch_id:
        raise ValueError("Patch decision selection does not match the current patch")
    expected_decision = PATCH_DECISION_BY_ACTION_ID[str(action["id"])]
    if selection.get("patch_decision_contract_version") != PATCH_DECISION_CONTRACT_VERSION:
        raise ValueError("Unsupported patch decision contract version")
    submitted_decision = selection.get("patch_decision")
    if submitted_decision not in {"apply", "reject"}:
        raise ValueError("Patch decision selection must include patch_decision")
    if submitted_decision != expected_decision:
        raise ValueError("Patch decision selection does not match the selected action")
    _validate_patch_review_selection_metadata(selection)
    if action_patch_id != expected_patch_id:
        raise ValueError("Patch decision selection does not match the current patch")
    return action


def patch_decision_action_ref_from_selection(
    card: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> ActionRef:
    resolve_patch_decision_selection(card, selection, patch_id=patch_id)
    return action_ref_from_selection(card, selection)


def resolve_patch_decision_action(
    card: dict[str, Any],
    *,
    patch_id: str,
    decision: str,
) -> dict[str, Any]:
    selection = build_patch_decision_selection(card, patch_id=patch_id, decision=decision)
    expected_patch_id = patch_id.strip()
    return resolve_patch_decision_selection(card, selection, patch_id=expected_patch_id)


def resolve_patch_preview_selection(
    card: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    action = _resolve_card_selection_contract(
        card,
        selection,
        allowed_fields=_PATCH_REVIEW_SELECTION_FIELDS,
        contract_name="patch preview selection",
    )
    if action.get("id") != "preview_patch":
        raise ValueError("Action selection is not a patch preview")
    _validate_selection_fields(
        selection,
        _PATCH_PREVIEW_SELECTION_FIELDS,
        "patch preview selection",
    )
    payload = action.get("payload")
    action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch preview patch_id is required")
    if selection.get("patch_id") != expected_patch_id:
        raise ValueError("Patch preview selection does not match the current patch")
    if selection.get("patch_preview_contract_version") != PATCH_PREVIEW_CONTRACT_VERSION:
        raise ValueError("Unsupported patch preview contract version")
    _validate_patch_review_selection_metadata(selection)
    if action_patch_id != expected_patch_id:
        raise ValueError("Patch preview selection does not match the current patch")
    return action


def _resolve_card_selection_contract(
    card: dict[str, Any],
    selection: dict[str, Any],
    *,
    allowed_fields: frozenset[str] | set[str],
    contract_name: str,
) -> dict[str, Any]:
    if not isinstance(selection, dict):
        raise ValueError("Action selection must be an object")
    _validate_selection_fields(selection, frozenset(allowed_fields), contract_name)
    if selection.get("contract_version") != ACTION_SELECTION_CONTRACT_VERSION:
        raise ValueError("Unsupported action selection contract version")
    if selection.get("selection_model") != "one_based_action_slot":
        raise ValueError("Unsupported action selection model")

    slot = selection.get("slot")
    action = resolve_card_selection_by_index(card, slot)
    expected_identity = canonical_action_identity_key(action)
    submitted_identity = selection.get("action_identity")
    if submitted_identity != expected_identity:
        raise ValueError("Action selection identity does not match the current card")
    return action


def patch_preview_action_ref_from_selection(
    card: dict[str, Any],
    selection: dict[str, Any],
    *,
    patch_id: str,
) -> ActionRef:
    resolve_patch_preview_selection(card, selection, patch_id=patch_id)
    return action_ref_from_selection(card, selection)


def build_patch_preview_selection(card: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch preview patch_id is required")

    patch_preview = card.get("patch_preview")
    if not isinstance(patch_preview, dict) or patch_preview.get("patch_id") != expected_patch_id:
        patch_preview = materialize_patch_preview_contract(card, expected_patch_id)
    if patch_preview.get("contract_version") != PATCH_PREVIEW_CONTRACT_VERSION:
        raise ValueError("Unsupported patch preview contract version")

    matching_entries = [
        entry for entry in patch_preview.get("previews", []) if isinstance(entry, dict)
    ]
    if len(matching_entries) != 1:
        raise ValueError("Patch preview is not available for the current patch")

    entry = matching_entries[0]
    selection = entry.get("selection")
    if isinstance(selection, dict):
        if selection.get("contract_version") != ACTION_SELECTION_CONTRACT_VERSION:
            raise ValueError("Unsupported action selection contract version")
        if selection.get("selection_model") != "one_based_action_slot":
            raise ValueError("Unsupported action selection model")
        if selection.get("slot") != entry.get("slot"):
            raise ValueError("Patch preview selection does not match the current card")
        if selection.get("action_identity") != entry.get("action_identity"):
            raise ValueError("Patch preview selection does not match the current card")
        _validate_patch_review_selection_metadata(selection)
        if selection.get("patch_preview_contract_version") != PATCH_PREVIEW_CONTRACT_VERSION:
            raise ValueError("Unsupported patch preview contract version")
        if selection.get("patch_id") != expected_patch_id:
            raise ValueError("Patch preview selection does not match the current patch")
        resolve_patch_preview_selection(card, selection, patch_id=expected_patch_id)
        return deepcopy(selection)
    selection = {
        "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
        "selection_model": "one_based_action_slot",
        "slot": entry.get("slot"),
        "action_identity": entry.get("action_identity"),
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY["preview"]),
        "patch_preview_contract_version": PATCH_PREVIEW_CONTRACT_VERSION,
        "patch_id": expected_patch_id,
    }
    resolve_patch_preview_selection(card, selection, patch_id=expected_patch_id)
    return selection


def resolve_patch_preview_action(card: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    selection = build_patch_preview_selection(card, patch_id=patch_id)
    expected_patch_id = patch_id.strip()
    return resolve_patch_preview_selection(card, selection, patch_id=expected_patch_id)


def build_patch_decision_selection(
    card: dict[str, Any],
    *,
    patch_id: str,
    decision: str,
) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch decision patch_id is required")

    normalized_decision = decision.strip().lower()
    if normalized_decision not in {"apply", "reject"}:
        raise ValueError("Patch decision must be 'apply' or 'reject'")

    patch_decision = card.get("patch_decision")
    if not isinstance(patch_decision, dict) or patch_decision.get("patch_id") != expected_patch_id:
        patch_decision = materialize_patch_decision_contract(card, expected_patch_id)
    if patch_decision.get("contract_version") != PATCH_DECISION_CONTRACT_VERSION:
        raise ValueError("Unsupported patch decision contract version")

    matching_entries = [
        entry
        for entry in patch_decision.get("decisions", [])
        if isinstance(entry, dict) and entry.get("decision") == normalized_decision
    ]
    if len(matching_entries) != 1:
        raise ValueError(f"Patch decision '{normalized_decision}' is not available for the current patch")

    entry = matching_entries[0]
    selection = entry.get("selection")
    if isinstance(selection, dict):
        if selection.get("contract_version") != ACTION_SELECTION_CONTRACT_VERSION:
            raise ValueError("Unsupported action selection contract version")
        if selection.get("selection_model") != "one_based_action_slot":
            raise ValueError("Unsupported action selection model")
        if selection.get("action_identity") != entry.get("action_identity"):
            raise ValueError("Patch decision selection does not match the current card")
        if selection.get("slot") != entry.get("slot"):
            raise ValueError("Patch decision selection does not match the current card")
        _validate_patch_review_selection_metadata(selection)
        if selection.get("patch_decision_contract_version") != PATCH_DECISION_CONTRACT_VERSION:
            raise ValueError("Unsupported patch decision contract version")
        if selection.get("patch_decision") != normalized_decision:
            raise ValueError("Patch decision selection does not match the selected action")
        if selection.get("patch_id") != expected_patch_id:
            raise ValueError("Patch decision selection does not match the current patch")
        resolve_patch_decision_selection(card, selection, patch_id=expected_patch_id)
        return deepcopy(selection)
    selection = {
        "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
        "selection_model": "one_based_action_slot",
        "slot": entry.get("slot"),
        "action_identity": entry.get("action_identity"),
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY[normalized_decision]),
        "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
        "decision_group": PATCH_REVIEW_DECISION_GROUP,
        "patch_decision": normalized_decision,
        "patch_id": expected_patch_id,
    }
    resolve_patch_decision_selection(card, selection, patch_id=expected_patch_id)
    return selection


def validate_action_ref(action: Any) -> None:
    if not isinstance(action, dict):
        raise ValueError("ActionRef must be an object")
    unexpected_fields = set(action) - _ACTION_REF_FIELDS
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported action field(s): {field_list}")
    action_id = action.get("id")
    if not isinstance(action_id, str) or not action_id.strip():
        raise ValueError("Action id is required")
    if action_id != action_id.strip():
        raise ValueError("Action id must be normalized")
    if action_id not in _ALLOWED_ACTION_SET:
        raise ValueError(f"Unsupported action id: {action_id}")
    label = action.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ValueError("Action label is required")
    payload = action.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Action payload must be an object")
    _validate_action_payload(action_id, payload)
    confirm = action.get("confirm")
    if confirm is not None:
        if not isinstance(confirm, dict):
            raise ValueError("Action confirm must be an object")
        unexpected_confirm_fields = set(confirm) - {"title"}
        if unexpected_confirm_fields:
            field_list = ", ".join(sorted(unexpected_confirm_fields))
            raise ValueError(f"Unsupported action confirm field(s): {field_list}")
        for key, value in confirm.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Action confirm keys must be non-empty strings")
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Action confirm values must be non-empty strings")
            if value != value.strip():
                raise ValueError("Action confirm values must be normalized")
    policy_sensitive = action.get("policy_sensitive", False)
    if not isinstance(policy_sensitive, bool):
        raise ValueError("Action policy_sensitive must be a boolean")


def _action_ref_from_contract(action: dict[str, Any]) -> ActionRef:
    validate_action_ref(action)
    confirm = action.get("confirm")
    if isinstance(confirm, dict):
        confirm = deepcopy(confirm)
    return ActionRef(
        id=str(action["id"]),
        label=str(action["label"]).strip(),
        payload=deepcopy(action["payload"]),
        confirm=confirm,
        policy_sensitive=action.get("policy_sensitive", False),
    )


def execute_action_with_policy_gate(
    *,
    action: ActionRef,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_action_capabilities(capabilities)
    action = engine_authoritative_action_ref(action)
    validate_action_ref(action.as_contract())
    if action.id not in _ALLOWED_ACTION_SET:
        raise ValueError("Unknown action id")
    if action.id not in set(capabilities.actions_supported):
        raise ValueError("Action not supported by client")
    policy_sensitive = action.policy_sensitive or is_policy_sensitive_action(action.id)
    if policy_sensitive != action.policy_sensitive:
        action = replace(action, policy_sensitive=policy_sensitive)
        validate_action_ref(action.as_contract())
    if not policy_gate.allow_action(action.id, action.payload, policy_sensitive=policy_sensitive):
        raise PermissionError("PolicyGate blocked action")
    return executor(action)


def execute_card_selection_with_policy_gate(
    *,
    card: dict[str, Any],
    selection: dict[str, Any],
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    execution = resolve_card_selection_execution(card, selection, capabilities=capabilities)
    return execute_action_with_policy_gate(
        action=_action_ref_from_contract(execution["action_contract"]),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def engine_authoritative_action_ref(action: ActionRef) -> ActionRef:
    validate_action_ref(action.as_contract())
    normalized_label = action.label.strip()
    if normalized_label != action.label:
        action = replace(action, label=normalized_label)
        validate_action_ref(action.as_contract())
    normalized_fields = ENGINE_NORMALIZED_ACTION_PAYLOAD_FIELDS.get(action.id, ())
    if normalized_fields:
        normalized_payload = dict(action.payload)
        changed = False
        for field_name in normalized_fields:
            value = normalized_payload.get(field_name)
            if isinstance(value, str):
                normalized_value = value.strip()
                if normalized_value != value:
                    normalized_payload[field_name] = normalized_value
                    changed = True
        if changed:
            action = replace(action, payload=normalized_payload)
            validate_action_ref(action.as_contract())
    if action.id == "preview_patch":
        if action.confirm is not None or action.policy_sensitive:
            return replace(action, confirm=None, policy_sensitive=False)
    if action.id in PATCH_DECISION_ACTION_IDS:
        confirm = {"title": PATCH_REVIEW_CONFIRMATION_TITLES[action.id]}
        if action.confirm != confirm or not action.policy_sensitive:
            return replace(action, confirm=confirm, policy_sensitive=True)
        return action
    if is_policy_sensitive_action(action.id):
        if action.confirm is not None or not action.policy_sensitive:
            return replace(action, confirm=None, policy_sensitive=True)
        return action
    if action.confirm is not None or action.policy_sensitive:
        return replace(action, confirm=None, policy_sensitive=False)
    return action


def is_policy_sensitive_action(action_id: str) -> bool:
    return action_id in _POLICY_SENSITIVE_ACTION_SET


def execute_patch_review_selection_with_policy_gate(
    *,
    card: dict[str, Any],
    review: dict[str, Any],
    selection: dict[str, Any],
    patch_id: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    selected = patch_review_action_selection_from_selection(
        card,
        review,
        selection,
        patch_id=patch_id,
    )
    return execute_action_with_policy_gate(
        action=engine_authoritative_action_ref(selected.action),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_patch_review_cli_command_with_policy_gate(
    *,
    card: dict[str, Any],
    review: dict[str, Any],
    patch_id: str,
    command: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    execution = resolve_patch_review_cli_command_execution(
        card,
        review,
        patch_id=patch_id,
        command=command,
        capabilities=capabilities,
    )
    return execute_action_with_policy_gate(
        action=_action_ref_from_contract(execution["action_contract"]),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_patch_review_control_with_policy_gate(
    *,
    card: dict[str, Any],
    review: dict[str, Any],
    patch_id: str,
    control: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    execution = resolve_patch_review_control_execution(
        card,
        review,
        patch_id=patch_id,
        control=control,
        capabilities=capabilities,
    )
    return execute_patch_review_selection_with_policy_gate(
        card=card,
        review=review,
        selection=execution["selection"],
        patch_id=patch_id,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_patch_review_decision_cli_command_with_policy_gate(
    *,
    card: dict[str, Any],
    review: dict[str, Any],
    patch_id: str,
    command: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    execution = resolve_patch_review_decision_cli_command_execution(
        card,
        review,
        patch_id=patch_id,
        command=command,
        capabilities=capabilities,
    )
    return execute_action_with_policy_gate(
        action=_action_ref_from_contract(execution["action_contract"]),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_complete_patch_review_action_with_policy_gate(
    *,
    card: dict[str, Any],
    patch_id: str,
    control: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_complete_patch_review_capabilities(capabilities)
    action = complete_patch_review_action_from_card(card, patch_id=patch_id, control=control)
    return execute_action_with_policy_gate(
        action=engine_authoritative_action_ref(action),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_complete_patch_review_control_with_policy_gate(
    *,
    card: dict[str, Any],
    patch_id: str,
    control: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    execution = resolve_complete_patch_review_control_execution(
        card,
        patch_id=patch_id,
        control=control,
        capabilities=capabilities,
    )
    return execute_action_with_policy_gate(
        action=_action_ref_from_contract(execution["action_contract"]),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_complete_patch_review_selection_with_policy_gate(
    *,
    card: dict[str, Any],
    selection: dict[str, Any],
    patch_id: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_complete_patch_review_capabilities(capabilities)
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    review = _complete_patch_review_contract_from_card(card, patch_id=expected_patch_id)
    complete_patch_review_actions_from_contract(card, review, patch_id=expected_patch_id)
    return execute_patch_review_selection_with_policy_gate(
        card=card,
        review=review,
        selection=selection,
        patch_id=expected_patch_id,
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_complete_patch_review_cli_command_with_policy_gate(
    *,
    card: dict[str, Any],
    patch_id: str,
    command: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_complete_patch_review_capabilities(capabilities)
    execution = resolve_complete_patch_review_cli_command_execution(
        card,
        patch_id=patch_id,
        command=command,
        capabilities=capabilities,
    )
    return execute_action_with_policy_gate(
        action=_action_ref_from_contract(execution["action_contract"]),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def execute_complete_patch_review_decision_cli_command_with_policy_gate(
    *,
    card: dict[str, Any],
    patch_id: str,
    command: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_complete_patch_review_capabilities(capabilities)
    execution = resolve_complete_patch_review_decision_cli_command_execution(
        card,
        patch_id=patch_id,
        command=command,
        capabilities=capabilities,
    )
    return execute_action_with_policy_gate(
        action=_action_ref_from_contract(execution["action_contract"]),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def _validate_action_payload(action_id: str, payload: dict[str, Any]) -> None:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"Unsupported action id: {action_id}")
    for key in payload:
        if not isinstance(key, str) or not key.strip():
            raise ValueError(f"Payload field names must be non-empty strings for action '{action_id}'")
    unexpected_fields = set(payload) - set(schema)
    if unexpected_fields:
        field_list = ", ".join(sorted(unexpected_fields))
        raise ValueError(f"Unsupported payload field(s) for action '{action_id}': {field_list}")
    for key, value_type in schema.items():
        if key not in payload:
            raise ValueError(f"Missing payload field '{key}' for action '{action_id}'")
        if not isinstance(payload[key], value_type):
            raise ValueError(f"Payload field '{key}' must be of type {value_type.__name__}")
        if value_type is str and not payload[key].strip():
            raise ValueError(f"Payload field '{key}' is required for action '{action_id}'")
