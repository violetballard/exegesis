from __future__ import annotations

import unittest

from exegesis_shared.contracts.actions import ACTION_SELECTION_CONTRACT_VERSION
from src.qual.ui.a2ui import (
    A2UICapabilities,
    materialize_terminal_card,
    render_terminal_card,
    resolve_card_selection_by_index,
    studio_materialize_card,
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
        client_name="Exegesis CLI",
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
        supports_streaming=False,
    )


class A2UICliFallbackSafetyTests(unittest.TestCase):
    def test_terminal_materialization_preserves_versioned_one_based_selection(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "run_agent", "label": "Revise", "payload": {"operation": "revise"}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }

        materialized = materialize_terminal_card(card)

        self.assertEqual(
            materialized["action_selection"]["contract_version"],
            ACTION_SELECTION_CONTRACT_VERSION,
        )
        self.assertEqual(materialized["action_selection"]["selection_model"], "one_based_action_slot")
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in materialized["action_selection"]["order"]],
            [(1, "apply_patch"), (2, "reject_patch"), (3, "run_agent")],
        )
        self.assertEqual(resolve_card_selection_by_index(materialized, 1)["payload"], {"patch_id": "p1"})

    def test_terminal_rendering_uses_canonical_fallback_action_order(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
            "actions": [
                {"id": "run_agent", "label": "Revise", "payload": {"operation": "revise"}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            ],
        }

        text = render_terminal_card(card)

        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("* ")],
            ["* 1. Apply", "* 2. Reject", "* 3. Revise"],
        )

    def test_terminal_rendering_surfaces_patch_confirmation_prompts(self) -> None:
        card = studio_materialize_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [],
            },
            _capabilities(actions_supported=("preview_patch", "apply_patch", "reject_patch")),
        )

        text = render_terminal_card(card)

        self.assertIn("Patch review flow: preview_then_decide", text)
        self.assertIn("Patch review decision policy: apply_or_reject", text)
        self.assertIn("Patch review action authority: engine_revalidated", text)
        self.assertIn("Patch review demo path step: preview_apply_or_reject_patch", text)
        self.assertIn("Patch review status: complete", text)
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("* ")],
            [
                "* 1. Preview patch",
                "* 2. Apply patch [confirm: Apply patch?]",
                "* 3. Reject patch [confirm: Reject patch?]",
            ],
        )
        self.assertIn("Patch review controls: preview=1, apply=2, reject=3", text)
        self.assertIn("Patch review CLI commands: preview=1, apply=2, reject=3", text)
        self.assertIn("Patch review decision controls: apply=2, reject=3", text)
        self.assertIn(
            "Patch review decision command lookup: "
            "2->apply, 3->reject, apply->apply, apply_patch->apply, "
            "reject->reject, reject_patch->reject",
            text,
        )
        self.assertIn(
            "Patch review CLI aliases: "
            "preview=preview/preview_patch, apply=apply/apply_patch, reject=reject/reject_patch",
            text,
        )
        self.assertIn(
            "Patch review CLI command lookup: "
            "1->preview, 2->apply, 3->reject, apply->apply, apply_patch->apply, "
            "preview->preview, preview_patch->preview, reject->reject, reject_patch->reject",
            text,
        )

    def test_terminal_rendering_surfaces_missing_patch_controls(self) -> None:
        card = studio_materialize_card(
            {
                "type": "ProposedEditCard",
                "patch_id": "p1",
                "title": "Patch",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [],
            },
            _capabilities(actions_supported=("preview_patch", "apply_patch")),
        )

        text = render_terminal_card(card)

        self.assertIn("Patch review status: incomplete", text)
        self.assertIn("Patch review controls: preview=1, apply=2", text)
        self.assertIn("Patch review missing controls: reject", text)
        self.assertIn("Patch review next required CLI aliases: reject/reject_patch", text)

    def test_terminal_fallback_preserves_distinct_patch_action_slots(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch choices",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Choose a patch"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply A", "payload": {"patch_id": "a"}},
                {"id": "apply_patch", "label": "Apply B", "payload": {"patch_id": "b"}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "a"}},
            ],
        }

        materialized = materialize_terminal_card(card)
        text = render_terminal_card(card)

        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in materialized["action_selection"]["order"]],
            [(1, "apply_patch"), (2, "apply_patch"), (3, "reject_patch")],
        )
        self.assertEqual(resolve_card_selection_by_index(materialized, 2)["payload"], {"patch_id": "b"})
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("* ")],
            ["* 1. Apply A", "* 2. Apply B", "* 3. Reject"],
        )

    def test_terminal_fallback_drops_blank_patch_action_slots(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch choices",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Choose a patch"}],
            "actions": [
                {"id": "apply_patch", "label": "Apply blank", "payload": {"patch_id": " "}},
                {"id": "reject_patch", "label": "Reject blank", "payload": {"patch_id": ""}},
                {"id": "apply_patch", "label": "Apply A", "payload": {"patch_id": "a"}},
            ],
        }

        materialized = materialize_terminal_card(card)
        text = render_terminal_card(card)

        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in materialized["action_selection"]["order"]],
            [(1, "apply_patch")],
        )
        self.assertEqual(resolve_card_selection_by_index(materialized, 1)["payload"], {"patch_id": "a"})
        self.assertEqual([line for line in text.splitlines() if line.startswith("* ")], ["* 1. Apply A"])

    def test_unknown_card_fallback_stays_cli_renderable_when_copy_is_unsupported(self) -> None:
        caps = _capabilities(
            cards_supported=("RunLogCard",),
            actions_supported=("apply_patch", "reject_patch"),
        )

        card = studio_materialize_card({"type": "FutureCard", "title": "Future"}, caps)
        text = render_terminal_card(card)

        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["actions"], [])
        self.assertEqual(card["action_selection"]["order"], [])
        self.assertIn("[UnknownCard] Unsupported card type: FutureCard", text)

    def test_unknown_patch_card_fallback_preserves_typed_patch_actions(self) -> None:
        caps = _capabilities(
            cards_supported=("RunLogCard",),
            actions_supported=("apply_patch", "reject_patch"),
        )

        card = studio_materialize_card(
            {
                "type": "FuturePatchCard",
                "patch_id": "p1",
                "title": "Future patch",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Preview"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "run_agent", "label": "Revise", "payload": {"operation": "revise"}},
                ],
            },
            caps,
        )
        text = render_terminal_card(card)

        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["patch_id"], "p1")
        self.assertEqual(
            [(entry["slot"], entry["action_id"]) for entry in card["action_selection"]["order"]],
            [(1, "apply_patch"), (2, "reject_patch")],
        )
        self.assertEqual(resolve_card_selection_by_index(card, 1)["payload"], {"patch_id": "p1"})
        self.assertIn("Patch review controls: apply=1, reject=2", text)
        self.assertEqual(
            [line for line in text.splitlines() if line.startswith("* ")],
            ["* 1. Apply", "* 2. Reject"],
        )


if __name__ == "__main__":
    unittest.main()
