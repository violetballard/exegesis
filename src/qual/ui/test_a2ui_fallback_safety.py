from __future__ import annotations

import json
import unittest
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import patch

import src.qual.ui as public_ui
from src.qual.ui.a2ui import (
    A2UI_ACTION_SCHEMA_VERSION,
    A2UI_CAPABILITIES_SCHEMA_VERSION,
    A2UI_LEAF_CONTRACTS_SCHEMA_VERSION,
    A2UICapabilities,
    A2UISessionStore,
    ALLOWED_ACTION_IDS,
    ActionRef,
    PolicyGate,
    CARD_CONTRACT_VERSION,
    REQUIRED_PRIMITIVE_BLOCKS,
    SELECTION_SCHEMA_VERSION,
    TERMINAL_FALLBACK_SCHEMA_VERSION,
    GENERIC_FALLBACK_SUBTITLE,
    card_contract_fingerprint,
    action_contract_fingerprint,
    a2ui_capabilities_contract_fingerprint,
    a2ui_contract_fingerprint,
    a2ui_dispatch_contract_fingerprint,
    a2ui_engine_contract_fingerprint,
    a2ui_leaf_contracts_fingerprint,
    build_unknown_card,
    describe_a2ui_contract,
    describe_a2ui_contract_fingerprints,
    describe_a2ui_dispatch_contract,
    describe_a2ui_dispatch_contract_fingerprints,
    describe_a2ui_capabilities_contract,
    describe_a2ui_engine_contract,
    describe_a2ui_leaf_contracts,
    describe_action_contract,
    describe_action_contract_manifest,
    describe_card_contract,
    describe_card_contract_manifest,
    describe_selection_contract,
    describe_selection_contract_manifest,
    describe_terminal_artifact_envelope_contract,
    describe_terminal_artifact_kind_contracts_manifest,
    describe_terminal_artifact_cli_fallback_contract,
    describe_terminal_artifact_cli_fallback_contract_manifest,
    describe_terminal_artifact_cli_fallback_contract_manifest_fingerprints,
    describe_terminal_artifact_cli_fallback_contract_fingerprints,
    describe_terminal_artifact_cli_fallback_entrypoint_contract,
    describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints,
    describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract,
    describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract,
    describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract,
    describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest,
    describe_terminal_artifact_cli_fallback_target_contract,
    describe_terminal_artifact_cli_fallback_target_contract_manifest,
    describe_terminal_artifact_cli_fallback_target_contract_manifest_fingerprints,
    describe_terminal_artifact_cli_fallback_target_contract_fingerprints,
    describe_terminal_artifact_cli_fallback_route_contract,
    describe_terminal_artifact_cli_fallback_route_contract_manifest,
    describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints,
    describe_terminal_artifact_cli_fallback_route_contract_fingerprints,
    describe_terminal_artifact_kind_contracts,
    describe_terminal_artifact_contract_fingerprints,
    describe_terminal_artifact_contract,
    describe_terminal_artifact_raw_leaf_card_default_contract,
    describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints,
    describe_terminal_artifact_raw_leaf_card_default_policy_contract,
    describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints,
    describe_terminal_artifact_kind_resolution_contract,
    describe_terminal_artifact_fallback_recovery_contract,
    describe_terminal_artifact_render_target_contract,
    describe_terminal_artifact_render_target_contract_manifest,
    describe_terminal_artifact_render_target_contract_fingerprints,
    describe_terminal_artifact_renderer_entrypoints_contract,
    describe_terminal_artifact_renderer_entrypoints_contract_manifest,
    describe_terminal_artifact_renderer_entrypoints_contract_fingerprints,
    describe_terminal_artifact_rendering_contract_manifest,
    describe_terminal_artifact_rendering_contract,
    describe_terminal_artifact_rendering_contract_fingerprints,
    describe_terminal_artifact_cli_fallback_entrypoint_contract_manifest,
    describe_terminal_fallback_contract,
    build_terminal_artifact_envelope,
    normalize_capabilities,
    normalize_action_ref,
    normalize_selection_ref,
    normalize_terminal_artifact_payload,
    engine_prepare_card,
    render_terminal_action,
    render_terminal_artifact,
    render_terminal_cli_fallback,
    render_terminal_card,
    render_terminal_selection,
    _infer_terminal_artifact_kind_from_mapping,
    refine_terminal_artifact_cli_fallback_target,
    _render_payload_preview,
    SelectionRef,
    _should_preserve_raw_leaf_card_default,
    resolve_terminal_artifact_cli_fallback_target,
    resolve_terminal_artifact_render_target,
    selection_contract_fingerprint,
    TERMINAL_ARTIFACT_DEFAULT_KIND,
    TERMINAL_ARTIFACT_SUPPORTED_KINDS,
    terminal_artifact_contract_fingerprint,
    terminal_artifact_envelope_contract_fingerprint,
    terminal_artifact_cli_fallback_contract_fingerprint,
    terminal_artifact_cli_fallback_contract_manifest_fingerprint,
    terminal_artifact_cli_fallback_contract_manifest_fingerprints_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint,
    terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint,
    terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint,
    terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint,
    terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint,
    terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint,
    terminal_artifact_cli_fallback_target_contract_fingerprint,
    terminal_artifact_cli_fallback_target_contract_manifest_fingerprint,
    terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint,
    terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint,
    terminal_artifact_cli_fallback_route_contract_fingerprint,
    terminal_artifact_cli_fallback_route_contract_manifest_fingerprint,
    terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint,
    terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint,
    terminal_artifact_kind_contracts_manifest_fingerprint,
    _fingerprint_manifest_section,
    terminal_artifact_raw_leaf_card_default_contract_fingerprint,
    terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint,
    terminal_artifact_render_target_contract_fingerprint,
    terminal_artifact_render_target_contract_manifest_fingerprint,
    terminal_artifact_renderer_entrypoints_contract_fingerprint,
    terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint,
    terminal_artifact_renderer_entrypoints_contract_fingerprints_fingerprint,
    terminal_artifact_rendering_contract_manifest_fingerprint,
    _build_terminal_artifact_renderer_entrypoints,
    terminal_artifact_kind_resolution_fingerprint,
    terminal_artifact_fallback_recovery_fingerprint,
    terminal_artifact_rendering_contract_fingerprint,
    terminal_artifact_kind_contracts_fingerprint,
    terminal_fallback_contract_fingerprint,
    TERMINAL_ARTIFACT_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION,
    TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
    _build_a2ui_schema_versions_manifest,
    _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT,
    studio_materialize_card,
    validate_action_ref,
    validate_terminal_artifact_envelope,
    validate_generic_card,
    validate_selection_ref,
)
from src.qual.ui.shell import (
    SHELL_UI_CONTRACT_VERSION,
    SHELL_UI_ENTRYPOINTS,
    SHELL_UI_STARTUP_EMPTY_PREVIEW,
    SHELL_UI_STARTUP_FIELDS,
    SHELL_UI_STARTUP_PREVIEW_LIMIT,
    ShellUI,
    describe_shell_ui_contract,
    describe_shell_ui_contract_manifest,
    describe_shell_ui_contract_fingerprints,
    describe_shell_ui_contract_manifest_fingerprints,
    shell_ui_contract_fingerprint,
    shell_ui_contract_manifest_fingerprint,
    shell_ui_contract_manifest_fingerprints_fingerprint,
)


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
    def test_public_ui_package_exports_authoritative_contract_allowlists(self) -> None:
        self.assertIs(public_ui.ALLOWED_ACTION_IDS, ALLOWED_ACTION_IDS)
        self.assertIs(public_ui.REQUIRED_PRIMITIVE_BLOCKS, REQUIRED_PRIMITIVE_BLOCKS)
        self.assertIs(public_ui.PolicyGate, PolicyGate)
        self.assertIs(public_ui.describe_a2ui_engine_contract, describe_a2ui_engine_contract)
        self.assertIs(public_ui.a2ui_engine_contract_fingerprint, a2ui_engine_contract_fingerprint)
        self.assertIs(public_ui.describe_action_contract_manifest, describe_action_contract_manifest)
        self.assertIs(public_ui.describe_card_contract_manifest, describe_card_contract_manifest)
        self.assertEqual(
            public_ui.TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
            TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
        )
        self.assertIs(public_ui.SHELL_UI_ENTRYPOINTS, SHELL_UI_ENTRYPOINTS)
        self.assertIs(public_ui.SHELL_UI_STARTUP_FIELDS, SHELL_UI_STARTUP_FIELDS)
        self.assertEqual(public_ui.SHELL_UI_STARTUP_PREVIEW_LIMIT, SHELL_UI_STARTUP_PREVIEW_LIMIT)
        self.assertEqual(public_ui.SHELL_UI_STARTUP_EMPTY_PREVIEW, SHELL_UI_STARTUP_EMPTY_PREVIEW)
        self.assertIs(
            public_ui.describe_terminal_artifact_renderer_entrypoints_contract,
            describe_terminal_artifact_renderer_entrypoints_contract,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_renderer_entrypoints_contract_manifest,
            describe_terminal_artifact_renderer_entrypoints_contract_manifest,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_renderer_entrypoints_contract_fingerprints,
            describe_terminal_artifact_renderer_entrypoints_contract_fingerprints,
        )
        self.assertIs(
            public_ui.terminal_artifact_renderer_entrypoints_contract_fingerprint,
            terminal_artifact_renderer_entrypoints_contract_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint,
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_renderer_entrypoints_contract_fingerprints_fingerprint,
            terminal_artifact_renderer_entrypoints_contract_fingerprints_fingerprint,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_render_target_contract_manifest,
            describe_terminal_artifact_render_target_contract_manifest,
        )
        self.assertIs(
            public_ui.terminal_artifact_render_target_contract_manifest_fingerprint,
            terminal_artifact_render_target_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_rendering_contract_manifest,
            describe_terminal_artifact_rendering_contract_manifest,
        )
        self.assertIs(
            public_ui.terminal_artifact_rendering_contract_manifest_fingerprint,
            terminal_artifact_rendering_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_entrypoint_contract,
            describe_terminal_artifact_cli_fallback_entrypoint_contract,
        )
        self.assertIs(
            public_ui.describe_selection_contract_manifest,
            describe_selection_contract_manifest,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_entrypoint_contract_manifest,
            describe_terminal_artifact_cli_fallback_entrypoint_contract_manifest,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints,
            describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_contract,
            describe_terminal_artifact_cli_fallback_contract,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_contract_manifest,
            describe_terminal_artifact_cli_fallback_contract_manifest,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_target_contract,
            describe_terminal_artifact_cli_fallback_target_contract,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_target_contract_manifest,
            describe_terminal_artifact_cli_fallback_target_contract_manifest,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_target_contract_manifest_fingerprints,
            describe_terminal_artifact_cli_fallback_target_contract_manifest_fingerprints,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract,
            describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract,
            describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest,
            describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_kind_contracts_manifest,
            describe_terminal_artifact_kind_contracts_manifest,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_entrypoint_contract_fingerprint,
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint,
            terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint,
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_contract_fingerprint,
            terminal_artifact_cli_fallback_contract_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_contract_manifest_fingerprint,
            terminal_artifact_cli_fallback_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint,
            terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint,
            terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint,
            terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_kind_contracts_manifest_fingerprint,
            terminal_artifact_kind_contracts_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_route_contract_fingerprint,
            terminal_artifact_cli_fallback_route_contract_fingerprint,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_route_contract_manifest,
            describe_terminal_artifact_cli_fallback_route_contract_manifest,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_route_contract_manifest_fingerprint,
            terminal_artifact_cli_fallback_route_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint,
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint,
            terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_target_contract_fingerprint,
            terminal_artifact_cli_fallback_target_contract_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_target_contract_manifest_fingerprint,
            terminal_artifact_cli_fallback_target_contract_manifest_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint,
            terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint,
        )
        self.assertIs(
            public_ui.refine_terminal_artifact_cli_fallback_target,
            refine_terminal_artifact_cli_fallback_target,
        )
        self.assertEqual(
            public_ui.TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION,
            TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION,
        )
        self.assertEqual(
            public_ui.TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            public_ui.A2UI_LEAF_CONTRACTS_SCHEMA_VERSION,
            A2UI_LEAF_CONTRACTS_SCHEMA_VERSION,
        )
        self.assertEqual(public_ui.SHELL_UI_CONTRACT_VERSION, SHELL_UI_CONTRACT_VERSION)
        self.assertIs(public_ui.describe_a2ui_leaf_contracts, describe_a2ui_leaf_contracts)
        self.assertIs(public_ui.a2ui_leaf_contracts_fingerprint, a2ui_leaf_contracts_fingerprint)
        self.assertIs(public_ui.describe_shell_ui_contract, describe_shell_ui_contract)
        self.assertIs(public_ui.describe_shell_ui_contract_manifest, describe_shell_ui_contract_manifest)
        self.assertIs(public_ui.shell_ui_contract_fingerprint, shell_ui_contract_fingerprint)
        self.assertIs(
            public_ui.shell_ui_contract_manifest_fingerprint,
            shell_ui_contract_manifest_fingerprint,
        )

    def test_selection_contract_manifest_exposes_contract_fingerprint_alias(self) -> None:
        manifest = describe_selection_contract()
        manifest_alias = describe_selection_contract_manifest()

        self.assertEqual(manifest["contract_fingerprint"], manifest["selection_fingerprint"])
        self.assertEqual(
            manifest["selection_contract_fingerprint"],
            manifest["selection_fingerprint"],
        )
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(manifest["schema_version"], SELECTION_SCHEMA_VERSION)
        self.assertEqual(manifest["selection_schema_version"], SELECTION_SCHEMA_VERSION)
        self.assertEqual(manifest["selection_version"], SELECTION_SCHEMA_VERSION)
        self.assertEqual(manifest["selection_contract_version"], SELECTION_SCHEMA_VERSION)

    def test_action_and_selection_contract_manifests_expose_contract_manifest_aliases(self) -> None:
        action_manifest = describe_action_contract()
        selection_manifest = describe_selection_contract()

        self.assertEqual(action_manifest["contract_manifest_fingerprint"], action_manifest["contract_fingerprint"])
        self.assertEqual(selection_manifest["contract_manifest_fingerprint"], selection_manifest["contract_fingerprint"])
        self.assertEqual(action_manifest["contract_manifest"]["contract_fingerprint"], action_manifest["contract_fingerprint"])
        self.assertEqual(
            selection_manifest["contract_manifest"]["contract_fingerprint"],
            selection_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            action_manifest["contract_manifest"]["action_contract_fingerprint"],
            action_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            selection_manifest["contract_manifest"]["selection_contract_fingerprint"],
            selection_manifest["contract_fingerprint"],
        )

    def test_leaf_contract_manifest_alias_helpers_match_the_base_contracts(self) -> None:
        self.assertEqual(describe_action_contract_manifest(), describe_action_contract())
        self.assertEqual(describe_card_contract_manifest(), describe_card_contract())

    def test_a2ui_leaf_contract_manifest_bundles_action_and_selection_contracts(self) -> None:
        manifest = describe_a2ui_leaf_contracts()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["schema_version"], A2UI_LEAF_CONTRACTS_SCHEMA_VERSION)
        self.assertEqual(manifest["leaf_contracts_schema_version"], A2UI_LEAF_CONTRACTS_SCHEMA_VERSION)
        self.assertEqual(manifest["leaf_contracts_version"], A2UI_LEAF_CONTRACTS_SCHEMA_VERSION)
        self.assertEqual(manifest["type"], "A2UILeafContracts")
        self.assertEqual(manifest["action"], describe_action_contract())
        self.assertEqual(manifest["selection"], describe_selection_contract())
        self.assertEqual(manifest["action_contract"], describe_action_contract())
        self.assertEqual(manifest["selection_contract"], describe_selection_contract())
        self.assertEqual(manifest["action_contract_manifest"], describe_action_contract())
        self.assertEqual(manifest["selection_contract_manifest"], describe_selection_contract())
        self.assertEqual(manifest["action_fingerprint"], action_contract_fingerprint())
        self.assertEqual(manifest["selection_fingerprint"], selection_contract_fingerprint())
        self.assertEqual(manifest["action_contract_manifest_fingerprint"], action_contract_fingerprint())
        self.assertEqual(manifest["selection_contract_manifest_fingerprint"], selection_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprints"]["action"], action_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprints"]["selection"], selection_contract_fingerprint())
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(manifest["contract_fingerprints"]),
        )
        self.assertEqual(manifest["contract_fingerprints_contract"], manifest["contract_fingerprints"])
        self.assertEqual(manifest["contract_fingerprint"], a2ui_leaf_contracts_fingerprint())
        self.assertEqual(manifest["leaf_contracts_fingerprint"], a2ui_leaf_contracts_fingerprint())
        self.assertEqual(manifest["leaf_contracts_contract_fingerprint"], a2ui_leaf_contracts_fingerprint())
        self.assertEqual(manifest["leaf_contracts_contract_manifest"]["type"], "A2UILeafContracts")
        self.assertEqual(
            manifest["leaf_contracts_contract_manifest"]["contract_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            manifest["leaf_contracts_contract_manifest"]["action_contract_manifest"],
            describe_action_contract(),
        )
        self.assertEqual(
            manifest["leaf_contracts_contract_manifest"]["selection_contract_manifest"],
            describe_selection_contract(),
        )
        self.assertEqual(
            manifest["leaf_contracts_contract_manifest_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(manifest["leaf_contracts_manifest"]["type"], "A2UILeafContracts")
        self.assertEqual(
            manifest["leaf_contracts_manifest"]["contract_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            manifest["leaf_contracts_manifest_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)

    def test_a2ui_contract_surfaces_leaf_contract_bundle_for_engine_consumers(self) -> None:
        leaf_contracts = describe_a2ui_leaf_contracts()
        manifest = describe_a2ui_contract()
        fingerprints = describe_a2ui_contract_fingerprints()
        aliased_fingerprints = describe_a2ui_contract_fingerprints(include_contract_aliases=True)
        leaf_fingerprint = a2ui_leaf_contracts_fingerprint()

        self.assertEqual(manifest["leaf_contracts"], leaf_contracts)
        self.assertEqual(manifest["leaf_contracts_contract"], leaf_contracts)
        self.assertEqual(manifest["leaf_contracts_contract_manifest"], leaf_contracts)
        self.assertEqual(manifest["leaf_contracts_fingerprint"], leaf_fingerprint)
        self.assertEqual(manifest["leaf_contracts_contract_fingerprint"], leaf_fingerprint)
        self.assertEqual(manifest["leaf_contracts_contract_manifest_fingerprint"], leaf_fingerprint)
        self.assertEqual(manifest["leaf_contracts_manifest"], leaf_contracts)
        self.assertEqual(manifest["leaf_contracts_manifest_fingerprint"], leaf_fingerprint)
        self.assertEqual(manifest["schemas"]["leaf_contracts"], leaf_contracts)
        self.assertEqual(manifest["contract_fingerprints"]["leaf_contracts"], leaf_fingerprint)
        self.assertEqual(fingerprints["leaf_contracts"], leaf_fingerprint)
        self.assertEqual(aliased_fingerprints["leaf_contracts_contract"], leaf_fingerprint)
        self.assertEqual(aliased_fingerprints["leaf_contracts_contract_fingerprint"], leaf_fingerprint)
        self.assertEqual(aliased_fingerprints["leaf_contracts_contract_manifest"], leaf_fingerprint)
        self.assertEqual(
            aliased_fingerprints["leaf_contracts_contract_manifest_fingerprint"],
            leaf_fingerprint,
        )
        self.assertEqual(aliased_fingerprints["leaf_contracts_manifest"], leaf_fingerprint)
        self.assertEqual(
            aliased_fingerprints["leaf_contracts_manifest_fingerprint"],
            leaf_fingerprint,
        )

    def test_a2ui_contract_surfaces_terminal_artifact_supported_kinds(self) -> None:
        manifest = describe_a2ui_contract()
        fingerprints = describe_a2ui_contract_fingerprints(include_terminal_artifact=True)
        supported_kinds = list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)
        supported_kinds_fingerprint = _fingerprint_manifest_section(supported_kinds)

        self.assertEqual(manifest["terminal_artifact_supported_kinds"], supported_kinds)
        self.assertEqual(manifest["terminal_artifact_supported_kinds_contract"], supported_kinds)
        self.assertEqual(manifest["terminal_artifact_supported_kinds_fingerprint"], supported_kinds_fingerprint)
        self.assertEqual(
            manifest["terminal_artifact_supported_kinds_contract_fingerprint"],
            supported_kinds_fingerprint,
        )
        self.assertEqual(fingerprints["terminal_artifact_supported_kinds"], supported_kinds_fingerprint)
        self.assertEqual(
            fingerprints["terminal_artifact_supported_kinds_contract"],
            supported_kinds_fingerprint,
        )
        self.assertEqual(
            fingerprints["terminal_artifact_supported_kinds_contract_fingerprint"],
            supported_kinds_fingerprint,
        )

    def test_shell_inclusive_a2ui_fingerprint_surface_is_stable(self) -> None:
        first = describe_a2ui_contract_fingerprints(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )
        second = describe_a2ui_contract_fingerprints(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )

        self.assertEqual(first, second)
        self.assertIn("shell_ui_contract", first)
        self.assertIn("shell_ui_contract_manifest", first)
        self.assertIn("shell_ui_contract_manifest_fingerprints", first)
        self.assertIn("terminal_artifact_cli_fallback_entrypoint_contract_manifest", first)
        self.assertIn("terminal_artifact_cli_fallback_route_contract_manifest", first)
        self.assertIn("terminal_artifact_cli_fallback_contract_manifest", first)
        self.assertEqual(first["shell_ui_contract"], first["shell_ui_contract_fingerprint"])
        self.assertEqual(
            first["shell_ui_contract_manifest"],
            first["shell_ui_contract_manifest_fingerprint"],
        )
        self.assertEqual(
            first["shell_ui_contract_manifest_fingerprints"],
            first["shell_ui_contract_manifest_fingerprints_fingerprint"],
        )

    def test_a2ui_fingerprint_snapshots_do_not_leak_mutations_between_calls(self) -> None:
        first = describe_a2ui_contract_fingerprints(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )
        first["shell_ui_contract"] = "mutated"
        first["contract"] = "mutated"

        second = describe_a2ui_contract_fingerprints(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )

        self.assertNotEqual(first["shell_ui_contract"], second["shell_ui_contract"])
        self.assertNotEqual(first["contract"], second["contract"])
        self.assertEqual(
            second["shell_ui_contract"],
            second["shell_ui_contract_fingerprint"],
        )
        self.assertEqual(
            second["contract"],
            describe_a2ui_contract(
                include_shell_ui_contract=True,
                include_contract_aliases=True,
            )["contract_fingerprint"],
        )

    def test_shell_ui_contract_exposes_the_cli_fallback_wrapper_manifest_by_default(self) -> None:
        shell_contract = describe_shell_ui_contract()
        cli_fallback_contract = describe_terminal_artifact_cli_fallback_contract()
        a2ui_shell_contract = describe_a2ui_contract(include_shell_ui_contract=True)["shell_ui_contract"]

        self.assertEqual(shell_contract["terminal_artifact_cli_fallback_contract_manifest"], cli_fallback_contract)
        self.assertEqual(a2ui_shell_contract["terminal_artifact_cli_fallback_contract_manifest"], cli_fallback_contract)
        self.assertEqual(
            shell_contract["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            cli_fallback_contract["contract_fingerprint"],
        )
        self.assertEqual(
            shell_contract["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints"],
            shell_contract["terminal_artifact_cli_fallback_target_contract_fingerprints"],
        )
        self.assertEqual(
            a2ui_shell_contract["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints"],
            a2ui_shell_contract["terminal_artifact_cli_fallback_target_contract_fingerprints"],
        )
        self.assertEqual(
            a2ui_shell_contract["shell_ui_contract_manifest_fingerprints"],
            a2ui_shell_contract["shell_ui_contract_fingerprints"],
        )

    def test_shell_ui_fingerprint_snapshots_do_not_leak_mutations_between_calls(self) -> None:
        first = describe_shell_ui_contract_fingerprints(include_contract_aliases=True)
        first["shell_ui_contract"] = "mutated"
        first["terminal_artifact_cli_fallback_contract_manifest"] = "mutated"

        second = describe_shell_ui_contract_fingerprints(include_contract_aliases=True)

        self.assertNotEqual(first["shell_ui_contract"], second["shell_ui_contract"])
        self.assertNotEqual(
            first["terminal_artifact_cli_fallback_contract_manifest"],
            second["terminal_artifact_cli_fallback_contract_manifest"],
        )
        self.assertEqual(
            second["shell_ui_contract"],
            second["shell_ui_contract_fingerprint"],
        )

    def test_shell_ui_contract_manifest_fingerprint_aliases_match_the_base_fingerprints(self) -> None:
        manifest_fingerprints = describe_shell_ui_contract_manifest_fingerprints(include_contract_aliases=True)
        base_fingerprints = describe_shell_ui_contract_fingerprints(include_contract_aliases=True)

        self.assertEqual(manifest_fingerprints, base_fingerprints)
        self.assertEqual(
            shell_ui_contract_manifest_fingerprints_fingerprint(include_contract_aliases=True),
            _fingerprint_manifest_section(base_fingerprints),
        )
        manifest = describe_shell_ui_contract(include_contract_aliases=True)
        self.assertEqual(
            manifest["shell_ui_contract_manifest_fingerprints"],
            base_fingerprints,
        )
        self.assertEqual(
            manifest["shell_ui_contract_manifest_fingerprints_fingerprint"],
            _fingerprint_manifest_section(base_fingerprints),
        )

    def test_a2ui_contract_exposes_leaf_contract_manifest_aliases(self) -> None:
        manifest = describe_a2ui_contract()
        fingerprints = describe_a2ui_contract_fingerprints(include_contract_aliases=True)
        action_contract = describe_action_contract()
        selection_contract = describe_selection_contract()

        self.assertEqual(manifest["action_contract_manifest"], action_contract)
        self.assertEqual(
            manifest["action_contract_manifest_fingerprint"],
            action_contract["contract_fingerprint"],
        )
        self.assertEqual(manifest["selection_contract_manifest"], selection_contract)
        self.assertEqual(
            manifest["selection_contract_manifest_fingerprint"],
            selection_contract["contract_fingerprint"],
        )
        self.assertEqual(fingerprints["action_contract"], action_contract["contract_fingerprint"])
        self.assertEqual(
            fingerprints["action_contract_fingerprint"],
            action_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["action_contract_manifest"],
            action_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["action_contract_manifest_fingerprint"],
            action_contract["contract_fingerprint"],
        )
        self.assertEqual(fingerprints["selection_contract"], selection_contract["contract_fingerprint"])
        self.assertEqual(
            fingerprints["selection_contract_fingerprint"],
            selection_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["selection_contract_manifest"],
            selection_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["selection_contract_manifest_fingerprint"],
            selection_contract["contract_fingerprint"],
        )

    def test_a2ui_engine_contract_aliases_the_engine_facing_slice(self) -> None:
        default_fingerprints = describe_a2ui_contract_fingerprints(include_contract_aliases=True)
        shell_fingerprints = describe_a2ui_contract_fingerprints(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )
        default_engine_fingerprint = a2ui_engine_contract_fingerprint()
        shell_engine_fingerprint = a2ui_engine_contract_fingerprint(include_shell_ui_contract=True)

        self.assertEqual(
            default_fingerprints["a2ui_engine_contract"],
            default_engine_fingerprint,
        )
        self.assertEqual(
            default_fingerprints["a2ui_engine_contract_fingerprint"],
            default_engine_fingerprint,
        )
        self.assertEqual(
            default_fingerprints["a2ui_engine_contract_manifest"],
            default_engine_fingerprint,
        )
        self.assertEqual(
            default_fingerprints["a2ui_engine_contract_manifest_fingerprint"],
            default_engine_fingerprint,
        )
        self.assertEqual(
            shell_fingerprints["a2ui_engine_contract"],
            shell_engine_fingerprint,
        )
        self.assertEqual(
            shell_fingerprints["a2ui_engine_contract_fingerprint"],
            shell_engine_fingerprint,
        )
        self.assertEqual(
            shell_fingerprints["a2ui_engine_contract_manifest"],
            shell_engine_fingerprint,
        )
        self.assertEqual(
            shell_fingerprints["a2ui_engine_contract_manifest_fingerprint"],
            shell_engine_fingerprint,
        )

    def test_a2ui_engine_contract_can_opt_in_to_terminal_artifact_cli_fallback_card_hint_recovery_policy_slice(self) -> None:
        engine_manifest = describe_a2ui_engine_contract(
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True,
        )
        engine_fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact=True,
            include_action=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_target=True,
            include_terminal_artifact_cli_fallback_route=True,
            include_terminal_artifact_cli_fallback_entrypoint=True,
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True,
        )
        policy_manifest = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
        engine_fingerprint = a2ui_engine_contract_fingerprint(
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True,
        )

        self.assertEqual(engine_manifest["card_hint_recovery_policy"], policy_manifest)
        self.assertEqual(
            engine_manifest["card_hint_recovery_policy_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["card_hint_recovery_policy_contract"],
            policy_manifest,
        )
        self.assertEqual(
            engine_manifest["card_hint_recovery_policy_contract_manifest"],
            policy_manifest,
        )
        self.assertEqual(
            engine_manifest["card_hint_recovery_policy_contract_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["card_hint_recovery_policy_contract_manifest_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["contract_fingerprints"]["card_hint_recovery_policy"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract_manifest"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract_manifest_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            engine_manifest["contract_fingerprints"],
            engine_fingerprints,
        )
        self.assertEqual(
            engine_manifest["contract_fingerprint"],
            engine_fingerprint,
        )

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

    def test_a2ui_capabilities_normalize_to_canonical_snapshots(self) -> None:
        capabilities = A2UICapabilities(
            a2ui_version=1,
            client_name="  Exegesis Studio  ",
            cards_supported=("RunLogCard", "EvidenceCard"),
            primitive_blocks_supported=(
                "ProgressBlock",
                "MarkdownBlock",
                "TableBlock",
                "KeyValueBlock",
                "ListBlock",
                "CodeBlock",
                "AlertBlock",
            ),
            actions_supported=("copy_to_clipboard", "export_document", "apply_patch"),
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )

        normalized = normalize_capabilities(capabilities)
        store = A2UISessionStore()
        store.register("session-1", capabilities)
        stored = store.get("session-1")

        from src.qual.ui import normalize_capabilities as exported_normalize_capabilities

        self.assertIs(exported_normalize_capabilities, normalize_capabilities)
        self.assertEqual(capabilities.client_name, "  Exegesis Studio  ")
        self.assertEqual(normalized.client_name, "Exegesis Studio")
        self.assertEqual(normalized.cards_supported, ("EvidenceCard", "RunLogCard"))
        self.assertEqual(
            normalized.primitive_blocks_supported,
            (
                "MarkdownBlock",
                "KeyValueBlock",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
        )
        self.assertEqual(
            normalized.actions_supported,
            ("apply_patch", "export_document", "copy_to_clipboard"),
        )
        self.assertEqual(stored, normalized)
        self.assertIsNot(stored, capabilities)

    def test_terminal_artifact_cli_fallback_target_contract_is_versioned_and_fingerprintable(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_target_contract()
        manifest_alias = describe_terminal_artifact_cli_fallback_target_contract_manifest()
        manifest_fingerprints_alias = describe_terminal_artifact_cli_fallback_target_contract_manifest_fingerprints()
        manifest_alias_fingerprint = terminal_artifact_cli_fallback_target_contract_manifest_fingerprint()
        manifest_fingerprints_alias_fingerprint = (
            terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint()
        )
        render_target_contract = describe_terminal_artifact_render_target_contract()
        terminal_fallback_contract = describe_terminal_fallback_contract()
        raw_leaf_card_default_contract = describe_terminal_artifact_raw_leaf_card_default_contract()
        raw_leaf_card_default_policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        entrypoint_contract = describe_terminal_artifact_cli_fallback_entrypoint_contract()
        renderer_entrypoints_contract = describe_terminal_artifact_renderer_entrypoints_contract()
        aliased_fingerprints = describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
            include_contract_aliases=True,
        )

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
        )
        self.assertEqual(manifest["type"], "TerminalArtifactCliFallbackTargetContract")
        self.assertEqual(manifest["fallback_target_resolver"], "resolve_terminal_artifact_cli_fallback_target")
        self.assertEqual(manifest["fallback_renderer"], "ShellUI.render_artifact")
        self.assertEqual(manifest["allowed_actions"], sorted(ALLOWED_ACTION_IDS))
        self.assertEqual(manifest["terminal_artifact_cli_fallback_entrypoint"], "render_terminal_cli_fallback")
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"],
            "render_terminal_cli_fallback",
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            entrypoint_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(manifest["renderer_entrypoints"], _build_terminal_artifact_renderer_entrypoints())
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest"],
            renderer_entrypoints_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint(),
        )
        leaf_contracts = describe_a2ui_leaf_contracts()
        self.assertEqual(manifest["leaf_contracts"], leaf_contracts)
        self.assertEqual(manifest["leaf_contracts_contract"], leaf_contracts)
        self.assertEqual(manifest["leaf_contracts_contract_manifest"], leaf_contracts)
        self.assertEqual(manifest["leaf_contracts_fingerprint"], a2ui_leaf_contracts_fingerprint())
        self.assertEqual(
            manifest["leaf_contracts_contract_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            manifest["leaf_contracts_contract_manifest_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(
            manifest_alias_fingerprint,
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(manifest["supported_kinds"], list(TERMINAL_ARTIFACT_SUPPORTED_KINDS))
        self.assertEqual(manifest["default_kind"], TERMINAL_ARTIFACT_DEFAULT_KIND)
        self.assertTrue(manifest["preserve_raw_leaf_card_default"])
        self.assertEqual(manifest["raw_leaf_required_fields"], ["id", "label", "payload"])
        self.assertEqual(
            manifest["raw_leaf_hint_fields"],
            {
                "action": ["confirm", "policy_sensitive"],
                "selection": ["selected", "disabled"],
            },
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["renderer_entrypoints_contract"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["leaf_renderers"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )
        self.assertEqual(
            aliased_fingerprints["leaf_renderers"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )
        self.assertEqual(
            aliased_fingerprints["leaf_renderers_contract"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )
        self.assertEqual(
            aliased_fingerprints["leaf_renderers_contract_manifest"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )
        self.assertEqual(manifest["render_target_contract"], render_target_contract)
        self.assertEqual(manifest["terminal_artifact_render_target"], render_target_contract)
        self.assertEqual(manifest["terminal_artifact_render_target_contract"], render_target_contract)
        self.assertEqual(
            manifest["leaf_renderers"],
            {
                "card": "render_terminal_card",
                "action": "render_terminal_action",
                "selection": "render_terminal_selection",
            },
        )
        self.assertEqual(
            manifest["leaf_renderers_fingerprint"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )
        self.assertEqual(
            manifest["leaf_renderers_contract_fingerprint"],
            manifest["leaf_renderers_fingerprint"],
        )
        self.assertEqual(manifest["leaf_renderers_contract"], manifest["leaf_renderers"])
        self.assertEqual(manifest["leaf_renderers_contract_manifest"], manifest["leaf_renderers"])
        self.assertEqual(
            manifest["leaf_renderers_contract_manifest_fingerprint"],
            manifest["leaf_renderers_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"]["contract_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"][
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest"
            ],
            entrypoint_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"]["renderer_entrypoints"],
            manifest["renderer_entrypoints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            manifest_alias_fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints"],
            manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprints_fingerprint"],
            manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(manifest_fingerprints_alias, manifest["contract_fingerprints"])
        self.assertEqual(
            manifest_fingerprints_alias_fingerprint,
            manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(manifest["terminal_fallback_contract"], terminal_fallback_contract)
        self.assertEqual(manifest["terminal_artifact_supported_kinds"], list(TERMINAL_ARTIFACT_SUPPORTED_KINDS))
        self.assertEqual(
            manifest["terminal_artifact_supported_kinds_contract"],
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        )
        self.assertEqual(
            manifest["terminal_artifact_supported_kinds_contract_fingerprint"],
            _fingerprint_manifest_section(list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)),
        )
        self.assertEqual(manifest["raw_leaf_card_default_contract"], raw_leaf_card_default_contract)
        self.assertEqual(
            manifest["raw_leaf_card_default_policy_contract"],
            raw_leaf_card_default_policy_contract,
        )
        self.assertIsNot(manifest["render_target_contract"], render_target_contract)
        self.assertIsNot(manifest["terminal_artifact_render_target"], render_target_contract)
        self.assertIsNot(manifest["terminal_artifact_render_target_contract"], render_target_contract)
        self.assertIsNot(manifest["terminal_fallback_contract"], terminal_fallback_contract)
        self.assertIsNot(manifest["raw_leaf_card_default_contract"], raw_leaf_card_default_contract)
        self.assertIsNot(
            manifest["raw_leaf_card_default_policy_contract"],
            raw_leaf_card_default_policy_contract,
        )
        self.assertEqual(
            manifest["kind_resolution_fingerprint"],
            terminal_artifact_kind_resolution_fingerprint(),
        )
        self.assertEqual(
            manifest["fallback_recovery_fingerprint"],
            terminal_artifact_fallback_recovery_fingerprint(),
        )
        self.assertEqual(
            manifest["shell_refinement_policy"],
            {
                "preserve_raw_leaf_card_default": True,
                "invalid_kind_treated_as_absent": True,
                "refine_card_underflow": True,
            },
        )
        self.assertEqual(
            manifest["route_precedence"],
            [
                "shared_target_resolver",
                "shell_refinement",
                "render_terminal_action",
                "render_terminal_selection",
                "render_terminal_card",
            ],
        )
        self.assertEqual(
            manifest["kind_resolution"]["caller_kind_hint_policy"],
            {
                "invalid_kind_treated_as_absent": True,
                "typed_payload_kind_is_authoritative": True,
                "explicit_card_kind_blocks_leaf_recovery": True,
            },
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"]["leaf_renderers"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(manifest["contract_fingerprints"]),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)

    def test_terminal_artifact_renderer_entrypoints_contract_is_versioned_and_embedded_in_a2ui_contract(
        self,
    ) -> None:
        manifest = describe_terminal_artifact_renderer_entrypoints_contract()
        manifest_alias = describe_terminal_artifact_renderer_entrypoints_contract_manifest()
        rendering_manifest = describe_terminal_artifact_rendering_contract()
        cli_manifest = describe_terminal_artifact_cli_fallback_contract()
        terminal_artifact_manifest = describe_terminal_artifact_contract()
        a2ui_manifest = describe_a2ui_contract()
        rendering_fingerprints = describe_terminal_artifact_rendering_contract_fingerprints(
            include_contract_aliases=True,
        )
        cli_fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints(
            include_contract_aliases=True,
        )
        a2ui_fingerprints = describe_a2ui_contract_fingerprints(include_contract_aliases=True)
        fingerprint = terminal_artifact_renderer_entrypoints_contract_fingerprint()
        alias_fingerprint = terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint()
        renderer_entrypoints = _build_terminal_artifact_renderer_entrypoints()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_schema_version"],
            TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_version"],
            TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
        )
        self.assertEqual(manifest["type"], "TerminalArtifactRendererEntrypointsContract")
        self.assertEqual(manifest["renderer_entrypoints"], renderer_entrypoints)
        self.assertEqual(manifest["renderer_entrypoints_contract"], renderer_entrypoints)
        self.assertEqual(
            manifest["renderer_entrypoints_fingerprint"],
            _fingerprint_manifest_section(manifest["renderer_entrypoints"]),
        )
        self.assertEqual(manifest["renderer_entrypoints_contract_fingerprint"], fingerprint)
        self.assertEqual(
            manifest["renderer_entrypoints_contract_manifest"]["renderer_entrypoints_contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["renderer_entrypoints_contract_manifest_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest"]["contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract"]["contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(alias_fingerprint, fingerprint)
        self.assertEqual(manifest["contract_fingerprint"], fingerprint)
        self.assertEqual(
            manifest["contract_fingerprints"],
            {"renderer_entrypoints": manifest["renderer_entrypoints_fingerprint"]},
        )
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["renderer_entrypoints"],
            manifest["renderer_entrypoints_fingerprint"],
        )
        self.assertEqual(
            describe_terminal_artifact_renderer_entrypoints_contract_fingerprints(),
            manifest["contract_fingerprints"],
        )
        aliased_fingerprints = describe_terminal_artifact_renderer_entrypoints_contract_fingerprints(
            include_contract_aliases=True,
        )
        self.assertEqual(
            aliased_fingerprints["renderer_entrypoints_contract"],
            fingerprint,
        )
        self.assertEqual(
            aliased_fingerprints["renderer_entrypoints_contract_manifest"],
            fingerprint,
        )
        self.assertEqual(
            aliased_fingerprints["renderer_entrypoints_contract_manifest_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            fingerprint,
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_renderer_entrypoints_contract"],
            fingerprint,
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            terminal_artifact_renderer_entrypoints_contract_fingerprints_fingerprint(
                include_contract_aliases=True,
            ),
            _fingerprint_manifest_section(aliased_fingerprints),
        )
        self.assertEqual(rendering_manifest["renderer_entrypoints_contract"], manifest)
        self.assertEqual(rendering_manifest["renderer_entrypoints_contract_fingerprint"], fingerprint)
        self.assertEqual(cli_manifest["renderer_entrypoints_contract"], manifest)
        self.assertEqual(cli_manifest["renderer_entrypoints_contract_fingerprint"], fingerprint)
        self.assertEqual(terminal_artifact_manifest["renderer_entrypoints_contract"], manifest)
        self.assertEqual(
            terminal_artifact_manifest["renderer_entrypoints_contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(a2ui_manifest["renderer_entrypoints_contract"], manifest)
        self.assertEqual(a2ui_manifest["renderer_entrypoints_contract_fingerprint"], fingerprint)
        self.assertEqual(rendering_fingerprints["renderer_entrypoints_contract"], fingerprint)
        self.assertEqual(
            rendering_fingerprints["renderer_entrypoints_contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(cli_fingerprints["renderer_entrypoints_contract"], fingerprint)
        self.assertEqual(cli_fingerprints["renderer_entrypoints_contract_fingerprint"], fingerprint)
        self.assertEqual(a2ui_fingerprints["renderer_entrypoints_contract"], fingerprint)
        self.assertEqual(a2ui_fingerprints["renderer_entrypoints_contract_fingerprint"], fingerprint)
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_renderer_entrypoints"],
            fingerprint,
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_renderer_entrypoints_contract"],
            fingerprint,
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            fingerprint,
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            fingerprint,
        )

    def test_terminal_artifact_cli_fallback_entrypoint_contract_is_versioned_and_fingerprintable(
        self,
    ) -> None:
        manifest = describe_terminal_artifact_cli_fallback_entrypoint_contract()
        fingerprint = terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
        contract_fingerprints = describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints()
        shell_policy_contract = describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract()
        resolver_policy_contract = describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(
            manifest["schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_schema_version"],
            TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION,
        )
        self.assertEqual(manifest["type"], "TerminalArtifactCliFallbackEntrypointContract")
        self.assertEqual(manifest["terminal_artifact_cli_fallback_entrypoint"], "render_terminal_cli_fallback")
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"],
            "render_terminal_cli_fallback",
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"]["contract_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["contract_manifest"],
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
        )
        self.assertEqual(manifest["contract_manifest_fingerprint"], fingerprint)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            contract_fingerprints["card_hint_recovery_policy_contract"],
            manifest["card_hint_recovery_policy_fingerprint"],
        )
        self.assertEqual(
            contract_fingerprints["card_hint_recovery_policy_contract_manifest"],
            manifest["card_hint_recovery_policy_fingerprint"],
        )
        self.assertEqual(
            manifest["renderer_entrypoints_contract"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_contract_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_shell_refinement_policy"],
            shell_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_shell_refinement_policy_fingerprint"],
            terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_shell_refinement_policy_contract"],
            shell_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest"],
            shell_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_resolver_failure_policy"],
            resolver_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_resolver_failure_policy_fingerprint"],
            terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_resolver_failure_policy_contract"],
            resolver_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest"],
            resolver_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy"],
            {
                "recover_typed_leaf_mappings": True,
                "recover_typed_leaf_payloads": True,
                "explicit_leaf_instances_rejected_under_card_hints": True,
                "preserve_raw_leaf_card_default": True,
            },
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_fingerprint"],
            _fingerprint_manifest_section(manifest["card_hint_recovery_policy"]),
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract"],
            describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract(),
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest"],
            describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract(),
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_fingerprint"],
            terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            contract_fingerprints,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            contract_fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            contract_fingerprints["renderer_entrypoints"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            contract_fingerprints["renderer_entrypoints_contract"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            contract_fingerprints["renderer_entrypoints_contract_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            contract_fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            contract_fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            contract_fingerprints["card_hint_recovery_policy"],
            _fingerprint_manifest_section(manifest["card_hint_recovery_policy"]),
        )
        self.assertEqual(
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
            _fingerprint_manifest_section(contract_fingerprints),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["renderer_entrypoints"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(manifest["contract_fingerprints"]),
        )
        self.assertEqual(manifest["contract_fingerprint"], fingerprint)
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)

    def test_terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint_alias_matches_contract(
        self,
    ) -> None:
        manifest = describe_terminal_artifact_cli_fallback_entrypoint_contract()
        fingerprint = terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
        manifest_fingerprint = terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint()
        manifest_alias = describe_terminal_artifact_cli_fallback_entrypoint_contract_manifest()

        self.assertEqual(manifest["contract_fingerprint"], fingerprint)
        self.assertEqual(manifest_fingerprint, fingerprint)
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(
            manifest["renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"]["contract_fingerprint"],
            fingerprint,
        )

    def test_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_include_self_describing_aliases(
        self,
    ) -> None:
        fingerprints = describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints(
            include_contract_aliases=True,
        )
        entrypoint_fingerprint = terminal_artifact_cli_fallback_entrypoint_contract_fingerprint()
        renderer_entrypoints_fingerprint = terminal_artifact_renderer_entrypoints_contract_fingerprint()
        shell_policy_contract = describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract()
        resolver_policy_contract = describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract()

        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
            entrypoint_fingerprint,
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            entrypoint_fingerprint,
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            entrypoint_fingerprint,
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            entrypoint_fingerprint,
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints["renderer_entrypoints_contract_manifest"],
            renderer_entrypoints_fingerprint,
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            renderer_entrypoints_fingerprint,
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            renderer_entrypoints_fingerprint,
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy"],
            shell_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy"],
            resolver_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy_contract"],
            shell_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy_contract_manifest"],
            shell_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy_contract"],
            resolver_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy_contract_manifest"],
            resolver_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy"],
            _fingerprint_manifest_section(
                {
                    "recover_typed_leaf_mappings": True,
                    "recover_typed_leaf_payloads": True,
                    "explicit_leaf_instances_rejected_under_card_hints": True,
                    "preserve_raw_leaf_card_default": True,
                }
            ),
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy_contract_fingerprint"],
            shell_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy_contract_manifest_fingerprint"],
            shell_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy_contract_fingerprint"],
            resolver_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy_contract_manifest_fingerprint"],
            resolver_policy_contract["contract_fingerprint"],
        )
        self.assertEqual(
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(
                include_contract_aliases=True,
            ),
            _fingerprint_manifest_section(fingerprints),
        )

    def test_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_is_public_and_canonical(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()
        fingerprint = terminal_artifact_cli_fallback_card_hint_recovery_policy_contract_fingerprint()

        self.assertTrue(manifest["recover_typed_leaf_mappings"])
        self.assertTrue(manifest["recover_typed_leaf_payloads"])
        self.assertTrue(manifest["explicit_leaf_instances_rejected_under_card_hints"])
        self.assertTrue(manifest["preserve_raw_leaf_card_default"])
        self.assertEqual(manifest["card_hint_recovery_policy_fingerprint"], fingerprint)
        self.assertEqual(manifest["card_hint_recovery_policy_contract_fingerprint"], fingerprint)
        self.assertEqual(manifest["contract_fingerprint"], fingerprint)

    def test_terminal_artifact_cli_fallback_resolver_failure_policy_contract_is_public_and_canonical(
        self,
    ) -> None:
        manifest = describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract()
        manifest_alias = describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest()
        fingerprint = terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint()
        manifest_fingerprint = terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint()

        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(manifest["resolver_failure_policy_fingerprint"], fingerprint)
        self.assertEqual(manifest["resolver_failure_policy_contract_fingerprint"], fingerprint)
        self.assertEqual(manifest["contract_fingerprint"], fingerprint)
        self.assertEqual(manifest_fingerprint, fingerprint)

    def test_a2ui_contract_can_opt_into_terminal_artifact_cli_fallback_entrypoint_contract_slice(self) -> None:
        default_manifest = describe_a2ui_contract()
        default_fingerprints = describe_a2ui_contract_fingerprints()
        manifest = describe_a2ui_contract(include_terminal_artifact_cli_fallback_entrypoint=True)
        fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact_cli_fallback_entrypoint=True,
        )
        entrypoint_manifest = describe_terminal_artifact_cli_fallback_entrypoint_contract()
        cli_fallback_manifest = describe_terminal_artifact_cli_fallback_contract()
        target_manifest = describe_terminal_artifact_cli_fallback_target_contract()
        entrypoint_fingerprints = describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints()
        shell_policy_manifest = describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract()
        resolver_policy_manifest = describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract()

        self.assertNotIn("terminal_artifact_cli_fallback_entrypoint_contract", default_manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_entrypoint", default_fingerprints)
        self.assertNotIn("terminal_artifact_cli_fallback", default_fingerprints)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint"],
            "render_terminal_cli_fallback",
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback"], cli_fallback_manifest)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_contract"], cli_fallback_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"]["schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"]["version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_fingerprint"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_fingerprint"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_manifest"],
            cli_fallback_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"],
            entrypoint_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            entrypoint_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_renderer_entrypoints_contract_manifest"
            ],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            entrypoint_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            target_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            target_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_shell_refinement_policy"
            ],
            shell_policy_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_shell_refinement_policy_contract"
            ],
            shell_policy_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest"
            ],
            shell_policy_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_shell_refinement_policy_contract_manifest_fingerprint"
            ],
            terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_resolver_failure_policy"
            ],
            resolver_policy_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_resolver_failure_policy_contract"
            ],
            resolver_policy_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest"
            ],
            resolver_policy_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"][
                "terminal_artifact_cli_fallback_resolver_failure_policy_contract_manifest_fingerprint"
            ],
            terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            entrypoint_fingerprints,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_fingerprint"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract_fingerprint"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract_manifest"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            cli_fallback_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            entrypoint_manifest["terminal_artifact_renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            entrypoint_fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy"],
            shell_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy_contract"],
            shell_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy_contract_manifest"],
            shell_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy"],
            resolver_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy_contract"],
            resolver_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy_contract_manifest"],
            resolver_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )

    def test_terminal_artifact_cli_fallback_target_contract_can_opt_into_route_contract(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=True,
        )
        route_manifest = describe_terminal_artifact_cli_fallback_route_contract()

        self.assertEqual(manifest["terminal_artifact_cli_fallback_route"], route_manifest)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route_contract"], route_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_fingerprint"],
            _fingerprint_manifest_section(manifest["renderer_entrypoints"]),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )

    def test_terminal_artifact_cli_fallback_route_contract_exposes_allowed_actions(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_route_contract()

        self.assertEqual(manifest["allowed_actions"], sorted(ALLOWED_ACTION_IDS))
        self.assertEqual(
            manifest["route_precedence"],
            [
                "shared_target_resolver",
                "shell_refinement",
                "render_terminal_action",
                "render_terminal_selection",
                "render_terminal_card",
            ],
        )
        self.assertEqual(manifest["route_precedence_contract"], manifest["route_precedence"])
        self.assertEqual(
            manifest["route_precedence_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["route_precedence"]),
        )
        self.assertEqual(
            manifest["leaf_renderers_contract"],
            {
                "card": "render_terminal_card",
                "action": "render_terminal_action",
                "selection": "render_terminal_selection",
            },
        )
        self.assertEqual(
            manifest["leaf_renderers_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["route_precedence"],
            _fingerprint_manifest_section(manifest["route_precedence"]),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["leaf_renderers"],
            _fingerprint_manifest_section(manifest["leaf_renderers"]),
        )

    def test_terminal_artifact_cli_fallback_route_contract_fingerprints_expose_route_sections(self) -> None:
        fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True,
            include_contract_aliases=True,
        )

        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["route_precedence"],
            _fingerprint_manifest_section([
                "shared_target_resolver",
                "shell_refinement",
                "render_terminal_action",
                "render_terminal_selection",
                "render_terminal_card",
            ]),
        )
        self.assertEqual(
            fingerprints["route_precedence_contract"],
            _fingerprint_manifest_section([
                "shared_target_resolver",
                "shell_refinement",
                "render_terminal_action",
                "render_terminal_selection",
                "render_terminal_card",
            ]),
        )
        self.assertEqual(
            fingerprints["leaf_renderers"],
            _fingerprint_manifest_section(
                {
                    "card": "render_terminal_card",
                    "action": "render_terminal_action",
                    "selection": "render_terminal_selection",
                }
            ),
        )
        self.assertEqual(
            fingerprints["leaf_renderers_contract"],
            _fingerprint_manifest_section(
                {
                    "card": "render_terminal_card",
                    "action": "render_terminal_action",
                    "selection": "render_terminal_selection",
                }
            ),
        )

    def test_terminal_artifact_cli_fallback_target_contract_fingerprints_are_public_and_canonical(
        self,
    ) -> None:
        manifest = describe_terminal_artifact_cli_fallback_target_contract()
        fingerprints = describe_terminal_artifact_cli_fallback_target_contract_fingerprints()
        fingerprints_with_self = describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
            include_terminal_artifact_cli_fallback_target=True,
            include_contract_aliases=True,
        )

        self.assertEqual(fingerprints, manifest["contract_fingerprints"])
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
        self.assertEqual(
            fingerprints["leaf_contracts"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints["kind_resolution"],
            terminal_artifact_kind_resolution_fingerprint(),
        )
        self.assertEqual(
            fingerprints["fallback_recovery"],
            terminal_artifact_fallback_recovery_fingerprint(),
        )
        self.assertEqual(
            fingerprints["kind_policy"],
            _fingerprint_manifest_section(manifest["kind_policy"]),
        )
        self.assertEqual(
            fingerprints["renderer_entrypoints_contract"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["kind_policy_contract"],
            _fingerprint_manifest_section(manifest["kind_policy"]),
        )
        self.assertEqual(
            fingerprints_with_self["kind_policy_contract_manifest"],
            _fingerprint_manifest_section(manifest["kind_policy"]),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_contract_manifest"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["contract_manifest"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_manifest"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )

    def test_terminal_artifact_cli_fallback_target_contract_exposes_raw_leaf_policy_contract_aliases(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_target_contract()
        policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()
        policy_contract_fingerprints = describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints()
        policy_contract_fingerprints_with_self = describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
            include_terminal_artifact_raw_leaf_card_default_policy=True,
        )

        self.assertEqual(manifest["raw_leaf_card_default_policy_contract"], policy_contract)
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            policy_contract,
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_policy_contract_fingerprints"],
            policy_contract_fingerprints,
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints"],
            policy_contract_fingerprints_with_self,
        )

    def test_a2ui_contract_fingerprints_can_opt_in_to_cli_fallback_target_contract(self) -> None:
        fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact_cli_fallback_target=True,
            include_contract_aliases=True,
        )

        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"][
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"
            ],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"]["renderer_entrypoints_contract"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"]["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(fingerprints["capabilities_contract"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(
            fingerprints["capabilities_contract_fingerprint"],
            a2ui_capabilities_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_render_target"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_render_target_contract_manifest"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )

    def test_a2ui_contract_manifest_exposes_action_contract_alias(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["capabilities"], describe_a2ui_capabilities_contract())
        self.assertEqual(manifest["capabilities"]["contract_fingerprint"], manifest["capabilities_fingerprint"])
        self.assertEqual(manifest["capabilities_fingerprint"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(manifest["capabilities"]["schema_version"], A2UI_CAPABILITIES_SCHEMA_VERSION)
        self.assertEqual(manifest["capabilities"]["capabilities_schema_version"], A2UI_CAPABILITIES_SCHEMA_VERSION)
        self.assertEqual(manifest["action"], describe_action_contract())
        self.assertEqual(manifest["action"]["contract_fingerprint"], manifest["action"]["action_fingerprint"])
        self.assertEqual(manifest["action_contract"], describe_action_contract())
        self.assertEqual(manifest["action_contract"]["contract_fingerprint"], manifest["action_contract_fingerprint"])
        self.assertEqual(manifest["action_contract_fingerprint"], action_contract_fingerprint())
        self.assertEqual(len(manifest["action"]["contract_fingerprint"]), 64)
        self.assertEqual(manifest["action_fingerprint"], action_contract_fingerprint())
        self.assertEqual(manifest["action"]["schema_version"], A2UI_ACTION_SCHEMA_VERSION)
        self.assertEqual(manifest["selection"], describe_selection_contract())
        self.assertEqual(manifest["selection"]["contract_fingerprint"], manifest["selection"]["selection_fingerprint"])
        self.assertEqual(manifest["selection_contract"], describe_selection_contract())
        self.assertEqual(
            manifest["selection_contract"]["contract_fingerprint"],
            manifest["selection_contract_fingerprint"],
        )
        self.assertEqual(manifest["selection_contract_fingerprint"], selection_contract_fingerprint())
        self.assertEqual(manifest["selection_fingerprint"], selection_contract_fingerprint())
        self.assertEqual(manifest["selection"]["schema_version"], SELECTION_SCHEMA_VERSION)
        self.assertEqual(manifest["terminal_artifact_contract"], describe_terminal_artifact_contract())
        self.assertEqual(
            manifest["terminal_artifact_contract"]["contract_fingerprint"],
            manifest["terminal_artifact_contract_fingerprint"],
        )
        self.assertEqual(manifest["terminal_artifact_contract_fingerprint"], terminal_artifact_contract_fingerprint())
        self.assertEqual(manifest["card_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["card_contract"]["schema_version"], CARD_CONTRACT_VERSION)
        self.assertEqual(
            manifest["schema_versions"],
            {
                "contract_version": 2,
                "a2ui_version": 1,
                "type": "A2UISchemaVersions",
                "capabilities_schema_version": A2UI_CAPABILITIES_SCHEMA_VERSION,
                "selection_schema_version": SELECTION_SCHEMA_VERSION,
                "selection_contract_version": SELECTION_SCHEMA_VERSION,
                "action_schema_version": A2UI_ACTION_SCHEMA_VERSION,
                "action_contract_version": A2UI_ACTION_SCHEMA_VERSION,
                "card_contract_version": CARD_CONTRACT_VERSION,
                "terminal_fallback_schema_version": 1,
                "terminal_artifact_schema_version": TERMINAL_ARTIFACT_SCHEMA_VERSION,
                "terminal_artifact_render_target_schema_version": TERMINAL_ARTIFACT_RENDER_TARGET_SCHEMA_VERSION,
                "terminal_artifact_renderer_entrypoints_schema_version": (
                    TERMINAL_ARTIFACT_RENDERER_ENTRYPOINTS_SCHEMA_VERSION
                ),
                "terminal_artifact_rendering_schema_version": TERMINAL_ARTIFACT_RENDERING_SCHEMA_VERSION,
                "terminal_artifact_cli_fallback_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_SCHEMA_VERSION,
                "terminal_artifact_cli_fallback_entrypoint_schema_version": (
                    TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION
                ),
                "terminal_artifact_cli_fallback_target_schema_version": TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_SCHEMA_VERSION,
                "terminal_artifact_raw_leaf_card_default_schema_version": TERMINAL_ARTIFACT_RAW_LEAF_CARD_DEFAULT_SCHEMA_VERSION,
            },
        )
        self.assertEqual(manifest["schema_versions"]["contract_version"], 2)
        self.assertEqual(manifest["schema_versions"]["a2ui_version"], 1)
        self.assertEqual(
            manifest["schema_versions_contract"],
            manifest["schema_versions"],
        )
        self.assertEqual(
            manifest["schema_versions_contract_fingerprint"],
            manifest["schema_versions_fingerprint"],
        )
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
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(manifest["terminal_artifact"], describe_terminal_artifact_contract())
        self.assertEqual(manifest["schemas"]["selection"], describe_selection_contract())
        self.assertEqual(manifest["schemas"]["terminal_artifact"], describe_terminal_artifact_contract())
        self.assertEqual(
            manifest["schemas"]["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertNotIn("terminal_artifact_cli_fallback_route", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_fingerprint", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract_fingerprint", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract_fingerprints", manifest)
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
                include_terminal_artifact_cli_fallback_target=True,
            ),
        )
        self.assertEqual(len(manifest["terminal_artifact"]["contract_fingerprint"]), 64)

    def test_a2ui_contract_manifest_exposes_capabilities_contract_alias(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["capabilities_contract"], describe_a2ui_capabilities_contract())
        self.assertEqual(
            manifest["capabilities_contract"]["contract_fingerprint"],
            manifest["capabilities_contract_fingerprint"],
        )
        self.assertEqual(manifest["capabilities_contract_fingerprint"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(manifest["capabilities"]["contract_fingerprint"], manifest["capabilities_contract_fingerprint"])

    def test_a2ui_contract_manifest_exposes_top_level_contract_alias(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertIsNot(manifest["a2ui_contract"], manifest)
        self.assertEqual(manifest["a2ui_contract"]["contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(manifest["a2ui_contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(manifest["a2ui_contract"]["contract_fingerprints"], manifest["contract_fingerprints"])
        self.assertIsNot(manifest["a2ui_contract"]["contract_fingerprints"], manifest["contract_fingerprints"])
        self.assertEqual(manifest["a2ui_contract"]["capabilities"], manifest["capabilities"])
        self.assertIsNot(manifest["a2ui_contract"]["capabilities"], manifest["capabilities"])

    def test_a2ui_contract_manifest_alias_sections_are_snapshot_isolated(self) -> None:
        manifest = describe_a2ui_contract()
        schema_versions_source = _build_a2ui_schema_versions_manifest()

        cases = [
            ("capabilities", manifest["schemas"]["capabilities"]),
            ("capabilities_contract", manifest["schemas"]["capabilities"]),
            ("card_contract", manifest["schemas"]["card_contract"]),
            ("action", manifest["schemas"]["action"]),
            ("selection", manifest["schemas"]["selection"]),
            ("schema_versions", schema_versions_source),
            ("schema_versions_contract", schema_versions_source),
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
                "terminal_artifact_cli_fallback_target_contract_fingerprints",
                manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target_contract_fingerprints"],
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
            (
                "terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints",
                describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                    include_terminal_artifact_raw_leaf_card_default_policy=True,
                ),
            ),
        ]

        for key, source in cases:
            with self.subTest(section=key):
                self.assertIsNot(manifest[key], source)
                self.assertEqual(manifest[key], source)

    def test_a2ui_contract_alias_sections_do_not_share_mutable_state(self) -> None:
        manifest = describe_a2ui_contract()
        routed_manifest = describe_a2ui_contract(include_terminal_artifact_cli_fallback_route=True)
        terminal_artifact_manifest = describe_terminal_artifact_contract()

        self.assertIsNot(manifest["action"], manifest["action_contract"])
        self.assertIsNot(manifest["selection"], manifest["selection_contract"])
        self.assertIsNot(manifest["capabilities"], manifest["capabilities_contract"])
        self.assertIsNot(manifest["schema_versions"], manifest["schema_versions_contract"])
        self.assertIsNot(manifest["terminal_fallback"], manifest["terminal_fallback_contract"])
        self.assertIsNot(manifest["terminal_artifact"], manifest["terminal_artifact_contract"])
        self.assertIsNot(
            manifest["terminal_artifact_cli_fallback_target"],
            manifest["terminal_artifact_cli_fallback_target_contract"],
        )
        self.assertNotIn("terminal_artifact_cli_fallback_route", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract_manifest", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_fingerprint", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract_fingerprint", manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract_fingerprints", manifest)
        self.assertIsNot(
            routed_manifest["terminal_artifact_cli_fallback_route"],
            routed_manifest["terminal_artifact_cli_fallback_route_contract"],
        )
        self.assertIsNot(
            routed_manifest["terminal_artifact_cli_fallback_route"],
            routed_manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
        )
        self.assertIsNot(
            routed_manifest["terminal_artifact_cli_fallback_route_contract"],
            routed_manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
        )
        self.assertIsNot(
            manifest["terminal_artifact_render_target"],
            manifest["terminal_artifact_render_target_contract"],
        )
        self.assertIsNot(
            manifest["terminal_artifact_envelope"],
            manifest["terminal_artifact_envelope_contract"],
        )
        self.assertIsNot(
            manifest["terminal_artifact_raw_leaf_card_default"],
            manifest["terminal_artifact_raw_leaf_card_default_contract"],
        )
        self.assertIsNot(
            manifest["terminal_artifact_raw_leaf_card_default_policy"],
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
        )
        self.assertIsNot(
            terminal_artifact_manifest["rendering"],
            terminal_artifact_manifest["terminal_artifact_rendering"],
        )
        self.assertIsNot(
            terminal_artifact_manifest["cli_fallback"],
            terminal_artifact_manifest["terminal_artifact_cli_fallback"],
        )
        self.assertIsNot(
            terminal_artifact_manifest["cli_fallback_contract"],
            terminal_artifact_manifest["terminal_artifact_cli_fallback_contract"],
        )
        self.assertIsNot(
            terminal_artifact_manifest["render_target_contract"],
            terminal_artifact_manifest["terminal_artifact_render_target_contract"],
        )

    def test_a2ui_contract_manifest_exposes_terminal_fallback_and_artifact_fingerprints(self) -> None:
        manifest = describe_a2ui_contract()
        cli_fallback_target_manifest = describe_terminal_artifact_cli_fallback_target_contract()

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
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target_contract"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(),
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
        self.assertEqual(manifest["terminal_artifact_cli_fallback_target"], cli_fallback_target_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(),
        )
        self.assertEqual(
            manifest["schemas"]["terminal_artifact_cli_fallback_target"],
            cli_fallback_target_manifest,
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
        raw_leaf_policy_contract = describe_terminal_artifact_raw_leaf_card_default_policy_contract()

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
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(manifest["terminal_artifact_raw_leaf_card_default_contract_fingerprints"]),
        )
        self.assertEqual(manifest["terminal_artifact"]["raw_leaf_card_default_contract"], raw_leaf_contract)
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy"],
            raw_leaf_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            raw_leaf_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            ),
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_raw_leaf_card_default_policy"],
            raw_leaf_policy_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact"]["terminal_artifact_raw_leaf_card_default_policy_contract"],
            raw_leaf_policy_contract,
        )
        self.assertIsNot(
            manifest["terminal_artifact_raw_leaf_card_default_policy"],
            manifest["terminal_artifact"]["terminal_artifact_raw_leaf_card_default_policy"],
        )

    def test_a2ui_contract_manifest_exposes_terminal_artifact_envelope_aliases(self) -> None:
        manifest = describe_a2ui_contract()
        envelope_contract = describe_terminal_artifact_envelope_contract()

        self.assertEqual(manifest["terminal_artifact_envelope"], envelope_contract)
        self.assertEqual(manifest["terminal_artifact_envelope_contract"], envelope_contract)
        self.assertEqual(
            manifest["terminal_artifact_envelope_fingerprint"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_envelope_contract_fingerprint"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(manifest["schemas"]["terminal_artifact_envelope"], envelope_contract)
        self.assertEqual(manifest["terminal_artifact"]["terminal_artifact_envelope_contract"], envelope_contract)

    def test_a2ui_contract_manifest_can_opt_into_cli_fallback_route_contract(self) -> None:
        default_manifest = describe_a2ui_contract()
        manifest = describe_a2ui_contract(include_terminal_artifact_cli_fallback_route=True)
        route_manifest = describe_terminal_artifact_cli_fallback_route_contract()
        terminal_artifact_manifest = describe_terminal_artifact_contract(
            include_terminal_artifact_cli_fallback_route=True,
        )
        fingerprints = describe_a2ui_contract_fingerprints(
            include_action=True,
            include_terminal_artifact=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_target=True,
            include_terminal_artifact_cli_fallback_route=True,
        )
        fingerprints_with_aliases = describe_a2ui_contract_fingerprints(
            include_action=True,
            include_terminal_artifact=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_target=True,
            include_terminal_artifact_cli_fallback_route=True,
            include_contract_aliases=True,
        )

        self.assertNotIn("terminal_artifact_cli_fallback_route", default_manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract", default_manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_fingerprint", default_manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract_fingerprint", default_manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract_fingerprints", default_manifest)
        self.assertEqual(manifest["terminal_artifact"], terminal_artifact_manifest)
        self.assertEqual(manifest["terminal_artifact_contract"], terminal_artifact_manifest)
        self.assertEqual(
            manifest["terminal_artifact_fingerprint"],
            terminal_artifact_contract_fingerprint(include_terminal_artifact_cli_fallback_route=True),
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route"], route_manifest)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route_contract"], route_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_fingerprint"],
            _fingerprint_manifest_section(manifest["renderer_entrypoints"]),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["schemas"]["terminal_artifact_cli_fallback_route"],
            route_manifest,
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            describe_a2ui_contract_fingerprints(
                include_action=True,
                include_terminal_artifact=True,
                include_terminal_artifact_render_target=True,
                include_terminal_artifact_rendering=True,
                include_terminal_artifact_cli_fallback=True,
                include_terminal_artifact_cli_fallback_target=True,
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_route_contract_manifest"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_route_contract"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(
                describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
                    include_terminal_artifact_cli_fallback_route=True,
                )
            ),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
        )

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
        self.assertNotIn("capabilities_contract", fingerprints)
        self.assertNotIn("a2ui_contract", fingerprints)
        self.assertEqual(fingerprints_with_aliases["capabilities_contract"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(
            fingerprints_with_aliases["contract_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(fingerprints_with_aliases["a2ui_contract"], manifest["contract_fingerprint"])
        self.assertEqual(
            fingerprints_with_aliases["a2ui_contract_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(fingerprints_with_aliases["card_fingerprint"], card_contract_fingerprint())
        self.assertEqual(fingerprints_with_aliases["card_contract_fingerprint"], card_contract_fingerprint())
        self.assertNotIn("card_contract_fingerprint_fingerprint", fingerprints_with_aliases)
        self.assertEqual(fingerprints_with_aliases["action_contract"], action_contract_fingerprint())
        self.assertEqual(fingerprints_with_aliases["selection_contract"], selection_contract_fingerprint())
        self.assertEqual(
            fingerprints_with_aliases["leaf_contracts_contract_manifest"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["leaf_contracts_contract_manifest_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["leaf_contracts_manifest"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["leaf_contracts_manifest_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(fingerprints_with_aliases["terminal_fallback_contract"], terminal_fallback_contract_fingerprint())
        self.assertEqual(fingerprints_with_aliases["terminal_artifact_contract"], terminal_artifact_contract_fingerprint())
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_envelope"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_envelope_contract"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_aliases["terminal_artifact_rendering_contract_manifest"],
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
            include_terminal_artifact_cli_fallback_target=True,
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
            fingerprints["terminal_artifact_envelope"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_envelope_contract"],
            terminal_artifact_envelope_contract_fingerprint(),
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
            fingerprints["renderer_entrypoints"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
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
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy"],
            _fingerprint_manifest_section(
                {
                    "recover_typed_leaf_mappings": True,
                    "recover_typed_leaf_payloads": True,
                    "explicit_leaf_instances_rejected_under_card_hints": True,
                    "preserve_raw_leaf_card_default": True,
                }
            ),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_contract_fingerprints"],
            _fingerprint_manifest_section(describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints()),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(describe_terminal_artifact_raw_leaf_card_default_contract_fingerprints()),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_policy"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(fingerprints["capabilities"], a2ui_capabilities_contract_fingerprint())
        self.assertEqual(
            describe_a2ui_contract()["contract_fingerprints"],
            manifest_fingerprints,
        )
        self.assertNotEqual(fingerprints, manifest_fingerprints)
        self.assertNotIn("action", describe_a2ui_contract_fingerprints())
        self.assertNotIn("action_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("selection_contract", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_render_target", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_rendering", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_cli_fallback", describe_a2ui_contract_fingerprints())
        self.assertNotIn("renderer_entrypoints", describe_a2ui_contract_fingerprints())
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
        self.assertNotIn(
            "terminal_artifact_raw_leaf_card_default_policy",
            describe_a2ui_contract_fingerprints(),
        )

    def test_a2ui_dispatch_contract_fingerprints_are_full_surface_and_route_aware(self) -> None:
        fingerprints = describe_a2ui_dispatch_contract_fingerprints()
        manifest = describe_a2ui_contract(include_terminal_artifact_cli_fallback_route=True)

        self.assertEqual(fingerprints, manifest["contract_fingerprints"])
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact"],
            terminal_artifact_contract_fingerprint(include_terminal_artifact_cli_fallback_route=True),
        )

    def test_a2ui_dispatch_contract_manifest_matches_route_aware_fingerprint_surface(self) -> None:
        from src.qual.ui import (
            a2ui_dispatch_contract_fingerprint as exported_dispatch_fingerprint,
            describe_a2ui_dispatch_contract as exported_dispatch_contract,
        )

        manifest = describe_a2ui_dispatch_contract()
        dispatch_fingerprints = describe_a2ui_dispatch_contract_fingerprints(
            include_terminal_artifact_cli_fallback_entrypoint=True,
        )

        self.assertIs(exported_dispatch_contract, describe_a2ui_dispatch_contract)
        self.assertIs(exported_dispatch_fingerprint, a2ui_dispatch_contract_fingerprint)
        self.assertEqual(manifest["dispatch_contract_fingerprints"], dispatch_fingerprints)
        self.assertEqual(
            manifest["dispatch_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(dispatch_fingerprints),
        )
        self.assertEqual(manifest["contract_fingerprint"], a2ui_dispatch_contract_fingerprint())
        self.assertEqual(
            manifest["dispatch_contract_fingerprint"],
            a2ui_dispatch_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact"],
            describe_terminal_artifact_contract(include_terminal_artifact_cli_fallback_route=True),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback"],
            describe_terminal_artifact_cli_fallback_contract(include_terminal_artifact_cli_fallback_route=True),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target"],
            describe_terminal_artifact_cli_fallback_target_contract(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route"],
            describe_terminal_artifact_cli_fallback_route_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"],
            describe_terminal_artifact_cli_fallback_entrypoint_contract(),
        )

    def test_a2ui_contract_can_opt_into_contract_aliases(self) -> None:
        manifest = describe_a2ui_contract(include_contract_aliases=True)
        engine_manifest = describe_a2ui_engine_contract(include_contract_aliases=True)
        fingerprints = describe_a2ui_contract_fingerprints(include_contract_aliases=True)

        self.assertIn("card_contract_manifest", manifest["contract_fingerprints"])
        self.assertIn("terminal_fallback_contract_manifest", manifest["contract_fingerprints"])
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(manifest["contract_fingerprints"]),
        )
        self.assertEqual(fingerprints["card_contract_manifest"], card_contract_fingerprint())
        self.assertEqual(
            fingerprints["terminal_fallback_contract_manifest"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["card_contract_manifest"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_fallback_contract_manifest"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            engine_manifest["contract_fingerprints"]["card_contract_manifest"],
            card_contract_fingerprint(),
        )

    def test_a2ui_contract_can_opt_in_to_shell_ui_contract_snapshot(self) -> None:
        default_manifest = describe_a2ui_contract()
        default_fingerprints = describe_a2ui_contract_fingerprints()
        shell_manifest = describe_shell_ui_contract()
        route_manifest = describe_terminal_artifact_cli_fallback_route_contract()
        target_manifest = describe_terminal_artifact_cli_fallback_target_contract()
        manifest = describe_a2ui_contract(include_shell_ui_contract=True)
        fingerprints = describe_a2ui_contract_fingerprints(include_shell_ui_contract=True)
        aliased_fingerprints = describe_a2ui_contract_fingerprints(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )
        aliased_manifest = describe_a2ui_contract(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )
        aliased_shell_manifest = describe_shell_ui_contract(include_contract_aliases=True)

        self.assertNotIn("shell_ui_contract", default_manifest)
        self.assertNotIn("shell_ui_contract_manifest", default_manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_entrypoint", default_manifest)
        self.assertNotIn("terminal_artifact_renderer_entrypoints_contract", default_manifest)
        self.assertNotIn("terminal_artifact_renderer_entrypoints_contract_manifest", default_manifest)
        self.assertNotIn("terminal_artifact_cli_fallback_contract_manifest", default_manifest)
        self.assertNotIn("shell_ui_contract_manifest", default_fingerprints)
        self.assertNotIn("terminal_artifact_renderer_entrypoints", default_fingerprints)
        self.assertNotIn("terminal_artifact_renderer_entrypoints_contract_manifest", default_fingerprints)
        self.assertNotIn("terminal_artifact_cli_fallback_target_contract_manifest", default_fingerprints)
        self.assertNotIn("terminal_artifact_cli_fallback_contract_manifest", default_fingerprints)
        self.assertEqual(
            default_manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(default_manifest["contract_fingerprints"]),
        )
        self.assertEqual(
            default_manifest["contract_fingerprints_contract"],
            default_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            default_manifest["contract_fingerprints_contract_fingerprint"],
            default_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(manifest["shell_ui_contract"], shell_manifest)
        self.assertEqual(
            manifest["shell_ui_contract_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract_fingerprints_fingerprint"],
            shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract"],
            shell_manifest["terminal_artifact_renderer_entrypoints_contract"],
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
            shell_manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"],
            target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            target_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            target_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_manifest"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route"],
            route_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract"],
            route_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_fingerprint"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_fingerprints["renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["shell_ui_contract_manifest"],
            shell_manifest,
        )
        self.assertEqual(
            manifest["shell_ui_contract_manifest_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest,
        )
        self.assertEqual(
            aliased_shell_manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest,
        )
        self.assertEqual(
            aliased_shell_manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_rendering_contract_manifest"],
            describe_terminal_artifact_rendering_contract(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_rendering_contract_manifest_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            describe_terminal_artifact_cli_fallback_entrypoint_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint"],
            shell_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract"],
            shell_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            shell_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            shell_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
        )
        self.assertEqual(
            manifest["shell_ui_contract_fingerprints"],
            shell_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract_fingerprints"]["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy"],
            shell_manifest["card_hint_recovery_policy"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_fingerprint"],
            shell_manifest["card_hint_recovery_policy_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract"],
            shell_manifest["card_hint_recovery_policy_contract"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_fingerprint"],
            shell_manifest["card_hint_recovery_policy_contract_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest"],
            shell_manifest["card_hint_recovery_policy_contract_manifest"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest_fingerprint"],
            shell_manifest["card_hint_recovery_policy_contract_manifest_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract_fingerprints"]["shell_ui_contract_manifest"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints_contract"],
            manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["contract_fingerprints_contract_fingerprint"],
            manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["shell_ui_contract_fingerprints"],
            shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_target_contract_manifest"],
            target_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract_fingerprints"][
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest"
            ],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"][
                "terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"
            ],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_manifest["terminal_artifact_cli_fallback_contract_manifest"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            aliased_manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_contract_manifest"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["shell_ui_contract"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["shell_ui_contract_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["shell_ui_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["shell_ui_contract_fingerprints_fingerprint"],
            shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["shell_ui_contract_manifest"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["shell_ui_contract"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_contract_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_contract_manifest"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_contract_manifest_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints"],
            shell_manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract"],
            shell_manifest["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy"],
            shell_manifest["contract_fingerprints"]["card_hint_recovery_policy"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract"],
            shell_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract_fingerprint"],
            shell_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract_manifest"],
            shell_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract_manifest"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract_manifest_fingerprint"],
            shell_manifest["contract_fingerprints"]["card_hint_recovery_policy_contract_manifest_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"],
            target_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_contract_fingerprints_fingerprint"],
            shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_contract_fingerprints"],
            shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_fingerprint"],
            aliased_shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_manifest"],
            aliased_shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_fingerprint"],
            aliased_shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_fingerprints"],
            aliased_shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
            shell_manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["card_hint_recovery_policy"],
            shell_manifest["contract_fingerprints"]["card_hint_recovery_policy"],
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_route"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_route_contract"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_route"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_route_contract"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprint"],
            a2ui_contract_fingerprint(include_shell_ui_contract=True),
        )
        self.assertEqual(aliased_manifest["shell_ui_contract"], aliased_shell_manifest)
        self.assertEqual(aliased_manifest["shell_ui_contract_manifest"], aliased_shell_manifest)
        self.assertEqual(
            aliased_manifest["shell_ui_contract"]["card_contract_manifest"],
            describe_card_contract(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract"]["card_contract_manifest_fingerprint"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract"]["terminal_fallback_contract_manifest"],
            describe_terminal_fallback_contract(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract"]["terminal_fallback_contract_manifest_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract_manifest"]["card_contract_manifest"],
            describe_card_contract(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract_manifest"]["terminal_fallback_contract_manifest"],
            describe_terminal_fallback_contract(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract_fingerprints"]["card_contract_manifest"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_manifest["shell_ui_contract_fingerprints"]["terminal_fallback_contract_manifest"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract"],
            aliased_shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_fingerprint"],
            aliased_shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_manifest"],
            aliased_shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_manifest_fingerprint"],
            aliased_shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_fingerprints"],
            aliased_shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_fingerprints_fingerprint"],
            aliased_shell_manifest["contract_fingerprints_fingerprint"],
        )

    def test_a2ui_contract_can_opt_in_to_terminal_artifact_cli_fallback_card_hint_recovery_policy_slice(self) -> None:
        default_manifest = describe_a2ui_contract()
        default_fingerprints = describe_a2ui_contract_fingerprints()
        manifest = describe_a2ui_contract(
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True,
        )
        fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact=True,
            include_action=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_target=True,
            include_terminal_artifact_cli_fallback_card_hint_recovery_policy=True,
        )
        policy_manifest = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()

        self.assertNotIn("card_hint_recovery_policy", default_manifest)
        self.assertNotIn("card_hint_recovery_policy", default_fingerprints)
        self.assertEqual(manifest["card_hint_recovery_policy"], policy_manifest)
        self.assertEqual(
            manifest["card_hint_recovery_policy_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract"],
            policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest"],
            policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract_manifest"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract_manifest_fingerprint"],
            policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            fingerprints,
        )

    def test_a2ui_contract_fingerprint_can_opt_into_terminal_artifact_cli_fallback_entrypoint_slice(self) -> None:
        manifest = describe_a2ui_contract(include_terminal_artifact_cli_fallback_entrypoint=True)
        fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact_cli_fallback_entrypoint=True,
        )

        self.assertEqual(
            a2ui_contract_fingerprint(include_terminal_artifact_cli_fallback_entrypoint=True),
            manifest["contract_fingerprint"],
        )
        self.assertEqual(fingerprints["contract"], manifest["contract_fingerprint"])
        self.assertEqual(
            fingerprints["contract"],
            a2ui_contract_fingerprint(include_terminal_artifact_cli_fallback_entrypoint=True),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )

    def test_a2ui_dispatch_contract_fingerprints_can_opt_into_shell_ui_contract_snapshot(self) -> None:
        shell_manifest = describe_shell_ui_contract(include_terminal_artifact_cli_fallback_route=True)
        manifest = describe_a2ui_contract(
            include_terminal_artifact_cli_fallback_route=True,
            include_shell_ui_contract=True,
        )
        fingerprints = describe_a2ui_dispatch_contract_fingerprints(include_shell_ui_contract=True)

        self.assertEqual(fingerprints, manifest["contract_fingerprints"])
        self.assertEqual(
            fingerprints["shell_ui_contract"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_contract_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_contract_manifest"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            fingerprints["shell_ui_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"],
            shell_manifest,
        )
        self.assertEqual(
            manifest["shell_ui_contract_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_fingerprint"],
            shell_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract_fingerprints_fingerprint"],
            shell_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )

    def test_a2ui_dispatch_contract_fingerprints_can_opt_into_terminal_artifact_cli_fallback_entrypoint_contract_slice(
        self,
    ) -> None:
        default_fingerprints = describe_a2ui_dispatch_contract_fingerprints()
        fingerprints = describe_a2ui_dispatch_contract_fingerprints(
            include_terminal_artifact_cli_fallback_entrypoint=True,
        )
        manifest = describe_a2ui_contract(
            include_terminal_artifact_cli_fallback_route=True,
            include_terminal_artifact_cli_fallback_entrypoint=True,
        )
        route_fingerprint = terminal_artifact_cli_fallback_route_contract_fingerprint()

        self.assertNotIn("terminal_artifact_cli_fallback_entrypoint", default_fingerprints)
        self.assertNotIn("terminal_artifact_cli_fallback_entrypoint_contract_manifest", default_fingerprints)
        self.assertEqual(
            default_fingerprints["terminal_artifact_cli_fallback_route"],
            route_fingerprint,
        )
        self.assertEqual(fingerprints["contract"], manifest["contract_fingerprint"])
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(fingerprints["terminal_artifact_cli_fallback_route"], route_fingerprint)

    def test_a2ui_dispatch_contract_fingerprints_can_opt_into_contract_aliases(self) -> None:
        default_fingerprints = describe_a2ui_dispatch_contract_fingerprints(
            include_shell_ui_contract=True,
        )
        aliased_fingerprints = describe_a2ui_dispatch_contract_fingerprints(
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )
        canonical_fingerprints = describe_a2ui_contract_fingerprints(
            include_action=True,
            include_terminal_artifact=True,
            include_terminal_artifact_render_target=True,
            include_terminal_artifact_rendering=True,
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_target=True,
            include_terminal_artifact_cli_fallback_route=True,
            include_shell_ui_contract=True,
            include_contract_aliases=True,
        )

        self.assertNotIn("contract_fingerprint", default_fingerprints)
        self.assertEqual(aliased_fingerprints, canonical_fingerprints)
        self.assertEqual(
            aliased_fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            aliased_fingerprints["shell_ui_contract_manifest"],
            shell_ui_contract_fingerprint(include_terminal_artifact_cli_fallback_route=True),
        )

    def test_a2ui_contract_fingerprint_map_can_opt_into_raw_leaf_card_default_dispatch(self) -> None:
        fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact_raw_leaf_card_default=True,
            include_terminal_artifact_raw_leaf_card_default_policy=True,
        )

        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_policy"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact_raw_leaf_card_default", describe_a2ui_contract_fingerprints())
        self.assertNotIn("terminal_artifact_raw_leaf_card_default_policy", describe_a2ui_contract_fingerprints())

    def test_terminal_artifact_contract_manifest_is_versioned_and_points_to_subcontracts(self) -> None:
        manifest = describe_terminal_artifact_contract()
        cli_fallback_target_manifest = describe_terminal_artifact_cli_fallback_target_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["type"], "TerminalArtifactContract")
        self.assertEqual(manifest["supported_kinds"], list(TERMINAL_ARTIFACT_SUPPORTED_KINDS))
        self.assertEqual(manifest["default_kind"], TERMINAL_ARTIFACT_DEFAULT_KIND)
        self.assertEqual(manifest["kind_contracts"]["card"]["contract_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["kind_contracts"]["action"]["contract_fingerprint"], action_contract_fingerprint())
        self.assertEqual(
            manifest["kind_contracts"]["selection"]["contract_fingerprint"],
            describe_selection_contract()["contract_fingerprint"],
        )
        self.assertEqual(manifest["card_contract"], manifest["kind_contracts"]["card"])
        self.assertEqual(manifest["action_contract"], manifest["kind_contracts"]["action"])
        self.assertEqual(manifest["selection_contract"], manifest["kind_contracts"]["selection"])
        self.assertEqual(manifest["card_contract_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["action_contract_fingerprint"], action_contract_fingerprint())
        self.assertEqual(manifest["selection_contract_fingerprint"], selection_contract_fingerprint())
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
        self.assertEqual(manifest["envelope"], describe_terminal_artifact_envelope_contract())
        self.assertEqual(manifest["terminal_artifact_envelope"], describe_terminal_artifact_envelope_contract())
        self.assertEqual(
            manifest["terminal_artifact_envelope_contract"],
            describe_terminal_artifact_envelope_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_envelope_fingerprint"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_envelope_contract_fingerprint"],
            terminal_artifact_envelope_contract_fingerprint(),
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
        self.assertEqual(manifest["terminal_artifact_cli_fallback_target"], cli_fallback_target_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            cli_fallback_target_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback"]["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            cli_fallback_target_manifest["contract_fingerprints"],
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

    def test_terminal_artifact_kind_contracts_manifest_is_versioned_and_fingerprintable(self) -> None:
        kind_contracts = describe_terminal_artifact_kind_contracts()
        manifest = describe_terminal_artifact_kind_contracts_manifest()
        fingerprint = terminal_artifact_kind_contracts_manifest_fingerprint()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], 1)
        self.assertEqual(manifest["terminal_artifact_kind_contracts_schema_version"], 1)
        self.assertEqual(manifest["terminal_artifact_kind_contracts_version"], 1)
        self.assertEqual(manifest["type"], "TerminalArtifactKindContractsContract")
        self.assertEqual(manifest["kind_contracts"], kind_contracts)
        self.assertEqual(manifest["terminal_artifact_kind_contracts"], kind_contracts)
        self.assertEqual(manifest["kind_contracts_fingerprint"], terminal_artifact_kind_contracts_fingerprint())
        self.assertEqual(
            manifest["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(manifest["contract_fingerprint"], fingerprint)
        self.assertEqual(manifest["contract_manifest"]["kind_contracts"], kind_contracts)
        self.assertEqual(manifest["contract_manifest"]["contract_fingerprint"], fingerprint)
        self.assertEqual(manifest["contract_manifest_fingerprint"], fingerprint)
        self.assertEqual(
            manifest["contract_fingerprints"]["kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(len(fingerprint), 64)

    def test_terminal_artifact_contract_fingerprint_map_can_opt_into_self_fingerprint(self) -> None:
        fingerprints = describe_terminal_artifact_contract_fingerprints(include_terminal_artifact=True)

        self.assertEqual(fingerprints["terminal_artifact"], terminal_artifact_contract_fingerprint())
        self.assertEqual(len(fingerprints["terminal_artifact"]), 64)
        self.assertNotIn("terminal_artifact", describe_terminal_artifact_contract_fingerprints())

    def test_terminal_artifact_contract_manifest_can_opt_into_cli_fallback_route_contract(self) -> None:
        default_manifest = describe_terminal_artifact_contract()
        manifest = describe_terminal_artifact_contract(include_terminal_artifact_cli_fallback_route=True)
        route_manifest = describe_terminal_artifact_cli_fallback_route_contract()
        fingerprints = describe_terminal_artifact_contract_fingerprints(
            include_terminal_artifact=True,
            include_terminal_artifact_cli_fallback_route=True,
            include_contract_aliases=True,
        )

        self.assertNotIn("terminal_artifact_cli_fallback_route", default_manifest)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route"], route_manifest)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route_contract"], route_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_fingerprint"],
            _fingerprint_manifest_section(manifest["renderer_entrypoints"]),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints"],
            describe_terminal_artifact_contract_fingerprints(
                include_terminal_artifact=True,
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            fingerprints["terminal_artifact"],
            terminal_artifact_contract_fingerprint(include_terminal_artifact_cli_fallback_route=True),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )

    def test_terminal_artifact_contract_fingerprint_map_can_opt_into_alias_contracts(self) -> None:
        fingerprints = describe_terminal_artifact_contract_fingerprints(include_contract_aliases=True)

        self.assertEqual(
            fingerprints["card_contract_fingerprint"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["action_contract_fingerprint"],
            action_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["selection_contract_fingerprint"],
            selection_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(fingerprints["terminal_artifact_contract"], terminal_artifact_contract_fingerprint())
        self.assertEqual(
            fingerprints["terminal_artifact_envelope"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_envelope_contract"],
            terminal_artifact_envelope_contract_fingerprint(),
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
            fingerprints["terminal_artifact_rendering_contract_manifest"],
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
            fingerprints["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_policy"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_raw_leaf_card_default_policy_contract"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
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
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
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
        self.assertEqual(
            a2ui_manifest["terminal_artifact_raw_leaf_card_default_policy"],
            manifest["terminal_artifact_raw_leaf_card_default_policy"],
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            manifest["terminal_artifact_raw_leaf_card_default_policy"],
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
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
        self.assertEqual(
            render_target_manifest["raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            render_target_manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            render_target_manifest["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
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
        self.assertEqual(
            rendering_manifest["raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            rendering_manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            rendering_manifest["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
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
        manifest_alias = describe_terminal_artifact_rendering_contract_manifest()
        manifest_alias_fingerprint = terminal_artifact_rendering_contract_manifest_fingerprint()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["type"], "TerminalArtifactRenderingContract")
        self.assertEqual(manifest["supported_kinds"], list(TERMINAL_ARTIFACT_SUPPORTED_KINDS))
        self.assertEqual(manifest["default_kind"], TERMINAL_ARTIFACT_DEFAULT_KIND)
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
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(
            manifest_alias_fingerprint,
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract_manifest"],
            manifest["terminal_artifact_rendering_contract"],
        )
        self.assertIsNot(
            manifest["terminal_artifact_rendering_contract_manifest"],
            manifest["terminal_artifact_rendering_contract"],
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering"]["contract_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract"]["contract_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(manifest["renderer_entrypoints"], _build_terminal_artifact_renderer_entrypoints())
        self.assertEqual(manifest["render_target_resolver"], "resolve_terminal_artifact_render_target")
        self.assertEqual(manifest["fallback_renderer"], "ShellUI.render_artifact")
        self.assertEqual(manifest["render_target_contract"], describe_terminal_artifact_render_target_contract())
        self.assertEqual(
            manifest["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(manifest["terminal_fallback_contract"], describe_terminal_fallback_contract())
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
            manifest["raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(manifest["terminal_fallback_fingerprint"], terminal_fallback_contract_fingerprint())
        self.assertEqual(
            manifest["terminal_fallback_contract_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
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
            manifest["kind_resolution"]["caller_kind_hint_policy"],
            {
                "invalid_kind_treated_as_absent": True,
                "typed_payload_kind_is_authoritative": True,
                "explicit_card_kind_blocks_leaf_recovery": True,
            },
        )
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
            manifest["kind_resolution_fingerprint"],
            terminal_artifact_kind_resolution_fingerprint(),
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
        self.assertEqual(
            manifest["fallback_recovery_fingerprint"],
            terminal_artifact_fallback_recovery_fingerprint(),
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
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_rendering_contract_manifest_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_fingerprint"],
            _fingerprint_manifest_section(manifest["renderer_entrypoints"]),
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
        self.assertEqual(
            fingerprints["raw_leaf_card_default_policy_contract"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact_rendering", fingerprints)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        for fingerprint in fingerprints.values():
            self.assertEqual(len(fingerprint), 64)
        self.assertEqual(len(fingerprints_with_self["terminal_artifact_rendering"]), 64)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_contract_manifest"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_contract"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )

    def test_terminal_artifact_kind_resolution_and_fallback_recovery_contract_sections_are_public_and_canonical(
        self,
    ) -> None:
        kind_resolution = describe_terminal_artifact_kind_resolution_contract()
        fallback_recovery = describe_terminal_artifact_fallback_recovery_contract()
        render_target_manifest = describe_terminal_artifact_render_target_contract()
        terminal_artifact_manifest = describe_terminal_artifact_contract()

        from src.qual.ui import (
            describe_terminal_artifact_fallback_recovery_contract as exported_fallback_recovery_contract,
        )
        from src.qual.ui import (
            describe_terminal_artifact_kind_resolution_contract as exported_kind_resolution_contract,
        )

        self.assertIs(exported_kind_resolution_contract, describe_terminal_artifact_kind_resolution_contract)
        self.assertIs(exported_fallback_recovery_contract, describe_terminal_artifact_fallback_recovery_contract)
        kind_resolution_snapshot = {
            key: value
            for key, value in kind_resolution.items()
            if key
            not in {
                "kind_resolution_fingerprint",
                "kind_resolution_contract_fingerprint",
                "contract_fingerprint",
            }
        }
        fallback_recovery_snapshot = {
            key: value
            for key, value in fallback_recovery.items()
            if key
            not in {
                "fallback_recovery_fingerprint",
                "fallback_recovery_contract_fingerprint",
                "contract_fingerprint",
            }
        }
        self.assertEqual(kind_resolution_snapshot, render_target_manifest["kind_resolution"])
        self.assertEqual(kind_resolution_snapshot, terminal_artifact_manifest["kind_resolution"])
        self.assertEqual(
            kind_resolution["contract_fingerprint"],
            terminal_artifact_kind_resolution_fingerprint(),
        )
        self.assertEqual(
            kind_resolution["kind_resolution_fingerprint"],
            terminal_artifact_kind_resolution_fingerprint(),
        )
        self.assertEqual(
            kind_resolution["kind_resolution_contract_fingerprint"],
            terminal_artifact_kind_resolution_fingerprint(),
        )
        self.assertEqual(
            kind_resolution["precedence"],
            [
                "validated envelope kind",
                "typed payload kind",
                "explicit caller kind hint",
                "partial leaf hint recovery",
                "schema-valid leaf payload recovery",
                "card default",
            ],
        )
        self.assertTrue(kind_resolution["card_payloads_override_conflicting_action_or_selection_hints"])
        self.assertEqual(
            kind_resolution["caller_kind_hint_policy"],
            {
                "invalid_kind_treated_as_absent": True,
                "typed_payload_kind_is_authoritative": True,
                "explicit_card_kind_blocks_leaf_recovery": True,
            },
        )
        self.assertEqual(kind_resolution["partial_leaf_recovery"], render_target_manifest["kind_resolution"]["partial_leaf_recovery"])
        self.assertEqual(fallback_recovery_snapshot, render_target_manifest["fallback_recovery"])
        self.assertEqual(fallback_recovery_snapshot, terminal_artifact_manifest["fallback_recovery"])
        self.assertEqual(
            fallback_recovery["contract_fingerprint"],
            terminal_artifact_fallback_recovery_fingerprint(),
        )
        self.assertEqual(
            fallback_recovery["fallback_recovery_fingerprint"],
            terminal_artifact_fallback_recovery_fingerprint(),
        )
        self.assertEqual(
            fallback_recovery["fallback_recovery_contract_fingerprint"],
            terminal_artifact_fallback_recovery_fingerprint(),
        )
        self.assertEqual(
            fallback_recovery,
            {
                "malformed_card_envelopes": {
                    "action": "normalize_action_ref",
                    "selection": "normalize_selection_ref",
                },
                "fallback_recovery_fingerprint": terminal_artifact_fallback_recovery_fingerprint(),
                "fallback_recovery_contract_fingerprint": terminal_artifact_fallback_recovery_fingerprint(),
                "contract_fingerprint": terminal_artifact_fallback_recovery_fingerprint(),
            },
        )

    def test_terminal_artifact_cli_fallback_contract_manifest_is_versioned_and_embedded_in_a2ui_contract(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_contract()
        manifest_alias = describe_terminal_artifact_cli_fallback_contract_manifest()
        manifest_alias_fingerprint = terminal_artifact_cli_fallback_contract_manifest_fingerprint()
        a2ui_manifest = describe_a2ui_contract()
        cli_fallback_target_manifest = describe_terminal_artifact_cli_fallback_target_contract()
        card_hint_recovery_policy_manifest = describe_terminal_artifact_cli_fallback_card_hint_recovery_policy_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_schema_version"], 1)
        self.assertEqual(manifest["type"], "TerminalArtifactCliFallbackContract")
        self.assertEqual(manifest["fallback_target_resolver"], "resolve_terminal_artifact_cli_fallback_target")
        self.assertEqual(manifest["fallback_renderer"], "ShellUI.render_artifact")
        self.assertEqual(manifest["terminal_artifact_cli_fallback_entrypoint"], "render_terminal_cli_fallback")
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section(manifest["terminal_artifact_cli_fallback_entrypoint"]),
        )
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(manifest_alias_fingerprint, terminal_artifact_cli_fallback_contract_fingerprint())
        self.assertEqual(
            manifest["contract_manifest"],
            manifest["terminal_artifact_cli_fallback_contract_manifest"],
        )
        self.assertEqual(manifest["contract_manifest_fingerprint"], terminal_artifact_cli_fallback_contract_fingerprint())
        self.assertEqual(manifest["raw_leaf_card_default"], _RAW_LEAF_CARD_DEFAULT_MANIFEST)
        self.assertEqual(manifest["allowed_actions"], sorted(ALLOWED_ACTION_IDS))
        self.assertEqual(
            manifest["allowed_actions_fingerprint"],
            _fingerprint_manifest_section(manifest["allowed_actions"]),
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy"],
            card_hint_recovery_policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_fingerprint"],
            card_hint_recovery_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract"],
            card_hint_recovery_policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest"],
            card_hint_recovery_policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_fingerprint"],
            card_hint_recovery_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest_fingerprint"],
            card_hint_recovery_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_contract"],
            describe_terminal_artifact_raw_leaf_card_default_contract(),
        )
        self.assertEqual(manifest["supported_kinds"], list(TERMINAL_ARTIFACT_SUPPORTED_KINDS))
        self.assertEqual(manifest["terminal_artifact_supported_kinds"], list(TERMINAL_ARTIFACT_SUPPORTED_KINDS))
        self.assertEqual(
            manifest["terminal_artifact_supported_kinds_contract"],
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        )
        self.assertEqual(
            manifest["terminal_artifact_supported_kinds_contract_fingerprint"],
            _fingerprint_manifest_section(list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)),
        )
        self.assertEqual(manifest["default_kind"], TERMINAL_ARTIFACT_DEFAULT_KIND)
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
        self.assertEqual(
            manifest["kind_policy_fingerprint"],
            _fingerprint_manifest_section(manifest["kind_policy"]),
        )
        self.assertEqual(manifest["kind_policy_contract"], manifest["kind_policy"])
        self.assertEqual(manifest["kind_policy_contract_fingerprint"], manifest["kind_policy_fingerprint"])
        self.assertEqual(manifest["kind_policy_contract_manifest"], manifest["kind_policy"])
        self.assertEqual(
            manifest["kind_policy_contract_manifest_fingerprint"],
            manifest["kind_policy_fingerprint"],
        )
        self.assertEqual(
            manifest["resolver_failure_policy"],
            {
                "retry_resolver": "resolve_terminal_artifact_render_target",
                "raw_leaf_card_default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
                "leaf_renderers": {
                    "card": "render_terminal_card",
                    "action": "render_terminal_action",
                    "selection": "render_terminal_selection",
                },
            },
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy"],
            card_hint_recovery_policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_fingerprint"],
            card_hint_recovery_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract"],
            card_hint_recovery_policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest"],
            card_hint_recovery_policy_manifest,
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_fingerprint"],
            card_hint_recovery_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["card_hint_recovery_policy_contract_manifest_fingerprint"],
            card_hint_recovery_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target"]["raw_leaf_card_default_policy"],
            {
                "default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
                "preserve_when_kind_is_unset": True,
                "invalid_kind_treated_as_absent": True,
            },
        )
        self.assertEqual(
            cli_fallback_target_manifest["raw_leaf_card_default_policy"],
            manifest["terminal_artifact_cli_fallback_target"]["raw_leaf_card_default_policy"],
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_policy"],
            manifest["terminal_artifact_cli_fallback_target"]["raw_leaf_card_default_policy"],
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["raw_leaf_card_default_policy"],
            manifest["raw_leaf_card_default_policy"],
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["resolver_failure_policy"],
            manifest["resolver_failure_policy"],
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
            manifest["terminal_artifact_cli_fallback_target"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertIsNot(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"],
            cli_fallback_target_manifest,
        )
        self.assertIsNot(manifest["terminal_artifact_cli_fallback_contract_manifest"], manifest)
        self.assertNotIn("contract_fingerprint", manifest["terminal_artifact_cli_fallback_contract_manifest"])
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
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
                "allowed_actions": _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
                "kind_contracts": terminal_artifact_kind_contracts_fingerprint(),
                "terminal_artifact_cli_fallback_entrypoint": _fingerprint_manifest_section(
                    "render_terminal_cli_fallback"
                ),
                "render_target_contract": terminal_artifact_render_target_contract_fingerprint(),
                "rendering_contract": terminal_artifact_rendering_contract_fingerprint(),
                "terminal_fallback_contract": terminal_fallback_contract_fingerprint(),
                "raw_leaf_card_default_contract": terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
                "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
                "shell_refinement_policy": _fingerprint_manifest_section(manifest["shell_refinement_policy"]),
                "resolver_failure_policy": _fingerprint_manifest_section(manifest["resolver_failure_policy"]),
                "kind_policy": _fingerprint_manifest_section(manifest["kind_policy"]),
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
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact"]["terminal_artifact_cli_fallback_target_contract"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(a2ui_manifest["terminal_artifact_cli_fallback"], manifest)
        self.assertEqual(a2ui_manifest["terminal_artifact_cli_fallback_target"], cli_fallback_target_manifest)
        self.assertEqual(
            a2ui_manifest["terminal_artifact_cli_fallback_target_contract"],
            cli_fallback_target_manifest,
        )
        self.assertEqual(a2ui_manifest["terminal_artifact_render_target"], describe_terminal_artifact_render_target_contract())
        self.assertEqual(a2ui_manifest["terminal_artifact_cli_fallback_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(
            a2ui_manifest["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact_render_target"],
            describe_terminal_artifact_render_target_contract(),
        )
        self.assertEqual(a2ui_manifest["schemas"]["terminal_artifact_cli_fallback"], manifest)
        self.assertEqual(
            a2ui_manifest["schemas"]["terminal_artifact_cli_fallback_target"],
            cli_fallback_target_manifest,
        )

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

    def test_terminal_artifact_cli_fallback_entrypoint_treats_non_string_kind_hints_as_absent(self) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        shell = ShellUI()

        self.assertEqual(render_terminal_cli_fallback(raw_leaf, kind=123), render_terminal_cli_fallback(raw_leaf))
        self.assertEqual(shell.render_artifact(raw_leaf, kind=123), shell.render_artifact(raw_leaf))

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

    def test_terminal_artifact_cli_fallback_entrypoint_preserves_invalid_card_hints_for_envelopes_without_kind_metadata(
        self,
    ) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "artifact": {
                "type": "ActionRef",
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
        }
        shell = ShellUI()

        direct_text = render_terminal_artifact(envelope, kind="card")
        cli_text = render_terminal_cli_fallback(envelope, kind="card")
        shell_text = shell.render_artifact(envelope, kind="card")

        self.assertEqual(direct_text, cli_text)
        self.assertEqual(cli_text, shell_text)
        self.assertIn("[UnknownCard] <invalid card>", cli_text)
        self.assertIn("Fallback: unknown card", cli_text)
        self.assertNotIn("[ActionRef]", cli_text)
        self.assertNotIn("[SelectionRef]", cli_text)

    def test_terminal_artifact_cli_fallback_entrypoint_recovers_typed_leaf_mappings_from_malformed_envelopes(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "ActionRef",
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                },
                "[ActionRef] Export",
                "Action schema v1",
            ),
            (
                "selection",
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "SelectionRef",
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                },
                "[SelectionRef] Choice",
                "Selection schema v1",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_schema in cases:
            with self.subTest(kind=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn(expected_prefix, cli_text)
                self.assertIn(expected_schema, cli_text)
                self.assertNotIn("[UnknownCard] <invalid card>", cli_text)

    def test_terminal_artifact_cli_fallback_entrypoint_recovers_typed_envelopes_under_card_hints(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "type": "TerminalArtifact",
                    "kind": "action",
                    "artifact": {
                        "type": "ActionRef",
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    "trace_id": "drop-me",
                },
                "[ActionRef] Export",
                "Action schema v1",
            ),
            (
                "selection",
                {
                    "type": "TerminalArtifact",
                    "kind": "selection",
                    "artifact": {
                        "type": "SelectionRef",
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                    "trace_id": "drop-me",
                },
                "[SelectionRef] Choice",
                "Selection schema v1",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_schema in cases:
            with self.subTest(kind=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn(expected_prefix, cli_text)
                self.assertIn(expected_schema, cli_text)
                self.assertNotIn("[UnknownCard] <invalid card>", cli_text)

    def test_terminal_artifact_cli_fallback_entrypoint_recovers_nested_typed_envelopes_under_card_hints(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
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
                },
                "[ActionRef] Export",
                "Action schema v1",
            ),
            (
                "selection",
                {
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
                },
                "[SelectionRef] Choice",
                "Selection schema v1",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_schema in cases:
            with self.subTest(kind=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn(expected_prefix, cli_text)
                self.assertIn(expected_schema, cli_text)
                self.assertNotIn("[UnknownCard] <invalid card>", cli_text)

    def test_terminal_artifact_cli_fallback_entrypoint_keeps_explicit_typed_leaf_mappings_invalid_for_card_hints(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "type": "ActionRef",
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
            ),
            (
                "selection",
                {
                    "type": "SelectionRef",
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(kind=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")
                shell_render_text = shell.render_artifact(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertEqual(shell_text, shell_render_text)
                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertNotIn("[ActionRef]", cli_text)
                self.assertNotIn("[SelectionRef]", cli_text)

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

    def test_terminal_artifact_cli_fallback_target_resolver_keeps_ambiguous_raw_leaf_payloads_on_card_default_for_leaf_kind_hints(
        self,
    ) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(raw_leaf, kind="action"),
            (raw_leaf, "card"),
        )
        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(raw_leaf, kind="selection"),
            (raw_leaf, "card"),
        )
        # Leaf-hint forwarding is covered by the renderer-focused tests below.
        # This case only locks the resolver's card-default policy.

    def test_terminal_artifact_cli_fallback_target_resolver_keeps_explicit_typed_leaf_mappings_on_card_path(
        self,
    ) -> None:
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

        self.assertEqual(resolve_terminal_artifact_cli_fallback_target(action, kind="card"), (action, "card"))
        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(selection, kind="card"),
            (selection, "card"),
        )

    def test_terminal_artifact_cli_fallback_target_resolver_keeps_direct_typed_envelopes_on_card_path(
        self,
    ) -> None:
        action_envelope = {
            "type": "TerminalArtifact",
            "kind": "action",
            "artifact": {
                "type": "ActionRef",
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
        }
        selection_envelope = {
            "type": "TerminalArtifact",
            "kind": "selection",
            "artifact": {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
            },
        }

        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(action_envelope, kind="card"),
            (action_envelope, "card"),
        )
        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(selection_envelope, kind="card"),
            (selection_envelope, "card"),
        )

    def test_terminal_artifact_cli_fallback_entrypoint_rejects_explicit_typed_leaf_mappings_under_card_hints(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "type": "ActionRef",
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
                "[ActionRef] Export",
                "Action schema v1",
            ),
            (
                "selection",
                {
                    "type": "SelectionRef",
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                "[SelectionRef] Choice",
                "Selection schema v1",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_schema in cases:
            with self.subTest(kind=case_name):
                self.assertEqual(
                    resolve_terminal_artifact_cli_fallback_target(artifact, kind="card"),
                    (artifact, "card"),
                )
                with self.assertRaises(ValueError):
                    render_terminal_artifact(artifact, kind="card")
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertIn("Action policy: copy_to_clipboard_only", cli_text)
                self.assertNotIn(expected_prefix, cli_text)
                self.assertNotIn(expected_schema, cli_text)

    def test_terminal_artifact_cli_fallback_target_resolver_keeps_ambiguous_raw_leaf_payloads_on_card_default_for_malformed_envelope_kinds(
        self,
    ) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
        }

        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(envelope),
            (envelope["artifact"], "card"),
        )

    def test_terminal_artifact_cli_fallback_target_resolver_recovers_nested_leaf_payloads_when_shared_resolver_fails(
        self,
    ) -> None:
        action_envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "type": "TerminalArtifact",
                "kind": "dialog",
                "artifact": {
                    "type": "ActionRef",
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
                "trace_id": "inner",
            },
            "trace_id": "outer",
        }
        selection_envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "type": "TerminalArtifact",
                "kind": "dialog",
                "artifact": {
                    "type": "SelectionRef",
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
                "trace_id": "inner",
            },
            "trace_id": "outer",
        }

        with patch("src.qual.ui.a2ui._resolve_terminal_artifact_render_target", side_effect=RuntimeError("boom")):
            action_target = resolve_terminal_artifact_cli_fallback_target(action_envelope)
            selection_target = resolve_terminal_artifact_cli_fallback_target(selection_envelope)

        self.assertEqual(action_target[1], "action")
        self.assertEqual(selection_target[1], "selection")
        self.assertEqual(action_target[0], action_envelope["artifact"]["artifact"])
        self.assertEqual(selection_target[0], selection_envelope["artifact"]["artifact"])

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
        self.assertIn("- label: Export", rendered_text)
        self.assertNotIn("[ActionRef]", rendered_text)
        self.assertNotIn("[SelectionRef]", rendered_text)

    def test_terminal_artifact_renderers_keep_ambiguous_raw_leaf_payloads_on_card_default_for_malformed_envelope_kinds(
        self,
    ) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
        }

        rendered_text = render_terminal_artifact(envelope)
        cli_fallback_text = render_terminal_cli_fallback(envelope)

        self.assertEqual(rendered_text, cli_fallback_text)
        self.assertIn("[<missing>] <untitled>", rendered_text)
        self.assertNotIn("[ActionRef]", rendered_text)
        self.assertNotIn("[SelectionRef]", rendered_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", rendered_text)

    def test_terminal_artifact_renderers_preserve_raw_leaf_card_default_for_explicit_card_hints(
        self,
    ) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
            "trace_id": "drop-me",
        }

        rendered_text = render_terminal_artifact(envelope, kind="card")
        cli_fallback_text = render_terminal_cli_fallback(envelope, kind="card")
        shell_text = ShellUI().render_artifact(envelope, kind="card")

        self.assertEqual(rendered_text, cli_fallback_text)
        self.assertEqual(shell_text, cli_fallback_text)
        self.assertIn("[<missing>] <untitled>", rendered_text)
        self.assertIn("- label: Export", rendered_text)
        self.assertNotIn("[UnknownCard] <invalid card>", rendered_text)
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

    def test_terminal_artifact_renderers_recover_when_card_renderer_returns_non_string(self) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch("src.qual.ui.a2ui.render_terminal_card", return_value={"oops": "not text"}):
            rendered_text = render_terminal_artifact(raw_leaf)
            cli_fallback_text = render_terminal_cli_fallback(raw_leaf)

        for text in (rendered_text, cli_fallback_text):
            self.assertIn("[UnknownCard] <invalid card>", text)
            self.assertIn("Fallback: unknown card", text)
            self.assertNotIsInstance(text, dict)

    def test_terminal_artifact_renderers_recover_when_card_renderer_returns_blank_string(self) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch("src.qual.ui.a2ui.render_terminal_card", return_value=""):
            rendered_text = render_terminal_artifact(raw_leaf)
            cli_fallback_text = render_terminal_cli_fallback(raw_leaf)

        for text in (rendered_text, cli_fallback_text):
            self.assertIn("[UnknownCard] <invalid card>", text)
            self.assertIn("Fallback: unknown card", text)
            self.assertNotEqual(text.strip(), "")

    def test_terminal_artifact_cli_fallback_entrypoint_recovers_leaf_payloads_when_shared_resolver_fails(
        self,
    ) -> None:
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

        with patch(
            "src.qual.ui.a2ui.resolve_terminal_artifact_cli_fallback_target",
            side_effect=RuntimeError("boom"),
        ):
            action_text = render_terminal_cli_fallback(action_envelope)
            selection_text = render_terminal_cli_fallback(selection_envelope)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("Action schema v1", action_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", action_text)

        self.assertIn("[SelectionRef] Choice", selection_text)
        self.assertIn("Selection schema v1", selection_text)
        self.assertIn("A2UI v1", selection_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", selection_text)

    def test_terminal_artifact_cli_fallback_entrypoint_preserves_raw_leaf_card_default_when_resolver_fails(
        self,
    ) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch(
            "src.qual.ui.a2ui.resolve_terminal_artifact_cli_fallback_target",
            side_effect=RuntimeError("boom"),
        ):
            text = render_terminal_cli_fallback(raw_leaf, kind="action")

        self.assertIn("[<missing>] <untitled>", text)
        self.assertNotIn("[ActionRef]", text)
        self.assertNotIn("[SelectionRef]", text)

    def test_terminal_artifact_cli_fallback_rejects_leaf_renderer_text_for_card_hints(self) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch(
            "src.qual.ui.a2ui._render_terminal_artifact_resolved",
            return_value="[ActionRef] Export\nAction schema v1",
        ):
            text = render_terminal_cli_fallback(raw_leaf, kind="card")

        self.assertIn("[<missing>] <untitled>", text)
        self.assertNotIn("[ActionRef] Export", text)
        self.assertNotIn("[SelectionRef]", text)
        self.assertNotIn("[TerminalArtifact]", text)

    def test_terminal_artifact_renderer_rejects_explicit_leaf_dataclasses_for_card_hints_and_cli_fallback_keeps_them_invalid(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            ("action", ActionRef(id="export_document", label="Export", payload={"format": "md"})),
            (
                "selection",
                SelectionRef(id="choice-1", label="Choice", payload={"nested": {"items": [1, 2]}}),
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(case=case_name):
                with self.assertRaises(ValueError):
                    render_terminal_artifact(artifact, kind="card")
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_artifact(artifact, kind="card")
                shell_cli_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertIn("[UnknownCard] <invalid card>", shell_text)
                self.assertIn("Action policy: copy_to_clipboard_only", shell_text)
                self.assertEqual(shell_cli_text, cli_text)
                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertIn("[UnknownCard] <invalid card>", shell_cli_text)
                self.assertNotIn("[ActionRef]", cli_text)
                self.assertNotIn("[SelectionRef]", cli_text)
                self.assertNotIn("[ActionRef]", shell_cli_text)
                self.assertNotIn("[SelectionRef]", shell_cli_text)

    def test_terminal_artifact_cli_fallback_contract_fingerprints_are_public_and_canonical(self) -> None:
        manifest = describe_terminal_artifact_cli_fallback_contract()
        fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints()
        target_fingerprints = describe_terminal_artifact_cli_fallback_target_contract_fingerprints()
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
            fingerprints["allowed_actions"],
            _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_fingerprint"],
            _fingerprint_manifest_section(manifest["renderer_entrypoints"]),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"]),
        )
        self.assertEqual(
            fingerprints["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_policy_contract"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy"],
            _fingerprint_manifest_section(manifest["shell_refinement_policy"]),
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy"],
            _fingerprint_manifest_section(manifest["resolver_failure_policy"]),
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy"],
            _fingerprint_manifest_section(
                {
                    "recover_typed_leaf_mappings": True,
                    "recover_typed_leaf_payloads": True,
                    "explicit_leaf_instances_rejected_under_card_hints": True,
                    "preserve_raw_leaf_card_default": True,
                }
            ),
        )
        self.assertEqual(
            terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(),
            _fingerprint_manifest_section(target_fingerprints),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["card_hint_recovery_policy_contract_manifest"],
            _fingerprint_manifest_section(
                {
                    "recover_typed_leaf_mappings": True,
                    "recover_typed_leaf_payloads": True,
                    "explicit_leaf_instances_rejected_under_card_hints": True,
                    "preserve_raw_leaf_card_default": True,
                }
            ),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_manifest"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["raw_leaf_card_default_policy_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints(
                include_terminal_artifact_raw_leaf_card_default_policy=True,
            ),
        )
        self.assertEqual(
            manifest["shell_refinement_policy"],
            {
                "preserve_raw_leaf_card_default": True,
                "invalid_kind_treated_as_absent": True,
                "refine_card_underflow": True,
            },
        )
        self.assertEqual(
            manifest["resolver_failure_policy"],
            {
                "retry_resolver": "resolve_terminal_artifact_render_target",
                "raw_leaf_card_default_kind": TERMINAL_ARTIFACT_DEFAULT_KIND,
                "leaf_renderers": {
                    "card": "render_terminal_card",
                    "action": "render_terminal_action",
                    "selection": "render_terminal_selection",
                },
            },
        )
        self.assertEqual(
            manifest["shell_refinement_policy_fingerprint"],
            _fingerprint_manifest_section(manifest["shell_refinement_policy"]),
        )
        self.assertEqual(
            manifest["resolver_failure_policy_fingerprint"],
            _fingerprint_manifest_section(manifest["resolver_failure_policy"]),
        )
        self.assertNotIn("terminal_artifact_cli_fallback", fingerprints)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_rendering_contract_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["shell_refinement_policy_fingerprint"],
            _fingerprint_manifest_section(manifest["shell_refinement_policy"]),
        )
        self.assertEqual(
            fingerprints_with_self["resolver_failure_policy_fingerprint"],
            _fingerprint_manifest_section(manifest["resolver_failure_policy"]),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_kind_contracts"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertIsNot(
            manifest["raw_leaf_card_default_policy_contract"],
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
        )
        self.assertIsNot(
            manifest["raw_leaf_card_default_policy_contract_fingerprints"],
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints"],
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
            fingerprints_with_self["allowed_actions_fingerprint"],
            _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_contract_manifest"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )

    def test_route_aware_fingerprint_summaries_propagate_route_into_target_fingerprints(self) -> None:
        route_target_fingerprints = describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True,
        )
        route_target_fingerprints_with_aliases = describe_terminal_artifact_cli_fallback_target_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True,
            include_contract_aliases=True,
        )
        route_target_fingerprint = terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint(
            include_terminal_artifact_cli_fallback_route=True,
        )

        cli_fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints(
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_route=True,
            include_contract_aliases=True,
        )
        a2ui_fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact=True,
            include_terminal_artifact_cli_fallback_target=True,
            include_terminal_artifact_cli_fallback_route=True,
            include_contract_aliases=True,
        )

        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            route_target_fingerprints,
        )
        self.assertEqual(route_target_fingerprints["leaf_contracts"], a2ui_leaf_contracts_fingerprint())
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts_contract"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts_contract_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts_contract_manifest"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts_contract_manifest_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts_manifest"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["leaf_contracts_manifest_fingerprint"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            route_target_fingerprints_with_aliases["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            route_target_fingerprint,
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            route_target_fingerprints,
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"]["leaf_contracts"],
            a2ui_leaf_contracts_fingerprint(),
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            route_target_fingerprint,
        )
        self.assertEqual(
            a2ui_fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )

    def test_a2ui_contract_fingerprints_can_opt_into_cli_fallback_contract_and_target_manifests(self) -> None:
        cli_fingerprints = describe_a2ui_contract_fingerprints(
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_target=True,
        )
        cli_fallback_fingerprint = terminal_artifact_cli_fallback_contract_fingerprint()
        target_fingerprint = terminal_artifact_cli_fallback_target_contract_fingerprint()

        self.assertEqual(cli_fingerprints["terminal_artifact_cli_fallback"], cli_fallback_fingerprint)
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_contract"],
            cli_fallback_fingerprint,
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_contract_manifest"],
            cli_fallback_fingerprint,
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_target"],
            target_fingerprint,
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_target_contract"],
            target_fingerprint,
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"],
            target_fingerprint,
        )
        self.assertEqual(
            cli_fingerprints["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            target_fingerprint,
        )

    def test_terminal_artifact_cli_fallback_route_contract_is_opt_in_and_fingerprintable(self) -> None:
        from src.qual.ui import (
            describe_terminal_artifact_cli_fallback_route_contract as exported_route_contract,
            terminal_artifact_cli_fallback_route_contract_fingerprint as exported_route_fingerprint,
        )

        manifest = describe_terminal_artifact_cli_fallback_contract()
        route_manifest = describe_terminal_artifact_cli_fallback_route_contract()
        route_fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints(
            include_contract_aliases=True,
        )
        routed_manifest = describe_terminal_artifact_cli_fallback_contract(
            include_terminal_artifact_cli_fallback_route=True,
        )
        fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True,
            include_contract_aliases=True,
        )

        self.assertIs(exported_route_contract, describe_terminal_artifact_cli_fallback_route_contract)
        self.assertIs(exported_route_fingerprint, terminal_artifact_cli_fallback_route_contract_fingerprint)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract", manifest)
        self.assertEqual(route_manifest["contract_version"], 2)
        self.assertEqual(route_manifest["a2ui_version"], 1)
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_route_schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ROUTE_SCHEMA_VERSION,
        )
        self.assertEqual(route_manifest["type"], "TerminalArtifactCliFallbackRouteContract")
        self.assertEqual(
            route_manifest["route_precedence"],
            [
                "shared_target_resolver",
                "shell_refinement",
                "render_terminal_action",
                "render_terminal_selection",
                "render_terminal_card",
            ],
        )
        self.assertEqual(
            route_manifest["route_precedence_fingerprint"],
            _fingerprint_manifest_section(route_manifest["route_precedence"]),
        )
        self.assertEqual(
            route_manifest["leaf_renderers_fingerprint"],
            _fingerprint_manifest_section(route_manifest["leaf_renderers"]),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_supported_kinds"],
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_supported_kinds_contract"],
            list(TERMINAL_ARTIFACT_SUPPORTED_KINDS),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_supported_kinds_contract_fingerprint"],
            _fingerprint_manifest_section(list(TERMINAL_ARTIFACT_SUPPORTED_KINDS)),
        )
        self.assertEqual(manifest["route_precedence"], route_manifest["route_precedence"])
        self.assertEqual(routed_manifest["route_precedence"], route_manifest["route_precedence"])
        self.assertEqual(route_manifest["terminal_artifact_cli_fallback_target_contract"]["route_precedence"], route_manifest["route_precedence"])
        self.assertEqual(
            route_manifest["leaf_renderers"],
            {
                "card": "render_terminal_card",
                "action": "render_terminal_action",
                "selection": "render_terminal_selection",
            },
        )
        self.assertEqual(
            route_manifest["shell_refinement_policy"],
            {
                "preserve_raw_leaf_card_default": True,
                "invalid_kind_treated_as_absent": True,
                "refine_card_underflow": True,
            },
        )
        self.assertEqual(
            route_manifest["shell_refinement_policy_fingerprint"],
            _fingerprint_manifest_section(route_manifest["shell_refinement_policy"]),
        )
        self.assertEqual(
            route_manifest["resolver_failure_policy_fingerprint"],
            _fingerprint_manifest_section(route_manifest["resolver_failure_policy"]),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_target_contract"],
            describe_terminal_artifact_cli_fallback_target_contract(),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_target_contract"]["route_precedence"],
            route_manifest["route_precedence"],
        )
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            describe_terminal_artifact_cli_fallback_target_contract_fingerprints(),
        )
        self.assertEqual(
            route_manifest["contract_manifest"],
            route_manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
        )
        self.assertEqual(
            route_manifest["contract_manifest_fingerprint"],
            route_manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"],
        )
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(route_manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"]),
        )
        self.assertEqual(
            route_manifest["contract_fingerprints"]["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            route_manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(route_manifest["contract_fingerprints"]),
        )
        self.assertEqual(
            route_manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints["contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            route_fingerprints["contract_manifest"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            route_fingerprints["contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(routed_manifest["terminal_artifact_cli_fallback_route_contract"], route_manifest)
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            route_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract"]["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract"]["terminal_artifact_cli_fallback_target_contract"],
            route_manifest["terminal_artifact_cli_fallback_target_contract"],
        )
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract"]["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            route_manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
        )
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract"]["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            route_manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
        )
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract"]["contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            routed_manifest["terminal_artifact_cli_fallback_route_contract"][
                "terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"
            ],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(len(route_manifest["contract_fingerprint"]), 64)

    def test_shell_ui_contract_is_versioned_and_fingerprintable(self) -> None:
        manifest = describe_shell_ui_contract()
        manifest_alias = describe_shell_ui_contract_manifest()
        target_contract = describe_terminal_artifact_cli_fallback_target_contract()
        route_fingerprint = terminal_artifact_cli_fallback_route_contract_fingerprint()
        shell_fingerprint = shell_ui_contract_fingerprint()
        shell_manifest_fingerprint = shell_ui_contract_manifest_fingerprint()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["shell_ui_schema_version"], SHELL_UI_CONTRACT_VERSION)
        self.assertEqual(manifest["shell_ui_version"], SHELL_UI_CONTRACT_VERSION)
        self.assertEqual(manifest["shell_ui_contract_version"], SHELL_UI_CONTRACT_VERSION)
        self.assertEqual(manifest["type"], "ShellUIContract")
        self.assertEqual(manifest["contract_fingerprint"], shell_fingerprint)
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(manifest["shell_ui_fingerprint"], shell_fingerprint)
        self.assertEqual(shell_manifest_fingerprint, shell_fingerprint)
        self.assertEqual(manifest["contract_manifest"], manifest["shell_ui_contract"])
        self.assertEqual(manifest["contract_manifest_fingerprint"], shell_fingerprint)
        self.assertEqual(manifest["shell_ui_contract_manifest"], manifest["shell_ui_contract"])
        self.assertEqual(manifest["shell_ui_contract_manifest_fingerprint"], shell_fingerprint)
        self.assertIsNot(manifest["shell_ui_contract"], manifest)
        self.assertEqual(manifest["shell_ui_contract"]["contract_version"], 2)
        self.assertEqual(manifest["shell_ui_contract"]["a2ui_version"], 1)
        self.assertEqual(
            manifest["shell_ui_contract"]["shell_ui_schema_version"],
            SHELL_UI_CONTRACT_VERSION,
        )
        self.assertEqual(manifest["shell_ui_contract"]["shell_ui_version"], SHELL_UI_CONTRACT_VERSION)
        self.assertEqual(
            manifest["shell_ui_contract"]["shell_ui_contract_version"],
            SHELL_UI_CONTRACT_VERSION,
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_entrypoint_schema_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_entrypoint_version"],
            TERMINAL_ARTIFACT_CLI_FALLBACK_ENTRYPOINT_SCHEMA_VERSION,
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            describe_terminal_artifact_cli_fallback_entrypoint_contract(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["entrypoints_contract_manifest"],
            manifest["shell_ui_contract"]["entrypoints_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["entrypoints_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["shell_ui_contract"]["entrypoints_contract"]),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["route_precedence_contract_manifest"],
            manifest["shell_ui_contract"]["route_precedence_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["route_precedence_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["shell_ui_contract"]["route_precedence_contract"]),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["startup_fields_contract_manifest"],
            manifest["shell_ui_contract"]["startup_fields_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["startup_fields_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["shell_ui_contract"]["startup_fields_contract"]),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["startup_preview_contract_manifest"],
            manifest["shell_ui_contract"]["startup_preview_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["startup_preview_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["shell_ui_contract"]["startup_preview_contract"]),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_target_contract"],
            manifest["terminal_artifact_cli_fallback_target_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            target_contract["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            target_contract["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_target_contract_manifest"],
            target_contract,
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_route_contract"],
            manifest["terminal_artifact_cli_fallback_route_contract"],
        )
        self.assertEqual(manifest["shell_ui_contract_fingerprint"], shell_fingerprint)
        self.assertEqual(
            manifest["entrypoints"],
            {
                "render_artifact": "ShellUI.render_artifact",
                "render_cli_fallback": "ShellUI.render_cli_fallback",
                "render_startup": "ShellUI.render_startup",
            },
        )
        self.assertIsNot(manifest["entrypoints_contract"], manifest["entrypoints"])
        self.assertEqual(manifest["entrypoints_contract"], manifest["entrypoints"])
        self.assertEqual(
            manifest["entrypoints_fingerprint"],
            _fingerprint_manifest_section(manifest["entrypoints"]),
        )
        self.assertEqual(
            manifest["entrypoints_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["entrypoints"]),
        )
        self.assertEqual(
            manifest["route_precedence"],
            [
                "shared_target_resolver",
                "shell_refinement",
                "render_terminal_action",
                "render_terminal_selection",
                "render_terminal_card",
            ],
        )
        self.assertEqual(manifest["route_precedence_contract"], manifest["route_precedence"])
        self.assertIsNot(manifest["route_precedence_contract"], manifest["route_precedence"])
        self.assertEqual(
            manifest["route_precedence_fingerprint"],
            _fingerprint_manifest_section(manifest["route_precedence"]),
        )
        self.assertEqual(
            manifest["route_precedence_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["route_precedence"]),
        )
        self.assertEqual(
            manifest["startup_fields"],
            ["project", "vault", "locked", "context_items", "context_preview"],
        )

    def test_shell_ui_entrypoint_contract_rejects_duplicate_names(self) -> None:
        duplicate_entrypoints = (
            ("render_artifact", "ShellUI.render_artifact"),
            ("render_artifact", "ShellUI.render_cli_fallback"),
            ("render_startup", "ShellUI.render_startup"),
        )

        from src.qual.ui import shell as shell_module

        shell_module._build_shell_ui_contract_manifest.cache_clear()
        shell_module._describe_shell_ui_contract_fingerprints_cached.cache_clear()
        try:
            with patch("src.qual.ui.shell.SHELL_UI_ENTRYPOINTS", duplicate_entrypoints):
                with self.assertRaisesRegex(ValueError, "Duplicate shell UI entrypoint: render_artifact"):
                    describe_shell_ui_contract()
                with self.assertRaisesRegex(ValueError, "Duplicate shell UI entrypoint: render_artifact"):
                    describe_shell_ui_contract_fingerprints()
        finally:
            shell_module._build_shell_ui_contract_manifest.cache_clear()
            shell_module._describe_shell_ui_contract_fingerprints_cached.cache_clear()

    def test_shell_ui_entrypoint_contract_rejects_blank_names(self) -> None:
        blank_entrypoints = (
            ("render_artifact", "ShellUI.render_artifact"),
            ("   ", "ShellUI.render_cli_fallback"),
            ("render_startup", "ShellUI.render_startup"),
        )

        from src.qual.ui import shell as shell_module

        shell_module._build_shell_ui_contract_manifest.cache_clear()
        shell_module._describe_shell_ui_contract_fingerprints_cached.cache_clear()
        try:
            with patch("src.qual.ui.shell.SHELL_UI_ENTRYPOINTS", blank_entrypoints):
                with self.assertRaisesRegex(ValueError, "Shell UI entrypoints must use non-empty string names"):
                    describe_shell_ui_contract()
                with self.assertRaisesRegex(ValueError, "Shell UI entrypoints must use non-empty string names"):
                    describe_shell_ui_contract_fingerprints()
        finally:
            shell_module._build_shell_ui_contract_manifest.cache_clear()
            shell_module._describe_shell_ui_contract_fingerprints_cached.cache_clear()

    def test_shell_ui_contract_snapshot_isolation_keeps_embedded_copy_stable(self) -> None:
        manifest = describe_shell_ui_contract()
        embedded = manifest["shell_ui_contract"]
        target_contract = describe_terminal_artifact_cli_fallback_target_contract()
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        route_fingerprint = terminal_artifact_cli_fallback_route_contract_fingerprint()

        manifest["entrypoints"]["render_artifact"] = "mutated"
        manifest["startup_preview"]["limit"] = 99
        manifest["contract_fingerprints"]["entrypoints"] = "mutated"

        self.assertEqual(
            embedded["entrypoints"],
            {
                "render_artifact": "ShellUI.render_artifact",
                "render_cli_fallback": "ShellUI.render_cli_fallback",
                "render_startup": "ShellUI.render_startup",
            },
        )
        self.assertEqual(
            embedded["startup_preview"],
            {
                "empty_value": "<empty>",
                "limit": SHELL_UI_STARTUP_PREVIEW_LIMIT,
                "source_field": "basket.item_ids",
            },
        )
        self.assertEqual(
            embedded["contract_fingerprints_contract"],
            manifest["contract_fingerprints_contract"],
        )
        self.assertIsNot(embedded["contract_fingerprints_contract"], manifest["contract_fingerprints"])
        self.assertEqual(
            embedded["contract_fingerprints_contract"]["entrypoints"],
            _fingerprint_manifest_section(embedded["entrypoints"]),
        )
        self.assertEqual(
            embedded["contract_fingerprints_contract_fingerprint"],
            manifest["contract_fingerprints_contract_fingerprint"],
        )
        self.assertEqual(embedded["route_precedence_contract"], manifest["route_precedence_contract"])
        self.assertIsNot(embedded["route_precedence_contract"], manifest["route_precedence_contract"])
        self.assertEqual(
            embedded["route_precedence_contract"],
            [
                "shared_target_resolver",
                "shell_refinement",
                "render_terminal_action",
                "render_terminal_selection",
                "render_terminal_card",
            ],
        )
        self.assertEqual(
            embedded["route_precedence_contract_fingerprint"],
            _fingerprint_manifest_section(embedded["route_precedence_contract"]),
        )
        self.assertIsNot(embedded["entrypoints_contract_manifest"], embedded["entrypoints_contract"])
        self.assertEqual(embedded["entrypoints_contract_manifest"], embedded["entrypoints_contract"])
        self.assertEqual(
            embedded["entrypoints_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(embedded["entrypoints_contract"]),
        )
        self.assertEqual(manifest["startup_preview"]["limit"], 99)
        self.assertIsNot(manifest["startup_fields_contract"], manifest["startup_fields"])
        self.assertEqual(manifest["startup_fields_contract"], manifest["startup_fields"])
        self.assertEqual(
            manifest["startup_fields_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_fields"]),
        )
        self.assertIsNot(manifest["startup_fields_contract_manifest"], manifest["startup_fields_contract"])
        self.assertEqual(manifest["startup_fields_contract_manifest"], manifest["startup_fields_contract"])
        self.assertEqual(
            manifest["startup_fields_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_fields_contract"]),
        )
        self.assertIsNot(manifest["startup_preview_contract"], manifest["startup_preview"])
        self.assertEqual(
            manifest["startup_preview_contract"],
            {
                "empty_value": "<empty>",
                "limit": SHELL_UI_STARTUP_PREVIEW_LIMIT,
                "source_field": "basket.item_ids",
            },
        )
        self.assertEqual(
            manifest["startup_preview_contract_fingerprint"],
            _fingerprint_manifest_section(embedded["startup_preview"]),
        )
        self.assertIsNot(manifest["startup_preview_contract_manifest"], manifest["startup_preview_contract"])
        self.assertEqual(manifest["startup_preview_contract_manifest"], manifest["startup_preview_contract"])
        self.assertEqual(
            manifest["startup_preview_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_preview_contract"]),
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback_entrypoint"], "render_terminal_cli_fallback")
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract"],
            "render_terminal_cli_fallback",
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback_target"], target_contract)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_target_contract"], target_contract)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_fingerprint"],
            route_fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            route_fingerprint,
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route"], route_contract)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route_contract"], route_contract)
        self.assertEqual(manifest["route_precedence"], route_contract["route_precedence"])
        self.assertEqual(manifest["route_precedence_contract"], route_contract["route_precedence"])
        self.assertEqual(
            manifest["route_precedence_fingerprint"],
            _fingerprint_manifest_section(route_contract["route_precedence"]),
        )
        self.assertEqual(
            manifest["route_precedence_contract_fingerprint"],
            _fingerprint_manifest_section(route_contract["route_precedence"]),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_contract["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_contract["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            target_contract["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            target_contract["contract_fingerprints_fingerprint"],
        )
        self.assertIsNot(
            manifest["terminal_artifact_cli_fallback_target"],
            manifest["terminal_artifact_cli_fallback_target_contract"],
        )
        self.assertIsNot(
            manifest["terminal_artifact_cli_fallback_route"],
            manifest["terminal_artifact_cli_fallback_route_contract"],
        )
        manifest["terminal_artifact_cli_fallback_target"]["contract_fingerprints"]["render_target_contract"] = (
            "mutated"
        )
        manifest["terminal_artifact_cli_fallback_route"]["route_precedence"][0] = "mutated"
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract"]["contract_fingerprints"][
                "render_target_contract"
            ],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract"]["route_precedence"][0],
            "shared_target_resolver",
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract"]["contract_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract"]["contract_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)

    def test_terminal_artifact_contract_exposes_allowed_actions_contract(self) -> None:
        manifest = describe_terminal_artifact_contract()

        self.assertEqual(manifest["allowed_actions"], sorted(ALLOWED_ACTION_IDS))
        self.assertEqual(
            manifest["allowed_actions_fingerprint"],
            _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
        )
        self.assertEqual(manifest["allowed_actions_contract"], sorted(ALLOWED_ACTION_IDS))
        self.assertEqual(manifest["allowed_actions_contract_manifest"], sorted(ALLOWED_ACTION_IDS))
        self.assertEqual(
            manifest["contract_fingerprints"]["allowed_actions"],
            _fingerprint_manifest_section(sorted(ALLOWED_ACTION_IDS)),
        )

    def test_cli_fallback_contract_exposes_manifest_specific_fingerprint_aliases(self) -> None:
        contract_fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints(
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_route=True,
        )
        route_fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints(
            include_contract_aliases=True,
        )
        manifest_fingerprints = describe_terminal_artifact_cli_fallback_contract_manifest_fingerprints(
            include_terminal_artifact_cli_fallback=True,
            include_terminal_artifact_cli_fallback_route=True,
        )
        route_manifest_fingerprints = describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints(
            include_contract_aliases=True,
        )

        self.assertEqual(manifest_fingerprints, contract_fingerprints)
        self.assertEqual(route_manifest_fingerprints, route_fingerprints)
        self.assertEqual(
            terminal_artifact_cli_fallback_contract_manifest_fingerprints_fingerprint(
                include_terminal_artifact_cli_fallback=True,
                include_terminal_artifact_cli_fallback_route=True,
            ),
            _fingerprint_manifest_section(manifest_fingerprints),
        )
        self.assertEqual(
            terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint(
                include_contract_aliases=True,
            ),
            _fingerprint_manifest_section(route_manifest_fingerprints),
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_contract_manifest_fingerprints,
            describe_terminal_artifact_cli_fallback_contract_manifest_fingerprints,
        )
        self.assertIs(
            public_ui.describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints,
            describe_terminal_artifact_cli_fallback_route_contract_manifest_fingerprints,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_contract_manifest_fingerprints_fingerprint,
            terminal_artifact_cli_fallback_contract_manifest_fingerprints_fingerprint,
        )
        self.assertIs(
            public_ui.terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint,
            terminal_artifact_cli_fallback_route_contract_manifest_fingerprints_fingerprint,
        )

    def test_shell_ui_render_cli_fallback_matches_shared_cli_fallback_renderer(self) -> None:
        shell = ShellUI()
        artifact = {
            "type": "TerminalArtifact",
            "kind": "action",
            "artifact": {
                "type": "ActionRef",
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "json"},
            },
        }

        self.assertEqual(
            shell.render_cli_fallback(artifact, kind="action"),
            render_terminal_cli_fallback(artifact, kind="action"),
        )
        self.assertEqual(
            shell.render_cli_fallback(artifact),
            render_terminal_cli_fallback(artifact),
        )

    def test_shell_ui_render_cli_fallback_uses_shared_resolver_for_clean_card_hints(self) -> None:
        shell = ShellUI()
        artifact = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "json"},
        }

        with patch(
            "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
            return_value=(artifact, "card"),
        ) as resolver:
            with patch(
                "src.qual.ui.shell.render_terminal_cli_fallback",
                return_value="cli-fallback",
            ) as cli_fallback:
                text = shell.render_cli_fallback(artifact, kind="card")

        self.assertEqual(text, "cli-fallback")
        resolver.assert_called_once_with(artifact, kind="card")
        cli_fallback.assert_called_once_with(artifact, kind="card")

    def test_shell_ui_render_cli_fallback_canonicalizes_kind_hint_before_dispatch(self) -> None:
        shell = ShellUI()
        artifact = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "json"},
        }

        with patch(
            "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
            return_value=(artifact, "card"),
        ) as resolver:
            with patch(
                "src.qual.ui.shell.render_terminal_cli_fallback",
                return_value="cli-fallback",
            ) as cli_fallback:
                text = shell.render_cli_fallback(artifact, kind=" Card ")

        self.assertEqual(text, "cli-fallback")
        resolver.assert_called_once_with(artifact, kind="card")
        cli_fallback.assert_called_once_with(artifact, kind="card")

    def test_shell_ui_render_artifact_preserves_card_hint_semantics(self) -> None:
        shell = ShellUI()
        cases = [
            (
                "action envelope",
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "ActionRef",
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "json"},
                    },
                },
            ),
            (
                "selection envelope",
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "SelectionRef",
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                },
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(case=case_name):
                direct_text = render_terminal_artifact(artifact, kind="card")
                shell_text = shell.render_artifact(artifact, kind="card")

                self.assertEqual(shell_text, direct_text)
                self.assertIn("[UnknownCard] <invalid card>", direct_text)
                self.assertIn("Fallback: unknown card", direct_text)

    def test_shell_ui_render_cli_fallback_prefers_pre_resolved_target_hint(self) -> None:
        shell = ShellUI()
        artifact = {
            "type": "TerminalArtifact",
            "kind": "action",
            "artifact": {
                "type": "ActionRef",
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "json"},
            },
        }
        seen_hint: list[tuple[object, str] | None] = []
        expected_text = "[ActionRef] Export\nAction schema v1"

        def _render_with_hint(rendered_artifact: object, *, kind: str | None = None) -> str:
            self.assertIs(rendered_artifact, artifact["artifact"])
            self.assertEqual(kind, "action")
            seen_hint.append(_TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.get())
            return expected_text

        with patch(
            "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
            return_value=(artifact["artifact"], "action"),
        ) as resolver:
            with patch(
                "src.qual.ui.shell.render_terminal_cli_fallback",
                side_effect=_render_with_hint,
                ) as cli_fallback:
                text = shell.render_cli_fallback(artifact)

        self.assertEqual(text, expected_text)
        resolver.assert_called_once_with(artifact, kind=None)
        cli_fallback.assert_called_once_with(artifact["artifact"], kind="action")
        self.assertEqual(seen_hint, [(artifact["artifact"], "action")])
        self.assertIsNone(_TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.get())

    def test_shell_ui_render_cli_fallback_recovers_when_shared_fallback_renderer_raises(self) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "json"},
                ),
                "render_terminal_action",
                "[ActionRef] recovered",
            ),
            (
                "selection",
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
                "render_terminal_selection",
                "[SelectionRef] recovered",
            ),
        ]

        for case_name, artifact, renderer_name, expected_text in cases:
            with self.subTest(case=case_name):
                with patch(
                    "src.qual.ui.shell.render_terminal_cli_fallback",
                    side_effect=RuntimeError("cli fallback boom"),
                ) as cli_fallback:
                    with patch(
                        f"src.qual.ui.shell.{renderer_name}",
                        return_value=expected_text,
                    ) as leaf_renderer:
                        text = shell.render_cli_fallback(artifact)

                self.assertEqual(text, expected_text)
                cli_fallback.assert_called_once_with(artifact, kind=case_name)
                leaf_renderer.assert_called_once_with(artifact)
                self.assertIsNone(_TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.get())

    def test_shell_ui_render_cli_fallback_rejects_leaf_renderer_text_for_card_hints(self) -> None:
        shell = ShellUI()
        artifact = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "json"},
        }

        with patch(
            "src.qual.ui.shell.render_terminal_cli_fallback",
            return_value="[ActionRef] leaked",
        ) as cli_fallback:
            with patch(
                "src.qual.ui.shell.render_terminal_artifact",
                return_value="[ActionRef] leaked",
            ) as generic_renderer:
                with patch(
                    "src.qual.ui.shell.render_terminal_card",
                    return_value="[<missing>] <untitled>",
                ) as card_renderer:
                    text = shell.render_cli_fallback(artifact, kind="card")

        self.assertEqual(text, "[<missing>] <untitled>")
        cli_fallback.assert_called_once_with(artifact, kind="card")
        generic_renderer.assert_called_once_with(artifact, kind="card")
        card_renderer.assert_called_once_with(artifact)

    def test_shell_ui_render_cli_fallback_preserves_shared_invalid_card_fallback_for_malformed_envelopes(
        self,
    ) -> None:
        shell = ShellUI()
        artifact = {
            "type": "TerminalArtifact",
            "artifact": {
                "type": "ActionRef",
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "json"},
            },
        }

        direct_text = render_terminal_cli_fallback(artifact, kind="card")
        shell_text = shell.render_cli_fallback(artifact, kind="card")

        self.assertEqual(shell_text, direct_text)
        self.assertIn("[UnknownCard] <invalid card>", shell_text)
        self.assertNotIn("[ActionRef]", shell_text)
        self.assertNotIn("[SelectionRef]", shell_text)

    def test_shell_ui_render_cli_fallback_recovers_leaf_renderer_when_shared_resolver_raises(self) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "json"},
                ),
                "render_terminal_action",
                "[ActionRef] recovered",
            ),
            (
                "selection",
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
                "render_terminal_selection",
                "[SelectionRef] recovered",
            ),
        ]

        for case_name, artifact, renderer_name, expected_text in cases:
            with self.subTest(case=case_name):
                with patch(
                    "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                    side_effect=RuntimeError("resolver boom"),
                ):
                    seen_hint: list[tuple[object, str] | None] = []

                    def _raise_after_capturing(rendered_artifact: object, *, kind: str | None = None) -> str:
                        seen_hint.append(_TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.get())
                        raise RuntimeError("cli fallback boom")

                    with patch(
                        "src.qual.ui.shell.render_terminal_cli_fallback",
                        side_effect=_raise_after_capturing,
                    ) as cli_fallback:
                        with patch(
                            "src.qual.ui.shell.render_terminal_artifact",
                            side_effect=RuntimeError("artifact boom"),
                        ) as generic_renderer:
                            with patch(
                                f"src.qual.ui.shell.{renderer_name}",
                                return_value=expected_text,
                            ) as leaf_renderer:
                                text = shell.render_cli_fallback(artifact)

                self.assertEqual(text, expected_text)
                cli_fallback.assert_called_once_with(artifact, kind=case_name)
                generic_renderer.assert_not_called()
                leaf_renderer.assert_called_once_with(artifact)
                self.assertEqual(seen_hint, [(artifact, case_name)])
                self.assertIsNone(_TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.get())

    def test_shell_ui_contract_can_opt_in_to_cli_fallback_route_contract(self) -> None:
        default_manifest = describe_shell_ui_contract()
        manifest = describe_shell_ui_contract(include_terminal_artifact_cli_fallback_route=True)
        route_manifest = describe_terminal_artifact_cli_fallback_route_contract()
        target_manifest = describe_terminal_artifact_cli_fallback_target_contract(
            include_terminal_artifact_cli_fallback_route=True,
        )
        fingerprints = describe_shell_ui_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True,
        )

        self.assertEqual(default_manifest["terminal_artifact_cli_fallback_route"], route_manifest)
        self.assertEqual(default_manifest["terminal_artifact_cli_fallback_route_contract"], route_manifest)
        self.assertEqual(
            default_manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest,
        )
        self.assertEqual(
            default_manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            default_manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback_target"], target_manifest)
        self.assertEqual(manifest["terminal_artifact_cli_fallback_target_contract"], target_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            target_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            target_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route"], route_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(manifest["terminal_artifact_cli_fallback_route_contract"], route_manifest)
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
            route_manifest,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(manifest["contract_fingerprints"], fingerprints)
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(fingerprints),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(
                include_terminal_artifact_cli_fallback_route=True,
            ),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            target_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            target_manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            shell_ui_contract_fingerprint(include_terminal_artifact_cli_fallback_route=True),
            manifest["contract_fingerprint"],
        )

    def test_shell_ui_contract_fingerprints_are_public_and_canonical(self) -> None:
        from src.qual.ui import (
            describe_shell_ui_contract_fingerprints as exported_shell_ui_contract_fingerprints,
        )

        manifest = describe_shell_ui_contract()
        fingerprints = describe_shell_ui_contract_fingerprints()
        target_contract = describe_terminal_artifact_cli_fallback_target_contract()
        route_contract = describe_terminal_artifact_cli_fallback_route_contract()
        shell_fingerprint = shell_ui_contract_fingerprint()

        self.assertIs(
            exported_shell_ui_contract_fingerprints,
            describe_shell_ui_contract_fingerprints,
        )
        self.assertEqual(fingerprints["shell_ui_contract_fingerprint"], shell_fingerprint)
        self.assertEqual(fingerprints["shell_ui_fingerprint"], shell_fingerprint)
        self.assertEqual(manifest["contract_fingerprints"], fingerprints)
        self.assertEqual(
            manifest["shell_ui_contract_fingerprints"],
            manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["shell_ui_contract_fingerprints_fingerprint"],
            manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["shell_ui_contract_fingerprints"],
            manifest["contract_fingerprints"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["shell_ui_contract_fingerprints_fingerprint"],
            manifest["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(fingerprints),
        )
        self.assertEqual(
            fingerprints["entrypoints"],
            _fingerprint_manifest_section(manifest["entrypoints"]),
        )
        self.assertEqual(
            fingerprints["entrypoints_contract"],
            _fingerprint_manifest_section(manifest["entrypoints"]),
        )
        self.assertEqual(
            fingerprints["entrypoints_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["entrypoints"]),
        )
        self.assertEqual(
            fingerprints["entrypoints_contract_manifest"],
            _fingerprint_manifest_section(manifest["entrypoints"]),
        )
        self.assertEqual(
            fingerprints["entrypoints_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["entrypoints"]),
        )
        self.assertEqual(
            manifest["startup_fields_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_fields"]),
        )
        self.assertEqual(
            manifest["startup_preview_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_preview"]),
        )
        self.assertEqual(
            fingerprints["startup_fields"],
            _fingerprint_manifest_section(manifest["startup_fields"]),
        )
        self.assertEqual(
            fingerprints["startup_fields_contract"],
            fingerprints["startup_fields"],
        )
        self.assertEqual(
            fingerprints["startup_fields_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_fields"]),
        )
        self.assertEqual(
            fingerprints["startup_fields_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_fields"]),
        )
        self.assertEqual(
            fingerprints["startup_fields_contract_manifest"],
            _fingerprint_manifest_section(manifest["startup_fields"]),
        )
        self.assertEqual(
            fingerprints["startup_fields_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_fields"]),
        )
        self.assertEqual(
            fingerprints["startup_preview"],
            _fingerprint_manifest_section(manifest["startup_preview"]),
        )
        self.assertEqual(
            fingerprints["startup_preview_contract"],
            fingerprints["startup_preview"],
        )
        self.assertEqual(
            fingerprints["startup_preview_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_preview"]),
        )
        self.assertEqual(
            fingerprints["startup_preview_contract_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_preview"]),
        )
        self.assertEqual(
            fingerprints["startup_preview_contract_manifest"],
            _fingerprint_manifest_section(manifest["startup_preview"]),
        )
        self.assertEqual(
            fingerprints["startup_preview_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["startup_preview"]),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprint"],
            _fingerprint_manifest_section("render_terminal_cli_fallback"),
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy"],
            _fingerprint_manifest_section(
                {
                    "recover_typed_leaf_mappings": True,
                    "recover_typed_leaf_payloads": True,
                    "explicit_leaf_instances_rejected_under_card_hints": True,
                    "preserve_raw_leaf_card_default": True,
                }
            ),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_manifest"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints[
                "terminal_artifact_cli_fallback_entrypoint_contract_manifest_fingerprint"
            ],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_rendering_contract_manifest"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_rendering_contract_manifest_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint"],
            route_contract["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            target_contract["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprints"],
            target_contract["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprints"],
            route_contract["contract_fingerprints_fingerprint"],
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy"],
            _fingerprint_manifest_section(
                {
                    "recover_typed_leaf_mappings": True,
                    "recover_typed_leaf_payloads": True,
                    "explicit_leaf_instances_rejected_under_card_hints": True,
                    "preserve_raw_leaf_card_default": True,
                }
            ),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target"],
            target_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest"],
            target_contract,
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_target_contract_manifest_fingerprint"],
            target_contract["contract_fingerprint"],
        )
        self.assertEqual(len(manifest["contract_fingerprints_fingerprint"]), 64)

    def test_terminal_artifact_cli_fallback_policy_contract_accessors_are_public_and_versioned(self) -> None:
        fallback_manifest = describe_terminal_artifact_cli_fallback_contract()
        shell_policy_manifest = describe_terminal_artifact_cli_fallback_shell_refinement_policy_contract()
        resolver_policy_manifest = describe_terminal_artifact_cli_fallback_resolver_failure_policy_contract()
        shell_policy_expected = fallback_manifest["shell_refinement_policy"]
        resolver_policy_expected = fallback_manifest["resolver_failure_policy"]

        self.assertEqual(
            {key: shell_policy_manifest[key] for key in shell_policy_expected},
            shell_policy_expected,
        )
        self.assertEqual(
            {key: resolver_policy_manifest[key] for key in resolver_policy_expected},
            resolver_policy_expected,
        )
        self.assertEqual(
            shell_policy_manifest["contract_fingerprint"],
            terminal_artifact_cli_fallback_shell_refinement_policy_contract_fingerprint(),
        )
        self.assertEqual(
            resolver_policy_manifest["contract_fingerprint"],
            terminal_artifact_cli_fallback_resolver_failure_policy_contract_fingerprint(),
        )
        self.assertEqual(
            shell_policy_manifest["shell_refinement_policy_fingerprint"],
            shell_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            shell_policy_manifest["shell_refinement_policy_contract_fingerprint"],
            shell_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            resolver_policy_manifest["resolver_failure_policy_fingerprint"],
            resolver_policy_manifest["contract_fingerprint"],
        )
        self.assertEqual(
            resolver_policy_manifest["resolver_failure_policy_contract_fingerprint"],
            resolver_policy_manifest["contract_fingerprint"],
        )

    def test_shell_ui_contract_fingerprints_can_include_contract_aliases(self) -> None:
        manifest = describe_shell_ui_contract(include_contract_aliases=True)
        fingerprints = describe_shell_ui_contract_fingerprints(include_contract_aliases=True)
        shell_fingerprint = shell_ui_contract_fingerprint(include_contract_aliases=True)

        self.assertEqual(fingerprints["contract"], shell_fingerprint)
        self.assertEqual(fingerprints["contract_fingerprint"], shell_fingerprint)
        self.assertEqual(fingerprints["shell_ui_contract"], shell_fingerprint)
        self.assertEqual(fingerprints["shell_ui_contract_fingerprint"], shell_fingerprint)
        self.assertEqual(fingerprints["shell_ui_contract_manifest"], shell_fingerprint)
        self.assertEqual(fingerprints["shell_ui_contract_manifest_fingerprint"], shell_fingerprint)
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint(),
        )
        self.assertEqual(
            fingerprints["route_precedence_contract_manifest"],
            _fingerprint_manifest_section(manifest["route_precedence"]),
        )
        self.assertEqual(
            fingerprints["route_precedence_contract_manifest_fingerprint"],
            _fingerprint_manifest_section(manifest["route_precedence"]),
        )
        self.assertEqual(
            fingerprints["renderer_entrypoints_contract_manifest"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_entrypoint_contract_fingerprints"],
            terminal_artifact_cli_fallback_entrypoint_contract_fingerprints_fingerprint(),
        )
        self.assertEqual(
            fingerprints["card_contract_manifest"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["card_contract_manifest_fingerprint"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_fallback_contract_manifest"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_contract_manifest"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_rendering_contract_manifest"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_rendering_contract_manifest_fingerprint"],
            terminal_artifact_rendering_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_fallback_contract_manifest_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["card_contract_manifest"],
            describe_card_contract(),
        )
        self.assertEqual(
            manifest["card_contract_manifest_fingerprint"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_fallback_contract_manifest"],
            describe_terminal_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_fallback_contract_manifest_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_manifest"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["entrypoints_contract_manifest"],
            manifest["shell_ui_contract"]["entrypoints_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["route_precedence_contract_manifest"],
            manifest["shell_ui_contract"]["route_precedence_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["startup_fields_contract_manifest"],
            manifest["shell_ui_contract"]["startup_fields_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["startup_preview_contract_manifest"],
            manifest["shell_ui_contract"]["startup_preview_contract"],
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["card_contract_manifest"],
            describe_card_contract(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_fallback_contract_manifest"],
            describe_terminal_fallback_contract(),
        )
        self.assertEqual(
            manifest["shell_ui_contract"]["terminal_artifact_cli_fallback_contract_manifest"],
            describe_terminal_artifact_cli_fallback_contract(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_manifest"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["card_hint_recovery_policy_contract"],
            _fingerprint_manifest_section(
                {
                    "recover_typed_leaf_mappings": True,
                    "recover_typed_leaf_payloads": True,
                    "explicit_leaf_instances_rejected_under_card_hints": True,
                    "preserve_raw_leaf_card_default": True,
                }
            ),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["shell_ui_contract_manifest"],
            shell_fingerprint,
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_manifest_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["card_contract_manifest"],
            card_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["contract_fingerprints"]["terminal_fallback_contract_manifest"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_contract_manifest"],
            describe_terminal_artifact_renderer_entrypoints_contract(),
        )
        self.assertEqual(
            manifest["renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["renderer_entrypoints_contract_manifest_fingerprint"],
            terminal_artifact_renderer_entrypoints_contract_fingerprint(),
        )
        self.assertEqual(manifest["contract_fingerprints"], fingerprints)
        self.assertEqual(
            manifest["contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(fingerprints),
        )

    def test_shell_ui_render_startup_uses_contract_preview_constants(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=["alpha", "beta", "gamma"]),
        )
        empty_runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=[]),
        )

        with patch("src.qual.ui.shell.SHELL_UI_STARTUP_PREVIEW_LIMIT", 2), patch(
            "src.qual.ui.shell.SHELL_UI_STARTUP_EMPTY_PREVIEW",
            "<none>",
        ):
            text = ShellUI().render_startup(runtime)
            empty_text = ShellUI().render_startup(empty_runtime)

        self.assertEqual(SHELL_UI_STARTUP_PREVIEW_LIMIT, 3)
        self.assertEqual(SHELL_UI_STARTUP_EMPTY_PREVIEW, "<empty>")
        self.assertIn("- context_preview: alpha, beta, +1 more item", text)
        self.assertIn("- context_preview: <none>", empty_text)

    def test_shell_ui_render_startup_handles_zero_preview_limit_without_leading_separator(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=["alpha"]),
        )

        with patch("src.qual.ui.shell.SHELL_UI_STARTUP_PREVIEW_LIMIT", 0):
            text = ShellUI().render_startup(runtime)

        self.assertIn("- context_preview: +1 more item", text)
        self.assertNotIn("- context_preview: , +1 more item", text)

    def test_shell_ui_render_startup_collapses_duplicate_preview_items(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=False),
            basket=SimpleNamespace(item_ids=["alpha", "alpha", "beta", "gamma"]),
        )

        with patch("src.qual.ui.shell.SHELL_UI_STARTUP_PREVIEW_LIMIT", 3):
            text = ShellUI().render_startup(runtime)

        self.assertIn("- context_items: 4", text)
        self.assertIn("- context_preview: alpha, beta, gamma", text)
        self.assertNotIn("- context_preview: alpha, alpha", text)

    def test_terminal_artifact_cli_fallback_route_contract_fingerprints_are_public_and_canonical(self) -> None:
        from src.qual.ui import (
            describe_terminal_artifact_cli_fallback_route_contract_fingerprints as exported_route_fingerprints,
        )

        manifest = describe_terminal_artifact_cli_fallback_route_contract()
        manifest_alias = describe_terminal_artifact_cli_fallback_route_contract_manifest()
        manifest_fingerprint = terminal_artifact_cli_fallback_route_contract_manifest_fingerprint()
        fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints()
        fingerprints_with_self = describe_terminal_artifact_cli_fallback_route_contract_fingerprints(
            include_terminal_artifact_cli_fallback_route=True,
        )

        self.assertIs(
            exported_route_fingerprints,
            describe_terminal_artifact_cli_fallback_route_contract_fingerprints,
        )
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(manifest_fingerprint, manifest["contract_fingerprint"])
        self.assertNotIn(
            "terminal_artifact_cli_fallback_route_contract_manifest",
            manifest["terminal_artifact_cli_fallback_route_contract_manifest"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_manifest"][
                "terminal_artifact_cli_fallback_route_contract_fingerprint"
            ],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(
            manifest["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"],
            manifest["contract_fingerprint"],
        )
        self.assertEqual(fingerprints, manifest["contract_fingerprints"])
        self.assertEqual(
            fingerprints["render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_policy_contract"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["kind_resolution"],
            terminal_artifact_kind_resolution_fingerprint(),
        )
        self.assertEqual(
            fingerprints["fallback_recovery"],
            terminal_artifact_fallback_recovery_fingerprint(),
        )
        self.assertEqual(
            fingerprints["shell_refinement_policy"],
            _fingerprint_manifest_section(manifest["shell_refinement_policy"]),
        )
        self.assertEqual(
            fingerprints["resolver_failure_policy"],
            _fingerprint_manifest_section(manifest["resolver_failure_policy"]),
        )
        self.assertEqual(
            terminal_artifact_cli_fallback_route_contract_fingerprints_fingerprint(),
            _fingerprint_manifest_section(fingerprints),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(len(fingerprints_with_self["terminal_artifact_cli_fallback_route"]), 64)

    def test_terminal_artifact_cli_fallback_fingerprint_maps_return_fresh_snapshots(self) -> None:
        contract_kwargs = {
            "include_terminal_artifact_cli_fallback": True,
            "include_terminal_artifact_cli_fallback_route": True,
            "include_contract_aliases": True,
        }
        entrypoint_kwargs = {"include_contract_aliases": True}
        route_kwargs = {
            "include_terminal_artifact_cli_fallback_route": True,
            "include_contract_aliases": True,
        }

        contract_fingerprints = describe_terminal_artifact_cli_fallback_contract_fingerprints(**contract_kwargs)
        entrypoint_fingerprints = describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints(
            **entrypoint_kwargs,
        )
        route_fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints(**route_kwargs)

        contract_snapshot = dict(contract_fingerprints)
        entrypoint_snapshot = dict(entrypoint_fingerprints)
        route_snapshot = dict(route_fingerprints)

        contract_fingerprints["terminal_artifact_cli_fallback_contract"] = "mutated"
        entrypoint_fingerprints["renderer_entrypoints"] = "mutated"
        route_fingerprints["route_precedence"] = "mutated"

        self.assertEqual(
            describe_terminal_artifact_cli_fallback_contract_fingerprints(**contract_kwargs),
            contract_snapshot,
        )
        self.assertEqual(
            describe_terminal_artifact_cli_fallback_entrypoint_contract_fingerprints(**entrypoint_kwargs),
            entrypoint_snapshot,
        )
        self.assertEqual(
            describe_terminal_artifact_cli_fallback_route_contract_fingerprints(**route_kwargs),
            route_snapshot,
        )

    def test_terminal_artifact_cli_fallback_route_contract_fingerprints_can_opt_into_aliases(self) -> None:
        fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints(
            include_contract_aliases=True,
        )
        default_fingerprints = describe_terminal_artifact_cli_fallback_route_contract_fingerprints()

        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_manifest"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_route_contract_manifest_fingerprint"],
            terminal_artifact_cli_fallback_route_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_fallback"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_fallback_contract"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_policy"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_policy_contract"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["render_target_contract"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["terminal_artifact_cli_fallback_target_contract_fingerprint"],
            terminal_artifact_cli_fallback_target_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact_cli_fallback_route", default_fingerprints)
        self.assertNotIn("terminal_artifact_cli_fallback_route_contract", default_fingerprints)

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

    def test_terminal_artifact_envelope_contract_manifest_is_versioned_and_shared(self) -> None:
        manifest = describe_terminal_artifact_envelope_contract()
        terminal_artifact_manifest = describe_terminal_artifact_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["terminal_artifact_schema_version"], TERMINAL_ARTIFACT_SCHEMA_VERSION)
        self.assertEqual(manifest["type"], "TerminalArtifact")
        self.assertEqual(manifest["required_fields"], ["kind", "artifact"])
        self.assertEqual(manifest["optional_fields"], ["contract_version", "a2ui_version"])
        self.assertEqual(manifest["kind_field"], "kind")
        self.assertEqual(manifest["artifact_field"], "artifact")
        self.assertEqual(manifest["supported_kinds"], ["card", "action", "selection"])
        self.assertEqual(manifest["contract_fingerprint"], terminal_artifact_envelope_contract_fingerprint())
        self.assertEqual(
            manifest["terminal_artifact_envelope_fingerprint"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_envelope_contract_fingerprint"],
            terminal_artifact_envelope_contract_fingerprint(),
        )
        self.assertEqual(terminal_artifact_manifest["envelope"], manifest)

    def test_terminal_artifact_render_target_contract_manifest_is_versioned_and_embedded_in_a2ui_contract(self) -> None:
        manifest = describe_terminal_artifact_render_target_contract()
        manifest_alias = describe_terminal_artifact_render_target_contract_manifest()
        manifest_alias_fingerprint = terminal_artifact_render_target_contract_manifest_fingerprint()
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
        self.assertEqual(
            manifest["raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_raw_leaf_card_default_policy_contract"],
            describe_terminal_artifact_raw_leaf_card_default_policy_contract(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract"]["contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract_manifest"],
            manifest["terminal_artifact_render_target_contract"],
        )
        self.assertIsNot(manifest["terminal_artifact_render_target_contract"], manifest)
        self.assertIsNot(
            manifest["terminal_artifact_render_target_contract_manifest"],
            manifest["terminal_artifact_render_target_contract"],
        )
        self.assertEqual(
            manifest["terminal_artifact_render_target_contract_manifest_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(manifest_alias, manifest)
        self.assertEqual(
            manifest_alias_fingerprint,
            terminal_artifact_render_target_contract_fingerprint(),
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
                "raw_leaf_card_default_policy_contract": terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
                "kind_resolution": terminal_artifact_kind_resolution_fingerprint(),
                "fallback_recovery": terminal_artifact_fallback_recovery_fingerprint(),
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
        self.assertEqual(
            a2ui_manifest["terminal_artifact_cli_fallback_target_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(a2ui_manifest["terminal_artifact_cli_fallback_target_contract_fingerprints"]),
        )
        self.assertEqual(
            a2ui_manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints_fingerprint"],
            _fingerprint_manifest_section(
                a2ui_manifest["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprints"],
            ),
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
            fingerprints["kind_resolution"],
            terminal_artifact_kind_resolution_fingerprint(),
        )
        self.assertEqual(
            fingerprints["fallback_recovery"],
            terminal_artifact_fallback_recovery_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_contract"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints["raw_leaf_card_default_policy_contract"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertNotIn("terminal_artifact_render_target", fingerprints)
        self.assertNotIn("terminal_artifact_render_target_contract_manifest", fingerprints)
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_kind_contracts_fingerprint"],
            terminal_artifact_kind_contracts_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_manifest"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_render_target_contract_manifest_fingerprint"],
            terminal_artifact_render_target_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_fallback_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_fallback_contract_fingerprint"],
            terminal_fallback_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_policy_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
        )
        self.assertEqual(
            fingerprints_with_self["raw_leaf_card_default_policy_contract_fingerprint"],
            terminal_artifact_raw_leaf_card_default_policy_contract_fingerprint(),
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

    def test_terminal_artifact_envelope_builder_is_idempotent_for_matching_envelopes(self) -> None:
        cases = [
            (
                "action",
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
            ),
            (
                "selection",
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                    selected=True,
                ),
            ),
            (
                "card",
                {
                    "type": "GenericCard",
                    "title": " Run Log ",
                    "a2ui_version": 1,
                    "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                    "actions": [],
                },
            ),
        ]

        for case_name, source in cases:
            with self.subTest(case=case_name):
                envelope = build_terminal_artifact_envelope(source, kind=case_name)
                rebuilt = build_terminal_artifact_envelope(envelope, kind=case_name)

                self.assertEqual(rebuilt, envelope)
                validate_terminal_artifact_envelope(rebuilt)

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

    def test_terminal_artifact_payload_normalizer_converts_tuple_values_to_lists(self) -> None:
        card_source = {
            "type": "GenericCard",
            "title": " Run Log ",
            "a2ui_version": 1,
            "blocks": (
                {"type": "MarkdownBlock", "markdown": "First"},
                {"type": "MarkdownBlock", "markdown": "Second"},
            ),
            "actions": (
                ActionRef(
                    id="copy_to_clipboard",
                    label="Copy",
                    payload={"text": "payload"},
                ),
                ActionRef(
                    id="apply_patch",
                    label="Apply",
                    payload={"patch_id": "p1"},
                ),
            ),
            "debug": {"tags": ("beta", "alpha")},
        }

        normalized = normalize_terminal_artifact_payload(card_source, kind="card")
        envelope = build_terminal_artifact_envelope(card_source, kind="card")

        self.assertIsInstance(normalized["blocks"], list)
        self.assertIsInstance(normalized["actions"], list)
        self.assertIsInstance(normalized["debug"]["tags"], list)
        self.assertEqual(
            normalized["blocks"],
            [
                {"type": "MarkdownBlock", "markdown": "First"},
                {"type": "MarkdownBlock", "markdown": "Second"},
            ],
        )
        self.assertEqual(
            [action["id"] for action in normalized["actions"]],
            ["apply_patch", "copy_to_clipboard"],
        )
        self.assertEqual(normalized["debug"]["tags"], ["beta", "alpha"])
        self.assertEqual(envelope["artifact"], normalized)
        self.assertNotIsInstance(normalized["blocks"], tuple)
        self.assertNotIsInstance(normalized["actions"], tuple)

    def test_terminal_artifact_payload_normalizer_preserves_raw_leaf_card_default_snapshots(self) -> None:
        raw_leaf = {
            "id": " export_document ",
            "label": " Export ",
            "payload": {"nested": {"b": 2, "a": 1}, "format": "md"},
            "trace_id": "drop-me",
        }

        normalized = normalize_terminal_artifact_payload(raw_leaf, kind="card")
        envelope = build_terminal_artifact_envelope(raw_leaf, kind="card")
        validate_terminal_artifact_envelope(envelope)
        rendered_text = render_terminal_artifact(envelope)
        cli_fallback_text = render_terminal_cli_fallback(envelope)

        raw_leaf["label"] = "Changed"
        raw_leaf["payload"]["nested"]["a"] = 99

        self.assertEqual(
            normalized,
            {
                "id": " export_document ",
                "label": " Export ",
                "payload": {"format": "md", "nested": {"a": 1, "b": 2}},
                "trace_id": "drop-me",
            },
        )
        self.assertEqual(envelope["artifact"], normalized)
        self.assertEqual(list(envelope["artifact"].keys()), ["id", "label", "payload", "trace_id"])
        self.assertEqual(list(envelope["artifact"]["payload"].keys()), ["format", "nested"])
        self.assertEqual(list(envelope["artifact"]["payload"]["nested"].keys()), ["a", "b"])
        self.assertIn("[<missing>] <untitled>", rendered_text)
        self.assertNotIn("[ActionRef]", rendered_text)
        self.assertNotIn("[SelectionRef]", rendered_text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", rendered_text)
        self.assertEqual(cli_fallback_text, rendered_text)

    def test_terminal_artifact_payload_normalizer_rejects_typed_leaf_mappings_when_card_kind_is_explicit(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            normalize_terminal_artifact_payload(
                {
                    "type": "ActionRef",
                    "id": " export_document ",
                    "label": " Export ",
                    "payload": {"format": "md"},
                },
                kind="card",
            )

        with self.assertRaises(ValueError):
            normalize_terminal_artifact_payload(
                {
                    "type": "SelectionRef",
                    "id": " choice-1 ",
                    "label": " Choice ",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                kind="card",
            )

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
        self.assertIn("- label: Export", action_text)
        self.assertIn("- label: Choice", selection_text)
        for text in (action_text, selection_text):
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

    def test_terminal_artifact_cli_fallback_entrypoint_rejects_conflicting_card_hints_for_authoritative_envelopes(
        self,
    ) -> None:
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
        partial_action_payload = {
            "id": "export_document",
            "payload": {"format": "md"},
            "confirm": {"title": "Confirm export", "message": "Export the draft?"},
        }
        partial_selection_payload = {
            "id": "choice-1",
            "payload": {"nested": {"items": [1, 2]}},
            "selected": True,
        }
        raw_leaf_envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
                "trace_id": "drop-me",
            },
        }
        minimal_raw_leaf_envelope = build_terminal_artifact_envelope(
            {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
            kind="card",
        )

        for case_name, artifact in (
            ("action envelope", action_envelope),
            ("selection envelope", selection_envelope),
            ("partial action payload", partial_action_payload),
            ("partial selection payload", partial_selection_payload),
        ):
            with self.subTest(case=case_name):
                text = render_terminal_cli_fallback(artifact, kind="card")
                self.assertEqual(text, shell.render_artifact(artifact, kind="card"))
                self.assertIn("[UnknownCard] <invalid card>", text)
                self.assertIn("- raw:", text)
                self.assertNotIn("[ActionRef]", text)
                self.assertNotIn("[SelectionRef]", text)

        raw_leaf_text = render_terminal_cli_fallback(raw_leaf_envelope, kind="card")
        self.assertIn("[<missing>] <untitled>", raw_leaf_text)
        self.assertNotIn("[UnknownCard] <invalid card>", raw_leaf_text)
        self.assertNotIn("[ActionRef]", raw_leaf_text)
        self.assertNotIn("[SelectionRef]", raw_leaf_text)

        minimal_raw_leaf_text = render_terminal_cli_fallback(minimal_raw_leaf_envelope)
        self.assertEqual(minimal_raw_leaf_text, render_terminal_artifact(minimal_raw_leaf_envelope))
        self.assertEqual(shell.render_artifact(minimal_raw_leaf_envelope), minimal_raw_leaf_text)
        self.assertEqual(
            resolve_terminal_artifact_cli_fallback_target(minimal_raw_leaf_envelope),
            (minimal_raw_leaf_envelope["artifact"], "card"),
        )
        self.assertIn("[<missing>] <untitled>", minimal_raw_leaf_text)
        self.assertNotIn("[ActionRef]", minimal_raw_leaf_text)
        self.assertNotIn("[SelectionRef]", minimal_raw_leaf_text)

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

    def test_shell_ui_recovers_when_shared_renderers_return_non_string(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch(
            "src.qual.ui.shell.render_terminal_cli_fallback",
            return_value={"oops": "not text"},
        ):
            with patch(
                "src.qual.ui.shell.render_terminal_artifact",
                return_value={"oops": "not text"},
            ):
                with patch(
                    "src.qual.ui.shell.render_terminal_card",
                    return_value={"oops": "not text"},
                ):
                    text = shell.render_artifact(raw_leaf)

        self.assertIn("[UnknownCard] <invalid card>", text)
        self.assertIn("Fallback: unknown card", text)
        self.assertNotIsInstance(text, dict)

    def test_shell_ui_recovers_when_shared_renderers_return_blank_string(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch(
            "src.qual.ui.shell.render_terminal_cli_fallback",
            return_value="",
        ):
            with patch(
                "src.qual.ui.shell.render_terminal_artifact",
                return_value="",
            ):
                with patch(
                    "src.qual.ui.shell.render_terminal_card",
                    return_value="",
                ):
                    text = shell.render_artifact(raw_leaf)

        self.assertIn("[UnknownCard] <invalid card>", text)
        self.assertIn("Fallback: unknown card", text)
        self.assertNotEqual(text.strip(), "")

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

    def test_shell_ui_forwards_explicit_raw_leaf_kind_hints_during_fallback(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        for hint, expected_prefix in (("action", "[ActionRef] Export"), ("selection", "[SelectionRef] Export")):
            with self.subTest(kind=hint):
                with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")) as primary_renderer:
                    with patch(
                        "src.qual.ui.shell.render_terminal_cli_fallback",
                        return_value="cli-fallback",
                    ) as cli_fallback:
                        text = shell.render_artifact(raw_leaf, kind=hint)

                self.assertIn(expected_prefix, text)
                self.assertNotIn("cli-fallback", text)
                self.assertNotIn("[<missing>] <untitled>", text)
                primary_renderer.assert_not_called()
                cli_fallback.assert_not_called()

    def test_shell_ui_forwards_explicit_raw_leaf_kind_hints_during_cli_fallback(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        cases = [
            ("action", "render_terminal_action", "[ActionRef] Export\nAction schema v1"),
            ("selection", "render_terminal_selection", "[SelectionRef] Export\nSelection schema v1"),
        ]

        for hint, renderer_name, expected_text in cases:
            with self.subTest(kind=hint):
                with patch(
                    "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                    side_effect=RuntimeError("resolver boom"),
                ) as resolver:
                    with patch(
                        "src.qual.ui.shell.render_terminal_cli_fallback",
                        return_value="cli-fallback",
                    ) as cli_fallback:
                        with patch(f"src.qual.ui.shell.{renderer_name}", return_value=expected_text) as leaf_renderer:
                            text = shell.render_cli_fallback(raw_leaf, kind=hint)

                self.assertEqual(text, expected_text)
                resolver.assert_not_called()
                cli_fallback.assert_not_called()
                leaf_renderer.assert_called_once_with(raw_leaf)

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

    def test_shell_ui_reuses_pre_resolved_cli_fallback_targets_for_explicit_card_hints(self) -> None:
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
                text = shell.render_artifact(raw_leaf, kind="card")

        self.assertIn("[<missing>] <untitled>", text)
        self.assertNotIn("[ActionRef]", text)
        self.assertNotIn("[SelectionRef]", text)
        resolver.assert_called_once_with(raw_leaf, kind="card")

    def test_shell_ui_does_not_retry_fallback_resolution_on_explicit_card_failure(self) -> None:
        shell = ShellUI()
        artifact = _OpaqueValue()

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch.object(ShellUI, "_resolve_fallback_artifact", side_effect=RuntimeError("resolver boom")) as resolver:
                text = shell.render_artifact(artifact, kind="card")

        self.assertIn("[UnknownCard] <invalid card>", text)
        self.assertIn("Fallback: unknown card", text)
        self.assertIn("<non-json:_OpaqueValue>", text)
        self.assertEqual(resolver.call_count, 1)
        resolver.assert_called_once_with(artifact, kind="card")

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

    def test_shell_ui_forwards_explicit_raw_leaf_kind_hints_even_when_shared_resolver_raises(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch(
                "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                side_effect=RuntimeError("resolver boom"),
            ) as resolver:
                with patch(
                    "src.qual.ui.shell.render_terminal_cli_fallback",
                    return_value="cli-fallback",
                ) as cli_fallback:
                    text = shell.render_artifact(raw_leaf, kind="action")

        self.assertIn("[ActionRef] Export", text)
        self.assertNotIn("cli-fallback", text)
        self.assertNotIn("[<missing>] <untitled>", text)
        resolver.assert_not_called()
        cli_fallback.assert_not_called()

    def test_shell_ui_forwards_explicit_raw_leaf_kind_hints_in_cli_fallback(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        action_text = shell.render_cli_fallback(raw_leaf, kind="action")
        selection_text = shell.render_cli_fallback(raw_leaf, kind="selection")
        default_text = shell.render_cli_fallback(raw_leaf)

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("[SelectionRef] Export", selection_text)
        self.assertIn("[<missing>] <untitled>", default_text)
        self.assertNotIn("[<missing>] <untitled>", action_text)
        self.assertNotIn("[<missing>] <untitled>", selection_text)
        self.assertNotIn("[ActionRef]", default_text)
        self.assertNotIn("[SelectionRef]", default_text)

    def test_terminal_artifact_cli_fallback_forwards_explicit_raw_leaf_kind_hints(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        action_text = render_terminal_cli_fallback(raw_leaf, kind="action")
        selection_text = render_terminal_cli_fallback(raw_leaf, kind="selection")
        shell_action_text = shell.render_cli_fallback(raw_leaf, kind="action")
        shell_selection_text = shell.render_cli_fallback(raw_leaf, kind="selection")

        self.assertEqual(action_text, shell_action_text)
        self.assertEqual(selection_text, shell_selection_text)
        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("[SelectionRef] Export", selection_text)
        self.assertNotIn("[<missing>] <untitled>", action_text)
        self.assertNotIn("[<missing>] <untitled>", selection_text)
        self.assertNotIn("[ActionRef]", selection_text)
        self.assertNotIn("[SelectionRef]", action_text)

    def test_shell_ui_forwards_explicit_raw_leaf_kind_hints(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        action_text = shell.render_artifact(raw_leaf, kind="action")
        selection_text = shell.render_artifact(raw_leaf, kind="selection")

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("[SelectionRef] Export", selection_text)
        self.assertNotIn("[<missing>] <untitled>", action_text)
        self.assertNotIn("[<missing>] <untitled>", selection_text)

    def test_shell_ui_prefers_specific_leaf_fallbacks_over_generic_artifact_retry(self) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "confirm": {"title": "Approve", "message": "Proceed?"},
                },
                "[ActionRef] Export",
                "render_terminal_action",
            ),
            (
                "selection",
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
                "[SelectionRef] Choice",
                "render_terminal_selection",
            ),
        ]

        for fallback_kind, artifact, expected_prefix, renderer_name in cases:
            with self.subTest(kind=fallback_kind):
                with patch("src.qual.ui.shell.render_terminal_cli_fallback", side_effect=RuntimeError("boom")):
                    with patch(
                        "src.qual.ui.shell.render_terminal_artifact",
                        return_value="generic-fallback",
                    ) as generic_renderer:
                        with patch(
                            f"src.qual.ui.shell.{renderer_name}",
                            return_value=expected_prefix,
                        ) as specific_renderer:
                            text = shell.render_artifact(artifact, kind=fallback_kind)

                self.assertEqual(text, expected_prefix)
                specific_renderer.assert_called_once_with(artifact)
                generic_renderer.assert_not_called()

    def test_shell_ui_skips_generic_artifact_retry_for_leaf_fallbacks_when_specific_renderer_fails(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
                "[ActionRef] <invalid action>",
                "render_terminal_action",
            ),
            (
                "selection",
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                "[SelectionRef] <invalid selection>",
                "render_terminal_selection",
            ),
        ]

        for fallback_kind, artifact, expected_prefix, renderer_name in cases:
            with self.subTest(kind=fallback_kind):
                with patch("src.qual.ui.shell.render_terminal_cli_fallback", side_effect=RuntimeError("boom")):
                    with patch(
                        "src.qual.ui.shell.render_terminal_artifact",
                        return_value="generic-fallback",
                    ) as generic_renderer:
                        with patch(
                            f"src.qual.ui.shell.{renderer_name}",
                            side_effect=RuntimeError(f"{fallback_kind} boom"),
                        ):
                            text = shell.render_artifact(artifact, kind=fallback_kind)

                self.assertIn(expected_prefix, text)
                generic_renderer.assert_not_called()

    def test_shell_ui_recovers_leaf_renderer_when_cli_fallback_returns_card_output(self) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "confirm": {"title": "Approve", "message": "Proceed?"},
                },
                "[ActionRef] Export",
                "render_terminal_action",
            ),
            (
                "selection",
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
                "[SelectionRef] Choice",
                "render_terminal_selection",
            ),
        ]

        for fallback_kind, artifact, expected_prefix, renderer_name in cases:
            with self.subTest(kind=fallback_kind):
                with patch(
                    "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                    return_value=(artifact, fallback_kind),
                ):
                    with patch(
                        "src.qual.ui.shell.render_terminal_cli_fallback",
                        return_value="[GenericCard] Fallback view for FutureCard",
                    ) as cli_fallback:
                        with patch(
                            f"src.qual.ui.shell.{renderer_name}",
                            return_value=expected_prefix,
                        ) as specific_renderer:
                            text = shell.render_artifact(artifact)

                self.assertEqual(text, expected_prefix)
                cli_fallback.assert_called_once_with(artifact, kind=fallback_kind)
                specific_renderer.assert_called_once_with(artifact)

    def test_shell_ui_keeps_ambiguous_raw_leaf_payloads_on_card_default_for_malformed_envelopes_when_shared_resolver_raises(
        self,
    ) -> None:
        shell = ShellUI()
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            },
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            with patch(
                "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                side_effect=RuntimeError("resolver boom"),
            ):
                text = shell.render_artifact(envelope)

        self.assertIn("[<missing>] <untitled>", text)
        self.assertNotIn("[ActionRef]", text)
        self.assertNotIn("[SelectionRef]", text)
        self.assertNotIn("[TerminalArtifact] <invalid artifact>", text)

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

    def test_shell_ui_defaults_unclassified_fallback_recovery_to_card(self) -> None:
        shell = ShellUI()
        artifact = _OpaqueValue()

        with patch(
            "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
            side_effect=RuntimeError("resolver boom"),
        ):
            fallback_artifact, fallback_kind = shell._resolve_fallback_artifact(artifact, kind=None)

        self.assertIs(fallback_artifact, artifact)
        self.assertEqual(fallback_kind, "card")

    def test_shell_ui_infer_fallback_kind_preserves_raw_leaf_card_default_before_schema_inference(self) -> None:
        shell = ShellUI()

        action_like_raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        selection_like_raw_leaf = {
            "id": "choice-1",
            "label": "Choice",
            "payload": {"nested": {"items": [1, 2]}},
        }

        self.assertEqual(shell._infer_fallback_kind(action_like_raw_leaf), "card")
        self.assertEqual(shell._infer_fallback_kind(selection_like_raw_leaf), "card")

    def test_shell_ui_infer_fallback_kind_stays_in_lockstep_with_shared_mapping_classifier(self) -> None:
        shell = ShellUI()
        cases = [
            (
                "card",
                {
                    "type": "GenericCard",
                    "title": "Run Log",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                    "actions": [],
                },
            ),
            (
                "action",
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "confirm": {"title": "Approve", "message": "Export now?"},
                },
            ),
            (
                "selection",
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
            ),
        ]

        for expected_kind, artifact in cases:
            with self.subTest(kind=expected_kind):
                self.assertEqual(_infer_terminal_artifact_kind_from_mapping(artifact), expected_kind)
                self.assertEqual(shell._infer_fallback_kind(artifact), expected_kind)

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

    def test_terminal_artifact_cli_fallback_recovers_leaf_kind_when_shared_resolver_underflows_to_card(
        self,
    ) -> None:
        cases = [
            (
                "action",
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "confirm": {"title": "Approve", "message": "Proceed?"},
                },
                "[ActionRef] Export",
                "Action schema v1",
            ),
            (
                "selection",
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
                "[SelectionRef] Choice",
                "Selection schema v1",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_schema in cases:
            with self.subTest(case=case_name):
                with patch(
                    "src.qual.ui.a2ui.resolve_terminal_artifact_cli_fallback_target",
                    return_value=(artifact, "card"),
                ):
                    text = render_terminal_cli_fallback(artifact)
                self.assertIn(expected_prefix, text)
                self.assertIn(expected_schema, text)
                self.assertNotIn("[UnknownCard] <invalid card>", text)

    def test_terminal_artifact_cli_fallback_keeps_typed_leaf_dataclasses_invalid_when_shared_resolver_underflows_to_card(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
                "[ActionRef] Export",
                "Action schema v1",
            ),
            (
                "selection",
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
                "[SelectionRef] Choice",
                "Selection schema v1",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_schema in cases:
            with self.subTest(case=case_name):
                with patch(
                    "src.qual.ui.a2ui.resolve_terminal_artifact_cli_fallback_target",
                    return_value=(artifact, "card"),
                ):
                    with patch(
                        "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                        return_value=(artifact, "card"),
                    ):
                        cli_text = render_terminal_cli_fallback(artifact, kind="card")
                        shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertIn("Fallback: unknown card", cli_text)
                self.assertIn("Action policy: copy_to_clipboard_only", cli_text)
                self.assertNotIn(expected_prefix, cli_text)
                self.assertNotIn(expected_schema, cli_text)

    def test_terminal_artifact_cli_fallback_keeps_explicit_typed_leaf_mappings_invalid_when_shared_resolver_underflows_to_card(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "type": "ActionRef",
                    "id": " export_document ",
                    "label": " Export ",
                    "payload": {"format": "md"},
                },
                "[ActionRef] Export",
                "Action schema v1",
            ),
            (
                "selection",
                {
                    "type": "SelectionRef",
                    "id": " choice-1 ",
                    "label": " Choice ",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                "[SelectionRef] Choice",
                "Selection schema v1",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_schema in cases:
            with self.subTest(case=case_name):
                with patch(
                    "src.qual.ui.a2ui.resolve_terminal_artifact_cli_fallback_target",
                    return_value=(artifact, "card"),
                ):
                    with patch(
                        "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                        return_value=(artifact, "card"),
                    ):
                        cli_text = render_terminal_cli_fallback(artifact, kind="card")
                        shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertIn("Action policy: copy_to_clipboard_only", cli_text)
                self.assertNotIn(expected_prefix, cli_text)
                self.assertNotIn(expected_schema, cli_text)

    def test_public_cli_fallback_target_refinement_helper_recovers_leaf_kinds(self) -> None:
        cases = [
            (
                "action",
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "confirm": {"title": "Approve", "message": "Proceed?"},
                },
                "action",
                "[ActionRef] Export",
            ),
            (
                "selection",
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
                "selection",
                "[SelectionRef] Choice",
            ),
        ]

        for case_name, artifact, requested_kind, expected_prefix in cases:
            with self.subTest(case=case_name):
                refined_artifact, refined_kind = refine_terminal_artifact_cli_fallback_target(
                    artifact,
                    "card",
                    requested_kind=requested_kind,
                )

                self.assertIs(refined_artifact, artifact)
                self.assertEqual(refined_kind, requested_kind)
                self.assertIn(
                    expected_prefix,
                    render_terminal_cli_fallback(refined_artifact, kind=refined_kind),
                )

    def test_terminal_artifact_cli_fallback_keeps_raw_leaf_card_default_when_shared_resolver_underflows_to_card(
        self,
    ) -> None:
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        with patch(
            "src.qual.ui.a2ui.resolve_terminal_artifact_cli_fallback_target",
            return_value=(raw_leaf, "card"),
        ):
            text = render_terminal_cli_fallback(raw_leaf)

        self.assertIn("[<missing>] <untitled>", text)
        self.assertIn("- label: Export", text)
        self.assertNotIn("[ActionRef]", text)
        self.assertNotIn("[SelectionRef]", text)

    def test_terminal_artifact_cli_fallback_refines_local_card_underflow_after_shared_resolver_failure(
        self,
    ) -> None:
        artifact = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
            "confirm": {"title": "Approve", "message": "Proceed?"},
        }

        with patch(
            "src.qual.ui.a2ui.resolve_terminal_artifact_cli_fallback_target",
            side_effect=RuntimeError("boom"),
        ):
            with patch(
                "src.qual.ui.a2ui._resolve_terminal_artifact_render_target",
                return_value=(artifact, "card"),
            ):
                text = render_terminal_cli_fallback(artifact)

        self.assertIn("[ActionRef] Export", text)
        self.assertIn("Action schema v1", text)
        self.assertNotIn("[UnknownCard] <invalid card>", text)

    def test_terminal_artifact_cli_fallback_ignores_stale_context_hints_for_other_artifacts(self) -> None:
        stale_artifact = {
            "id": "choice-1",
            "label": "Choice",
            "payload": {"nested": {"items": [1, 2]}},
            "selected": True,
        }
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }

        token = _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.set((stale_artifact, "selection"))
        try:
            text = render_terminal_cli_fallback(raw_leaf)
        finally:
            _TERMINAL_ARTIFACT_CLI_FALLBACK_TARGET_HINT.reset(token)

        self.assertEqual(text, render_terminal_card(raw_leaf))
        self.assertIn("[<missing>] <untitled>", text)
        self.assertIn("- label: Export", text)
        self.assertNotIn("[SelectionRef] Choice", text)
        self.assertNotIn("[ActionRef] Export", text)

    def test_shell_ui_recovers_leaf_kind_when_shared_resolver_underflows_to_card_and_cli_fallback_fails(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                    "confirm": {"title": "Approve", "message": "Proceed?"},
                },
                "[ActionRef] Export",
                "action",
            ),
            (
                "selection",
                {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                    "selected": True,
                },
                "[SelectionRef] Choice",
                "selection",
            ),
        ]

        for case_name, artifact, expected_prefix, expected_kind in cases:
            with self.subTest(case=case_name):
                with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
                    with patch(
                        "src.qual.ui.shell.resolve_terminal_artifact_cli_fallback_target",
                        return_value=(artifact, "card"),
                    ):
                        with patch(
                            "src.qual.ui.shell.render_terminal_cli_fallback",
                            side_effect=RuntimeError("cli fallback boom"),
                        ) as cli_fallback:
                            text = shell.render_artifact(artifact)

                self.assertIn(expected_prefix, text)
                self.assertIn(f"{case_name.capitalize()} schema v1", text)
                cli_fallback.assert_called_once_with(artifact, kind=expected_kind)

    def test_shell_ui_retries_shared_renderer_on_resolved_fallback_target_after_cli_fallback_failure(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": raw_leaf,
            "trace_id": "drop-me",
        }

        with patch("src.qual.ui.shell.render_terminal_cli_fallback", side_effect=RuntimeError("cli fallback boom")):
            with patch("src.qual.ui.shell.render_terminal_artifact") as generic_renderer:
                generic_renderer.side_effect = (
                    lambda artifact, kind=None: "resolved-target"
                    if artifact is raw_leaf
                    else AssertionError("expected the resolved raw leaf payload")
                )
                text = shell.render_artifact(envelope)

        self.assertEqual(text, "resolved-target")
        generic_renderer.assert_called_once_with(raw_leaf, kind="card")

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
        self.assertEqual(manifest["schema_version"], CARD_CONTRACT_VERSION)
        self.assertEqual(manifest["card_contract_version"], CARD_CONTRACT_VERSION)
        self.assertEqual(manifest["card_version"], CARD_CONTRACT_VERSION)
        self.assertEqual(manifest["type"], "CardContract")
        self.assertEqual(manifest["card_fingerprint"], card_contract_fingerprint())
        self.assertEqual(manifest["contract_fingerprint"], manifest["card_fingerprint"])
        self.assertEqual(manifest["contract_manifest"]["contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(manifest["contract_manifest_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(len(manifest["card_fingerprint"]), 64)
        self.assertEqual(a2ui_manifest["card_contract"], manifest)
        self.assertEqual(a2ui_manifest["card_contract_manifest"], manifest)
        self.assertEqual(a2ui_manifest["card_contract_manifest_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(a2ui_manifest["card_contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(manifest["card_schemas"], a2ui_manifest["schemas"]["cards"])
        self.assertEqual(a2ui_manifest["schemas"]["card_contract"], manifest)
        self.assertEqual(manifest["fallbacks"], a2ui_manifest["fallbacks"])

    def test_terminal_fallback_contract_manifest_is_versioned_and_embedded_in_a2ui_contract(self) -> None:
        manifest = describe_terminal_fallback_contract()
        a2ui_manifest = describe_a2ui_contract()

        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["schema_version"], TERMINAL_FALLBACK_SCHEMA_VERSION)
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
        self.assertEqual(manifest["contract_manifest"]["contract_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(manifest["contract_manifest_fingerprint"], manifest["contract_fingerprint"])
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(a2ui_manifest["schemas"]["terminal_fallback"], manifest)

    def test_action_contract_manifest_exposes_contract_fingerprint_alias(self) -> None:
        manifest = describe_action_contract()

        self.assertEqual(manifest["contract_fingerprint"], manifest["action_fingerprint"])
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(manifest["schema_version"], A2UI_ACTION_SCHEMA_VERSION)
        self.assertEqual(manifest["action_schema_version"], A2UI_ACTION_SCHEMA_VERSION)
        self.assertEqual(manifest["action_version"], A2UI_ACTION_SCHEMA_VERSION)
        self.assertEqual(manifest["action_contract_version"], A2UI_ACTION_SCHEMA_VERSION)
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

    def test_action_and_selection_refs_round_trip_version_metadata(self) -> None:
        action = normalize_action_ref(
            {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
                "schema_version": A2UI_ACTION_SCHEMA_VERSION,
                "a2ui_version": 1,
            }
        )
        selection = normalize_selection_ref(
            {
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
                "schema_version": SELECTION_SCHEMA_VERSION,
                "a2ui_version": 1,
            }
        )

        self.assertEqual(action.schema_version, A2UI_ACTION_SCHEMA_VERSION)
        self.assertEqual(action.a2ui_version, 1)
        self.assertEqual(selection.schema_version, SELECTION_SCHEMA_VERSION)
        self.assertEqual(selection.a2ui_version, 1)
        self.assertEqual(
            action,
            ActionRef(
                id="export_document",
                label="Export",
                payload={"format": "md"},
                schema_version=A2UI_ACTION_SCHEMA_VERSION,
                a2ui_version=1,
            ),
        )
        self.assertEqual(
            selection,
            SelectionRef(
                id="choice-1",
                label="Choice",
                payload={"nested": {"items": [1, 2]}},
                schema_version=SELECTION_SCHEMA_VERSION,
                a2ui_version=1,
            ),
        )

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
        self.assertIn("A2UI v1", text)
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
        self.assertIn("A2UI v1", invalid)
        self.assertIn('"icon":"sparkle"', invalid)

    def test_terminal_renderer_invalid_card_preview_canonicalizes_action_list_order(self) -> None:
        card_variants = [
            {
                "type": "ActionRef",
                "id": "launch_missiles",
                "label": "Run",
                "payload": {"operation": "x"},
                "actions": [
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    {
                        "id": "copy_to_clipboard",
                        "label": "Copy JSON",
                        "payload": {"text": "safe"},
                    },
                ],
            },
            {
                "type": "ActionRef",
                "id": "launch_missiles",
                "label": "Run",
                "payload": {"operation": "x"},
                "actions": [
                    {
                        "id": "copy_to_clipboard",
                        "label": "Copy JSON",
                        "payload": {"text": "safe"},
                    },
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                ],
            },
        ]

        rendered_cards = [render_terminal_card(card) for card in card_variants]
        rendered_cli_fallback = [render_terminal_cli_fallback(card, kind="card") for card in card_variants]

        self.assertEqual(rendered_cards[0], rendered_cards[1])
        self.assertEqual(rendered_cli_fallback[0], rendered_cli_fallback[1])
        self.assertEqual(rendered_cards[0], rendered_cli_fallback[0])
        self.assertIn("[UnknownCard] <invalid card>", rendered_cards[0])
        self.assertIn('"actions":[{"id":"copy_to_clipboard"', rendered_cards[0])
        self.assertLess(
            rendered_cards[0].index('"id":"copy_to_clipboard"'),
            rendered_cards[0].index('"id":"export_document"'),
        )

    def test_terminal_renderer_invalid_action_preview_strips_malformed_terminal_envelope_metadata(
        self,
    ) -> None:
        invalid = render_terminal_action(
            {
                "type": "TerminalArtifact",
                "kind": "dialog",
                "artifact": {
                    "id": "launch_missiles",
                    "label": "Run",
                    "payload": {"operation": "x"},
                },
                "trace_id": "drop-me",
            }
        )

        self.assertIn("[ActionRef] <invalid action>", invalid)
        self.assertIn("Action schema v1", invalid)
        self.assertIn('"id":"launch_missiles"', invalid)
        self.assertNotIn("TerminalArtifact", invalid)
        self.assertNotIn("trace_id", invalid)

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

    def test_terminal_artifact_explicit_leaf_kind_hints_stay_authoritative(self) -> None:
        action_payload = {
            "type": "ActionRef",
            "id": "copy_to_clipboard",
            "label": "Copy JSON",
            "payload": {"text": "hi"},
        }
        selection_payload = {
            "type": "SelectionRef",
            "id": "choice-1",
            "label": "Choice",
            "payload": {"nested": {"items": [1, 2]}},
        }

        action_as_selection = render_terminal_artifact(action_payload, kind="selection")
        selection_as_action = render_terminal_artifact(selection_payload, kind="action")
        cli_action_as_selection = render_terminal_cli_fallback(action_payload, kind="selection")
        cli_selection_as_action = render_terminal_cli_fallback(selection_payload, kind="action")
        shell = ShellUI()

        self.assertIn("[SelectionRef] <invalid selection>", action_as_selection)
        self.assertIn("Selection schema v1", action_as_selection)
        self.assertIn("[ActionRef] <invalid action>", selection_as_action)
        self.assertIn("Action schema v1", selection_as_action)
        self.assertEqual(cli_action_as_selection, action_as_selection)
        self.assertEqual(cli_selection_as_action, selection_as_action)
        self.assertEqual(shell.render_artifact(action_payload, kind="selection"), action_as_selection)
        self.assertEqual(shell.render_artifact(selection_payload, kind="action"), selection_as_action)
        self.assertEqual(shell.render_cli_fallback(action_payload, kind="selection"), action_as_selection)
        self.assertEqual(shell.render_cli_fallback(selection_payload, kind="action"), selection_as_action)

    def test_terminal_artifact_malformed_envelope_leaf_hints_stay_kind_authoritative(self) -> None:
        malformed_action_envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": {
                "type": "ActionRef",
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
                "confirm": {"title": "Approve", "message": "Proceed?"},
            },
        }
        shell = ShellUI()

        action_text = render_terminal_cli_fallback(malformed_action_envelope, kind="action")
        selection_text = render_terminal_cli_fallback(malformed_action_envelope, kind="selection")
        shell_action_text = shell.render_artifact(malformed_action_envelope, kind="action")
        shell_selection_text = shell.render_artifact(malformed_action_envelope, kind="selection")
        shell_cli_action_text = shell.render_cli_fallback(malformed_action_envelope, kind="action")
        shell_cli_selection_text = shell.render_cli_fallback(malformed_action_envelope, kind="selection")

        self.assertIn("[ActionRef] Export", action_text)
        self.assertIn("- confirm:", action_text)
        self.assertIn("[ActionRef] Export", shell_action_text)
        self.assertIn("- confirm:", shell_action_text)
        self.assertIn("[ActionRef] Export", shell_cli_action_text)
        self.assertIn("- confirm:", shell_cli_action_text)
        self.assertIn("[SelectionRef] <invalid selection>", selection_text)
        self.assertIn("[SelectionRef] <invalid selection>", shell_selection_text)
        self.assertIn("[SelectionRef] <invalid selection>", shell_cli_selection_text)
        self.assertNotIn("[ActionRef]", selection_text)
        self.assertNotIn("[ActionRef]", shell_selection_text)
        self.assertNotIn("[ActionRef]", shell_cli_selection_text)

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

    def test_terminal_artifact_cli_fallback_entrypoint_keeps_explicit_typed_leaves_invalid_under_card_hints(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
            ),
            (
                "selection",
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(case=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_artifact(artifact, kind="card")
                shell_cli_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertIn("[UnknownCard] <invalid card>", shell_text)
                self.assertIn("Fallback: unknown card", shell_text)
                self.assertIn("Action policy: copy_to_clipboard_only", shell_text)
                self.assertEqual(cli_text, shell_cli_text)
                self.assertIn("[UnknownCard] <invalid card>", shell_cli_text)
                self.assertNotIn("[ActionRef]", cli_text)
                self.assertNotIn("[SelectionRef]", cli_text)
                self.assertNotIn("[ActionRef]", shell_cli_text)
                self.assertNotIn("[SelectionRef]", shell_cli_text)

    def test_shell_ui_keeps_explicit_typed_leaf_instances_invalid_when_cli_fallback_recovery_raises(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                ActionRef(
                    id=" export_document ",
                    label=" Export ",
                    payload={"format": "md"},
                ),
            ),
            (
                "action_mapping",
                {
                    "type": "ActionRef",
                    "id": " export_document ",
                    "label": " Export ",
                    "payload": {"format": "md"},
                },
            ),
            (
                "selection",
                SelectionRef(
                    id=" choice-1 ",
                    label=" Choice ",
                    payload={"nested": {"items": [1, 2]}},
                ),
            ),
            (
                "selection_mapping",
                {
                    "type": "SelectionRef",
                    "id": " choice-1 ",
                    "label": " Choice ",
                    "payload": {"nested": {"items": [1, 2]}},
                },
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(case=case_name):
                with patch(
                    "src.qual.ui.shell.render_terminal_cli_fallback",
                    side_effect=RuntimeError("cli fallback boom"),
                ):
                    cli_text = shell.render_cli_fallback(artifact, kind="card")
                render_text = shell.render_artifact(artifact, kind="card")

                self.assertEqual(cli_text, render_text)
                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertIn("Action policy: copy_to_clipboard_only", cli_text)
                self.assertNotIn("[ActionRef]", cli_text)
                self.assertNotIn("[SelectionRef]", cli_text)

    def test_terminal_artifact_cli_fallback_entrypoint_matches_shell_for_malformed_card_hint_envelopes(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "ActionRef",
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                },
            ),
            (
                "selection",
                {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": {
                        "type": "SelectionRef",
                        "id": "choice-1",
                        "label": "Choice",
                        "payload": {"nested": {"items": [1, 2]}},
                    },
                },
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(case=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn("[ActionRef]" if case_name == "action" else "[SelectionRef]", cli_text)
                self.assertNotIn("[UnknownCard] <invalid card>", cli_text)

    def test_terminal_artifact_cli_fallback_distinguishes_card_and_non_card_malformed_envelopes(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                {
                    "type": "ActionRef",
                    "id": "export_document",
                    "label": "Export",
                    "payload": {"format": "md"},
                },
            ),
            (
                "selection",
                {
                    "type": "SelectionRef",
                    "id": "selected",
                    "label": "Selected",
                    "payload": {"value": True},
                },
            ),
        ]

        for case_name, payload in cases:
            with self.subTest(case=case_name):
                card_envelope = {
                    "type": "TerminalArtifact",
                    "kind": "card",
                    "artifact": payload,
                }
                dialog_envelope = {
                    "type": "TerminalArtifact",
                    "kind": "dialog",
                    "artifact": payload,
                }

                card_cli_text = render_terminal_cli_fallback(card_envelope, kind="card")
                dialog_cli_text = render_terminal_cli_fallback(dialog_envelope, kind="card")
                card_shell_text = shell.render_cli_fallback(card_envelope, kind="card")
                dialog_shell_text = shell.render_cli_fallback(dialog_envelope, kind="card")

                expected_header = (
                    "[ActionRef] Export" if case_name == "action" else "[SelectionRef] Selected"
                )
                self.assertEqual(card_cli_text, card_shell_text)
                self.assertEqual(dialog_cli_text, dialog_shell_text)
                self.assertIn("[UnknownCard] <invalid card>", card_cli_text)
                self.assertIn("[UnknownCard] <invalid card>", card_shell_text)
                self.assertIn(expected_header, dialog_cli_text)
                self.assertIn(expected_header, dialog_shell_text)
                self.assertNotIn(expected_header, card_cli_text)
                self.assertNotIn(expected_header, card_shell_text)

    def test_terminal_artifact_cli_fallback_entrypoint_preserves_card_hints_for_valid_typed_envelopes(
        self,
    ) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                build_terminal_artifact_envelope(
                    ActionRef(
                        id=" export_document ",
                        label=" Export ",
                        payload={"format": "md"},
                    ),
                    kind="action",
                ),
            ),
            (
                "selection",
                build_terminal_artifact_envelope(
                    SelectionRef(
                        id=" choice-1 ",
                        label=" Choice ",
                        payload={"nested": {"items": [1, 2]}},
                        selected=True,
                    ),
                    kind="selection",
                ),
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(case=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertNotIn("[ActionRef]", cli_text)
                self.assertNotIn("[SelectionRef]", cli_text)

    def test_terminal_artifact_cli_fallback_entrypoint_rejects_plain_cards_under_leaf_hints(self) -> None:
        shell = ShellUI()
        card = {
            "type": "GenericCard",
            "title": "Run Log",
            "a2ui_version": 1,
            "blocks": [{"type": "MarkdownBlock", "markdown": "Hi"}],
            "actions": [],
        }

        for kind, invalid_prefix in (
            ("action", "[ActionRef] <invalid action>"),
            ("selection", "[SelectionRef] <invalid selection>"),
        ):
            with self.subTest(kind=kind):
                cli_text = render_terminal_cli_fallback(card, kind=kind)
                shell_text = shell.render_cli_fallback(card, kind=kind)

                self.assertEqual(cli_text, shell_text)
                self.assertEqual(cli_text.splitlines()[0], invalid_prefix)
                self.assertNotIn("[GenericCard] Run Log", cli_text)

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

    def test_shell_ui_preserves_card_kind_hint_for_nested_card_envelopes_with_raw_leaf_defaults(self) -> None:
        shell = ShellUI()
        raw_leaf = {
            "id": "export_document",
            "label": "Export",
            "payload": {"format": "md"},
        }
        nested_card_envelope = {
            "type": "TerminalArtifact",
            "kind": "card",
            "artifact": build_terminal_artifact_envelope(raw_leaf, kind="card"),
        }

        with patch("src.qual.ui.shell.render_terminal_artifact", side_effect=RuntimeError("boom")):
            text = shell.render_artifact(nested_card_envelope, kind="card")

        self.assertEqual(text, render_terminal_cli_fallback(nested_card_envelope, kind="card"))
        self.assertIn("[<missing>] <untitled>", text)
        self.assertIn("- label: Export", text)
        self.assertNotIn("[UnknownCard] <invalid card>", text)

    def test_terminal_artifact_cli_fallback_entrypoint_recovers_nested_typed_leaves_under_card_hints(
        self,
    ) -> None:
        shell = ShellUI()
        nested_envelopes = [
            (
                "action",
                {
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
                },
            ),
            (
                "selection",
                {
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
                },
            ),
        ]

        for case_name, artifact in nested_envelopes:
            with self.subTest(case=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertEqual(cli_text, shell_text)
                self.assertIn(
                    "[ActionRef] Export" if case_name == "action" else "[SelectionRef] Choice",
                    cli_text,
                )
                self.assertNotIn("[UnknownCard] <invalid card>", cli_text)
                self.assertNotIn("Action policy: copy_to_clipboard_only", cli_text)

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

    def test_terminal_artifact_cli_fallback_keeps_explicit_leaf_payloads_on_invalid_card_path(self) -> None:
        shell = ShellUI()
        cases = [
            (
                "action",
                ActionRef(
                    id="export_document",
                    label="Export",
                    payload={"format": "md"},
                ),
            ),
            (
                "selection",
                SelectionRef(
                    id="choice-1",
                    label="Choice",
                    payload={"nested": {"items": [1, 2]}},
                ),
            ),
        ]

        for case_name, artifact in cases:
            with self.subTest(case=case_name):
                cli_text = render_terminal_cli_fallback(artifact, kind="card")
                shell_text = shell.render_cli_fallback(artifact, kind="card")

                self.assertIn("[UnknownCard] <invalid card>", cli_text)
                self.assertEqual(shell_text, cli_text)
                self.assertNotIn("[ActionRef]", cli_text)
                self.assertNotIn("[SelectionRef]", cli_text)

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

    def test_terminal_card_renderer_rejects_non_string_nested_envelope_render_results(self) -> None:
        envelope = {
            "type": "TerminalArtifact",
            "kind": "dialog",
            "artifact": _OpaqueValue(),
            "trace_id": "drop-me",
        }

        with patch("src.qual.ui.a2ui.render_terminal_artifact", return_value={"oops": "not text"}):
            text = render_terminal_card(envelope)

        self.assertIn("[TerminalArtifact] <untitled>", text)
        self.assertNotIsInstance(text, dict)
        self.assertNotIn("oops", text)

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

    def test_terminal_card_renderer_rejects_non_string_nested_leaf_render_results(self) -> None:
        cases = [
            (
                "action",
                build_terminal_artifact_envelope(
                    ActionRef(
                        id=" export_document ",
                        label=" Export ",
                        payload={"format": "md"},
                    ),
                    kind="action",
                ),
                "render_terminal_action",
                "[ActionRef] <invalid action>",
            ),
            (
                "selection",
                build_terminal_artifact_envelope(
                    SelectionRef(
                        id=" choice-1 ",
                        label=" Choice ",
                        payload={"nested": {"items": [1, 2]}},
                    ),
                    kind="selection",
                ),
                "render_terminal_selection",
                "[SelectionRef] <invalid selection>",
            ),
        ]

        for case_name, envelope, renderer_name, expected_prefix in cases:
            with self.subTest(case=case_name):
                with patch("src.qual.ui.a2ui.render_terminal_artifact", side_effect=RuntimeError("boom")):
                    with patch(
                        f"src.qual.ui.a2ui.{renderer_name}",
                        return_value={"oops": "not text"},
                    ):
                        text = render_terminal_card(envelope)

                self.assertIn(expected_prefix, text)
                self.assertNotIsInstance(text, dict)
                self.assertNotIn("oops", text)

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

    def test_engine_card_materializers_snapshot_debug_payloads(self) -> None:
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
            actions_supported=(
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
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )
        supported_debug = {"tags": ["alpha", "beta"]}
        generic_debug = {"tags": ["gamma", "delta"]}

        supported_card = engine_prepare_card(
            {
                "type": "RunLogCard",
                "title": " Run Log ",
                "a2ui_version": 1,
                "blocks": [{"type": "MarkdownBlock", "markdown": "Kept"}],
                "actions": [],
                "debug": supported_debug,
            },
            caps,
        )
        generic_card = engine_prepare_card(
            {
                "type": "GenericCard",
                "title": " Patch ",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Kept"}],
                "actions": [],
                "debug": generic_debug,
            },
            caps,
        )

        supported_debug["tags"].append("mutated")
        generic_debug["tags"].append("mutated")

        self.assertEqual(supported_card["debug"], {"tags": ["alpha", "beta"]})
        self.assertEqual(generic_card["debug"], {"tags": ["gamma", "delta"]})
        self.assertIsNot(supported_card["debug"], supported_debug)
        self.assertIsNot(generic_card["debug"], generic_debug)
        self.assertIsNot(supported_card["debug"]["tags"], supported_debug["tags"])
        self.assertIsNot(generic_card["debug"]["tags"], generic_debug["tags"])

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

    def test_typed_action_and_selection_mappings_are_valid_leaf_contract_inputs(self) -> None:
        validate_action_ref(
            {"type": "ActionRef", "id": "export_document", "label": "Export", "payload": {"format": "md"}}
        )
        validate_selection_ref(
            {
                "type": "SelectionRef",
                "id": "choice-1",
                "label": "Choice",
                "payload": {"nested": {"items": [1, 2]}},
            }
        )

    def test_terminal_renderer_preserves_typed_action_refs_inside_generic_card_actions(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Run Log",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
            "actions": [
                {
                    "type": "ActionRef",
                    "id": "copy_to_clipboard",
                    "label": "Copy JSON",
                    "payload": {"text": "{}"},
                }
            ],
        }

        validate_generic_card(card)
        text = render_terminal_card(card)

        self.assertIn("[GenericCard] Run Log", text)
        self.assertIn("- Copy JSON (copy_to_clipboard)", text)
        self.assertNotIn("Actions filtered out by allowlist or validation", text)

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

    def test_terminal_renderer_keeps_action_order_deterministic_across_input_variants(self) -> None:
        card_variants = [
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "safe"}],
                "actions": [
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                    {
                        "id": "copy_to_clipboard",
                        "label": "Copy JSON",
                        "payload": {"text": "safe"},
                    },
                ],
            },
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "safe"}],
                "actions": [
                    {
                        "id": "copy_to_clipboard",
                        "label": "Copy JSON",
                        "payload": {"text": "safe"},
                    },
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                    },
                ],
            },
        ]

        rendered = [render_terminal_card(card) for card in card_variants]

        self.assertEqual(rendered[0], rendered[1])
        self.assertIn("- Copy JSON (copy_to_clipboard)", rendered[0])
        self.assertIn("- Export (export_document)", rendered[0])

    def test_terminal_renderer_materializes_generator_actions_for_cli_fallback(self) -> None:
        def action_stream():
            yield {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            }
            yield {
                "id": "copy_to_clipboard",
                "label": "Copy JSON",
                "payload": {"text": "safe"},
            }

        text = render_terminal_cli_fallback(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "safe"}],
                "actions": action_stream(),
            }
        )

        self.assertIn("- Copy JSON (copy_to_clipboard)", text)
        self.assertIn("- Export (export_document)", text)

    def test_terminal_renderer_materializes_generator_actions_for_card_rendering(self) -> None:
        def action_stream():
            yield {
                "id": "export_document",
                "label": "Export",
                "payload": {"format": "md"},
            }
            yield {
                "id": "copy_to_clipboard",
                "label": "Copy JSON",
                "payload": {"text": "safe"},
            }

        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "safe"}],
                "actions": action_stream(),
            }
        )

        self.assertIn("- Copy JSON (copy_to_clipboard)", text)
        self.assertIn("- Export (export_document)", text)

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

    def test_terminal_renderer_infers_generic_fallback_for_generator_actions(self) -> None:
        def action_stream():
            yield {
                "id": "copy_to_clipboard",
                "label": "Copy JSON",
                "payload": {"text": "{}"},
            }

        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback view for FutureCard",
                "blocks": [],
                "actions": action_stream(),
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

    def test_invalid_selection_renderer_strips_malformed_terminal_envelope_metadata(self) -> None:
        text = render_terminal_selection(
            {
                "type": "TerminalArtifact",
                "kind": "dialog",
                "artifact": {
                    "id": "choice-1",
                    "label": "Choice",
                    "payload": {"nested": {"items": [1, 2]}},
                },
                "trace_id": "drop-me",
            }
        )

        self.assertIn("[SelectionRef] <invalid selection>", text)
        self.assertIn("Selection schema v1", text)
        self.assertIn('"id":"choice-1"', text)
        self.assertNotIn("TerminalArtifact", text)
        self.assertNotIn("trace_id", text)

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

    def test_shell_ui_escapes_control_characters_in_bootstrap_metadata(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(
                project_name="Demo\nProject",
                root_dir="/tmp/demo\u202e",
                is_locked=False,
            ),
            basket=SimpleNamespace(item_ids=[]),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn("- project: Demo\\x0aProject", text)
        self.assertIn("- vault: /tmp/demo\\u202e", text)
        self.assertNotIn("Demo\nProject", text)
        self.assertNotIn("/tmp/demo\u202e", text)

    def test_shell_ui_normalizes_locked_flag_in_bootstrap_metadata(self) -> None:
        runtime = SimpleNamespace(
            vault=SimpleNamespace(project_name="Demo", root_dir="/tmp/demo", is_locked=True),
            basket=SimpleNamespace(item_ids=[]),
        )

        text = ShellUI().render_startup(runtime)

        self.assertIn("- locked: true", text)
        self.assertNotIn("- locked: True", text)

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
        first_type_name, first_preview_token, first_tiebreaker = ShellUI._snapshot_item_sort_key(
            _OpaqueValue()
        )
        second_type_name, second_preview_token, second_tiebreaker = ShellUI._snapshot_item_sort_key(
            _OpaqueValue()
        )

        self.assertEqual(first_type_name, "_OpaqueValue")
        self.assertEqual(second_type_name, "_OpaqueValue")
        self.assertEqual(first_preview_token, "<non-json:_OpaqueValue>")
        self.assertEqual(second_preview_token, "<non-json:_OpaqueValue>")
        self.assertNotEqual(first_tiebreaker, second_tiebreaker)

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

    def test_engine_prepare_card_accepts_iterable_actions_for_rendering(self) -> None:
        card = engine_prepare_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Safe content"}],
                "actions": (
                    action
                    for action in [
                        {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "alpha"}},
                        {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "alpha"}},
                    ]
                ),
            },
            _capabilities(),
        )

        self.assertEqual([action["id"] for action in card["actions"]], ["copy_to_clipboard"])
        self.assertEqual(card["actions"][0]["label"], "Copy JSON")
        self.assertIn("Safe content", render_terminal_card(card))


if __name__ == "__main__":
    unittest.main()
