# Notebook Context Compaction MVP Spec

This document defines the MVP notebook context-compaction behavior for Exegesis.

Context compaction is part of the MVP dogfooding path, not a post-MVP feature. It exists so long writing sessions can continue without losing useful context or overflowing the active model window.

This spec is implementable scaffolding only until the relevant active lanes pick it up. It does not activate Textual UI work by itself.

## Research Basis

The MVP design is based on five practical findings from current context-management work:

- Long-context models still show position sensitivity. `Lost in the Middle` finds that models often use information best when it appears near the beginning or end of the input and worse when relevant material is buried in the middle.
- Prompt-compression papers such as `LLMLingua` and `LongLLMLingua` show that aggressively reducing prompt tokens can preserve useful information, but those methods add extra model/tool complexity and are better treated as optional later compressors.
- `Selective Context` shows that pruning low-information or redundant context can reduce memory and latency while keeping quality close to full-context baselines.
- `MemGPT` frames the core product problem well: the model needs a managed hierarchy of fast active context and slower archived memory rather than a single ever-growing transcript.
- `ReSum` supports the MVP pattern of periodically condensing interaction history into compact summaries for long-running agent work, without requiring model architecture changes.

MVP decision:
- Use structured rolling summaries, protected verbatim pins, and retrieval backfill as the default.
- Do not depend on LLMLingua-style token classifiers, latent compression, or training-time model changes for MVP.
- Keep all raw notebook history immutable and recoverable; compaction changes model context assembly, not the source transcript.

References:
- `Lost in the Middle`: https://arxiv.org/abs/2307.03172
- `LLMLingua`: https://arxiv.org/abs/2310.05736
- `LongLLMLingua`: https://arxiv.org/abs/2310.06839
- `Selective Context`: https://arxiv.org/abs/2310.06201
- `MemGPT`: https://arxiv.org/abs/2310.08560
- `ReSum`: https://arxiv.org/abs/2509.13313

## Goals

- Keep notebook chat, draft, rewrite, and later search/retrieval sessions usable across long writing sessions.
- Preserve user trust by keeping the full raw transcript available for inspection and export.
- Keep important writing decisions, pinned context, unresolved tasks, citation keys, and basket provenance visible to the model.
- Reduce prompt size before model requests exceed the configured budget.
- Make compaction status explicit in the notebook UI and exportable in transcripts.
- Support local/confidential operation without requiring cloud compaction.

## Non-Goals

- No latent-vector context compression for MVP.
- No hidden deletion of raw notebook messages.
- No irreversible transcript rewriting.
- No automatic cloud compaction in confidential/local-only projects.
- No claim that a compacted context is equivalent to full raw history.
- No summary synthesis of project documents unless those documents were explicitly part of notebook history, active document context, basket context, or retrieval backfill.

## Core Concepts

### Notebook Entry

Every user action or assistant result in the notebook history is a structured entry:

- `entry_id`
- `chat_id`
- `role`: user, assistant, system_status, search_card, rewrite_card, draft_event, compaction_event
- `mode`: chat, draft, rewrite, search, summary, system
- `content`
- `created_at`
- `token_estimate`
- `document_id`
- `document_title`
- `document_type`
- `basket_entry_ids`
- `source_card_id`
- `pinned`: boolean
- `compaction_state`: active, compacted, protected, archived

### Protected Context

The following content is never summarized away in the active request if relevant to the current action:

- system prompt
- current user instruction
- current open document metadata and selected text
- active rewrite proposal or unresolved review card
- current basket entries and their source document types
- pinned notebook entries
- citation keys or literature references used in the current request
- the most recent notebook turns inside the recency window

Protected content may still be stored in raw history, but compaction may not replace it with a lossy summary while it is active or pinned.

### Compaction Block

A compaction block replaces a contiguous span of old notebook entries in the active context assembly:

- `compaction_id`
- `chat_id`
- `source_entry_ids`
- `source_start_at`
- `source_end_at`
- `summary_markdown`
- `structured_summary`
- `token_estimate_before`
- `token_estimate_after`
- `compression_ratio`
- `model_provider`
- `model_name`
- `prompt_version`
- `created_at`
- `validation_status`
- `loss_flags`

The raw source entries remain stored and exportable.

### Structured Summary Shape

The compactor should produce both readable Markdown and structured data:

```json
{
  "working_goal": "string",
  "current_document_state": ["string"],
  "user_decisions": ["string"],
  "assistant_commitments": ["string"],
  "open_questions": ["string"],
  "pending_actions": ["string"],
  "important_facts": ["string"],
  "basket_and_source_notes": ["string"],
  "citations_and_literature_keys": ["string"],
  "rewrite_or_patch_state": ["string"],
  "retrieval_terms": ["string"],
  "source_entry_ids": ["entry-id"]
}
```

