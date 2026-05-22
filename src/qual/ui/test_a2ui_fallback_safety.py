from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.qual.ui.a2ui import (
    A2UICapabilities,
    build_unknown_card,
    engine_prepare_card,
    render_terminal_card,
    studio_materialize_card,
)


def _capabilities(
    *,
    cards_supported: tuple[str, ...] = (),
    actions_supported: tuple[str, ...] = ("preview_patch", "apply_patch", "reject_patch", "copy_to_clipboard"),
) -> A2UICapabilities:
    return A2UICapabilities(
        a2ui_version=1,
        client_name="CLI",
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


class A2UIFallbackSafetyTests(unittest.TestCase):
    def test_unknown_card_copy_action_respects_client_capabilities(self) -> None:
        card = build_unknown_card(
            {"type": "FutureCard", "blocks": [{"type": "MarkdownBlock", "markdown": "body"}]},
            _capabilities(actions_supported=("apply_patch",)),
        )

        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["actions"], [])
        self.assertIn("body", render_terminal_card(card))

    def test_studio_unsupported_card_filters_unknown_fallback_actions(self) -> None:
        card = studio_materialize_card(
            {"type": "FutureCard", "title": "Future"},
            _capabilities(actions_supported=("reject_patch",)),
        )

        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["actions"], [])

    def test_engine_generic_fallback_preserves_patch_review_action_order(self) -> None:
        card = engine_prepare_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "actions": [
                    {"id": "reject_patch", "label": "Reject Patch", "payload": {"patch_id": "p1"}},
                    {"id": "preview_patch", "label": "Preview Patch", "payload": {"patch_id": "p1"}},
                    {"id": "apply_patch", "label": "Apply Patch", "payload": {"patch_id": "p1"}},
                ],
            },
            _capabilities(cards_supported=("RunLogCard",)),
        )

        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(
            [action["id"] for action in card["actions"]],
            ["preview_patch", "apply_patch", "reject_patch"],
        )
        text = render_terminal_card(card)
        self.assertIn("1. Preview Patch [preview_patch, preview]", text)
        self.assertIn("2. Apply Patch [apply_patch, apply]", text)
        self.assertIn("3. Reject Patch [reject_patch, reject]", text)


if __name__ == "__main__":
    unittest.main()
