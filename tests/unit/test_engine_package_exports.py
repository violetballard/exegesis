import json
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from exegesis_engine.api import ExegesisAppService, PatchPreview, PatchResolution

import src.qual.engine as engine
import src.qual.engine.retrieval as engine_retrieval
import src.qual.retrieval as package_retrieval


class EnginePackageExportTests(unittest.TestCase):
    def test_lazy_public_exports_match_engine_api_surface(self) -> None:
        expected_exports = [
            "EngineRuntime",
            "EngineService",
            "EngineRunFlowResult",
            "EngineRunFlowSnapshot",
            "EngineRunRecord",
            "EngineRunService",
            "RunArtifact",
            "RunEvent",
            "RunSummary",
        ]

        self.assertEqual(engine.__all__, expected_exports)
        for export_name in expected_exports:
            self.assertIn(export_name, dir(engine))

    def test_lazy_export_resolver_imports_target_modules_on_demand(self) -> None:
        sentinels = {name: object() for name in engine.__all__}

        def fake_import_module(module_name: str) -> SimpleNamespace:
            attrs = {
                attr_name: value
                for attr_name, (target_module, _target_attr) in engine._EXPORTS.items()
                if target_module == module_name
                for value in [sentinels[attr_name]]
            }
            return SimpleNamespace(**attrs)

        for export_name in engine.__all__:
            engine.__dict__.pop(export_name, None)

        with patch("src.qual.engine.import_module", side_effect=fake_import_module) as import_module:
            for export_name in engine.__all__:
                self.assertIs(getattr(engine, export_name), sentinels[export_name])

        imported_modules = [call.args[0] for call in import_module.call_args_list]
        self.assertIn("src.qual.engine.service", imported_modules)
        self.assertIn("src.qual.engine.run_pipeline", imported_modules)

    def test_unknown_export_raises_attribute_error(self) -> None:
        with self.assertRaises(AttributeError):
            engine.__getattr__("MissingExport")

    def test_retrieval_query_constructor_rejects_boolean_max_results(self) -> None:
        for constructor in (engine_retrieval.build_retrieval_query, package_retrieval.build_retrieval_query):
            with self.subTest(constructor=constructor.__module__):
                with self.assertRaisesRegex(TypeError, "max_results must be an integer retrieval limit"):
                    constructor(
                        query_text="memo comparison",
                        scope="vault",
                        intent="compare",
                        constraints={"max_results": True},
                        confidentiality_profile="standard",
                    )


class ExegesisEngineAppServicePatchResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmp.name)
        (self.project_root / "draft.md").write_text("hello world\n", encoding="utf-8")
        self.service = ExegesisAppService()
        self.service.open_project(self.project_root)
        self.service.open_document("draft.md")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_resolve_patch_accepts_and_persists_document_for_continuation(self) -> None:
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")

        preview = self.service.preview_patch(patch.patch_id)

        self.assertIsInstance(preview, PatchPreview)
        self.assertEqual(preview.patch_id, patch.patch_id)
        self.assertEqual(preview.target_document_id, "draft.md")
        self.assertEqual(preview.target_range, (6, 11))
        self.assertEqual(preview.original_text, "world")
        self.assertEqual(preview.proposed_text, "team")
        self.assertIn("-world", preview.preview_text)
        self.assertIn("+team", preview.preview_text)

        resolution = self.service.resolve_patch(patch.patch_id, decision="accepted", persist=True)

        self.assertIsInstance(resolution, PatchResolution)
        self.assertEqual(resolution.decision, "accepted")
        self.assertEqual(resolution.document_content, "hello team\n")
        self.assertFalse(resolution.dirty)
        self.assertTrue(resolution.persisted)
        self.assertIsNone(self.service.state.document.current_selection)
        self.assertEqual((self.project_root / "draft.md").read_text(encoding="utf-8"), "hello team\n")
        self.assertEqual(self.service.state.workflow.focused_card_id, f"{patch.patch_id}:resolution")
        self.assertEqual(self.service.state.workflow.cards[-1].metadata["decision"], "accepted")
        self.assertEqual(self.service.state.workflow.cards[-1].metadata["target_range"], [6, 11])
        self.assertEqual(self.service.state.workflow.cards[-1].metadata["original_text"], "world")
        self.assertEqual(self.service.state.workflow.cards[-1].metadata["proposed_text"], "team")
        self.assertIn("+team", self.service.state.workflow.cards[-1].metadata["preview_text"])

    def test_failed_accepted_patch_attempt_leaves_proposal_pending(self) -> None:
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")
        self.service.state.document.current_document_content = "hello city\n"

        with self.assertRaisesRegex(ValueError, "original text does not match"):
            self.service.resolve_patch(patch.patch_id, decision="accepted")

        preview = self.service.preview_patch(patch.patch_id)
        described = self.service.describe_state()
        self.assertEqual(preview.patch_id, patch.patch_id)
        self.assertEqual(preview.original_text, "world")
        self.assertEqual(preview.proposed_text, "team")
        self.assertEqual(described["pending_patch_proposals"][0]["patch_id"], patch.patch_id)
        self.assertEqual(described["pending_patch_proposals"][0]["target_range"], [6, 11])
        self.assertEqual(self.service.state.workflow.focused_card_id, patch.patch_id)

    def test_resolve_patch_rejects_without_mutating_document(self) -> None:
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")

        resolution = self.service.resolve_patch(patch.patch_id, decision="rejected")

        self.assertEqual(resolution.decision, "rejected")
        self.assertEqual(resolution.document_content, "hello world\n")
        self.assertFalse(resolution.dirty)
        self.assertFalse(resolution.persisted)
        self.assertIsNone(self.service.state.document.current_selection)
        self.assertEqual((self.project_root / "draft.md").read_text(encoding="utf-8"), "hello world\n")
        self.assertEqual(self.service.state.workflow.cards[-1].metadata["decision"], "rejected")

    def test_advertised_apply_patch_action_resolves_pending_patch(self) -> None:
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")
        patch_card = self.service.state.workflow.cards[-1]
        action = next(item for item in patch_card.actions if item["id"] == "apply_patch")

        self.assertEqual(action, {"id": "apply_patch", "label": "Apply", "payload": {"patch_id": patch.patch_id}})
        resolution = self.service.apply_patch(action["payload"]["patch_id"])
        described = self.service.describe_state()

        self.assertIsInstance(resolution, PatchResolution)
        self.assertEqual(resolution.decision, "accepted")
        self.assertEqual(resolution.document_content, "hello team\n")
        self.assertTrue(resolution.dirty)
        self.assertFalse(resolution.persisted)
        self.assertEqual(described["pending_patch_proposals"], [])
        self.assertIsNone(described["document"]["current_selection"])
        self.assertEqual(described["document"]["current_document_content"], "hello team\n")
        self.assertTrue(described["document"]["dirty"])
        self.assertEqual(described["workflow"]["focused_card_id"], f"{patch.patch_id}:resolution")
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["card_type"], "patch_resolution")
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["metadata"]["patch_id"], patch.patch_id)
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["metadata"]["decision"], "accepted")
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["metadata"]["target_range"], [6, 11])
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["metadata"]["original_text"], "world")
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["metadata"]["proposed_text"], "team")
        self.assertIn("+team", described["workflow"]["patch_resolutions"][0]["metadata"]["preview_text"])
        self.assertFalse(described["workflow"]["patch_resolutions"][0]["metadata"]["persisted"])
        self.assertEqual((self.project_root / "draft.md").read_text(encoding="utf-8"), "hello world\n")

    def test_advertised_reject_patch_action_resolves_pending_patch(self) -> None:
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")
        patch_card = self.service.state.workflow.cards[-1]
        action = next(item for item in patch_card.actions if item["id"] == "reject_patch")

        self.assertEqual(action, {"id": "reject_patch", "label": "Reject", "payload": {"patch_id": patch.patch_id}})
        resolution = self.service.reject_patch(action["payload"]["patch_id"])
        described = self.service.describe_state()

        self.assertIsInstance(resolution, PatchResolution)
        self.assertEqual(resolution.decision, "rejected")
        self.assertEqual(resolution.document_content, "hello world\n")
        self.assertFalse(resolution.dirty)
        self.assertFalse(resolution.persisted)
        self.assertEqual(described["pending_patch_proposals"], [])
        self.assertIsNone(described["document"]["current_selection"])
        self.assertEqual(described["document"]["current_document_content"], "hello world\n")
        self.assertFalse(described["document"]["dirty"])
        self.assertEqual(described["workflow"]["focused_card_id"], f"{patch.patch_id}:resolution")
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["card_type"], "patch_resolution")
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["metadata"]["patch_id"], patch.patch_id)
        self.assertEqual(described["workflow"]["patch_resolutions"][0]["metadata"]["decision"], "rejected")
        self.assertFalse(described["workflow"]["patch_resolutions"][0]["metadata"]["persisted"])
        self.assertEqual((self.project_root / "draft.md").read_text(encoding="utf-8"), "hello world\n")

    def test_resolve_patch_rejects_unknown_decision_before_consuming_proposal(self) -> None:
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")

        with self.assertRaisesRegex(ValueError, "patch decision must be accepted or rejected"):
            self.service.resolve_patch(patch.patch_id, decision="maybe")  # type: ignore[arg-type]

        preview = self.service.preview_patch(patch.patch_id)
        self.assertEqual(preview.proposed_text, "team")

        resolution = self.service.resolve_patch(patch.patch_id, decision="accepted")
        self.assertEqual(resolution.document_content, "hello team\n")

    def test_describe_state_records_pending_patch_preview_and_resolution_chain(self) -> None:
        self.service.add_basket_item(
            "retrieval:fts:draft.md:1",
            label="Draft excerpt",
            payload={"source": "fts"},
        )
        plan = self.service.plan_from_basket()
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")

        pending = self.service.describe_state()

        self.assertEqual(pending["project"]["open_document_id"], "draft.md")
        self.assertEqual(pending["document"]["current_selection"]["selected_text"], "world")
        self.assertEqual(pending["basket"]["selected_basket_item_id"], "retrieval:fts:draft.md:1")
        self.assertEqual(pending["workflow"]["cards"][0]["id"], plan.id)
        self.assertEqual(pending["workflow"]["command_history"], ["plan_from_basket", "revise_selection"])
        self.assertEqual(
            [record["action"] for record in pending["workflow"]["action_records"]],
            ["plan_from_basket", "revise_selection"],
        )
        self.assertEqual(pending["workflow"]["action_records"][0]["sequence"], 1)
        self.assertEqual(
            pending["workflow"]["action_records"][0]["request"],
            {"basket_item_ids": ["retrieval:fts:draft.md:1"], "basket_item_count": 1},
        )
        self.assertEqual(pending["workflow"]["action_records"][0]["result"]["card_id"], plan.id)
        self.assertEqual(
            pending["workflow"]["action_records"][1]["request"],
            {
                "document_id": "draft.md",
                "target_range": [6, 11],
                "original_text": "world",
                "proposed_text": "team",
            },
        )
        self.assertEqual(pending["workflow"]["action_records"][1]["result"]["patch_id"], patch.patch_id)
        self.assertEqual(pending["pending_patch_proposals"][0]["patch_id"], patch.patch_id)
        self.assertEqual(pending["pending_patch_proposals"][0]["target_range"], [6, 11])
        self.assertEqual(pending["pending_patch_proposals"][0]["original_text"], "world")
        self.assertIn("+team", pending["pending_patch_proposals"][0]["preview_text"])

        self.service.resolve_patch(patch.patch_id, decision="accepted", persist=True)
        resolved = self.service.describe_state()

        self.assertEqual(resolved["pending_patch_proposals"], [])
        self.assertEqual(resolved["document"]["current_document_content"], "hello team\n")
        self.assertFalse(resolved["document"]["dirty"])
        self.assertIsNone(resolved["document"]["current_selection"])
        self.assertEqual(resolved["workflow"]["patch_resolutions"][0]["metadata"]["decision"], "accepted")
        self.assertEqual(resolved["workflow"]["focused_card_id"], f"{patch.patch_id}:resolution")
        self.assertEqual(
            resolved["workflow"]["command_history"],
            ["plan_from_basket", "revise_selection", "resolve_patch"],
        )
        self.assertEqual(
            [record["action"] for record in resolved["workflow"]["action_records"]],
            ["plan_from_basket", "revise_selection", "resolve_patch"],
        )
        self.assertEqual(
            resolved["workflow"]["action_records"][2]["request"],
            {"patch_id": patch.patch_id, "decision": "accepted", "persist": True},
        )
        self.assertEqual(
            resolved["workflow"]["action_records"][2]["result"],
            {
                "patch_id": patch.patch_id,
                "decision": "accepted",
                "target_document_id": "draft.md",
                "dirty": False,
                "persisted": True,
            },
        )

    def test_save_session_snapshot_persists_current_engine_loop_state(self) -> None:
        self.service.add_basket_item("retrieval:fts:draft.md:1", label="Draft excerpt")
        self.service.plan_from_basket()
        self.service.set_document_selection(start=6, end=11)
        patch = self.service.revise_selection(proposed_text="team")
        self.service.resolve_patch(patch.patch_id, decision="rejected")

        session = self.service.save_session_snapshot()

        self.assertEqual(session.item_type, "session")
        self.assertEqual(session.id, "sessions/current-session.md")
        snapshot_text = (self.project_root / session.id).read_text(encoding="utf-8")
        snapshot_json = snapshot_text.split("```json\n", 1)[1].split("\n```", 1)[0]
        snapshot = json.loads(snapshot_json)
        self.assertEqual(snapshot["document"]["current_document_content"], "hello world\n")
        self.assertEqual(snapshot["workflow"]["patch_resolutions"][0]["metadata"]["decision"], "rejected")
        self.assertEqual(snapshot["workflow"]["patch_resolutions"][0]["metadata"]["target_range"], [6, 11])
        self.assertEqual(snapshot["workflow"]["patch_resolutions"][0]["metadata"]["original_text"], "world")
        self.assertEqual(snapshot["workflow"]["patch_resolutions"][0]["metadata"]["proposed_text"], "team")
        self.assertIn("+team", snapshot["workflow"]["patch_resolutions"][0]["metadata"]["preview_text"])
        self.assertEqual(
            snapshot["workflow"]["command_history"],
            ["plan_from_basket", "revise_selection", "resolve_patch", "save_session_snapshot"],
        )
        self.assertEqual(
            [record["action"] for record in snapshot["workflow"]["action_records"]],
            ["plan_from_basket", "revise_selection", "resolve_patch", "save_session_snapshot"],
        )
        self.assertEqual(snapshot["workflow"]["action_records"][3]["sequence"], 4)
        self.assertEqual(
            snapshot["workflow"]["action_records"][3]["request"],
            {"session_id": "sessions/current-session.md"},
        )
        self.assertEqual(
            snapshot["workflow"]["action_records"][3]["result"],
            {"snapshot_kind": "app_state"},
        )
        self.assertEqual(snapshot["pending_patch_proposals"], [])
        self.assertTrue(any(item.id == session.id for item in self.service.state.project.sessions))
        state_session = next(item for item in self.service.state.project.sessions if item.id == session.id)
        self.assertEqual(state_session.metadata, session.metadata)
        described = self.service.describe_state()
        self.assertEqual(described["project"]["sessions"][0]["metadata"], session.metadata)
        self.assertEqual(
            described["workflow"]["command_history"],
            ["plan_from_basket", "revise_selection", "resolve_patch", "save_session_snapshot"],
        )
        self.assertEqual(described["workflow"]["action_records"][3]["result"]["item_id"], session.id)
        self.assertEqual(described["workflow"]["action_records"][3]["result"]["path"], session.path)

        self.service.list_project_items()
        refreshed_session = next(item for item in self.service.state.project.sessions if item.id == session.id)
        self.assertEqual(refreshed_session.metadata, session.metadata)


if __name__ == "__main__":
    unittest.main()