MVP summaries should prefer small lists over prose paragraphs so later request assembly can select relevant fields.

## Trigger Policy

Compaction should be available manually and automatically.

Manual triggers:
- command palette: `Compact Notebook Context`
- notebook toolbar or card action: `Compact`
- card action on a compaction event: `Rebuild Compaction`

Automatic triggers:
- before model request assembly when the projected request exceeds `context_compaction_trigger_ratio`
- after a draft/rewrite/chat response when the active notebook history exceeds `notebook_active_history_token_budget`
- when opening a long-running chat whose active entries plus required document/basket context exceed the target budget

Recommended defaults:

```yaml
notebook_context:
  compaction_enabled: true
  context_compaction_trigger_ratio: 0.72
  context_compaction_target_ratio: 0.55
  recent_turns_min: 6
  recent_turns_token_floor: 6000
  protected_context_token_reserve_ratio: 0.35
  retrieval_backfill_token_ratio: 0.15
  max_compaction_block_tokens: 3000
  max_recursive_summary_depth: 3
```

The request builder should leave enough room for output tokens. It must not fill the entire model context with input.

## Compaction Algorithm

### 1. Estimate Request Size

Before chat, draft, rewrite, search-card explanation, or summary generation:

1. Estimate tokens for the system prompt.
2. Estimate tokens for the current action frame.
3. Estimate tokens for current document context.
4. Estimate tokens for selected text or active rewrite proposal.
5. Estimate tokens for basket context.
6. Estimate tokens for protected notebook entries.
7. Estimate tokens for recent notebook entries.
8. Estimate tokens for existing compaction blocks.
9. Estimate output reserve.

If projected input exceeds the trigger threshold, begin compaction.

### 2. Select Compaction Span

Choose the oldest contiguous notebook entries that are:

- not pinned
- not currently unresolved
- not inside the recency window
- not required by the active selection/rewrite/draft path
- not already compacted at the current recursive level

Prefer compacting complete interaction units:

- user question/instruction
- assistant answer/result
- related status entries or cards

Do not split a rewrite review card from its apply/reject decision.

### 3. Summarize To Structured State

Use the same repo-backed system prompt family, plus a compaction-specific instruction:

- preserve user decisions exactly where possible
- preserve unresolved tasks
- preserve document titles/types and basket source types
- preserve citation keys and literature references
- preserve warning/error states
- do not invent new facts
- mark uncertainty explicitly
- include source entry IDs for every summary claim where possible

Compaction mode returns replacement context only. It must not write into the document.

### 4. Validate Summary

Validation checks:

- every pinned entry remains outside the compacted span or appears verbatim in protected context
- every unresolved rewrite/draft/search card remains outside the compacted span
- all source entry IDs are valid
- summary token estimate is below `max_compaction_block_tokens`
- summary contains no new document/citation IDs absent from source entries
- summary includes a non-empty `working_goal` or `important_facts` field

If validation fails, keep raw history active and show a notebook status event.

### 5. Replace Active Context, Not Raw History

After validation:

- mark source entries as `compacted`
- store the compaction block
- active request assembly uses the compaction block instead of the raw source entries
- raw source entries remain available for transcript export, inspection, and future re-compaction

### 6. Recursive Compaction

If active context remains too large after first-level compaction:

- compact older compaction blocks into a higher-level summary
- preserve source block IDs and source entry IDs
- cap recursive depth at `max_recursive_summary_depth`
- if still too large, reduce retrieval backfill before reducing recent turns

Recursive compaction must never discard raw source history.

## Request Assembly Order

Because long-context models can underuse middle-position material, request assembly should place high-value context deliberately:

1. system prompt
2. mode-specific instruction
3. compacted notebook state and pinned decisions
4. current document metadata and active selection
5. basket context
6. retrieval backfill from archived notebook entries, if relevant
7. recent notebook turns
8. current user instruction

Rationale:
- durable state belongs early
- immediate recency and the exact user instruction belong late
- middle budget should be reserved for document and basket material rather than low-value chat filler

## Retrieval Backfill

Compaction does not replace retrieval.

When a compacted notebook exists, the request builder may retrieve from:

- raw archived notebook entries
- compaction summaries
- current project documents
- basket entries
- later RAG chunks when Milestone 8 is active

MVP backfill can be FTS-first:

- search current instruction terms
- search active document title and document type
- search terms from `retrieval_terms` in compaction blocks
- rank by recency, pinned status, explicit document match, and keyword score

Backfill entries must be labeled as recovered context and include source entry IDs.

## UI And Notebook Behavior

Notebook history should render compaction transparently:

- compacted spans appear as a small `Compacted context` card
- card shows source time range, original token estimate, compacted token estimate, and compression ratio
- card actions:
  - `Expand`
  - `Rebuild`
  - `Pin`
  - `Restore Raw Context`
