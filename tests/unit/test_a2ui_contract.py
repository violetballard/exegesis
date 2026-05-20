from __future__ import annotations

import unittest
from dataclasses import dataclass

import exegesis_shared.contracts as shared_contracts
from exegesis_shared.contracts.actions import (
    ACTION_SELECTION_CONTRACT_VERSION,
    materialize_action_selection_contract,
)
from exegesis_shared.contracts import studio_materialize_card as shared_studio_materialize_card
from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    _terminal_action_slots,
    build_unknown_card,
    engine_prepare_card,
    execute_action_with_policy_gate,
    materialize_cli_fallback_card,
    materialize_terminal_card,
    resolve_card_selection_by_index,
    render_terminal_card,
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
        max_payload_bytes=1_000_000,
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
        payload = {"type": "ProposedEditCard", "title": "Patch"}
        card = engine_prepare_card(payload, caps)
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["blocks"][0]["type"], "AlertBlock")

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

    def test_filtered_actions_are_canonicalized_by_identity(self) -> None:
        caps = _capabilities(actions_supported=("reject_patch", "copy_to_clipboard", "apply_patch"))
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p2"}},
                {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "payload"}},
                {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "payload"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }

        filtered = studio_materialize_card(card, caps)

        self.assertEqual(
            [action["id"] for action in filtered["actions"]],
            ["apply_patch", "reject_patch", "copy_to_clipboard"],
        )

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
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {"id": "run_agent", "label": "Run", "payload": {"operation": "draft"}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }

        contract = materialize_action_selection_contract(card)
        fallback = materialize_cli_fallback_card(card)

        self.assertEqual(contract["contract_version"], ACTION_SELECTION_CONTRACT_VERSION)
        self.assertEqual(contract["selection_model"], "one_based_action_slot")
        self.assertEqual(fallback["action_selection"], contract)
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in contract["order"]],
            [(1, "apply_patch"), (2, "reject_patch"), (3, "run_agent")],
        )
        self.assertEqual(resolve_card_selection_by_index(fallback, 1)["payload"], {"patch_id": "p1"})

    def test_terminal_materialization_canonicalizes_patch_action_slots(self) -> None:
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

    def test_terminal_rendering_uses_materialized_selection_order(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "reject_patch", "label": "Reject patch", "payload": {"patch_id": "p9"}},
                {"id": "apply_patch", "label": "Apply patch", "payload": {"patch_id": "p9"}},
            ],
        }

        materialized = materialize_terminal_card(card)
        text = render_terminal_card(materialized)

        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in materialized["action_selection"]["order"]],
            [(1, "apply_patch"), (2, "reject_patch")],
        )
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("* ")],
            ["* 1. Apply patch", "* 2. Reject patch"],
        )

    def test_terminal_materialization_preserves_distinct_patch_action_slots(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch choices",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "reject_patch", "label": "Reject B", "payload": {"patch_id": "b"}},
                {"id": "apply_patch", "label": "Apply B", "payload": {"patch_id": "b"}},
                {"id": "reject_patch", "label": "Reject A", "payload": {"patch_id": "a"}},
                {"id": "apply_patch", "label": "Apply A", "payload": {"patch_id": "a"}},
            ],
        }

        materialized = materialize_terminal_card(card)
        text = render_terminal_card(materialized)

        self.assertEqual(
            [(action["id"], action["payload"]["patch_id"]) for action in materialized["actions"]],
            [("apply_patch", "a"), ("apply_patch", "b"), ("reject_patch", "a"), ("reject_patch", "b")],
        )
        self.assertEqual(
            [
                (entry["slot"], entry["action_id"])
                for entry in materialized["action_selection"]["order"]
            ],
            [(1, "apply_patch"), (2, "apply_patch"), (3, "reject_patch"), (4, "reject_patch")],
        )
        self.assertEqual(resolve_card_selection_by_index(materialized, 2)["payload"], {"patch_id": "b"})
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("* ")],
            ["* 1. Apply A", "* 2. Apply B", "* 3. Reject A", "* 4. Reject B"],
        )

    def test_terminal_action_slots_sort_materialized_selection_entries(self) -> None:
        materialized = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply patch", "payload": {"patch_id": "p9"}},
                {"id": "reject_patch", "label": "Reject patch", "payload": {"patch_id": "p9"}},
            ],
        }
        materialized["action_selection"] = materialize_action_selection_contract(materialized)
        materialized["action_selection"]["order"].reverse()

        self.assertEqual(
            [(slot["slot"], slot["action"]["id"]) for slot in _terminal_action_slots(materialized)],
            [(1, "apply_patch"), (2, "reject_patch")],
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
