from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    build_unknown_card,
    engine_prepare_card,
    execute_action_with_policy_gate,
    materialize_action_slots,
    materialize_patch_selection_envelope,
    render_terminal_card,
    resolve_action_selection,
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
        payload = {
            "type": "ProposedEditCard",
            "title": "Patch",
            "actions": [
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
            ],
        }
        card = engine_prepare_card(payload, caps)
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["blocks"][0]["type"], "AlertBlock")
        self.assertEqual([action["id"] for action in card["actions"]], ["apply_patch", "reject_patch"])

    def test_studio_renders_unknown_card_for_unsupported_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertIn("Unsupported card type", card["title"])
        self.assertEqual(card["actions"][0]["id"], "copy_to_clipboard")

    def test_unknown_card_fallback_filters_copy_action_by_capability(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",), actions_supported=("apply_patch",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["actions"], [])

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
            ["apply_patch", "copy_to_clipboard", "reject_patch"],
        )

    def test_action_slots_are_one_based_and_resolve_cli_selection(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }
        slots = materialize_action_slots(card)
        self.assertEqual([slot["slot"] for slot in slots], [1, 2])
        self.assertEqual([slot["command"] for slot in slots], ["1", "2"])

        selected = resolve_action_selection(card, "apply")

        self.assertEqual(selected.id, "apply_patch")
        self.assertEqual(selected.payload, {"patch_id": "p1"})

    def test_patch_selection_envelope_exposes_preview_apply_reject_controls(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "diff"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply Patch", "payload": {"patch_id": "p9"}},
                {"id": "reject_patch", "label": "Reject Patch", "payload": {"patch_id": "p9"}},
            ],
        }

        envelope = materialize_patch_selection_envelope(card)

        self.assertEqual(envelope["type"], "PatchActionSelection")
        self.assertEqual(envelope["preview"]["command"], "preview")
        self.assertEqual([slot["action"]["id"] for slot in envelope["actions"]], ["apply_patch", "reject_patch"])

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

    def test_terminal_renders_cli_action_slots_for_patch_controls(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "diff"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply Patch", "payload": {"patch_id": "p1"}},
                {"id": "reject_patch", "label": "Reject Patch", "payload": {"patch_id": "p1"}},
            ],
        }

        text = render_terminal_card(card)

        self.assertIn("1. Apply Patch [apply_patch, apply]", text)
        self.assertIn("2. Reject Patch [reject_patch, reject]", text)


if __name__ == "__main__":
    unittest.main()
