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
    "pin_to_context_set",
    "create_context_set",
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
PATCH_REVIEW_ACTION_AUTHORITY = "engine_revalidated"
PATCH_REVIEW_DEMO_PATH_STEP = "preview_apply_or_reject_patch"
PATCH_REVIEW_EXECUTION_POLICY: dict[str, dict[str, Any]] = {
    "preview": {
        "policy_gate": "optional",
        "requires_confirmation": False,
        "mutates_patch": False,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
    },
    "apply": {
        "policy_gate": "required",
        "requires_confirmation": True,
        "mutates_patch": True,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
    },
    "reject": {
        "policy_gate": "required",
        "requires_confirmation": True,
        "mutates_patch": True,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
    },
}
PATCH_REVIEW_CONFIRMATION_TITLES: dict[str, str] = {
    "apply_patch": "Apply patch?",
    "reject_patch": "Reject patch?",
}
PATCH_REVIEW_REQUIRED_PARTS: tuple[str, ...] = ("preview", "apply", "reject")

CANONICAL_ACTION_ORDER: tuple[str, ...] = (
    "preview_patch",
    "apply_patch",
    "reject_patch",
    "open_section",
    "open_corpus_item",
    "pin_to_context_set",
    "create_context_set",
    "copy_to_clipboard",
    "export_document",
    "refresh_license",
    "run_agent",
)
CANONICAL_ACTION_PRIORITY: dict[str, int] = {
    action_id: index for index, action_id in enumerate(CANONICAL_ACTION_ORDER)
}
_ALLOWED_ACTION_SET = set(ALLOWED_ACTION_IDS)
if set(CANONICAL_ACTION_ORDER) != _ALLOWED_ACTION_SET:
    raise RuntimeError("A2UI canonical action order must match allowed action IDs")

