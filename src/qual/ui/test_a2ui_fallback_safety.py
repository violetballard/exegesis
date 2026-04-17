from __future__ import annotations

import json
import unittest
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import patch

from src.qual.ui.a2ui import (
    A2UI_ACTION_SCHEMA_VERSION,
    A2UI_CAPABILITIES_SCHEMA_VERSION,
    A2UICapabilities,
    ActionRef,
    CARD_CONTRACT_VERSION,
    SELECTION_SCHEMA_VERSION,
    GENERIC_FALLBACK_SUBTITLE,
    card_contract_fingerprint,
    action_contract_fingerprint,
    a2ui_capabilities_contract_fingerprint,
    build_unknown_card,
    describe_a2ui_contract,
    describe_a2ui_contract_fingerprints,
    describe_a2ui_capabilities_contract,
    describe_action_contract,
    describe_card_contract,
    describe_selection_contract,
    describe_terminal_artifact_cli_fallback_contract,
    describe_terminal_artifact_cli_fallback_contract_fingerprints,
    describe_terminal_artifact_kind_contracts,
    describe_terminal_artifact_contract_fingerprints,
    describe_terminal_artifact_contract,
    describe_terminal_artifact_raw_leaf_card_default_contract,
    describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints,
    describe_terminal_artifact_render_target_contract,
    describe_terminal_artifact_render_target_contract_fingerprints,
    describe_terminal_artifact_rendering_contract,
    describe_terminal_artifact_rendering_contract_fingerprints,
    describe_terminal_fallback_contract,
    build_terminal_artifact_envelope,
    normalize_terminal_artifact_payload,
    engine_prepare_card,
    render_terminal_action,
    render_terminal_artifact,
    render_terminal_cli_fallback,
    render_terminal_card,
    render_terminal_selection,
    _render_payload_preview,
    SelectionRef,
    _should_preserve_raw_leaf_card_default,
    resolve_terminal_artifact_cli_fallback_target,
    resolve_terminal_artifact_render_target,
    selection_contract_fingerprint,
    terminal_artifact_contract_fingerprint,
    terminal_artifact_cli_fallback_contract_fingerprint,
    terminal_artifact_raw_leaf_card_default_contract_fingerprint,
    terminal_artifact_render_target_contract_fingerprint,
    terminal_artifact_rendering_contract_fingerprint,
    terminal_artifact_kind_contracts_fingerprint,
    terminal_fallback_contract_fingerprint,
    TERMINAL_ARTIFACT_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
    studio_materialize_card,
    validate_terminal_artifact_envelope,
    validate_generic_card,
)
from src.qual.ui.shell import ShellUI


class _OpaqueValue:
    pass


@dataclass
class _StructuredCard:
    type: str
    title: str
    a2ui_version: int
    blocks: list[dict[str, object]]
    actions: list[dict[str, object]]
    debug: dict[str, object] | None = None


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


_RAW_LEAF_CARD_DEFAULT_MANIFEST = {
    "preserve_when_kind_is_unset": True,
    "required_fields": ["id", "label", "payload"],
    "excluded_fields": ["type", "blocks", "actions", "confirm", "policy_sensitive", "selected", "disabled"],
}

_RAW_LEAF_CARD_DEFAULT_CONTRACT_MANIFEST = {
    "contract_version": 2,
    "a2ui_version": 1,
    "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
    "terminal_artifact_raw_leaf_card_default_schema_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
    "terminal_artifact_raw_leaf_card_default_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
    "type": "TerminalArtifactRawLeafCardDefaultContract",
    "default_kind": "card",
    "preserve_when_kind_is_unset": True,
    "required_fields": ["id", "label", "payload"],
    "excluded_fields": ["type", "blocks", "actions", "confirm", "policy_sensitive", "selected", "disabled"],
    "raw_leaf_card_default_contract_fingerprint": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
    "raw_leaf_card_default_contract_fingerprints": {
        "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
    },
}


