from __future__ import annotations

import unittest

from codex_packet_handoff.tools.planner import build_packet, resolve_reviewed_head_sha


class PacketPlannerTests(unittest.TestCase):
    def test_resolve_reviewed_head_sha_prefers_lane_metadata(self) -> None:
        self.assertEqual(
            resolve_reviewed_head_sha(
                {
                    "final_head_sha": "42820d4864f8b5137a6a9e05399ad68fe5b9d4ac",
                    "reviewed_implementation_range": "1d6057e9..78f173d5",
                },
                "deadbeef",
            ),
            "42820d4864f8b5137a6a9e05399ad68fe5b9d4ac",
        )
        self.assertEqual(
            resolve_reviewed_head_sha(
                {"reviewed_implementation_range": "1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac"},
                "deadbeef",
            ),
            "42820d4864f8b5137a6a9e05399ad68fe5b9d4ac",
        )
        self.assertEqual(resolve_reviewed_head_sha({}, "deadbeef"), "deadbeef")

    def test_build_packet_includes_completed_scope_and_cumulative_context(self) -> None:
        meta = {
            "scope_goal": "Complete the FTS-first retrieval MVP review packet.",
            "scope_completed": (
                "Shipped the cumulative 1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac retrieval thread: SQLite FTS stayed authoritative, "
                "the canonical retrieval query constructor was exported through both retrieval facades, and the "
                "retrieval payload/provenance helpers stayed deterministic while payloads were reconstructed from "
                "source bundles."
            ),
            "reviewed_implementation_range": "1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac",
            "tasks_completed": [
                "Kept SQLite FTS authoritative.",
                "Normalized retrieval payload and provenance snapshots.",
            ],
            "risk": "LOW",
            "roadmap_items": ["ROADMAP.md: Milestone 3: Real workflow loop"],
            "vision_capabilities": ["2. Retrieval-first context handling"],
            "routing_provider_impact": "None",
            "shared_file_exception": False,
        }

        packet = build_packet(
            lane="feat-retrieval-fts",
            branch="codex/feat-retrieval-fts",
            sha="42820d4864f8b5137a6a9e05399ad68fe5b9d4ac",
            meta=meta,
            files=[
                "src/qual/engine/retrieval/__init__.py",
                "src/qual/engine/retrieval/payload.py",
                "src/qual/retrieval/__init__.py",
                "src/qual/retrieval/service.py",
            ],
            gate_results=[("./quality-test.sh", 0)],
        )

        self.assertIn("## Scope goal", packet)
        self.assertIn("## Scope completed", packet)
        self.assertIn("- Reviewed implementation range: `1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac`", packet)
        self.assertIn("## Files changed (cumulative range)", packet)
        self.assertIn("Shipped the cumulative 1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac retrieval thread", packet)


if __name__ == "__main__":
    unittest.main()