- active context status line shows whether compaction is active

Required copy:

- `Notebook context compacted. Raw history is still saved.`
- `Using compacted notebook context for this request.`
- `Compaction failed validation; raw notebook history remains active.`
- `Pinned entries are kept verbatim.`
- `Recovered archived notebook context: {entry_count} entries.`

Export behavior:

- transcript export includes raw entries by default
- optional export section may include compaction blocks for audit
- export must not silently replace raw transcript with summaries

## Engine/API Surface

Required engine contracts:

```text
estimate_notebook_context(chat_id, action_context) -> ContextBudgetReport
compact_notebook_context(chat_id, target_budget, protected_entry_ids) -> CompactionResult
build_compacted_model_request(chat_id, action_context, mode) -> ModelRequestContext
list_compaction_blocks(chat_id) -> list[CompactionBlock]
expand_compaction_block(compaction_id) -> list[NotebookEntry]
restore_raw_context(chat_id, compaction_id) -> RestoreResult
pin_notebook_entry(entry_id) -> NotebookEntry
unpin_notebook_entry(entry_id) -> NotebookEntry
retrieve_archived_notebook_context(chat_id, query, budget) -> list[RecoveredContextEntry]
```

Required A2UI/card contracts:

- `ContextBudgetCard`
- `CompactionBlockCard`
- `RecoveredNotebookContextCard`
- actions: compact, expand, rebuild, pin, unpin, restore raw

## Provider And Privacy Rules

- In confidential/local-only projects, compaction must use the local provider only.
- If local compaction is unavailable in confidential mode, block compaction and keep raw history; do not fall back to cloud.
- In non-confidential projects, compaction may use the configured default model/provider according to the existing provider policy.
- Compaction prompts must never include more raw context than needed for the selected compaction span.
- Compaction artifacts are project data and must be included in project transfer archives only as project-local state, not as license/provider credentials.

## Lane Ownership

No new lane is required for MVP. Implementation should be split across existing active and disabled lanes:

- `feat-context-storage`
  - notebook entries, compaction blocks, raw-history preservation, pin state, archived lookup
- `feat-engine-runs`
  - request budgeting, compaction trigger policy, compaction-mode model call, compacted request assembly
- `feat-retrieval-fts`
  - FTS backfill over archived notebook entries and compaction summaries
- `feat-a2ui-contract`
  - compaction cards, context-budget cards, recovered-context cards, action contracts
- `feat-commands`
  - CLI commands for compact, inspect budget, expand, and restore
- `feat-console-workflow`
  - later Textual notebook rendering and controls once UI lanes are activated

## CLI Surface

MVP CLI commands:

```text
exegesis notebook budget <chat-id>
exegesis notebook compact <chat-id> [--target-tokens N]
exegesis notebook compactions <chat-id>
exegesis notebook expand-compaction <compaction-id>
exegesis notebook restore-raw <chat-id> <compaction-id>
exegesis notebook pin <entry-id>
exegesis notebook unpin <entry-id>
```

## Test Plan

Storage tests:
- Raw notebook entries remain stored after compaction.
- Compaction blocks retain source entry IDs.
- Pinned entries are not compacted away.
- Restore raw context reactivates source entries.

Budget tests:
- Context budget report includes system, document, basket, protected, recent, compacted, backfill, and output-reserve buckets.
- Automatic compaction triggers when projected request exceeds threshold.
- Automatic compaction does not trigger when request is below threshold.

Compaction tests:
- Oldest eligible complete interaction span is selected.
- Recency window is preserved.
- Unresolved rewrite review cards are preserved.
- Summary validation rejects hallucinated document IDs.
- Recursive compaction stops at configured depth.

Request assembly tests:
- Current user instruction appears at the end of assembled context.
- Durable compacted state appears near the beginning.
- Basket context includes source document type labels.
- Retrieval backfill is labeled with source entry IDs.

Privacy/provider tests:
- Confidential mode uses local compaction only.
- Confidential mode blocks cloud fallback.
- Non-confidential mode respects configured provider policy.

UI/card tests:
- Compaction card shows original tokens, compacted tokens, compression ratio, and source time range.
- Expand action reveals raw source entries.
- Rebuild action replaces the compaction block only after validation.
- Transcript export defaults to raw entries, not compacted summaries.

## Done Means

- Long notebook sessions can continue without context overflow.
- The model receives a compacted but provenance-linked notebook state.
- Raw transcript history remains intact and exportable.
- Users can see when compaction happened and inspect or restore source entries.
- Confidential projects never send compaction spans to cloud providers.
- The implementation makes the canonical MVP path more real: open document, retrieve/gather context, draft/revise, apply/reject, persist, and continue without losing context.
