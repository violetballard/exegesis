from __future__ import annotations

import unittest

from exegesis_textual.actions import (
    AppActionSpec,
    claude_tools_from_specs,
    google_tools_from_specs,
    mistral_tools_from_specs,
    openai_tools_from_specs,
    provider_tool_specs,
    validate_app_action_registry,
)
from exegesis_textual.actions.registry import app_action_specs, get_app_action_spec, palette_action_specs, tool_action_specs


class AppActionRegistryTests(unittest.TestCase):
    def test_registry_validates_unique_ids_shortcuts_and_schemas(self) -> None:
        validate_app_action_registry()

        specs = app_action_specs(include_local_developer=True)
        self.assertEqual(len({spec.id for spec in specs}), len(specs))
        shortcuts = [spec.shortcut.casefold() for spec in specs if spec.shortcut]
        self.assertEqual(len(set(shortcuts)), len(shortcuts))
        self.assertTrue(all(spec.input_schema["type"] == "object" for spec in specs))

    def test_palette_and_tool_visibility_are_separate(self) -> None:
        palette_ids = {spec.id for spec in palette_action_specs(include_local_developer=True)}
        tool_ids = {spec.id for spec in tool_action_specs()}

        self.assertIn("model_settings", palette_ids)
        self.assertNotIn("model_settings", tool_ids)
        self.assertIn("search_documents", palette_ids)
        self.assertIn("search_documents", tool_ids)
        self.assertIn("add_document_to_basket", tool_ids)
        self.assertEqual(get_app_action_spec("search_documents").safety, "read_only_auto")
        self.assertEqual(get_app_action_spec("add_document_to_basket").safety, "confirm_required")
        self.assertIn("close_document_tab", tool_ids)
        self.assertEqual(get_app_action_spec("close_document_tab").safety, "confirm_required")

    def test_basket_tool_schemas_accept_notebook_payloads(self) -> None:
        excerpt_schema = get_app_action_spec("add_excerpt_to_basket").input_schema
        document_schema = get_app_action_spec("add_document_to_basket").input_schema

        self.assertIn("document", excerpt_schema["properties"])
        self.assertIn("excerpt", excerpt_schema["properties"])
        self.assertIn("start", excerpt_schema["properties"])
        self.assertIn("end", excerpt_schema["properties"])
        self.assertIn("document", document_schema["properties"])

    def test_rewrite_tool_schema_accepts_header_target(self) -> None:
        rewrite_schema = get_app_action_spec("rewrite_selection").input_schema

        self.assertIn("instruction", rewrite_schema["properties"])
        self.assertIn("target_heading", rewrite_schema["properties"])
        self.assertIn("section_heading", rewrite_schema["properties"])

    def test_notebook_tool_catalog_allows_file_ops_but_not_project_or_import_ops(self) -> None:
        tool_ids = {spec.id for spec in tool_action_specs()}

        self.assertIn("rename_project", tool_ids)
        self.assertIn("close_chat", tool_ids)
        self.assertIn("close_document_tab", tool_ids)
        self.assertEqual(get_app_action_spec("close_chat").safety, "confirm_required")
        self.assertIn("create_memo", tool_ids)
        self.assertIn("create_folder", tool_ids)
        self.assertIn("update_selected_project_item", tool_ids)
        self.assertIn("restore_trash_item", tool_ids)
        self.assertEqual(get_app_action_spec("restore_trash_item").safety, "confirm_required")
        self.assertIn("trash_item", get_app_action_spec("restore_trash_item").input_schema["properties"])
        self.assertIn("filename", get_app_action_spec("restore_trash_item").input_schema["properties"])
        self.assertIn("permanently_delete_trash_item", tool_ids)
        self.assertEqual(get_app_action_spec("permanently_delete_trash_item").safety, "confirm_required")
        self.assertIn("trash_item", get_app_action_spec("permanently_delete_trash_item").input_schema["properties"])
        self.assertNotIn("new_project", tool_ids)
        self.assertNotIn("open_project_browser", tool_ids)
        self.assertNotIn("change_projects_directory", tool_ids)
        self.assertNotIn("import_document", tool_ids)
        self.assertNotIn("import_folder", tool_ids)

    def test_provider_adapters_emit_expected_tool_shapes(self) -> None:
        search_tool = next(tool for tool in provider_tool_specs() if tool.name == "search_documents")

        mistral = mistral_tools_from_specs([search_tool])[0]
        openai = openai_tools_from_specs([search_tool])[0]
        claude = claude_tools_from_specs([search_tool])[0]
        google = google_tools_from_specs([search_tool])[0]

        self.assertEqual(mistral["type"], "function")
        self.assertEqual(mistral["function"]["name"], "search_documents")
        self.assertEqual(mistral["function"]["parameters"]["required"], ["query"])
        self.assertEqual(openai["function"]["name"], "search_documents")
        self.assertEqual(claude["name"], "search_documents")
        self.assertEqual(claude["input_schema"]["required"], ["query"])
        self.assertEqual(google["function_declarations"][0]["name"], "search_documents")
        self.assertEqual(google["function_declarations"][0]["parameters"]["required"], ["query"])

    def test_google_adapter_groups_multiple_function_declarations_in_one_tool(self) -> None:
        tools = provider_tool_specs()[:2]

        google = google_tools_from_specs(tools)

        self.assertEqual(len(google), 1)
        self.assertEqual(
            [declaration["name"] for declaration in google[0]["function_declarations"]],
            [tool.name for tool in tools],
        )

    def test_validation_rejects_system_only_tool_visibility(self) -> None:
        bad = AppActionSpec(
            id="unsafe_settings",
            label="Unsafe",
            description="Bad spec.",
            category="system",
            shortcut=None,
            palette_visible=True,
            tool_visible=True,
            safety="system_only",
        )

        with self.assertRaises(ValueError):
            validate_app_action_registry((bad,))


if __name__ == "__main__":
    unittest.main()
