from __future__ import annotations

import unittest

from codex_packet_handoff.tools.planner import build_packet


class PlannerPacketTests(unittest.TestCase):
    def test_scope_note_separates_owned_source_and_approved_exception_updates(self) -> None:
        packet = build_packet(
            lane="feat-context-storage",
            branch="codex/feat-context-storage",
            sha="deadbeef",
            meta={
                "scope_goal": "Harden recovery and packet hygiene.",
                "tasks_completed": ["Patch recovery", "Add regression tests"],
                "risk": "MEDIUM",
                "roadmap_items": ["Milestone 1"],
                "vision_capabilities": ["Capability 1"],
                "routing_provider_impact": "None",
                "shared_file_exception": True,
            },
            files=[
                "src/qual/context/store.py",
                "tests/unit/test_context_storage_recovery.py",
            ],
            gate_results=[("./quality-test.sh", 0)],
        )

        self.assertIn("Lane-owned source changes: `YES`", packet)
        self.assertIn("Approved non-owned metadata/state updates: `YES`", packet)


if __name__ == "__main__":
    unittest.main()
