from __future__ import annotations

import unittest

from src.qual.ui.a2ui import (
    A2UI_ACTION_SCHEMA_VERSION,
    A2UICapabilities,
    ActionRef,
    action_contract_fingerprint,
    build_unknown_card,
    describe_a2ui_contract,
    describe_action_contract,
    describe_selection_contract,
    engine_prepare_card,
    render_terminal_action,
    render_terminal_card,
    render_terminal_selection,
)


class _OpaqueValue:
    pass


def _capabilities() -> A2UICapabilities:
    return A2UICapabilities(
        a2ui_version=1,
        client_name="Exegesis Studio",
        cards_supported=("RunLogCard",),
        primitive_blocks_supported=(
            "MarkdownBlock",
            "KeyValueBlock",
            "ListBlock",
            "TableBlock",
            "AlertBlock",
            "ProgressBlock",
            "CodeBlock",
        ),
        actions_supported=("copy_to_clipboard",),
        max_payload_bytes=1_000_000,
        supports_streaming=True,
    )


class A2UIFallbackSafetyTests(unittest.TestCase):
    def test_selection_contract_manifest_exposes_contract_fingerprint_alias(self) -> None:
        manifest = describe_selection_contract()

        self.assertEqual(manifest["contract_fingerprint"], manifest["selection_fingerprint"])
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)

    def test_a2ui_contract_manifest_exposes_action_contract_alias(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["action"], describe_action_contract())
        self.assertEqual(manifest["action"]["contract_fingerprint"], manifest["action"]["action_fingerprint"])
        self.assertEqual(len(manifest["action"]["contract_fingerprint"]), 64)

    def test_action_contract_manifest_exposes_contract_fingerprint_alias(self) -> None:
        manifest = describe_action_contract()

        self.assertEqual(manifest["contract_fingerprint"], manifest["action_fingerprint"])
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(manifest["action_schema_version"], A2UI_ACTION_SCHEMA_VERSION)
        self.assertEqual(manifest["type"], "ActionRef")

    def test_action_contract_manifest_lists_canonical_payload_schemas(self) -> None:
        manifest = describe_action_contract()

        self.assertEqual(
            manifest["allowed_actions"],
            [
                "apply_patch",
                "copy_to_clipboard",
                "create_context_set",
                "export_document",
                "open_corpus_item",
                "open_section",
                "pin_to_context_set",
                "refresh_license",
                "reject_patch",
                "run_agent",
            ],
        )
        self.assertEqual(
            manifest["payload_schemas"],
            [
                {"id": "apply_patch", "version": 1, "fields": ["patch_id"]},
                {"id": "copy_to_clipboard", "version": 1, "fields": ["text"]},
                {"id": "create_context_set", "version": 1, "fields": ["name"]},
                {"id": "export_document", "version": 1, "fields": ["format"]},
                {"id": "open_corpus_item", "version": 1, "fields": ["item_id"]},
                {"id": "open_section", "version": 1, "fields": ["section_id"]},
                {"id": "pin_to_context_set", "version": 1, "fields": ["item_id"]},
                {"id": "refresh_license", "version": 1, "fields": []},
                {"id": "reject_patch", "version": 1, "fields": ["patch_id"]},
                {"id": "run_agent", "version": 1, "fields": ["operation"]},
            ],
        )
        self.assertEqual(action_contract_fingerprint(), manifest["contract_fingerprint"])

    def test_terminal_renderer_renders_canonical_actionref_and_invalid_fallback(self) -> None:
        text = render_terminal_action(
            ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
                confirm={"title": " Approve ", "message": " Export now? "},
                policy_sensitive=True,
            )
        )

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertIn("- id: export_document", text)
        self.assertIn('- payload: {"format":"md"}', text)
        self.assertIn('- confirm: {"message":"Export now?","title":"Approve"}', text)
        self.assertIn("- policy_sensitive: true", text)

        invalid = render_terminal_action(
            {
                "id": "launch_missiles",
                "label": "Run",
                "payload": {"operation": "x"},
                "icon": "sparkle",
            }
        )

        self.assertIn("[ActionRef] <invalid action>", invalid)
        self.assertIn("Action schema v1", invalid)
        self.assertIn('"icon":"sparkle"', invalid)

    def test_engine_materializes_generic_cards_by_sanitizing_unsupported_content(self) -> None:
        card = engine_prepare_card(
            {
                "type": "GenericCard",
                "title": "   ",
                "subtitle": "  Ready  ",
                "blocks": [
                    {"type": "ChartBlock", "series": [1, 2, 3]},
                    {"type": "MarkdownBlock", "markdown": "Kept"},
                    {
                        "type": "KeyValueBlock",
                        "items": [
                            {"key": "Owner", "value": "alice"},
                            {"key": "Opaque", "value": _OpaqueValue()},
                        ],
                    },
                ],
                "actions": [
                    {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "safe"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
                "trace_id": "drop-me",
            },
            _capabilities(),
        )

        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["title"], "<untitled>")
        self.assertEqual(card["subtitle"], "Ready")
        self.assertNotIn("trace_id", card)
        self.assertEqual(
            card["blocks"],
            [
                {"type": "MarkdownBlock", "markdown": "Kept"},
                {"type": "KeyValueBlock", "items": [{"key": "Owner", "value": "alice"}]},
            ],
        )
        self.assertEqual(
            card["actions"],
            [{"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "safe"}}],
        )

        text = render_terminal_card(card)
        self.assertIn("[GenericCard] <untitled>", text)
        self.assertIn("Ready", text)
        self.assertIn("- Owner: alice", text)
        self.assertIn("- Copy (copy_to_clipboard)", text)
        self.assertNotIn("ChartBlock", text)
        self.assertNotIn("Opaque", text)

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

    def test_terminal_renderers_escape_unicode_format_controls(self) -> None:
        unsafe_title = "Future\u202eCard"
        unsafe_label = "Choice\u202eOne"

        card_text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": unsafe_title,
                "blocks": [{"type": "MarkdownBlock", "markdown": "safe"}],
                "actions": [],
            }
        )
        selection_text = render_terminal_selection(
            {
                "id": "choice-1",
                "label": unsafe_label,
                "payload": {"note": "safe"},
            }
        )

        self.assertIn("Future\\u202eCard", card_text)
        self.assertNotIn(unsafe_title, card_text)
        self.assertIn("Choice\\u202eOne", selection_text)
        self.assertNotIn(unsafe_label, selection_text)

    def test_invalid_selection_renderer_keeps_safe_raw_preview(self) -> None:
        text = render_terminal_selection(
            {
                "id": " choice-1 ",
                "label": 123,
                "payload": {"secret": "safe"},
                "selected": "yes",
            }
        )

        self.assertIn("[SelectionRef] <invalid selection>", text)
        self.assertIn("Selection schema v1", text)
        self.assertIn('- raw: {"id":" choice-1 ","label":123,"payload":{"secret":"safe"},"selected":"yes"}', text)

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
