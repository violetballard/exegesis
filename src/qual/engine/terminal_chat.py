from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, Protocol

from src.qual.ui.a2ui import GENERIC_CARD_TYPE

TERMINAL_CHAT_MODEL = "magistral-small"
DEEP_PLANNER_MODEL = "qwen3-next-instruct"
EDITOR_MODEL = "mistral-small"
BULK_BEST_MODEL = "gpt-oss-120b"

TerminalOperationKind = Literal[
    "terminal_chat",
    "terminal_query",
    "terminal_tool_orchestration",
    "terminal_outline_request",
    "terminal_synthesis_request",
]
TerminalMode = Literal["normal", "hidden_planner_mode", "none"]
EscalationReason = Literal[
    "none",
    "op_kind_orchestration",
    "op_kind_outline",
    "multi_step_tools",
    "prompt_complexity",
    "section_discussion_conclusion",
]

_ARGUMENT_INTENTS = {"argument", "synthesis", "structure", "theory", "implications"}
_SUPPORTED_TOOL_BLOCK_TYPES = {"tool_call", "tool_result"}


@dataclass(frozen=True)
class TerminalRoutingInput:
    operation_kind: TerminalOperationKind
    sku_gb: int
    pack_contains_qwen: bool
    runtime_supports_qwen: bool
    requires_multi_step_tools: bool
    input_tokens: int
    constraints_count: int
    section_type: str | None = None
    user_intent: str | None = None


@dataclass(frozen=True)
class TerminalRoutingDecision:
    model_used: str
    escalation_applied: bool
    escalation_reason: EscalationReason
    mode_used: TerminalMode
    max_output_tokens: int


@dataclass(frozen=True)
class TerminalRunProvenance:
    operation_kind: TerminalOperationKind
    model_used: str
    escalation_applied: bool
    escalation_reason: EscalationReason
    mode_used: TerminalMode
    tool_calls_count: int
    context_set_ids: tuple[str, ...]
    section_id: str | None
    output_hash: str
    started_at: str
    completed_at: str
    duration_ms: int


@dataclass(frozen=True)
class ToolCallEnvelope:
    tool_name: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ToolValidationResult:
    valid: bool
    tool_call: ToolCallEnvelope | None
    error: str | None
    used_fallback_model: bool = False


class ResidentModelManager(Protocol):
    def snapshot(self) -> str:
        ...

    def unload_all(self) -> None:
        ...

    def load_model(self, model_id: str, *, max_ctx: int | None = None) -> None:
        ...

    def restore(self, snapshot_id: str) -> bool:
        ...


def route_terminal_model(payload: TerminalRoutingInput) -> TerminalRoutingDecision:
    qwen_available_resident = payload.sku_gb >= 256 and payload.pack_contains_qwen
    qwen_available_ondemand = (
        payload.sku_gb in {128, 192} and payload.pack_contains_qwen and payload.runtime_supports_qwen
    )
    should_escalate, reason = _should_escalate(payload)
    if not should_escalate:
        return TerminalRoutingDecision(
            model_used=TERMINAL_CHAT_MODEL,
            escalation_applied=False,
            escalation_reason="none",
            mode_used="none",
            max_output_tokens=800,
        )

    if qwen_available_resident:
        return TerminalRoutingDecision(
            model_used=DEEP_PLANNER_MODEL,
            escalation_applied=True,
            escalation_reason=reason,
            mode_used="normal",
            max_output_tokens=800,
        )
    if qwen_available_ondemand:
        return TerminalRoutingDecision(
            model_used=DEEP_PLANNER_MODEL,
            escalation_applied=True,
            escalation_reason=reason,
            mode_used="hidden_planner_mode",
            max_output_tokens=800,
        )
    return TerminalRoutingDecision(
        model_used=TERMINAL_CHAT_MODEL,
        escalation_applied=False,
        escalation_reason="none",
        mode_used="none",
        max_output_tokens=800,
    )


