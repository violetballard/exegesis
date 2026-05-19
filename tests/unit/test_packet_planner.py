from __future__ import annotations

import unittest

from packet_garden.tools.planner import build_packet, build_shared_packet, should_skip_for_active_feature, validate_meta


class PacketPlannerTests(unittest.TestCase):
    def test_active_feature_does_not_block_reemit_after_review_notes(self) -> None:
        state = {"lane_refill": {"feat-engine-runs": {"feature_active": True}}}

        self.assertTrue(should_skip_for_active_feature(state, "feat-engine-runs", fast_reemit=False))
        self.assertFalse(should_skip_for_active_feature(state, "feat-engine-runs", fast_reemit=True))

    def test_validate_meta_requires_approval_note_for_shared_files(self) -> None:
        missing = validate_meta(
            {
                "scope_completed": "Engine-run lifecycle hardening is complete within `src/qual/engine/**` and its direct tests.",
                "tasks_completed": ["Hardened the engine run lifecycle and its direct tests under `src/qual/engine/**`."],
                "risk": "LOW",
                "roadmap_items": ["Milestone 5: A2UI Presentation Layer."],
                "vision_capabilities": ["Agent-to-UI protocol (A2UI)."],
                "routing_provider_impact": "None",
                "shared_file_exception": True,
            }
        )

        self.assertIn("scope_goal", missing)
        self.assertIn("approved_exception_note", missing)

    def test_build_packet_stays_lane_only_for_owned_paths(self) -> None:
        packet = build_packet(
            lane="feat-engine-runs",
            branch="codex/feat-engine-runs",
            sha="deadbeef",
            meta={
                "scope_goal": "Harden the engine run lifecycle in `src/qual/engine/**` and its direct tests.",
                "scope_completed": "Engine-run lifecycle hardening is complete within `src/qual/engine/**` and its direct tests.",
                "tasks_completed": [
                    "Hardened the engine run lifecycle and its direct tests under `src/qual/engine/**`.",
                    "Kept the feature scope limited to engine-owned paths and direct tests.",
                    "Recorded the required roadmap and vision mapping for `Milestone 5: A2UI Presentation Layer` and `Agent-to-UI protocol (A2UI)`.",
                ],
                "risk": "LOW",
                "roadmap_items": ["Milestone 5: A2UI Presentation Layer."],
                "vision_capabilities": ["Agent-to-UI protocol (A2UI).", "Auditable generation."],
                "routing_provider_impact": "None",
            },
            files=[
                "src/qual/engine/run_pipeline.py",
                "tests/unit/test_bulk_draft_routing.py",
                "tests/unit/test_engine_run_pipeline.py",
            ],
            gate_results=[
                ("make scope-check", 0),
                ("./quality-test.sh", 0),
            ],
        )

        self.assertIn("## Scope completed", packet)
        self.assertIn("Engine-run lifecycle hardening is complete within `src/qual/engine/**` and its direct tests.", packet)
        self.assertIn("1. Hardened the engine run lifecycle and its direct tests under `src/qual/engine/**`.", packet)
        self.assertIn("2. Kept the feature scope limited to engine-owned paths and direct tests.", packet)
        self.assertIn("## Required handoff fields", packet)
        self.assertIn("Milestone 5: A2UI Presentation Layer.", packet)
        self.assertIn("Agent-to-UI protocol (A2UI).", packet)
        self.assertIn("Auditable generation.", packet)
        self.assertIn("### Engine-owned files", packet)
        self.assertIn("`src/qual/engine/run_pipeline.py`", packet)
        self.assertIn("`tests/unit/test_bulk_draft_routing.py`", packet)
        self.assertIn("`tests/unit/test_engine_run_pipeline.py`", packet)
        self.assertIn("- Shared/integrator-locked edits: `NO`", packet)
        self.assertIn("- Ownership note: lane packet is limited to `src/qual/engine/**`", packet)
        self.assertIn("`tests/unit/test_engine_run_pipeline.py`", packet)
        self.assertNotIn(
            "- Ownership note: lane packet is limited to `src/qual/engine/**` and its direct tests.",
            packet,
        )
        self.assertNotIn("## Approved exception note", packet)
        self.assertNotIn("### Approved shared/integrator-locked files", packet)

    def test_build_packet_ignores_shared_files_in_lane_packet_output(self) -> None:
        packet = build_packet(
            lane="feat-engine-runs",
            branch="codex/feat-engine-runs",
            sha="deadbeef",
            meta={
                "scope_goal": "Harden the engine run lifecycle in `src/qual/engine/**` and its direct tests.",
                "scope_completed": "Engine-run lifecycle hardening is complete within `src/qual/engine/**` and its direct tests.",
                "tasks_completed": [
                    "Hardened the engine run lifecycle and its direct tests under `src/qual/engine/**`.",
                    "Kept the feature scope limited to engine-owned paths and direct tests.",
                ],
                "risk": "LOW",
                "roadmap_items": ["Milestone 5: A2UI Presentation Layer."],
                "vision_capabilities": ["Agent-to-UI protocol (A2UI).", "Auditable generation."],
                "routing_provider_impact": "None",
                "shared_file_exception": True,
                "approved_exception_note": (
                    "Approved shared/integrator-locked handoff maintenance is recorded in the companion shared packet."
                ),
            },
            files=[
                "src/qual/engine/run_pipeline.py",
                ".codex/kickoff_packets/feat-engine-runs.shared.md",
                "THREAD_PACKET.md",
                "packet_garden/tools/planner.py",
                "tests/unit/test_packet_planner.py",
            ],
            gate_results=[("make scope-check", 0)],
            companion_shared_packet=".codex/kickoff_packets/feat-engine-runs.shared.md",
        )

        self.assertIn("## Approved exception note", packet)
        self.assertIn("### Approved shared/integrator-locked changes", packet)
        self.assertIn(
            "- These handoff-maintenance edits are recorded in the companion shared packet and are not part of lane-owned feature scope.",
            packet,
        )
        self.assertIn("- Companion shared packet: .codex/kickoff_packets/feat-engine-runs.shared.md", packet)
        self.assertIn("- Shared/integrator-locked edits: `YES`", packet)
        self.assertIn("- Ownership note: lane packet is limited to `src/qual/engine/**`", packet)
        self.assertIn(
            "approved shared handoff-maintenance artifacts are recorded in the companion shared packet.",
            packet,
        )
        self.assertNotIn("### Approved shared/integrator-locked files", packet)
        self.assertIn(
            "Approved shared/integrator-locked handoff maintenance is recorded in the companion shared packet.",
            packet,
        )

    def test_build_shared_packet_lists_approved_shared_files(self) -> None:
        packet = build_shared_packet(
            lane="feat-engine-runs",
            branch="codex/feat-engine-runs",
            sha="deadbeef",
            meta={
                "scope_goal": "Harden the engine run lifecycle in `src/qual/engine/**` and its direct tests.",
                "scope_completed": "Shared handoff-maintenance edits are recorded separately from the lane-only `src/qual/engine/**` feature packet.",
                "tasks_completed": [
                    "Split the shared coordinator and handoff-maintenance edits into the companion shared packet.",
                    "Kept the primary engine packet focused on `src/qual/engine/**` and its direct tests.",
                ],
                "risk": "LOW",
                "roadmap_items": ["Milestone 5: A2UI Presentation Layer."],
                "vision_capabilities": ["Agent-to-UI protocol (A2UI).", "Auditable generation."],
                "routing_provider_impact": "None",
                "approved_exception_note": (
                    "Approved shared/integrator-locked handoff maintenance is recorded in the companion shared packet."
                ),
            },
            files=[
                "src/qual/engine/run_pipeline.py",
                "THREAD_PACKET.md",
                "packet_garden/tools/planner.py",
                "tests/unit/test_packet_planner.py",
            ],
            gate_results=[("make scope-check", 0), ("./quality-test.sh", 0)],
            companion_lane_packet=".codex/kickoff_packets/feat-engine-runs.md",
        )

        self.assertIn("## Handoff Alignment", packet)
        self.assertIn("- Scope completed: shared handoff-maintenance edits are recorded separately from the lane-only", packet)
        self.assertIn("`src/qual/engine/**`", packet)
        self.assertIn("`tests/unit/test_engine_run_pipeline.py` feature packet.", packet)
        self.assertIn("- Shared/integrator-locked edits: `YES`", packet)
        self.assertIn(
            "- Approval note: Approved shared/integrator-locked handoff maintenance is recorded in the companion shared packet.",
            packet,
        )
        self.assertIn("- Companion lane packet: .codex/kickoff_packets/feat-engine-runs.md", packet)
        self.assertIn("### Approved shared/integrator-locked files", packet)
        self.assertIn("`THREAD_PACKET.md`", packet)
        self.assertIn("`packet_garden/tools/planner.py`", packet)
        self.assertIn("`tests/unit/test_packet_planner.py`", packet)


if __name__ == "__main__":
    unittest.main()
