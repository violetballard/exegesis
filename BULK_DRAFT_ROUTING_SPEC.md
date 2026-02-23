# Dual Bulk Draft Routing Spec

This document captures the enforced routing and execution policy for bulk drafting.

## Goals

- Deterministic dual bulk drafting routing with no UI choice.
- Allow `best` bulk drafting on 128GB+ when installed and runtime-supported, even if non-resident.
- Engine manages residency/mode switching automatically.

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

## Capability Gates

Compute from behavior tier + installed pack metadata + runtime support.
Behavior tier is auto-mapped from unified memory:

- `<32` => unsupported (minimum supported memory is 32GB unified)
- `32..47` => `32`
- `48..95` => `64`
- `96..191` => `128`
- `192..255` => `128` (extra headroom profile; no new SKU)
- `256..511` => `256`
- `>=512` => `512`

Pack selection:
- prefer exact `pack_memory_tier_gb == behavior_tier_gb`
- if missing, choose next-lower pack only (`512 -> 256 -> 128 -> 64 -> 32`)
- never auto-select a higher tier

Capability gates:

- `supports_best_bulk := pack.contains_model("gpt-oss-120b") AND runtime.supports_model("gpt-oss-120b")`
- `supports_best_bulk_resident := supports_best_bulk AND behavior_tier_gb >= 256`
- `supports_best_bulk_ondemand := supports_best_bulk AND behavior_tier_gb >= 128`

If `supports_best_bulk` is false, best is never selected.
If `supports_best_bulk` is true but `supports_best_bulk_ondemand` is false, route as unsupported.

## Routing Inputs

- `section_type`
- `target_word_count`
- `operation_kind`
- `supports_best_bulk`
- `supports_best_bulk_resident`
- `supports_best_bulk_ondemand`

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

## Deterministic Rules (ordered)

1. If `supports_best_bulk == false` or `supports_best_bulk_ondemand == false` -> `fast/unsupported/normal`
2. If `operation_kind` not allowlisted -> `fast/op_not_allowed/normal`
3. `discussion` -> `best/section_type_discussion`
4. `conclusion` -> `best/section_type_conclusion`
5. Thresholds:
   - `methods|findings` and `target_word_count >= 2500` -> `best/word_count_threshold_methods_findings`
   - all other section types and `target_word_count >= 1500` -> `best/word_count_threshold_general`
   - otherwise -> `fast/default_fast`

Mode selection:
- `fast` -> `normal`
- `best` with resident support -> `normal`
- `best` without resident support -> `drafting_mode`

## Drafting Mode Lifecycle

When `bulk_draft_mode == drafting_mode`:
1. Snapshot resident models.
2. Unload all resident models.
3. Load `gpt-oss-120b` as sole resident model.
4. Run best bulk drafting with strict context limits.
5. Unload `gpt-oss-120b`.
6. Restore resident snapshot.
7. Run editor pass.

Context policy defaults:
- default load ctx: 12k
- hard max ctx: 16k

## Execution Pipeline

Inputs:
- `outline_id`
- `section_id`
- `context_set_id(s)`

Steps:
1. Require `outline_id`; deny bulk drafting if missing.
2. Route to tier/reason/mode.
3. Run bulk drafting (`fast` or `best`).
4. Always run editor pass.
5. Produce patch proposal + evidence refs + open questions.
6. Persist AgentRun metadata/provenance.

## AgentRun Fields

Persist at minimum:
- `bulk_draft_tier`
- `bulk_draft_reason`
- `bulk_draft_mode`
- `planner_outline_id`
- `target_word_count`
- `section_type`
- `operation_kind`
- `model_id_bulk`
- `model_id_editor`
- `context_set_ids`
- output/provenance hashes and timing fields
- optional restore/debug fields (`restore_success`, snapshot reference)

## UI/Client Rules

- Studio has no model-selection controls.
- Optional transparency label only: `Bulk drafting: auto (Fast/Best)` and/or `Drafting Mode: engaged`.
- CLI may alter pack installation/config, but routing remains deterministic for given inputs.

## Implementation

- Policy module: `src/qual/engine/bulk_draft.py`
- Tests: `tests/unit/test_bulk_draft_routing.py`
