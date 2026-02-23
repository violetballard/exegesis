# Engine Local Web Console Spec (OSS, Barebones, A2UI-First, Admin Config)

## Purpose

- Ship a minimal open-source local web console for `Exegesis Engine`.
- Keep this a reference/admin client, not a replacement for `Exegesis Studio`.
- Render A2UI cards and execute typed actions safely.

## Non-Goals

- No model picker UI.
- No remote hosting by default.
- No advanced editor UX beyond minimal section viewing/edit + patch apply/reject.
- No collaboration features in v1.
- No cloud admin dashboard.

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
- Settings/Config (admin)

## Configuration Ownership and Precedence

Engine-owned config files:
- User config: `~/.config/exegesis/config.toml`
- Optional project override: `<vault>/.exegesis/config.toml`

Effective-value precedence:
1. CLI flags (ephemeral, highest)
2. Project config
3. User config
4. Pack defaults (lowest)

The config UI must display effective values and their source layer.

## Settings/Config Page (Required)

Capabilities:
- Default read-only effective config view
- Explicit edit mode with warning:
  - "Advanced settings can break stability and confidentiality."
- Save-time schema validation with inline field errors
- Security/profile validation:
  - Confidential profile blocks remote endpoints unless user explicitly switches profile and confirms
- Revision history + rollback to recent saved revisions
- Provider compatibility report panel with:
  - current probe results
  - degraded-mode warnings
  - explicit "Re-run probe" action

Recommended safeguards:
- Optional re-auth (vault passphrase or short-lived admin token) before save
- "Restart required" indicator for changes that cannot hot-apply

## Config Domains in v1

Supported edits:
- Model routing overrides:
  - `terminal_chat_model`
  - `planner_default_model`
  - `planner_deep_model`
  - `editor_model`
  - `bulk_best_model`
  - `vision_model`
- Provider endpoints:
  - `openai_compat.base_url`
  - local auth token fields
  - `allow_external_providers` (default false in confidential mode)
- Runtime knobs (bounded):
  - per-model ctx override
  - per-model KV cache settings
  - on-demand unload idle seconds
  - max tokens by operation kind

All edits must pass schema validation and safety rail bounds before apply.

## Studio Access to Admin Console

Studio remains simple and does not expose model picker controls. For power users it may provide:
- "Open Admin Console..."

Token bridge flow:
1. Studio requests one-time admin token from engine:
   - `POST /api/admin/session_token` with purpose `open_console`
2. Studio opens:
   - `http://127.0.0.1:<port>/admin?token=<one_time_token>`
3. Engine exchanges token for short-lived `HttpOnly` session cookie.

Token constraints:
- single-use
- short TTL (recommended 60 seconds)
- scoped to admin/config surface

## Engine API Surface (minimum)

- `POST /api/a2ui/capabilities`
- `GET /api/terminal/stream?session_id=...` (SSE)
- `POST /api/terminal/send`
- `POST /api/actions/execute`
- `POST /api/retrieval/auto`
- `POST /api/retrieval/in_doc`
- `POST /api/admin/session_token`
- `GET /api/config/effective`
- `POST /api/config/validate`
- `POST /api/config/save`
- `GET /api/config/revisions`
- `POST /api/config/revert`
- `GET /api/provider/probe_report`
- `POST /api/provider/probe`
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

## Audit Events (Config + Admin)

Record (hashed metadata only; avoid plaintext secrets/config dumps):
- `config_viewed`
- `config_edit_started`
- `config_saved` (with config hash)
- `config_reverted`
- `profile_changed` (when applicable)
- `provider_probe_run`

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
   - view/edit effective config with validation, revision history, and rollback
3. Same engine `PolicyGate` applies regardless of client (CLI, Web Console, Studio).
4. No remote network dependency is required for baseline web console operation.
5. Studio can open admin console via one-time localhost token flow without adding in-Studio model pickers.
6. Admin config UI exposes provider capability probe results and supports on-demand re-probe.
