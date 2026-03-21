from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    a2ui_contract_fingerprint,
    build_unknown_card,
    describe_a2ui_contract,
    engine_prepare_card,
    execute_action_with_policy_gate,
    normalize_action_ref,
    render_terminal_card,
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

    def test_contract_manifest_is_versioned_and_fingerprintable(self) -> None:
        manifest = describe_a2ui_contract()

        self.assertEqual(manifest["a2ui_version"], 1)
        self.assertEqual(manifest["contract_fingerprint"], a2ui_contract_fingerprint())
        self.assertEqual(len(manifest["contract_fingerprint"]), 64)
        self.assertEqual(
            manifest["cards"],
            {
                "generic": "GenericCard",
                "unknown": "UnknownCard",
                "reserved": ["GenericCard", "UnknownCard"],
            },
        )
        self.assertEqual(
            manifest["schemas"]["cards"],
            [
                {
                    "type": "GenericCard",
                    "version": 1,
                    "required_fields": ["type", "title"],
                    "optional_fields": ["a2ui_version", "subtitle", "blocks", "actions", "debug"],
                    "action_policy": "client_allowlist",
                },
                {
                    "type": "UnknownCard",
                    "version": 1,
                    "required_fields": ["type", "title", "subtitle", "a2ui_version", "debug", "blocks", "actions"],
                    "optional_fields": [],
                    "action_policy": "copy_to_clipboard_only",
                },
            ],
        )
        self.assertEqual(
            manifest["schemas"]["actions"],
            [
                {
                    "type": "ActionRef",
                    "required_fields": ["id", "label", "payload"],
                    "optional_fields": ["confirm", "policy_sensitive"],
                    "payload_schemas": [
                        {"id": "apply_patch", "fields": ["patch_id"]},
                        {"id": "copy_to_clipboard", "fields": ["text"]},
                        {"id": "create_context_set", "fields": ["name"]},
                        {"id": "export_document", "fields": ["format"]},
                        {"id": "open_corpus_item", "fields": ["item_id"]},
                        {"id": "open_section", "fields": ["section_id"]},
                        {"id": "pin_to_context_set", "fields": ["item_id"]},
                        {"id": "refresh_license", "fields": []},
                        {"id": "reject_patch", "fields": ["patch_id"]},
                        {"id": "run_agent", "fields": ["operation"]},
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

        text = render_terminal_card(card)
        self.assertIn("Fallback: generic from ProposedEditCard", text)
        self.assertIn("Debug:", text)
        self.assertIn("- fallback_kind: generic", text)
        self.assertIn("- source_card_type: ProposedEditCard", text)
        self.assertIn("Safe content", text)
        self.assertIn("- alpha", text)
        self.assertNotIn("[unsupported block: ChartBlock]", text)
        self.assertEqual(card["debug"], {"fallback_kind": "generic", "source_card_type": "ProposedEditCard"})

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
        self.assertEqual(card["actions"][0]["label"], "Copy")

        text = render_terminal_card(card)
        self.assertIn("- Copy (copy_to_clipboard)", text)
        self.assertNotIn("- Apply (apply_patch)", text)

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
        self.assertEqual(card["debug"], {"fallback_kind": "generic", "source_card_type": "<missing>"})

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
                "title": "Run Log",
                "blocks": None,
                "actions": None,
            },
            caps,
        )

        self.assertEqual(card["a2ui_version"], 1)
        self.assertEqual(card["blocks"], [])
        self.assertEqual(card["actions"], [])

    def test_engine_materializes_generic_card_with_missing_lists(self) -> None:
        caps = _capabilities(actions_supported=("copy_to_clipboard", "apply_patch"))
        card = engine_prepare_card(
            {
                "type": "GenericCard",
                "title": "Patch",
                "blocks": None,
                "actions": [
                    {"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "hello"}},
                    {"id": "apply_patch", "label": "Broken", "payload": {"patch_id": "p1", "extra": True}},
                    {"id": "run_agent", "label": "Run", "payload": {"operation": "x"}},
                ],
            },
            caps,
        )

        self.assertEqual(card["a2ui_version"], 1)
        self.assertEqual(card["blocks"], [])
        self.assertEqual(
            card["actions"],
            [{"id": "copy_to_clipboard", "label": "Copy", "payload": {"text": "hello"}}],
        )

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
        self.assertEqual(card["debug"], {"fallback_kind": "unknown", "source_card_type": "QuestionsCard"})

    def test_studio_renders_unknown_card_for_missing_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = studio_materialize_card({"type": None, "foo": "bar"}, caps)
        self.assertEqual(card["title"], "Unsupported card type: <missing>")
        self.assertEqual(card["debug"], {"fallback_kind": "unknown", "source_card_type": "<missing>"})

    def test_studio_renders_unknown_card_for_non_string_type(self) -> None:
        caps = _capabilities(cards_supported=("RunLogCard",))
        card = studio_materialize_card({"type": 123, "title": "Questions", "foo": "bar"}, caps)
        self.assertEqual(card["title"], "Unsupported card type: <missing>")
        self.assertEqual(card["debug"], {"fallback_kind": "unknown", "source_card_type": "<missing>"})

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

    def test_filtered_actions_preserve_input_order(self) -> None:
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
            ["reject_patch", "copy_to_clipboard", "apply_patch"],
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

        self.assertEqual(text.count("- Export (export_document)"), 1)

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
        self.assertIn("- fallback_kind: unknown", unknown_text)
        self.assertIn("- source_card_type: FutureCard", unknown_text)
        self.assertIn("- Copy JSON (copy_to_clipboard)", unknown_text)

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
