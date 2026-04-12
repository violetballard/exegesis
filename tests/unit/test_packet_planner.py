from __future__ import annotations

import importlib.util
import pathlib
import unittest


def _load_planner_module():
    path = pathlib.Path(__file__).resolve().parents[2] / "codex_packet_handoff" / "tools" / "planner.py"
    spec = importlib.util.spec_from_file_location("packet_planner_test_module", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load planner module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


planner = _load_planner_module()

ROADMAP_MAPPING = (
    "ROADMAP.md Milestone 3: Real workflow loop (see ROADMAP.md lines 43-65) -> "
    "lane mapping `feat-a2ui-contract`: shared card/action contracts and selection "
    "models; scope bullet `move A2UI contracts into shared while keeping renderers "
    "outside shared`"
)
SCOPE_GOAL = (
    "Align packet planner defaults and review-facing packet text with the current "
    "Milestone 3 / capability 4 canon while preserving the runtime A2UI ordering "
    "fix already landed in b929fe6c7a1159c7882acedd247aca31a93cd123."
)
SCOPE_COMPLETED = (
    "Canonicalized stale feat-a2ui-contract handoff fields in the packet planner to "
    "the current Milestone 3 / capability 4 canon, removed the synthetic handback "
    "note for missing tasks_completed, and added explicit Scope completed packet "
    "support."
)
STALE_ROADMAP_MAPPING = (
    "ROADMAP.md Milestone 5: A2UI Presentation Layer (In Progress) (see ROADMAP.md "
    "lines 88-106) -> scope bullets Add agent-side card/section/action payload "
    "generation with deterministic schemas, and Provide CLI rendering fallback for "
    "the same structured payloads, with exit criterion A2UI schema/versioning is "
    "documented and stable; deterministic action ordering is the concrete A2UI "
    "payload-stability step completed by this lane"
)
VISION_MAPPING = (
    "PRODUCT_VISION.md Capability 4: Shared UI contract (A2UI) (see PRODUCT_VISION.md "
    "lines 39-41) -> cards/actions/selection types live in a client-agnostic shared "
    "layer; rendering adapters stay outside shared"
)
STALE_VISION_MAPPING = (
    "PRODUCT_VISION.md Capability 5: Agent-to-UI protocol (A2UI) (see PRODUCT_VISION.md "
    "lines 44-47) -> agent emits structured presentation artifacts that are "
    "consumable by CLI first, then Exegesis Console, then future Studio UI, and CLI "
    "remains able to render a text fallback of the same underlying artifacts; "
    "deterministic action ordering keeps that CLI text fallback stable"
)


class PacketPlannerTests(unittest.TestCase):
    def test_build_packet_uses_explicit_handoff_mappings(self) -> None:
        packet = planner.build_packet(
            lane="feat-a2ui-contract",
            branch="codex/feat-a2ui-contract",
            sha="abc123",
            meta={
                "scope_goal": SCOPE_GOAL,
                "scope_completed": SCOPE_COMPLETED,
                "roadmap_items": [],
                "vision_capabilities": [],
                "required_handoff_fields": {
                    "roadmap_items": [ROADMAP_MAPPING],
                    "vision_capabilities": [VISION_MAPPING],
                },
                "tasks_completed": ["Updated packet handoff fields."],
                "risk": "LOW",
                "routing_provider_impact": "None",
            },
            files=["src/qual/ui/a2ui.py"],
            gate_results=[("make scope-check", 0)],
        )

        self.assertIn(ROADMAP_MAPPING, packet)
        self.assertIn(VISION_MAPPING, packet)
        self.assertIn("## Required handoff fields", packet)
        self.assertIn("### Roadmap item(s) affected", packet)
        self.assertIn("### Vision capability affected", packet)
        self.assertIn("shared card/action contracts and selection models", packet)
        self.assertIn("client-agnostic shared layer", packet)
        self.assertIn("## Scope completed", packet)
        self.assertIn(SCOPE_COMPLETED, packet)
        self.assertNotIn("(auto) reviewer handback update", packet)
        self.assertNotIn("MVP Focus Through 2026-05-04", packet)
        self.assertNotIn("Capability 5: Agent-to-UI protocol", packet)

    def test_build_packet_uses_saved_handoff_mappings_when_meta_lists_are_empty(self) -> None:
        packet = planner.build_packet(
            lane="feat-a2ui-contract",
            branch="codex/feat-a2ui-contract",
            sha="def456",
            meta={
                "scope_goal": SCOPE_GOAL,
                "scope_completed": SCOPE_COMPLETED,
                "roadmap_items": [],
                "vision_capabilities": [],
                "last_handoff_fields": {
                    "roadmap_items": [ROADMAP_MAPPING],
                    "vision_capabilities": [VISION_MAPPING],
                },
                "tasks_completed": ["Synced saved packet handoff fields."],
                "risk": "LOW",
                "routing_provider_impact": "None",
            },
            files=["THREAD_PACKET.md"],
            gate_results=[("make scope-check", 0)],
        )

        self.assertIn(ROADMAP_MAPPING, packet)
        self.assertIn(VISION_MAPPING, packet)
        self.assertIn("## Required handoff fields", packet)
        self.assertIn("### Roadmap item(s) affected", packet)
        self.assertIn("### Vision capability affected", packet)
        self.assertIn("## Scope completed", packet)
        self.assertIn(SCOPE_COMPLETED, packet)
        self.assertNotIn("(auto) reviewer handback update", packet)
        self.assertNotIn("MVP Focus Through 2026-05-04", packet)
        self.assertNotIn("Capability 5: Agent-to-UI protocol", packet)

    def test_build_packet_uses_tasks_as_scope_completed_fallback(self) -> None:
        packet = planner.build_packet(
            lane="feat-a2ui-contract",
            branch="codex/feat-a2ui-contract",
            sha="def457",
            meta={
                "scope_goal": SCOPE_GOAL,
                "roadmap_items": [],
                "vision_capabilities": [],
                "required_handoff_fields": {
                    "roadmap_items": [ROADMAP_MAPPING],
                    "vision_capabilities": [VISION_MAPPING],
                },
                "tasks_completed": [
                    "Updated packet handoff fields.",
                    "Updated packet-planner regression coverage.",
                ],
                "risk": "LOW",
                "routing_provider_impact": "None",
            },
            files=["THREAD_PACKET.md"],
            gate_results=[("make scope-check", 0)],
        )

        self.assertIn("## Scope completed", packet)
        self.assertIn("Updated packet handoff fields.", packet)
        self.assertIn("Updated packet-planner regression coverage.", packet)
        self.assertIn("Updated packet handoff fields.; Updated packet-planner regression coverage.", packet)
        self.assertNotIn("(auto) reviewer handback update", packet)

    def test_build_packet_canonicalizes_stale_feat_a2ui_contract_mappings(self) -> None:
        packet = planner.build_packet(
            lane="feat-a2ui-contract",
            branch="codex/feat-a2ui-contract",
            sha="ghi789",
            meta={
                "scope_goal": SCOPE_GOAL,
                "scope_completed": SCOPE_COMPLETED,
                "roadmap_items": [STALE_ROADMAP_MAPPING],
                "vision_capabilities": [STALE_VISION_MAPPING],
                "tasks_completed": ["Canonicalized stale planner handoff fields."],
                "risk": "LOW",
                "routing_provider_impact": "None",
            },
            files=["THREAD_PACKET.md"],
            gate_results=[("make scope-check", 0)],
        )

        self.assertIn(ROADMAP_MAPPING, packet)
        self.assertIn(VISION_MAPPING, packet)
        self.assertIn("## Scope completed", packet)
        self.assertIn(SCOPE_COMPLETED, packet)
        self.assertNotIn("MVP Focus Through 2026-05-04", packet)
        self.assertNotIn("Capability 5: Agent-to-UI protocol", packet)
        self.assertNotIn("Milestone 5: A2UI Presentation Layer", packet)

    def test_apply_meta_defaults_leaves_tasks_missing_when_missing(self) -> None:
        meta = planner.apply_meta_defaults(
            {},
            ["tasks_completed", "roadmap_items", "vision_capabilities", "risk", "routing_provider_impact"],
        )

        self.assertNotIn("tasks_completed", meta)
        self.assertNotIn("roadmap_items", meta)
        self.assertNotIn("vision_capabilities", meta)
        self.assertEqual(meta["risk"], "MEDIUM")
        self.assertEqual(meta["routing_provider_impact"], "None")


if __name__ == "__main__":
    unittest.main()