def run_hidden_planner_mode(
    *,
    resident_models: ResidentModelManager,
    planner_runner: Callable[[], Any],
    load_ctx: int = 8192,
) -> Any:
    snapshot = resident_models.snapshot()
    resident_models.unload_all()
    try:
        resident_models.load_model(DEEP_PLANNER_MODEL, max_ctx=load_ctx)
        return planner_runner()
    finally:
        resident_models.unload_all()
        resident_models.restore(snapshot)


def validate_or_retry_tool_call(
    *,
    raw_output: dict[str, Any],
    tool_schemas: dict[str, dict[str, type]],
    retry_once: Callable[[str], dict[str, Any]] | None = None,
    fallback_runner: Callable[[str], dict[str, Any]] | None = None,
) -> ToolValidationResult:
    valid, envelope, error = _validate_tool_call(raw_output, tool_schemas)
    if valid:
        return ToolValidationResult(valid=True, tool_call=envelope, error=None)

    strict = "Output must be a single valid tool call JSON. No prose."
    if retry_once is not None:
        retry_payload = retry_once(strict)
        valid, envelope, error = _validate_tool_call(retry_payload, tool_schemas)
        if valid:
            return ToolValidationResult(valid=True, tool_call=envelope, error=None)

    if fallback_runner is not None:
        fallback_payload = fallback_runner(strict)
        valid, envelope, error = _validate_tool_call(fallback_payload, tool_schemas)
        if valid:
            return ToolValidationResult(valid=True, tool_call=envelope, error=None, used_fallback_model=True)

    return ToolValidationResult(valid=False, tool_call=None, error=error)


def build_terminal_error_card(message: str) -> dict[str, Any]:
    return {
        "type": GENERIC_CARD_TYPE,
        "title": "Tool call error",
        "blocks": [
            {
                "type": "AlertBlock",
                "severity": "error",
                "title": "Tool call validation failed",
                "message": message,
            }
        ],
        "actions": [{"id": "run_agent", "label": "Retry", "payload": {"operation": "terminal_chat"}}],
    }


def supports_terminal_block(block_type: str) -> bool:
    return block_type in _SUPPORTED_TOOL_BLOCK_TYPES


def _should_escalate(payload: TerminalRoutingInput) -> tuple[bool, EscalationReason]:
    if payload.operation_kind == "terminal_tool_orchestration":
        return True, "op_kind_orchestration"
    if payload.operation_kind == "terminal_outline_request":
        return True, "op_kind_outline"
    if payload.requires_multi_step_tools:
        return True, "multi_step_tools"
    if payload.input_tokens >= 600 or payload.constraints_count >= 6:
        return True, "prompt_complexity"
    if (
        payload.section_type in {"discussion", "conclusion"}
        and (payload.user_intent or "").strip().lower() in _ARGUMENT_INTENTS
    ):
        return True, "section_discussion_conclusion"
    return False, "none"


def _validate_tool_call(
    raw_output: dict[str, Any],
    tool_schemas: dict[str, dict[str, type]],
) -> tuple[bool, ToolCallEnvelope | None, str | None]:
    if not isinstance(raw_output, dict):
        return False, None, "tool call output must be an object"
    tool_name = raw_output.get("tool_name")
    payload = raw_output.get("payload")
    if not isinstance(tool_name, str) or not tool_name:
        return False, None, "tool_name is required"
    if not isinstance(payload, dict):
        return False, None, "payload must be an object"
    schema = tool_schemas.get(tool_name)
    if schema is None:
        return False, None, f"unknown tool: {tool_name}"
    for key, field_type in schema.items():
        if key not in payload:
            return False, None, f"missing payload field: {key}"
        if not isinstance(payload[key], field_type):
            return False, None, f"invalid payload field type: {key}"
    return True, ToolCallEnvelope(tool_name=tool_name, payload=payload), None
