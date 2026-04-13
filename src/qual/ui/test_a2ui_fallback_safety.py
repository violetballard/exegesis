from __future__ import annotations

import unittest

from src.qual.ui.a2ui import build_unknown_card, render_terminal_card


class _OpaqueValue:
    pass


class A2UIFallbackSafetyTests(unittest.TestCase):
    def test_unknown_card_sanitizes_key_value_and_alert_blocks(self) -> None:
        unknown = build_unknown_card(
            {
                "type": "FutureCard",
                "title": "Future",
                "blocks": [
                    {
                        "type": "AlertBlock",
                        "severity": {"unexpected": "value"},
                        "title": 123,
                        "message": "Recovered",
                    },
                    {
                        "type": "KeyValueBlock",
                        "items": [
                            {"key": "Owner", "value": "alice"},
                            {"key": "Enabled", "value": True},
                            {"key": "Opaque", "value": _OpaqueValue()},
                        ],
                    },
                ],
            },
            supported_actions=("copy_to_clipboard",),
        )

        self.assertEqual(
            unknown["blocks"][0],
            {"type": "AlertBlock", "severity": "info", "message": "Recovered"},
        )
        self.assertEqual(
            unknown["blocks"][1],
            {
                "type": "KeyValueBlock",
                "items": [
                    {"key": "Owner", "value": "alice"},
                    {"key": "Enabled", "value": True},
                ],
            },
        )

        text = render_terminal_card(unknown)
        self.assertIn("INFO: Recovered", text)
        self.assertIn("- Owner: alice", text)
        self.assertIn("- Enabled: true", text)
        self.assertNotIn("- Opaque:", text)

    def test_terminal_renderer_skips_non_scalar_key_value_entries(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback",
                "blocks": [
                    {
                        "type": "KeyValueBlock",
                        "items": [
                            {"key": "Owner", "value": "alice"},
                            {"key": "Enabled", "value": True},
                            {"key": "Opaque", "value": _OpaqueValue()},
                        ],
                    }
                ],
            }
        )

        self.assertIn("[GenericCard] Fallback", text)
        self.assertIn("- Owner: alice", text)
        self.assertIn("- Enabled: true", text)
        self.assertNotIn("- Opaque:", text)


if __name__ == "__main__":
    unittest.main()
