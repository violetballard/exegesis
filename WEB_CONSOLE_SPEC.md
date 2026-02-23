# Engine Local Web Console Spec (OSS, Barebones, A2UI-First)

## Purpose

- Ship a minimal open-source local web console for `Exegesis Engine`.
- Keep this a reference/admin client, not a replacement for `Exegesis Studio`.
- Render A2UI cards and execute typed actions safely.

## Non-Goals

- No model picker UI.
- No remote hosting by default.
- No advanced editor UX beyond minimal section viewing/edit + patch apply/reject.
- No collaboration features in v1.

## Localhost, Auth, and Session

- Bind to `127.0.0.1` only.
- Default port should be OS-selected ephemeral or random local port.
- Remote binding (`0.0.0.0`) is unsupported in v1.
- Require session token auth:
  - one-time token/link printed in terminal, or
  - local passcode page with passcode shown in terminal.
- Token must be short-lived and stored in `HttpOnly` cookie.

## Security Requirements

- Strict CSP (`self` only; no remote scripts/styles).
- No agent-provided HTML/CSS/JS execution.
- CSRF protection on mutating routes.
- No plaintext prompt/response persistence in browser localStorage by default.
- Session expiry + logout cookie clear.
- Engine `PolicyGate` remains authoritative for all actions.

## A2UI Requirements

- Client sends `A2UI_CAPABILITIES` on session attach.
- Must render `GenericCard` primitives:
  - `MarkdownBlock`
  - `KeyValueBlock`
  - `ListBlock`
  - `TableBlock`
  - `AlertBlock`
  - `ProgressBlock`
  - `CodeBlock`
- Must support typed action allowlist execution through engine validation.
- Must support `UnknownCard` fallback with collapsed raw JSON and safe copy action.

## Transport and Runtime

- Keep stack lightweight (no SPA framework required).
- Preferred:
  - server-rendered pages for navigation
  - HTMX-style partial updates
  - SSE for transcript/card/progress streaming
- Optional later: WebSocket.

## MVP Pages

- Vault
- Corpus
- Context Sets
- Terminal
- Drafts
- Export
- Audit (read-only)

## Engine API Surface (minimum)

- `POST /api/a2ui/capabilities`
- `GET /api/terminal/stream?session_id=...` (SSE)
- `POST /api/terminal/send`
- `POST /api/actions/execute`
- `POST /api/retrieval/auto`
- `POST /api/retrieval/in_doc`
- Minimal vault/corpus/context/draft/export/audit endpoints

`/api/actions/execute` must enforce:
- action ID allowlist
- payload schema validation
- `PolicyGate` checks

## Terminal Stream Events (SSE)

- `message.delta`
- `card`
- `tool.call`
- `tool.result`
- `progress`
- `done`

## Packaging

- Ship web assets with engine repo/runtime (`/webconsole` or embedded assets).
- No separate install required for v1.
- Web Console remains OSS/community client; Studio remains flagship workstation client.

## Acceptance Criteria

1. `exegesis serve` launches API + web console + stream endpoints on localhost with token auth.
2. Web console can:
   - open vault
   - import/search corpus
   - create context sets and pin excerpts
   - run terminal chat and render A2UI cards
   - apply/reject draft patches
   - preview/export with explicit confirmation in confidential mode
   - view audit events
3. Same engine `PolicyGate` applies regardless of client (CLI, Web Console, Studio).
4. No remote network dependency is required for baseline web console operation.
