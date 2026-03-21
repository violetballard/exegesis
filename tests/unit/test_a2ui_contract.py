from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.qual.ui.a2ui import (
    A2UICapabilities,
    A2UISessionStore,
    ActionRef,
    build_unknown_card,
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

    def test_session_store_rejects_invalid_capabilities(self) -> None:
        store = A2UISessionStore()
        with self.assertRaises(ValueError):
            store.register(
                "sess-2",
                _capabilities(
                    actions_supported=("apply_patch", "launch_missiles"),
                ),
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
        self.assertEqual([block["type"] for block in card["blocks"]], ["AlertBlock", "MarkdownBlock", "ListBlock", "CodeBlock"])

        text = render_terminal_card(card)
        self.assertIn("Safe content", text)
        self.assertIn("- alpha", text)
        self.assertNotIn("[unsupported block: ChartBlock]", text)
        self.assertEqual(card["debug"], {"fallback_kind": "generic", "source_card_type": "ProposedEditCard"})

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

    def test_studio_unknown_card_omits_unavailable_clipboard_action(self) -> None:
        caps = _capabilities(actions_supported=("apply_patch",))
        payload = {"type": "QuestionsCard", "title": "Questions", "foo": "bar"}
        card = studio_materialize_card(payload, caps)
        self.assertEqual(card["type"], "UnknownCard")
        self.assertEqual(card["actions"], [])

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
        self.assertIn("- Copy JSON (copy_to_clipboard)", unknown_text)

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
