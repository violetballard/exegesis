from __future__ import annotations

import unittest

from codex_packet_handoff.tools.planner import select_packet_files, validate_meta


class PacketPlannerTests(unittest.TestCase):
    def test_validate_meta_requires_scope_completed(self) -> None:
        missing = validate_meta(
            {
                "tasks_completed": ["done"],
                "risk": "LOW",
                "roadmap_items": ["roadmap"],
                "vision_capabilities": ["vision"],
                "routing_provider_impact": "None",
            }
        )

        self.assertIn("scope_completed", missing)

    def test_select_packet_files_filters_related_files_to_lane_owned_paths(self) -> None:
        files = select_packet_files(
            "feat-retrieval-fts",
            {
                "related_implementation_files": [
                    "codex_packet_handoff/tools/planner.py",
                    "src/qual/retrieval/service.py",
                    "src/qual/engine/tools/retrieval_tools.py",
                    "src/qual/engine/retrieval/policy.py",
                ]
            },
            [
                "codex_packet_handoff/tools/planner.py",
                "src/qual/retrieval/service.py",
                "src/qual/engine/tools/retrieval_tools.py",
                "src/qual/engine/retrieval/policy.py",
            ],
        )

        self.assertEqual(
            files,
            ["src/qual/retrieval/service.py", "src/qual/engine/retrieval/policy.py"],
        )

    def test_select_packet_files_filters_raw_diff_to_lane_owned_paths(self) -> None:
        files = select_packet_files(
            "feat-retrieval-fts",
            {},
            [
                "codex_packet_handoff/tools/emit_feature_packet.py",
                "src/qual/retrieval/service.py",
                "src/qual/engine/retrieval/__init__.py",
                "src/qual/engine/tools/retrieval_tools.py",
            ],
        )

        self.assertEqual(
            files,
            ["src/qual/retrieval/service.py", "src/qual/engine/retrieval/__init__.py"],
        )


if __name__ == "__main__":
    unittest.main()
