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
    "ROADMAP.md Milestone 5: A2UI Presentation Layer (In Progress) -> scope bullets "
    "Add agent-side card/section/action payload generation with deterministic schemas "
    "and Provide CLI rendering fallback for the same structured payloads, with exit "
    "criterion A2UI schema/versioning is documented and stable"
)
VISION_MAPPING = (
    "PRODUCT_VISION.md Capability 5: Agent-to-UI protocol (A2UI) -> agent emits "
    "structured presentation artifacts that are consumable by CLI first, then "
    "Exegesis Console, then future Studio UI, and CLI remains able to render a "
    "text fallback of the same underlying artifacts; deterministic action ordering "
    "keeps that CLI text fallback stable"
)


class PacketPlannerTests(unittest.TestCase):
    def test_build_packet_uses_explicit_handoff_mappings(self) -> None:
        packet = planner.build_packet(
            lane="feat-a2ui-contract",
            branch="codex/feat-a2ui-contract",
            sha="abc123",
            meta={
                "scope_goal": "Canonicalize materialized A2UI action order.",
                "roadmap_items": [],
                "vision_capabilities": [],
                "required_handoff_fields": {
                    "roadmap_item": ROADMAP_MAPPING,
                    "vision_capability": VISION_MAPPING,
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
        self.assertIn("Provide CLI rendering fallback for the same structured payloads", packet)
        self.assertIn("text fallback of the same underlying artifacts", packet)
        self.assertNotIn("including the CLI fallback rendering path used by this fix", packet)
        self.assertNotIn("pending reviewer/integrator confirmation", packet)

    def test_build_packet_uses_saved_handoff_mappings_when_meta_lists_are_empty(self) -> None:
        packet = planner.build_packet(
            lane="feat-a2ui-contract",
            branch="codex/feat-a2ui-contract",
            sha="def456",
            meta={
                "scope_goal": "Canonicalize materialized A2UI action order.",
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
        self.assertNotIn("including the CLI fallback rendering path used by this fix", packet)
        self.assertNotIn("pending reviewer/integrator confirmation", packet)

    def test_apply_meta_defaults_does_not_invent_handoff_placeholders(self) -> None:
        meta = planner.apply_meta_defaults(
            {},
            ["tasks_completed", "roadmap_items", "vision_capabilities", "risk", "routing_provider_impact"],
        )

        self.assertEqual(meta["tasks_completed"], ["(auto) reviewer handback update; see lane commits for concrete changes"])
        self.assertNotIn("roadmap_items", meta)
        self.assertNotIn("vision_capabilities", meta)
        self.assertEqual(meta["risk"], "MEDIUM")
        self.assertEqual(meta["routing_provider_impact"], "None")


if __name__ == "__main__":
    unittest.main()
