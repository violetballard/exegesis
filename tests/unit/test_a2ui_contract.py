from __future__ import annotations

import unittest
from copy import deepcopy
from dataclasses import dataclass

import exegesis_shared.contracts as shared_contracts
from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    PATCH_DECISION_CONTRACT_VERSION,
    PATCH_PREVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_ACTION_AUTHORITY,
    PATCH_REVIEW_CLI_COMMAND_ALIASES,
    PATCH_REVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_DECISION_GROUP,
    PATCH_REVIEW_DECISION_POLICY,
    PATCH_REVIEW_DEMO_PATH_STEP,
    PATCH_REVIEW_EXECUTION_PRECONDITIONS,
    PATCH_REVIEW_EXECUTION_POLICY,
    PATCH_REVIEW_FLOW,
    PATCH_REVIEW_REQUIRED_PARTS,
    materialize_action_selection_contract,
)
from exegesis_shared.contracts import studio_materialize_card as shared_studio_materialize_card
from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    BASKET_CARD_TYPE,
    CONTEXT_SET_CARD_TYPE,
    DEMO_CONTEXT_ACTION_IDS,
    DEMO_CONTEXT_CARD_TYPES,
    CompletePatchReviewActions,
    GENERIC_CARD_TYPE,
    KNOWN_CARD_TYPES,
    PATCH_REVIEW_REQUIRED_PARTS as UI_PATCH_REVIEW_REQUIRED_PARTS,
    PatchReviewActionSelection,
    PATCH_REVIEW_CLI_COMMAND_ALIASES as UI_PATCH_REVIEW_CLI_COMMAND_ALIASES,
    PATCH_REVIEW_DECISION_GROUP as UI_PATCH_REVIEW_DECISION_GROUP,
    PATCH_REVIEW_EXECUTION_PRECONDITIONS as UI_PATCH_REVIEW_EXECUTION_PRECONDITIONS,
    RETRIEVAL_RESULTS_CARD_TYPE,
    action_ref_from_selection,
    build_complete_patch_review_contract,
    build_action_resolved_event,
    build_action_resolved_event_from_selection,
    build_action_selected_event,
    build_action_selected_event_from_selection,
    build_card_published_event,
    build_complete_patch_review_action_resolved_event,
    build_complete_patch_review_action_selected_event,
    build_patch_decision_selection,
    build_patch_preview_selection,
    build_patch_review_availability,
    build_patch_review_contract,
    build_patch_review_selection,
    build_unknown_card,
    complete_patch_review_decision_action_ref_from_cli_command,
    complete_patch_review_action_ref_from_cli_command,
    complete_patch_review_action_from_card,
    complete_patch_review_actions_from_card,
    complete_patch_review_actions_from_contract,
    complete_patch_review_action_refs_from_contract,
    engine_prepare_card,
    execute_complete_patch_review_cli_command_with_policy_gate,
    execute_patch_review_cli_command_with_policy_gate,
    execute_patch_review_control_with_policy_gate,
    execute_complete_patch_review_action_with_policy_gate,
    execute_complete_patch_review_control_with_policy_gate,
    execute_complete_patch_review_selection_with_policy_gate,
    execute_action_with_policy_gate,
    execute_card_selection_with_policy_gate,
    execute_patch_review_decision_cli_command_with_policy_gate,
    execute_complete_patch_review_decision_cli_command_with_policy_gate,
    execute_patch_review_selection_with_policy_gate,
    engine_authoritative_action_ref,
    materialize_card_actions,
    materialize_patch_preview_contract,
    materialize_proposed_edit_card,
    materialize_terminal_card,
    patch_decision_action_ref_from_selection,
    patch_preview_action_ref_from_selection,
    patch_review_action_ref_from_selection,
    patch_review_action_selection_from_selection,
    patch_review_availability_from_contract,
    patch_review_action_ref_from_cli_command,
    patch_review_action_refs_from_contract,
    patch_review_cli_command_lookup_from_contract,
    patch_review_cli_control_map_from_contract,
    patch_review_control_actions_from_contract,
    patch_review_decision_cli_command_lookup_from_contract,
    patch_review_decision_controls_from_contract,
    patch_review_control_plan_from_contract,
    patch_review_control_summary_from_contract,
    patch_review_control_slots_from_contract,
    patch_review_execution_preconditions,
    patch_review_next_control_from_contract,
    patch_review_selection_from_cli_command,
    render_terminal_card,
    resolve_card_selection_contract,
    resolve_card_selection_execution,
    resolve_complete_patch_review_card_cli_command_execution,
    resolve_complete_patch_review_card_control_execution,
    resolve_complete_patch_review_card_decision_cli_command_execution,
    resolve_patch_decision_action,
    resolve_patch_decision_selection,
    resolve_patch_preview_action,
    resolve_patch_preview_selection,
    resolve_complete_patch_review_control_execution,
    resolve_complete_patch_review_cli_command_execution,
    resolve_complete_patch_review_decision_cli_command_execution,
    resolve_patch_review_contract,
    resolve_patch_review_cli_command_execution,
    resolve_patch_review_control_execution,
    resolve_patch_review_decision_cli_command_execution,
    resolve_patch_review_selection,
    studio_materialize_card,
    validate_action_capabilities,
    validate_action_ref,
    validate_basket_card,
    validate_capabilities,
    validate_complete_patch_review_capabilities,
    validate_complete_patch_review_card_capabilities,
    validate_context_set_card,
    validate_demo_context_card_capabilities,
    validate_engine_demo_path_capabilities,
    validate_known_card,
    validate_patch_review_contract,
    validate_retrieval_results_card,
    validate_stream_event,
)


def _capabilities(
    *,
    cards_supported: tuple[str, ...] = ("ProposedEditCard",),
    actions_supported: tuple[str, ...] = (
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
    ),
    max_payload_bytes: int = 1_000_000,
) -> A2UICapabilities:
    return A2UICapabilities(
        a2ui_version=1,
        client_name="Exegesis Studio",
        cards_supported=cards_supported,
        primitive_blocks_supported=(
            "MarkdownBlock",
            "KeyValueBlock",
            "ListBlock",
            "TableBlock",
            "AlertBlock",
            "ProgressBlock",
            "CodeBlock",
        ),
        actions_supported=actions_supported,
        max_payload_bytes=max_payload_bytes,
        supports_streaming=True,
    )


def _patch_review_selection_metadata() -> dict[str, object]:
    return {
        "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
        "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
        "execution_policy": deepcopy(PATCH_REVIEW_EXECUTION_POLICY["apply"]),
        "decision_group": PATCH_REVIEW_DECISION_GROUP,
    }


@dataclass
class _PolicyGateStub:
    allow: bool

    def allow_action(self, *_args, **_kwargs) -> bool:
        return self.allow


@dataclass
class _RecordingPolicyGate:
    allow: bool
    calls: list[tuple[str, dict[str, object], bool]]

    def allow_action(
        self,
        action_id: str,
        payload: dict[str, object],
        *,
        policy_sensitive: bool,
    ) -> bool:
        self.calls.append((action_id, payload, policy_sensitive))
        return self.allow


