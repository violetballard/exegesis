from __future__ import annotations

import unittest
from dataclasses import dataclass, field

from src.qual.engine.terminal_chat import (
    DEEP_PLANNER_MODEL,
    TERMINAL_CHAT_MODEL,
    build_terminal_error_card,
    route_terminal_model,
    run_hidden_planner_mode,
    supports_terminal_block,
    validate_or_retry_tool_call,
    TerminalRoutingInput,
)


@dataclass
class _ResidentStub:
    events: list[str] = field(default_factory=list)

    def snapshot(self) -> str:
        self.events.append("snapshot")
        return "snap-1"

    def unload_all(self) -> None:
        self.events.append("unload")

    def load_model(self, model_id: str, *, max_ctx: int | None = None) -> None:
        self.events.append(f"load:{model_id}:{max_ctx}")

    def restore(self, snapshot_id: str) -> bool:
        self.events.append(f"restore:{snapshot_id}")
        return True


class TerminalChatRoutingTests(unittest.TestCase):
    def test_terminal_defaults_to_magistral(self) -> None:
        decision = route_terminal_model(
            _input(
                operation_kind="terminal_chat",
                sku_gb=128,
                pack_contains_qwen=True,
                runtime_supports_qwen=True,
                requires_multi_step_tools=False,
                input_tokens=100,
                constraints_count=0,
            )
        )
        self.assertEqual(decision.model_used, TERMINAL_CHAT_MODEL)
        self.assertFalse(decision.escalation_applied)
        self.assertEqual(decision.mode_used, "none")

    def test_orchestration_escalates_to_qwen_when_resident_available(self) -> None:
        decision = route_terminal_model(
            _input(
                operation_kind="terminal_tool_orchestration",
                sku_gb=256,
                pack_contains_qwen=True,
                runtime_supports_qwen=True,
            )
        )
        self.assertEqual(decision.model_used, DEEP_PLANNER_MODEL)
        self.assertTrue(decision.escalation_applied)
        self.assertEqual(decision.escalation_reason, "op_kind_orchestration")
        self.assertEqual(decision.mode_used, "normal")

    def test_outline_request_escalates_to_qwen_hidden_mode_on_192(self) -> None:
        decision = route_terminal_model(
            _input(
                operation_kind="terminal_outline_request",
                sku_gb=192,
                pack_contains_qwen=True,
                runtime_supports_qwen=True,
            )
        )
        self.assertEqual(decision.model_used, DEEP_PLANNER_MODEL)
        self.assertEqual(decision.mode_used, "hidden_planner_mode")

    def test_escalation_falls_back_to_magistral_when_qwen_unavailable(self) -> None:
        decision = route_terminal_model(
            _input(
                operation_kind="terminal_outline_request",
                sku_gb=128,
                pack_contains_qwen=False,
                runtime_supports_qwen=False,
            )
        )
        self.assertEqual(decision.model_used, TERMINAL_CHAT_MODEL)
        self.assertFalse(decision.escalation_applied)

    def test_prompt_complexity_triggers_escalation(self) -> None:
        decision = route_terminal_model(
            _input(
                operation_kind="terminal_query",
                sku_gb=256,
                pack_contains_qwen=True,
                runtime_supports_qwen=True,
                input_tokens=650,
            )
        )
        self.assertEqual(decision.model_used, DEEP_PLANNER_MODEL)
        self.assertEqual(decision.escalation_reason, "prompt_complexity")

    def test_section_intent_escalation_for_discussion(self) -> None:
        decision = route_terminal_model(
            _input(
                operation_kind="terminal_synthesis_request",
                sku_gb=256,
                pack_contains_qwen=True,
                runtime_supports_qwen=True,
                section_type="discussion",
                user_intent="theory",
            )
        )
        self.assertTrue(decision.escalation_applied)
        self.assertEqual(decision.escalation_reason, "section_discussion_conclusion")

    def test_hidden_planner_mode_swaps_models(self) -> None:
        resident = _ResidentStub()
        output = run_hidden_planner_mode(
            resident_models=resident,
            planner_runner=lambda: {"ok": True},
            load_ctx=4096,
        )
        self.assertEqual(output, {"ok": True})
        self.assertEqual(
            resident.events,
            ["snapshot", "unload", "load:qwen3-next-instruct:4096", "unload", "restore:snap-1"],
        )

    def test_tool_call_validation_retry_then_fallback(self) -> None:
        schemas = {"search": {"query": str}}
        attempts: list[str] = []

        def retry(_strict: str) -> dict[str, object]:
            attempts.append("retry")
            return {"tool_name": "search", "payload": {}}

        def fallback(_strict: str) -> dict[str, object]:
            attempts.append("fallback")
            return {"tool_name": "search", "payload": {"query": "x"}}

        result = validate_or_retry_tool_call(
            raw_output={"tool_name": "search", "payload": {}},
            tool_schemas=schemas,
            retry_once=retry,
            fallback_runner=fallback,
        )
        self.assertTrue(result.valid)
        self.assertTrue(result.used_fallback_model)
        self.assertEqual(result.tool_call.tool_name, "search")  # type: ignore[union-attr]
        self.assertEqual(attempts, ["retry", "fallback"])

    def test_invalid_tool_call_returns_error_card(self) -> None:
        card = build_terminal_error_card("Bad tool schema")
        self.assertEqual(card["type"], "GenericCard")
        self.assertEqual(card["blocks"][0]["type"], "AlertBlock")
        self.assertIn("Bad tool schema", card["blocks"][0]["message"])

    def test_terminal_block_support(self) -> None:
        self.assertTrue(supports_terminal_block("tool_call"))
        self.assertTrue(supports_terminal_block("tool_result"))
        self.assertFalse(supports_terminal_block("random_block"))


def _input(
    *,
    operation_kind: str,
    sku_gb: int,
    pack_contains_qwen: bool,
    runtime_supports_qwen: bool,
    requires_multi_step_tools: bool = False,
    input_tokens: int = 100,
    constraints_count: int = 0,
    section_type: str | None = None,
    user_intent: str | None = None,
) -> TerminalRoutingInput:
    return TerminalRoutingInput(
        operation_kind=operation_kind,  # type: ignore[arg-type]
        sku_gb=sku_gb,
        pack_contains_qwen=pack_contains_qwen,
        runtime_supports_qwen=runtime_supports_qwen,
        requires_multi_step_tools=requires_multi_step_tools,
        input_tokens=input_tokens,
        constraints_count=constraints_count,
        section_type=section_type,
        user_intent=user_intent,
    )


if __name__ == "__main__":
    unittest.main()
