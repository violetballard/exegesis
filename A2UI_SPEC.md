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
- Local Web Console renderer (localhost-only reference client)
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
- `UIPatternProposal` (dev mode suggestion card only)

Engine emits specialized cards only when client support is declared; otherwise it emits `GenericCard`.
`UIPatternProposal` never changes runtime behavior by itself; it is review/backlog input only.

## Primitive Blocks

Required safe blocks:
- `MarkdownBlock`
- `KeyValueBlock`
- `ListBlock`
- `TableBlock`
- `FormBlock` (JSON-schema-based)
- `DiffBlock`
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

Web Console follows the same action model:
- client-side action/payload validation
- engine-side allowlist and schema re-validation
- engine-authoritative policy enforcement

`UIPatternProposal` rules:
- must declare `required_actions` as a strict subset of allowlisted action IDs
- proposals requiring new runtime action IDs must be rejected or revised
- proposals are data-only and must not include executable UI code

## Security Invariants

- No arbitrary HTML/CSS/JS from agent payloads
- No unknown runtime action execution
- No engine-driven OS dialogs
- Policy-sensitive actions require explicit user confirmation and `PolicyGate` approval
- No runtime creation of new action types
- No automatic runtime promotion of proposed cards

## Streaming Contract

A2UI-compatible streaming clients should support event-driven updates for:
- message deltas
- cards
- tool call/result blocks
- progress
- completion (`done`)

SSE is the baseline transport for the local web console.
