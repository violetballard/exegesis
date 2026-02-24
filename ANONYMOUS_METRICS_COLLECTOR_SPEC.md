# Anonymous Metrics Collector Spec

## Goal

- Allow users (opt-in) to send anonymous, non-content usage metrics over the network at any time.
- Support send-on-quit prompt and send-now from Settings.
- Preserve Exegesis confidentiality posture by construction: telemetry contains no research content, ever.

## Non-Goals

- No collection of prompts, excerpts, document text, filenames, paths, citekeys, URLs, or user identity.
- No background sending unless the user explicitly opts in.
- No advertising identifiers, cross-app tracking, or third-party analytics SDKs.

## A) Product Rules

1. Opt-in only
- Default metrics setting: OFF.
- Default send-on-quit: OFF.
- User can enable metrics in Settings; disclosure must state what is shared and what is not.

2. Non-content by schema enforcement
- Telemetry payload schema is strictly allowlisted.
- Engine/Studio validates payload against schema before sending.
- Server re-validates and rejects nonconforming payloads.

3. Allowed in both Confidential and Online projects (if user opts in)
- Telemetry is permitted even in Confidential projects because it is non-content.
- UI must state: this contains no vault content.
- If an institution forbids telemetry, user can keep it off.

## B) Client Behavior (Studio and/or Engine)

1. Collection
- Metrics are stored locally in encrypted state when enabled.
- Store aggregated metrics by default (not raw events).

2. Sending triggers
- Manual: Settings -> Send anonymous metrics now.
- On quit (if enabled): show prompt with checkbox Send anonymous metrics now.
- Scheduled (optional): daily/weekly only if automatic sending is enabled (default OFF).

3. Transport
- HTTPS `POST` to telemetry endpoint.
- Retry policy: exponential backoff, max 3 attempts per send batch.
- Queue unsent batches locally; retention capped (for example, last 30 days).

## C) Payload Schema (Aggregates Only)

`TelemetryEnvelope`:
- `schema_version: int` (start 1)
- `app: "exegesis-studio" | "exegesis-engine"`
- `app_version: string`
- `platform: "macos"`
- `os_version_major: string` (for example, `macOS 15`)
- `hardware_bucket: enum` (`<=32GB`, `48-64GB`, `96-128GB`, `192-256GB`, `512GB+`)
- `profile_mode_counts`:
  - `confidential_runs: int`
  - `online_runs: int`
- `capability_flags`:
  - `streaming: bool`
  - `tool_calling_native: bool`
  - `vision_available: bool`
- `install_id: uuid` (random, generated locally)
- `project_count_bucket: enum` (`0`, `1`, `2-5`, `6-20`, `20+`) (optional)
- `metrics_aggregate: AggregatedCardMetrics[]`
- `proposals_included: bool`
- `timestamp_bucket: date` (`YYYY-MM-DD`)

`AggregatedCardMetrics`:
- `card_type_id: string`
- `workflow: enum` (`context_building|retrieval|drafting|revision|export|audit|other`)
- `rendered_count: int`
- `interacted_count: int`
- `action_counts_by_id: map(action_id -> count)` where `action_id` must be allowlisted
- `accept_count: int?` (patch-like cards)
- `reject_count: int?`
- `duration_bucket_counts: map(bucket -> count)` where bucket in `<250ms`, `250ms-1s`, `1s-5s`, `5s-20s`, `>20s`

Optional: `ProposalBundleSummary` (no proposal content by default)
- `proposal_count: int`
- `proposed_card_type_ids: [string]`

Note:
- Full proposal bundles are user-exported separately unless explicitly enabled.

Hard bans (server rejects if present):
- any free-form text fields other than IDs/enums
- prompts, excerpts, filenames, paths, URLs, citekeys, provider messages
- IP storage beyond transient logs

## D) Telemetry Server (Ballard Education LLC)

1. Endpoints
- `POST /v1/telemetry/ingest`
  - body: `TelemetryEnvelope` (JSON)
  - auth: none or optional lightweight key
- `POST /v1/telemetry/proposals` (optional, separate)
  - only if user explicitly enables proposal sending; otherwise proposals are manual export only

2. Security
- HTTPS only
- Rate limiting by `install_id` and/or IP (no permanent IP storage)
- Validate JSON schema and reject unknown fields
- Store only validated aggregates

3. Storage
- Postgres (recommended) or SQLite for MVP
- tables:
  - `telemetry_envelopes` (`install_id`, `date_bucket`, `app_version`, `hardware_bucket`, flags)
  - `telemetry_card_metrics` (`install_id`, `date_bucket`, `card_type_id`, `workflow`, counts)
  - optional `telemetry_proposal_summaries`

Retention:
- raw envelopes: 90 days
- aggregated rollups: longer (for example, 2 years)

Optional trust endpoint:
- `POST /v1/telemetry/delete { install_id }`

4. Transparency
- Publish telemetry schema and examples publicly.
- Document retention policy and what is not collected.

## E) UX Copy Requirements

Settings text:
- Anonymous metrics never include your documents, excerpts, prompts, filenames, paths, citations, or personal identity.
- You can preview exactly what will be sent.

Quit prompt:
- checkbox Send anonymous metrics now (unchecked by default)

## F) Acceptance Criteria

1. Metrics are OFF by default.
2. When ON, client sends only schema-valid aggregate payloads.
3. Server rejects payloads with disallowed fields.
4. User can preview payload before sending.
5. Send-on-quit works and never sends unless checkbox is checked.
6. Telemetry sending does not require Online project mode; it is independent and opt-in.
