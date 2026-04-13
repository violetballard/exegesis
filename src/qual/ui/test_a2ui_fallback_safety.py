from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.qual.ui.a2ui import (
    A2UI_ACTION_SCHEMA_VERSION,
    A2UICapabilities,
    ActionRef,
    CARD_CONTRACT_VERSION,
    SELECTION_SCHEMA_VERSION,
    GENERIC_FALLBACK_SUBTITLE,
    card_contract_fingerprint,
    action_contract_fingerprint,
    build_unknown_card,
    describe_a2ui_contract,
    describe_a2ui_contract_fingerprints,
    describe_action_contract,
    describe_card_contract,
    describe_selection_contract,
    describe_terminal_fallback_contract,
    engine_prepare_card,
    render_terminal_action,
    render_terminal_artifact,
    render_terminal_card,
    render_terminal_selection,
    SelectionRef,
    terminal_fallback_contract_fingerprint,
)
from src.qual.ui.shell import ShellUI


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
        self.assertEqual(manifest["selection_schema_version"], SELECTION_SCHEMA_VERSION)
        self.assertEqual(manifest["selection_version"], SELECTION_SCHEMA_VERSION)

    def test_a2ui_contract_manifest_exposes_action_contract_alias(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["action"], describe_action_contract())
        self.assertEqual(manifest["action"]["contract_fingerprint"], manifest["action"]["action_fingerprint"])
        self.assertEqual(len(manifest["action"]["contract_fingerprint"]), 64)

    def test_a2ui_contract_fingerprint_map_matches_section_contracts(self) -> None:
        manifest = describe_a2ui_contract()
        fingerprints = describe_a2ui_contract_fingerprints()

        self.assertEqual(fingerprints["contract"], manifest["contract_fingerprint"])
        self.assertEqual(fingerprints["selection"], describe_selection_contract()["contract_fingerprint"])
        self.assertEqual(len(fingerprints["actions"]), 64)

    def test_card_contract_manifest_is_versioned_and_aligns_with_a2ui_schema(self) -> None:
        manifest = describe_card_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["card_contract_version"], CARD_CONTRACT_VERSION)
        self.assertEqual(manifest["type"], "CardContract")
        self.assertEqual(manifest["card_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprint"], manifest["card_fingerprint"])
        self.assertEqual(len(manifest["card_fingerprint"]), 64)
        self.assertEqual(manifest["card_schemas"], a2ui_manifest["schemas"]["cards"])
        self.assertEqual(manifest["fallbacks"], a2ui_manifest["fallbacks"])

    def test_terminal_fallback_contract_manifest_is_versioned_and_embedded_in_a2ui_contract(self) -> None:
        manifest = describe_terminal_fallback_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_fallback_schema_version"], 1)
        self.assertEqual(manifest["terminal_fallback_version"], 1)
        self.assertEqual(manifest["type"], "TerminalFallbackContract")
        self.assertEqual(manifest["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(manifest["default_kind"], "card")
        self.assertEqual(
            manifest["read_only_action"],
            {"id": "copy_to_clipboard", "label": "Copy JSON", "version": 1, "payload_fields": ["text"]},
        )
        self.assertEqual(manifest["card_fallbacks"], a2ui_manifest["fallbacks"])
        self.assertEqual(manifest["contract_fingerprint"], terminal_fallback_contract_fingerprint())
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(a2ui_manifest["schemas"]["terminal_fallback"], manifest)

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

    def test_terminal_artifact_dispatches_structured_payloads_and_shell_forwards(self) -> None:
        action = ActionRef(
            id=" export_document ",
            label=" Export ",
            payload={"format": "md"},
        )
        selection = SelectionRef(
            id=" choice-1 ",
            label=" Choice ",
            payload={"nested": {"items": [1, 2]}},
            selected=True,
        )
        card = {
            "type": "GenericCard",
            "title": " Run Log ",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
            "actions": [],
        }

        shell = ShellUI()

        self.assertIn("[ActionRef] Export", render_terminal_artifact(action))
        self.assertIn("[SelectionRef] Choice", render_terminal_artifact(selection))
        self.assertIn("[GenericCard] Run Log", render_terminal_artifact(card))
        self.assertIn("[ActionRef] Export", shell.render_artifact(action))
        self.assertIn("[SelectionRef] Choice", shell.render_artifact(selection))
        self.assertIn("[GenericCard] Run Log", shell.render_artifact(card))

    def test_terminal_artifact_uses_explicit_kind_for_raw_mappings(self) -> None:
        action_text = render_terminal_artifact(
            {"id": "export_document", "label": "Export", "payload": {"format": "md"}},
            kind="action",
        )
        selection_text = render_terminal_artifact(
            {"id": "choice-1", "label": "Choice", "payload": {"nested": {"items": [1, 2]}}},
            kind="selection",
        )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("[SelectionRef] Choice", selection_text)
        with self.assertRaises(ValueError):
            render_terminal_artifact({"type": "GenericCard", "title": "Run Log", "blocks": [], "actions": []}, kind="dialog")

    def test_generic_cards_preserve_nested_actionref_instances(self) -> None:
        raw_card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Kept"}],
            "actions": [
                ActionRef(
                    id=" apply_patch ",
                    label=" Apply ",
                    payload={"patch_id": "p1"},
                ),
            ],
        }

        caps = A2UICapabilities(
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
            actions_supported=("apply_patch",),
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )

        card = engine_prepare_card(raw_card, caps)

        self.assertEqual(
            card["actions"],
            [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}}],
        )

        text = render_terminal_card(raw_card)
        self.assertIn("- Apply (apply_patch)", text)
        self.assertNotIn("Actions: none available", text)

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

    def test_terminal_renderer_requires_read_only_actions_for_generic_fallback_inference(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback view for FutureCard",
                "subtitle": "Operator notes",
                "blocks": [],
                "actions": [
                    {
                        "id": "open_section",
                        "label": "Open",
                        "payload": {"section_id": "section-1"},
                    }
                ],
            }
        )

        self.assertIn("[GenericCard] Fallback view for FutureCard", text)
        self.assertIn("Operator notes", text)
        self.assertNotIn(GENERIC_FALLBACK_SUBTITLE, text)
        self.assertNotIn("Fallback: generic from", text)
        self.assertNotIn("Action policy: client_allowlist", text)
        self.assertNotIn("Debug:", text)
        self.assertIn("- Open (open_section)", text)

    def test_terminal_renderer_infers_generic_fallback_when_actions_are_canonical_copy_only(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback view for FutureCard",
                "blocks": [],
                "actions": [
                    {
                        "id": "copy_to_clipboard",
                        "label": "Copy JSON",
                        "payload": {"text": "{}"},
                    }
                ],
            }
        )

        self.assertIn("[GenericCard] Fallback view for FutureCard", text)
        self.assertIn(GENERIC_FALLBACK_SUBTITLE, text)
        self.assertIn("Fallback: generic from FutureCard", text)
        self.assertIn("Action policy: client_allowlist", text)
        self.assertIn("Debug:", text)
        self.assertIn("- contract_version: 2", text)
        self.assertIn("- fallback_kind: generic", text)
        self.assertIn("- source_card_type: FutureCard", text)
        self.assertIn("- Copy JSON (copy_to_clipboard)", text)

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

    def test_shell_ui_escapes_unicode_format_controls_in_preview(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=["alpha\u202ebeta"]),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn('- context_preview: "alpha\\\\u202ebeta"', text)
        self.assertNotIn("alpha\u202ebeta", text)

    def test_shell_ui_quotes_ambiguous_preview_tokens_and_keeps_set_order(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids={"gamma", "alpha beta"}),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn('- context_preview: "alpha beta", gamma', text)
        self.assertNotIn("alpha beta, gamma", text)

    def test_shell_ui_truncates_without_splitting_unicode_escape_sequences(self) -> None:
        self.assertEqual(ShellUI._format_item_id("x" * 18 + "\u202e" + "yz"), "xxxxxxxxxxxxxxxxxx...")


if __name__ == "__main__":
    unittest.main()
