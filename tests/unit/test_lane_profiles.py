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

    def test_feature_lane_prompt_includes_engine_execution_order(self) -> None:
        prompt = build_prompt("feat-commands", "/tmp/fake-worktree")

        self.assertIn(ENGINE_MILESTONE_FOCUS, prompt)
        self.assertIn("Active engine execution order", prompt)
        self.assertIn(engine_priority_lines()[0], prompt)
        self.assertIn("Textual UI lanes remain disabled", prompt)


if __name__ == "__main__":
    unittest.main()