class A2UIFallbackSafetyTests(unittest.TestCase):
    def test_selection_contract_manifest_exposes_contract_fingerprint_alias(self) -> None:
        manifest = describe_selection_contract()

        self.assertEqual(manifest["contract_fingerprint"], manifest["selection_fingerprint"])
        self.assertEqual(
            manifest["selection_contract_fingerprint"],
            manifest["selection_fingerprint"],
        )
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(manifest["selection_schema_version"], SELECTION_SCHEMA_VERSION)
        self.assertEqual(manifest["selection_version"], SELECTION_SCHEMA_VERSION)

    def test_standalone_contract_manifests_expose_contract_fingerprint_aliases(self) -> None:
        cases = [
            (
                "action",
                describe_action_contract(),
                "action_contract_fingerprint",
                action_contract_fingerprint(),
            ),
            (
                "card",
                describe_card_contract(),
                "card_contract_fingerprint",
                card_contract_fingerprint(),
            ),
            (
                "selection",
                describe_selection_contract(),
                "selection_contract_fingerprint",
                selection_contract_fingerprint(),
            ),
            (
                "terminal_fallback",
                describe_terminal_fallback_contract(),
                "terminal_fallback_contract_fingerprint",
                terminal_fallback_contract_fingerprint(),
            ),
            (
                "terminal_artifact",
                describe_terminal_artifact_contract(),
                "terminal_artifact_contract_fingerprint",
                terminal_artifact_contract_fingerprint(),
            ),
            (
                "terminal_artifact_render_target",
                describe_terminal_artifact_render_target_contract(),
                "terminal_artifact_render_target_contract_fingerprint",
                terminal_artifact_render_target_contract_fingerprint(),
            ),
            (
                "terminal_artifact_rendering",
                describe_terminal_artifact_rendering_contract(),
                "terminal_artifact_rendering_contract_fingerprint",
                terminal_artifact_rendering_contract_fingerprint(),
            ),
            (
                "terminal_artifact_cli_fallback",
                describe_terminal_artifact_cli_fallback_contract(),
                "terminal_artifact_cli_fallback_contract_fingerprint",
                terminal_artifact_cli_fallback_contract_fingerprint(),
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                describe_terminal_artifact_raw_leaf_card_default_contract(),
                "raw_leaf_card_default_contract_fingerprint",
                terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            ),
        ]

        for section_name, manifest, alias_key, expected_fingerprint in cases:
            with self.subTest(section=section_name):
                self.assertEqual(manifest["contract_fingerprint"], expected_fingerprint)
                self.assertEqual(manifest[alias_key], expected_fingerprint)

    def test_a2ui_contract_manifest_exposes_action_contract_alias(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["capabilities"], describe_a2ui_capabilities_contract())
        self.assertEqual(manifest["capabilities"]["contract_fingerprint"], manifest["capabilities_fingerprint"])
        self.assertEqual(manifest["capabilities_fingerprint"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(manifest["capabilities"]["capabilities_schema_version"], A2UI_CAPABILITIES_SCHEMA_VERSION)
        self.assertEqual(manifest["action"], describe_action_contract())
        self.assertEqual(manifest["action"]["contract_fingerprint"], manifest["action"]["action_fingerprint"])
        self.assertEqual(manifest["action_contract"], describe_action_contract())
        self.assertEqual(manifest["action_contract"]["contract_fingerprint"], manifest["action_contract_fingerprint"])
        self.assertEqual(manifest["action_contract_fingerprint"], action_contract_fingerprint())
        self.assertEqual(len(manifest["action"]["contract_fingerprint"]), 64)
        self.assertEqual(manifest["action_fingerprint"], action_contract_fingerprint())
        self.assertEqual(manifest["selection"], describe_selection_contract())
        self.assertEqual(manifest["selection"]["contract_fingerprint"], manifest["selection"]["selection_fingerprint"])
        self.assertEqual(manifest["selection_contract"], describe_selection_contract())
        self.assertEqual(
            manifest["selection_contract"]["contract_fingerprint"],
            manifest["selection_contract_fingerprint"],
        )
        self.assertEqual(manifest["selection_contract_fingerprint"], selection_contract_fingerprint())
        self.assertEqual(manifest["selection_fingerprint"], selection_contract_fingerprint())
        self.assertEqual(manifest["card_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["schemas"]["capabilities"], describe_a2ui_capabilities_contract())
        self.assertEqual(manifest["schemas"]["action"], describe_action_contract())
        self.assertEqual(manifest["contract_fingerprints"]["capabilities"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprints"]["selection"], selection_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprints"]["card_contract"], card_contract_fingerprint())
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact"],
            terminal_artifact_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_render_target"],
            manifest["terminal_artifact_render_target_fingerprint"],
        )
        self.assertEqual(manifest["terminal_artifact"], describe_terminal_artifact_contract())
        self.assertEqual(manifest["schemas"]["selection"], describe_selection_contract())
        self.assertEqual(manifest["schemas"]["terminal_artifact"], describe_terminal_artifact_contract())
        self.assertEqual(
            manifest["schemas"]["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["schemas"]["terminal_artifact_rendering"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["cli_fallback"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["cli_fallback_contract"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["schemas"]["terminal_artifact_cli_fallback"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["contract_fingerprint"],
            manifest["schemas"]["terminal_artifact"]["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact"]["rendering"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["render_target_contract"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(len(manifest["terminal_artifact_cli_fallback_fingerprint"]), 64)
        self.assertEqual(
            manifest["contract_fingerprints"],
            describe_a2ui_contract_fingerprints(
                include_action=True,
                include_terminal_artifact=True,
                include_terminal_artifact_render_target=True,
                include_terminal_artifact_rendering=True,
                include_terminal_artifact_cli_fallback=True,
            ),
        )
        self.assertEqual(len(manifest["terminal_artifact"]["contract_fingerprint"]), 64)

    def test_a2ui_contract_manifest_alias_sections_are_snapshot_isolated(self) -> None:
        manifest = describe_a2ui_contract()

        cases = [
            ("capabilities", manifest["schemas"]["capabilities"]),
            ("card_contract", manifest["schemas"]["card_contract"]),
            ("action", manifest["schemas"]["action"]),
            ("selection", manifest["schemas"]["selection"]),
            ("terminal_fallback", manifest["schemas"]["terminal_fallback"]),
            ("terminal_artifact", manifest["schemas"]["terminal_artifact"]),
            (
                "terminal_artifact_render_target",
                manifest["schemas"]["terminal_artifact_render_target"],
            ),
            (
                "terminal_artifact_rendering",
                manifest["schemas"]["terminal_artifact_rendering"],
            ),
            (
                "terminal_artifact_cli_fallback",
                manifest["schemas"]["terminal_artifact_cli_fallback"],
            ),
            (
                "terminal_artifact_raw_leaf_card_default",
                manifest["terminal_artifact"]["raw_leaf_card_default_contract"],
            ),
            (
                "terminal_artifact_kind_contracts",
                manifest["terminal_artifact"]["terminal_artifact_kind_contracts"],
            ),
            (
                "terminal_artifact_raw_leaf_card_default_contract_fingerprints",
                manifest["terminal_artifact"]["raw_leaf_card_default_contract_fingerprints"],
            ),
        ]

        for key, source in cases:
            with self.subTest(section=key):
                self.assertIsNot(manifest[key], source)
                self.assertEqual(manifest[key], source)

    def test_a2ui_contract_manifest_exposes_terminal_fallback_and_artifact_fingerprints(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["capabilities_fingerprint"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(manifest["terminal_fallback_fingerprint"], terminal_fallback_contract_fingerprint())
        self.assertEqual(manifest["terminal_fallback_contract"], manifest["terminal_fallback"])
        self.assertEqual(
            manifest["terminal_fallback_contract_fingerprint"],
            manifest["terminal_fallback_fingerprint"],
        )
        self.assertEqual(manifest["terminal_artifact_fingerprint"], terminal_artifact_contract_fingerprint())
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_fallback"]["contract_fingerprint"],
            manifest["terminal_fallback_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact"]["contract_fingerprint"],
            manifest["terminal_artifact_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact"]["cli_fallback"]["contract_fingerprint"],
            manifest["terminal_artifact_cli_fallback_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact"]["cli_fallback_contract"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_fallback_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_cli_fallback_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(manifest["terminal_artifact_contract"], describe_terminal_artifact_contract())
        self.assertEqual(
            manifest["terminal_artifact_contract_fingerprint"],
            terminal_artifact_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["capabilities"],
            a2ui_capabilities_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_render_target"],
            terminal_artifact_render_target_contract_fingerprint(),
        )

    def test_a2ui_contract_manifest_exposes_raw_leaf_card_default_aliases(self) -> None:
        manifest = describe_a2ui_contract()
        raw_leaf_contract = describe_terminal_artifact_raw_leaf_card_default_contract()

        self.assertEqual(manifest["terminal_artifact_raw_leaf_card_default"], raw_leaf_contract)
        self.assertEqual(manifest["terminal_artifact_raw_leaf_card_default_contract"], raw_leaf_contract)
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(manifest["terminal_artifact"]["raw_leaf_card_default_contract"], raw_leaf_contract)

    def test_a2ui_contract_fingerprint_map_matches_section_contracts(self) -> None:
        manifest = describe_a2ui_contract()
        fingerprints = describe_a2ui_contract_fingerprints()
        fingerprints_with_aliases = describe_a2ui_contract_fingerprints(include_contract_aliases=True)

        self.assertEqual(fingerprints["contract"], manifest["contract_fingerprint"])
        self.assertEqual(fingerprints["capabilities"], manifest["capabilities_fingerprint"])
        self.assertEqual(fingerprints["selection"], describe_selection_contract()["contract_fingerprint"])
        self.assertEqual(fingerprints["card_contract"], card_contract_fingerprint())
        self.assertEqual(fingerprints["terminal_fallback"], terminal_fallback_contract_fingerprint())
        self.assertEqual(fingerprints["capabilities"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(len(fingerprints["actions"]), 64)
        self.assertEqual(fingerprints_with_aliases["action_contract"], action_contract_fingerprint())
        self.assertEqual(fingerprints_with_aliases["selection_contract"], selection_contract_fingerprint())
        self.assertEqual(fingerprints_with_aliases["terminal_fallback_contract"], terminal_fallback_contract_fingerprint())
        self.assertEqual(fingerprints_with_aliases["terminal_artifact_contract"], terminal_artifact_contract_fingerprint())
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_contract"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertNotIn("action_contract", fingerprints)
        self.assertNotIn("selection_contract", fingerprints)

    def test_a2ui_contract_fingerprint_map_can_opt_into_terminal_artifact_dispatch(self) -> None:
        fingerprints = describe_a2ui_contract_fingerprints(include_terminal_artifact=True)

        self.assertEqual(fingerprints["terminal_artifact"], terminal_artifact_contract_fingerprint())
        self.assertEqual(len(fingerprints["terminal_artifact"]), 64)
        self.assertNotIn("terminal_artifact", describe_a2ui_contract_fingerprints())

    def test_a2ui_contract_fingerprint_map_can_opt_into_embedded_dispatch_contracts(self) -> None:
        fingerprints = describe_a2ui_contract_fingerprints(
            include_action=True,
            include_terminal_artifact=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_contract_aliases=True,
        )
        fingerprints_without_render_target = describe_a2ui_contract_fingerprints(
            include_action=True,
            include_terminal_artifact=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_contract_aliases=True,
        )
        manifest_fingerprints = describe_a2ui_contract_fingerprints(
            include_action=True,
            include_terminal_artifact=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
        )

        self.assertEqual(fingerprints["action"], action_contract_fingerprint())
        self.assertEqual(fingerprints["action_contract"], action_contract_fingerprint())
        self.assertEqual(fingerprints["selection_contract"], selection_contract_fingerprint())
        self.assertEqual(
            fingerprints["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_contract"],
            terminal_artifact_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_render_target"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_rendering"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(fingerprints["capabilities"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(
            describe_a2ui_contract()["contract_fingerprints"],
            manifest_fingerprints,
        )
        self.assertNotEqual(fingerprints, fingerprints_without_render_target)
        self.assertNotIn("action", describe_a2ui_contract_fingerprints())
        self.assertNotIn("action_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("selection_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_render_target", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_rendering", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_cli_fallback", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_fallback_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_kind_contracts", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_render_target_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_rendering_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_cli_fallback_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn(
            "terminal_artifact_raw_leaf_card_default_contract",
            describe_a2ui_contract_fingerprints(),
        )

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
            manifest["terminal_artifact_render_target_contract"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(
            manifest["terminal_fallback_contract"]["contract_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(manifest["terminal_fallback_fingerprint"], terminal_fallback_contract_fingerprint())
        self.assertEqual(
            manifest["render_target_contract"]["contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract"]["contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["cli_fallback"]["contract_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(manifest["cli_fallback_contract"], describe_terminal_artifact_cli_fallback_contract())
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["rendering"]["contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["rendering_contract"]["contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            describe_terminal_artifact_contract_fingerprints(include_terminal_artifact=True),
        )
        self.assertEqual(
            set(manifest["contract_fingerprints"]),
            {
                "terminal_artifact",
                "card_contract",
                "action_contract",
                "selection_contract",
                "render_target_contract",
                "terminal_fallback_contract",
                "rendering_contract",
                "cli_fallback_contract",
                "raw_leaf_card_default_contract",
            },
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact"],
            terminal_artifact_contract_fingerprint(),
        )
        self.assertEqual(manifest["contract_fingerprints"]["card_contract"], card_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprints"]["action_contract"], action_contract_fingerprint())
        self.assertEqual(
            manifest["contract_fingerprints"]["selection_contract"],
            selection_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["cli_fallback_contract"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(manifest["contract_fingerprint"], terminal_artifact_contract_fingerprint())
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)

    def test_terminal_artifact_kind_contract_helper_is_shared_and_fingerprintable(self) -> None:
        kind_contracts = describe_terminal_artifact_kind_contracts()
        manifest = describe_terminal_artifact_contract()
        fingerprints = describe_terminal_artifact_contract_fingerprints(include_kind_contracts=True)

        self.assertEqual(kind_contracts, manifest["kind_contracts"])
        self.assertEqual(set(kind_contracts), {"card", "action", "selection"})
        self.assertEqual(kind_contracts["card"]["kind"], "card")
        self.assertEqual(kind_contracts["action"]["kind"], "action")
        self.assertEqual(kind_contracts["selection"]["kind"], "selection")
        self.assertEqual(kind_contracts["card"]["contract_fingerprint"], card_contract_fingerprint())
        self.assertEqual(kind_contracts["action"]["contract_fingerprint"], action_contract_fingerprint())
        self.assertEqual(
            kind_contracts["selection"]["contract_fingerprint"],
            selection_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(len(fingerprints["kind_contracts"]), 64)
        self.assertEqual(
            fingerprints["render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact", describe_terminal_artifact_contract_fingerprints())
        self.assertNotIn("kind_contracts", describe_terminal_artifact_contract_fingerprints())

    def test_terminal_artifact_contract_fingerprint_map_can_opt_into_self_fingerprint(self) -> None:
        fingerprints = describe_terminal_artifact_contract_fingerprints(include_terminal_artifact=True)

        self.assertEqual(fingerprints["terminal_artifact"], terminal_artifact_contract_fingerprint())
        self.assertEqual(len(fingerprints["terminal_artifact"]), 64)
        self.assertNotIn("terminal_artifact", describe_terminal_artifact_contract_fingerprints())

    def test_terminal_artifact_contract_fingerprint_map_can_opt_into_alias_contracts(self) -> None:
        fingerprints = describe_terminal_artifact_contract_fingerprints(include_contract_aliases=True)

        self.assertEqual(
            fingerprints["terminal_artifact_kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(fingerprints["terminal_artifact_contract"], terminal_artifact_contract_fingerprint())
        self.assertEqual(
            fingerprints["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )

    def test_terminal_artifact_contract_manifest_surfaces_rendering_recovery_aliases(self) -> None:
        manifest = describe_terminal_artifact_contract()
        render_target_manifest = describe_terminal_artifact_render_target_contract()
        rendering_manifest = describe_terminal_artifact_rendering_contract()
        kind_contracts = describe_terminal_artifact_kind_contracts()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["render_target_contract"], render_target_manifest)
        self.assertEqual(rendering_manifest["render_target_contract"], render_target_manifest)
        self.assertEqual(manifest["kind_resolution"], rendering_manifest["kind_resolution"])
        self.assertEqual(
            manifest["kind_resolution"]["leaf_recovery"],
            rendering_manifest["kind_resolution"]["leaf_recovery"],
        )
        self.assertEqual(manifest["fallback_recovery"], rendering_manifest["fallback_recovery"])
        self.assertEqual(render_target_manifest["kind_resolution"], rendering_manifest["kind_resolution"])
        self.assertEqual(render_target_manifest["fallback_recovery"], rendering_manifest["fallback_recovery"])
        self.assertEqual(manifest["kind_contracts"], kind_contracts)
        self.assertEqual(manifest["terminal_artifact_kind_contracts"], kind_contracts)
        self.assertEqual(
            manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_fallback_contract_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(render_target_manifest["terminal_artifact_kind_contracts"], kind_contracts)
        self.assertEqual(
            render_target_manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(rendering_manifest["terminal_artifact_kind_contracts"], kind_contracts)
        self.assertEqual(
            rendering_manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["kind_resolution"],
            rendering_manifest["kind_resolution"],
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["fallback_recovery"],
            rendering_manifest["fallback_recovery"],
        )
        self.assertEqual(a2ui_manifest["terminal_artifact_kind_contracts"], kind_contracts)
        self.assertEqual(
            a2ui_manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["render_target_contract"],
            render_target_manifest,
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_kind_contracts"],
            kind_contracts,
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_render_target"],
            render_target_manifest,
        )
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact"]["kind_resolution"],
            rendering_manifest["kind_resolution"],
        )
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact"]["fallback_recovery"],
            rendering_manifest["fallback_recovery"],
        )
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact"]["terminal_artifact_kind_contracts"],
            kind_contracts,
        )
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact_render_target"],
            render_target_manifest,
        )

    def test_terminal_artifact_contract_version_alias_matches_schema_version(self) -> None:
        manifest = describe_terminal_artifact_contract()

        self.assertEqual(manifest["terminal_artifact_version"], manifest["terminal_artifact_schema_version"])
        self.assertEqual(manifest["terminal_artifact_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)

    def test_terminal_artifact_raw_leaf_card_default_contract_manifest_is_versioned_and_embedded_in_terminal_artifact_contracts(
        self,
    ) -> None:
        manifest = describe_terminal_artifact_raw_leaf_card_default_contract()
        terminal_artifact_manifest = describe_terminal_artifact_contract()
        render_target_manifest = describe_terminal_artifact_render_target_contract()
        rendering_manifest = describe_terminal_artifact_rendering_contract()
        cli_manifest = describe_terminal_artifact_cli_fallback_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_schema_version"],
            TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_version"],
            TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
        )
        self.assertEqual(manifest["type"], "TerminalArtifactRawLeafCardDefaultContract")
        self.assertEqual(manifest["default_kind"], "card")
        self.assertTrue(manifest["preserve_when_kind_is_unset"])
        self.assertEqual(manifest["required_fields"], ["id", "label", "payload"])
        self.assertEqual(
            manifest["excluded_fields"],
            ["type", "blocks", "actions", "confirm", "policy_sensitive", "selected", "disabled"],
        )
        self.assertEqual(
            manifest["contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        )
        self.assertEqual(
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default=True,
            ),
            {
                "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
                "terminal_artifact_raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            },
        )
        self.assertEqual(
            manifest,
            {
                **_RAW_LEAF_CARD_DEFAULT_CONTRACT_MANIFEST,
                "contract_fingerprint": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
                "raw_leaf_card_default_fingerprint": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            },
        )
        self.assertEqual(terminal_artifact_manifest["raw_leaf_card_default_contract"], manifest)
        self.assertEqual(
            terminal_artifact_manifest["terminal_artifact_raw_leaf_card_default_contract"],
            manifest,
        )
        self.assertEqual(terminal_artifact_manifest["raw_leaf_card_default_contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(
            terminal_artifact_manifest["raw_leaf_card_default_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        )
        self.assertEqual(render_target_manifest["raw_leaf_card_default_contract"], manifest)
        self.assertEqual(
            render_target_manifest["terminal_artifact_raw_leaf_card_default_contract"],
            manifest,
        )
        self.assertEqual(render_target_manifest["raw_leaf_card_default_contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(
            render_target_manifest["raw_leaf_card_default_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        )
        self.assertEqual(rendering_manifest["raw_leaf_card_default_contract"], manifest)
        self.assertEqual(
            rendering_manifest["terminal_artifact_raw_leaf_card_default_contract"],
            manifest,
        )
        self.assertEqual(rendering_manifest["raw_leaf_card_default_contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(
            rendering_manifest["raw_leaf_card_default_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        )
        self.assertEqual(cli_manifest["raw_leaf_card_default_contract"], manifest)
        self.assertEqual(
            cli_manifest["terminal_artifact_raw_leaf_card_default_contract"],
            manifest,
        )
        self.assertEqual(cli_manifest["raw_leaf_card_default_contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(
            cli_manifest["raw_leaf_card_default_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        )
        self.assertEqual(a2ui_manifest["terminal_artifact"]["raw_leaf_card_default_contract"], manifest)
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_raw_leaf_card_default_contract"],
            manifest,
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["raw_leaf_card_default_contract_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["raw_leaf_card_default_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints(),
        )

    def test_terminal_artifact_rendering_contract_manifest_is_versioned_and_embedded_in_a2ui_contract(self) -> None:
        manifest = describe_terminal_artifact_rendering_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["type"], "TerminalArtifactRenderingContract")
        self.assertEqual(manifest["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(manifest["default_kind"], "card")
        self.assertEqual(manifest["envelope"], describe_terminal_artifact_contract()["envelope"])
        self.assertEqual(manifest["kind_contracts"], describe_terminal_artifact_contract()["kind_contracts"])
        self.assertEqual(manifest["envelope"]["type"], "TerminalArtifact")
        self.assertEqual(manifest["envelope"]["required_fields"], ["kind", "artifact"])
        self.assertEqual(manifest["envelope"]["optional_fields"], ["contract_version", "a2ui_version"])
        self.assertEqual(manifest["envelope"]["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(
            manifest["kind_contracts"]["card"],
            {"kind": "card", "contract_fingerprint": card_contract_fingerprint()},
        )
        self.assertEqual(
            manifest["kind_contracts"]["action"],
            {"kind": "action", "contract_fingerprint": action_contract_fingerprint()},
        )
        self.assertEqual(
            manifest["kind_contracts"]["selection"],
            {"kind": "selection", "contract_fingerprint": selection_contract_fingerprint()},
        )
        self.assertEqual(
            manifest["render_target_contract"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints"],
            {
                "terminal_artifact": "render_terminal_artifact",
                "cli_fallback": "render_terminal_cli_fallback",
                "card": "render_terminal_card",
                "action": "render_terminal_action",
                "selection": "render_terminal_selection",
            },
        )
        self.assertEqual(manifest["render_target_resolver"], "resolve_terminal_artifact_render_target")
        self.assertEqual(manifest["fallback_renderer"], "ShellUI.render_artifact")
        self.assertEqual(manifest["raw_leaf_card_default"], _RAW_LEAF_CARD_DEFAULT_MANIFEST)
        self.assertEqual(
            manifest["raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["kind_resolution"]["precedence"],
            [
                "validated envelope kind",
                "typed payload kind",
                "explicit caller kind hint",
                "partial leaf hint recovery",
                "schema-valid leaf payload recovery",
                "card default",
            ],
        )
        self.assertTrue(manifest["kind_resolution"]["card_payloads_override_conflicting_action_or_selection_hints"])
        self.assertEqual(
            manifest["kind_resolution"]["partial_leaf_recovery"],
            {
                "required_fields": ["id", "payload"],
                "action_hints": ["confirm", "policy_sensitive"],
                "selection_hints": ["selected", "disabled"],
            },
        )
        self.assertEqual(
            manifest["kind_resolution"]["leaf_recovery"],
            {
                "malformed_card_envelopes": {
                    "action": "normalize_action_ref",
                    "selection": "normalize_selection_ref",
                }
            },
        )
        self.assertEqual(
            manifest["fallback_recovery"],
            {
                "malformed_card_envelopes": {
                    "action": "normalize_action_ref",
                    "selection": "normalize_selection_ref",
                }
            },
        )
        self.assertEqual(manifest["terminal_fallback_contract"], describe_terminal_fallback_contract())
        self.assertEqual(manifest["render_target_contract"], describe_terminal_artifact_render_target_contract())
        self.assertEqual(
            manifest["terminal_fallback_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_schema_version"],
            TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_version"],
            TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(manifest["terminal_artifact_kind_contracts"], describe_terminal_artifact_kind_contracts())
        self.assertEqual(
            manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            describe_terminal_artifact_rendering_contract_fingerprints(),
        )
        self.assertEqual(manifest["contract_fingerprint"], terminal_artifact_rendering_contract_fingerprint())
        self.assertEqual(a2ui_manifest["terminal_artifact_rendering"], manifest)
        self.assertEqual(a2ui_manifest["terminal_artifact_render_target"], describe_terminal_artifact_render_target_contract())
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_rendering_contract"],
            manifest,
        )
        self.assertEqual(a2ui_manifest["schemas"]["terminal_artifact_rendering"], manifest)
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(a2ui_manifest["terminal_artifact"]["rendering"], manifest)

    def test_terminal_artifact_rendering_contract_fingerprints_are_public_and_canonical(self) -> None:
        manifest = describe_terminal_artifact_rendering_contract()
        fingerprints = describe_terminal_artifact_rendering_contract_fingerprints()
        fingerprints_with_self = describe_terminal_artifact_rendering_contract_fingerprints(
            include_terminal_artifact_rendering=True,
            include_contract_aliases=True,
        )

        self.assertEqual(fingerprints, manifest["contract_fingerprints"])
        self.assertEqual(
            fingerprints["kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints["render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact_rendering", fingerprints)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self,
            {
                **fingerprints,
                "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
                "terminal_artifact_rendering": terminal_artifact_rendering_contract_fingerprint(),
                "terminal_artifact_render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
                "terminal_artifact_rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
                "terminal_artifact_raw_leaf_card_default_contract": (
                    terminal_artifact_raw_leaf_card_default_contract_fingerprint()
                ),
            },
        )
        for fingerprint in fingerprints.values():
            self.assertEqual(len(fingerprint), 64)
        self.assertEqual(len(fingerprints_with_self["terminal_artifact_rendering"]), 64)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )

    def test_terminal_artifact_cli_fallback_contract_manifest_is_versioned_and_embedded_in_a2ui_contract(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_schema_version"], 1)
        self.assertEqual(manifest["type"], "TerminalArtifactCliFallbackContract")
        self.assertEqual(manifest["fallback_renderer"], "ShellUI.render_artifact")
        self.assertEqual(manifest["raw_leaf_card_default"], _RAW_LEAF_CARD_DEFAULT_MANIFEST)
        self.assertEqual(
            manifest["raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(manifest["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(manifest["default_kind"], "card")
        self.assertEqual(manifest["envelope"]["type"], "TerminalArtifact")
        self.assertEqual(manifest["envelope"]["contract_version"], 2)
        self.assertEqual(manifest["envelope"]["a2ui_version"], 1)
        self.assertEqual(
            manifest["envelope"]["terminal_artifact_schema_version"],
            TERMINAL_ARTIFACT_SCHEMA_VERSION,
        )
        self.assertEqual(manifest["envelope"]["required_fields"], ["kind", "artifact"])
        self.assertEqual(manifest["envelope"]["optional_fields"], ["contract_version", "a2ui_version"])
        self.assertEqual(manifest["envelope"]["kind_field"], "kind")
        self.assertEqual(manifest["envelope"]["artifact_field"], "artifact")
        self.assertEqual(manifest["envelope"]["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(
            manifest["kind_contracts"]["card"],
            {"kind": "card", "contract_fingerprint": card_contract_fingerprint()},
        )
        self.assertEqual(
            manifest["kind_contracts"]["action"],
            {"kind": "action", "contract_fingerprint": action_contract_fingerprint()},
        )
        self.assertEqual(
            manifest["kind_contracts"]["selection"],
            {"kind": "selection", "contract_fingerprint": selection_contract_fingerprint()},
        )
        self.assertEqual(manifest["terminal_artifact_kind_contracts"], describe_terminal_artifact_kind_contracts())
        self.assertEqual(
            manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints"],
            {
                "terminal_artifact": "render_terminal_artifact",
                "cli_fallback": "render_terminal_cli_fallback",
                "card": "render_terminal_card",
                "action": "render_terminal_action",
                "selection": "render_terminal_selection",
            },
        )
        self.assertEqual(manifest["render_target_resolver"], "resolve_terminal_artifact_render_target")
        self.assertEqual(manifest["raw_leaf_card_default"], _RAW_LEAF_CARD_DEFAULT_MANIFEST)
        self.assertEqual(
            manifest["kind_policy"],
            {
                "card": "defer to terminal artifact dispatch and keep card as the default recovery path",
                "action": "recover action payloads with render_terminal_action",
                "selection": "recover selection payloads with render_terminal_selection",
            },
        )
        self.assertEqual(manifest["render_target_contract"], describe_terminal_artifact_render_target_contract())
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(manifest["rendering"], describe_terminal_artifact_rendering_contract())
        self.assertEqual(
            manifest["terminal_artifact_rendering"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_fallback_contract_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            {
                "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
                "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
                "rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
                "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
                "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            },
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(manifest["kind_resolution"], manifest["render_target_contract"]["kind_resolution"])
        self.assertEqual(manifest["fallback_recovery"], manifest["render_target_contract"]["fallback_recovery"])
        self.assertEqual(manifest["terminal_fallback_contract"], describe_terminal_fallback_contract())
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(manifest["terminal_artifact_rendering_contract"], manifest["rendering"])
        self.assertEqual(
            manifest["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(manifest["contract_fingerprint"], terminal_artifact_cli_fallback_contract_fingerprint())
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(a2ui_manifest["terminal_artifact"]["cli_fallback"], manifest)
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_rendering"],
            manifest["terminal_artifact_rendering"],
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_cli_fallback"],
            a2ui_manifest["terminal_artifact_cli_fallback"],
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_cli_fallback_contract"],
            manifest,
        )
        self.assertEqual(a2ui_manifest["terminal_artifact_cli_fallback"], manifest)
        self.assertEqual(a2ui_manifest["terminal_artifact_render_target"], describe_terminal_artifact_render_target_contract())
        self.assertEqual(a2ui_manifest["terminal_artifact_cli_fallback_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(
            a2ui_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(a2ui_manifest["schemas"]["terminal_artifact_cli_fallback"], manifest)

    def test_terminal_artifact_cli_fallback_entrypoint_matches_generic_renderer(self) -> None:
        envelope = build_terminal_artifact_envelope(
            ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
            ),
            kind="action",
        )

        self.assertEqual(render_terminal_cli_fallback(envelope), render_terminal_artifact(envelope))

    def test_terminal_artifact_cli_fallback_entrypoint_ignores_invalid_kind_hints(self) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        action_envelope = build_terminal_artifact_envelope(
            ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
            ),
            kind="action",
        )

        self.assertEqual(
            render_terminal_cli_fallback(raw_leaf, kind="dialog"),
            render_terminal_cli_fallback(raw_leaf),
        )
        self.assertEqual(
            render_terminal_cli_fallback(action_envelope, kind="dialog"),
            render_terminal_cli_fallback(action_envelope),
        )

    def test_terminal_artifact_cli_fallback_entrypoint_preserves_invalid_card_hints_for_malformed_envelopes(
        self,
    ) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": {
                "type": "ActionRef",
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
        }

        text = render_terminal_cli_fallback(envelope, kind="card")

        self.assertIn("[UnknownCard] <invalid card>", text)
        self.assertIn("Fallback: unknown card", text)
        self.assertNotIn("[ActionRef]", text)
        self.assertNotIn("[SelectionRef]", text)

    def test_terminal_artifact_cli_fallback_target_resolver_preserves_raw_leaf_card_default(self) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        self.assertEqual(resolve_terminal_artifact_cli_fallback_target(raw_leaf), (raw_leaf, "card"))
        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(raw_leaf, kind="dialog"),
            (raw_leaf, "card"),
        )

    def test_terminal_artifact_renderers_preserve_raw_leaf_card_default_without_shared_resolver(self) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch(
            "src.qual.ui.a2ui.resolve_terminal_artifact_render_target",
            side_effect=AssertionError("resolver should not be used"),
        ):
            rendered_text = render_terminal_artifact(raw_leaf)
            cli_fallback_text = render_terminal_cli_fallback(raw_leaf)

        self.assertEqual(rendered_text, cli_fallback_text)
        self.assertIn("[<missing>] <untitled>", rendered_text)
        self.assertNotIn("[ActionRef]", rendered_text)
        self.assertNotIn("[SelectionRef]", rendered_text)

    def test_terminal_artifact_cli_fallback_entrypoint_survives_generic_renderer_failure(self) -> None:
        envelope = build_terminal_artifact_envelope(
            ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
            ),
            kind="action",
        )

        with patch("src.qual.ui.a2ui.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = render_terminal_cli_fallback(envelope)

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_terminal_artifact_cli_fallback_contract_fingerprints_are_public_and_canonical(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_contract()
        fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints()
        fingerprints_with_self = describe_terminal_artifact_cli_fallback_contract_fingerprints(
            include_terminal_artifact_cli_fallback=True,
            include_contract_aliases=True,
        )

        self.assertEqual(fingerprints, manifest["contract_fingerprints"])
        self.assertEqual(
            fingerprints["kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints["render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact_cli_fallback", fingerprints)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self,
            {
                **fingerprints,
                "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
                "terminal_artifact_cli_fallback": terminal_artifact_cli_fallback_contract_fingerprint(),
                "terminal_artifact_render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
                "terminal_artifact_rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
                "terminal_artifact_cli_fallback_contract": terminal_artifact_cli_fallback_contract_fingerprint(),
                "terminal_artifact_raw_leaf_card_default_contract": (
                    terminal_artifact_raw_leaf_card_default_contract_fingerprint()
                ),
            },
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        for fingerprint in fingerprints.values():
            self.assertEqual(len(fingerprint), 64)
        self.assertEqual(len(fingerprints_with_self["terminal_artifact_cli_fallback"]), 64)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_contract"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )

    def test_raw_leaf_card_default_helper_only_preserves_untyped_leaf_payloads(self) -> None:
        self.assertTrue(
            _should_preserve_raw_leaf_card_default(
                {"id": "export_document", "label": "Export", "payload": {"format": "md"}}
            )
        )
        self.assertFalse(
            _should_preserve_raw_leaf_card_default(
                ActionRef(id="export_document", label="Export", payload={"format": "md"})
            )
        )
        self.assertFalse(
            _should_preserve_raw_leaf_card_default(
                SelectionRef(id="choice-1", label="Choice", payload={"nested": {"items": [1, 2]}})
            )
        )
        self.assertFalse(
            _should_preserve_raw_leaf_card_default(
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                }
            )
        )
        self.assertFalse(
            _should_preserve_raw_leaf_card_default(
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "policy_sensitive": True,
                }
            )
        )

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
        self.assertEqual(manifest["raw_leaf_card_default"], _RAW_LEAF_CARD_DEFAULT_MANIFEST)

    def test_terminal_artifact_render_target_contract_manifest_is_versioned_and_embedded_in_a2ui_contract(self) -> None:
        manifest = describe_terminal_artifact_render_target_contract()
        rendering_manifest = describe_terminal_artifact_rendering_contract()
        cli_manifest = describe_terminal_artifact_cli_fallback_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(
            manifest["terminal_artifact_render_target_schema_version"],
            TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_version"],
            TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
        )
        self.assertEqual(manifest["type"], "TerminalArtifactRenderTargetContract")
        self.assertEqual(manifest["render_target_resolver"], "resolve_terminal_artifact_render_target")
        self.assertEqual(manifest["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(manifest["default_kind"], "card")
        self.assertEqual(manifest["raw_leaf_card_default"], _RAW_LEAF_CARD_DEFAULT_MANIFEST)
        self.assertEqual(
            manifest["raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(manifest["envelope"], describe_terminal_artifact_contract()["envelope"])
        self.assertEqual(manifest["kind_contracts"], describe_terminal_artifact_kind_contracts())
        self.assertEqual(manifest["kind_resolution"], rendering_manifest["kind_resolution"])
        self.assertEqual(manifest["fallback_recovery"], rendering_manifest["fallback_recovery"])
        self.assertEqual(
            manifest["contract_fingerprints"],
            {
                "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
                "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
            },
        )
        self.assertEqual(manifest["terminal_artifact_kind_contracts"], describe_terminal_artifact_kind_contracts())
        self.assertEqual(
            manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(manifest["contract_fingerprint"], terminal_artifact_render_target_contract_fingerprint())
        self.assertEqual(rendering_manifest["render_target_contract"], manifest)
        self.assertEqual(rendering_manifest["terminal_artifact_render_target_contract"], manifest)
        self.assertEqual(cli_manifest["render_target_contract"], manifest)
        self.assertEqual(cli_manifest["terminal_artifact_render_target_contract"], manifest)
        self.assertEqual(a2ui_manifest["terminal_artifact_render_target"], manifest)
        self.assertEqual(a2ui_manifest["terminal_artifact"]["render_target_contract"], manifest)
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_render_target_contract"],
            manifest,
        )
        self.assertEqual(a2ui_manifest["schemas"]["terminal_artifact_render_target"], manifest)

    def test_terminal_artifact_render_target_contract_fingerprints_are_public_and_canonical(self) -> None:
        manifest = describe_terminal_artifact_render_target_contract()
        fingerprints = describe_terminal_artifact_render_target_contract_fingerprints()
        fingerprints_with_self = describe_terminal_artifact_render_target_contract_fingerprints(
            include_terminal_artifact_render_target=True,
            include_contract_aliases=True,
        )

        self.assertEqual(fingerprints, manifest["contract_fingerprints"])
        self.assertEqual(
            fingerprints["kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(len(fingerprints["kind_contracts"]), 64)
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact_render_target", fingerprints)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self,
            {
                **fingerprints,
                "terminal_artifact_kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
                "terminal_artifact_render_target": terminal_artifact_render_target_contract_fingerprint(),
                "terminal_artifact_render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
                "terminal_artifact_raw_leaf_card_default_contract": (
                    terminal_artifact_raw_leaf_card_default_contract_fingerprint()
                ),
            },
        )
        self.assertEqual(len(fingerprints_with_self["terminal_artifact_render_target"]), 64)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )

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
        self.assertEqual(
            envelope["artifact"],
            normalize_terminal_artifact_payload(action, kind="action"),
        )
        validate_terminal_artifact_envelope(envelope)

        text = render_terminal_artifact(envelope)

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertIn("- confirm: {\"message\":\"Export now?\",\"title\":\"Approve\"}", text)

    def test_terminal_artifact_envelope_builder_accepts_typed_leaf_mappings(self) -> None:
        action = {
            "type": "ActionRef",
            "id": " export_document ",
            "label": " Export ",
            "payload": {"format": "md"},
            "confirm": {"title": " Approve ", "message": " Export now? "},
            "policy_sensitive": True,
        }
        selection = {
            "type": "SelectionRef",
            "id": " choice-1 ",
            "label": " Choice ",
            "payload": {"nested": {"items": [1, 2]}},
            "selected": True,
        }

        action_envelope = build_terminal_artifact_envelope(action, kind="action")
        selection_envelope = build_terminal_artifact_envelope(selection, kind="selection")

        self.assertEqual(action_envelope["artifact"], normalize_terminal_artifact_payload(action, kind="action"))
        self.assertEqual(
            selection_envelope["artifact"],
            normalize_terminal_artifact_payload(selection, kind="selection"),
        )
        self.assertNotIn("type", action_envelope["artifact"])
        self.assertNotIn("type", selection_envelope["artifact"])
        validate_terminal_artifact_envelope(action_envelope)
        validate_terminal_artifact_envelope(selection_envelope)

        action_text = render_terminal_artifact(action_envelope)
        selection_text = render_terminal_artifact(selection_envelope)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)

    def test_terminal_artifact_payload_normalizer_returns_plain_dict_snapshots(self) -> None:
        action_payload = normalize_terminal_artifact_payload(
            ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
                confirm={"title": " Approve ", "message": " Export now? "},
                policy_sensitive=True,
            ),
            kind="action",
        )
        selection_payload = normalize_terminal_artifact_payload(
            SelectionRef(
                id=" choice-1 ",
                label=" Choice ",
                payload={"nested": {"items": [1, 2]}},
                selected=True,
            ),
            kind="selection",
        )
        card_payload = normalize_terminal_artifact_payload(
            {
                "type": "GenericCard",
                "title": " Run Log ",
                "a2ui_version": 1,
                "blocks": [{"type": "MarkdownBlock", "markdown": "Original"}],
                "actions": [],
                "trace_id": "drop-me",
            },
            kind="card",
        )

        self.assertEqual(
            action_payload,
            {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
                "confirm": {"title": "Approve", "message": "Export now?"},
                "policy_sensitive": True,
            },
        )
        self.assertEqual(
            selection_payload,
            {
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
                "selected": True,
            },
        )
        self.assertEqual(
            card_payload,
            {
                "type": "GenericCard",
                "title": " Run Log ",
                "a2ui_version": 1,
                "blocks": [{"type": "MarkdownBlock", "markdown": "Original"}],
                "actions": [],
            },
        )

    def test_terminal_artifact_payload_normalizer_canonicalizes_unordered_set_like_values(self) -> None:
        tag_view = {"beta": 1, "alpha": 2}.keys()
        selection = SelectionRef(
            id=" choice-1 ",
            label=" Choice ",
            payload={"tags": tag_view},
            selected=True,
        )
        card_source = {
            "type": "GenericCard",
            "title": " Run Log ",
            "a2ui_version": 1,
            "blocks": [{"type": "MarkdownBlock", "markdown": "Original"}],
            "actions": [],
            "debug": {"tags": tag_view},
        }

        selection_payload = normalize_terminal_artifact_payload(selection, kind="selection")
        card_payload = normalize_terminal_artifact_payload(card_source, kind="card")
        envelope = build_terminal_artifact_envelope(card_source, kind="card")
        preview = _render_payload_preview(card_source, max_payload_bytes=1_000)

        self.assertEqual(selection_payload["payload"]["tags"], ["alpha", "beta"])
        self.assertEqual(card_payload["debug"]["tags"], ["alpha", "beta"])
        self.assertEqual(envelope["artifact"]["debug"]["tags"], ["alpha", "beta"])
        self.assertIs(card_source["debug"]["tags"], tag_view)
        self.assertEqual(
            json.loads(json.dumps(envelope["artifact"]))["debug"]["tags"],
            ["alpha", "beta"],
        )
        self.assertIn('"tags":["alpha","beta"]', preview)
        self.assertNotIn("<non-json:dict_keys>", preview)

    def test_terminal_artifact_payload_normalizer_canonicalizes_mapping_key_order(self) -> None:
        action = ActionRef(
            id=" copy_to_clipboard ",
            label=" Copy JSON ",
            payload={"text": "copy me"},
        )
        selection = SelectionRef(
            id=" choice-1 ",
            label=" Choice ",
            payload={"b": 2, "a": {"z": 9, "y": 8}},
        )
        card_source = {
            "type": "GenericCard",
            "title": " Run Log ",
            "a2ui_version": 1,
            "blocks": [],
            "actions": [],
            "debug": {"b": 2, "a": {"z": 9, "y": 8}},
        }

        action_payload = normalize_terminal_artifact_payload(action, kind="action")
        selection_payload = normalize_terminal_artifact_payload(selection, kind="selection")
        card_payload = normalize_terminal_artifact_payload(card_source, kind="card")
        envelope = build_terminal_artifact_envelope(card_source, kind="card")

        self.assertEqual(list(action_payload["payload"].keys()), ["text"])
        self.assertEqual(action_payload["payload"], {"text": "copy me"})
        self.assertEqual(list(selection_payload["payload"].keys()), ["a", "b"])
        self.assertEqual(list(selection_payload["payload"]["a"].keys()), ["y", "z"])
        self.assertEqual(list(card_payload["debug"].keys()), ["a", "b"])
        self.assertEqual(list(card_payload["debug"]["a"].keys()), ["y", "z"])
        self.assertEqual(list(envelope["artifact"]["debug"].keys()), ["a", "b"])
        self.assertEqual(list(envelope["artifact"]["debug"]["a"].keys()), ["y", "z"])

    def test_terminal_artifact_payload_normalizer_rejects_action_or_selection_payloads_when_card_kind_is_explicit(self) -> None:
        with self.assertRaises(ValueError):
            normalize_terminal_artifact_payload(
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
                kind="card",
            )

        with self.assertRaises(ValueError):
            normalize_terminal_artifact_payload(
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
                kind="card",
            )

    def test_terminal_artifact_envelope_snapshots_source_payloads(self) -> None:
        card = {
            "type": "GenericCard",
            "title": " Run Log ",
            "a2ui_version": 1,
            "blocks": [{"type": "MarkdownBlock", "markdown": "Original"}],
            "actions": [],
            "trace_id": "drop-me",
        }

        envelope = build_terminal_artifact_envelope(card, kind="card")
        card["title"] = "Changed"
        card["blocks"][0]["markdown"] = "Mutated"

        self.assertNotIn("trace_id", envelope["artifact"])
        text = render_terminal_artifact(envelope)

        self.assertIn("[GenericCard] Run Log", text)
        self.assertIn("Original", text)
        self.assertNotIn("Changed", text)
        self.assertNotIn("Mutated", text)

    def test_terminal_artifact_card_snapshots_nested_action_refs_into_plain_dicts(self) -> None:
        action = ActionRef(
            id="copy_to_clipboard",
            label="Copy JSON",
            payload={"text": "{}"},
        )
        card = {
            "type": "GenericCard",
            "title": " Run Log ",
            "a2ui_version": 1,
            "blocks": [{"type": "MarkdownBlock", "markdown": "Original"}],
            "actions": [action],
        }

        normalized_card = normalize_terminal_artifact_payload(card, kind="card")
        envelope = build_terminal_artifact_envelope(card, kind="card")
        action.payload["text"] = '{"changed": true}'

        self.assertEqual(
            normalized_card["actions"],
            [{"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": "{}"}}],
        )
        self.assertIsInstance(normalized_card["actions"][0], dict)
        self.assertEqual(
            envelope["artifact"]["actions"],
            [{"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": "{}"}}],
        )
        self.assertIsInstance(envelope["artifact"]["actions"][0], dict)
        self.assertNotIn("changed", envelope["artifact"]["actions"][0]["payload"]["text"])
        self.assertIn("- Copy JSON (copy_to_clipboard)", render_terminal_artifact(envelope))

    def test_terminal_artifact_envelope_snapshots_cyclic_dataclass_payloads(self) -> None:
        debug: dict[str, object] = {}
        card = _StructuredCard(
            type="GenericCard",
            title=" Run Log ",
            a2ui_version=1,
            blocks=[{"type": "MarkdownBlock", "markdown": "Original"}],
            actions=[],
            debug=debug,
        )
        debug["self"] = debug

        envelope = build_terminal_artifact_envelope(card, kind="card")
        rendered = render_terminal_artifact(envelope)
        serialized = json.dumps(envelope, sort_keys=True)
        round_tripped = json.loads(serialized)

        self.assertEqual(envelope["artifact"]["debug"]["self"], "<cycle:dict>")
        self.assertEqual(round_tripped["artifact"]["debug"]["self"], "<cycle:dict>")
        self.assertIn("<cycle:dict>", rendered)
        self.assertIn("[GenericCard] Run Log", rendered)

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

    def test_terminal_artifact_renderer_recovers_from_malformed_envelopes(self) -> None:
        action_text = render_terminal_artifact(
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

        selection_text = render_terminal_artifact(
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

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("contract_version", selection_text)

    def test_terminal_artifact_recovers_valid_payload_from_malformed_envelope_kind(self) -> None:
        text = render_terminal_artifact(
            {
                "type": "TerminalArtifact",
                "kind": "dialog",
                "artifact": {
                    "type": "SelectionRef",
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
            }
        )

        self.assertIn("[SelectionRef] Choice", text)
        self.assertIn("Selection schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_terminal_artifact_recovers_card_payloads_from_malformed_envelopes_even_with_conflicting_hints(
        self,
    ) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "type": "GenericCard",
                "title": " Run Log ",
                "a2ui_version": 1,
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [],
            },
            "trace_id": "drop-me",
        }

        for requested_kind in (None, "card", "action", "selection"):
            with self.subTest(requested_kind=requested_kind):
                if requested_kind is None:
                    text = render_terminal_artifact(envelope)
                else:
                    text = render_terminal_artifact(envelope, kind=requested_kind)

                self.assertIn("[GenericCard] Run Log", text)
                self.assertIn("A2UI v1", text)
                self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
                self.assertNotIn("trace_id", text)

    def test_terminal_artifact_render_target_resolver_matches_shell_fallback_for_malformed_envelopes(self) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
                "selected": True,
            },
        }

        resolved_artifact, resolved_kind = resolve_terminal_artifact_render_target(
            envelope,
            requested_kind=None,
        )

        shell = ShellUI()
        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            fallback_artifact, fallback_kind = shell._resolve_fallback_artifact(envelope, kind="dialog")

        self.assertEqual(resolved_kind, "selection")
        self.assertEqual(
            resolved_artifact,
            {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
                "selected": True,
            },
        )
        self.assertEqual(fallback_kind, resolved_kind)
        self.assertEqual(fallback_artifact, resolved_artifact)

    def test_terminal_artifact_recovers_schema_valid_leaf_payloads_from_malformed_card_envelopes(self) -> None:
        action_envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
            "trace_id": "drop-me",
        }
        selection_envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": {
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
            },
            "trace_id": "drop-me",
        }

        action_text = render_terminal_artifact(action_envelope)
        selection_text = render_terminal_artifact(selection_envelope)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("trace_id", selection_text)

    def test_terminal_artifact_render_target_resolver_recovers_partial_leaf_payloads_in_fallback_mode(
        self,
    ) -> None:
        shell = ShellUI()
        partial_action = {
            "id": "export_document",
            "payload": {"format": "md"},
            "confirm": {"title": "Approve", "message": "Proceed?"},
        }
        partial_selection = {
            "id": "choice-1",
            "payload": {"nested": {"items": [1, 2]}},
            "selected": True,
        }

        for artifact, expected_kind in ((partial_action, "action"), (partial_selection, "selection")):
            resolved_artifact, resolved_kind = resolve_terminal_artifact_render_target(
                artifact,
                requested_kind=None,
                allow_invalid_envelope_recovery=True,
            )
            with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
                fallback_artifact, fallback_kind = shell._resolve_fallback_artifact(artifact, kind=None)

            self.assertEqual(resolved_kind, expected_kind)
            self.assertEqual(resolved_artifact, artifact)
            self.assertEqual(fallback_artifact, resolved_artifact)
            self.assertEqual(fallback_kind, resolved_kind)

    def test_terminal_artifact_renderer_recovers_partial_leaf_payloads_with_hints_without_fallback_failure(
        self,
    ) -> None:
        shell = ShellUI()
        partial_action = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
            "confirm": {"title": "Approve", "message": "Proceed?"},
        }
        partial_selection = {
            "id": "choice-1",
            "label": "Choice",
            "payload": {"nested": {"items": [1, 2]}},
            "selected": True,
        }

        action_text = render_terminal_artifact(partial_action)
        selection_text = render_terminal_artifact(partial_selection)
        shell_action_text = shell.render_artifact(partial_action)
        shell_selection_text = shell.render_artifact(partial_selection)

        for text in (action_text, shell_action_text):
            self.assertIn("[ActionRef] Export", text)
            self.assertIn("Action schema v1", text)
            self.assertNotIn("[<missing>] <untitled>", text)

        for text in (selection_text, shell_selection_text):
            self.assertIn("[SelectionRef] Choice", text)
            self.assertIn("Selection schema v1", text)
            self.assertNotIn("[<missing>] <untitled>", text)

    def test_terminal_artifact_renderer_keeps_valid_card_envelopes_authoritative_over_partial_leaf_hints(
        self,
    ) -> None:
        shell = ShellUI()
        envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": {
                "type": "GenericCard",
                "title": " Run Log ",
                "a2ui_version": 1,
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [],
                "confirm": {"title": "Approve", "message": "Proceed?"},
            },
        }

        text = render_terminal_artifact(envelope)
        shell_text = shell.render_artifact(envelope)

        for rendered in (text, shell_text):
            self.assertIn("[GenericCard] Run Log", rendered)
            self.assertIn("A2UI v1", rendered)
            self.assertNotIn("[ActionRef]", rendered)
            self.assertNotIn("[SelectionRef]", rendered)

    def test_terminal_artifact_render_target_resolver_recovers_schema_valid_leaf_payloads_without_hints_in_fallback_mode(
        self,
    ) -> None:
        shell = ShellUI()
        raw_action = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        raw_selection = {
            "id": "choice-1",
            "label": "Choice",
            "payload": {"nested": {"items": [1, 2]}},
        }

        for artifact, expected_kind in ((raw_action, "action"), (raw_selection, "selection")):
            resolved_artifact, resolved_kind = resolve_terminal_artifact_render_target(
                artifact,
                requested_kind=None,
                allow_invalid_envelope_recovery=True,
            )
            with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
                fallback_artifact, fallback_kind = shell._resolve_fallback_artifact(artifact, kind=None)

            self.assertEqual(resolved_kind, expected_kind)
            self.assertEqual(resolved_artifact, artifact)
            self.assertEqual(fallback_artifact, artifact)
            self.assertEqual(fallback_kind, "card")

    def test_shell_ui_keeps_ambiguous_raw_leaf_payloads_on_card_default_during_fallback(self) -> None:
        shell = ShellUI()
        raw_action = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        raw_selection = {
            "id": "choice-1",
            "label": "Choice",
            "payload": {"nested": {"items": [1, 2]}},
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(raw_action)
            selection_text = shell.render_artifact(raw_selection)

        for text in (action_text, selection_text):
            self.assertIn("[<missing>] <untitled>", text)
            self.assertNotIn("[ActionRef]", text)
            self.assertNotIn("[SelectionRef]", text)
            self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_terminal_card_renderer_recovers_valid_card_payloads_from_malformed_terminal_artifacts(
        self,
    ) -> None:
        text = render_terminal_card(
            {
                "type": "TerminalArtifact",
                "kind": "dialog",
                "artifact": {
                    "type": "GenericCard",
                    "title": " Run Log ",
                    "a2ui_version": 1,
                    "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                    "actions": [],
                },
                "trace_id": "drop-me",
            }
        )

        self.assertIn("[GenericCard] Run Log", text)
        self.assertIn("A2UI v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_shell_ui_recovers_action_payload_from_invalid_terminal_artifacts(self) -> None:
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

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_shell_ui_recovers_selection_payload_from_invalid_terminal_artifacts(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "card",
                    "artifact": {
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                    "trace_id": "drop-me",
                }
            )

        self.assertIn("[SelectionRef] Choice", text)
        self.assertIn("Selection schema v1", text)
        self.assertNotIn("[UnknownCard] <invalid card>", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_shell_ui_recovers_schema_valid_leaf_payloads_from_card_envelopes_with_explicit_hints(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "card",
                    "artifact": {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                },
                kind="action",
            )
            selection_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "card",
                    "artifact": {
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                    "trace_id": "drop-me",
                },
                kind="selection",
            )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("trace_id", selection_text)

    def test_shell_ui_preserves_authoritative_and_explicit_kinds_for_malformed_action_and_selection_payloads(
        self,
    ) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_envelope_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "action",
                    "artifact": {
                        "id": "export_document",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                }
            )
            selection_envelope_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "selection",
                    "artifact": {
                        "id": "choice-1",
                        "label": "Choice",
                    },
                    "trace_id": "drop-me",
                }
            )
            explicit_action_text = shell.render_artifact(
                {
                    "id": "export_document",
                    "payload": {"format": "md"},
                },
                kind="action",
            )
            explicit_selection_text = shell.render_artifact(
                {
                    "id": "choice-1",
                    "label": "Choice",
                },
                kind="selection",
            )

        for text in (action_envelope_text, explicit_action_text):
            self.assertIn("[ActionRef] <invalid action>", text)
            self.assertIn("Action schema v1", text)
            self.assertNotIn("[<missing>] <untitled>", text)
            self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
            self.assertNotIn("trace_id", text)

        for text in (selection_envelope_text, explicit_selection_text):
            self.assertIn("[SelectionRef] <invalid selection>", text)
            self.assertIn("Selection schema v1", text)
            self.assertNotIn("[<missing>] <untitled>", text)
            self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
            self.assertNotIn("trace_id", text)

    def test_shell_ui_recovers_canonical_action_payloads_without_hints_during_fallback(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "card",
                    "artifact": {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                }
            )

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("[UnknownCard] <invalid card>", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_terminal_artifact_renderer_and_shell_fallback_preserve_card_hints_for_malformed_action_envelopes(
        self,
    ) -> None:
        shell = ShellUI()
        envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
            "trace_id": "drop-me",
        }

        direct_text = render_terminal_artifact(envelope, kind="card")

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            shell_text = shell.render_artifact(envelope, kind="card")

        for text in (direct_text, shell_text):
            self.assertIn("[UnknownCard] <invalid card>", text)
            self.assertIn("- raw:", text)
            self.assertNotIn("[ActionRef]", text)
            self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_shell_ui_recovers_matching_kinds_from_malformed_terminal_artifacts(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                build_terminal_artifact_envelope(
                    ActionRef(
                        id=" export_document ",
                        label=" Export ",
                        payload={"format": "md"},
                    ),
                    kind="action",
                )
                | {"trace_id": "drop-me"}
            )
            selection_text = shell.render_artifact(
                build_terminal_artifact_envelope(
                    SelectionRef(
                        id=" choice-1 ",
                        label=" Choice ",
                        payload={"nested": {"items": [1, 2]}},
                    ),
                    kind="selection",
                )
                | {"trace_id": "drop-me"}
            )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("trace_id", selection_text)

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

    def test_shell_ui_keeps_authoritative_envelope_kind_during_fallback(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                build_terminal_artifact_envelope(
                    ActionRef(
                        id=" export_document ",
                        label=" Export ",
                        payload={"format": "md"},
                    ),
                    kind="action",
                ),
                kind="selection",
            )

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("[SelectionRef]", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_shell_ui_rejects_action_and_selection_payloads_under_conflicting_card_hints(self) -> None:
        shell = ShellUI()

        action_text = shell.render_artifact(
            {"type": "ActionRef", "id": "export_document", "label": "Export", "payload": {"format": "md"}},
            kind="card",
        )
        selection_text = shell.render_artifact(
            {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
            },
            kind="card",
        )

        self.assertIn("[UnknownCard] <invalid card>", action_text)
        self.assertIn("Action policy: copy_to_clipboard_only", action_text)
        self.assertNotIn("[ActionRef]", action_text)
        self.assertNotIn("[SelectionRef]", action_text)

        self.assertIn("[UnknownCard] <invalid card>", selection_text)
        self.assertIn("Action policy: copy_to_clipboard_only", selection_text)
        self.assertNotIn("[ActionRef]", selection_text)
        self.assertNotIn("[SelectionRef]", selection_text)

    def test_shell_ui_prefers_typed_payload_kind_over_conflicting_hint_for_non_envelope_payloads(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            card_text = shell.render_artifact(
                {
                    "type": "GenericCard",
                    "title": " Run Log ",
                    "a2ui_version": 1,
                    "blocks": [],
                    "actions": [],
                },
                kind="action",
            )
            action_text = shell.render_artifact(
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
                kind="selection",
            )
            selection_text = shell.render_artifact(
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
                kind="action",
            )

        self.assertIn("[GenericCard] Run Log", card_text)
        self.assertIn("A2UI v1", card_text)
        self.assertNotIn("[ActionRef]", card_text)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[SelectionRef]", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[ActionRef]", selection_text)

    def test_shell_ui_prefers_typed_payload_kind_over_conflicting_hint_during_fallback(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "ActionRef",
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                },
                kind="selection",
            )

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("[SelectionRef]", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_validate_generic_card_requires_blocks_and_actions_fields(self) -> None:
        with self.assertRaises(ValueError):
            validate_generic_card(
                {
                    "type": "GenericCard",
                    "title": "Patch",
                    "actions": [],
                }
            )

        with self.assertRaises(ValueError):
            validate_generic_card(
                {
                    "type": "GenericCard",
                    "title": "Patch",
                    "blocks": [],
                }
            )

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

        self.assertIn("[SelectionRef] Choice", text)
        self.assertIn("Selection schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_shell_ui_routes_fallback_rendering_through_the_explicit_cli_entrypoint(self) -> None:
        shell = ShellUI()
        artifact = {
            "type": "GenericCard",
            "title": " Fallback ",
            "blocks": [],
            "actions": [],
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch(
                "src.qual.ui.shell.render_terminal_cli_fallback",
                return_value="cli-fallback",
            ) as cli_fallback:
                text = shell.render_artifact(artifact)

        self.assertEqual(text, "cli-fallback")
        cli_fallback.assert_called_once_with(artifact, kind="card")

    def test_shell_ui_prefers_the_explicit_cli_fallback_entrypoint_when_available(self) -> None:
        shell = ShellUI()
        artifact = {
            "type": "GenericCard",
            "title": " Fallback ",
            "blocks": [],
            "actions": [],
        }

        with patch(
            "src.qual.ui.shell.render_terminal_cli_fallback",
            return_value="cli-fallback",
        ) as cli_fallback:
            with patch(
                "src.qual.ui.shell.render_terminal_artifact",
                return_value="generic-fallback",
            ) as generic_renderer:
                text = shell.render_artifact(artifact)

        self.assertEqual(text, "cli-fallback")
        cli_fallback.assert_called_once_with(artifact, kind="card")
        generic_renderer.assert_not_called()

    def test_shell_ui_keeps_raw_leaf_card_default_for_invalid_kind_hints_during_fallback(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch(
                "src.qual.ui.shell.render_terminal_cli_fallback",
                return_value="cli-fallback",
            ) as cli_fallback:
                text = shell.render_artifact(raw_leaf, kind="dialog")

        self.assertEqual(text, "cli-fallback")
        cli_fallback.assert_called_once_with(raw_leaf, kind="card")

    def test_shell_ui_keeps_raw_leaf_card_default_for_explicit_card_hints_during_fallback(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch(
                "src.qual.ui.shell.render_terminal_cli_fallback",
                return_value="cli-fallback",
            ) as cli_fallback:
                text = shell.render_artifact(raw_leaf, kind="card")

        self.assertEqual(text, "cli-fallback")
        cli_fallback.assert_called_once_with(raw_leaf, kind="card")

    def test_shell_ui_uses_shared_cli_fallback_target_resolver_for_explicit_card_hints(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch(
                "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                return_value=(raw_leaf, "card"),
            ) as resolver:
                with patch("src.qual.ui.shell.render_terminal_cli_fallback", return_value="cli-fallback") as cli_fallback:
                    text = shell.render_artifact(raw_leaf, kind="card")

        self.assertEqual(text, "cli-fallback")
        resolver.assert_called_once_with(raw_leaf, kind="card")
        cli_fallback.assert_called_once_with(raw_leaf, kind="card")

    def test_terminal_renderer_includes_safe_raw_preview_for_invalid_cards(self) -> None:
        text = render_terminal_card(_OpaqueValue())

        self.assertIn("[UnknownCard] <invalid card>", text)
        self.assertIn("Fallback: unknown card", text)
        self.assertIn("Action policy: copy_to_clipboard_only", text)
        self.assertIn("- raw:", text)
        self.assertIn("<non-json:_OpaqueValue>", text)
        self.assertNotIn("object at 0x", text)

    def test_shell_ui_falls_back_to_safe_invalid_card_preview_when_primary_rendering_fails(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(_OpaqueValue())

        self.assertIn("[UnknownCard] <invalid card>", text)
        self.assertIn("Fallback: unknown card", text)
        self.assertIn("Action policy: copy_to_clipboard_only", text)
        self.assertIn("- raw:", text)
        self.assertIn("<non-json:_OpaqueValue>", text)
        self.assertNotIn("object at 0x", text)

    def test_shell_ui_falls_back_when_fallback_resolution_raises(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch.object(ShellUI, "_resolve_fallback_artifact", side_effect=RuntimeError("resolver boom")):
                text = shell.render_artifact(_OpaqueValue(), kind="action")

        self.assertIn("[ActionRef] <invalid action>", text)
        self.assertIn("Action schema v1", text)
        self.assertIn("- raw:", text)
        self.assertIn("<non-json:_OpaqueValue>", text)
        self.assertNotIn("resolver boom", text)

    def test_shell_ui_recovers_leaf_payloads_from_terminal_envelopes_when_shared_resolver_raises(
        self,
    ) -> None:
        shell = ShellUI()
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
                "selected": True,
            },
            "trace_id": "drop-me",
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch(
                "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                side_effect=RuntimeError("resolver boom"),
            ):
                with patch("src.qual.ui.shell.render_terminal_card", side_effect=RuntimeError("card boom")):
                    text = shell.render_artifact(envelope)

        self.assertIn("[SelectionRef] Choice", text)
        self.assertIn("Selection schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("resolver boom", text)
        self.assertNotIn("card boom", text)

    def test_shell_ui_keeps_schema_valid_leaf_payloads_on_card_default_when_fallback_resolution_raises(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch.object(ShellUI, "_resolve_fallback_artifact", side_effect=RuntimeError("resolver boom")):
                action_text = shell.render_artifact(
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    }
                )
                selection_text = shell.render_artifact(
                    {
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    }
                )

        self.assertIn("[<missing>] <untitled>", action_text)
        self.assertNotIn("[ActionRef]", action_text)
        self.assertNotIn("[SelectionRef]", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)

        self.assertIn("[<missing>] <untitled>", selection_text)
        self.assertNotIn("[ActionRef]", selection_text)
        self.assertNotIn("[SelectionRef]", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)

    def test_shell_ui_prefers_partial_leaf_hints_over_generic_card_fallbacks(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                {
                    "id": "export_document",
                    "payload": {"format": "md"},
                    "confirm": {"title": "Approve", "message": "Export now?"},
                }
            )
            selection_text = shell.render_artifact(
                {
                    "id": "choice-1",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                }
            )

        self.assertIn("[ActionRef] <invalid action>", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[UnknownCard] <invalid card>", action_text)

        self.assertIn("[SelectionRef] <invalid selection>", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[UnknownCard] <invalid card>", selection_text)

    def test_shell_ui_keeps_schema_valid_leaf_payloads_on_card_default_when_resolver_returns_card(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                }
            )
            selection_text = shell.render_artifact(
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                }
            )

        self.assertIn("[<missing>] <untitled>", action_text)
        self.assertNotIn("[ActionRef]", action_text)
        self.assertNotIn("[SelectionRef]", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)

        self.assertIn("[<missing>] <untitled>", selection_text)
        self.assertNotIn("[ActionRef]", selection_text)
        self.assertNotIn("[SelectionRef]", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)

    def test_shell_ui_routes_raw_leaf_card_default_through_cli_fallback_entrypoint(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch("src.qual.ui.shell.render_terminal_cli_fallback", return_value="cli-fallback") as cli_fallback:
                with patch("src.qual.ui.shell.render_terminal_card", side_effect=RuntimeError("card boom")):
                    text = shell.render_artifact(raw_leaf)

        self.assertEqual(text, "cli-fallback")
        cli_fallback.assert_called_once_with(raw_leaf, kind="card")

    def test_shell_ui_unwraps_malformed_terminal_envelopes_for_explicit_kinds(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "action",
                    "artifact": {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                },
                kind="action",
            )
            selection_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "selection",
                    "artifact": {
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                    "trace_id": "drop-me",
                },
                kind="selection",
            )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("trace_id", selection_text)

    def test_shell_ui_recovers_nested_terminal_envelopes_during_fallback(self) -> None:
        shell = ShellUI()

        action_wrapper = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": build_terminal_artifact_envelope(
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
                kind="action",
            ),
            "trace_id": "drop-me",
        }
        selection_wrapper = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": build_terminal_artifact_envelope(
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
                kind="selection",
            ),
            "trace_id": "drop-me",
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(action_wrapper)
            selection_text = shell.render_artifact(selection_wrapper)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("trace_id", selection_text)

    def test_shell_ui_recovers_deeply_nested_terminal_envelopes_during_fallback(self) -> None:
        shell = ShellUI()

        def wrap(payload: object) -> dict[str, object]:
            return {
                "type": "TerminalArtifact",
                "kind": "card",
                "artifact": payload,
                "trace_id": "drop-me",
            }

        action_wrapper = wrap(
            wrap(
                build_terminal_artifact_envelope(
                    ActionRef(
                        id=" export_document ",
                        label=" Export ",
                        payload={"format": "md"},
                    ),
                    kind="action",
                )
            )
        )
        selection_wrapper = wrap(
            wrap(
                build_terminal_artifact_envelope(
                    SelectionRef(
                        id=" choice-1 ",
                        label=" Choice ",
                        payload={"nested": {"items": [1, 2]}},
                    ),
                    kind="selection",
                )
            )
        )

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch("src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target", side_effect=RuntimeError("boom")):
                action_text = shell.render_artifact(action_wrapper)
                selection_text = shell.render_artifact(selection_wrapper)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("trace_id", selection_text)

    def test_card_contract_manifest_is_versioned_and_aligns_with_a2ui_schema(self) -> None:
        manifest = describe_card_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["card_contract_version"], CARD_CONTRACT_VERSION)
        self.assertEqual(manifest["card_version"], CARD_CONTRACT_VERSION)
        self.assertEqual(manifest["type"], "CardContract")
        self.assertEqual(manifest["card_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprint"], manifest["card_fingerprint"])
        self.assertEqual(len(manifest["card_fingerprint"]), 64)
        self.assertEqual(a2ui_manifest["card_contract"], manifest)
        self.assertEqual(a2ui_manifest["card_contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(manifest["card_schemas"], a2ui_manifest["schemas"]["cards"])
        self.assertEqual(a2ui_manifest["schemas"]["card_contract"], manifest)
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
        self.assertEqual(manifest["action_version"], A2UI_ACTION_SCHEMA_VERSION)
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

    def test_terminal_card_renderer_rejects_explicit_action_and_selection_payloads(self) -> None:
        action = {
            "type": "ActionRef",
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        selection = {
            "type": "SelectionRef",
            "id": "choice-1",
            "label": "Choice",
            "payload": {"nested": {"items": [1, 2]}},
        }

        action_text = render_terminal_card(action)
        selection_text = render_terminal_card(selection)

        self.assertIn("[UnknownCard] <invalid card>", action_text)
        self.assertIn("Action policy: copy_to_clipboard_only", action_text)
        self.assertNotIn("[ActionRef] <untitled>", action_text)

        self.assertIn("[UnknownCard] <invalid card>", selection_text)
        self.assertIn("Action policy: copy_to_clipboard_only", selection_text)
        self.assertNotIn("[SelectionRef] <untitled>", selection_text)

    def test_shell_ui_recovers_action_and_selection_payloads_from_malformed_terminal_artifacts(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            action_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "ActionRef",
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                        "confirm": {"title": "Approve", "message": "Proceed?"},
                    },
                    "trace_id": "drop-me",
                }
            )
            selection_text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "SelectionRef",
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                        "selected": True,
                    },
                    "trace_id": "drop-me",
                }
            )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)
        self.assertNotIn("trace_id", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)
        self.assertNotIn("trace_id", selection_text)

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

    def test_shell_ui_keeps_policy_sensitive_raw_leaf_payloads_on_the_action_path_during_fallback(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "policy_sensitive": True,
                }
            )

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("- policy_sensitive: true", text)
        self.assertNotIn("[GenericCard]", text)

    def test_shell_ui_preserves_explicit_card_kind_hints_during_fallback(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                kind="card",
            )

        self.assertIn("[<missing>] <untitled>", text)
        self.assertNotIn("[UnknownCard] <invalid card>", text)
        self.assertNotIn("[SelectionRef]", text)
        self.assertNotIn("[ActionRef]", text)

    def test_shell_ui_preserves_card_kind_hint_for_action_and_selection_envelopes_during_fallback(self) -> None:
        shell = ShellUI()
        direct_action_envelope = build_terminal_artifact_envelope(
            ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
            ),
            kind="action",
        )
        direct_selection_envelope = build_terminal_artifact_envelope(
            SelectionRef(
                id=" choice-1 ",
                label=" Choice ",
                payload={"nested": {"items": [1, 2]}},
            ),
            kind="selection",
        )
        nested_action_envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": direct_action_envelope,
        }
        nested_selection_envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": direct_selection_envelope,
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            for case_name, artifact in (
                ("direct action envelope", direct_action_envelope),
                ("direct selection envelope", direct_selection_envelope),
                ("nested action envelope", nested_action_envelope),
                ("nested selection envelope", nested_selection_envelope),
            ):
                with self.subTest(case=case_name):
                    text = shell.render_artifact(artifact, kind="card")
                    self.assertIn("[UnknownCard] <invalid card>", text)
                    self.assertNotIn("[ActionRef]", text)
                    self.assertNotIn("[SelectionRef]", text)
                    self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_terminal_artifact_renderer_and_shell_fallback_preserve_card_hints_for_malformed_envelopes(
        self,
    ) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
                "selected": True,
            },
        }

        direct_text = render_terminal_artifact(envelope, kind="card")
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            shell_text = shell.render_artifact(envelope, kind="card")

        for text in (direct_text, shell_text):
            self.assertIn("[UnknownCard] <invalid card>", text)
            self.assertIn("- raw:", text)
            self.assertNotIn("[SelectionRef]", text)
            self.assertNotIn("[ActionRef]", text)
            self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

    def test_shell_ui_recovers_card_hints_from_malformed_terminal_artifacts(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "card",
                    "artifact": {
                        "type": "GenericCard",
                        "title": "Run Log",
                        "a2ui_version": 1,
                        "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                        "actions": [],
                    },
                    "trace_id": "drop-me",
                },
                kind="card",
            )

        self.assertIn("[GenericCard] Run Log", text)
        self.assertIn("A2UI v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_shell_ui_recovers_typed_card_payloads_from_malformed_terminal_envelopes(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "GenericCard",
                        "title": " Run Log ",
                        "a2ui_version": 1,
                        "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                        "actions": [],
                    },
                    "trace_id": "drop-me",
                }
            )

        self.assertIn("[GenericCard] Run Log", text)
        self.assertIn("A2UI v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_shell_ui_falls_back_to_invalid_action_when_action_recovery_renderer_raises(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch("src.qual.ui.shell.render_terminal_cli_fallback", side_effect=RuntimeError("cli fallback boom")):
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
        self.assertNotIn("cli fallback boom", text)

    def test_shell_ui_falls_back_to_invalid_selection_when_selection_recovery_renderer_raises(self) -> None:
        shell = ShellUI()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch("src.qual.ui.shell.render_terminal_cli_fallback", side_effect=RuntimeError("cli fallback boom")):
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
        self.assertNotIn("cli fallback boom", text)

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

    def test_terminal_artifact_snapshots_card_dataclasses_before_rendering(self) -> None:
        card = _StructuredCard(
            type="GenericCard",
            title=" Run Log ",
            a2ui_version=1,
            blocks=[{"type": "MarkdownBlock", "markdown": "Hello"}],
            actions=[],
        )

        envelope = build_terminal_artifact_envelope(card, kind="card")
        rendered_card = render_terminal_artifact(card)

        card.title = "Changed"
        card.blocks[0]["markdown"] = "Mutated"

        rendered_envelope = render_terminal_artifact(envelope)

        self.assertIn("[GenericCard] Run Log", rendered_card)
        self.assertIn("A2UI v1", rendered_card)
        self.assertEqual(envelope["artifact"]["title"], " Run Log ")
        self.assertEqual(envelope["artifact"]["blocks"], [{"type": "MarkdownBlock", "markdown": "Hello"}])
        self.assertIn("[GenericCard] Run Log", rendered_envelope)
        self.assertIn("Hello", rendered_envelope)
        self.assertNotIn("Changed", rendered_envelope)
        self.assertNotIn("Mutated", rendered_envelope)

    def test_terminal_artifact_prefers_typed_card_payloads_over_conflicting_non_card_hints(self) -> None:
        artifact = {
            "type": "GenericCard",
            "title": " Run Log ",
            "a2ui_version": 1,
            "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
            "actions": [],
        }

        action_text = render_terminal_artifact(artifact, kind="action")
        selection_text = render_terminal_artifact(artifact, kind="selection")

        self.assertIn("[GenericCard] Run Log", action_text)
        self.assertIn("A2UI v1", action_text)
        self.assertNotIn("[ActionRef]", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)

        self.assertIn("[GenericCard] Run Log", selection_text)
        self.assertIn("A2UI v1", selection_text)
        self.assertNotIn("[SelectionRef]", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)

    def test_terminal_artifact_prefers_card_shape_over_conflicting_action_hints(self) -> None:
        mixed_card = {
            "title": " Run Log ",
            "a2ui_version": 1,
            "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
            "actions": [],
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
            "confirm": {"title": "Approve", "message": "Proceed?"},
        }

        text = render_terminal_artifact(mixed_card)

        self.assertIn("[<missing>] Run Log", text)
        self.assertIn("A2UI v1", text)
        self.assertIn("Hello", text)
        self.assertNotIn("[ActionRef]", text)
        self.assertNotIn("[SelectionRef]", text)

        shell = ShellUI()
        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            fallback_text = shell.render_artifact(mixed_card)

        self.assertIn("[<missing>] Run Log", fallback_text)
        self.assertIn("A2UI v1", fallback_text)
        self.assertIn("Hello", fallback_text)
        self.assertNotIn("[ActionRef]", fallback_text)
        self.assertNotIn("[SelectionRef]", fallback_text)

    def test_terminal_artifact_rejects_action_or_selection_payloads_when_card_kind_is_explicit(self) -> None:
        with self.assertRaises(ValueError):
            render_terminal_artifact(
                {"type": "ActionRef", "id": "export_document", "label": "Export", "payload": {"format": "md"}},
                kind="card",
            )

        with self.assertRaises(ValueError):
            render_terminal_artifact(
                {
                    "type": "SelectionRef",
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                kind="card",
            )

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

    def test_terminal_artifact_prefers_typed_action_and_selection_mappings_over_conflicting_non_card_hints(self) -> None:
        action_text = render_terminal_artifact(
            {"type": "ActionRef", "id": "export_document", "label": "Export", "payload": {"format": "md"}},
            kind="selection",
        )
        selection_text = render_terminal_artifact(
            {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
            },
            kind="action",
        )

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[SelectionRef]", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[ActionRef]", selection_text)

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

    def test_terminal_artifact_envelope_recovers_structured_payloads_even_with_conflicting_hints(self) -> None:
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

        recovered_text = render_terminal_artifact(
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

        self.assertIn("[SelectionRef] Choice", recovered_text)
        self.assertIn("Selection schema v1", recovered_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", recovered_text)

    def test_terminal_leaf_renderers_accept_matching_terminal_artifact_envelopes(self) -> None:
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
                selected=True,
            ),
            kind="selection",
        )

        action_text = render_terminal_action(action_envelope)
        selection_text = render_terminal_selection(selection_envelope)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)

    def test_terminal_card_renderer_accepts_terminal_artifact_envelopes_for_cli_fallback(self) -> None:
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
                "blocks": [],
                "actions": [],
            },
            kind="card",
        )

        action_text = render_terminal_card(action_envelope)
        selection_text = render_terminal_card(selection_envelope)
        card_text = render_terminal_card(card_envelope)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)

        self.assertIn("[GenericCard] Run Log", card_text)
        self.assertIn("A2UI v1", card_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", card_text)

    def test_terminal_card_renderer_recovers_action_payloads_from_malformed_terminal_artifacts(
        self,
    ) -> None:
        with patch("src.qual.ui.a2ui.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = render_terminal_card(
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "ActionRef",
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                }
            )

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_terminal_card_renderer_recovers_selection_payloads_from_malformed_terminal_artifacts(
        self,
    ) -> None:
        with patch("src.qual.ui.a2ui.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = render_terminal_card(
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "SelectionRef",
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                    "trace_id": "drop-me",
                }
            )

        self.assertIn("[SelectionRef] Choice", text)
        self.assertIn("Selection schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)
        self.assertNotIn("trace_id", text)

    def test_terminal_artifact_unwraps_nested_envelopes_before_rendering(self) -> None:
        nested_envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": build_terminal_artifact_envelope(
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                    selected=True,
                ),
                kind="selection",
            ),
            "trace_id": "drop-me",
        }

        text = render_terminal_artifact(nested_envelope)

        self.assertIn("[SelectionRef] Choice", text)
        self.assertIn("Selection schema v1", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

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

    def test_card_materializers_accept_structured_dataclass_payloads(self) -> None:
        caps = _capabilities()
        structured_generic = _StructuredCard(
            type="GenericCard",
            title=" Run Log ",
            a2ui_version=1,
            blocks=[{"type": "MarkdownBlock", "markdown": "Kept"}],
            actions=[
                ActionRef(
                    id=" copy_to_clipboard ",
                    label=" Copy ",
                    payload={"text": "safe"},
                ),
            ],
        )
        structured_unknown = _StructuredCard(
            type="FutureCard",
            title="Future",
            a2ui_version=1,
            blocks=[{"type": "MarkdownBlock", "markdown": "Recovered"}],
            actions=[],
        )

        prepared = engine_prepare_card(structured_generic, caps)
        materialized = studio_materialize_card(structured_unknown, caps)
        direct_unknown = build_unknown_card(structured_unknown, supported_actions=("copy_to_clipboard",))

        self.assertEqual(prepared["type"], "GenericCard")
        self.assertEqual(prepared["title"], "Run Log")
        self.assertEqual(
            prepared["actions"],
            [{"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "safe"}}],
        )
        self.assertEqual(materialized["type"], "UnknownCard")
        self.assertEqual(materialized["title"], "Unsupported card type: FutureCard")
        self.assertEqual(materialized["actions"][0]["id"], "copy_to_clipboard")
        self.assertEqual(direct_unknown["type"], "UnknownCard")
        self.assertEqual(direct_unknown["title"], "Unsupported card type: FutureCard")
        self.assertEqual(direct_unknown["actions"][0]["id"], "copy_to_clipboard")

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
