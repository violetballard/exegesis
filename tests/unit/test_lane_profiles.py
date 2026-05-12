from __future__ import annotations

import unittest

from codex_packet_handoff.tools.lane_profiles import (
    ENGINE_MILESTONE_FOCUS,
    default_lane_meta,
    engine_priority_lines,
)
from codex_packet_handoff.tools.launch_feature_lanes import build_prompt
from codex_packet_handoff.tools.planner import build_packet, merge_lane_meta_defaults


class LaneProfileDefaultsTests(unittest.TestCase):
    def test_default_lane_meta_seeds_engine_run_expectations(self) -> None:
        meta = default_lane_meta("feat-engine-runs")

        self.assertIn("Milestone 3", meta["roadmap_items"][0])
        self.assertTrue(meta["definition_of_done"])
        self.assertTrue(meta["do_not_spend_time_on"])
        self.assertIn("engine-side acceptance flow", " ".join(meta["definition_of_done"]))

    def test_planner_merges_lane_defaults_into_sparse_meta(self) -> None:
        merged = merge_lane_meta_defaults(
            "feat-a2ui-contract",
            {
                "scope_goal": "",
                "tasks_completed": [],
                "risk": "LOW",
                "roadmap_items": [],
                "vision_capabilities": [],
                "routing_provider_impact": "",
            },
        )

        self.assertTrue(merged["scope_goal"])
        self.assertTrue(merged["roadmap_items"])
        self.assertTrue(merged["vision_capabilities"])
        self.assertTrue(merged["definition_of_done"])
        self.assertTrue(merged["do_not_spend_time_on"])

    def test_planner_packet_includes_program_brief_and_lane_guardrails(self) -> None:
        meta = merge_lane_meta_defaults(
            "feat-context-storage",
            {
                "tasks_completed": ["Recovered malformed basket payloads safely."],
                "shared_file_exception": False,
            },
        )

        packet = build_packet(
            "feat-context-storage",
            "codex/feat-context-storage",
            "deadbeef",
            meta,
            ["engine/src/exegesis_engine/storage/project_store.py"],
            [("make scope-check", 0)],
        )

        self.assertIn(ENGINE_MILESTONE_FOCUS, packet)
        self.assertIn("## Definition of done for this lane", packet)
        self.assertIn("## Do not spend time on", packet)
        self.assertIn(engine_priority_lines()[0], packet)

    def test_planner_packet_supports_metadata_only_refresh_traceability(self) -> None:
        packet = build_packet(
            "feat-retrieval-fts",
            "codex/feat-retrieval-fts",
            "refreshsha",
            {
                "scope_goal": "Refresh the retrieval handoff packet against the reviewed implementation slice.",
                "scope_completed": "Re-pointed the handoff to the actual reviewed retrieval implementation.",
                "tasks_completed": ["Updated the packet traceability and reviewed file list."],
                "roadmap_items": ["Milestone 3: Real workflow loop"],
                "vision_capabilities": ["Retrieval-first context handling"],
                "routing_provider_impact": "None",
                "reviewed_commit": "implsha",
                "reviewed_commit_range": "base..implsha",
                "packet_head_role": "metadata-only reviewer-fix finalization",
                "metadata_only_note": "The current branch tip is a docs-only packet refresh; review the implementation at `implsha`.",
                "reviewed_files": ["src/qual/retrieval/service.py"],
                "metadata_only_files": ["THREAD_PACKET.md"],
            },
            ["THREAD_PACKET.md"],
            [("make scope-check", 0)],
        )

        self.assertIn("- Commit: `implsha`", packet)
        self.assertIn("- Packet refresh commit: `refreshsha`", packet)
        self.assertIn("- Packet refresh role: `metadata-only reviewer-fix finalization`", packet)
        self.assertIn("- Reviewed implementation range: `base..implsha`", packet)
        self.assertIn("## Packet traceability note", packet)
        self.assertIn("### Reviewed implementation files", packet)
        self.assertIn("### Metadata-only handoff files", packet)

    def test_planner_packet_accepts_scope_completed_string(self) -> None:
        packet = build_packet(
            "feat-engine-runs",
            "codex/feat-engine-runs",
            "deadbeef",
            {
                "scope_goal": "Keep engine manifests deterministic across legacy replay paths.",
                "scope_completed": "Recovered legacy run provenance and kept retrieval evidence in serialized manifests.",
                "tasks_completed": ["Updated the engine-run manifest backfill path."],
                "roadmap_items": ["Milestone 3: Real workflow loop"],
                "vision_capabilities": ["Auditable state and workflow"],
                "routing_provider_impact": "None",
            },
            ["src/qual/engine/run_pipeline.py"],
            [("make scope-check", 0)],
        )

        self.assertIn("## Scope completed", packet)
        self.assertIn(
            "- Recovered legacy run provenance and kept retrieval evidence in serialized manifests.",
            packet,
        )

    def test_feature_lane_prompt_includes_engine_execution_order(self) -> None:
        prompt = build_prompt("feat-commands", "/tmp/fake-worktree")

        self.assertIn(ENGINE_MILESTONE_FOCUS, prompt)
        self.assertIn("Active engine execution order", prompt)
        self.assertIn(engine_priority_lines()[0], prompt)
        self.assertIn("Textual UI lanes remain disabled", prompt)
        self.assertIn("Do not use full-file `cat`, full-file Read", prompt)
        self.assertIn("First use `rg -n`", prompt)
        self.assertIn("normally <=80 lines", prompt)


if __name__ == "__main__":
    unittest.main()
