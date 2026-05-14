from __future__ import annotations

import json
import unittest
from dataclasses import dataclass

from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    a2ui_contract_fingerprint,
    build_unknown_card,
    describe_a2ui_contract,
    GENERIC_FALLBACK_SUBTITLE,
    engine_prepare_card,
    execute_action_with_policy_gate,
    normalize_action_ref,
    render_terminal_card,
    studio_materialize_card,
    UNKNOWN_FALLBACK_SUBTITLE,
    validate_generic_card,
    validate_unknown_card,
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

    def test_contract_manifest_is_versioned_and_fingerprintable(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["contract_version"], 2)
        self.assertEqual(manifest["contract_fingerprint"], a2ui_contract_fingerprint())
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(
            manifest["cards"],
            {
                "generic": "GenericCard",
                "unknown": "UnknownCard",
                "reserved": ["GenericCard", "UnknownCard"],
                "specialized": [
                    "ProposedEditCard",
                    "EvidenceCard",
                    "QuestionsCard",
                    "RunLogCard",
                ],
            },
        )
        self.assertEqual(
            manifest["fallbacks"],
            {
                "generic_card": {
                    "type": "GenericCard",
                    "action_policy": "client_allowlist",
                    "allowed_actions": ["copy_to_clipboard"],
                    "actions": [
                        {
                            "id": "copy_to_clipboard",
                            "label": "Copy JSON",
                            "version": 1,
                            "payload_fields": ["text"],
                        }
                    ],
                },
                "unknown_card": {
                    "type": "UnknownCard",
                    "action_policy": "copy_to_clipboard_only",
                    "allowed_actions": ["copy_to_clipboard"],
                    "default_preview_bytes": 8192,
                    "actions": [
                        {
                            "id": "copy_to_clipboard",
                            "label": "Copy JSON",
                            "version": 1,
                            "payload_fields": ["text"],
                        }
                    ],
                },
            },
        )
        self.assertEqual(
            manifest["schemas"]["cards"],
            [
                {
                    "type": "GenericCard",
                    "version": 1,
                    "required_fields": ["type", "title", "a2ui_version", "blocks", "actions"],
                    "optional_fields": ["subtitle", "debug"],
                    "allowed_actions": [
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
                    "action_policy": "client_allowlist",
                },
                {
                    "type": "UnknownCard",
                    "version": 1,
                    "required_fields": ["type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions"],
                    "optional_fields": [],
                    "allowed_actions": ["copy_to_clipboard"],
                    "action_policy": "copy_to_clipboard_only",
                },
            ],
        )
        self.assertEqual(
            manifest["schemas"]["actions"],
            [
                {
                    "type": "ActionRef",
                    "version": 1,
                    "required_fields": ["id", "label", "payload"],
                    "optional_fields": ["confirm", "policy_sensitive"],
                    "payload_schemas": [
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
                }
            ],
        )
        self.assertEqual(
            manifest["primitive_blocks"],
            [
                {"type": "MarkdownBlock", "fields": ["markdown"]},
                {"type": "KeyValueBlock", "fields": ["items"]},
                {"type": "ListBlock", "fields": ["items"]},
                {"type": "TableBlock", "fields": ["rows"]},
                {"type": "AlertBlock", "fields": ["severity", "title", "message"]},
                {"type": "ProgressBlock", "fields": ["status_text", "title"]},
                {"type": "CodeBlock", "fields": ["code", "language", "collapsed"]},
            ],
        )
        self.assertEqual(
            [entry["id"] for entry in manifest["actions"]],
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
            [entry["id"] for entry in manifest["actions"]],
            sorted(entry["id"] for entry in manifest["actions"]),
        )
        self.assertEqual(len(a2ui_contract_fingerprint()), 64)

    def test_session_store_rejects_invalid_capabilities(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2",
                _capabilities(
                    actions_supported=("apply_patch", "launch_missiles"),
                ),
            )

    def test_session_store_rejects_non_sequence_capability_fields(self) -> None:
        store = A2UISessionStore()
        base_kwargs = {
            "a2ui_version": 1,
            "client_name": "Exegesis Studio",
            "cards_supported": ("ProposedEditCard",),
            "primitive_blocks_supported": (
                "MarkdownBlock",
                "KeyValueBlock",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
            "actions_supported": (
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
            "max_payload_bytes": 1_000_000,
            "supports_streaming": True,
        }

        for field_name, override in (
            ("cards_supported", "RunLogCard"),
            ("primitive_blocks_supported", "MarkdownBlock"),
            ("actions_supported", "copy_to_clipboard"),
        ):
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValueError):
                    store.register(
                        f"sess-{field_name}",
                        A2UICapabilities(**{**base_kwargs, field_name: override}),
                    )

    def test_session_store_rejects_reserved_card_types(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2b",
                _capabilities(cards_supported=("UnknownCard",)),
            )

        with self.assertRaises(ValueError):
            store.register(
                "sess-2c",
                _capabilities(cards_supported=("GenericCard",)),
            )

    def test_session_store_rejects_blank_supported_card_types(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2d",
                _capabilities(cards_supported=("",)),
            )

    def test_session_store_rejects_whitespace_padded_supported_card_types(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2e",
                _capabilities(cards_supported=(" RunLogCard ",)),
            )

    def test_session_store_rejects_duplicate_supported_card_types(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2f",
                _capabilities(cards_supported=("RunLogCard", "RunLogCard")),
            )

    def test_session_store_rejects_canonical_action_ids_only(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2g",
                _capabilities(actions_supported=("apply_patch", " copy_to_clipboard ")),
            )

    def test_session_store_rejects_duplicate_supported_action_ids(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2h",
                _capabilities(actions_supported=("apply_patch", "apply_patch")),
            )

    def test_session_store_rejects_non_bool_streaming_flag(self) -> None:
        store = A2UISessionStore()
        caps = A2UICapabilities(
            a2ui_version=1,
            client_name="Exegesis Studio",
            cards_supported=("ProposedEditCard",),
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
            supports_streaming="yes",  # type: ignore[arg-type]
        )
        with self.assertRaises(ValueError):
            store.register("sess-2i", caps)

    def test_session_store_rejects_bool_version_and_payload_size(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2i-1",
                A2UICapabilities(
                    a2ui_version=True,  # type: ignore[arg-type]
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
                ),
            )

        with self.assertRaises(ValueError):
            store.register(
                "sess-2i-2",
                A2UICapabilities(
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
                    max_payload_bytes=True,  # type: ignore[arg-type]
                    supports_streaming=True,
                ),
            )

    def test_session_store_rejects_canonical_primitive_block_types_only(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2j",
                A2UICapabilities(
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
                        " CodeBlock ",
                    ),
                    actions_supported=("apply_patch",),
                    max_payload_bytes=1_000_000,
                    supports_streaming=True,
                ),
            )

    def test_session_store_rejects_future_a2ui_version(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-3",
                A2UICapabilities(
                    a2ui_version=2,
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
                ),
            )

    def test_engine_falls_back_to_generic_for_unsupported_specialized_card(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {
            "type": "ProposedEditCard",
            "title": "Patch",
            "blocks": [
                {"type": "MarkdownBlock", "markdown": "Safe content"},
                {"type": "ChartBlock", "series": [1, 2, 3]},
                {"type": "ListBlock", "items": ["alpha", "beta"]},
            ],
        }
        card = engine_prepare_card(payload, caps)
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(
            [block["type"] for block in card["blocks"]],
            ["AlertBlock", "MarkdownBlock", "ListBlock", "CodeBlock"],
        )
        self.assertTrue(card["blocks"][-1]["collapsed"])
        self.assertTrue(card["blocks"][-1]["code"].startswith('{\n  "blocks": ['))
        self.assertIn('\n  "title": "Patch",', card["blocks"][-1]["code"])
        self.assertIn('\n  "type": "ProposedEditCard"', card["blocks"][-1]["code"])

        text = render_terminal_card(card)
        self.assertIn("Fallback: generic from ProposedEditCard", text)
        self.assertIn("Action policy: client_allowlist", text)
        self.assertIn("Debug:", text)
        self.assertIn("- fallback_kind: generic", text)
        self.assertIn("- source_card_type: ProposedEditCard", text)
        self.assertIn("- contract_version: 2", text)
        self.assertIn("Safe content", text)
        self.assertIn("- alpha", text)
        self.assertNotIn("[unsupported block: ChartBlock]", text)
        self.assertEqual(
            card["debug"],
            {"contract_version": 2, "fallback_kind": "generic", "source_card_type": "ProposedEditCard"},
        )

    def test_engine_fallback_keeps_only_read_only_copy_action(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = engine_prepare_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "safe"}},
                ],
            },
            caps,
        )

        self.assertEqual([action["id"] for action in card["actions"]], ["copy_to_clipboard"])
        self.assertEqual(card["actions"][0]["label"], "Copy JSON")
        self.assertIn("ProposedEditCard", card["actions"][0]["payload"]["text"])
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(
            card["debug"],
            {"contract_version": 2, "fallback_kind": "generic", "source_card_type": "ProposedEditCard"},
        )
        validate_generic_card(card)

        text = render_terminal_card(card)
        self.assertIn("- Copy JSON (copy_to_clipboard)", text)
        self.assertNotIn("- Apply (apply_patch)", text)

    def test_engine_fallback_surfaces_missing_copy_action_availability(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",), actions_supported=("apply_patch",))
        card = engine_prepare_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                ],
            },
            caps,
        )

        self.assertEqual(card["actions"], [])

        text = render_terminal_card(card)
        self.assertIn("Actions: none available", text)
        self.assertIn("Fallback: generic from ProposedEditCard", text)

    def test_unknown_card_validator_accepts_sanitized_fallback_cards(self) -> None:
        unknown = build_unknown_card(
            {
                "type": "FutureCard",
                "title": "Future",
                "blocks": [{"type": "MarkdownBlock", "markdown": "safe"}],
            },
            supported_actions=("copy_to_clipboard",),
        )

        validate_unknown_card(unknown)

    def test_engine_preserves_unknown_cards_as_unknown_fallbacks(self) -> None:
        unknown = engine_prepare_card(
            {
                "type": "UnknownCard",
                "title": " Unsupported card type: FutureCard ",
                "subtitle": " Read-only fallback view with safe primitive blocks and raw JSON preview. ",
                "a2ui_version": 1,
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": "unknown",
                    "source_card_type": "FutureCard",
                },
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "safe"},
                    {"type": "ListBlock", "items": ["alpha", "beta"]},
                ],
                "actions": [
                    {"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": "{}"}},
                ],
            },
            _capabilities(actions_supported=("apply_patch",)),
        )

        self.assertEqual(unknown["type"], "UnknownCard")
        self.assertEqual(unknown["title"], "Unsupported card type: FutureCard")
        self.assertEqual(
            unknown["subtitle"],
            "Read-only fallback view with safe primitive blocks and raw JSON preview.",
        )
        self.assertEqual(unknown["actions"], [])
        self.assertEqual(
            [block["type"] for block in unknown["blocks"]],
            ["MarkdownBlock", "ListBlock", "CodeBlock"],
        )
        self.assertEqual(unknown["blocks"][0], {"type": "MarkdownBlock", "markdown": "safe"})
        self.assertEqual(unknown["blocks"][1], {"type": "ListBlock", "items": ["alpha", "beta"]})
        self.assertIn('"type": "FutureCard"', unknown["blocks"][-1]["code"])

        text = render_terminal_card(unknown)
        self.assertIn("[UnknownCard] Unsupported card type: FutureCard", text)
        self.assertIn("Fallback: unknown from FutureCard", text)
        self.assertIn("Action policy: copy_to_clipboard_only", text)
        self.assertIn("- contract_version: 2", text)
        self.assertIn("- fallback_kind: unknown", text)

    def test_engine_canonicalizes_malformed_unknown_card_input(self) -> None:
        unknown = engine_prepare_card(
            {
                "type": " UnknownCard ",
                "title": "  should not leak  ",
                "subtitle": "  raw subtitle should not leak  ",
                "a2ui_version": 1,
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": " unknown ",
                    "source_card_type": " FutureCard ",
                    "unexpected": "ignored",
                },
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "safe"},
                    {"type": "ChartBlock", "series": [1, 2, 3]},
                ],
                "actions": [
                    {"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": "{}"}},
                ],
                "trace_id": "abc123",
            },
            _capabilities(actions_supported=("copy_to_clipboard",)),
        )

        self.assertEqual(unknown["type"], "UnknownCard")
        self.assertEqual(unknown["title"], "Unsupported card type: FutureCard")
        self.assertEqual(unknown["subtitle"], UNKNOWN_FALLBACK_SUBTITLE)
        self.assertEqual(
            unknown["debug"],
            {"contract_version": 2, "fallback_kind": "unknown", "source_card_type": "FutureCard"},
        )
        self.assertEqual([block["type"] for block in unknown["blocks"]], ["MarkdownBlock", "CodeBlock"])
        self.assertEqual(
            unknown["actions"],
            [
                {
                    "id": "copy_to_clipboard",
                    "label": "Copy JSON",
                    "payload": {"text": unknown["actions"][0]["payload"]["text"]},
                }
            ],
        )
        self.assertNotIn("should not leak", unknown["blocks"][-1]["code"])
        self.assertNotIn("should not leak", render_terminal_card(unknown))

    def test_engine_unknown_card_synthesizes_copy_action_when_supported(self) -> None:
        unknown = engine_prepare_card(
            {
                "type": "UnknownCard",
                "title": "Unsupported card type: FutureCard",
                "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                "a2ui_version": 1,
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": "unknown",
                    "source_card_type": "FutureCard",
                },
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "safe"},
                ],
                "actions": [],
            },
            _capabilities(actions_supported=("copy_to_clipboard",)),
        )

        self.assertEqual([action["id"] for action in unknown["actions"]], ["copy_to_clipboard"])
        self.assertEqual(unknown["actions"][0]["label"], "Copy JSON")
        payload = json.loads(unknown["actions"][0]["payload"]["text"])
        self.assertEqual(payload["actions"], [])
        self.assertEqual(unknown["blocks"][-1]["code"], unknown["actions"][0]["payload"]["text"])

    def test_engine_unknown_card_uses_canonical_copy_action_when_supported(self) -> None:
        unknown = engine_prepare_card(
            {
                "type": "UnknownCard",
                "title": "Unsupported card type: FutureCard",
                "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                "a2ui_version": 1,
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": "unknown",
                    "source_card_type": "FutureCard",
                },
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "safe"},
                ],
                "actions": [
                    {"id": "copy_to_clipboard", "label": "Copy me", "payload": {"text": "unsafe"}},
                ],
            },
            _capabilities(actions_supported=("copy_to_clipboard",)),
        )

        payload_text = unknown["actions"][0]["payload"]["text"]
        self.assertEqual(
            unknown["actions"],
            [
                {
                    "id": "copy_to_clipboard",
                    "label": "Copy JSON",
                    "payload": {"text": payload_text},
                }
            ],
        )
        payload = json.loads(payload_text)
        self.assertEqual(payload["actions"], [])
        self.assertEqual(unknown["blocks"][-1]["code"], payload_text)

    def test_studio_preserves_unknown_cards_and_copy_action_when_supported(self) -> None:
        unknown = studio_materialize_card(
            {
                "type": "UnknownCard",
                "title": " Unsupported card type: FutureCard ",
                "subtitle": " Read-only fallback view with safe primitive blocks and raw JSON preview. ",
                "a2ui_version": 1,
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": "unknown",
                    "source_card_type": "FutureCard",
                },
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "safe"},
                    {"type": "KeyValueBlock", "items": [{"key": "Owner", "value": "alice"}]},
                ],
                "actions": [
                    {"id": "copy_to_clipboard", "label": "Copy JSON", "payload": {"text": "{}"}},
                ],
            },
            _capabilities(actions_supported=("copy_to_clipboard",)),
        )

        self.assertEqual(unknown["type"], "UnknownCard")
        self.assertEqual(unknown["title"], "Unsupported card type: FutureCard")
        self.assertEqual([block["type"] for block in unknown["blocks"]], ["MarkdownBlock", "KeyValueBlock", "CodeBlock"])
        self.assertEqual(unknown["blocks"][0], {"type": "MarkdownBlock", "markdown": "safe"})
        self.assertEqual(unknown["blocks"][1], {"type": "KeyValueBlock", "items": [{"key": "Owner", "value": "alice"}]})
        self.assertEqual(unknown["blocks"][2]["language"], "json")
        self.assertTrue(unknown["blocks"][2]["collapsed"])
        self.assertEqual(
            unknown["actions"][0]["id"],
            "copy_to_clipboard",
        )
        self.assertEqual(unknown["actions"][0]["label"], "Copy JSON")
        payload = json.loads(unknown["actions"][0]["payload"]["text"])
        self.assertEqual(payload["actions"], [])
        self.assertEqual(unknown["blocks"][2]["code"], unknown["actions"][0]["payload"]["text"])

    def test_unknown_card_validator_rejects_non_copy_actions(self) -> None:
        with self.assertRaises(ValueError):
            validate_unknown_card(
                {
                    "type": "UnknownCard",
                    "title": "Unsupported card type: FutureCard",
                    "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                    "a2ui_version": 1,
                    "debug": {
                        "contract_version": 2,
                        "fallback_kind": "unknown",
                        "source_card_type": "FutureCard",
                    },
                    "blocks": [],
                    "actions": [
                        {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    ],
                }
            )

    def test_unknown_card_validator_rejects_non_canonical_copy_actions(self) -> None:
        with self.assertRaises(ValueError):
            validate_unknown_card(
                {
                    "type": "UnknownCard",
                    "title": "Unsupported card type: FutureCard",
                    "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                    "a2ui_version": 1,
                    "debug": {
                        "contract_version": 2,
                        "fallback_kind": "unknown",
                        "source_card_type": "FutureCard",
                    },
                    "blocks": [],
                    "actions": [
                        {
                            "id": "copy_to_clipboard",
                            "label": "Copy",
                            "payload": {"text": "{}"},
                        },
                    ],
                }
            )

        with self.assertRaises(ValueError):
            validate_unknown_card(
                {
                    "type": "UnknownCard",
                    "title": "Unsupported card type: FutureCard",
                    "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                    "a2ui_version": 1,
                    "debug": {
                        "contract_version": 2,
                        "fallback_kind": "unknown",
                        "source_card_type": "FutureCard",
                    },
                    "blocks": [],
                    "actions": [
                        {
                            "id": "copy_to_clipboard",
                            "label": "Copy JSON",
                            "payload": {"text": "{}"},
                            "policy_sensitive": True,
                        },
                    ],
                }
            )

    def test_unknown_card_validator_rejects_extra_fields(self) -> None:
        with self.assertRaises(ValueError):
            validate_unknown_card(
                {
                    "type": "UnknownCard",
                    "title": "Unsupported card type: FutureCard",
                    "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                    "a2ui_version": 1,
                    "debug": {
                        "contract_version": 2,
                        "fallback_kind": "unknown",
                        "source_card_type": "FutureCard",
                    },
                    "blocks": [],
                    "actions": [],
                    "trace_id": "abc123",
                }
            )

    def test_unknown_card_validator_rejects_extra_debug_fields(self) -> None:
        with self.assertRaises(ValueError):
            validate_unknown_card(
                {
                    "type": "UnknownCard",
                    "title": "Unsupported card type: FutureCard",
                    "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                    "a2ui_version": 1,
                    "debug": {
                        "contract_version": 2,
                        "fallback_kind": "unknown",
                        "source_card_type": "FutureCard",
                        "trace_id": "abc123",
                    },
                    "blocks": [],
                    "actions": [
                        {
                            "id": "copy_to_clipboard",
                            "label": "Copy JSON",
                            "payload": {"text": "{}"},
                        },
                    ],
                }
            )

    def test_engine_fallback_sanitizes_safe_primitive_blocks(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = engine_prepare_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "Kept"},
                    {"type": "MarkdownBlock", "markdown": 123},
                    {"type": "KeyValueBlock", "items": [{"key": "Owner", "value": "alice"}, {"key": " ", "value": "ignored"}]},
                    {"type": "ListBlock", "items": ["first", "", {"label": "second"}, {"label": " "} ]},
                    {"type": "ProgressBlock", "title": "Sync", "status_text": "Working"},
                    {"type": "TableBlock", "rows": [[1, 2, 3]]},
                ],
            },
            caps,
        )

        self.assertEqual(
            [block["type"] for block in card["blocks"]],
            ["AlertBlock", "MarkdownBlock", "KeyValueBlock", "ListBlock", "ProgressBlock", "TableBlock", "CodeBlock"],
        )
        self.assertEqual(card["blocks"][1], {"type": "MarkdownBlock", "markdown": "Kept"})
        self.assertEqual(card["blocks"][2], {"type": "KeyValueBlock", "items": [{"key": "Owner", "value": "alice"}]})
        self.assertEqual(card["blocks"][3], {"type": "ListBlock", "items": ["first", {"label": "second"}]})
        self.assertEqual(card["blocks"][4], {"type": "ProgressBlock", "title": "Sync", "status_text": "Working"})
        self.assertEqual(card["blocks"][5], {"type": "TableBlock", "rows": [[1, 2, 3]]})

    def test_engine_fallback_omits_source_code_blocks_from_read_only_view(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = engine_prepare_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "Kept"},
                    {"type": "CodeBlock", "language": "python", "code": "print('source block')", "collapsed": False},
                ],
            },
            caps,
        )

        self.assertEqual([block["type"] for block in card["blocks"]], ["AlertBlock", "MarkdownBlock", "CodeBlock"])
        self.assertEqual(len(card["blocks"]), 3)
        self.assertEqual(card["blocks"][1], {"type": "MarkdownBlock", "markdown": "Kept"})
        self.assertEqual(card["blocks"][2]["language"], "json")
        self.assertTrue(card["blocks"][2]["code"].startswith("{"))

    def test_engine_falls_back_to_generic_for_missing_card_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = engine_prepare_card(
            {
                "type": None,
                "title": "Patch",
                "blocks": [],
            },
            caps,
        )

        self.assertEqual(card["title"], "Fallback view for <missing>")
        self.assertEqual(
            card["debug"],
            {"contract_version": 2, "fallback_kind": "generic", "source_card_type": "<missing>"},
        )

    def test_engine_filters_invalid_actions_for_supported_cards(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch",))
        specialized = engine_prepare_card(
            {
                "type": "ProposedEditCard",
                "title": "Patch",
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "run_agent", "label": "Run", "payload": {"operation": "x"}},
                    {"id": "apply_patch", "label": "Broken", "payload": {}},
                ],
            },
            caps,
        )
        self.assertEqual(specialized["a2ui_version"], 1)
        self.assertEqual(specialized["actions"], [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}}])

        generic = engine_prepare_card(
            {
                "type": "GenericCard",
                "title": "Patch",
                "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p2"}},
                    {"id": "run_agent", "label": "Run", "payload": {"operation": "x"}},
                ],
            },
            caps,
        )
        self.assertEqual(generic["a2ui_version"], 1)
        self.assertEqual(generic["actions"], [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p2"}}])

    def test_engine_materializes_supported_cards_with_canonical_lists(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",), actions_supported=("apply_patch",))
        card = engine_prepare_card(
            {
                "type": "RunLogCard",
                "title": " Run Log ",
                "subtitle": "  Demo output  ",
                "blocks": None,
                "actions": None,
            },
            caps,
        )

        self.assertEqual(card["a2ui_version"], 1)
        self.assertEqual(card["title"], "Run Log")
        self.assertEqual(card["subtitle"], "Demo output")
        self.assertEqual(card["blocks"], [])
        self.assertEqual(card["actions"], [])

    def test_engine_materializes_supported_cards_without_unknown_top_level_fields(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",), actions_supported=("apply_patch",))
        card = engine_prepare_card(
            {
                "type": "RunLogCard",
                "title": " Patch ",
                "subtitle": "  Ready  ",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Kept"}],
                "actions": [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}}],
                "trace_id": "drop-me",
                "debug": {"step": "canonical"},
            },
            caps,
        )

        self.assertNotIn("trace_id", card)
        self.assertEqual(card["debug"], {"step": "canonical"})
        self.assertEqual(card["title"], "Patch")
        self.assertEqual(card["subtitle"], "Ready")
        self.assertEqual(card["blocks"], [{"type": "MarkdownBlock", "markdown": "Kept"}])
        self.assertEqual(card["actions"], [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}}])

    def test_engine_materializes_generic_card_with_missing_lists(self) -> None:
        caps = _capabilities(actions_supported=("copy_to_clipboard", "apply_patch"))
        card = engine_prepare_card(
            {
                "type": "GenericCard",
                "title": " Patch ",
                "subtitle": "  Ready to copy  ",
                "blocks": None,
                "actions": [
                    {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "hello"}},
                    {"id": "apply_patch", "label": "Broken", "payload": {"patch_id": "p1", "extra": True}},
                    {"id": "run_agent", "label": "Run", "payload": {"operation": "x"}},
                ],
                "trace_id": "drop-me",
            },
            caps,
        )

        self.assertEqual(card["a2ui_version"], 1)
        self.assertNotIn("trace_id", card)
        self.assertEqual(card["title"], "Patch")
        self.assertEqual(card["subtitle"], "Ready to copy")
        self.assertEqual(card["blocks"], [])
        self.assertEqual(
            card["actions"],
            [{"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "hello"}}],
        )

    def test_generic_card_validator_allows_blank_subtitle(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "subtitle": "   ",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Kept"}],
            "actions": [],
        }

        validate_generic_card(card)

    def test_engine_materializes_supported_card_with_sanitized_blocks(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",), actions_supported=("apply_patch",))
        card = engine_prepare_card(
            {
                "type": "RunLogCard",
                "title": "Patch",
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "Kept"},
                    {"type": "MarkdownBlock", "markdown": 123},
                    {"type": "ChartBlock", "series": [1, 2, 3]},
                    {"type": "ListBlock", "items": ["first", {"label": " second "}, " "]},
                ],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "run_agent", "label": "Run", "payload": {"operation": "x"}},
                ],
            },
            caps,
        )

        self.assertEqual(
            card["blocks"],
            [
                {"type": "MarkdownBlock", "markdown": "Kept"},
                {"type": "ListBlock", "items": ["first", {"label": "second"}]},
            ],
        )
        self.assertEqual(card["actions"], [{"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}}])

    def test_engine_rejects_version_mismatched_supported_cards(self) -> None:
        caps = _capabilities(cards_supported=("ProposedEditCard",))
        with self.assertRaises(ValueError):
            engine_prepare_card(
                {
                    "type": "ProposedEditCard",
                    "a2ui_version": 2,
                    "title": "Patch",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
                },
                caps,
            )

    def test_engine_rejects_bool_a2ui_version_on_generic_card(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        with self.assertRaises(ValueError):
            engine_prepare_card(
                {
                    "type": "GenericCard",
                    "a2ui_version": True,  # type: ignore[arg-type]
                    "title": "Patch",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
                    "actions": [],
                },
                caps,
            )

    def test_engine_rejects_bool_a2ui_version_on_supported_card(self) -> None:
        caps = _capabilities(cards_supported=("ProposedEditCard",))
        with self.assertRaises(ValueError):
            engine_prepare_card(
                {
                    "type": "ProposedEditCard",
                    "a2ui_version": True,  # type: ignore[arg-type]
                    "title": "Patch",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
                },
                caps,
            )

    def test_engine_rejects_invalid_capabilities_before_materialization(self) -> None:
        caps = A2UICapabilities(
            a2ui_version=1,
            client_name="Exegesis Studio",
            cards_supported=("ProposedEditCard",),
            primitive_blocks_supported=(
                "MarkdownBlock",
                "KeyValueBlock",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
            actions_supported=("apply_patch", "launch_missiles"),
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )

        with self.assertRaises(ValueError):
            engine_prepare_card(
                {
                    "type": "ProposedEditCard",
                    "title": "Patch",
                    "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
                },
                caps,
            )

    def test_studio_renders_unknown_card_for_unsupported_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertIn("Unsupported card type", card["title"])
        self.assertEqual(card["a2ui_version"], 1)
        self.assertEqual(card["actions"][0]["id"], "copy_to_clipboard")
        self.assertEqual(
            card["debug"],
            {"contract_version": 2, "fallback_kind": "unknown", "source_card_type": "QuestionsCard"},
        )

    def test_studio_unknown_card_synthesizes_copy_action_when_supported(self) -> None:
        caps = _capabilities(actions_supported=("copy_to_clipboard",))
        card = studio_materialize_card(
            {
                "type": "UnknownCard",
                "title": "Unsupported card type: FutureCard",
                "subtitle": "Read-only fallback view with safe primitive blocks and raw JSON preview.",
                "a2ui_version": 1,
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": "unknown",
                    "source_card_type": "FutureCard",
                },
                "blocks": [
                    {"type": "MarkdownBlock", "markdown": "safe"},
                ],
                "actions": [],
            },
            caps,
        )

        self.assertEqual([action["id"] for action in card["actions"]], ["copy_to_clipboard"])
        self.assertEqual(card["actions"][0]["label"], "Copy JSON")

    def test_studio_renders_unknown_card_for_missing_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = studio_materialize_card({"type": None, "foo": "bar"}, caps)
        self.assertEqual(card["title"], "Unsupported card type: <missing>")
        self.assertEqual(
            card["debug"],
            {"contract_version": 2, "fallback_kind": "unknown", "source_card_type": "<missing>"},
        )
        self.assertEqual([block["type"] for block in card["blocks"]], ["CodeBlock"])

    def test_studio_renders_unknown_card_for_non_string_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = studio_materialize_card({"type": 123, "title": "Questions", "foo": "bar"}, caps)
        self.assertEqual(card["title"], "Unsupported card type: <missing>")
        self.assertEqual(
            card["debug"],
            {"contract_version": 2, "fallback_kind": "unknown", "source_card_type": "<missing>"},
        )
        self.assertEqual([block["type"] for block in card["blocks"]], ["CodeBlock"])

    def test_unknown_card_sanitizes_safe_primitive_blocks(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        payload = {
            "type": "QuestionsCard",
            "title": "Questions",
            "blocks": [
                {"type": "MarkdownBlock", "markdown": "Recovered"},
                {"type": "MarkdownBlock", "markdown": 123},
                {"type": "ListBlock", "items": ["first", "", {"label": "second"}, {"label": " "} ]},
                {"type": "KeyValueBlock", "items": [{"key": "Owner", "value": "alice"}, {"key": "Bad", "value": {"nested": "drop"}}]},
                {"type": "ProgressBlock", "title": "Sync", "status_text": "Working"},
                {"type": "TableBlock", "rows": [[1, 2, 3]]},
            ],
            "foo": "bar",
        }

        card = studio_materialize_card(payload, caps)

        self.assertEqual(
            [block["type"] for block in card["blocks"]],
            ["MarkdownBlock", "ListBlock", "KeyValueBlock", "ProgressBlock", "TableBlock", "CodeBlock"],
        )
        self.assertEqual(card["blocks"][0], {"type": "MarkdownBlock", "markdown": "Recovered"})
        self.assertEqual(card["blocks"][1], {"type": "ListBlock", "items": ["first", {"label": "second"}]})
        self.assertEqual(card["blocks"][2], {"type": "KeyValueBlock", "items": [{"key": "Owner", "value": "alice"}]})
        self.assertEqual(card["blocks"][3], {"type": "ProgressBlock", "title": "Sync", "status_text": "Working"})
        self.assertEqual(card["blocks"][4], {"type": "TableBlock", "rows": [[1, 2, 3]]})
        self.assertEqual(card["blocks"][5]["type"], "CodeBlock")
        self.assertEqual(card["actions"][0]["id"], "copy_to_clipboard")

    def test_unknown_card_preserves_tuple_shaped_safe_blocks(self) -> None:
        unknown = build_unknown_card(
            {
                "type": "FutureCard",
                "title": "Future",
                "blocks": (
                    {"type": "MarkdownBlock", "markdown": "Recovered"},
                    {"type": "ListBlock", "items": ["alpha", "beta"]},
                ),
            },
            supported_actions=("copy_to_clipboard",),
        )

        self.assertEqual(
            [block["type"] for block in unknown["blocks"][:-1]],
            ["MarkdownBlock", "ListBlock"],
        )
        self.assertEqual(unknown["blocks"][0], {"type": "MarkdownBlock", "markdown": "Recovered"})
        self.assertEqual(unknown["blocks"][1], {"type": "ListBlock", "items": ["alpha", "beta"]})
        self.assertEqual(unknown["actions"][0]["id"], "copy_to_clipboard")

    def test_studio_unknown_card_omits_unavailable_clipboard_action(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["actions"], [])

    def test_studio_unknown_card_strips_raw_actions_and_keeps_clipboard_only(self) -> None:
        caps = _capabilities(actions_supported=("copy_to_clipboard", "apply_patch"))
        payload = {
            "type": "QuestionsCard",
            "title": "Questions",
            "actions": [
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "unsafe"}},
            ],
            "foo": "bar",
        }

        card = studio_materialize_card(payload, caps)

        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual([action["id"] for action in card["actions"]], ["copy_to_clipboard"])
        self.assertEqual(card["actions"][0]["label"], "Copy JSON")

    def test_unknown_card_canonicalizes_supported_actions_before_copy_action(self) -> None:
        raw_unknown = {"type": "FutureCard", "title": "Future"}

        unknown = build_unknown_card(
            raw_unknown,
            supported_actions=(" copy_to_clipboard ", "copy_to_clipboard", "apply_patch"),
        )

        self.assertEqual([action["id"] for action in unknown["actions"]], ["copy_to_clipboard"])
        payload_text = unknown["actions"][0]["payload"]["text"]
        self.assertEqual(
            unknown["actions"][0],
            {
                "id": "copy_to_clipboard",
                "label": "Copy JSON",
                "payload": {"text": payload_text},
            },
        )

    def test_unknown_card_preserves_safe_table_rows(self) -> None:
        raw_unknown = {
            "type": "FutureCard",
            "title": "Future",
            "blocks": [
                {
                    "type": "TableBlock",
                    "rows": [
                        ["left", "right"],
                        ["alpha", None, 2],
                        ["drop", {"nested": True}],
                        "ignored",
                    ],
                }
            ],
        }

        unknown = build_unknown_card(raw_unknown)
        unknown_text = render_terminal_card(unknown)

        self.assertEqual(
            unknown["blocks"][0],
            {
                "type": "TableBlock",
                "rows": [
                    ["left", "right"],
                    ["alpha", None, 2],
                    ["drop"],
                ],
            },
        )
        self.assertIn("[table]", unknown_text)
        self.assertIn("- left | right", unknown_text)
        self.assertIn("- alpha | <blank> | 2", unknown_text)
        self.assertIn("- drop", unknown_text)

    def test_studio_rejects_invalid_capabilities_before_materialization(self) -> None:
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
            actions_supported=("copy_to_clipboard", "launch_missiles"),
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )

        with self.assertRaises(ValueError):
            studio_materialize_card({"type": "QuestionsCard", "title": "Questions"}, caps)

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
                {"id": "apply_patch", "label": "   ", "payload": {"patch_id": "p3"}},
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
                {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p2"}},
            ],
        }

        filtered = studio_materialize_card(card, caps)

        self.assertEqual(
            [action["id"] for action in filtered["actions"]],
            ["apply_patch", "copy_to_clipboard", "reject_patch"],
        )

    def test_action_payload_schema_rejects_extra_fields(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch",))
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1", "force": True},
                }
            ],
        }
        filtered = studio_materialize_card(card, caps)
        self.assertEqual(filtered["actions"], [])

    def test_action_top_level_schema_rejects_extra_fields(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch",))
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "icon": "sparkle",
                }
            ],
        }

        filtered = studio_materialize_card(card, caps)

        self.assertEqual(filtered["actions"], [])

    def test_filtered_actions_preserve_distinct_policy_and_confirm_variants(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch",))
        card = {
            "type": "GenericCard",
            "title": "Patch",
            "blocks": [{"type": "MarkdownBlock", "markdown": "x"}],
            "actions": [
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "confirm": {"title": "Approve", "message": "Apply patch?"},
                },
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "policy_sensitive": True,
                },
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "confirm": {"title": " ", "message": "Apply patch?"},
                },
            ],
        }

        filtered = studio_materialize_card(card, caps)

        self.assertEqual(
            filtered["actions"],
            [
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "confirm": {"title": "Approve", "message": "Apply patch?"},
                },
                {
                    "id": "apply_patch",
                    "label": "Apply",
                    "payload": {"patch_id": "p1"},
                    "policy_sensitive": True,
                },
            ],
        )

    def test_terminal_renderer_skips_actions_with_extra_top_level_fields(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [
                    {"id": "export_document", "label": "Export", "payload": {"format": "md"}},
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                        "icon": "sparkle",
                    },
                ],
            }
        )

        self.assertIn("- Export (export_document)", text)
        self.assertEqual(text.count("- Export (export_document)"), 1)

    def test_terminal_renderer_deduplicates_visible_action_affordances(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [
                    {"id": "export_document", "label": "Export", "payload": {"format": "md"}},
                    {"id": "export_document", "label": "Export", "payload": {"format": "md"}},
                    {"id": "export_document", "label": "Export", "payload": {"format": "txt"}},
                ],
            }
        )

        self.assertEqual(text.count("- Export (export_document; payload:"), 2)
        self.assertIn('- Export (export_document; payload: {"format":"md"})', text)
        self.assertIn('- Export (export_document; payload: {"format":"txt"})', text)

    def test_terminal_renderer_renders_supported_actions_in_canonical_order(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p2"}},
                    {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "payload"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": "p2"}},
                ],
            }
        )

        self.assertLess(text.index("- Apply (apply_patch)"), text.index("- Copy (copy_to_clipboard)"))
        self.assertLess(text.index("- Copy (copy_to_clipboard)"), text.index("- Reject (reject_patch)"))

    def test_terminal_renderer_shows_payloads_for_duplicate_action_labels(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [
                    {"id": "export_document", "label": "Export", "payload": {"format": "md"}},
                    {"id": "export_document", "label": "Export", "payload": {"format": "txt"}},
                ],
            }
        )

        self.assertIn('- Export (export_document; payload: {"format":"md"})', text)
        self.assertIn('- Export (export_document; payload: {"format":"txt"})', text)

    def test_terminal_renderer_surfaces_action_variants(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "md"},
                        "confirm": {"title": "Approve", "message": "Export now?"},
                    },
                    {
                        "id": "export_document",
                        "label": "Export",
                        "payload": {"format": "txt"},
                        "policy_sensitive": True,
                    },
                ],
            }
        )

        self.assertIn('- Export (export_document; confirm: Approve; payload: {"format":"md"})', text)
        self.assertIn('- Export (export_document; policy-sensitive; payload: {"format":"txt"})', text)

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

    def test_execute_action_rejects_invalid_capabilities_before_policy_gate(self) -> None:
        caps = A2UICapabilities(
            a2ui_version=1,
            client_name="Exegesis Studio",
            cards_supported=("ProposedEditCard",),
            primitive_blocks_supported=(
                "MarkdownBlock",
                "KeyValueBlock",
                "ListBlock",
                "TableBlock",
                "AlertBlock",
                "ProgressBlock",
                "CodeBlock",
            ),
            actions_supported=("export_document", "launch_missiles"),
            max_payload_bytes=1_000_000,
            supports_streaming=True,
        )

        with self.assertRaises(ValueError):
            execute_action_with_policy_gate(
                action=ActionRef(
                    id="export_document",
                    label="Export",
                    payload={"format": "md"},
                ),
                capabilities=caps,
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action.id,
            )

    def test_normalize_action_ref_trims_and_preserves_optional_fields(self) -> None:
        normalized = normalize_action_ref(
            ActionRef(
                id=" apply_patch ",
                label=" Apply ",
                payload={"patch_id": "p1"},
                confirm={"title": " Approve ", "message": " Apply patch? "},
                policy_sensitive=True,
            )
        )

        self.assertEqual(normalized.id, "apply_patch")
        self.assertEqual(normalized.label, "Apply")
        self.assertEqual(normalized.confirm, {"title": "Approve", "message": "Apply patch?"})
        self.assertTrue(normalized.policy_sensitive)

    def test_execute_action_rejects_malformed_direct_actionref(self) -> None:
        with self.assertRaises(ValueError):
            execute_action_with_policy_gate(
                action=ActionRef(
                    id="apply_patch",
                    label="Apply",
                    payload={"patch_id": "p1"},
                    confirm={"title": "", "message": "Apply patch?"},
                ),
                capabilities=_capabilities(actions_supported=("apply_patch",)),
                policy_gate=_PolicyGateStub(True),
                executor=lambda action: action.id,
            )

    def test_execute_action_passes_normalized_actionref_to_executor(self) -> None:
        observed: list[ActionRef] = []

        execute_action_with_policy_gate(
            action=ActionRef(
                id=" export_document ",
                label=" Export ",
                payload={"format": "md"},
                confirm={"title": " Confirm ", "message": " Export now? "},
            ),
            capabilities=_capabilities(actions_supported=("export_document",)),
            policy_gate=_PolicyGateStub(True),
            executor=lambda action: observed.append(action),
        )

        self.assertEqual(
            observed,
            [
                ActionRef(
                    id="export_document",
                    label="Export",
                    payload={"format": "md"},
                    confirm={"title": "Confirm", "message": "Export now?"},
                    policy_sensitive=False,
                )
            ],
        )

    def test_terminal_can_render_inline_generic_and_unknown_cards(self) -> None:
        generic = {
            "type": "GenericCard",
            "title": "Run Log",
            "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
            "actions": [
                {"id": "export_document", "label": "Export", "payload": {"format": "md"}},
                {"id": "export_document", "label": "Broken", "payload": {"format": "md", "extra": 1}},
            ],
        }
        text = render_terminal_card(generic)
        self.assertIn("[GenericCard] Run Log", text)
        self.assertIn("Hello", text)
        self.assertIn("Actions:", text)
        self.assertIn("- Export (export_document)", text)
        self.assertNotIn("Broken", text)

        raw_unknown = {
            "type": "FutureCard",
            "blocks": [
                {"type": "MarkdownBlock", "markdown": "Recovered"},
                {"type": "ChartBlock", "series": [1, 2, 3]},
            ],
            "payload": {"body": "x" * 200},
        }
        unknown = build_unknown_card(raw_unknown, max_payload_bytes=80)
        self.assertEqual([block["type"] for block in unknown["blocks"][:2]], ["MarkdownBlock", "CodeBlock"])
        self.assertIn("Recovered", render_terminal_card(unknown))
        self.assertTrue(unknown["blocks"][1]["code"].startswith("{"))
        self.assertIn("[truncated to 80 bytes]", unknown["blocks"][1]["code"])
        self.assertIn("[truncated to 80 bytes]", unknown["actions"][0]["payload"]["text"])
        self.assertLessEqual(len(unknown["actions"][0]["payload"]["text"].encode("utf-8")), 80)
        unknown_text = render_terminal_card(unknown)
        self.assertIn("[UnknownCard] Unsupported card type: FutureCard", unknown_text)
        self.assertIn("Fallback: unknown from FutureCard", unknown_text)
        self.assertIn("Debug:", unknown_text)
        self.assertIn("- contract_version: 2", unknown_text)
        self.assertIn("- fallback_kind: unknown", unknown_text)
        self.assertIn("- source_card_type: FutureCard", unknown_text)
        self.assertIn("- Copy JSON (copy_to_clipboard)", unknown_text)

    def test_terminal_renderer_accepts_tuple_shaped_blocks_and_actions(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Run Log",
                "blocks": (
                    {"type": "MarkdownBlock", "markdown": "Hello"},
                    {"type": "ListBlock", "items": ["alpha", "beta"]},
                ),
                "actions": (
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "payload"}},
                ),
            }
        )

        self.assertIn("Hello", text)
        self.assertIn("- alpha", text)
        self.assertIn("Actions:", text)
        self.assertIn("- Apply (apply_patch)", text)
        self.assertIn("- Copy (copy_to_clipboard)", text)
        self.assertNotIn("Actions filtered out by allowlist or validation", text)

    def test_terminal_renderer_marks_unknown_cards_without_debug(self) -> None:
        text = render_terminal_card(
            {
                "type": "UnknownCard",
                "title": "Fallback",
                "blocks": [],
                "actions": [],
            }
        )

        self.assertIn("[UnknownCard] Fallback", text)
        self.assertIn("Fallback: unknown card", text)
        self.assertIn("Action policy: copy_to_clipboard_only", text)
        self.assertNotIn("Debug:", text)

    def test_terminal_renderer_infers_unknown_fallback_without_debug(self) -> None:
        text = render_terminal_card(
            {
                "type": "UnknownCard",
                "title": "Unsupported card type: FutureCard",
                "blocks": [],
                "actions": [],
            }
        )

        self.assertIn("[UnknownCard] Unsupported card type: FutureCard", text)
        self.assertIn("Fallback: unknown from FutureCard", text)
        self.assertIn("Action policy: copy_to_clipboard_only", text)
        self.assertIn("Debug:", text)
        self.assertIn("- fallback_kind: unknown", text)
        self.assertIn("- source_card_type: FutureCard", text)

    def test_terminal_renderer_infers_generic_fallback_without_debug(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback view for FutureCard",
                "subtitle": "raw subtitle should not leak",
                "blocks": [],
                "actions": [],
            }
        )

        self.assertIn("[GenericCard] Fallback view for FutureCard", text)
        self.assertIn(GENERIC_FALLBACK_SUBTITLE, text)
        self.assertIn("Fallback: generic from FutureCard", text)
        self.assertIn("Action policy: client_allowlist", text)
        self.assertIn("Debug:", text)
        self.assertIn("- fallback_kind: generic", text)
        self.assertIn("- source_card_type: FutureCard", text)
        self.assertNotIn("raw subtitle should not leak", text)

    def test_terminal_renderer_synthesizes_canonical_fallback_subtitles(self) -> None:
        generic = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback view for FutureCard",
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": "generic",
                    "source_card_type": "FutureCard",
                },
                "blocks": [],
                "actions": [],
            }
        )
        unknown = render_terminal_card(
            {
                "type": "UnknownCard",
                "title": "Unsupported card type: FutureCard",
                "blocks": [],
                "actions": [],
            }
        )

        self.assertIn(GENERIC_FALLBACK_SUBTITLE, generic)
        self.assertIn(UNKNOWN_FALLBACK_SUBTITLE, unknown)
        self.assertIn("- contract_version: 2", generic)

    def test_terminal_renderer_uses_canonical_fallback_subtitles_over_raw_values(self) -> None:
        generic = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback view for FutureCard",
                "subtitle": "raw subtitle should not leak",
                "debug": {
                    "contract_version": 2,
                    "fallback_kind": "generic",
                    "source_card_type": "FutureCard",
                },
                "blocks": [],
                "actions": [],
            }
        )
        unknown = render_terminal_card(
            {
                "type": "UnknownCard",
                "title": "Unsupported card type: FutureCard",
                "subtitle": "raw subtitle should not leak",
                "blocks": [],
                "actions": [],
            }
        )

        self.assertIn(GENERIC_FALLBACK_SUBTITLE, generic)
        self.assertNotIn("raw subtitle should not leak", generic)
        self.assertIn(UNKNOWN_FALLBACK_SUBTITLE, unknown)
        self.assertNotIn("raw subtitle should not leak", unknown)

    def test_terminal_renderer_surfaces_missing_actions_for_unknown_fallbacks(self) -> None:
        unknown = build_unknown_card(
            {
                "type": "FutureCard",
                "title": "Future",
            },
            supported_actions=("apply_patch",),
        )

        text = render_terminal_card(unknown)

        self.assertEqual(unknown["actions"], [])
        self.assertIn("Actions: none available", text)
        self.assertIn("Fallback: unknown from FutureCard", text)

    def test_unknown_card_copy_payload_matches_preview_budget(self) -> None:
        raw_unknown = {
            "type": "FutureCard",
            "title": "Future",
            "payload": {"body": "x" * 200},
        }

        unknown = build_unknown_card(raw_unknown, max_payload_bytes=48)

        self.assertIn("[truncated to 48 bytes]", unknown["blocks"][-1]["code"])
        self.assertIn("[truncated to 48 bytes]", unknown["actions"][0]["payload"]["text"])
        self.assertLessEqual(len(unknown["blocks"][-1]["code"].encode("utf-8")), 48)
        self.assertLessEqual(len(unknown["actions"][0]["payload"]["text"].encode("utf-8")), 48)

    def test_unknown_card_uses_safe_default_preview_budget(self) -> None:
        raw_unknown = {
            "type": "FutureCard",
            "title": "Future",
            "payload": {"body": "x" * 20_000},
        }

        unknown = build_unknown_card(raw_unknown)

        self.assertIn("[truncated to 8192 bytes]", unknown["blocks"][-1]["code"])
        self.assertIn("[truncated to 8192 bytes]", unknown["actions"][0]["payload"]["text"])
        self.assertLessEqual(len(unknown["blocks"][-1]["code"].encode("utf-8")), 8192)
        self.assertLessEqual(len(unknown["actions"][0]["payload"]["text"].encode("utf-8")), 8192)

    def test_unknown_card_rejects_negative_preview_budget(self) -> None:
        with self.assertRaises(ValueError):
            build_unknown_card(
                {
                    "type": "FutureCard",
                    "title": "Future",
                    "payload": {"body": "x" * 32},
                },
                max_payload_bytes=-1,
            )

    def test_unknown_card_handles_zero_preview_budget(self) -> None:
        unknown = build_unknown_card(
            {
                "type": "FutureCard",
                "title": "Future",
                "payload": {"body": "x" * 32},
            },
            max_payload_bytes=0,
            supported_actions=("copy_to_clipboard",),
        )

        self.assertEqual(unknown["blocks"][-1]["code"], "")
        self.assertEqual(unknown["actions"][0]["payload"]["text"], "")
        self.assertEqual(len(unknown["blocks"][-1]["code"].encode("utf-8")), 0)
        self.assertEqual(len(unknown["actions"][0]["payload"]["text"].encode("utf-8")), 0)

    def test_unknown_card_handles_non_json_payload_values(self) -> None:
        class _OpaqueValue:
            pass

        raw_unknown = {
            "type": "FutureCard",
            "title": "Future",
            "payload": {
                "opaque": _OpaqueValue(),
                "nested": [_OpaqueValue()],
                "loop": None,
            },
        }
        raw_unknown["payload"]["loop"] = raw_unknown["payload"]

        unknown = build_unknown_card(raw_unknown, supported_actions=("copy_to_clipboard",))
        unknown_text = render_terminal_card(unknown)

        self.assertEqual(unknown["type"], "UnknownCard")
        self.assertIn("<non-json:_OpaqueValue>", unknown["blocks"][-1]["code"])
        self.assertIn("<non-json:_OpaqueValue>", unknown["actions"][0]["payload"]["text"])
        self.assertIn("<cycle:dict>", unknown["blocks"][-1]["code"])
        self.assertIn("Fallback: unknown from FutureCard", unknown_text)
        self.assertIn("- Copy JSON (copy_to_clipboard)", unknown_text)

    def test_terminal_fallback_renders_unsupported_or_malformed_blocks(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Fallback",
            "blocks": [
                {"type": "ChartBlock", "series": [1, 2, 3]},
                {"markdown": "missing type"},
                "not-a-block",
                {"type": "ListBlock", "items": "broken"},
                {"type": "KeyValueBlock", "items": [{"value": "missing key"}, {"key": " ", "value": "ignored"}, {"key": "Owner", "value": "  "}]},
                {"type": "ListBlock", "items": ["   ", {"label": "  "}, {"label": "Kept"}]},
            ],
            "actions": [],
        }

        text = render_terminal_card(card)
        self.assertIn("[unsupported block: ChartBlock]", text)
        self.assertIn("[unsupported block: missing type]", text)
        self.assertIn("[unsupported block: malformed]", text)
        self.assertIn("[ListBlock: invalid items]", text)
        self.assertIn("- Owner: <blank>", text)
        self.assertIn("- Kept", text)

    def test_terminal_renderer_ignores_non_list_blocks_and_actions(self) -> None:
        card = {
            "type": "GenericCard",
            "title": "Fallback",
            "blocks": None,
            "actions": None,
        }

        text = render_terminal_card(card)

        self.assertIn("[GenericCard] Fallback", text)
        self.assertNotIn("Actions:", text)

    def test_terminal_renderer_reports_explicit_empty_actions_list(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback",
                "blocks": [],
                "actions": [],
            }
        )

        self.assertIn("Actions: none available", text)

    def test_terminal_renderer_reports_malformed_actions_container(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
            }
        )

        self.assertIn("Actions: none available", text)
        self.assertIn("Actions filtered out by allowlist or validation", text)
        self.assertNotIn("- Apply (apply_patch)", text)

    def test_terminal_renderer_reports_filtered_out_actions(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [
                    {"id": "launch_missiles", "label": "Run", "payload": {"operation": "x"}},
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1", "extra": True}},
                ],
            }
        )

        self.assertIn("Actions: none available", text)
        self.assertIn("Actions filtered out by allowlist or validation", text)
        self.assertNotIn("- Run (launch_missiles)", text)
        self.assertNotIn("- Apply (apply_patch)", text)

    def test_terminal_renderer_reports_partially_filtered_actions(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback",
                "blocks": [{"type": "MarkdownBlock", "markdown": "Hello"}],
                "actions": [
                    {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": "p1"}},
                    {"id": "launch_missiles", "label": "Run", "payload": {"operation": "x"}},
                ],
            }
        )

        self.assertIn("Actions:", text)
        self.assertIn("- Apply (apply_patch)", text)
        self.assertIn("Some actions filtered out by allowlist or validation", text)
        self.assertNotIn("- Run (launch_missiles)", text)

    def test_terminal_renderer_normalizes_missing_card_metadata(self) -> None:
        text = render_terminal_card(
            {
                "type": 123,
                "title": None,
                "blocks": [],
                "actions": [],
            }
        )

        self.assertIn("[<missing>] <untitled>", text)
        self.assertNotIn("[123]", text)
        self.assertNotIn("None", text)

    def test_terminal_renderer_ignores_bool_a2ui_version(self) -> None:
        text = render_terminal_card(
            {
                "type": "GenericCard",
                "title": "Fallback",
                "a2ui_version": True,  # type: ignore[arg-type]
                "blocks": [],
                "actions": [],
            }
        )

        self.assertNotIn("A2UI vTrue", text)
        self.assertNotIn("A2UI v1", text)


if __name__ == "__main__":
    unittest.main()
