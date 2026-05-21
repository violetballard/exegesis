from __future__ import annotations

import unittest
from dataclasses import dataclass

import exegesis_shared.contracts as shared_contracts
from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    PATCH_DECISION_CONTRACT_VERSION,
)
from exegesis_shared.contracts import studio_materialize_card as shared_studio_materialize_card
from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    build_unknown_card,
    engine_prepare_card,
    execute_action_with_policy_gate,
    materialize_proposed_edit_card,
    materialize_terminal_card,
    render_terminal_card,
    resolve_card_selection_contract,
    resolve_patch_decision_selection,
    studio_materialize_card,
    validate_capabilities,
)


def _capabilities(
    *,
    cards_supported: tuple[str, ...] = ("ProposedEditCard",),
    actions_supported: tuple[str, ...] = (
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


class A2UIContractTests(unittest.TestCase):
    def test_capabilities_handshake_is_stored_per_session(self) -> None:
        store = A2UISessionStore()
        caps = _capabilities()
        validate_capabilities(caps)
        store.register("sess-1", caps)
        self.assertEqual(store.get("sess-1").client_name, "Exegesis Studio")

    def test_engine_falls_back_to_generic_for_unsupported_specialized_card(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {"type": "RunDecisionCard", "title": "Patch"}
        card = engine_prepare_card(payload, caps)
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["blocks"][0]["type"], "AlertBlock")

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
        self.assertEqual([action["id"] for action in materialized["actions"]], ["apply_patch", "reject_patch"])
        self.assertEqual(
            [action["payload"] for action in materialized["actions"]],
            [{"patch_id": "patch-1"}, {"patch_id": "patch-1"}],
        )
        self.assertEqual(materialized["patch_decision"]["contract_version"], PATCH_DECISION_CONTRACT_VERSION)
        self.assertEqual(materialized["patch_decision"]["patch_id"], "patch-1")
        self.assertEqual(
            [
                (entry["decision"], entry["slot"], entry["action_id"])
                for entry in materialized["patch_decision"]["decisions"]
            ],
            [("apply", 1, "apply_patch"), ("reject", 2, "reject_patch")],
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
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "other"}},
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
