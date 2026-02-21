# Dual Bulk Draft Routing Spec

This document captures the enforced routing and execution policy for bulk drafting.

## Goals

- Deterministic routing between `fast` and `best` bulk drafting tiers.
- No UI model choice for bulk drafting.
- Allow `best` bulk drafting on 128GB machines in non-resident Drafting Mode.
- Keep role-based automatic routing as the default execution model.
- Allow power-user role overrides only through localhost-gated OpenAI-compatible endpoints.

## Model Roles

- Planner: Magistral Small
- Editor: Mistral Small
- Bulk Fast: Magistral Small
- Bulk Best: gpt-oss-120b

## Role Override Policy (Power User)

Default:
- Engine selects models automatically using deterministic policy.
- UI does not expose direct model picker controls.

Power-user overrides:
- Overrides are role-scoped (`planner`, `editor`, `bulk_fast`, `bulk_best`) and optional.
- Overrides must not bypass routing invariants (allowlist, outline requirement, editor-always pass).
- `bulk_best` remains restricted to allowed operation kinds even when overridden.

Endpoint constraints (required):
- Override providers must use OpenAI-compatible API shape.
- Endpoint host must resolve to localhost only:
  - `127.0.0.1`
  - `::1`
  - `localhost`
- Non-local endpoints are rejected by policy.
- URL scheme must be `http` or `https`.

## Invariants

- Bulk drafting requires a planner outline (`outline_id` required).
- Editor pass always runs after bulk drafting.
- gpt-oss-120b is restricted to best-allowlisted bulk operations.

## Routing Inputs

- `section_type`: `introduction|literature_review|methods|findings|discussion|conclusion|other`
- `target_word_count`: integer
- `operation_kind`: operation enum
- `supports_best_bulk`: bool
- `supports_best_bulk_resident`: bool
- `supports_best_bulk_ondemand`: bool

## Routing Outputs

- `bulk_draft_tier`: `fast|best`
- `bulk_draft_reason`:
  - `unsupported`
  - `op_not_allowed`
  - `section_type_discussion`
  - `section_type_conclusion`
  - `word_count_threshold_general`
  - `word_count_threshold_methods_findings`
  - `default_fast`
- `bulk_draft_mode`: `normal|drafting_mode`

## Capability Gates

- `supports_best_bulk`:
  - installed pack contains `gpt-oss-120b`
  - runtime supports `gpt-oss-120b`
- `supports_best_bulk_resident`:
  - `supports_best_bulk` and memory tier >= 256GB
- `supports_best_bulk_ondemand`:
  - `supports_best_bulk` and memory tier >= 128GB

## Deterministic Rules

1. If best unsupported or on-demand unsupported -> `fast`, `unsupported`, `normal`.
2. If operation not in best allowlist -> `fast`, `op_not_allowed`, `normal`.
3. `discussion` -> `best`, `section_type_discussion`.
4. `conclusion` -> `best`, `section_type_conclusion`.
5. Threshold rules:
   - `methods|findings`: >=2500 => `best`, else `fast`.
   - all other section types: >=1500 => `best`, else `fast`.
6. Mode rules for best:
   - resident supported => `normal`
   - else => `drafting_mode`

## Drafting Mode Lifecycle

When mode is `drafting_mode`:

1. Snapshot resident models.
2. Unload all resident models.
3. Load `gpt-oss-120b` as sole resident model.
4. Run best bulk drafting with strict context limits.
5. Unload `gpt-oss-120b`.
6. Restore resident snapshot.
7. Run editor pass.

Context policy defaults:
- default best ctx for drafting mode load: 12k
- hard max ctx for drafting mode execution: 16k

## Persistence Fields

Store these for each bulk draft run:

- `bulk_draft_tier`, `bulk_draft_reason`, `bulk_draft_mode`
- `planner_outline_id`, `section_type`, `target_word_count`, `operation_kind`
- `model_id_bulk`, `model_id_editor`
- `context_set_ids`
- output/provenance metadata and timing fields
- optional override provenance:
  - `model_id_planner_effective`
  - `model_id_editor_effective`
  - `model_id_bulk_effective`
  - `role_override_source` (`default|user_override`)
  - `endpoint_profile_id` (if override used)

## Validation Requirements

- Invalid override endpoint host => override ignored and run marked with validation warning.
- Invalid model id for a role => override ignored and fallback to default role model.
- Best role override must still satisfy capability gates (`supports_best_bulk*`).

## Implementation

- Routing + execution policy: `src/qual/engine/bulk_draft.py`
- Core tests: `tests/unit/test_bulk_draft_routing.py`
