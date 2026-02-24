# Milestone Addendum: UI Evolution Loop (A2UI Proposals -> Review -> Promotion)

## Goal

- Make UI grow organically without losing safety, consistency, or auditability.
- Use A2UI primitives as universal fallback and a proposal mechanism to suggest specialized cards.
- Promotion is a human decision (or gated dev mode), never automatic at runtime.

## Non-Goals

- No runtime execution of arbitrary UI code (no model-provided HTML/JS/CSS).
- No runtime creation of new action types.
- No self-modifying UI outside allowlisted A2UI protocol.

## A) Concepts

1. Primitive UI Kit (always supported)
- `MarkdownBlock`, `KeyValueBlock`, `ListBlock`, `TableBlock`, `FormBlock` (JSON-schema-based), `DiffBlock`, `AlertBlock`, `ProgressBlock`, `CodeBlock`
- typed actions: allowlisted IDs only (`apply_patch`, `pin_excerpt`, `create_context_set`, `run_agent`, `export_document`, etc.)

2. `GenericCard` (default composition)
- Engine uses `GenericCard` composed of primitives for new UI needs.
- Studio/Web Console must always render `GenericCard` reliably.

3. `UIPatternProposal` (developer-facing suggestion)
- Structured proposal emitted by engine/model suggesting a specialized card type.
- Rendered as a standard card and never changes runtime behavior unless accepted and implemented in code.

## B) Triggering Proposals

Generate proposals from friction moments:
1. repeated multi-step sequences:
  - same 5-10 action chain repeated 3+ times
2. high-frequency `GenericCard` patterns:
  - recurring layouts with heavy interaction
3. explicit user request:
  - request to make a reusable UI/card for a workflow

## C) Proposal Schema (required fields)

`UIPatternProposal` payload:
- `type: "UIPatternProposal"`
- `proposal_id: uuid`
- `proposed_card_type_id: string` (for example, `ContextSetBuilderCard`)
- `description: string`
- `target_workflow: enum` (`context_building|retrieval|drafting|revision|export|audit|other`)
- `data_schema_json: object` (JSON Schema for payload)
- `example_payload: object`
- `suggested_generic_layout: GenericCard`
- `required_actions: string[]` (subset of allowlisted actions)
- `safety_notes`:
  - `data_exposure_risk: "low"|"medium"|"high"`
  - `mitigations: string[]`
- `metrics_hypothesis`:
  - `expected_step_reduction: int`
  - `expected_time_reduction_seconds: int`
- `status: "proposal"`

Rules:
- `required_actions` MUST be subset of existing allowlist.
- If proposal requires new action ID, it must be rejected or revised to existing actions.

## D) Storage + Backlog (local-first)

1. Proposal storage:
- persist to:
  - `/ui_proposals/<YYYY-MM-DD>/<proposal_id>-<type_id>.json`
- also store in encrypted DB for search/filtering.

2. Metadata:
- `created_at`
- `created_by` (model id + run_id)
- `project_id`
- `linked_friction_event_ids` (optional)

## E) Review + Promotion Workflow (developer mode)

1. Review UI:
- Admin Console/Studio dev mode `UI Proposals` page:
  - list proposals
  - view schema + example + rendered generic layout
  - actions: Accept for implementation / Reject / Request revision

2. Acceptance criteria:
- material step reduction or clarity gain
- uses only existing allowlisted actions
- improves or preserves provenance/auditability
- does not increase sensitive data exposure risk (or includes mitigations)
- consistent across Terminal + Inspector contexts

3. Promotion mechanics:
- Accept creates tracked implementation task:
  - generate stub under `/ui_cards/<type_id>.md` or `/ui_cards/<type_id>.json`
  - add backlog item for renderer + tests
- developers implement specialized support in Studio/Web Console:
  - renderer
  - capabilities list update
  - conformance tests
- until implemented, proposals render as `GenericCard`.

## F) Capability Negotiation (versioned growth)

1. Client advertises:
- `supported_cards`
- `supported_blocks`
- `supported_actions`

2. Engine behavior:
- if specialized card unsupported, fall back to `GenericCard`
- `UnknownCard` fallback must always render safely

## G) Metrics (local-first, privacy-safe)

Local-only metrics for promoted-card value:
- `usage_count` by card type
- avg actions per task (before/after)
- time-to-completion proxies
- rejection rate of proposals/accepted cards

No content metrics and no default telemetry send.

## H) Security Constraints

- No arbitrary UI execution from model output.
- No new runtime actions.
- All actions validated by engine `PolicyGate`.
- Proposals are data-only and local-first; safe to store encrypted.

## I) Acceptance Criteria (Milestone)

1. Engine can emit `UIPatternProposal` cards (dev mode only) with required schema.
2. Studio/Web Console renders proposals safely with schema + example + generic layout.
3. Proposals are saved locally to `/ui_proposals` for later review.
4. Accepting proposal generates implementation artifact (spec stub) without runtime behavior change.
5. Engine falls back to `GenericCard` when specialized cards are unsupported.
6. `UnknownCard` fallback works for unexpected card types.
