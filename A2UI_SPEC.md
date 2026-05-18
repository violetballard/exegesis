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

## Dynamic A2UI Generation Policy

Baseline A2UI is declarative and reviewable. The engine may emit cards, blocks,
and typed actions that the client already knows how to validate and render.

Future dynamic A2UI generation is a privileged build capability, not a universal
runtime behavior:
- Developer builds may enable dynamic generated task surfaces for internal
  workflow and renderer development.
- Initial CoP/beta builds may enable dynamic generated task surfaces for
  trusted workflow discovery when the build profile explicitly allows it.
- Direct-distribution Studio/Pro builds may enable dynamic generated task
  surfaces when the renderer sandbox and promotion rules are implemented.
- Lite/App Store-oriented builds should default to promoted/preapproved A2UI
  components unless Apple App Store policy explicitly permits broader
  agent-generated interface behavior.
- iPad Lite should assume promoted declarative A2UI only until the same behavior
  is Swift-native, gateway-backed, and App Store-compliant.

Dynamic generated task surfaces must be treated as untrusted interface drafts:
- they render through the fixed Exegesis A2UI renderer shipped with the app
- they cannot execute arbitrary Swift, Python, JavaScript, shell, or downloaded
  code
- they cannot access files, network, credentials, project mutation, or OS
  dialogs directly
- every mutation must map to a known, typed, allowlisted Exegesis action
- every policy-sensitive action still requires explicit user confirmation and
  engine-side `PolicyGate` approval

Promotion rules:
- generated surfaces start as temporary/project-local drafts
- useful generated patterns can be reviewed and promoted into a named,
  versioned A2UI component catalog
- promoted components become eligible for stable clients and stricter
  distribution channels
- App Store/iPad builds may ship only the promoted/preapproved catalog unless
  current Apple policy allows dynamic generation for that build profile

MVP dogfooding requirement:
- generated A2UI promotion tracking starts after the Milestone 5 demo path
  stands and before broad import/RAG/coding expansion
- trusted CoP/beta builds may collect generated A2UI draft candidates early so
  promotion decisions come from real workflow use, not only human speculation
- every generated draft is stored as declarative data, not executable code
- every generated draft keeps provenance linking it to the triggering workflow,
  source prompt/context, project mode, client capability set, model/provider,
  allowed action schemas, usage outcome, user feedback, review status, and
  promotion status
- promotion into the named/versioned component catalog requires explicit human
  review

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
