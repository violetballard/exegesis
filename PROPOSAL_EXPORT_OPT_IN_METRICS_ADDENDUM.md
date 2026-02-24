# Milestone Addendum: Optional Proposal Export + Opt-in Metrics

## Goal

- Allow users to optionally export `UIPatternProposals` with local usage metrics to prioritize card implementation.
- Metrics collection is opt-in at install/first-run with clear disclosure.
- Metrics must be non-confidential by construction: no prompts, no document text, no filenames/paths, no excerpts, no citation content.

## Non-Goals

- No background telemetry uploads by default.
- No content collection, even anonymized.
- No personal identifiers beyond an optional random install ID.

## A) Install / First-run Consent UX (Studio)

1. Choice on install/first-run:
- Toggle: Share anonymous usage metrics to improve Exegesis.
  - Default OFF
- Secondary toggle: Include UI proposal exports when I choose to send them.
  - Default OFF

2. Disclosure must explicitly state:
- Shared:
  - card type IDs
  - action counts and acceptance/rejection rates
  - timing metrics (durations only)
  - capability flags (for example, vision available)
  - performance buckets
- Not shared:
  - text from documents, prompts, chat, excerpts, notes
  - filenames, file paths, URLs, citekeys, bibliography entries
  - user identity, email, institution, precise location
  - vault IDs or project names
- UI statement:
  - You can preview exactly what will be exported before sending.

3. Consent storage:
- Stored locally (Keychain or local settings file).
- Editable anytime in Settings:
  - Metrics: On/Off
  - Proposal exports: On/Off

## B) Metrics Collection (Local-Only First)

1. Metrics are stored locally in encrypted state.
2. If consent is OFF:
- Metrics may exist as ephemeral in-memory counters for UX only (optional), and MUST NOT be persisted.
3. If consent is ON:
- Persist only allowlisted metrics fields.
- Never persist raw prompts/model outputs for telemetry.

## C) Allowlisted Metrics Schema (strict)

`MetricsEvent` (local/exportable):
- `event_type` enum:
  - `card_rendered`
  - `card_action_clicked`
  - `card_dismissed`
  - `card_accepted` | `card_rejected`
  - `proposal_created`
  - `proposal_viewed`
  - `proposal_exported`
- `timestamp_bucket` (date or hour bucket)
- `card_type_id`
- `workflow` enum (`context_building|retrieval|drafting|revision|export|audit|other`)
- `action_id?` (allowlisted only; no payload)
- `success?`
- `duration_ms_bucket` enum (`<250`, `250-1000`, `1-5s`, `5-20s`, `>20s`)
- `run_mode` enum (`confidential|online`)
- `provider_used` enum (`local_openai|openai_cloud|anthropic|none`)
- `model_role` enum (`terminal_chat|planner_deep|bulk_best|editor|vision`)
- `capability_flags`:
  - `vision_enabled`
  - `tool_calling_native`
  - `streaming`
- `app_version`
- `os_version_major`
- `hardware_bucket` enum (`<=32GB`, `48-64GB`, `96-128GB`, `192-256GB`, `512GB+`)
- `install_id` random UUID (optional)

Hard bans:
- prompt/excerpt text, document titles, filenames, paths, citekeys, URLs, user identifiers

## D) Aggregation (preferred)

Prefer local aggregates over raw events for export:

`AggregatedCardMetrics`:
- `card_type_id`
- `times_rendered`
- `times_interacted`
- `action_counts_by_action_id`
- accept/reject counts
- `median_duration_bucket`
- `failure_rate`
- workflow breakdown counts

## E) Proposal Export Bundle (user-triggered)

1. Explicit export only (never background):
- UI action: Export UI Proposals & Metrics...
- Scope:
  - Selected proposal(s)
  - All proposals
  - Metrics summary only

2. Required preview:
- show exact export fields
- include View raw JSON

3. Export format:
- `.zip` with:
  - `proposals/<proposal_id>.json` (`UIPatternProposal`)
  - `metrics/aggregates.json` (`AggregatedCardMetrics`)
  - `env/info.json` (`app_version`, `hardware_bucket`, `capability_flags`)
  - `signature.json` (optional integrity hash)

4. Destination and audit:
- user chooses file path
- default suggestion: Desktop/Downloads
- record audit event `proposal_bundle_exported` (no paths stored)

5. Submission:
- default manual sharing by user
- optional later Send to Ballard flow only with online mode + explicit confirmation

## F) Dev Mode Interaction

- Dev Mode may enable:
  - proposal generation triggers
  - export proposal bundle UI
  - extra diagnostics
- Dev Mode must still obey consent:
  - if metrics OFF, no persisted/exported metrics unless user explicitly exports proposal-only bundle

## G) UI Evolution Prioritization

Use exports for prioritization when:
- `GenericCard` is frequent + highly interacted
- patch acceptance patterns repeat
- workflows have high step count/latency
- proposal schemas recur across users

## H) Acceptance Criteria

1. Install/first-run shows opt-in toggles (default OFF) with explicit disclosure.
2. With consent OFF: no persisted telemetry; exports include only user-selected proposals.
3. With consent ON: only allowlisted fields are stored/exported; preview shows exact payload.
4. Users can export `.zip` bundle with proposals + aggregated metrics and inspect raw JSON.
5. Validator prevents confidential content from entering metrics schema.
6. Export audit event recorded without storing paths or payload content.
