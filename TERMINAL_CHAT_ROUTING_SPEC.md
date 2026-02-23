# Terminal Chat Routing Spec

## Goal

- Terminal is a first-class agent console with tool-capable chat by default.
- Deterministic model routing: Magistral default, Qwen escalation when available.
- No Studio model-selection UI; routing is engine-owned and deterministic.

## Model Roles

- `TerminalChatModel`: `magistral-small` (tools on)
- `DeepPlannerModel`: `qwen3-next-instruct` (planning/orchestration only)
- `EditorModel`: `mistral-small` (editor actions, non-terminal rewrite paths)
- `BulkBestModel`: `gpt-oss-120b` (bulk drafting only)

## Terminal Operation Kinds

- `terminal_chat`
- `terminal_query`
- `terminal_tool_orchestration`
- `terminal_outline_request`
- `terminal_synthesis_request`

Default route is Magistral unless deterministic escalation conditions apply.

## Escalation Rules

Escalate from Magistral to Qwen when Qwen is available and any rule triggers:
- operation kind is orchestration or outline request
- multi-step tools required
- prompt complexity threshold reached (`input_tokens >= 600` or `constraints_count >= 6`)
- section type discussion/conclusion with synthesis/argument-style intents

Qwen availability:
- resident: `sku >= 256` and pack contains Qwen
- ondemand hidden planner mode: `sku in {128,192}` and pack contains Qwen and runtime supports Qwen

If no Qwen availability, stay on Magistral.

## Tool Calling Discipline

- Tool calls must be strict schema-valid JSON payloads.
- Invalid calls retry once with strict instruction.
- If still invalid and Qwen was used, fallback to Magistral.
- If unresolved, emit safe error card for retry.

## Output and Provenance

- Terminal supports inline A2UI cards and tool blocks.
- For each run persist routing provenance:
  - operation_kind
  - model_used
  - escalation_applied + reason
  - mode_used
  - tool_calls_count
  - context references and timing hashes