class A2UIContractTests(unittest.TestCase):
    def test_shared_exports_engine_demo_card_contract_types(self) -> None:
        self.assertIn(RETRIEVAL_RESULTS_CARD_TYPE, KNOWN_CARD_TYPES)
        self.assertIn(BASKET_CARD_TYPE, KNOWN_CARD_TYPES)
        self.assertIn(CONTEXT_SET_CARD_TYPE, KNOWN_CARD_TYPES)
        self.assertIs(shared_contracts.RETRIEVAL_RESULTS_CARD_TYPE, RETRIEVAL_RESULTS_CARD_TYPE)
        self.assertIs(shared_contracts.BASKET_CARD_TYPE, BASKET_CARD_TYPE)
        self.assertIs(shared_contracts.CONTEXT_SET_CARD_TYPE, CONTEXT_SET_CARD_TYPE)
        self.assertEqual(
            DEMO_CONTEXT_CARD_TYPES,
            (RETRIEVAL_RESULTS_CARD_TYPE, BASKET_CARD_TYPE, CONTEXT_SET_CARD_TYPE),
        )
        self.assertEqual(
            shared_contracts.DEMO_CONTEXT_ACTION_IDS,
            DEMO_CONTEXT_ACTION_IDS,
        )

    def test_demo_context_card_capabilities_require_full_context_flow_surface(self) -> None:
        caps = _capabilities(cards_supported=DEMO_CONTEXT_CARD_TYPES)

        validate_demo_context_card_capabilities(caps)
        shared_contracts.validate_demo_context_card_capabilities(caps)

        with self.assertRaisesRegex(
            ValueError,
            "Demo context flow requires card support: ContextSetCard",
        ):
            validate_demo_context_card_capabilities(
                _capabilities(cards_supported=(RETRIEVAL_RESULTS_CARD_TYPE, BASKET_CARD_TYPE))
            )
        with self.assertRaisesRegex(
            ValueError,
            "Demo context flow requires action support: gather_context",
        ):
            validate_demo_context_card_capabilities(
                _capabilities(
                    cards_supported=DEMO_CONTEXT_CARD_TYPES,
                    actions_supported=tuple(
                        action_id
                        for action_id in _capabilities().actions_supported
                        if action_id != "gather_context"
                    ),
                )
            )

    def test_engine_demo_path_capabilities_require_context_and_patch_review(self) -> None:
        cards_supported = DEMO_CONTEXT_CARD_TYPES + ("ProposedEditCard",)
        caps = _capabilities(cards_supported=cards_supported)

        validate_engine_demo_path_capabilities(caps)
        shared_contracts.validate_engine_demo_path_capabilities(caps)

        with self.assertRaisesRegex(
            ValueError,
            "Demo context flow requires card support: BasketCard",
        ):
            validate_engine_demo_path_capabilities(
                _capabilities(
                    cards_supported=(
                        RETRIEVAL_RESULTS_CARD_TYPE,
                        CONTEXT_SET_CARD_TYPE,
                        "ProposedEditCard",
                    )
                )
            )
        with self.assertRaisesRegex(
            ValueError,
            "Complete patch review client support is missing: reject",
        ):
            validate_engine_demo_path_capabilities(
                _capabilities(
                    cards_supported=cards_supported,
                    actions_supported=tuple(
                        action_id
                        for action_id in _capabilities().actions_supported
                        if action_id != "reject_patch"
                    ),
                )
            )

    def test_retrieval_basket_and_context_cards_validate_typed_payloads(self) -> None:
        retrieval_card = {
            "type": RETRIEVAL_RESULTS_CARD_TYPE,
            "title": "Retrieval",
            "query": "chapter five",
            "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
            "actions": [
                {"id": "promote_to_basket", "label": "Add to basket", "payload": {"item_id": "doc-1"}},
                {
                    "id": "pin_to_context_set",
                    "label": "Pin",
                    "payload": {"item_id": "doc-1", "context_set_id": "ctx-1"},
                },
            ],
        }
        basket_card = {
            "type": BASKET_CARD_TYPE,
            "title": "Basket",
            "basket_id": "basket-1",
            "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
            "actions": [
                {"id": "create_context_set", "label": "Create context", "payload": {"name": "Chapter 5"}},
                {
                    "id": "gather_context",
                    "label": "Gather context",
                    "payload": {"basket_id": "basket-1", "context_set_id": "ctx-1"},
                },
            ],
        }
        context_card = {
            "type": CONTEXT_SET_CARD_TYPE,
            "title": "Context",
            "context_set_id": "ctx-1",
            "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
            "actions": [
                {
                    "id": "pin_to_context_set",
                    "label": "Keep pinned",
                    "payload": {"item_id": "doc-1", "context_set_id": "ctx-1"},
                },
                {"id": "run_agent", "label": "Plan", "payload": {"operation": "plan"}},
            ],
        }

        validate_retrieval_results_card(retrieval_card)
        validate_basket_card(basket_card)
        validate_context_set_card(context_card)
        validate_known_card(retrieval_card)
        validate_known_card(basket_card)
        validate_known_card(context_card)

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported payload field\\(s\\) for action 'promote_to_basket': context_set_id",
        ):
            validate_retrieval_results_card(
                {
                    "type": RETRIEVAL_RESULTS_CARD_TYPE,
                    "title": "Retrieval",
                    "query": "chapter five",
                    "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
                    "actions": [
                        {
                            "id": "promote_to_basket",
                            "label": "Add to basket",
                            "payload": {"item_id": "doc-1", "context_set_id": "ctx-1"},
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "RetrievalResultsCard result field 'snippet' is required"):
            validate_retrieval_results_card(
                {
                    "type": RETRIEVAL_RESULTS_CARD_TYPE,
                    "title": "Retrieval",
                    "query": "chapter five",
                    "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": ""}],
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "promote_to_basket item_id must reference a RetrievalResultsCard result",
        ):
            validate_retrieval_results_card(
                {
                    "type": RETRIEVAL_RESULTS_CARD_TYPE,
                    "title": "Retrieval",
                    "query": "chapter five",
                    "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
                    "actions": [
                        {"id": "promote_to_basket", "label": "Add to basket", "payload": {"item_id": "doc-2"}}
                    ],
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "RetrievalResultsCard result item_id entries must be unique: doc-1",
        ):
            validate_retrieval_results_card(
                {
                    "type": RETRIEVAL_RESULTS_CARD_TYPE,
                    "title": "Retrieval",
                    "query": "chapter five",
                    "results": [
                        {"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"},
                        {"item_id": " doc-1 ", "title": "Chapter 5 duplicate", "snippet": "Same source"},
                    ],
                    "actions": [
                        {"id": "promote_to_basket", "label": "Add to basket", "payload": {"item_id": "doc-1"}}
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "Unsupported RetrievalResultsCard field\\(s\\): client_hint"):
            validate_retrieval_results_card(
                {
                    "type": RETRIEVAL_RESULTS_CARD_TYPE,
                    "title": "Retrieval",
                    "query": "chapter five",
                    "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
                    "client_hint": "render-wide",
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported RetrievalResultsCard result field\\(s\\): client_hint",
        ):
            validate_retrieval_results_card(
                {
                    "type": RETRIEVAL_RESULTS_CARD_TYPE,
                    "title": "Retrieval",
                    "query": "chapter five",
                    "results": [
                        {
                            "item_id": "doc-1",
                            "title": "Chapter 5",
                            "snippet": "Relevant paragraph",
                            "client_hint": "render-wide",
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "BasketCard item field 'item_id' is required"):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "items": [{"item_id": " ", "title": "Chapter 5"}],
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "pin_to_context_set item_id must reference a BasketCard item",
        ):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [
                        {
                            "id": "pin_to_context_set",
                            "label": "Pin",
                            "payload": {"item_id": "doc-2", "context_set_id": "ctx-1"},
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "Missing payload field 'context_set_id' for action 'pin_to_context_set'",
        ):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [{"id": "pin_to_context_set", "label": "Pin", "payload": {"item_id": "doc-1"}}],
                }
            )

        with self.assertRaisesRegex(ValueError, "gather_context requires BasketCard basket_id"):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [
                        {
                            "id": "gather_context",
                            "label": "Gather context",
                            "payload": {"basket_id": "basket-1", "context_set_id": "ctx-1"},
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "gather_context basket_id must match BasketCard basket_id"):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "basket_id": "basket-1",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [
                        {
                            "id": "gather_context",
                            "label": "Gather context",
                            "payload": {"basket_id": "basket-2", "context_set_id": "ctx-1"},
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "BasketCard basket_id must be normalized"):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "basket_id": " basket-1 ",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [
                        {
                            "id": "gather_context",
                            "label": "Gather context",
                            "payload": {"basket_id": "basket-1", "context_set_id": "ctx-1"},
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "BasketCard item item_id entries must be unique: doc-1"):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "items": [
                        {"item_id": "doc-1", "title": "Chapter 5"},
                        {"item_id": " doc-1 ", "title": "Chapter 5 duplicate"},
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "Unsupported BasketCard field\\(s\\): client_hint"):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "client_hint": "render-wide",
                }
            )

        with self.assertRaisesRegex(ValueError, "Unsupported BasketCard item field\\(s\\): client_hint"):
            validate_basket_card(
                {
                    "type": BASKET_CARD_TYPE,
                    "title": "Basket",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5", "client_hint": "render-wide"}],
                }
            )

        with self.assertRaisesRegex(ValueError, "ContextSetCard context_set_id is required"):
            validate_context_set_card(
                {
                    "type": CONTEXT_SET_CARD_TYPE,
                    "title": "Context",
                    "context_set_id": "",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "open_corpus_item item_id must reference a ContextSetCard item",
        ):
            validate_context_set_card(
                {
                    "type": CONTEXT_SET_CARD_TYPE,
                    "title": "Context",
                    "context_set_id": "ctx-1",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [{"id": "open_corpus_item", "label": "Open", "payload": {"item_id": "doc-2"}}],
                }
            )

        with self.assertRaisesRegex(
            ValueError,
            "pin_to_context_set context_set_id must match ContextSetCard context_set_id",
        ):
            validate_context_set_card(
                {
                    "type": CONTEXT_SET_CARD_TYPE,
                    "title": "Context",
                    "context_set_id": "ctx-1",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [
                        {
                            "id": "pin_to_context_set",
                            "label": "Pin",
                            "payload": {"item_id": "doc-1", "context_set_id": "ctx-2"},
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "ContextSetCard context_set_id must be normalized"):
            validate_context_set_card(
                {
                    "type": CONTEXT_SET_CARD_TYPE,
                    "title": "Context",
                    "context_set_id": " ctx-1 ",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "actions": [
                        {
                            "id": "pin_to_context_set",
                            "label": "Pin",
                            "payload": {"item_id": "doc-1", "context_set_id": "ctx-1"},
                        }
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "ContextSetCard item item_id entries must be unique: doc-1"):
            validate_context_set_card(
                {
                    "type": CONTEXT_SET_CARD_TYPE,
                    "title": "Context",
                    "context_set_id": "ctx-1",
                    "items": [
                        {"item_id": "doc-1", "title": "Chapter 5"},
                        {"item_id": " doc-1 ", "title": "Chapter 5 duplicate"},
                    ],
                }
            )

        with self.assertRaisesRegex(ValueError, "Unsupported ContextSetCard field\\(s\\): client_hint"):
            validate_context_set_card(
                {
                    "type": CONTEXT_SET_CARD_TYPE,
                    "title": "Context",
                    "context_set_id": "ctx-1",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                    "client_hint": "render-wide",
                }
            )

        with self.assertRaisesRegex(ValueError, "Unsupported ContextSetCard item field\\(s\\): client_hint"):
            validate_context_set_card(
                {
                    "type": CONTEXT_SET_CARD_TYPE,
                    "title": "Context",
                    "context_set_id": "ctx-1",
                    "items": [{"item_id": "doc-1", "title": "Chapter 5", "client_hint": "render-wide"}],
                }
            )

    def test_known_cards_reject_stale_embedded_action_selection_contracts(self) -> None:
        card = {
            "type": RETRIEVAL_RESULTS_CARD_TYPE,
            "title": "Retrieval",
            "query": "chapter five",
            "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
            "actions": [
                {"id": "promote_to_basket", "label": "Add", "payload": {"item_id": "doc-1"}},
            ],
        }
        card["action_selection"] = materialize_action_selection_contract(card)
        validate_retrieval_results_card(card)

        stale = deepcopy(card)
        stale["action_selection"] = deepcopy(card["action_selection"])
        stale["action_selection"]["order"][0]["action_identity"] = "stale-client-selection"

        with self.assertRaisesRegex(
            ValueError,
            "RetrievalResultsCard action_selection must match materialized actions",
        ):
            validate_retrieval_results_card(stale)

    def test_known_card_validator_covers_full_known_card_registry(self) -> None:
        generic_card = {
            "type": GENERIC_CARD_TYPE,
            "title": "Run log",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Ready"}],
        }
        patch_card = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
            "actions": [
                {"id": "preview_patch", "label": "Preview patch", "payload": {"patch_id": "patch-1"}},
                {
                    "id": "apply_patch",
                    "label": "Apply patch",
                    "payload": {"patch_id": "patch-1"},
                    "confirm": {"title": "Apply patch?"},
                    "policy_sensitive": True,
                },
                {
                    "id": "reject_patch",
                    "label": "Reject patch",
                    "payload": {"patch_id": "patch-1"},
                    "confirm": {"title": "Reject patch?"},
                    "policy_sensitive": True,
                },
            ],
        }

        validate_known_card(generic_card)
        validate_known_card(patch_card)

        self.assertTrue({GENERIC_CARD_TYPE, "ProposedEditCard"}.issubset(set(KNOWN_CARD_TYPES)))

    def test_engine_known_card_fallback_preserves_supported_typed_actions(self) -> None:
        card = {
            "type": RETRIEVAL_RESULTS_CARD_TYPE,
            "title": "Retrieval",
            "query": "chapter five",
            "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
            "actions": [
                {
                    "id": "pin_to_context_set",
                    "label": "Pin",
                    "payload": {"item_id": "doc-1", "context_set_id": "ctx-1"},
                },
                {"id": "promote_to_basket", "label": "Add to basket", "payload": {"item_id": "doc-1"}},
                {"id": "open_corpus_item", "label": "Open", "payload": {"item_id": "doc-1"}},
            ],
        }
        prepared = engine_prepare_card(
            card,
            _capabilities(
                cards_supported=("GenericCard",),
                actions_supported=("pin_to_context_set", "promote_to_basket"),
            ),
        )

        self.assertEqual(prepared["type"], "GenericCard")
        self.assertEqual([action["id"] for action in prepared["actions"]], ["promote_to_basket", "pin_to_context_set"])
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in prepared["action_selection"]["order"]],
            [(1, "promote_to_basket"), (2, "pin_to_context_set")],
        )

    def test_capabilities_handshake_is_stored_per_session(self) -> None:
        store = A2UISessionStore()
        caps = _capabilities()
        validate_capabilities(caps)
        store.register("sess-1", caps)
        self.assertEqual(store.get("sess-1").client_name, "Exegesis Studio")

    def test_complete_patch_review_card_capabilities_require_card_and_actions(self) -> None:
        caps = _capabilities(cards_supported=("ProposedEditCard", "GenericCard"))

        validate_complete_patch_review_card_capabilities(caps)
        shared_contracts.validate_complete_patch_review_card_capabilities(caps)

        with self.assertRaisesRegex(ValueError, "requires ProposedEditCard support"):
            validate_complete_patch_review_card_capabilities(
                _capabilities(cards_supported=("GenericCard",))
            )

        with self.assertRaisesRegex(ValueError, "Complete patch review client support is missing: reject"):
            validate_complete_patch_review_card_capabilities(
                _capabilities(
                    cards_supported=("ProposedEditCard",),
                    actions_supported=("preview_patch", "apply_patch"),
                )
            )

    def test_complete_patch_review_card_execution_requires_card_capability(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "requires ProposedEditCard support"):
            resolve_complete_patch_review_card_control_execution(
                card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(cards_supported=("GenericCard",)),
            )

        execution = resolve_complete_patch_review_card_control_execution(
            card,
            patch_id="p1",
            control="apply",
            capabilities=_capabilities(cards_supported=("ProposedEditCard", "GenericCard")),
        )

        self.assertEqual(execution["action_id"], "apply_patch")
        self.assertEqual(execution["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(execution["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertIs(
            shared_contracts.resolve_complete_patch_review_card_control_execution,
            resolve_complete_patch_review_card_control_execution,
        )

    def test_complete_patch_review_card_cli_execution_requires_card_capability(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "requires ProposedEditCard support"):
            resolve_complete_patch_review_card_cli_command_execution(
                card,
                patch_id="p1",
                command="apply",
                capabilities=_capabilities(cards_supported=("GenericCard",)),
            )

        execution = resolve_complete_patch_review_card_cli_command_execution(
            card,
            patch_id="p1",
            command="reject_patch",
            capabilities=_capabilities(cards_supported=("ProposedEditCard", "GenericCard")),
        )

        self.assertEqual(execution["control"], "reject")
        self.assertEqual(execution["action_id"], "reject_patch")
        self.assertIs(
            shared_contracts.resolve_complete_patch_review_card_cli_command_execution,
            resolve_complete_patch_review_card_cli_command_execution,
        )

        decision = resolve_complete_patch_review_card_decision_cli_command_execution(
            card,
            patch_id="p1",
            command="reject",
            capabilities=_capabilities(cards_supported=("ProposedEditCard", "GenericCard")),
        )
        self.assertEqual(decision["control"], "reject")
        self.assertIs(
            shared_contracts.resolve_complete_patch_review_card_decision_cli_command_execution,
            resolve_complete_patch_review_card_decision_cli_command_execution,
        )

    def test_capabilities_reject_duplicate_advertised_contracts(self) -> None:
        with self.assertRaisesRegex(ValueError, "cards_supported entries must be unique: ProposedEditCard"):
            validate_capabilities(
                _capabilities(cards_supported=("ProposedEditCard", "ProposedEditCard")),
            )

        with self.assertRaisesRegex(ValueError, "actions_supported entries must be unique: apply_patch"):
            validate_capabilities(
                _capabilities(actions_supported=("preview_patch", "apply_patch", "apply_patch")),
            )
        with self.assertRaisesRegex(ValueError, "actions_supported entries must be unique: apply_patch"):
            validate_action_capabilities(
                _capabilities(actions_supported=("preview_patch", "apply_patch", "apply_patch")),
            )
        with self.assertRaisesRegex(ValueError, "actions_supported entries must be unique: apply_patch"):
            validate_complete_patch_review_capabilities(
                _capabilities(actions_supported=("preview_patch", "apply_patch", "apply_patch", "reject_patch")),
            )

        with self.assertRaisesRegex(
            ValueError,
            "primitive_blocks_supported entries must be unique: MarkdownBlock",
        ):
            validate_capabilities(
                A2UICapabilities(
                    a2ui_version=1,
                    client_name="Exegesis Studio",
                    cards_supported=("ProposedEditCard",),
                    primitive_blocks_supported=(
                        "MarkdownBlock",
                        "MarkdownBlock",
                        "KeyValueBlock",
                        "ListBlock",
                        "TableBlock",
                        "AlertBlock",
                        "ProgressBlock",
                        "CodeBlock",
                    ),
                    actions_supported=("preview_patch", "apply_patch", "reject_patch"),
                    max_payload_bytes=1_000_000,
                    supports_streaming=True,
                ),
            )

    def test_session_store_rejects_invalid_capabilities_before_registration(self) -> None:
        store = A2UISessionStore()
        caps = _capabilities(actions_supported=("apply_patch", "delete_project"))

        with self.assertRaisesRegex(ValueError, "Unknown action in capabilities"):
            store.register("sess-1", caps)

        with self.assertRaisesRegex(KeyError, "Unknown session"):
            store.get("sess-1")

    def test_session_store_rejects_malformed_capability_lists_before_registration(self) -> None:
        store = A2UISessionStore()
        caps = A2UICapabilities(
            a2ui_version=1,
            client_name="Exegesis Studio",
            cards_supported=["ProposedEditCard"],  # type: ignore[arg-type]
            primitive_blocks_supported=(
                "MarkdownBlock",
                "KeyValueBlock",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
            actions_supported=("preview_patch", "apply_patch", "reject_patch"),
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )

        with self.assertRaisesRegex(ValueError, "cards_supported must be a tuple"):
            store.register("sess-1", caps)

        with self.assertRaisesRegex(KeyError, "Unknown session"):
            store.get("sess-1")

    def test_card_materialization_revalidates_malformed_capabilities(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Review patch"}],
            "actions": [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}}],
        }

        with self.assertRaisesRegex(ValueError, "Unknown action in capabilities: delete_everything"):
            studio_materialize_card(
                card,
                _capabilities(actions_supported=("apply_patch", "delete_everything")),
            )

        with self.assertRaisesRegex(ValueError, "Missing required primitive block support"):
            engine_prepare_card(
                card,
                A2UICapabilities(
                    a2ui_version=1,
                    client_name="CLI",
                    cards_supported=("GenericCard",),
                    primitive_blocks_supported=("MarkdownBlock",),
                    actions_supported=("apply_patch",),
                    max_payload_bytes=1_000_000,
                    supports_streaming=True,
                ),
            )

    def test_session_store_rejects_untyped_streaming_flag_before_registration(self) -> None:
        store = A2UISessionStore()
        caps = A2UICapabilities(
            a2ui_version=1,
            client_name="Exegesis Studio",
            cards_supported=("ProposedEditCard",),
            primitive_blocks_supported=(
                "MarkdownBlock",
                "KeyValueBlock",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
            actions_supported=("preview_patch", "apply_patch", "reject_patch"),
            max_payload_bytes=1_000_000,
            supports_streaming="yes",  # type: ignore[arg-type]
        )

        with self.assertRaisesRegex(ValueError, "supports_streaming must be a boolean"):
            store.register("sess-1", caps)

        with self.assertRaisesRegex(KeyError, "Unknown session"):
            store.get("sess-1")

    def test_session_store_rejects_untyped_numeric_handshake_fields_before_registration(self) -> None:
        store = A2UISessionStore()
        caps = _capabilities()
        invalid_version = A2UICapabilities(
            a2ui_version=True,  # type: ignore[arg-type]
            client_name=caps.client_name,
            cards_supported=caps.cards_supported,
            primitive_blocks_supported=caps.primitive_blocks_supported,
            actions_supported=caps.actions_supported,
            max_payload_bytes=caps.max_payload_bytes,
            supports_streaming=caps.supports_streaming,
        )

        with self.assertRaisesRegex(ValueError, "a2ui_version must be a positive integer"):
            store.register("sess-1", invalid_version)

        invalid_payload_limit = A2UICapabilities(
            a2ui_version=caps.a2ui_version,
            client_name=caps.client_name,
            cards_supported=caps.cards_supported,
            primitive_blocks_supported=caps.primitive_blocks_supported,
            actions_supported=caps.actions_supported,
            max_payload_bytes=False,  # type: ignore[arg-type]
            supports_streaming=caps.supports_streaming,
        )

        with self.assertRaisesRegex(ValueError, "max_payload_bytes must be a positive integer"):
            store.register("sess-1", invalid_payload_limit)

        with self.assertRaisesRegex(KeyError, "Unknown session"):
            store.get("sess-1")

    def test_session_store_requires_stable_session_id(self) -> None:
        store = A2UISessionStore()

        with self.assertRaisesRegex(ValueError, "session_id is required"):
            store.register(" ", _capabilities())

    def test_capability_names_must_be_normalized_before_registration(self) -> None:
        caps = _capabilities()
        store = A2UISessionStore()

        padded_action = A2UICapabilities(
            a2ui_version=caps.a2ui_version,
            client_name=caps.client_name,
            cards_supported=caps.cards_supported,
            primitive_blocks_supported=caps.primitive_blocks_supported,
            actions_supported=("preview_patch", " apply_patch ", "reject_patch"),
            max_payload_bytes=caps.max_payload_bytes,
            supports_streaming=caps.supports_streaming,
        )
        with self.assertRaisesRegex(ValueError, "actions_supported entries must be normalized"):
            store.register("sess-actions", padded_action)

        padded_card = A2UICapabilities(
            a2ui_version=caps.a2ui_version,
            client_name=caps.client_name,
            cards_supported=(" ProposedEditCard ",),
            primitive_blocks_supported=caps.primitive_blocks_supported,
            actions_supported=caps.actions_supported,
            max_payload_bytes=caps.max_payload_bytes,
            supports_streaming=caps.supports_streaming,
        )
        with self.assertRaisesRegex(ValueError, "cards_supported entries must be normalized"):
            validate_capabilities(padded_card)

        padded_block = A2UICapabilities(
            a2ui_version=caps.a2ui_version,
            client_name=caps.client_name,
            cards_supported=caps.cards_supported,
            primitive_blocks_supported=(
                "MarkdownBlock",
                " KeyValueBlock ",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
            actions_supported=caps.actions_supported,
            max_payload_bytes=caps.max_payload_bytes,
            supports_streaming=caps.supports_streaming,
        )
        with self.assertRaisesRegex(ValueError, "primitive_blocks_supported entries must be normalized"):
            validate_capabilities(padded_block)

    def test_engine_falls_back_to_generic_for_unsupported_specialized_card(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {"type": "RunDecisionCard", "title": "Patch"}
        card = engine_prepare_card(payload, caps)
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["blocks"][0]["type"], "AlertBlock")

    def test_engine_falls_back_for_unknown_card_even_when_client_advertises_it(self) -> None:
        caps = _capabilities(cards_supported=("RunDecisionCard",))
        payload = {
            "type": "RunDecisionCard",
            "title": "Patch",
            "actions": [
                {"id": "run_agent", "label": "Run unsafe", "payload": {"operation": "revise"}}
            ],
        }

        card = engine_prepare_card(payload, caps)

        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["title"], "Fallback view for RunDecisionCard")
        self.assertEqual(card["actions"][0]["id"], "run_agent")

    def test_engine_generic_fallback_preserves_supported_patch_decisions(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
            "actions": [],
        }

        card = engine_prepare_card(payload, caps)
        selection = build_patch_decision_selection(card, patch_id="patch-1", decision="apply")
        action = resolve_patch_decision_selection(card, selection, patch_id="patch-1")

        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual([action["id"] for action in card["actions"]], ["preview_patch", "apply_patch", "reject_patch"])
        self.assertEqual(card["patch_decision"]["patch_id"], "patch-1")
        self.assertEqual(action["payload"], {"patch_id": "patch-1"})

    def test_engine_generic_fallback_filters_unsupported_patch_decisions(self) -> None:
        caps = _capabilities(
            cards_supported=("RunLogCard",),
            actions_supported=("preview_patch", "reject_patch"),
        )
        payload = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
            "actions": [],
        }

        card = engine_prepare_card(payload, caps)

        self.assertEqual([action["id"] for action in card["actions"]], ["preview_patch", "reject_patch"])
        with self.assertRaisesRegex(ValueError, "not available"):
            build_patch_decision_selection(card, patch_id="patch-1", decision="apply")

    def test_engine_supported_proposed_edit_card_filters_unsupported_patch_decisions(self) -> None:
        caps = _capabilities(actions_supported=("preview_patch", "reject_patch"))
        payload = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
            "actions": [],
        }

        card = engine_prepare_card(payload, caps)

        self.assertEqual(card["type"], "ProposedEditCard")
        self.assertEqual([action["id"] for action in card["actions"]], ["preview_patch", "reject_patch"])
        self.assertEqual(card["patch_review"]["availability"]["missing"], ["apply"])
        with self.assertRaisesRegex(ValueError, "not available"):
            build_patch_decision_selection(card, patch_id="patch-1", decision="apply")

    def test_engine_rejects_cards_over_negotiated_payload_limit(self) -> None:
        caps = _capabilities(max_payload_bytes=100)
        payload = {
            "type": "GenericCard",
            "title": "Oversized",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x" * 200}],
            "actions": [],
        }

        with self.assertRaisesRegex(ValueError, "max_payload_bytes"):
            engine_prepare_card(payload, caps)

    def test_proposed_edit_card_materializes_patch_actions_for_cli_fallback(self) -> None:
        card = {
            "type": "ProposedEditCard",
            "patch_id": " patch-1 ",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
            "actions": [],
        }

        materialized = studio_materialize_card(card, _capabilities())

        self.assertEqual(materialized["patch_id"], "patch-1")
        self.assertEqual(
            [action["id"] for action in materialized["actions"]],
            ["preview_patch", "apply_patch", "reject_patch"],
        )
        self.assertEqual(
            [action["payload"] for action in materialized["actions"]],
            [{"patch_id": "patch-1"}, {"patch_id": "patch-1"}, {"patch_id": "patch-1"}],
        )
        apply_action = materialized["actions"][1]
        reject_action = materialized["actions"][2]
        self.assertEqual(apply_action["confirm"], {"title": "Apply patch?"})
        self.assertTrue(apply_action["policy_sensitive"])
        self.assertEqual(reject_action["confirm"], {"title": "Reject patch?"})
        self.assertTrue(reject_action["policy_sensitive"])
        self.assertEqual(materialized["patch_decision"]["contract_version"], PATCH_DECISION_CONTRACT_VERSION)
        self.assertEqual(materialized["patch_decision"]["patch_id"], "patch-1")
        self.assertEqual(
            [
                entry["selection"]["patch_decision_contract_version"]
                for entry in materialized["patch_decision"]["decisions"]
            ],
            [PATCH_DECISION_CONTRACT_VERSION, PATCH_DECISION_CONTRACT_VERSION],
        )
        self.assertEqual(
            [
                (entry["decision"], entry["slot"], entry["action_id"])
                for entry in materialized["patch_decision"]["decisions"]
            ],
            [("apply", 2, "apply_patch"), ("reject", 3, "reject_patch")],
        )

    def test_proposed_edit_card_replaces_malformed_same_patch_actions_for_cli_fallback(self) -> None:
        card = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
            "actions": [
                {
                    "id": "apply_patch",
                    "label": "Unsafe apply",
                    "payload": {"patch_id": "patch-1"},
                    "target_file": "chapter.md",
                },
                {
                    "id": "preview_patch",
                    "label": "Preview patch",
                    "payload": {"patch_id": "patch-1"},
                },
            ],
        }

        materialized = studio_materialize_card(card, _capabilities())

        self.assertEqual(
            [action["id"] for action in materialized["actions"]],
            ["preview_patch", "apply_patch", "reject_patch"],
        )
        self.assertNotIn("target_file", materialized["actions"][1])
        self.assertEqual(materialized["patch_review"]["availability"]["missing"], [])
        self.assertTrue(materialized["patch_review"]["availability"]["is_complete"])

    def test_proposed_edit_card_replaces_unsafe_same_patch_decision_actions(self) -> None:
        card = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
            "actions": [
                {
                    "id": "apply_patch",
                    "label": "Apply without gate",
                    "payload": {"patch_id": "patch-1"},
                },
                {
                    "id": "reject_patch",
                    "label": "Reject without gate",
                    "payload": {"patch_id": "patch-1"},
                },
            ],
        }

        materialized = studio_materialize_card(card, _capabilities())

        apply_action = materialized["actions"][1]
        reject_action = materialized["actions"][2]
        self.assertEqual(apply_action["label"], "Apply patch")
        self.assertEqual(apply_action["confirm"], {"title": "Apply patch?"})
        self.assertTrue(apply_action["policy_sensitive"])
        self.assertEqual(reject_action["label"], "Reject patch")
        self.assertEqual(reject_action["confirm"], {"title": "Reject patch?"})
        self.assertTrue(reject_action["policy_sensitive"])

    def test_generated_patch_decision_action_refs_preserve_policy_gate_metadata(self) -> None:
        card = studio_materialize_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "patch-1",
                "title": "Preview patch",
                "blocks": [{"type": "MarkdownBlock", "markdown": "```diff\n+new\n```"}],
                "actions": [],
            },
            _capabilities(),
        )

        apply_ref = patch_decision_action_ref_from_selection(
            card,
            build_patch_decision_selection(card, patch_id="patch-1", decision="apply"),
            patch_id="patch-1",
        )
        reject_ref = patch_decision_action_ref_from_selection(
            card,
            build_patch_decision_selection(card, patch_id="patch-1", decision="reject"),
            patch_id="patch-1",
        )

        self.assertEqual(apply_ref.confirm, {"title": "Apply patch?"})
        self.assertTrue(apply_ref.policy_sensitive)
        self.assertEqual(reject_ref.confirm, {"title": "Reject patch?"})
        self.assertTrue(reject_ref.policy_sensitive)

    def test_engine_authoritative_patch_actions_normalize_labels_and_payloads(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "title": "Patch",
                "patch_id": "patch-1",
                "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
                "actions": [
                    {
                        "id": "apply_patch",
                        "label": " Apply patch ",
                        "payload": {"patch_id": " patch-1 "},
                    },
                    {
                        "id": "reject_patch",
                        "label": " Reject patch ",
                        "payload": {"patch_id": " patch-1 "},
                    },
                ],
            }
        )

        self.assertEqual([action["label"] for action in card["actions"]], ["Apply patch", "Reject patch"])
        self.assertEqual([action["payload"]["patch_id"] for action in card["actions"]], ["patch-1", "patch-1"])
        self.assertEqual(card["patch_review"]["decisions"][0]["selection"]["patch_id"], "patch-1")

    def test_proposed_edit_patch_actions_match_normalized_patch_id(self) -> None:
        card = studio_materialize_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "patch_id": " patch-1 ",
                "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
                "actions": [
                    {
                        "id": "apply_patch",
                        "label": " Apply patch ",
                        "payload": {"patch_id": " patch-1 "},
                    },
                    {
                        "id": "reject_patch",
                        "label": " Reject patch ",
                        "payload": {"patch_id": " patch-1 "},
                    },
                ],
            },
            _capabilities(cards_supported=("ProposedEditCard",)),
        )

        self.assertEqual(card["patch_id"], "patch-1")
        self.assertEqual(
            [action["id"] for action in card["actions"]],
            ["preview_patch", "apply_patch", "reject_patch"],
        )
        self.assertEqual([action["payload"]["patch_id"] for action in card["actions"]], ["patch-1"] * 3)
        self.assertEqual(card["patch_review"]["preview"]["patch_id"], "patch-1")
        self.assertEqual(
            [entry["selection"]["patch_id"] for entry in card["patch_review"]["decisions"]],
            ["patch-1", "patch-1"],
        )

    def test_cli_fallback_materialization_enforces_negotiated_payload_limit(self) -> None:
        card = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Oversized patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x" * 200}],
            "actions": [],
        }

        with self.assertRaisesRegex(ValueError, "max_payload_bytes"):
            studio_materialize_card(card, _capabilities(max_payload_bytes=160))

    def test_proposed_edit_card_rejects_mismatched_patch_actions(self) -> None:
        card = {
            "type": "ProposedEditCard",
            "patch_id": "patch-1",
            "title": "Preview patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "other"}},
            ],
        }

        with self.assertRaisesRegex(ValueError, "must match ProposedEditCard patch_id"):
            materialize_proposed_edit_card(card)

    def test_primitive_blocks_require_typed_payload_fields(self) -> None:
        malformed = {
            "type": "GenericCard",
            "title": "Bad blocks",
            "blocks": [{"type": "MarkdownBlock", "markdown": ["not", "text"]}],
            "actions": [],
        }

        with self.assertRaisesRegex(ValueError, "MarkdownBlock field 'markdown' must be str"):
            studio_materialize_card(malformed, _capabilities())

    def test_unknown_card_fallback_filters_invalid_nested_primitive_blocks(self) -> None:
        card = build_unknown_card(
            {
                "type": "FuturePatchCard",
                "title": "Future patch",
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": ["not", "text"]},
                    {"type": "MarkdownBlock", "markdown": "safe preview"},
                ],
            }
        )

        self.assertEqual(card["blocks"][0], {"type": "MarkdownBlock", "markdown": "safe preview"})
        self.assertEqual(card["blocks"][1]["type"], "KeyValueBlock")
        self.assertEqual(card["blocks"][1]["items"][0], {"key": "original_type", "value": "FuturePatchCard"})
        self.assertEqual(card["blocks"][2]["type"], "CodeBlock")

    def test_studio_renders_unknown_card_for_unsupported_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertIn("Unsupported card type", card["title"])
        self.assertEqual(card["actions"][0]["id"], "copy_to_clipboard")

    def test_studio_renders_unknown_card_even_when_client_advertises_unknown_type(self) -> None:
        caps = _capabilities(cards_supported=("QuestionsCard",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertIn("Unsupported card type: QuestionsCard", card["title"])

    def test_studio_renders_unknown_card_for_unsupported_known_card_type(self) -> None:
        caps = _capabilities(
            cards_supported=("GenericCard",),
            actions_supported=("open_corpus_item", "promote_to_basket"),
        )
        payload = {
            "type": RETRIEVAL_RESULTS_CARD_TYPE,
            "title": "Retrieval",
            "query": "chapter five",
            "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
            "actions": [
                {"id": "promote_to_basket", "label": "Add to basket", "payload": {"item_id": "doc-1"}},
                {"id": "open_corpus_item", "label": "Open", "payload": {"item_id": "doc-1"}},
            ],
        }

        card = studio_materialize_card(payload, caps)

        self.assertEqual(card["type"], "UnknownCard")
        self.assertIn("Unsupported card type: RetrievalResultsCard", card["title"])
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in card["action_selection"]["order"]],
            [(1, "open_corpus_item"), (2, "promote_to_basket")],
        )

    def test_unsupported_proposed_edit_card_degrades_to_unknown_with_patch_controls(self) -> None:
        caps = _capabilities(
            cards_supported=("GenericCard",),
            actions_supported=("preview_patch", "apply_patch", "reject_patch"),
        )
        payload = {
            "type": "ProposedEditCard",
            "title": "Patch",
            "patch_id": "p1",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [],
        }

        card = studio_materialize_card(payload, caps)

        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["patch_id"], "p1")
        self.assertIn("Unsupported card type: ProposedEditCard", card["title"])
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in card["action_selection"]["order"]],
            [(1, "preview_patch"), (2, "apply_patch"), (3, "reject_patch")],
        )

    def test_unknown_card_fallback_honors_supported_actions(self) -> None:
        caps = _capabilities(
            cards_supported=("RunLogCard",),
            actions_supported=("apply_patch", "reject_patch"),
        )
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["actions"], [])
        self.assertEqual(card["action_selection"]["order"], [])

    def test_unknown_or_invalid_actions_are_filtered_client_side(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch",))
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                {"id": "run_agent", "label": "Run", "payload": {"operation": "x"}},
                {"id": "apply_patch", "label": "Broken", "payload": {}},
            ],
        }
        filtered = studio_materialize_card(card, caps)
        self.assertEqual(len(filtered["actions"]), 1)
        self.assertEqual(filtered["actions"][0]["id"], "apply_patch")

    def test_blank_patch_action_identifiers_are_filtered_client_side(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch", "reject_patch"))
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "   "}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": ""}},
                {"id": "apply_patch", "label": "Apply p1", "payload": {"patch_id": "p1"}},
            ],
        }

        filtered = studio_materialize_card(card, caps)

        self.assertEqual([action["payload"]["patch_id"] for action in filtered["actions"]], ["p1"])

    def test_shared_contract_export_materializes_versioned_action_selection(self) -> None:
        caps = _capabilities(actions_supported=("reject_patch", "apply_patch"))
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                {"id": "run_agent", "label": "Run", "payload": {"operation": "draft"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }

        materialized = shared_studio_materialize_card(card, caps)

        self.assertEqual(materialized["action_selection"]["contract_version"], ACTION_SELECTION_CONTRACT_VERSION)
        self.assertEqual(materialized["action_selection"]["selection_model"], "one_based_action_slot")
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in materialized["action_selection"]["order"]],
            [(1, "apply_patch"), (2, "reject_patch")],
        )
        self.assertEqual([action["id"] for action in materialized["actions"]], ["apply_patch", "reject_patch"])

    def test_shared_contract_exports_no_terminal_renderer(self) -> None:
        self.assertFalse(hasattr(shared_contracts, "render_terminal_card"))
        self.assertFalse(hasattr(shared_contracts, "materialize_terminal_card"))

    def test_shared_selection_contract_is_versioned_and_cli_consumable(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "run_agent", "label": "Revise", "payload": {"operation": "revise"}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }

        fallback = materialize_terminal_card(card)
        text = render_terminal_card(card)

        self.assertEqual([action["id"] for action in fallback["actions"]], ["apply_patch", "reject_patch", "run_agent"])
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in fallback["action_selection"]["order"]],
            [(1, "apply_patch"), (2, "reject_patch"), (3, "run_agent")],
        )
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("* ")],
            [
                "* 1. Apply [confirm: Apply patch?]",
                "* 2. Reject [confirm: Reject patch?]",
                "* 3. Revise",
            ],
        )

    def test_shared_selection_contract_resolves_only_current_slot_identity(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply A", "payload": {"patch_id": "a"}},
                {"id": "apply_patch", "label": "Apply B", "payload": {"patch_id": "b"}},
            ],
        }
        fallback = materialize_terminal_card(card)
        second_slot = fallback["action_selection"]["order"][1]

        action = resolve_card_selection_contract(
            fallback,
            {
                "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                "selection_model": "one_based_action_slot",
                "slot": second_slot["slot"],
                "action_identity": second_slot["action_identity"],
            },
        )

        self.assertEqual(action["payload"], {"patch_id": "b"})

        with self.assertRaisesRegex(ValueError, "identity does not match"):
            resolve_card_selection_contract(
                fallback,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": second_slot["slot"],
                    "action_identity": fallback["action_selection"]["order"][0]["action_identity"],
                },
            )

        with self.assertRaisesRegex(ValueError, "Unsupported action selection field"):
            resolve_card_selection_contract(
                fallback,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": second_slot["slot"],
                    "action_identity": second_slot["action_identity"],
                    "client_note": "apply the second patch",
                },
            )

    def test_patch_decision_selection_must_match_current_patch(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "open_section", "label": "Open", "payload": {"section_id": "intro"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        apply_slot = card["action_selection"]["order"][0]
        open_slot = card["action_selection"]["order"][2]

        action = resolve_patch_decision_selection(
            card,
            {
                "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                "selection_model": "one_based_action_slot",
                "slot": apply_slot["slot"],
                "action_identity": apply_slot["action_identity"],
                **_patch_review_selection_metadata(),
                "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
                "patch_decision": "apply",
                "patch_id": "p1",
            },
            patch_id=" p1 ",
        )
        self.assertEqual(action["id"], "apply_patch")

        with self.assertRaisesRegex(ValueError, "current patch"):
            resolve_patch_decision_selection(
                card,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": apply_slot["slot"],
                    "action_identity": apply_slot["action_identity"],
                    **_patch_review_selection_metadata(),
                    "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
                    "patch_decision": "apply",
                    "patch_id": "p1",
                },
                patch_id="p2",
            )
        with self.assertRaisesRegex(ValueError, "not a patch decision"):
            resolve_patch_decision_selection(
                card,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": open_slot["slot"],
                    "action_identity": open_slot["action_identity"],
                    **_patch_review_selection_metadata(),
                    "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
                    "patch_decision": "apply",
                    "patch_id": "p1",
                },
                patch_id="p1",
            )
        with self.assertRaisesRegex(ValueError, "Unsupported patch decision selection field"):
            resolve_patch_decision_selection(
                card,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": apply_slot["slot"],
                    "action_identity": apply_slot["action_identity"],
                    **_patch_review_selection_metadata(),
                    "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
                    "patch_decision": "apply",
                    "patch_id": "p1",
                    "client_note": "apply without preview",
                },
                patch_id="p1",
            )

    def test_patch_decision_selection_revalidates_typed_decision_metadata(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        apply_slot = card["action_selection"]["order"][0]

        with self.assertRaisesRegex(ValueError, "must include patch_decision"):
            resolve_patch_decision_selection(
                card,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": apply_slot["slot"],
                    "action_identity": apply_slot["action_identity"],
                    **_patch_review_selection_metadata(),
                    "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
                    "patch_id": "p1",
                },
                patch_id="p1",
            )
        with self.assertRaisesRegex(ValueError, "selected action"):
            resolve_patch_decision_selection(
                card,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": apply_slot["slot"],
                    "action_identity": apply_slot["action_identity"],
                    **_patch_review_selection_metadata(),
                    "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
                    "patch_decision": "reject",
                    "patch_id": "p1",
                },
                patch_id="p1",
            )
        with self.assertRaisesRegex(ValueError, "Unsupported patch decision contract version"):
            resolve_patch_decision_selection(
                card,
                {
                    "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
                    "selection_model": "one_based_action_slot",
                    "slot": apply_slot["slot"],
                    "action_identity": apply_slot["action_identity"],
                    **_patch_review_selection_metadata(),
                    "patch_decision_contract_version": 0,
                    "patch_decision": "apply",
                    "patch_id": "p1",
                },
                patch_id="p1",
            )

    def test_patch_decision_contract_tracks_duplicate_patch_action_slots(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply A", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply B", "payload": {"patch_id": "p2"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        self.assertEqual(card["patch_decision"]["patch_id"], "p1")
        self.assertEqual(
            [
                (entry["decision"], entry["slot"], entry["action_id"])
                for entry in card["patch_decision"]["decisions"]
            ],
            [("apply", 1, "apply_patch"), ("reject", 3, "reject_patch")],
        )

    def test_patch_decision_action_resolves_current_contract_decision(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        apply_action = resolve_patch_decision_action(card, patch_id=" p1 ", decision=" APPLY ")
        reject_action = resolve_patch_decision_action(card, patch_id="p1", decision="reject")

        self.assertEqual(apply_action["id"], "apply_patch")
        self.assertEqual(apply_action["payload"], {"patch_id": "p1"})
        self.assertEqual(reject_action["id"], "reject_patch")
        self.assertEqual(reject_action["payload"], {"patch_id": "p1"})

    def test_patch_decision_selection_requires_engine_decision_group(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        missing_group = deepcopy(selection)
        missing_group.pop("decision_group")
        with self.assertRaisesRegex(ValueError, "decision group"):
            resolve_patch_decision_selection(card, missing_group, patch_id="p1")

        tampered_group = deepcopy(selection)
        tampered_group["decision_group"] = "client_decision"
        with self.assertRaisesRegex(ValueError, "decision group"):
            resolve_patch_decision_selection(card, tampered_group, patch_id="p1")

    def test_patch_preview_selection_builder_returns_typed_slot_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        selection = build_patch_preview_selection(card, patch_id=" p1 ")
        action = resolve_patch_preview_selection(card, selection, patch_id="p1")

        self.assertEqual(selection["contract_version"], ACTION_SELECTION_CONTRACT_VERSION)
        self.assertEqual(selection["selection_model"], "one_based_action_slot")
        self.assertEqual(selection["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(selection["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(selection["patch_preview_contract_version"], PATCH_PREVIEW_CONTRACT_VERSION)
        self.assertEqual(selection["patch_id"], "p1")
        self.assertEqual(selection["slot"], 1)
        self.assertEqual(selection["action_identity"], card["action_selection"]["order"][0]["action_identity"])
        self.assertEqual(card["patch_preview"]["patch_id"], "p1")
        self.assertEqual(card["patch_preview"]["previews"][0]["selection"], selection)
        self.assertEqual(action["id"], "preview_patch")
        self.assertEqual(resolve_patch_preview_action(card, patch_id="p1")["payload"], {"patch_id": "p1"})

    def test_patch_preview_contract_tracks_only_current_patch_preview_slots(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview A", "payload": {"patch_id": "p1"}},
                    {"id": "preview_patch", "label": "Preview B", "payload": {"patch_id": "p2"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        self.assertEqual(card["patch_preview"]["patch_id"], "p1")
        self.assertEqual(
            [
                (entry["slot"], entry["action_id"])
                for entry in card["patch_preview"]["previews"]
            ],
            [(1, "preview_patch")],
        )
        self.assertEqual(
            build_patch_preview_selection(card, patch_id="p1"),
            card["patch_preview"]["previews"][0]["selection"],
        )

    def test_patch_preview_builder_revalidates_embedded_preview_metadata(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["patch_preview"]["previews"][0]["selection"]["patch_id"] = "p2"

        with self.assertRaisesRegex(ValueError, "current patch"):
            build_patch_preview_selection(card, patch_id="p1")

    def test_patch_preview_contract_is_absent_when_preview_action_is_unsupported(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        self.assertNotIn("patch_preview", card)
        self.assertEqual(
            materialize_patch_preview_contract(card, "p1"),
            {"contract_version": PATCH_PREVIEW_CONTRACT_VERSION, "patch_id": "p1", "previews": []},
        )
        with self.assertRaisesRegex(ValueError, "not available"):
            build_patch_preview_selection(card, patch_id="p1")

    def test_patch_preview_selection_revalidates_current_patch_and_action(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        preview_selection = build_patch_preview_selection(card, patch_id="p1")
        apply_selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        with self.assertRaisesRegex(ValueError, "current patch"):
            resolve_patch_preview_selection(card, preview_selection, patch_id="p2")
        with self.assertRaisesRegex(ValueError, "not a patch preview"):
            resolve_patch_preview_selection(card, apply_selection, patch_id="p1")

        preview_selection["patch_preview_contract_version"] = 0
        with self.assertRaisesRegex(ValueError, "Unsupported patch preview contract version"):
            resolve_patch_preview_selection(card, preview_selection, patch_id="p1")

        preview_selection = build_patch_preview_selection(card, patch_id="p1")
        preview_selection["client_note"] = "preview this patch"
        with self.assertRaisesRegex(ValueError, "Unsupported patch preview selection field"):
            resolve_patch_preview_selection(card, preview_selection, patch_id="p1")

    def test_patch_review_contract_bundles_preview_and_decisions_for_current_patch(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        review = build_patch_review_contract(card, patch_id=" p1 ")
        resolved = resolve_patch_review_contract(card, review, patch_id="p1")

        self.assertEqual(review["contract_version"], PATCH_REVIEW_CONTRACT_VERSION)
        self.assertEqual(review["patch_id"], "p1")
        self.assertEqual(review["preview"], build_patch_preview_selection(card, patch_id="p1"))
        self.assertEqual(
            review["availability"],
            {
                "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
                "patch_id": "p1",
                "flow": PATCH_REVIEW_FLOW,
                "decision_policy": PATCH_REVIEW_DECISION_POLICY,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
                "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
                "required": ["preview", "apply", "reject"],
                "available": ["preview", "apply", "reject"],
                "missing": [],
                "next_required": None,
                "is_complete": True,
            },
        )
        self.assertEqual(
            [
                (
                    entry["decision"],
                    entry["slot"],
                    entry["action_id"],
                    entry["action_identity"],
                    entry["selection"]["patch_id"],
                )
                for entry in review["decisions"]
            ],
            [
                (
                    "apply",
                    2,
                    "apply_patch",
                    review["decisions"][0]["selection"]["action_identity"],
                    "p1",
                ),
                (
                    "reject",
                    3,
                    "reject_patch",
                    review["decisions"][1]["selection"]["action_identity"],
                    "p1",
                ),
            ],
        )
        self.assertEqual(resolved["preview"]["id"], "preview_patch")
        self.assertEqual(
            [(entry["decision"], entry["action"]["id"]) for entry in resolved["decisions"]],
            [("apply", "apply_patch"), ("reject", "reject_patch")],
        )

    def test_patch_review_contract_resolves_to_typed_action_refs(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        refs = patch_review_action_refs_from_contract(card, review, patch_id=" p1 ")

        self.assertIsInstance(refs["preview"], ActionRef)
        self.assertEqual(refs["preview"].id, "preview_patch")
        self.assertEqual(refs["preview"].payload, {"patch_id": "p1"})
        self.assertEqual(
            {decision: ref.id for decision, ref in refs["decisions"].items()},
            {"apply": "apply_patch", "reject": "reject_patch"},
        )
        self.assertEqual(
            {decision: ref.payload for decision, ref in refs["decisions"].items()},
            {"apply": {"patch_id": "p1"}, "reject": {"patch_id": "p1"}},
        )

    def test_patch_review_contract_exports_current_cli_control_slots(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        slots = patch_review_control_slots_from_contract(card, review, patch_id=" p1 ")

        self.assertEqual(
            {control: slot["slot"] for control, slot in slots.items()},
            {"preview": 1, "apply": 2, "reject": 3},
        )
        self.assertEqual(
            {control: slot["action_id"] for control, slot in slots.items()},
            {
                "preview": "preview_patch",
                "apply": "apply_patch",
                "reject": "reject_patch",
            },
        )

    def test_patch_review_contract_exports_fallback_control_actions(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {
                        "id": "reject_patch",
                        "label": "Reject",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Reject patch?"},
                        "policy_sensitive": True,
                    },
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        controls = patch_review_control_actions_from_contract(card, review, patch_id=" p1 ")

        self.assertEqual(list(controls), ["preview", "apply", "reject"])
        self.assertEqual(
            {control: data["slot"] for control, data in controls.items()},
            {"preview": 1, "apply": 2, "reject": 3},
        )
        self.assertEqual(controls["preview"]["label"], "Preview")
        self.assertEqual(controls["preview"]["payload"], {"patch_id": "p1"})
        self.assertEqual(controls["preview"]["selection"], review["preview"])
        self.assertIsNone(controls["preview"]["confirm"])
        self.assertFalse(controls["preview"]["policy_sensitive"])
        self.assertEqual(controls["apply"]["selection"], review["decisions"][0]["selection"])
        self.assertEqual(controls["apply"]["confirm"], {"title": "Apply patch?"})
        self.assertTrue(controls["apply"]["policy_sensitive"])
        self.assertEqual(controls["reject"]["selection"], review["decisions"][1]["selection"])
        self.assertEqual(controls["reject"]["confirm"], {"title": "Reject patch?"})
        self.assertTrue(controls["reject"]["policy_sensitive"])
        self.assertEqual(
            shared_contracts.patch_review_control_actions_from_contract(card, review, patch_id="p1"),
            controls,
        )

    def test_patch_review_control_plan_reports_available_and_missing_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        plan = patch_review_control_plan_from_contract(card, review, patch_id=" p1 ")

        self.assertEqual(
            [(entry["control"], entry["status"]) for entry in plan],
            [("preview", "available"), ("apply", "available"), ("reject", "missing")],
        )
        self.assertEqual(
            [(entry.get("slot"), entry.get("action_id")) for entry in plan],
            [(1, "preview_patch"), (2, "apply_patch"), (None, None)],
        )
        self.assertEqual(
            [entry["command_aliases"] for entry in plan],
            [["preview", "preview_patch"], ["apply", "apply_patch"], ["reject", "reject_patch"]],
        )
        self.assertFalse(plan[0]["execution_policy"]["requires_confirmation"])
        self.assertFalse(plan[0]["execution_policy"]["requires_preview"])
        self.assertTrue(plan[1]["execution_policy"]["requires_confirmation"])
        self.assertTrue(plan[1]["execution_policy"]["requires_preview"])
        self.assertEqual(
            shared_contracts.patch_review_control_plan_from_contract(card, review, patch_id="p1"),
            plan,
        )

    def test_patch_review_next_control_reports_missing_required_step(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        next_control = patch_review_next_control_from_contract(card, review, patch_id="p1")

        self.assertEqual(
            next_control,
            {
                "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
                "patch_id": "p1",
                "control": "reject",
                "status": "missing",
                "command_aliases": ["reject", "reject_patch"],
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
                "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            },
        )
        self.assertEqual(
            shared_contracts.patch_review_next_control_from_contract(card, review, patch_id=" p1 "),
            next_control,
        )

    def test_patch_review_next_control_is_none_when_review_is_complete(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        self.assertIsNone(patch_review_next_control_from_contract(card, review, patch_id="p1"))

    def test_patch_review_cli_control_map_exports_one_based_commands(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        command_map = patch_review_cli_control_map_from_contract(
            card,
            review,
            patch_id=" p1 ",
        )

        self.assertEqual(command_map["selection_model"], "one_based_action_slot")
        self.assertEqual(command_map["flow"], PATCH_REVIEW_FLOW)
        self.assertEqual(command_map["decision_policy"], PATCH_REVIEW_DECISION_POLICY)
        self.assertEqual(command_map["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(command_map["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(command_map["required"], list(PATCH_REVIEW_REQUIRED_PARTS))
        self.assertEqual(command_map["available"], list(PATCH_REVIEW_REQUIRED_PARTS))
        self.assertTrue(command_map["is_complete"])
        self.assertEqual(command_map["missing"], [])
        self.assertIsNone(command_map["next_required"])
        self.assertEqual(command_map["next_required_command_aliases"], [])
        self.assertEqual(
            [
                (
                    entry["control"],
                    entry["command"],
                    entry["command_aliases"],
                    entry["slot"],
                    entry["action_id"],
                    entry["payload"],
                    entry["policy_gate"],
                    entry["requires_confirmation"],
                )
                for entry in command_map["controls"]
            ],
            [
                (
                    "preview",
                    "1",
                    ["preview", "preview_patch"],
                    1,
                    "preview_patch",
                    {"patch_id": "p1"},
                    "optional",
                    False,
                ),
                (
                    "apply",
                    "2",
                    ["apply", "apply_patch"],
                    2,
                    "apply_patch",
                    {"patch_id": "p1"},
                    "required",
                    True,
                ),
                (
                    "reject",
                    "3",
                    ["reject", "reject_patch"],
                    3,
                    "reject_patch",
                    {"patch_id": "p1"},
                    "required",
                    True,
                ),
            ],
        )
        self.assertEqual(
            command_map["controls"][1]["selection"],
            review["decisions"][0]["selection"],
        )
        self.assertEqual(
            command_map["controls"][1]["action_contract"],
            {
                "id": "apply_patch",
                "label": "Apply",
                "payload": {"patch_id": "p1"},
                "confirm": {"title": "Apply patch?"},
                "policy_sensitive": True,
            },
        )
        self.assertEqual(
            shared_contracts.patch_review_cli_control_map_from_contract(
                card,
                review,
                patch_id="p1",
            ),
            command_map,
        )
        self.assertEqual(
            shared_contracts.PATCH_REVIEW_CLI_COMMAND_ALIASES,
            PATCH_REVIEW_CLI_COMMAND_ALIASES,
        )

    def test_patch_review_decision_controls_export_apply_reject_pair(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        decisions = patch_review_decision_controls_from_contract(card, review, patch_id=" p1 ")

        self.assertEqual(decisions["selection_model"], "one_based_action_slot")
        self.assertEqual(decisions["decision_policy"], PATCH_REVIEW_DECISION_POLICY)
        self.assertEqual(decisions["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(decisions["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(decisions["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(decisions["required"], ["apply", "reject"])
        self.assertEqual(decisions["available"], ["apply", "reject"])
        self.assertEqual(decisions["missing"], [])
        self.assertTrue(decisions["is_complete"])
        self.assertEqual(
            [
                (
                    entry["control"],
                    entry["command"],
                    entry["slot"],
                    entry["action_id"],
                    entry["payload"],
                    entry["policy_gate"],
                    entry["requires_confirmation"],
                )
                for entry in decisions["controls"]
            ],
            [
                ("apply", "2", 2, "apply_patch", {"patch_id": "p1"}, "required", True),
                ("reject", "3", 3, "reject_patch", {"patch_id": "p1"}, "required", True),
            ],
        )
        self.assertEqual(
            shared_contracts.patch_review_decision_controls_from_contract(
                card,
                review,
                patch_id="p1",
            ),
            decisions,
        )

    def test_patch_review_decision_cli_lookup_exports_only_mutating_choices(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        lookup = patch_review_decision_cli_command_lookup_from_contract(
            card,
            review,
            patch_id=" p1 ",
        )

        self.assertEqual(lookup["selection_model"], "one_based_action_slot")
        self.assertEqual(lookup["decision_policy"], PATCH_REVIEW_DECISION_POLICY)
        self.assertEqual(lookup["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(lookup["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(lookup["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(lookup["required"], ["apply", "reject"])
        self.assertEqual(lookup["available"], ["apply", "reject"])
        self.assertEqual(lookup["missing"], [])
        self.assertTrue(lookup["is_complete"])
        self.assertEqual(
            sorted(lookup["commands"]),
            ["2", "3", "apply", "apply_patch", "reject", "reject_patch"],
        )
        self.assertNotIn("preview", lookup["commands"])
        self.assertNotIn("preview_patch", lookup["commands"])
        self.assertEqual(lookup["commands"]["apply"]["control"], "apply")
        self.assertEqual(lookup["commands"]["apply_patch"]["selection"], review["decisions"][0]["selection"])
        self.assertEqual(
            lookup["commands"]["apply_patch"]["action_contract"],
            {
                "id": "apply_patch",
                "label": "Apply",
                "payload": {"patch_id": "p1"},
                "confirm": {"title": "Apply patch?"},
                "policy_sensitive": True,
            },
        )
        self.assertEqual(lookup["commands"]["reject"]["policy_gate"], "required")
        self.assertTrue(lookup["commands"]["reject"]["policy_sensitive"])
        self.assertEqual(
            shared_contracts.patch_review_decision_cli_command_lookup_from_contract(
                card,
                review,
                patch_id="p1",
            ),
            lookup,
        )

    def test_patch_review_cli_command_lookup_exports_slots_and_aliases(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        lookup = patch_review_cli_command_lookup_from_contract(card, review, patch_id=" p1 ")

        self.assertEqual(lookup["selection_model"], "one_based_action_slot")
        self.assertEqual(lookup["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(lookup["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(
            sorted(lookup["commands"]),
            ["1", "2", "3", "apply", "apply_patch", "preview", "preview_patch", "reject", "reject_patch"],
        )
        self.assertEqual(lookup["commands"]["2"]["control"], "apply")
        self.assertEqual(lookup["commands"]["2"]["payload"], {"patch_id": "p1"})
        self.assertEqual(lookup["commands"]["apply_patch"]["slot"], 2)
        self.assertEqual(lookup["commands"]["apply_patch"]["payload"], {"patch_id": "p1"})
        self.assertEqual(lookup["commands"]["reject"]["action_id"], "reject_patch")
        self.assertEqual(lookup["commands"]["reject"]["selection"], review["decisions"][1]["selection"])
        self.assertEqual(
            shared_contracts.patch_review_cli_command_lookup_from_contract(card, review, patch_id="p1"),
            lookup,
        )

    def test_patch_review_cli_command_resolves_to_current_selection(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        selection = patch_review_selection_from_cli_command(
            card,
            review,
            patch_id=" p1 ",
            command=" 2 ",
        )

        self.assertEqual(selection, review["decisions"][0]["selection"])
        self.assertEqual(
            shared_contracts.patch_review_selection_from_cli_command(
                card,
                review,
                patch_id="p1",
                command="2",
            ),
            selection,
        )

    def test_patch_review_cli_command_resolves_to_typed_action_ref(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        action = patch_review_action_ref_from_cli_command(
            card,
            review,
            patch_id=" p1 ",
            command="apply_patch",
        )

        self.assertIsInstance(action, ActionRef)
        self.assertEqual(action.id, "apply_patch")
        self.assertEqual(action.payload, {"patch_id": "p1"})
        self.assertEqual(
            shared_contracts.patch_review_action_ref_from_cli_command(
                card,
                review,
                patch_id="p1",
                command="2",
            ),
            action,
        )

    def test_patch_review_cli_command_rejects_unknown_or_stale_commands(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        apply_selection = patch_review_selection_from_cli_command(
            card,
            review,
            patch_id="p1",
            command=" APPLY ",
        )
        self.assertEqual(apply_selection, review["decisions"][0]["selection"])

        reject_selection = patch_review_selection_from_cli_command(
            card,
            review,
            patch_id="p1",
            command="reject_patch",
        )
        self.assertEqual(reject_selection, review["decisions"][1]["selection"])

        with self.assertRaisesRegex(ValueError, "Unsupported patch review CLI command: approve"):
            patch_review_selection_from_cli_command(
                card,
                review,
                patch_id="p1",
                command="approve",
            )

        stale_review = build_complete_patch_review_contract(card, patch_id="p1")
        stale_review["decisions"][0]["selection"]["action_identity"] = "{}"
        with self.assertRaisesRegex(ValueError, "does not match"):
            patch_review_selection_from_cli_command(
                card,
                stale_review,
                patch_id="p1",
                command="2",
            )

    def test_patch_review_control_summary_reports_missing_demo_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        summary = patch_review_control_summary_from_contract(card, review, patch_id="p1")

        self.assertEqual(summary["required"], ["preview", "apply", "reject"])
        self.assertEqual(summary["available"], ["preview", "apply"])
        self.assertEqual(summary["missing"], ["reject"])
        self.assertEqual(summary["next_required"], "reject")
        self.assertEqual(summary["next_required_command_aliases"], ["reject", "reject_patch"])
        self.assertFalse(summary["is_complete"])
        self.assertEqual(
            [(name, control["slot"]) for name, control in summary["controls"].items()],
            [("preview", 1), ("apply", 2)],
        )
        self.assertEqual(
            [(entry["control"], entry["slot"], entry["action_id"]) for entry in summary["order"]],
            [("preview", 1, "preview_patch"), ("apply", 2, "apply_patch")],
        )
        self.assertEqual(
            [(entry["control"], entry["status"]) for entry in summary["control_plan"]],
            [("preview", "available"), ("apply", "available"), ("reject", "missing")],
        )
        self.assertEqual(summary["controls"]["apply"]["selection"]["patch_decision"], "apply")
        self.assertTrue(summary["controls"]["apply"]["policy_sensitive"])
        self.assertEqual(
            shared_contracts.patch_review_control_summary_from_contract(card, review, patch_id="p1"),
            summary,
        )

    def test_patch_review_control_summary_marks_decisions_engine_authoritative(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        summary = patch_review_control_summary_from_contract(card, review, patch_id="p1")

        self.assertFalse(summary["controls"]["preview"]["policy_sensitive"])
        self.assertTrue(summary["controls"]["apply"]["policy_sensitive"])
        self.assertTrue(summary["controls"]["reject"]["policy_sensitive"])
        self.assertEqual(
            [(entry["control"], entry["policy_sensitive"]) for entry in summary["order"]],
            [("preview", False), ("apply", True), ("reject", True)],
        )

    def test_patch_review_control_summary_exports_execution_policy(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        summary = patch_review_control_summary_from_contract(card, review, patch_id="p1")

        self.assertEqual(summary["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(shared_contracts.PATCH_REVIEW_DEMO_PATH_STEP, PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(
            shared_contracts.PATCH_REVIEW_EXECUTION_POLICY,
            PATCH_REVIEW_EXECUTION_POLICY,
        )
        self.assertEqual(
            summary["controls"]["preview"]["execution_policy"],
            {
                "policy_gate": "optional",
                "requires_confirmation": False,
                "requires_preview": False,
                "mutates_patch": False,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            },
        )
        self.assertEqual(
            summary["controls"]["apply"]["execution_policy"],
            {
                "policy_gate": "required",
                "requires_confirmation": True,
                "requires_preview": True,
                "mutates_patch": True,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            },
        )
        self.assertEqual(
            summary["controls"]["reject"]["execution_policy"],
            {
                "policy_gate": "required",
                "requires_confirmation": True,
                "requires_preview": True,
                "mutates_patch": True,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            },
        )

    def test_terminal_patch_review_fallback_renders_policy_gated_controls(self) -> None:
        text = render_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        self.assertIn("Patch review controls: preview=1, apply=2, reject=3", text)
        self.assertIn("Patch review CLI commands: preview=1, apply=2, reject=3", text)
        self.assertIn(
            "Patch review CLI aliases: "
            "preview=preview/preview_patch, apply=apply/apply_patch, reject=reject/reject_patch",
            text,
        )
        self.assertIn("Policy-gated patch controls: apply, reject", text)
        self.assertIn(
            "Patch review control plan: "
            "preview=available(slot 1, aliases preview/preview_patch), "
            "apply=available(slot 2, aliases apply/apply_patch, confirm, requires-preview, policy-gated), "
            "reject=available(slot 3, aliases reject/reject_patch, confirm, requires-preview, policy-gated)",
            text,
        )

    def test_terminal_patch_review_fallback_renders_next_required_control(self) -> None:
        text = render_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        self.assertIn("Patch review missing controls: reject", text)
        self.assertIn("Patch review next control: reject=missing", text)
        self.assertIn("Patch review next required control: reject", text)

    def test_patch_review_selection_resolves_cli_slot_through_review_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        preview = resolve_patch_review_selection(card, review, review["preview"], patch_id=" p1 ")
        decision = resolve_patch_review_selection(
            card,
            review,
            review["decisions"][1]["selection"],
            patch_id="p1",
        )

        self.assertEqual(preview["kind"], "preview")
        self.assertEqual(preview["action"]["id"], "preview_patch")
        self.assertEqual(decision["kind"], "decision")
        self.assertEqual(decision["decision"], "reject")
        self.assertEqual(decision["action"]["id"], "reject_patch")

    def test_patch_review_selection_builds_demo_path_controls_from_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        preview = build_patch_review_selection(card, review, patch_id=" p1 ", control=" preview ")
        apply = build_patch_review_selection(card, review, patch_id="p1", control="APPLY")
        reject = build_patch_review_selection(card, review, patch_id="p1", control="reject")

        self.assertEqual(resolve_patch_review_selection(card, review, preview, patch_id="p1")["kind"], "preview")
        self.assertEqual(
            resolve_patch_review_selection(card, review, apply, patch_id="p1")["decision"],
            "apply",
        )
        self.assertEqual(
            resolve_patch_review_selection(card, review, reject, patch_id="p1")["decision"],
            "reject",
        )

    def test_patch_review_selection_builder_rejects_unavailable_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "reject is not available"):
            build_patch_review_selection(card, review, patch_id="p1", control="reject")
        with self.assertRaisesRegex(ValueError, "control must be"):
            build_patch_review_selection(card, review, patch_id="p1", control="open")

    def test_patch_review_selection_returns_typed_action_ref_for_policy_gate(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {
                        "id": "reject_patch",
                        "label": "Reject",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Reject patch?"},
                        "policy_sensitive": True,
                    },
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        selected = patch_review_action_ref_from_selection(
            card,
            review,
            review["decisions"][0]["selection"],
            patch_id=" p1 ",
        )

        self.assertEqual(selected["kind"], "decision")
        self.assertEqual(selected["patch_id"], "p1")
        self.assertEqual(selected["decision"], "apply")
        self.assertEqual(selected["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(
            selected["action"],
            {
                "id": "apply_patch",
                "label": "Apply",
                "payload": {"patch_id": "p1"},
                "confirm": {"title": "Apply patch?"},
                "policy_sensitive": True,
            },
        )

    def test_patch_review_selection_has_typed_shared_result_with_contract_shape(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        selected = patch_review_action_selection_from_selection(
            card,
            review,
            review["decisions"][1]["selection"],
            patch_id="p1",
        )

        self.assertIsInstance(selected, PatchReviewActionSelection)
        self.assertEqual(selected.kind, "decision")
        self.assertEqual(selected.patch_id, "p1")
        self.assertEqual(selected.decision, "reject")
        self.assertEqual(selected.action.id, "reject_patch")
        self.assertEqual(
            selected.action.as_contract(),
            {
                "id": "reject_patch",
                "label": "Reject",
                "payload": {"patch_id": "p1"},
                "confirm": {"title": "Reject patch?"},
                "policy_sensitive": True,
            },
        )
        self.assertEqual(
            selected.as_contract(),
            {
                **patch_review_action_ref_from_selection(
                    card,
                    review,
                    review["decisions"][1]["selection"],
                    patch_id="p1",
                ),
                "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
            },
        )
        self.assertEqual(selected.as_contract()["contract_version"], PATCH_REVIEW_CONTRACT_VERSION)
        self.assertEqual(selected.as_contract()["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(selected.as_contract()["action"]["id"], "reject_patch")

    def test_patch_review_selection_rejects_actions_outside_review_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        stale = build_patch_decision_selection(card, patch_id="p1", decision="reject")
        review["decisions"] = [entry for entry in review["decisions"] if entry["decision"] != "reject"]
        review["availability"] = patch_review_availability_from_contract(review)

        with self.assertRaisesRegex(ValueError, "not part of the current review contract"):
            resolve_patch_review_selection(card, review, stale, patch_id="p1")

    def test_complete_patch_review_contract_requires_preview_apply_and_reject(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        review = build_complete_patch_review_contract(card, patch_id=" p1 ")

        self.assertEqual(review["preview"], build_patch_preview_selection(card, patch_id="p1"))
        self.assertEqual(
            [entry["decision"] for entry in review["decisions"]],
            ["apply", "reject"],
        )

    def test_complete_patch_review_action_refs_require_demo_path_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        refs = complete_patch_review_action_refs_from_contract(card, review, patch_id="p1")

        self.assertEqual(refs["preview"].id, "preview_patch")
        self.assertEqual(refs["decisions"]["apply"].id, "apply_patch")
        self.assertEqual(refs["decisions"]["reject"].id, "reject_patch")

    def test_complete_patch_review_actions_return_typed_demo_path_bundle(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {
                        "id": "reject_patch",
                        "label": "Reject",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Reject patch?"},
                        "policy_sensitive": True,
                    },
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        actions = complete_patch_review_actions_from_contract(card, review, patch_id=" p1 ")

        self.assertIsInstance(actions, CompletePatchReviewActions)
        self.assertEqual(actions.patch_id, "p1")
        self.assertEqual(actions.preview.id, "preview_patch")
        self.assertEqual(actions.apply.id, "apply_patch")
        self.assertTrue(actions.apply.policy_sensitive)
        self.assertEqual(actions.reject.id, "reject_patch")
        self.assertEqual(
            actions.as_contract(),
            {
                "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
                "patch_id": "p1",
                "flow": PATCH_REVIEW_FLOW,
                "decision_policy": PATCH_REVIEW_DECISION_POLICY,
                "decision_group": PATCH_REVIEW_DECISION_GROUP,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
                "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
                "execution_policy": PATCH_REVIEW_EXECUTION_POLICY,
                "preview": {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                "decisions": {
                    "apply": {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    "reject": {
                        "id": "reject_patch",
                        "label": "Reject",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Reject patch?"},
                        "policy_sensitive": True,
                    },
                },
            },
        )

    def test_complete_patch_review_actions_from_card_uses_embedded_cli_fallback_review(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {
                        "id": "reject_patch",
                        "label": "Reject",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Reject patch?"},
                        "policy_sensitive": True,
                    },
                ],
            }
        )

        actions = complete_patch_review_actions_from_card(card, patch_id=" p1 ")

        self.assertIsInstance(actions, CompletePatchReviewActions)
        self.assertEqual(actions.patch_id, "p1")
        self.assertEqual(actions.preview.id, "preview_patch")
        self.assertEqual(actions.apply.id, "apply_patch")
        self.assertEqual(actions.reject.id, "reject_patch")
        self.assertTrue(actions.apply.policy_sensitive)
        self.assertTrue(actions.reject.policy_sensitive)

    def test_cli_fallback_embeds_complete_patch_review_action_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        embedded = card["complete_patch_review_actions"]

        self.assertEqual(embedded["patch_id"], "p1")
        self.assertEqual(embedded["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(embedded["preview"]["id"], "preview_patch")
        self.assertEqual(embedded["decisions"]["apply"]["id"], "apply_patch")
        self.assertEqual(embedded["decisions"]["reject"]["id"], "reject_patch")
        self.assertTrue(embedded["decisions"]["apply"]["policy_sensitive"])
        self.assertTrue(embedded["decisions"]["reject"]["policy_sensitive"])

    def test_complete_patch_review_actions_from_card_rejects_stale_embedded_actions(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["complete_patch_review_actions"]["decisions"]["apply"]["payload"]["patch_id"] = "stale"

        with self.assertRaisesRegex(ValueError, "do not match engine-resolved actions"):
            complete_patch_review_actions_from_card(card, patch_id="p1")

    def test_complete_patch_review_execution_rejects_stale_embedded_actions(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["complete_patch_review_actions"]["decisions"]["apply"]["payload"]["patch_id"] = "stale"

        with self.assertRaisesRegex(ValueError, "do not match engine-resolved actions"):
            resolve_complete_patch_review_control_execution(
                card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(),
            )
        with self.assertRaisesRegex(ValueError, "do not match engine-resolved actions"):
            resolve_complete_patch_review_cli_command_execution(
                card,
                patch_id="p1",
                command="apply",
                capabilities=_capabilities(),
            )

    def test_complete_patch_review_actions_from_card_rejects_untyped_embedded_actions(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["complete_patch_review_actions"] = "stale"

        with self.assertRaisesRegex(ValueError, "actions contract must be an object"):
            complete_patch_review_actions_from_card(card, patch_id="p1")

    def test_partial_patch_review_fallback_omits_complete_action_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        self.assertIn("patch_review", card)
        self.assertNotIn("complete_patch_review_actions", card)

    def test_complete_patch_review_action_from_card_resolves_named_demo_path_control(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {
                        "id": "reject_patch",
                        "label": "Reject",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Reject patch?"},
                        "policy_sensitive": True,
                    },
                ],
            }
        )

        preview = complete_patch_review_action_from_card(card, patch_id=" p1 ", control=" preview ")
        apply = complete_patch_review_action_from_card(card, patch_id="p1", control="APPLY")
        reject = complete_patch_review_action_from_card(card, patch_id="p1", control="reject")

        self.assertIsInstance(preview, ActionRef)
        self.assertEqual(preview.id, "preview_patch")
        self.assertEqual(apply.id, "apply_patch")
        self.assertTrue(apply.policy_sensitive)
        self.assertEqual(reject.id, "reject_patch")
        self.assertTrue(reject.policy_sensitive)

    def test_complete_patch_review_action_from_card_rejects_unknown_control(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "preview', 'apply', or 'reject"):
            complete_patch_review_action_from_card(card, patch_id="p1", control="open")

    def test_complete_patch_review_actions_from_card_revalidates_embedded_review(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["patch_review"]["decisions"][0]["selection"]["patch_id"] = "p2"

        with self.assertRaisesRegex(ValueError, "current patch"):
            complete_patch_review_actions_from_card(card, patch_id="p1")

    def test_complete_patch_review_action_refs_reject_partial_review(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "missing: reject"):
            complete_patch_review_action_refs_from_contract(card, review, patch_id="p1")

    def test_complete_patch_review_contract_rejects_partial_demo_path_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "missing: reject"):
            build_complete_patch_review_contract(card, patch_id="p1")

    def test_patch_review_availability_reports_demo_path_gaps(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        availability = build_patch_review_availability(card, patch_id=" p1 ")

        self.assertEqual(availability["patch_id"], "p1")
        self.assertEqual(availability["required"], list(PATCH_REVIEW_REQUIRED_PARTS))
        self.assertEqual(availability["available"], ["preview", "apply"])
        self.assertEqual(availability["missing"], ["reject"])
        self.assertEqual(availability["next_required"], "reject")
        self.assertFalse(availability["is_complete"])

    def test_patch_review_contract_validator_enforces_capabilities_and_completion(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        availability = validate_patch_review_contract(
            card,
            review,
            patch_id=" p1 ",
            capabilities=_capabilities(),
            require_complete=True,
        )

        self.assertTrue(availability["is_complete"])
        self.assertEqual(shared_contracts.validate_patch_review_contract(card, review, patch_id="p1"), availability)
        with self.assertRaisesRegex(ValueError, "reject action is not supported"):
            validate_patch_review_contract(
                card,
                review,
                patch_id="p1",
                capabilities=_capabilities(actions_supported=("preview_patch", "apply_patch")),
            )

        partial_card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        partial_review = build_patch_review_contract(partial_card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "missing: reject"):
            validate_patch_review_contract(partial_card, partial_review, patch_id="p1", require_complete=True)

    def test_patch_review_availability_ignores_stale_selection_entries(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        review["preview"] = dict(review["preview"], patch_id="stale")
        review["decisions"][0]["selection"] = dict(
            review["decisions"][0]["selection"],
            patch_id="stale",
        )

        availability = patch_review_availability_from_contract(review)

        self.assertEqual(availability["required"], list(PATCH_REVIEW_REQUIRED_PARTS))
        self.assertEqual(availability["available"], ["reject"])
        self.assertEqual(availability["missing"], ["preview", "apply"])
        self.assertEqual(availability["next_required"], "preview")
        self.assertFalse(availability["is_complete"])

    def test_patch_review_availability_revalidates_decision_action_ids(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        review["decisions"][0]["action_id"] = "reject_patch"

        availability = patch_review_availability_from_contract(review)

        self.assertEqual(availability["available"], ["preview", "reject"])
        self.assertEqual(availability["missing"], ["apply"])
        self.assertEqual(availability["next_required"], "apply")
        self.assertFalse(availability["is_complete"])

    def test_complete_patch_review_refs_reject_mismatched_decision_action_ids(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        review["decisions"][1]["action_id"] = "apply_patch"

        with self.assertRaisesRegex(ValueError, "missing: reject"):
            complete_patch_review_action_refs_from_contract(card, review, patch_id="p1")

    def test_patch_review_availability_accepts_complete_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        availability = patch_review_availability_from_contract(review)

        self.assertEqual(availability["required"], list(PATCH_REVIEW_REQUIRED_PARTS))
        self.assertEqual(availability["available"], ["preview", "apply", "reject"])
        self.assertEqual(availability["missing"], [])
        self.assertIsNone(availability["next_required"])
        self.assertEqual(availability["flow"], PATCH_REVIEW_FLOW)
        self.assertEqual(availability["decision_policy"], PATCH_REVIEW_DECISION_POLICY)
        self.assertEqual(availability["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertTrue(availability["is_complete"])

    def test_patch_review_availability_requires_action_selection_contract_shape(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        review["preview"]["selection_model"] = "zero_based_action_index"
        review["decisions"][0]["selection"]["contract_version"] = ACTION_SELECTION_CONTRACT_VERSION + 1

        availability = patch_review_availability_from_contract(review)

        self.assertEqual(availability["available"], ["reject"])
        self.assertEqual(availability["missing"], ["preview", "apply"])
        self.assertEqual(availability["next_required"], "preview")
        self.assertFalse(availability["is_complete"])

    def test_patch_review_required_parts_are_shared_and_cli_exported(self) -> None:
        self.assertEqual(shared_contracts.PATCH_REVIEW_ACTION_AUTHORITY, PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(shared_contracts.PATCH_REVIEW_REQUIRED_PARTS, ("preview", "apply", "reject"))
        self.assertEqual(UI_PATCH_REVIEW_REQUIRED_PARTS, shared_contracts.PATCH_REVIEW_REQUIRED_PARTS)

    def test_patch_review_contract_rejects_stale_availability_snapshot(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        review["availability"]["missing"] = ["reject"]
        review["availability"]["is_complete"] = False

        with self.assertRaisesRegex(ValueError, "availability"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["availability"]["flow"] = "decide_without_preview"
        with self.assertRaisesRegex(ValueError, "availability"):
            resolve_patch_review_contract(card, review, patch_id="p1")

    def test_patch_review_availability_rejects_unsupported_contract_header(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        review["flow"] = "decide_without_preview"
        with self.assertRaisesRegex(ValueError, "flow"):
            patch_review_availability_from_contract(review)

        review = build_patch_review_contract(card, patch_id="p1")
        review["decision_policy"] = "apply_only"
        with self.assertRaisesRegex(ValueError, "decision policy"):
            patch_review_availability_from_contract(review)

        review = build_patch_review_contract(card, patch_id="p1")
        review["action_authority"] = "client_authoritative"
        with self.assertRaisesRegex(ValueError, "action authority"):
            patch_review_availability_from_contract(review)

    def test_patch_review_availability_rejects_duplicate_decisions(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        review["decisions"].append(deepcopy(review["decisions"][0]))

        with self.assertRaisesRegex(ValueError, "duplicated"):
            patch_review_availability_from_contract(review)

    def test_cli_fallback_materializes_patch_review_contract_for_current_patch(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply stale", "payload": {"patch_id": "p2"}},
                ],
            }
        )

        review = card["patch_review"]
        resolved = resolve_patch_review_contract(card, review, patch_id="p1")

        self.assertEqual(review["contract_version"], PATCH_REVIEW_CONTRACT_VERSION)
        self.assertEqual(review["patch_id"], "p1")
        self.assertEqual(review["flow"], PATCH_REVIEW_FLOW)
        self.assertEqual(review["decision_policy"], PATCH_REVIEW_DECISION_POLICY)
        self.assertEqual(review["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(review["preview"], card["patch_preview"]["previews"][0]["selection"])
        self.assertEqual(review["availability"]["available"], ["preview", "apply", "reject"])
        self.assertEqual(review["availability"]["missing"], [])
        self.assertTrue(review["availability"]["is_complete"])
        self.assertEqual(
            [(entry["decision"], entry["selection"]["patch_id"]) for entry in review["decisions"]],
            [("apply", "p1"), ("reject", "p1")],
        )
        self.assertEqual(resolved["preview"]["id"], "preview_patch")
        self.assertEqual(resolved["flow"], PATCH_REVIEW_FLOW)
        self.assertEqual(resolved["decision_policy"], PATCH_REVIEW_DECISION_POLICY)
        self.assertEqual(resolved["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(
            [(entry["decision"], entry["action"]["id"]) for entry in resolved["decisions"]],
            [("apply", "apply_patch"), ("reject", "reject_patch")],
        )

    def test_patch_review_contract_revalidates_stale_or_mismatched_selections(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        review["preview"]["patch_id"] = "p2"
        with self.assertRaisesRegex(ValueError, "current patch"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["decisions"][0]["decision"] = "reject"
        with self.assertRaisesRegex(ValueError, "selected action"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["decisions"][0]["slot"] = 99
        with self.assertRaisesRegex(ValueError, "slot"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["decisions"][0]["action_id"] = "reject_patch"
        with self.assertRaisesRegex(ValueError, "action_id"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["decisions"][0]["action_identity"] = "{}"
        with self.assertRaisesRegex(ValueError, "action_identity"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["flow"] = "decide_without_preview"
        with self.assertRaisesRegex(ValueError, "flow"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["decision_policy"] = "apply_only"
        with self.assertRaisesRegex(ValueError, "decision policy"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        review["action_authority"] = "client_authoritative"
        with self.assertRaisesRegex(ValueError, "action authority"):
            resolve_patch_review_contract(card, review, patch_id="p1")

        review = build_patch_review_contract(card, patch_id="p1")
        del review["action_authority"]
        self.assertEqual(
            resolve_patch_review_contract(card, review, patch_id="p1")["action_authority"],
            PATCH_REVIEW_ACTION_AUTHORITY,
        )

    def test_patch_decision_selection_builder_returns_typed_slot_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        selection = build_patch_decision_selection(card, patch_id=" p1 ", decision=" APPLY ")
        decision_entry = next(
            entry for entry in card["patch_decision"]["decisions"] if entry["decision"] == "apply"
        )

        self.assertEqual(selection["contract_version"], ACTION_SELECTION_CONTRACT_VERSION)
        self.assertEqual(selection["selection_model"], "one_based_action_slot")
        self.assertEqual(selection["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(selection["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(selection["patch_decision_contract_version"], PATCH_DECISION_CONTRACT_VERSION)
        self.assertEqual(selection["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(selection["patch_decision"], "apply")
        self.assertEqual(selection["patch_id"], "p1")
        self.assertEqual(selection["slot"], 1)
        self.assertEqual(selection["action_identity"], card["action_selection"]["order"][0]["action_identity"])
        self.assertEqual(decision_entry["selection"], selection)
        self.assertEqual(
            resolve_patch_decision_selection(card, selection, patch_id="p1")["id"],
            "apply_patch",
        )

    def test_patch_review_action_selection_type_rejects_invalid_direct_contracts(self) -> None:
        preview = ActionRef(
            id="preview_patch",
            label="Preview",
            payload={"patch_id": "p1"},
        )
        apply = ActionRef(
            id="apply_patch",
            label="Apply",
            payload={"patch_id": "p1"},
        )
        reject = ActionRef(
            id="reject_patch",
            label="Reject",
            payload={"patch_id": "p1"},
        )

        self.assertEqual(
            PatchReviewActionSelection(
                kind="preview",
                patch_id="p1",
                action=preview,
            ).as_contract(),
            {
                "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
                "kind": "preview",
                "patch_id": "p1",
                "flow": PATCH_REVIEW_FLOW,
                "decision_policy": PATCH_REVIEW_DECISION_POLICY,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
                "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
                "action": {
                    "id": "preview_patch",
                    "label": "Preview",
                    "payload": {"patch_id": "p1"},
                },
            },
        )
        self.assertEqual(
            PatchReviewActionSelection(
                kind="decision",
                patch_id="p1",
                action=apply,
                decision="apply",
            ).as_contract(),
            {
                "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
                "kind": "decision",
                "patch_id": "p1",
                "flow": PATCH_REVIEW_FLOW,
                "decision_policy": PATCH_REVIEW_DECISION_POLICY,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
                "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
                "action": {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                },
                "decision": "apply",
            },
        )

        with self.assertRaisesRegex(ValueError, "must not include a decision"):
            PatchReviewActionSelection(
                kind="preview",
                patch_id="p1",
                action=preview,
                decision="apply",
            )
        with self.assertRaisesRegex(ValueError, "does not match the selected action"):
            PatchReviewActionSelection(
                kind="decision",
                patch_id="p1",
                action=reject,
                decision="apply",
            )
        with self.assertRaisesRegex(ValueError, "current patch"):
            PatchReviewActionSelection(
                kind="decision",
                patch_id="p1",
                action=ActionRef(
                    id="apply_patch",
                    label="Apply",
                    payload={"patch_id": "p2"},
                ),
                decision="apply",
            )
        with self.assertRaisesRegex(ValueError, "must be normalized"):
            PatchReviewActionSelection(
                kind="decision",
                patch_id=" p1 ",
                action=apply,
                decision="apply",
            )

    def test_patch_decision_action_revalidates_stale_contract_identity(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["patch_decision"]["decisions"][0]["action_identity"] = "stale"

        with self.assertRaisesRegex(ValueError, "current card"):
            resolve_patch_decision_action(card, patch_id="p1", decision="apply")

    def test_patch_decision_builder_revalidates_embedded_selection_metadata(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        card["patch_decision"]["decisions"][0]["selection"]["patch_decision"] = "reject"
        with self.assertRaisesRegex(ValueError, "selected action"):
            build_patch_decision_selection(card, patch_id="p1", decision="apply")

        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["patch_decision"]["decisions"][0]["selection"]["patch_id"] = "p2"
        with self.assertRaisesRegex(ValueError, "current patch"):
            build_patch_decision_selection(card, patch_id="p1", decision="apply")

        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["patch_decision"]["decisions"][0]["selection"]["patch_decision_contract_version"] = 0
        with self.assertRaisesRegex(ValueError, "Unsupported patch decision contract version"):
            build_patch_decision_selection(card, patch_id="p1", decision="apply")

    def test_patch_decision_builder_rejects_stale_cached_slot(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        apply_entry = card["patch_decision"]["decisions"][0]
        reject_entry = card["patch_decision"]["decisions"][1]
        apply_entry["slot"] = reject_entry["slot"]
        apply_entry["action_identity"] = reject_entry["action_identity"]
        apply_entry["selection"]["slot"] = reject_entry["slot"]
        apply_entry["selection"]["action_identity"] = reject_entry["action_identity"]

        with self.assertRaisesRegex(ValueError, "selected action"):
            build_patch_decision_selection(card, patch_id="p1", decision="apply")

    def test_patch_decision_action_requires_current_patch_and_known_decision(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "current patch"):
            resolve_patch_decision_action(card, patch_id="p2", decision="apply")
        with self.assertRaisesRegex(ValueError, "must be 'apply' or 'reject'"):
            resolve_patch_decision_action(card, patch_id="p1", decision="open")

    def test_selection_contract_materializes_typed_action_ref_for_engine_policy_gate(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {
                        "id": "apply_patch",
                        "label": " Apply ",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        action = action_ref_from_selection(card, selection)

        self.assertEqual(action.id, "apply_patch")
        self.assertEqual(action.label, "Apply")
        self.assertEqual(action.payload, {"patch_id": "p1"})
        self.assertEqual(action.confirm, {"title": "Apply patch?"})
        self.assertTrue(action.policy_sensitive)

    def test_patch_selection_action_refs_revalidate_current_patch_kind(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        preview_selection = build_patch_preview_selection(card, patch_id="p1")
        apply_selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        self.assertEqual(
            patch_preview_action_ref_from_selection(card, preview_selection, patch_id="p1").id,
            "preview_patch",
        )
        self.assertEqual(
            patch_decision_action_ref_from_selection(card, apply_selection, patch_id="p1").id,
            "apply_patch",
        )
        with self.assertRaisesRegex(ValueError, "not a patch decision"):
            patch_decision_action_ref_from_selection(card, preview_selection, patch_id="p1")
        with self.assertRaisesRegex(ValueError, "not a patch preview"):
            patch_preview_action_ref_from_selection(card, apply_selection, patch_id="p1")

    def test_engine_policy_gate_is_authoritative(self) -> None:
        executed: list[str] = []
        action = ActionRef(
            id="export_document",
            label="Export",
            payload={"format": "md"},
            policy_sensitive=True,
        )
        caps = _capabilities()

        with self.assertRaises(PermissionError):
            execute_action_with_policy_gate(
                action=action,
                capabilities=caps,
                policy_gate=_PolicyGateStub(False),
                executor=lambda a: executed.append(a.id),
            )
        self.assertEqual(executed, [])

        execute_action_with_policy_gate(
            action=action,
            capabilities=caps,
            policy_gate=_PolicyGateStub(True),
            executor=lambda a: executed.append(a.id),
        )
        self.assertEqual(executed, ["export_document"])

    def test_patch_review_selection_execution_revalidates_policy_gate(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        apply_selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        executed: list[str] = []

        with self.assertRaises(PermissionError):
            execute_patch_review_selection_with_policy_gate(
                card=card,
                review=review,
                selection=apply_selection,
                patch_id="p1",
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(False),
                executor=lambda action: executed.append(action.id),
            )
        self.assertEqual(executed, [])

        execute_patch_review_selection_with_policy_gate(
            card=card,
            review=review,
            selection=apply_selection,
            patch_id="p1",
            capabilities=_capabilities(),
            policy_gate=_PolicyGateStub(True),
            executor=lambda action: executed.append(action.id),
        )

        self.assertEqual(executed, ["apply_patch"])

    def test_patch_review_cli_command_execution_uses_engine_policy_gate(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")
        gate = _RecordingPolicyGate(False, [])

        with self.assertRaises(PermissionError):
            execute_patch_review_cli_command_with_policy_gate(
                card=card,
                review=review,
                patch_id="p1",
                command="apply",
                capabilities=_capabilities(),
                policy_gate=gate,
                executor=lambda action: action.id,
            )

        self.assertEqual(gate.calls, [("apply_patch", {"patch_id": "p1"}, True)])

        gate = _RecordingPolicyGate(True, [])
        result = execute_patch_review_cli_command_with_policy_gate(
            card=card,
            review=review,
            patch_id="p1",
            command="3",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: (action.id, action.policy_sensitive, action.confirm),
        )

        self.assertEqual(result, ("reject_patch", True, {"title": "Reject patch?"}))
        self.assertEqual(gate.calls, [("reject_patch", {"patch_id": "p1"}, True)])

    def test_patch_review_named_control_execution_uses_typed_selection_contract(self) -> None:
        card = materialize_terminal_card(
            materialize_proposed_edit_card(
                {
                    "type": "ProposedEditCard",
                    "patch_id": "p1",
                    "title": "Patch choices",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                    "actions": [],
                }
            )
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")
        gate = _RecordingPolicyGate(True, [])
        executed: list[ActionRef] = []

        result = execute_patch_review_control_with_policy_gate(
            card=card,
            review=review,
            patch_id=" p1 ",
            control=" REJECT ",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: executed.append(action) or f"ran {action.id}",
        )

        self.assertEqual(result, "ran reject_patch")
        self.assertEqual(gate.calls, [("reject_patch", {"patch_id": "p1"}, True)])
        self.assertEqual(executed[0].confirm, {"title": "Reject patch?"})
        self.assertTrue(executed[0].policy_sensitive)

    def test_patch_review_decision_cli_execution_rejects_preview_commands(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported patch review decision CLI command: preview",
        ):
            resolve_patch_review_decision_cli_command_execution(
                card,
                review,
                patch_id="p1",
                command="preview",
                capabilities=_capabilities(),
            )

    def test_patch_review_decision_cli_execution_is_policy_gated(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")
        execution = resolve_patch_review_decision_cli_command_execution(
            card,
            review,
            patch_id="p1",
            command=" apply_patch ",
            capabilities=_capabilities(),
        )

        self.assertEqual(execution["control"], "apply")
        self.assertEqual(execution["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(execution["action_contract"]["id"], "apply_patch")
        self.assertTrue(execution["requires_confirmation"])
        self.assertEqual(execution["policy_gate"], "required")

        gate = _RecordingPolicyGate(True, [])
        result = execute_patch_review_decision_cli_command_with_policy_gate(
            card=card,
            review=review,
            patch_id="p1",
            command="2",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: (action.id, action.policy_sensitive, action.confirm),
        )

        self.assertEqual(result, ("apply_patch", True, {"title": "Apply patch?"}))
        self.assertEqual(gate.calls, [("apply_patch", {"patch_id": "p1"}, True)])

    def test_complete_patch_review_decision_cli_execution_rebuilds_full_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        execution = resolve_complete_patch_review_decision_cli_command_execution(
            card,
            patch_id=" p1 ",
            command="reject_patch",
            capabilities=_capabilities(),
        )

        self.assertEqual(execution["control"], "reject")
        self.assertEqual(execution["action_id"], "reject_patch")
        self.assertEqual(execution["normalized_command"], "reject_patch")
        self.assertEqual(execution["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(execution["action_contract"]["confirm"], {"title": "Reject patch?"})
        self.assertTrue(execution["action_contract"]["policy_sensitive"])
        self.assertEqual(execution["complete_patch_review"]["missing"], [])
        self.assertIsNone(execution["complete_patch_review"]["next_required"])
        self.assertIs(
            shared_contracts.resolve_complete_patch_review_decision_cli_command_execution,
            resolve_complete_patch_review_decision_cli_command_execution,
        )

    def test_complete_patch_review_decision_cli_execution_rejects_preview_commands(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported patch review decision CLI command: preview",
        ):
            resolve_complete_patch_review_decision_cli_command_execution(
                card,
                patch_id="p1",
                command="preview",
                capabilities=_capabilities(),
            )

    def test_complete_patch_review_decision_cli_execution_is_policy_gated(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        gate = _RecordingPolicyGate(True, [])
        result = execute_complete_patch_review_decision_cli_command_with_policy_gate(
            card=card,
            patch_id="p1",
            command="2",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: (action.id, action.policy_sensitive, action.confirm),
        )

        self.assertEqual(result, ("apply_patch", True, {"title": "Apply patch?"}))
        self.assertEqual(gate.calls, [("apply_patch", {"patch_id": "p1"}, True)])

    def test_patch_review_named_control_execution_rejects_unsupported_control(self) -> None:
        card = materialize_terminal_card(
            materialize_proposed_edit_card(
                {
                    "type": "ProposedEditCard",
                    "patch_id": "p1",
                    "title": "Patch choices",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                    "actions": [],
                }
            )
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "control must be 'preview', 'apply', or 'reject'"):
            execute_patch_review_control_with_policy_gate(
                card=card,
                review=review,
                patch_id="p1",
                control="open",
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action,
            )

    def test_complete_patch_review_action_execution_uses_engine_policy_gate(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {
                        "id": "apply_patch",
                        "label": "Apply",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Apply patch?"},
                        "policy_sensitive": True,
                    },
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        executed: list[str] = []

        with self.assertRaises(PermissionError):
            execute_complete_patch_review_action_with_policy_gate(
                card=card,
                patch_id=" p1 ",
                control=" apply ",
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(False),
                executor=lambda action: executed.append(action.id),
            )
        self.assertEqual(executed, [])

        execute_complete_patch_review_action_with_policy_gate(
            card=card,
            patch_id="p1",
            control="APPLY",
            capabilities=_capabilities(),
            policy_gate=_PolicyGateStub(True),
            executor=lambda action: executed.append(action.id),
        )

        self.assertEqual(executed, ["apply_patch"])

    def test_complete_patch_review_control_execution_uses_resolved_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        gate = _RecordingPolicyGate(True, [])

        result = execute_complete_patch_review_control_with_policy_gate(
            card=card,
            patch_id=" p1 ",
            control=" apply ",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: (action.id, action.confirm, action.policy_sensitive),
        )

        self.assertEqual(result, ("apply_patch", {"title": "Apply patch?"}, True))
        self.assertEqual(gate.calls, [("apply_patch", {"patch_id": "p1"}, True)])
        self.assertIs(
            shared_contracts.execute_complete_patch_review_control_with_policy_gate,
            execute_complete_patch_review_control_with_policy_gate,
        )

    def test_complete_patch_review_control_execution_rejects_incomplete_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "Complete patch review is missing: reject"):
            execute_complete_patch_review_control_with_policy_gate(
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action,
            )

    def test_complete_patch_review_selection_execution_uses_complete_engine_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        gate = _RecordingPolicyGate(True, [])

        result = execute_complete_patch_review_selection_with_policy_gate(
            card=card,
            selection=selection,
            patch_id=" p1 ",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: (action.id, action.confirm, action.policy_sensitive),
        )

        self.assertEqual(result, ("apply_patch", {"title": "Apply patch?"}, True))
        self.assertEqual(gate.calls, [("apply_patch", {"patch_id": "p1"}, True)])
        self.assertIs(
            shared_contracts.execute_complete_patch_review_selection_with_policy_gate,
            execute_complete_patch_review_selection_with_policy_gate,
        )

    def test_complete_patch_review_selection_execution_rejects_incomplete_demo_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        with self.assertRaisesRegex(ValueError, "Complete patch review is missing: reject"):
            execute_complete_patch_review_selection_with_policy_gate(
                card=card,
                selection=selection,
                patch_id="p1",
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action,
            )

    def test_complete_patch_review_cli_command_execution_uses_complete_engine_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        gate = _RecordingPolicyGate(True, [])

        selected = complete_patch_review_action_ref_from_cli_command(
            card,
            patch_id=" p1 ",
            command="2",
        )
        result = execute_complete_patch_review_cli_command_with_policy_gate(
            card=card,
            patch_id="p1",
            command="apply",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: (action.id, action.confirm, action.policy_sensitive),
        )

        self.assertEqual(selected.id, "apply_patch")
        self.assertEqual(result, ("apply_patch", {"title": "Apply patch?"}, True))
        self.assertEqual(gate.calls, [("apply_patch", {"patch_id": "p1"}, True)])

    def test_complete_patch_review_decision_action_ref_from_cli_command_is_decision_only(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        selected = complete_patch_review_decision_action_ref_from_cli_command(
            card,
            patch_id=" p1 ",
            command="reject_patch",
        )

        self.assertEqual(selected.id, "reject_patch")
        self.assertEqual(selected.payload, {"patch_id": "p1"})
        self.assertEqual(selected.confirm, {"title": "Reject patch?"})
        self.assertTrue(selected.policy_sensitive)
        self.assertIs(
            shared_contracts.complete_patch_review_decision_action_ref_from_cli_command,
            complete_patch_review_decision_action_ref_from_cli_command,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsupported patch review decision CLI command: preview",
        ):
            complete_patch_review_decision_action_ref_from_cli_command(
                card,
                patch_id="p1",
                command="preview",
            )

    def test_complete_patch_review_cli_command_execution_rejects_incomplete_demo_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "Complete patch review is missing: reject"):
            execute_complete_patch_review_cli_command_with_policy_gate(
                card=card,
                patch_id="p1",
                command="apply",
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action.id,
            )

    def test_complete_patch_review_action_execution_rejects_stale_embedded_review(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["patch_review"] = build_complete_patch_review_contract(card, patch_id="p1")
        card["patch_review"]["patch_id"] = "stale"

        with self.assertRaisesRegex(ValueError, "does not match the current patch"):
            execute_complete_patch_review_action_with_policy_gate(
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action.id,
            )

    def test_complete_patch_review_action_execution_rejects_untyped_embedded_review(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        card["patch_review"] = "stale"

        with self.assertRaisesRegex(ValueError, "contract must be an object"):
            complete_patch_review_actions_from_card(card, patch_id="p1")

    def test_complete_patch_review_action_execution_rejects_unsupported_client_action(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "Complete patch review client support is missing: apply",
        ):
            execute_complete_patch_review_action_with_policy_gate(
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(actions_supported=("preview_patch", "reject_patch")),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action.id,
            )

    def test_complete_patch_review_capabilities_require_full_demo_controls(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "Complete patch review client support is missing: reject",
        ):
            validate_complete_patch_review_capabilities(
                _capabilities(actions_supported=("preview_patch", "apply_patch"))
            )

    def test_complete_patch_review_action_execution_requires_full_client_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(
            ValueError,
            "Complete patch review client support is missing: reject",
        ):
            execute_complete_patch_review_action_with_policy_gate(
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(actions_supported=("preview_patch", "apply_patch")),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action.id,
            )

    def test_complete_patch_review_action_execution_rejects_malformed_action_capabilities(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        malformed_caps = A2UICapabilities(
            a2ui_version=1,
            client_name="Exegesis Studio",
            cards_supported=("ProposedEditCard",),
            primitive_blocks_supported=(
                "MarkdownBlock",
                "KeyValueBlock",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
            actions_supported=["preview_patch", "apply_patch", "reject_patch"],  # type: ignore[arg-type]
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )

        with self.assertRaisesRegex(ValueError, "actions_supported must be a tuple"):
            execute_complete_patch_review_action_with_policy_gate(
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=malformed_caps,
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action.id,
            )

    def test_patch_decision_execution_is_policy_sensitive_even_when_card_omits_flag(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")
        apply_selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        gate = _RecordingPolicyGate(False, [])

        with self.assertRaises(PermissionError):
            execute_patch_review_selection_with_policy_gate(
                card=card,
                review=review,
                selection=apply_selection,
                patch_id="p1",
                capabilities=_capabilities(),
                policy_gate=gate,
                executor=lambda action: action.id,
            )

        self.assertEqual(gate.calls, [("apply_patch", {"patch_id": "p1"}, True)])

    def test_complete_patch_review_decision_is_policy_sensitive_even_when_card_omits_flag(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        gate = _RecordingPolicyGate(True, [])

        result = execute_complete_patch_review_action_with_policy_gate(
            card=card,
            patch_id="p1",
            control="reject",
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: action.policy_sensitive,
        )

        self.assertTrue(result)
        self.assertEqual(gate.calls, [("reject_patch", {"patch_id": "p1"}, True)])

    def test_patch_decision_execution_adds_engine_confirmation_metadata(self) -> None:
        executed: list[ActionRef] = []
        action = ActionRef(
            id="apply_patch",
            label="Apply",
            payload={"patch_id": "p1"},
        )

        execute_action_with_policy_gate(
            action=action,
            capabilities=_capabilities(),
            policy_gate=_PolicyGateStub(True),
            executor=lambda a: executed.append(a),
        )

        self.assertEqual(len(executed), 1)
        self.assertEqual(executed[0].confirm, {"title": "Apply patch?"})
        self.assertTrue(executed[0].policy_sensitive)

    def test_patch_decision_execution_normalizes_before_policy_gate(self) -> None:
        gate = _RecordingPolicyGate(True, [])
        action = ActionRef(
            id="reject_patch",
            label="Reject",
            payload={"patch_id": " p1 "},
        )

        result = execute_action_with_policy_gate(
            action=action,
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda a: (a.payload, a.policy_sensitive, a.confirm),
        )

        self.assertEqual(result, ({"patch_id": "p1"}, True, {"title": "Reject patch?"}))
        self.assertEqual(gate.calls, [("reject_patch", {"patch_id": "p1"}, True)])

    def test_engine_authoritative_patch_actions_normalize_patch_id(self) -> None:
        apply_action = engine_authoritative_action_ref(
            ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": " p1 "},
            )
        )
        preview_action = engine_authoritative_action_ref(
            ActionRef(
                id="preview_patch",
                label="Preview",
                payload={"patch_id": " p1 "},
            )
        )

        self.assertEqual(apply_action.payload, {"patch_id": "p1"})
        self.assertEqual(preview_action.payload, {"patch_id": "p1"})
        self.assertTrue(apply_action.policy_sensitive)
        self.assertFalse(preview_action.policy_sensitive)

    def test_engine_authoritative_mvp_actions_normalize_control_payloads(self) -> None:
        actions = [
            engine_authoritative_action_ref(
                ActionRef(
                    id="promote_to_basket",
                    label="Add",
                    payload={"item_id": " doc-1 "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="pin_to_context_set",
                    label="Pin",
                    payload={"item_id": " doc-1 ", "context_set_id": " ctx-1 "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="open_corpus_item",
                    label="Open",
                    payload={"item_id": " doc-1 "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="open_section",
                    label="Open section",
                    payload={"section_id": " sec-1 "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="create_context_set",
                    label="Create",
                    payload={"name": " Chapter 5 "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="gather_context",
                    label="Gather",
                    payload={"basket_id": " basket-1 ", "context_set_id": " ctx-1 "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="run_agent",
                    label="Plan",
                    payload={"operation": " plan "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="export_document",
                    label="Export",
                    payload={"format": " markdown "},
                )
            ),
            engine_authoritative_action_ref(
                ActionRef(
                    id="copy_to_clipboard",
                    label="Copy",
                    payload={"text": " keep intentional whitespace "},
                )
            ),
        ]

        self.assertEqual(actions[0].payload, {"item_id": "doc-1"})
        self.assertEqual(actions[1].payload, {"item_id": "doc-1", "context_set_id": "ctx-1"})
        self.assertEqual(actions[2].payload, {"item_id": "doc-1"})
        self.assertEqual(actions[3].payload, {"section_id": "sec-1"})
        self.assertEqual(actions[4].payload, {"name": "Chapter 5"})
        self.assertEqual(actions[5].payload, {"basket_id": "basket-1", "context_set_id": "ctx-1"})
        self.assertEqual(actions[6].payload, {"operation": "plan"})
        self.assertEqual(actions[7].payload, {"format": "markdown"})
        self.assertEqual(actions[8].payload, {"text": " keep intentional whitespace "})

    def test_engine_action_materialization_dedupes_padded_item_payloads(self) -> None:
        card = {
            "type": RETRIEVAL_RESULTS_CARD_TYPE,
            "title": "Retrieval",
            "query": "chapter five",
            "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
            "actions": [
                {"id": "promote_to_basket", "label": "Add padded", "payload": {"item_id": " doc-1 "}},
                {"id": "promote_to_basket", "label": "Add", "payload": {"item_id": "doc-1"}},
            ],
        }

        actions = materialize_card_actions(card)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["payload"], {"item_id": "doc-1"})

    def test_engine_authoritative_preview_action_stays_optional_non_mutating(self) -> None:
        gate = _RecordingPolicyGate(False, [])
        action = ActionRef(
            id="preview_patch",
            label="Preview",
            payload={"patch_id": " p1 "},
            confirm={"title": "Preview patch?"},
            policy_sensitive=True,
        )

        with self.assertRaises(PermissionError):
            execute_action_with_policy_gate(
                action=action,
                capabilities=_capabilities(),
                policy_gate=gate,
                executor=lambda a: a,
            )

        self.assertEqual(gate.calls, [("preview_patch", {"patch_id": "p1"}, False)])

    def test_patch_decision_execution_uses_engine_confirmation_metadata(self) -> None:
        executed: list[ActionRef] = []
        action = ActionRef(
            id="reject_patch",
            label="Reject",
            payload={"patch_id": "p1"},
            confirm={"title": "Reject this generated patch?"},
        )

        execute_action_with_policy_gate(
            action=engine_authoritative_action_ref(action),
            capabilities=_capabilities(),
            policy_gate=_PolicyGateStub(True),
            executor=lambda a: executed.append(a),
        )

        self.assertEqual(len(executed), 1)
        self.assertEqual(executed[0].confirm, {"title": "Reject patch?"})
        self.assertTrue(executed[0].policy_sensitive)

    def test_engine_authoritative_non_decision_actions_drop_client_confirmation(self) -> None:
        executed: list[ActionRef] = []
        action = ActionRef(
            id="gather_context",
            label="Gather context",
            payload={"basket_id": "basket-1", "context_set_id": "set-1"},
            confirm={"title": "Client supplied confirmation"},
            policy_sensitive=True,
        )

        execute_action_with_policy_gate(
            action=action,
            capabilities=_capabilities(),
            policy_gate=_PolicyGateStub(True),
            executor=lambda a: executed.append(a),
        )

        self.assertEqual(len(executed), 1)
        self.assertIsNone(executed[0].confirm)
        self.assertFalse(executed[0].policy_sensitive)

    def test_engine_authoritative_context_actions_drop_client_policy_sensitivity(self) -> None:
        gate = _RecordingPolicyGate(True, [])
        action = ActionRef(
            id="promote_to_basket",
            label="Add to basket",
            payload={"item_id": " doc-1 "},
            policy_sensitive=True,
        )

        result = execute_action_with_policy_gate(
            action=action,
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda a: a.as_contract(),
        )

        self.assertEqual(result["payload"], {"item_id": "doc-1"})
        self.assertNotIn("policy_sensitive", result)
        self.assertEqual(gate.calls, [("promote_to_basket", {"item_id": "doc-1"}, False)])

    def test_card_selection_execution_resolves_context_action_through_policy_gate(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "BasketCard",
                "title": "Basket",
                "basket_id": "basket-1",
                "items": [{"item_id": "doc-1", "title": "Chapter 5"}],
                "actions": [
                    {
                        "id": "gather_context",
                        "label": "Gather context",
                        "payload": {"basket_id": " basket-1 ", "context_set_id": " ctx-1 "},
                    }
                ],
            }
        )
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 1,
            "action_identity": card["action_selection"]["order"][0]["action_identity"],
        }
        gate = _RecordingPolicyGate(True, [])

        result = execute_card_selection_with_policy_gate(
            card=card,
            selection=selection,
            capabilities=_capabilities(),
            policy_gate=gate,
            executor=lambda action: action.as_contract(),
        )

        self.assertEqual(result["id"], "gather_context")
        self.assertEqual(result["payload"], {"basket_id": "basket-1", "context_set_id": "ctx-1"})
        self.assertNotIn("confirm", result)
        self.assertNotIn("policy_sensitive", result)
        self.assertEqual(gate.calls, [("gather_context", {"basket_id": "basket-1", "context_set_id": "ctx-1"}, False)])

        execution = resolve_card_selection_execution(
            card,
            selection,
            capabilities=_capabilities(),
        )
        self.assertEqual(execution["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(
            execution["execution_policy"],
            {
                "policy_gate": "optional",
                "requires_confirmation": False,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            },
        )
        self.assertEqual(
            execution["action_contract"]["payload"],
            {"basket_id": "basket-1", "context_set_id": "ctx-1"},
        )

    def test_card_selection_execution_rejects_unsupported_client_action(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "RetrievalResultsCard",
                "title": "Retrieval",
                "query": "chapter five",
                "results": [{"item_id": "doc-1", "title": "Chapter 5", "snippet": "Relevant paragraph"}],
                "actions": [
                    {"id": "promote_to_basket", "label": "Add", "payload": {"item_id": "doc-1"}},
                ],
            }
        )
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 1,
            "action_identity": card["action_selection"]["order"][0]["action_identity"],
        }

        with self.assertRaisesRegex(ValueError, "Action not supported by client"):
            resolve_card_selection_execution(
                card,
                selection,
                capabilities=_capabilities(actions_supported=("open_corpus_item",)),
            )

    def test_action_payload_rejects_untyped_extra_fields_before_policy_gate(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported payload field"):
            ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": "p1", "target_file": "chapter.md"},
            )

    def test_action_payload_rejects_untyped_field_names_before_policy_gate(self) -> None:
        with self.assertRaisesRegex(ValueError, "Payload field names must be non-empty strings"):
            ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": "p1", 1: "chapter.md"},  # type: ignore[dict-item]
            )

        with self.assertRaisesRegex(ValueError, "Payload field names must be non-empty strings"):
            ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": "p1", "": "chapter.md"},
            )

    def test_action_id_must_be_typed_and_normalized_before_policy_gate(self) -> None:
        with self.assertRaisesRegex(ValueError, "Action id must be normalized"):
            validate_action_ref(
                {
                    "id": " apply_patch ",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                }
            )

        with self.assertRaisesRegex(ValueError, "Action id is required"):
            validate_action_ref(
                {
                    "id": 1,
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                }
            )

    def test_card_action_materialization_drops_malformed_action_ids(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch choices",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
            "actions": [
                {"id": " apply_patch ", "label": "Apply padded", "payload": {"patch_id": "p1"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }

        actions = materialize_card_actions(card)

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["id"], "apply_patch")

    def test_action_ref_metadata_rejects_bad_runtime_values_before_policy_gate(self) -> None:
        with self.assertRaisesRegex(ValueError, "confirm values must be non-empty strings"):
            ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": "p1"},
                confirm={"title": ""},
            )

        with self.assertRaisesRegex(ValueError, "Unsupported action confirm field"):
            ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": "p1"},
                confirm={"title": "Apply patch?", "body": "Extra client copy"},
            )

        with self.assertRaisesRegex(ValueError, "confirm values must be normalized"):
            ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": "p1"},
                confirm={"title": " Apply patch? "},
            )

    def test_action_metadata_must_stay_typed_for_engine_policy_gate(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported action field"):
            validate_action_ref(
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "target_file": "chapter.md",
                }
            )

        with self.assertRaisesRegex(ValueError, "policy_sensitive must be a boolean"):
            validate_action_ref(
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "policy_sensitive": "yes",
                }
            )

        with self.assertRaisesRegex(ValueError, "confirm values must be non-empty strings"):
            validate_action_ref(
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "confirm": {"title": ""},
                }
            )

        with self.assertRaisesRegex(ValueError, "Unsupported action confirm field"):
            validate_action_ref(
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "confirm": {"title": "Apply patch?", "body": "Extra client copy"},
                }
            )

        with self.assertRaisesRegex(ValueError, "confirm values must be normalized"):
            validate_action_ref(
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "confirm": {"title": " Apply patch? "},
                }
            )

    def test_cli_fallback_materializes_patch_decisions_as_engine_authoritative(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "title": "Patch choices",
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        apply_action = card["actions"][0]
        reject_action = card["actions"][1]
        self.assertEqual(apply_action["confirm"], {"title": "Apply patch?"})
        self.assertTrue(apply_action["policy_sensitive"])
        self.assertEqual(reject_action["confirm"], {"title": "Reject patch?"})
        self.assertTrue(reject_action["policy_sensitive"])

    def test_cli_fallback_drops_actions_with_untyped_metadata(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {
                        "id": "apply_patch",
                        "label": "Unsafe apply",
                        "payload": {"patch_id": "p1"},
                        "target_file": "chapter.md",
                    },
                    {
                        "id": "reject_patch",
                        "label": "Reject",
                        "payload": {"patch_id": "p1"},
                        "confirm": {"title": "Reject patch?"},
                    },
                ],
            }
        )

        self.assertEqual([action["id"] for action in card["actions"]], ["reject_patch"])
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in card["action_selection"]["order"]],
            [(1, "reject_patch")],
        )

    def test_streaming_card_event_materializes_engine_card_contract(self) -> None:
        event = build_card_published_event(
            event_id="evt-1",
            run_id="run-1",
            sequence=1,
            card={
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [],
            },
            capabilities=_capabilities(),
        )

        self.assertEqual(event["event_type"], "card_published")
        self.assertEqual(event["card"]["type"], "ProposedEditCard")
        self.assertEqual(
            [action["id"] for action in event["card"]["actions"]],
            ["preview_patch", "apply_patch", "reject_patch"],
        )
        self.assertEqual(event["card"]["patch_decision"]["patch_id"], "p1")

    def test_streaming_action_events_carry_versioned_selection_and_resolution(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}}],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        selected = build_action_selected_event(
            event_id="evt-2",
            run_id="run-1",
            sequence=2,
            action_id="apply_patch",
            selection=selection,
        )
        resolved = build_action_resolved_event(
            event_id="evt-3",
            run_id="run-1",
            sequence=3,
            action_id="apply_patch",
            status="applied",
            selection=selection,
        )

        self.assertEqual(selected["selection"]["patch_decision"], "apply")
        self.assertEqual(resolved["status"], "applied")
        self.assertEqual(resolved["selection"]["action_identity"], selection["action_identity"])

    def test_streaming_action_resolved_event_can_derive_action_id_from_selection(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="reject")

        resolved = build_action_resolved_event_from_selection(
            event_id="evt-3",
            run_id="run-1",
            sequence=3,
            card=card,
            selection=selection,
            status="rejected",
            message="Rejected by operator",
        )

        self.assertEqual(resolved["action_id"], "reject_patch")
        self.assertEqual(resolved["status"], "rejected")
        self.assertEqual(resolved["message"], "Rejected by operator")
        self.assertEqual(resolved["selection"]["patch_decision"], "reject")

    def test_streaming_action_resolved_event_rejects_mismatched_patch_selection(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        with self.assertRaisesRegex(ValueError, "does not match patch decision selection"):
            build_action_resolved_event(
                event_id="evt-3",
                run_id="run-1",
                sequence=3,
                action_id="reject_patch",
                status="rejected",
                selection=selection,
            )

    def test_streaming_action_selected_event_can_derive_action_id_from_selection(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        selected = build_action_selected_event_from_selection(
            event_id="evt-2",
            run_id="run-1",
            sequence=2,
            card=card,
            selection=selection,
        )

        self.assertEqual(selected["action_id"], "apply_patch")
        self.assertEqual(selected["selection"]["action_identity"], selection["action_identity"])

    def test_streaming_action_selected_event_revalidates_client_action_capabilities(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")

        with self.assertRaisesRegex(ValueError, "Client does not support A2UI stream event action id"):
            build_action_selected_event_from_selection(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                card=card,
                selection=selection,
                capabilities=_capabilities(actions_supported=("preview_patch", "reject_patch")),
            )

    def test_streaming_action_selected_event_rejects_stale_selection_identity(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        selection["action_identity"] = "stale"

        with self.assertRaisesRegex(ValueError, "does not match the current card"):
            build_action_selected_event_from_selection(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                card=card,
                selection=selection,
            )

    def test_streaming_patch_review_events_reject_client_authoritative_selection(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        selection["action_authority"] = "client_authoritative"

        with self.assertRaisesRegex(ValueError, "engine-authoritative"):
            build_action_selected_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                action_id="apply_patch",
                selection=selection,
            )

    def test_streaming_patch_review_events_require_decision_group(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        self.assertEqual(selection["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        selection["decision_group"] = "client_decision"

        with self.assertRaisesRegex(ValueError, "decision group"):
            build_action_selected_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                action_id="apply_patch",
                selection=selection,
            )

    def test_streaming_action_events_reject_unknown_action_ids(self) -> None:
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 1,
            "action_identity": "unknown",
        }

        with self.assertRaisesRegex(ValueError, "Unsupported A2UI stream event action id"):
            build_action_selected_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                action_id="delete_everything",
                selection=selection,
            )

    def test_streaming_action_selected_event_rejects_untyped_selection_shape(self) -> None:
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "freeform",
            "slot": 0,
            "action_identity": "",
        }

        with self.assertRaisesRegex(ValueError, "Unsupported action selection model"):
            build_action_selected_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                action_id="apply_patch",
                selection=selection,
            )

    def test_streaming_action_selected_event_rejects_generic_identity_action_mismatch(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 2,
            "action_identity": card["action_selection"]["order"][1]["action_identity"],
        }

        with self.assertRaisesRegex(ValueError, "Action id does not match action selection identity"):
            build_action_selected_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                action_id="apply_patch",
                selection=selection,
            )

    def test_streaming_action_selected_event_rejects_mismatched_patch_selection(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "GenericCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        apply_selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        preview_selection = build_patch_preview_selection(card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "does not match patch decision selection"):
            build_action_selected_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                action_id="reject_patch",
                selection=apply_selection,
            )
        with self.assertRaisesRegex(ValueError, "does not match patch preview selection"):
            build_action_selected_event(
                event_id="evt-3",
                run_id="run-1",
                sequence=3,
                action_id="apply_patch",
                selection=preview_selection,
            )

    def test_streaming_patch_review_events_require_patch_id_in_selection(self) -> None:
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 1,
            "action_identity": "apply_patch:1:p1",
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
            "patch_decision": "apply",
        }

        with self.assertRaisesRegex(ValueError, "patch_id is required"):
            build_action_selected_event(
                event_id="evt-4",
                run_id="run-1",
                sequence=4,
                action_id="apply_patch",
                selection=selection,
            )

        preview_selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 1,
            "action_identity": "preview_patch:1:p1",
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "patch_preview_contract_version": PATCH_PREVIEW_CONTRACT_VERSION,
            "patch_id": " ",
        }

        with self.assertRaisesRegex(ValueError, "patch_id is required"):
            build_action_selected_event(
                event_id="evt-5",
                run_id="run-1",
                sequence=5,
                action_id="preview_patch",
                selection=preview_selection,
            )

    def test_complete_patch_review_action_selected_event_uses_named_control(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        event = build_complete_patch_review_action_selected_event(
            event_id="evt-4",
            run_id="run-1",
            sequence=4,
            card=card,
            patch_id=" p1 ",
            control=" APPLY ",
        )

        self.assertEqual(event["event_type"], "action_selected")
        self.assertEqual(event["action_id"], "apply_patch")
        self.assertEqual(event["selection"]["patch_decision"], "apply")
        self.assertEqual(event["selection"]["patch_id"], "p1")

    def test_complete_patch_review_action_resolved_event_uses_control_status(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        preview = build_complete_patch_review_action_resolved_event(
            event_id="evt-1",
            run_id="run-1",
            sequence=1,
            card=card,
            patch_id=" p1 ",
            control="preview",
        )
        rejected = build_complete_patch_review_action_resolved_event(
            event_id="evt-2",
            run_id="run-1",
            sequence=2,
            card=card,
            patch_id="p1",
            control="reject",
            message="User rejected patch",
        )

        self.assertEqual(preview["action_id"], "preview_patch")
        self.assertEqual(preview["status"], "previewed")
        self.assertEqual(preview["selection"]["patch_id"], "p1")
        self.assertEqual(rejected["action_id"], "reject_patch")
        self.assertEqual(rejected["status"], "rejected")
        self.assertEqual(rejected["message"], "User rejected patch")

    def test_patch_review_control_execution_envelope_is_engine_authoritative(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        execution = resolve_patch_review_control_execution(
            card,
            review,
            patch_id="p1",
            control=" APPLY ",
        )

        self.assertEqual(execution["control"], "apply")
        self.assertEqual(execution["action_id"], "apply_patch")
        self.assertEqual(execution["payload"], {"patch_id": "p1"})
        self.assertEqual(execution["action_contract"]["confirm"], {"title": "Apply patch?"})
        self.assertTrue(execution["action_contract"]["policy_sensitive"])
        self.assertEqual(execution["execution_policy"], PATCH_REVIEW_EXECUTION_POLICY["apply"])
        self.assertTrue(execution["requires_confirmation"])
        self.assertTrue(execution["requires_preview"])
        self.assertEqual(execution["policy_gate"], "required")
        self.assertEqual(execution["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(execution["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)
        self.assertEqual(execution["selection"]["patch_decision"], "apply")

    def test_patch_decision_selection_rebuilds_legacy_entry_with_decision_group(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        legacy_card = deepcopy(card)
        del legacy_card["patch_decision"]["decisions"][0]["selection"]

        selection = build_patch_decision_selection(legacy_card, patch_id="p1", decision="apply")

        self.assertEqual(selection["decision_group"], PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(selection["patch_decision"], "apply")
        self.assertEqual(
            resolve_patch_decision_selection(legacy_card, selection, patch_id="p1")["id"],
            "apply_patch",
        )

    def test_patch_review_control_execution_rejects_missing_control(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_patch_review_contract(card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "reject is not available"):
            resolve_patch_review_control_execution(
                card,
                review,
                patch_id="p1",
                control="reject",
            )

    def test_patch_review_control_execution_revalidates_client_capability(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "apply action is not supported by client"):
            resolve_patch_review_control_execution(
                card,
                review,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(actions_supported=("preview_patch", "reject_patch")),
            )

        execution = resolve_patch_review_control_execution(
            card,
            review,
            patch_id="p1",
            control="apply",
            capabilities=_capabilities(actions_supported=("preview_patch", "apply_patch", "reject_patch")),
        )

        self.assertEqual(execution["control"], "apply")
        self.assertEqual(execution["action_id"], "apply_patch")

    def test_patch_review_cli_command_execution_envelope_is_engine_authoritative(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        execution = resolve_patch_review_cli_command_execution(
            card,
            review,
            patch_id="p1",
            command=" APPLY_PATCH ",
            capabilities=_capabilities(),
        )

        self.assertEqual(execution["command"], "APPLY_PATCH")
        self.assertEqual(execution["normalized_command"], "apply_patch")
        self.assertEqual(execution["control"], "apply")
        self.assertEqual(execution["action_id"], "apply_patch")
        self.assertEqual(execution["action_contract"]["confirm"], {"title": "Apply patch?"})
        self.assertTrue(execution["action_contract"]["policy_sensitive"])
        self.assertEqual(execution["execution_policy"], PATCH_REVIEW_EXECUTION_POLICY["apply"])
        self.assertEqual(execution["action_authority"], PATCH_REVIEW_ACTION_AUTHORITY)
        self.assertEqual(execution["demo_path_step"], PATCH_REVIEW_DEMO_PATH_STEP)

    def test_patch_review_cli_command_execution_revalidates_client_capability(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        with self.assertRaisesRegex(ValueError, "apply action is not supported by client"):
            resolve_patch_review_cli_command_execution(
                card,
                review,
                patch_id="p1",
                command="2",
                capabilities=_capabilities(actions_supported=("preview_patch", "reject_patch")),
            )

    def test_complete_patch_review_control_execution_rebuilds_full_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        execution = resolve_complete_patch_review_control_execution(
            card,
            patch_id=" p1 ",
            control="reject",
            capabilities=_capabilities(actions_supported=("preview_patch", "apply_patch", "reject_patch")),
        )

        self.assertEqual(execution["control"], "reject")
        self.assertEqual(execution["action_id"], "reject_patch")
        self.assertEqual(execution["payload"], {"patch_id": "p1"})
        self.assertEqual(execution["action_contract"]["confirm"], {"title": "Reject patch?"})
        self.assertTrue(execution["action_contract"]["policy_sensitive"])
        self.assertEqual(execution["execution_policy"], PATCH_REVIEW_EXECUTION_POLICY["reject"])
        self.assertEqual(
            execution["complete_patch_review"],
            {
                "contract_version": PATCH_REVIEW_CONTRACT_VERSION,
                "patch_id": "p1",
                "flow": PATCH_REVIEW_FLOW,
                "decision_policy": PATCH_REVIEW_DECISION_POLICY,
                "decision_group": PATCH_REVIEW_DECISION_GROUP,
                "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
                "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
                "execution_policy": PATCH_REVIEW_EXECUTION_POLICY,
                "required": ["preview", "apply", "reject"],
                "available": ["preview", "apply", "reject"],
                "missing": [],
                "next_required": None,
                "is_complete": True,
            },
        )
        self.assertIs(
            shared_contracts.resolve_complete_patch_review_control_execution,
            resolve_complete_patch_review_control_execution,
        )

    def test_complete_patch_review_cli_command_execution_rebuilds_full_contract(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        execution = resolve_complete_patch_review_cli_command_execution(
            card,
            patch_id=" p1 ",
            command="reject",
            capabilities=_capabilities(),
        )

        self.assertEqual(execution["control"], "reject")
        self.assertEqual(execution["action_id"], "reject_patch")
        self.assertEqual(execution["normalized_command"], "reject")
        self.assertEqual(execution["action_contract"]["confirm"], {"title": "Reject patch?"})
        self.assertTrue(execution["action_contract"]["policy_sensitive"])
        self.assertEqual(execution["complete_patch_review"]["patch_id"], "p1")
        self.assertEqual(execution["complete_patch_review"]["missing"], [])
        self.assertIsNone(execution["complete_patch_review"]["next_required"])
        self.assertEqual(
            execution["complete_patch_review"]["decision_group"],
            PATCH_REVIEW_DECISION_GROUP,
        )
        self.assertEqual(
            execution["complete_patch_review"]["action_authority"],
            PATCH_REVIEW_ACTION_AUTHORITY,
        )
        self.assertEqual(
            execution["complete_patch_review"]["demo_path_step"],
            PATCH_REVIEW_DEMO_PATH_STEP,
        )
        self.assertEqual(
            execution["complete_patch_review"]["execution_policy"],
            PATCH_REVIEW_EXECUTION_POLICY,
        )
        self.assertIs(
            shared_contracts.resolve_complete_patch_review_cli_command_execution,
            resolve_complete_patch_review_cli_command_execution,
        )

    def test_complete_patch_review_control_execution_requires_full_demo_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "Complete patch review is missing: reject"):
            resolve_complete_patch_review_control_execution(
                card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(actions_supported=("preview_patch", "apply_patch", "reject_patch")),
            )

        with self.assertRaisesRegex(ValueError, "Complete patch review client support is missing: reject"):
            resolve_complete_patch_review_control_execution(
                card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(actions_supported=("preview_patch", "apply_patch")),
            )

    def test_complete_patch_review_contract_carries_engine_execution_policy(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        self.assertEqual(review["execution_policy"], PATCH_REVIEW_EXECUTION_POLICY)
        resolved = resolve_patch_review_contract(card, review, patch_id="p1")
        self.assertEqual(resolved["execution_policy"], PATCH_REVIEW_EXECUTION_POLICY)

        review["execution_policy"]["apply"]["policy_gate"] = "optional"
        with self.assertRaisesRegex(ValueError, "Unsupported patch review execution policy"):
            resolve_patch_review_contract(card, review, patch_id="p1")

    def test_patch_review_controls_carry_typed_execution_preconditions(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        self.assertEqual(
            PATCH_REVIEW_EXECUTION_PRECONDITIONS["apply"],
            {
                "requires_preview": True,
                "requires_confirmation": True,
                "requires_policy_gate": True,
            },
        )
        self.assertEqual(
            patch_review_execution_preconditions("preview"),
            {
                "requires_preview": False,
                "requires_confirmation": False,
                "requires_policy_gate": False,
            },
        )
        plan = patch_review_control_plan_from_contract(card, review, patch_id="p1")
        self.assertEqual(
            {entry["control"]: entry["preconditions"] for entry in plan},
            PATCH_REVIEW_EXECUTION_PRECONDITIONS,
        )

        execution = resolve_patch_review_control_execution(
            card,
            review,
            patch_id="p1",
            control="apply",
            capabilities=_capabilities(),
        )

        self.assertEqual(
            execution["preconditions"],
            PATCH_REVIEW_EXECUTION_PRECONDITIONS["apply"],
        )
        self.assertIs(
            shared_contracts.patch_review_execution_preconditions,
            patch_review_execution_preconditions,
        )

    def test_cli_shim_exports_patch_review_contract_constants(self) -> None:
        self.assertEqual(UI_PATCH_REVIEW_DECISION_GROUP, PATCH_REVIEW_DECISION_GROUP)
        self.assertEqual(UI_PATCH_REVIEW_CLI_COMMAND_ALIASES, PATCH_REVIEW_CLI_COMMAND_ALIASES)
        self.assertEqual(UI_PATCH_REVIEW_EXECUTION_PRECONDITIONS, PATCH_REVIEW_EXECUTION_PRECONDITIONS)
        self.assertIs(shared_contracts.PATCH_REVIEW_DECISION_GROUP, PATCH_REVIEW_DECISION_GROUP)
        self.assertIs(
            shared_contracts.PATCH_REVIEW_CLI_COMMAND_ALIASES,
            PATCH_REVIEW_CLI_COMMAND_ALIASES,
        )
        self.assertIs(
            shared_contracts.PATCH_REVIEW_EXECUTION_PRECONDITIONS,
            PATCH_REVIEW_EXECUTION_PRECONDITIONS,
        )

    def test_patch_review_selections_carry_engine_execution_policy(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        self.assertEqual(
            review["preview"]["execution_policy"],
            PATCH_REVIEW_EXECUTION_POLICY["preview"],
        )
        decision_policies = {
            entry["decision"]: entry["selection"]["execution_policy"]
            for entry in review["decisions"]
        }
        self.assertEqual(decision_policies["apply"], PATCH_REVIEW_EXECUTION_POLICY["apply"])
        self.assertEqual(decision_policies["reject"], PATCH_REVIEW_EXECUTION_POLICY["reject"])

    def test_patch_review_rejects_selection_policy_tampering(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")
        preview = deepcopy(review["preview"])
        preview["execution_policy"]["policy_gate"] = "required"

        with self.assertRaisesRegex(
            ValueError,
            "Patch review selection execution policy does not match engine policy",
        ):
            resolve_patch_preview_selection(card, preview, patch_id="p1")

        apply_selection = deepcopy(review["decisions"][0]["selection"])
        apply_selection["execution_policy"]["policy_gate"] = "optional"
        with self.assertRaisesRegex(
            ValueError,
            "Patch review selection execution policy does not match engine policy",
        ):
            resolve_patch_decision_selection(card, apply_selection, patch_id="p1")

    def test_patch_review_contract_rejects_untyped_fields(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        review = build_complete_patch_review_contract(card, patch_id="p1")

        contract_with_extra = deepcopy(review)
        contract_with_extra["client_hint"] = "apply"
        with self.assertRaisesRegex(ValueError, "Unsupported patch review contract field"):
            resolve_patch_review_contract(card, contract_with_extra, patch_id="p1")

        decision_with_extra = deepcopy(review)
        decision_with_extra["decisions"][0]["client_hint"] = "apply"
        with self.assertRaisesRegex(ValueError, "Unsupported patch review decision entry field"):
            patch_review_availability_from_contract(decision_with_extra)

        availability_with_extra = deepcopy(review)
        availability_with_extra["availability"]["client_hint"] = "apply"
        with self.assertRaisesRegex(ValueError, "Unsupported patch review availability field"):
            resolve_patch_review_contract(card, availability_with_extra, patch_id="p1")

    def test_complete_patch_review_actions_normalizes_policy_gated_decisions(self) -> None:
        actions = CompletePatchReviewActions(
            patch_id="p1",
            preview=ActionRef(
                id="preview_patch",
                label="Preview",
                payload={"patch_id": " p1 "},
            ),
            apply=ActionRef(
                id="apply_patch",
                label="Apply",
                payload={"patch_id": " p1 "},
            ),
            reject=ActionRef(
                id="reject_patch",
                label="Reject",
                payload={"patch_id": " p1 "},
            ),
        )

        contract = actions.as_contract()

        self.assertEqual(contract["preview"]["payload"], {"patch_id": "p1"})
        self.assertEqual(contract["decisions"]["apply"]["confirm"], {"title": "Apply patch?"})
        self.assertTrue(contract["decisions"]["apply"]["policy_sensitive"])
        self.assertEqual(contract["decisions"]["reject"]["confirm"], {"title": "Reject patch?"})
        self.assertTrue(contract["decisions"]["reject"]["policy_sensitive"])

    def test_complete_patch_review_actions_rejects_mismatched_control(self) -> None:
        with self.assertRaisesRegex(ValueError, "apply control must use apply_patch"):
            CompletePatchReviewActions(
                patch_id="p1",
                preview=ActionRef(
                    id="preview_patch",
                    label="Preview",
                    payload={"patch_id": "p1"},
                ),
                apply=ActionRef(
                    id="reject_patch",
                    label="Reject",
                    payload={"patch_id": "p1"},
                ),
                reject=ActionRef(
                    id="reject_patch",
                    label="Reject",
                    payload={"patch_id": "p1"},
                ),
            )

        with self.assertRaisesRegex(ValueError, "reject control must match the current patch"):
            CompletePatchReviewActions(
                patch_id="p1",
                preview=ActionRef(
                    id="preview_patch",
                    label="Preview",
                    payload={"patch_id": "p1"},
                ),
                apply=ActionRef(
                    id="apply_patch",
                    label="Apply",
                    payload={"patch_id": "p1"},
                ),
                reject=ActionRef(
                    id="reject_patch",
                    label="Reject",
                    payload={"patch_id": "p2"},
                ),
            )

    def test_complete_patch_review_events_revalidate_client_action_capabilities(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        caps = _capabilities(actions_supported=("preview_patch", "reject_patch"))

        with self.assertRaisesRegex(ValueError, "Client does not support A2UI stream event action id"):
            build_complete_patch_review_action_selected_event(
                event_id="evt-1",
                run_id="run-1",
                sequence=1,
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=caps,
            )
        with self.assertRaisesRegex(ValueError, "Client does not support A2UI stream event action id"):
            build_complete_patch_review_action_resolved_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=caps,
            )

    def test_complete_patch_review_action_resolved_event_rejects_wrong_status(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "resolved status does not match"):
            build_complete_patch_review_action_resolved_event(
                event_id="evt-1",
                run_id="run-1",
                sequence=1,
                card=card,
                patch_id="p1",
                control="preview",
                status="applied",
            )

    def test_complete_patch_review_events_reject_unknown_control(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "control must be 'preview', 'apply', or 'reject'"):
            build_complete_patch_review_action_selected_event(
                event_id="evt-1",
                run_id="run-1",
                sequence=1,
                card=card,
                patch_id="p1",
                control="delete",
            )
        with self.assertRaisesRegex(ValueError, "control must be 'preview', 'apply', or 'reject'"):
            build_complete_patch_review_action_resolved_event(
                event_id="evt-2",
                run_id="run-1",
                sequence=2,
                card=card,
                patch_id="p1",
                control="delete",
            )

    def test_complete_patch_review_action_selected_event_requires_full_demo_controls(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            }
        )

        with self.assertRaisesRegex(ValueError, "Complete patch review is missing: reject"):
            build_complete_patch_review_action_selected_event(
                event_id="evt-4",
                run_id="run-1",
                sequence=4,
                card=card,
                patch_id="p1",
                control="apply",
            )

    def test_streaming_events_are_rejected_when_client_does_not_support_streaming(self) -> None:
        caps = _capabilities()
        caps = A2UICapabilities(
            a2ui_version=caps.a2ui_version,
            client_name=caps.client_name,
            cards_supported=caps.cards_supported,
            primitive_blocks_supported=caps.primitive_blocks_supported,
            actions_supported=caps.actions_supported,
            max_payload_bytes=caps.max_payload_bytes,
            supports_streaming=False,
        )

        with self.assertRaisesRegex(ValueError, "does not support A2UI streaming"):
            validate_stream_event(
                {
                    "contract_version": 1,
                    "event_id": "evt-1",
                    "run_id": "run-1",
                    "sequence": 1,
                    "event_type": "card_published",
                    "card": {"type": "GenericCard", "title": "Run", "blocks": []},
                },
                caps,
            )

    def test_streaming_events_reject_patch_review_selection_policy_tampering(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_decision_selection(card, patch_id="p1", decision="apply")
        selection["execution_policy"] = deepcopy(PATCH_REVIEW_EXECUTION_POLICY["preview"])

        with self.assertRaisesRegex(ValueError, "execution policy does not match engine policy"):
            validate_stream_event(
                {
                    "contract_version": 1,
                    "event_id": "evt-1",
                    "run_id": "run-1",
                    "sequence": 1,
                    "event_type": "action_selected",
                    "action_id": "apply_patch",
                    "selection": selection,
                }
            )

    def test_streaming_events_reject_untyped_patch_review_selection_fields(self) -> None:
        card = materialize_terminal_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch choices",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Choose"}],
                "actions": [
                    {"id": "preview_patch", "label": "Preview", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                ],
            }
        )
        selection = build_patch_preview_selection(card, patch_id="p1")
        selection["target_file"] = "chapter.md"

        with self.assertRaisesRegex(ValueError, "Unsupported patch preview selection field"):
            validate_stream_event(
                {
                    "contract_version": 1,
                    "event_id": "evt-1",
                    "run_id": "run-1",
                    "sequence": 1,
                    "event_type": "action_selected",
                    "action_id": "preview_patch",
                    "selection": selection,
                }
            )

    def test_streaming_events_reject_untyped_patch_review_metadata(self) -> None:
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 1,
            "action_identity": "apply_patch:1:p1",
            "action_authority": PATCH_REVIEW_ACTION_AUTHORITY,
            "demo_path_step": PATCH_REVIEW_DEMO_PATH_STEP,
            "execution_policy": PATCH_REVIEW_EXECUTION_POLICY["apply"],
            "patch_id": "p1",
        }

        with self.assertRaisesRegex(
            ValueError,
            "Patch review selection must identify preview or decision policy",
        ):
            validate_stream_event(
                {
                    "contract_version": 1,
                    "event_id": "evt-1",
                    "run_id": "run-1",
                    "sequence": 1,
                    "event_type": "action_selected",
                    "action_id": "apply_patch",
                    "selection": selection,
                }
            )

    def test_streaming_events_reject_untyped_metadata_fields(self) -> None:
        selection = {
            "contract_version": ACTION_SELECTION_CONTRACT_VERSION,
            "selection_model": "one_based_action_slot",
            "slot": 1,
            "action_identity": "apply_patch:1:p1",
            "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
            "patch_decision": "apply",
            "patch_id": "p1",
        }

        with self.assertRaisesRegex(ValueError, "Unsupported A2UI stream event field"):
            validate_stream_event(
                {
                    "contract_version": 1,
                    "event_id": "evt-1",
                    "run_id": "run-1",
                    "sequence": 1,
                    "event_type": "action_selected",
                    "action_id": "apply_patch",
                    "selection": selection,
                    "target_file": "chapter.md",
                }
            )

        with self.assertRaisesRegex(ValueError, "message must be a non-empty string"):
            validate_stream_event(
                {
                    "contract_version": 1,
                    "event_id": "evt-2",
                    "run_id": "run-1",
                    "sequence": 2,
                    "event_type": "action_resolved",
                    "action_id": "apply_patch",
                    "status": "applied",
                    "selection": selection,
                    "message": "",
                }
            )

    def test_terminal_can_render_inline_generic_and_unknown_cards(self) -> None:
        generic = {
            "type": "GenericCard",
            "title": "Run Log",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
        }
        text = render_terminal_card(generic)
        self.assertIn("[GenericCard] Run Log", text)
        self.assertIn("Hello", text)

        unknown = build_unknown_card({"type": "FutureCard", "payload": 1})
        unknown_text = render_terminal_card(unknown)
        self.assertIn("[UnknownCard] Unsupported card type: FutureCard", unknown_text)


if __name__ == "__main__":
    unittest.main()
