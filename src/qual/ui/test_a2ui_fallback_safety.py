from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

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
    describe_terminal_artifact_contract_fingerprints,
    describe_terminal_artifact_contract,
    describe_terminal_fallback_contract,
    build_terminal_artifact_envelope,
    engine_prepare_card,
    render_terminal_action,
    render_terminal_artifact,
    render_terminal_card,
    render_terminal_selection,
    SelectionRef,
    selection_contract_fingerprint,
    terminal_artifact_contract_fingerprint,
    terminal_fallback_contract_fingerprint,
    TERMINAL_ARTIFACT_SCHEMA_VERSION,
    validate_terminal_artifact_envelope,
    validate_generic_card,
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
        self.assertEqual(manifest["terminal_artifact"], describe_terminal_artifact_contract())
        self.assertEqual(manifest["schemas"]["terminal_artifact"], describe_terminal_artifact_contract())
        self.assertEqual(
            manifest["terminal_artifact"]["contract_fingerprint"],
            manifest["schemas"]["terminal_artifact"]["contract_fingerprint"],
        )
        self.assertEqual(len(manifest["terminal_artifact"]["contract_fingerprint"]), 64)

    def test_a2ui_contract_manifest_exposes_terminal_fallback_and_artifact_fingerprints(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["terminal_fallback_fingerprint"], terminal_fallback_contract_fingerprint())
        self.assertEqual(manifest["terminal_artifact_fingerprint"], terminal_artifact_contract_fingerprint())
        self.assertEqual(
            manifest["terminal_fallback"]["contract_fingerprint"],
            manifest["terminal_fallback_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact"]["contract_fingerprint"],
            manifest["terminal_artifact_fingerprint"],
        )

    def test_a2ui_contract_fingerprint_map_matches_section_contracts(self) -> None:
        manifest = describe_a2ui_contract()
        fingerprints = describe_a2ui_contract_fingerprints()

        self.assertEqual(fingerprints["contract"], manifest["contract_fingerprint"])
        self.assertEqual(fingerprints["selection"], describe_selection_contract()["contract_fingerprint"])
        self.assertEqual(fingerprints["card_contract"], card_contract_fingerprint())
        self.assertEqual(fingerprints["terminal_fallback"], terminal_fallback_contract_fingerprint())
        self.assertEqual(len(fingerprints["actions"]), 64)

    def test_a2ui_contract_fingerprint_map_can_opt_into_terminal_artifact_dispatch(self) -> None:
        fingerprints = describe_a2ui_contract_fingerprints(include_terminal_artifact=True)

        self.assertEqual(fingerprints["terminal_artifact"], terminal_artifact_contract_fingerprint())
        self.assertEqual(len(fingerprints["terminal_artifact"]), 64)
        self.assertNotIn("terminal_artifact", describe_a2ui_contract_fingerprints())

    def test_terminal_artifact_contract_manifest_is_versioned_and_points_to_subcontracts(self) -> None:
        manifest = describe_terminal_artifact_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["type"], "TerminalArtifactContract")
        self.assertEqual(manifest["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(manifest["default_kind"], "card")
        self.assertEqual(manifest["kind_contracts"]["card"]["contract_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["kind_contracts"]["action"]["contract_fingerprint"], action_contract_fingerprint())
        self.assertEqual(
            manifest["kind_contracts"]["selection"]["contract_fingerprint"],
            describe_selection_contract()["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_fallback_contract"]["contract_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            describe_terminal_artifact_contract_fingerprints(),
        )
        self.assertEqual(
            set(manifest["contract_fingerprints"]),
            {
                "card_contract",
                "action_contract",
                "selection_contract",
                "terminal_fallback_contract",
            },
        )
        self.assertEqual(manifest["contract_fingerprints"]["card_contract"], card_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprints"]["action_contract"], action_contract_fingerprint())
        self.assertEqual(
            manifest["contract_fingerprints"]["selection_contract"],
            selection_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(manifest["contract_fingerprint"], terminal_artifact_contract_fingerprint())
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)

    def test_terminal_artifact_contract_version_alias_matches_schema_version(self) -> None:
        manifest = describe_terminal_artifact_contract()

        self.assertEqual(manifest["terminal_artifact_version"], manifest["terminal_artifact_schema_version"])
        self.assertEqual(manifest["terminal_artifact_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)

    def test_terminal_artifact_contract_manifest_includes_explicit_envelope_shape(self) -> None:
        manifest = describe_terminal_artifact_contract()

        self.assertEqual(manifest["envelope"]["type"], "TerminalArtifact")
        self.assertEqual(manifest["envelope"]["contract_version"], 2)
        self.assertEqual(manifest["envelope"]["a2ui_version"], 1)
        self.assertEqual(manifest["envelope"]["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["envelope"]["required_fields"], ["kind", "artifact"])
        self.assertEqual(manifest["envelope"]["optional_fields"], ["contract_version", "a2ui_version"])
        self.assertEqual(manifest["envelope"]["kind_field"], "kind")
        self.assertEqual(manifest["envelope"]["artifact_field"], "artifact")
        self.assertEqual(manifest["envelope"]["supported_kinds"], ["card", "action", "selection"])

    def test_terminal_artifact_envelope_builder_creates_canonical_payloads(self) -> None:
        action = ActionRef(
            id=" export_document ",
            label=" Export ",
            payload={"format": "md"},
            confirm={"title": " Approve ", "message": " Export now? "},
            policy_sensitive=True,
        )

        envelope = build_terminal_artifact_envelope(action, kind=" ACTION ")

        self.assertEqual(envelope["type"], "TerminalArtifact")
        self.assertEqual(envelope["kind"], "action")
        self.assertEqual(envelope["contract_version"], 2)
        self.assertEqual(envelope["a2ui_version"], 1)
        self.assertEqual(envelope["artifact"], action)
        validate_terminal_artifact_envelope(envelope)

        text = render_terminal_artifact(envelope)

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertIn("- confirm: {\"message\":\"Export now?\",\"title\":\"Approve\"}", text)

    def test_terminal_artifact_envelope_builder_rejects_kind_payload_mismatches(self) -> None:
        with self.assertRaises(ValueError):
            build_terminal_artifact_envelope(
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
                kind="card",
            )

        with self.assertRaises(ValueError):
            build_terminal_artifact_envelope(
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
                kind="action",
            )

    def test_terminal_artifact_envelope_validator_rejects_invalid_or_overspecified_payloads(self) -> None:
        with self.assertRaises(ValueError):
            validate_terminal_artifact_envelope({"type": "TerminalArtifact", "kind": "dialog", "artifact": {}})

        with self.assertRaises(ValueError):
            validate_terminal_artifact_envelope(
                {
                    "type": "TerminalArtifact",
                    "kind": "selection",
                    "artifact": {"id": "choice-1"},
                    "trace_id": "drop-me",
                }
            )

    def test_terminal_artifact_renderer_rejects_invalid_envelopes(self) -> None:
        with self.assertRaises(ValueError):
            render_terminal_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "action",
                    "artifact": {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                }
            )

        with self.assertRaises(ValueError):
            render_terminal_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "selection",
                    "artifact": {
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                    "contract_version": 999,
                }
            )

    def test_shell_ui_falls_back_to_safe_card_rendering_for_invalid_terminal_artifacts(self) -> None:
        shell = ShellUI()

        text = shell.render_artifact(
            {
                "type": "TerminalArtifact",
                "kind": "action",
                "artifact": {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
                "trace_id": "drop-me",
            }
        )

        self.assertIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertIn("TerminalArtifact schema v1", text)
        self.assertIn('"trace_id":"drop-me"', text)
        self.assertIn('"kind":"action"', text)

    def test_shell_ui_unwraps_valid_terminal_artifact_envelopes_during_fallback(self) -> None:
        shell = ShellUI()
        action_envelope = build_terminal_artifact_envelope(
            ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
            ),
            kind="action",
        )
        selection_envelope = build_terminal_artifact_envelope(
            SelectionRef(
                id=" choice-1 ",
                label=" Choice ",
                payload={"nested": {"items": [1, 2]}},
            ),
            kind="selection",
        )
        card_envelope = build_terminal_artifact_envelope(
            {
                "type": "GenericCard",
                "title": " Run Log ",
                "a2ui_version": 1,
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [],
            },
            kind="card",
        )

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(action_envelope)
            selection_text = shell.render_artifact(selection_envelope)
            card_text = shell.render_artifact(card_envelope)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)

        self.assertIn("[GenericCard] Run Log", card_text)
        self.assertIn("A2UI v1", card_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", card_text)

    def test_shell_ui_recovers_structured_kinds_from_raw_payloads_during_fallback(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                )
            )
            selection_text = shell.render_artifact(
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                )
            )
            typed_action_text = shell.render_artifact(
                {
                    "type": "ActionRef",
                    "id": " export_document ",
                    "label": " Export ",
                    "payload": {"format": "md"},
                }
            )
            typed_selection_text = shell.render_artifact(
                {
                    "type": "SelectionRef",
                    "id": " choice-1 ",
                    "label": " Choice ",
                    "payload": {"nested": {"items": [1, 2]}},
                }
            )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[GenericCard]", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[GenericCard]", selection_text)

        self.assertIn("[ActionRef] Export", typed_action_text)
        self.assertIn("Action schema v1", typed_action_text)
        self.assertNotIn("[GenericCard]", typed_action_text)

        self.assertIn("[SelectionRef] Choice", typed_selection_text)
        self.assertIn("Selection schema v1", typed_selection_text)
        self.assertNotIn("[GenericCard]", typed_selection_text)

    def test_shell_ui_keeps_cli_fallback_for_mismatched_terminal_artifacts(self) -> None:
        shell = ShellUI()

        text = shell.render_artifact(
            {
                "type": "TerminalArtifact",
                "kind": "action",
                "artifact": {
                    "type": "SelectionRef",
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
            }
        )

        self.assertIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertIn("TerminalArtifact schema v1", text)

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
        self.assertEqual(a2ui_manifest["terminal_fallback"], manifest)
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

    def test_shell_ui_forwards_explicit_artifact_kind_hints(self) -> None:
        shell = ShellUI()

        action_text = shell.render_artifact(
            {"id": "export_document", "label": "Export", "payload": {"format": "md"}},
            kind="action",
        )
        selection_text = shell.render_artifact(
            {"id": "choice-1", "label": "Choice", "payload": {"nested": {"items": [1, 2]}}},
            kind="selection",
        )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("[SelectionRef] Choice", selection_text)

    def test_shell_ui_falls_back_when_primary_renderer_raises_unexpected_error(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "type": "GenericCard",
                    "title": "Fallback",
                    "blocks": [],
                    "actions": [],
                }
            )

        self.assertIn("[GenericCard] Fallback", text)
        self.assertNotIn("boom", text)

    def test_shell_ui_preserves_explicit_kind_hints_during_fallback(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
                kind="action",
            )
            selection_text = shell.render_artifact(
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                kind="selection",
            )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertNotIn("[GenericCard]", action_text)
        self.assertNotIn("[GenericCard]", selection_text)

    def test_shell_ui_falls_back_to_invalid_action_when_action_recovery_renderer_raises(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch("src.qual.ui.shell.render_terminal_action", side_effect=RuntimeError("fallback boom")):
                text = shell.render_artifact(
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    kind="action",
                )

        self.assertIn("[ActionRef] <invalid action>", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("fallback boom", text)

    def test_shell_ui_falls_back_to_invalid_selection_when_selection_recovery_renderer_raises(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch("src.qual.ui.shell.render_terminal_selection", side_effect=RuntimeError("fallback boom")):
                text = shell.render_artifact(
                    {
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                    kind="selection",
                )

        self.assertIn("[SelectionRef] <invalid selection>", text)
        self.assertIn("Selection schema v1", text)
        self.assertNotIn("fallback boom", text)

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
        with self.assertRaises(ValueError):
            render_terminal_artifact({"type": "GenericCard", "title": "Run Log", "blocks": [], "actions": []}, kind=1)

    def test_terminal_artifact_infers_typed_action_and_selection_mappings(self) -> None:
        action_text = render_terminal_artifact(
            {"type": "ActionRef", "id": "export_document", "label": "Export", "payload": {"format": "md"}}
        )
        selection_text = render_terminal_artifact(
            {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
            }
        )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)

    def test_terminal_artifact_infers_action_and_selection_hints_without_type_markers(self) -> None:
        action_text = render_terminal_artifact(
            {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
                "confirm": {"title": "Approve", "message": "Proceed?"},
            }
        )
        selection_text = render_terminal_artifact(
            {
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
                "selected": True,
            }
        )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("- confirm: {\"message\":\"Proceed?\",\"title\":\"Approve\"}", action_text)
        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("- selected: true", selection_text)

    def test_terminal_artifact_envelope_renders_structured_payloads_and_rejects_conflicting_hints(self) -> None:
        action_text = render_terminal_artifact(
            {
                "type": "TerminalArtifact",
                "kind": "action",
                "artifact": {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
            }
        )
        selection_text = render_terminal_artifact(
            {
                "type": "TerminalArtifact",
                "kind": "selection",
                "artifact": {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
            }
        )
        card_text = render_terminal_artifact(
            {
                "type": "TerminalArtifact",
                "kind": "card",
                "artifact": {
                    "type": "GenericCard",
                    "title": "Run Log",
                    "blocks": [],
                    "actions": [],
                },
            }
        )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("[GenericCard] Run Log", card_text)

        with self.assertRaises(ValueError):
            render_terminal_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "action",
                    "artifact": {
                        "type": "SelectionRef",
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                },
                kind="selection",
            )

    def test_terminal_artifact_keeps_ambiguous_shared_key_mappings_as_cards(self) -> None:
        ambiguous = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        text = render_terminal_artifact(ambiguous)

        self.assertIn("[<missing>] <untitled>", text)
        self.assertNotIn("[ActionRef]", text)
        self.assertNotIn("[SelectionRef]", text)

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

    def test_validate_generic_card_accepts_actionref_instances_and_rejects_duplicates(self) -> None:
        validate_generic_card(
            {
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
        )

        with self.assertRaises(ValueError):
            validate_generic_card(
                {
                    "type": "GenericCard",
                    "title": "Patch",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "Kept"}],
                    "actions": [
                        ActionRef(
                            id=" apply_patch ",
                            label=" Apply ",
                            payload={"patch_id": "p1"},
                        ),
                        {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    ],
                }
            )

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

    def test_terminal_renderer_infers_generic_fallback_when_actions_are_missing(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback view for FutureCard",
                "blocks": [],
                "actions": None,
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
        self.assertNotIn("Actions:", text)

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

    def test_terminal_renderer_treats_generic_fallback_subtitle_as_a_fallback_signal(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Operator notes",
                "subtitle": GENERIC_FALLBACK_SUBTITLE,
                "blocks": [],
                "actions": None,
            }
        )

        self.assertIn("[GenericCard] Operator notes", text)
        self.assertIn(GENERIC_FALLBACK_SUBTITLE, text)
        self.assertIn("Fallback: generic card", text)
        self.assertIn("Action policy: client_allowlist", text)
        self.assertNotIn("Debug:", text)

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

    def test_terminal_renderer_marks_malformed_primitive_fields_without_object_repr_leaks(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback",
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": _OpaqueValue()},
                    {"type": "AlertBlock", "message": _OpaqueValue(), "severity": {"level": "info"}},
                    {"type": "CodeBlock", "code": _OpaqueValue()},
                    {"type": "ProgressBlock", "status_text": _OpaqueValue(), "title": _OpaqueValue()},
                    {"type": "ListBlock", "items": [{"label": _OpaqueValue()}]},
                    {"type": "TableBlock", "rows": [[_OpaqueValue(), 2, True, None]]},
                ],
                "actions": [],
            }
        )

        self.assertIn("[MarkdownBlock: invalid markdown]", text)
        self.assertIn("[AlertBlock: invalid message]", text)
        self.assertIn("[CodeBlock: invalid code]", text)
        self.assertIn("[ProgressBlock: invalid status_text]", text)
        self.assertIn("[table]", text)
        self.assertIn("- <non-json:_OpaqueValue> | 2 | true | <blank>", text)
        self.assertNotIn("object at 0x", text)

    def test_shell_ui_escapes_unicode_format_controls_in_preview(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=["alpha\u202ebeta"]),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn('- context_preview: "alpha\\\\u202ebeta"', text)
        self.assertNotIn("alpha\u202ebeta", text)

    def test_shell_ui_replaces_opaque_object_reprs_in_preview(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=[_OpaqueValue()]),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn("- context_items: 1", text)
        self.assertIn("- context_preview: <non-json:_OpaqueValue>", text)
        self.assertNotIn("object at 0x", text)

    def test_shell_ui_snapshot_sort_key_reuses_stable_opaque_preview_tokens(self) -> None:
        type_name, preview_token = ShellUI._snapshot_item_sort_key(_OpaqueValue())

        self.assertEqual(type_name, "_OpaqueValue")
        self.assertEqual(preview_token, "<non-json:_OpaqueValue>")

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
