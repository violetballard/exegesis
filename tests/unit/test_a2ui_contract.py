from __future__ import annotations

import unittest
from dataclasses import dataclass

import exegesis_shared.contracts as shared_contracts
from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    PATCH_DECISION_CONTRACT_VERSION,
    PATCH_PREVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_CONTRACT_VERSION,
    PATCH_REVIEW_DECISION_POLICY,
    PATCH_REVIEW_FLOW,
    PATCH_REVIEW_REQUIRED_PARTS,
)
from exegesis_shared.contracts import studio_materialize_card as shared_studio_materialize_card
from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    CompletePatchReviewActions,
    PATCH_REVIEW_REQUIRED_PARTS as UI_PATCH_REVIEW_REQUIRED_PARTS,
    PatchReviewActionSelection,
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
    complete_patch_review_action_from_card,
    complete_patch_review_actions_from_card,
    complete_patch_review_actions_from_contract,
    complete_patch_review_action_refs_from_contract,
    engine_prepare_card,
    execute_complete_patch_review_action_with_policy_gate,
    execute_action_with_policy_gate,
    execute_patch_review_selection_with_policy_gate,
    materialize_patch_preview_contract,
    materialize_proposed_edit_card,
    materialize_terminal_card,
    patch_decision_action_ref_from_selection,
    patch_preview_action_ref_from_selection,
    patch_review_action_ref_from_selection,
    patch_review_action_selection_from_selection,
    patch_review_availability_from_contract,
    patch_review_action_refs_from_contract,
    patch_review_control_actions_from_contract,
    patch_review_control_slots_from_contract,
    render_terminal_card,
    resolve_card_selection_contract,
    resolve_patch_decision_action,
    resolve_patch_decision_selection,
    resolve_patch_preview_action,
    resolve_patch_preview_selection,
    resolve_patch_review_contract,
    resolve_patch_review_selection,
    studio_materialize_card,
    validate_action_ref,
    validate_capabilities,
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
        "pin_to_context_set",
        "create_context_set",
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
    def test_capabilities_handshake_is_stored_per_session(self) -> None:
        store = A2UISessionStore()
        caps = _capabilities()
        validate_capabilities(caps)
        store.register("sess-1", caps)
        self.assertEqual(store.get("sess-1").client_name, "Exegesis Studio")

    def test_session_store_rejects_invalid_capabilities_before_registration(self) -> None:
        store = A2UISessionStore()
        caps = _capabilities(actions_supported=("apply_patch", "delete_project"))

        with self.assertRaisesRegex(ValueError, "Unknown action in capabilities"):
            store.register("sess-1", caps)

        with self.assertRaisesRegex(KeyError, "Unknown session"):
            store.get("sess-1")

    def test_session_store_requires_stable_session_id(self) -> None:
        store = A2UISessionStore()

        with self.assertRaisesRegex(ValueError, "session_id is required"):
            store.register(" ", _capabilities())

    def test_engine_falls_back_to_generic_for_unsupported_specialized_card(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {"type": "RunDecisionCard", "title": "Patch"}
        card = engine_prepare_card(payload, caps)
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["blocks"][0]["type"], "AlertBlock")

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

    def test_studio_renders_unknown_card_for_unsupported_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertIn("Unsupported card type", card["title"])
        self.assertEqual(card["actions"][0]["id"], "copy_to_clipboard")

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
            ["* 1. Apply", "* 2. Reject", "* 3. Revise"],
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
                    "patch_decision_contract_version": PATCH_DECISION_CONTRACT_VERSION,
                    "patch_decision": "apply",
                    "patch_id": "p1",
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
                "required": ["preview", "apply", "reject"],
                "available": ["preview", "apply", "reject"],
                "missing": [],
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
            {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
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
        self.assertFalse(availability["is_complete"])

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
        self.assertEqual(availability["flow"], PATCH_REVIEW_FLOW)
        self.assertEqual(availability["decision_policy"], PATCH_REVIEW_DECISION_POLICY)
        self.assertTrue(availability["is_complete"])

    def test_patch_review_required_parts_are_shared_and_cli_exported(self) -> None:
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
        self.assertEqual(selection["patch_decision_contract_version"], PATCH_DECISION_CONTRACT_VERSION)
        self.assertEqual(selection["patch_decision"], "apply")
        self.assertEqual(selection["patch_id"], "p1")
        self.assertEqual(selection["slot"], 1)
        self.assertEqual(selection["action_identity"], card["action_selection"]["order"][0]["action_identity"])
        self.assertEqual(decision_entry["selection"], selection)
        self.assertEqual(
            resolve_patch_decision_selection(card, selection, patch_id="p1")["id"],
            "apply_patch",
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

        with self.assertRaisesRegex(ValueError, "Action not supported by client"):
            execute_complete_patch_review_action_with_policy_gate(
                card=card,
                patch_id="p1",
                control="apply",
                capabilities=_capabilities(actions_supported=("preview_patch", "reject_patch")),
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

    def test_action_payload_rejects_untyped_extra_fields_before_policy_gate(self) -> None:
        executed: list[str] = []
        action = ActionRef(
            id="apply_patch",
            label="Apply",
            payload={"patch_id": "p1", "target_file": "chapter.md"},
        )

        with self.assertRaisesRegex(ValueError, "Unsupported payload field"):
            execute_action_with_policy_gate(
                action=action,
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(True),
                executor=lambda a: executed.append(a.id),
            )

        self.assertEqual(executed, [])

    def test_action_ref_metadata_rejects_bad_runtime_values_before_policy_gate(self) -> None:
        executed: list[str] = []
        action = ActionRef(
            id="apply_patch",
            label="Apply",
            payload={"patch_id": "p1"},
            confirm={"title": ""},
        )

        with self.assertRaisesRegex(ValueError, "confirm values must be non-empty strings"):
            execute_action_with_policy_gate(
                action=action,
                capabilities=_capabilities(),
                policy_gate=_PolicyGateStub(True),
                executor=lambda a: executed.append(a.id),
            )

        self.assertEqual(executed, [])

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
