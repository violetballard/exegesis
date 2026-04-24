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
            "scope_goal": "Make canonical excerpt lookup fail closed to FTS-only IDs for the Milestone 3 retrieval path.",
            "scope_completed": (
                "Tightened the cumulative 1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac retrieval slice so "
                "canonical excerpt lookup stays on SQLite FTS, PageIndex-only excerpt IDs fail closed, and "
                "query-constraint provenance stays deterministic while payloads are reconstructed from source bundles."
            ),
            "reviewed_implementation_range": "1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac",
            "tasks_completed": [
                "Kept SQLite FTS authoritative.",
                "Normalized retrieval payload and provenance snapshots.",
            ],
            "risk": "LOW",
            "roadmap_items": ["ROADMAP.md: Milestone 3: Real workflow loop"],
            "canonical_demo_path_step": "retrieve relevant material",
            "canonical_demo_path_impact": (
                "This change makes `retrieve relevant material` more real by forcing excerpt "
                "lookup to fail closed unless the hit comes from the authoritative SQLite FTS path."
            ),
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
        self.assertIn("Tightened the cumulative 1d6057e9..42820d4864f8b5137a6a9e05399ad68fe5b9d4ac retrieval slice", packet)
        self.assertIn("### Canonical demo-path step advanced", packet)
        self.assertIn("- retrieve relevant material", packet)
        self.assertIn("authoritative SQLite FTS path", packet)

    def test_build_packet_uses_lane_default_demo_path_when_metadata_is_stale(self) -> None:
        meta = {
            "scope_goal": "Make canonical excerpt lookup fail closed to FTS-only IDs for the Milestone 3 retrieval path.",
            "tasks_completed": ["Kept SQLite FTS authoritative."],
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
            files=["src/qual/retrieval/service.py"],
            gate_results=[("./quality-test.sh", 0)],
        )

        self.assertIn("### Canonical demo-path step advanced", packet)
        self.assertIn("- retrieve relevant material", packet)
        self.assertIn("fail closed unless the hit comes from the authoritative SQLite FTS path", packet)


if __name__ == "__main__":
    unittest.main()
