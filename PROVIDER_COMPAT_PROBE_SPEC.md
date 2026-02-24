# Engine Provider Compatibility Probe Spec (OpenAI-Compatible Runtime)

## Purpose

- Probe the configured OpenAI-compatible runtime on first run and on demand.
- Determine capability flags used by engine routing and safety behavior:
  - reachability
  - streaming support
  - tool-calling mode (native vs text fallback)
  - vision/image-input support
  - role-model availability
- Produce a clear operator report for CLI and web admin console.

## Non-Goals

- No quality benchmarking.
- No model downloading/management.
- No network targets beyond configured `provider.base_url`.

## Inputs

- `provider.base_url`
- `provider.api_key` (optional)
- `models.*` role mapping
- active profile mode (`confidential|standard`) + online override state

## Probe Flow

1. Confidential localhost enforcement:
   - If profile mode is confidential, fail fast unless host is `localhost` or `127.0.0.1`.
2. Reachability:
   - `GET {base_url}/models`
   - Require HTTP 200 + parseable JSON.
3. Streaming check:
   - `POST /chat/completions` with `stream=true` and terminal-chat role model.
   - If stream fails, set `streaming=false` and continue.
4. Tool calling check:
   - `POST /chat/completions` with tools payload and required tool choice.
   - Detect structured tool call fields.
   - If absent, set `tool_calling=text_fallback` (or `unsupported` if no safe fallback).
5. Vision check (conditional):
   - Run only if vision role configured or pageindex vision flag expects it.
   - Send minimal image-input request to vision model.
   - If fails, set `vision=false` and disable scanned-PDF vision path.
6. Role presence checks:
   - Compare configured role model IDs against `/models` list.
   - Mark missing roles unavailable and emit closest-match suggestions.

## Capability Report (persisted)

Store non-sensitive report JSON in app/vault state:
- `provider` (`base_url`, optional runtime metadata)
- `streaming` (`true|false`)
- `tool_calling` (`native|text_fallback|unsupported`)
- `vision` (`true|false`)
- `roles_available` (map role -> bool)
- `recommended_actions` (operator guidance)
- `timestamp`

## Operator UX

CLI:
- `exegesis doctor` prints status lines and role warnings.

Web admin console:
- Render same report on settings/config area.
- Include `Re-run probe` action.

## Engine Behavior Hooks

- If `tool_calling != native`:
  - enforce text tool-call protocol + schema validation + retry.
- If `vision == false`:
  - disable `vision_read_pages` and mark scanned PDFs as OCR-required.

## Security

- Confidential mode never permits non-localhost probe targets.
- Never log API keys or raw sensitive payloads in audit/probe output.

## Acceptance Criteria

1. `exegesis doctor` reports capability state and remediation guidance.
2. Admin console can display and re-run provider probe.
3. Engine policy gates and routing consume probe outputs deterministically.
4. Probe failures degrade gracefully (fallbacks), except confidential non-localhost which hard-fails.
