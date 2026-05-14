# A2UI Composable UI Spec

This document defines the baseline A2UI contract used by Exegesis Engine and future Studio clients.

## Handshake

Client sends `A2UI_CAPABILITIES` at session start:
- `a2ui_version`
- `client_name`
- `cards_supported`
- `primitive_blocks_supported`
- `actions_supported`
- `max_payload_bytes`
- `supports_streaming`

Engine stores capabilities per session and adapts output to supported cards/blocks/actions.

Reference clients:
- CLI text fallback renderer
- Future `Exegesis Console` renderer
- Future Exegesis Studio renderer

## Card Model

Required default:
- `GenericCard` with:
  - `title`
  - `subtitle?`
  - `blocks[]`
  - `actions[]?`
  - `debug?`

Optional specialized cards:
- `ProposedEditCard`
- `EvidenceCard`
- `QuestionsCard`
- `RunLogCard`

Engine emits specialized cards only when client support is declared; otherwise it emits `GenericCard`.

## Primitive Blocks

Required safe blocks:
- `MarkdownBlock`
- `KeyValueBlock`
- `ListBlock`
- `TableBlock`
- `AlertBlock`
- `ProgressBlock`
- `CodeBlock`

No arbitrary HTML/CSS/JS execution is permitted in block payloads.

## Unknown Card Fallback

If a client receives an unsupported card type, render:
- `UnknownCard`
- title `"Unsupported card type: <type>"`
- read-only raw JSON viewer (`CodeBlock`)
- discoverable nested primitive blocks when available
- safe `copy_to_clipboard` action for payload JSON

## Action Model

All actions are typed and allowlisted:
- `apply_patch`
- `reject_patch`
- `open_section`
- `open_corpus_item`
- `pin_to_context_set`
- `create_context_set`
- `run_agent`
- `refresh_license`
- `export_document`
- `copy_to_clipboard`

Each action includes:
- `id`
- `label`
- `payload`
- optional `confirm`
- optional `policy_sensitive`

Studio validates actions and payloads client-side. Engine re-validates and enforces `PolicyGate`.

Any future console client follows the same action model:
- client-side action/payload validation
- engine-side allowlist and schema re-validation
- engine-authoritative policy enforcement

## Security Invariants

- No arbitrary HTML/CSS/JS from agent payloads
- No unknown runtime action execution
- No engine-driven OS dialogs
- Policy-sensitive actions require explicit user confirmation and `PolicyGate` approval

## Streaming Contract

A2UI-compatible streaming clients should support event-driven updates for:
- message deltas
- cards
- tool call/result blocks
- progress
- completion (`done`)

Streaming transport is client-specific. CLI remains the current baseline consumer.
