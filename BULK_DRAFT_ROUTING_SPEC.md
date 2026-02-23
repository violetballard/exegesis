# Dual Bulk Draft Routing Spec (No UI Choice)

This document captures the enforced routing and execution policy for bulk drafting.

## Goal

- Deterministic dual bulk drafting routing in Exegesis Engine.
- Users never choose models in UI.
- Routing is automatic from:
  - installed pack capability (memory-tier gate)
  - section type
  - target word count thresholds

## Model Roles

- Planner: Magistral Small
- Editor: Mistral Small
- Bulk Fast: Magistral Small
- Bulk Best: gpt-oss-120b

## Invariants

- Bulk drafting requires planner outline (`outline_id` required).
- Editor pass always runs after bulk drafting.
- Best model is never used for chat/quick edits/tool planning.

## Section Types

- `introduction|literature_review|methods|findings|discussion|conclusion|other`

## Best Allowlist

Best model may be used only for:
- `draft_from_outline`
- `expand_outline`
- `rewrite_section_from_outline`
- `synthesis_lookup_from_outline` (optional)

All other operations force `fast`.

## Capability Gate

`supports_best_bulk := pack.contains_model("gpt-oss-120b") AND pack.memory_tier_gb >= 256`

If false, routing always selects `fast`.

## Routing Inputs

- `section_type`
- `target_word_count`
- `supports_best_bulk`
- `operation_kind`

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

## Deterministic Rules (ordered)

1. If `supports_best_bulk == false` -> `fast/unsupported`
2. If `operation_kind` not allowlisted -> `fast/op_not_allowed`
3. `discussion` -> `best/section_type_discussion`
4. `conclusion` -> `best/section_type_conclusion`
5. Thresholds:
   - `methods|findings` and `target_word_count >= 2500` -> `best/word_count_threshold_methods_findings`
   - all other section types and `target_word_count >= 1500` -> `best/word_count_threshold_general`
   - otherwise -> `fast/default_fast`

## Execution Pipeline

Inputs:
- `outline_id`
- `section_id`
- `context_set_id(s)`

Steps:
1. Require `outline_id`; deny bulk drafting if missing.
2. Route to `fast|best` via deterministic function.
3. Run bulk drafting with selected tier model.
4. Always run editor pass.
5. Produce patch proposal + evidence refs + open questions.
6. Persist AgentRun metadata/provenance.

## AgentRun Fields

Persist at minimum:
- `bulk_draft_tier`
- `bulk_draft_reason`
- `planner_outline_id`
- `target_word_count`
- `section_type`
- `operation_kind`
- `model_id_bulk`
- `model_id_editor`
- `context_set_ids`
- `output_hash`, `patch_hash`, timestamps, duration

## UI/Client Rules

- Studio has no model-selection controls.
- Optional transparency label only: `Bulk draft: Fast/Best (auto)`.
- CLI may alter pack installation/config, but routing remains deterministic for given inputs.

## Implementation

- Policy module: `src/qual/engine/bulk_draft.py`
- Tests: `tests/unit/test_bulk_draft_routing.py`