_ACTION_SCHEMAS: dict[str, dict[str, type]] = {
    "preview_patch": {"patch_id": str},
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
_ACTION_REF_FIELDS: frozenset[str] = frozenset(
    {"id", "label", "payload", "confirm", "policy_sensitive"}
)


@dataclass(frozen=True)
class ActionRef:
    id: str
    label: str
    payload: dict[str, Any]
    confirm: dict[str, str] | None = None
    policy_sensitive: bool = False

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

    def as_contract(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
            "kind": self.kind,
            "patch_id": self.patch_id,
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
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

    def as_contract(self) -> dict[str, Any]:
        return {
            "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
            "patch_id": self.patch_id,
            "flow": PATCH_REVIEW_FLOW,
            "decision_policy": PATCH_REVIEW_DECISION_POLICY,
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "preview": self.preview.as_contract(),
            "decisions": {
                "apply": self.apply.as_contract(),
                "reject": self.reject.as_contract(),
            },
        }


class PolicyGate(Protocol):
    def allow_action(self, action_id: str, payload: dict[str, Any], *, policy_sensitive: bool) -> bool:
        ...


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
        identity_key = canonical_action_identity_key(action)
        current = by_identity.get(identity_key)
        if current is None or canonical_action_key(action) < canonical_action_key(current):
            by_identity[identity_key] = deepcopy(action)
    return canonicalize_action_order(list(by_identity.values()))


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
            "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
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

    available: list[str] = []
    preview = review.get("preview")
    if (
        isinstance(preview, dict)
        and preview.get("patch_id") == patch_id.strip()
        and preview.get("patch_preview_contract_version") == PATCH_PREVIEW_CONTRACT_VERSION
    ):
        available.append("preview")

    decisions = review.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("Patch review decisions must be a list")
    decision_names = set()
    for entry in decisions:
        if not isinstance(entry, dict):
            continue
        decision = str(entry.get("decision", "")).strip().lower()
        selection = entry.get("selection")
        expected_action_id = {"apply": "apply_patch", "reject": "reject_patch"}.get(decision)
        if (
            expected_action_id is not None
            and entry.get("action_id") == expected_action_id
            and isinstance(selection, dict)
            and selection.get("patch_id") == patch_id.strip()
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
    return {
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


def build_patch_review_availability(card: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    review = build_patch_review_contract(card, patch_id=patch_id)
    return patch_review_availability_from_contract(review)


def resolve_patch_review_contract(card: dict[str, Any], review: dict[str, Any], *, patch_id: str) -> dict[str, Any]:
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch review patch_id is required")
    if not isinstance(review, dict):
        raise ValueError("Patch review contract must be an object")
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
    resolved: dict[str, Any] = {
        "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
        "patch_id": expected_patch_id,
        "flow": PATCH_REVIEW_FLOW,
        "decision_policy": PATCH_REVIEW_DECISION_POLICY,
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
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
    if availability is not None and availability != expected_availability:
        raise ValueError("Patch review availability does not match the current contract")
    return resolved


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
            "selection": deepcopy(selection_by_control[control]),
            "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY[control]),
            "confirm": deepcopy(action_ref.confirm),
            "policy_sensitive": action_ref.policy_sensitive,
        }
    return controls


def patch_review_control_summary_from_contract(
    card: dict[str, Any],
    review: dict[str, Any],
    *,
    patch_id: str,
) -> dict[str, Any]:
    controls = patch_review_control_actions_from_contract(card, review, patch_id=patch_id)
    availability = patch_review_availability_from_contract(review)
    control_plan = patch_review_control_plan_from_contract(card, review, patch_id=patch_id)
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
        "next_required": availability["next_required"],
        "is_complete": availability["is_complete"],
        "controls": deepcopy(controls),
        "control_plan": control_plan,
        "order": ordered_controls,
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
                "slot": slot,
                "action_id": entry["action_id"],
                "action_identity": entry["action_identity"],
                "label": entry["label"],
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
        "selection_model": "one_based_action_slot",
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "is_complete": summary["is_complete"],
        "missing": deepcopy(summary["missing"]),
        "controls": controls,
    }


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
            "status": "missing" if control in missing else "available",
            "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY[control]),
        }
        control_payload = controls.get(control)
        if control_payload is not None:
            entry.update(
                {
                    "slot": control_payload["slot"],
                    "action_id": control_payload["action_id"],
                    "action_identity": control_payload["action_identity"],
                    "label": control_payload["label"],
                    "payload": deepcopy(control_payload["payload"]),
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

    review = card.get("patch_review")
    if not isinstance(review, dict) or review.get("patch_id") != expected_patch_id:
        review = build_complete_patch_review_contract(card, patch_id=expected_patch_id)
    resolve_patch_review_contract(card, review, patch_id=expected_patch_id)
    return complete_patch_review_actions_from_contract(
        card,
        review,
        patch_id=expected_patch_id,
    )


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
    if not isinstance(selection, dict):
        raise ValueError("Action selection must be an object")
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


def action_ref_from_selection(card: dict[str, Any], selection: dict[str, Any]) -> ActionRef:
    action = resolve_card_selection_contract(card, selection)
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
    action = resolve_card_selection_contract(card, selection)
    if action.get("id") not in {"apply_patch", "reject_patch"}:
        raise ValueError("Action selection is not a patch decision")
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
    action = resolve_card_selection_contract(card, selection)
    if action.get("id") != "preview_patch":
        raise ValueError("Action selection is not a patch preview")
    payload = action.get("payload")
    action_patch_id = payload.get("patch_id") if isinstance(payload, dict) else None
    expected_patch_id = patch_id.strip()
    if not expected_patch_id:
        raise ValueError("Patch preview patch_id is required")
    if selection.get("patch_id") != expected_patch_id:
        raise ValueError("Patch preview selection does not match the current patch")
    if selection.get("patch_preview_contract_version") != PATCH_PREVIEW_CONTRACT_VERSION:
        raise ValueError("Unsupported patch preview contract version")
    if action_patch_id != expected_patch_id:
        raise ValueError("Patch preview selection does not match the current patch")
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
        "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
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
    action_id = str(action.get("id", ""))
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
        for key, value in confirm.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Action confirm keys must be non-empty strings")
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Action confirm values must be non-empty strings")
    policy_sensitive = action.get("policy_sensitive", False)
    if not isinstance(policy_sensitive, bool):
        raise ValueError("Action policy_sensitive must be a boolean")


def execute_action_with_policy_gate(
    *,
    action: ActionRef,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    validate_action_ref(action.as_contract())
    if action.id not in _ALLOWED_ACTION_SET:
        raise ValueError("Unknown action id")
    if action.id not in set(capabilities.actions_supported):
        raise ValueError("Action not supported by client")
    if not policy_gate.allow_action(action.id, action.payload, policy_sensitive=action.policy_sensitive):
        raise PermissionError("PolicyGate blocked action")
    return executor(action)


def engine_authoritative_action_ref(action: ActionRef) -> ActionRef:
    validate_action_ref(action.as_contract())
    if action.id in {"preview_patch", *PATCH_DECISION_ACTION_IDS}:
        patch_id = action.payload.get("patch_id")
        if isinstance(patch_id, str):
            normalized_payload = dict(action.payload)
            normalized_payload["patch_id"] = patch_id.strip()
            action = replace(action, payload=normalized_payload)
            validate_action_ref(action.as_contract())
    if action.id in PATCH_DECISION_ACTION_IDS:
        confirm = action.confirm
        confirmation_added = False
        if confirm is None:
            confirm = {"title": PATCH_REVIEW_CONFIRMATION_TITLES[action.id]}
            confirmation_added = True
        if not action.policy_sensitive or confirmation_added:
            return replace(action, confirm=confirm, policy_sensitive=True)
    return action


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


def execute_complete_patch_review_action_with_policy_gate(
    *,
    card: dict[str, Any],
    patch_id: str,
    control: str,
    capabilities: Any,
    policy_gate: PolicyGate,
    executor: Callable[[ActionRef], Any],
) -> Any:
    action = complete_patch_review_action_from_card(card, patch_id=patch_id, control=control)
    return execute_action_with_policy_gate(
        action=engine_authoritative_action_ref(action),
        capabilities=capabilities,
        policy_gate=policy_gate,
        executor=executor,
    )


def _validate_action_payload(action_id: str, payload: dict[str, Any]) -> None:
    schema = _ACTION_SCHEMAS.get(action_id)
    if schema is None:
        raise ValueError(f"Unsupported action id: {action_id}")
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
