# Deep Research Milestone Spec

## Purpose

- Implement Deep Research as a workflow runner that produces first-class vault artifacts (not chat text).
- Phase 1 (MVP for this module): internal-only research (vault sources only). No web.
- Phase 2 (later): online research tools allowed only for online projects, with explicit policy gating.

## Non-Goals (Phase 1)

- No web search, crawling, or remote OCR.
- No agent autonomy framing. This is a deterministic pipeline with tool-using models.
- No requirement for remote/hosted embeddings services in Phase 1; local embeddings retrieval is part of MVP via unified retrieval.

## Core Concept

Deep Research is a run that:
1. plans sub-questions
2. retrieves evidence (vault)
3. extracts/pins excerpts with provenance
4. synthesizes artifacts (memo/report/matrix)
5. optionally proposes patch edits to a target section

Everything is stored and traceable.

## A) Entry Points (Engine API)

1. `deep_research.run(request: DeepResearchRequest) -> stream events + final DeepResearchResult`
2. `deep_research.resume(run_id) -> stream events`
3. `deep_research.cancel(run_id) -> ok`

`DeepResearchRequest` fields:
- `project_id: uuid`
- `topic: string`
- `mode: "internal_only" | "online_allowed"` (Phase 1 supports `internal_only` only)
- `scope`:
  - `"vault" | "collection:<id>" | "doc:<doc_id>" | "section:<section_id>"`
- `target_section_id: uuid?` (optional) // if provided, module may propose patches
- `outputs: list` of:
  - `"research_plan"`
  - `"source_set"`
  - `"evidence_table_csv"`
  - `"synthesis_memo"`
  - `"annotated_outline"`
  - `"patch_proposals"` (only if `target_section_id` present)
- `constraints`:
  - `max_sources: int` (default 20)
  - `max_excerpts: int` (default 40)
  - `citation_style_id: string?` (for example, `"apa"`)
  - `require_provenance: bool` (default true)
  - `prefer_recent: bool` (optional)
- `user_notes: string?` (optional)

## B) Outputs (Vault Artifacts)

All outputs are stored as encrypted artifacts in the vault and linked to the run.

Artifact types:

1. `ResearchPlanArtifact`
- `questions[]` (sub-questions)
- `retrieval_strategy` (`fts/pageindex/embeddings`)
- `inclusion_criteria`, `exclusion_criteria`
- `stopping_rules` (when to stop collecting)
- `next_actions`

2. `SourceSetArtifact`
- `items[]`:
  - `doc_id`
  - `doc_type`
  - `title_hint` (safe; avoid full paths)
  - `reason_included` (short)
- `provenance`:
  - `run_id`
  - `retrieval_hits` (ids only)

3. `EvidenceTableArtifact` (CSV)
- output file: `evidence_table.csv` (always CSV)
- columns (minimum):
  - `excerpt_id`, `doc_id`, `location` (`page_range/char_range`), `node_path` (optional), `tags`, `notes`, `relevance_score`
- store as CSV artifact + schema metadata

4. `SynthesisMemoArtifact`
- markdown memo with inline citations referencing `excerpt_ids` and/or citekeys
- MUST include `Evidence Used` section listing `excerpt_ids` and `doc_ids`
- MUST avoid claims without evidence unless explicitly flagged as `Interpretation`

5. `AnnotatedOutlineArtifact`
- outline sections + bullet claims
- each claim line references `excerpt_ids` (or says `needs evidence`)

6. `PatchProposalsArtifact` (optional)
- list of `ProposedEdit` patches targeting `target_section_id`
- patch format aligns with existing diff/patch A2UI cards
- each patch links to `excerpt_ids` used

## C) Run Graph + Audit

`DeepResearchRunRecord` (encrypted DB):
- `run_id`, `project_id`, `started_at`, `completed_at`, `status`
- `mode`, `scope`, `target_section_id`
- `models_used`:
  - `terminal_chat` (Magistral)
  - `planner_deep` (Qwen) when escalated
  - `bulk_best` (GPT) only if generating long memo or patches (optional policy)
- `policy_state`:
  - `project_mode` (`confidential/online`)
  - `cloud_send_policy` (if online; Phase 1 unused)
- `stats`:
  - `docs_considered`, `docs_selected`, `excerpts_created`, `tool_calls_count`, `duration_ms`
- `artifact_ids[]` (all created artifacts)
- `error_summary` (no content)

`AuditEvents` (existing system) must record:
- `deep_research_started`
- `deep_research_step_completed(step_name)`
- `deep_research_completed`
- `deep_research_cancelled`
- `deep_research_failed`

## D) Pipeline Steps (Deterministic)

Step 0: Validate + PolicyGate
- If `project_mode == confidential`:
  - enforce `internal_only` (Phase 1)
  - deny any online tools
- Validate request constraints (`max_sources`, `max_excerpts`)
- Initialize run record

Step 1: Plan
- Model: `planner_default` (Magistral) OR `planner_deep` (Qwen) if complexity triggers
- Output: `ResearchPlanArtifact`
- Plan must specify:
  - sub-questions
  - what constitutes sufficient evidence
  - retrieval approach (FTS + embeddings shortlist + PageIndex deep dive)
  - max sources/excerpts targets

Step 2: Retrieve candidates (vault only)
- Use unified retrieval interface:
  - `retrieval.auto(query, scope, intent="lookup/compare/summarize")`
- Retrieval auto in MVP combines FTS + embeddings shortlist signals, then applies PageIndex where available.
- Create `SourceSetArtifact` with top `doc_ids` (`<= max_sources`)
- For each selected doc:
  - run PageIndex query when available to locate relevant sections
  - produce `RetrievalHits` with `excerpt_ids`

Step 3: Extract + Normalize evidence
- Ensure each hit is an `Excerpt` object (encrypted) with stable IDs and spans
- Cap to `max_excerpts` with clear selection rule:
  - prioritize diversity of sources + direct relevance
- Output: `EvidenceTableArtifact` (CSV) listing `excerpt_ids` and provenance

Step 4: Synthesize
- Input to model is ONLY:
  - topic + plan
  - selected excerpts (by `excerpt_id -> fetched text`)
  - citations metadata
- Output: `SynthesisMemoArtifact`
- Requirements:
  - every substantive claim references at least one `excerpt_id` OR is labeled `Interpretation`
  - include `Evidence Used` appendix listing `excerpt_ids/doc_ids`

Step 5: (Optional) Annotated outline
- Create `AnnotatedOutlineArtifact` with claim-to-evidence mapping

Step 6: (Optional) Patch proposals to target section
- Only if `target_section_id` provided
- Generate patches (`ProposedEdit`) referencing evidence `excerpt_ids`
- Output: `PatchProposalsArtifact` and A2UI `ProposedEditCards`

Step 7: Emit final result
`DeepResearchResult`:
- `run_id`
- `artifact_ids` by type
- `summary` (short)
- `warnings[]` (for example, evidence thin in area X)

## E) Tools (Phase 1)

Deep research uses existing tools only:
- `retrieval.auto` / `retrieval.in_doc`
- `fetch_excerpt(excerpt_id)`
- `create_context_set(name, excerpt_ids)`
- `write_artifact(type, content, metadata)`
- `propose_patch(target_section_id, patch, evidence_excerpt_ids)`

No web tools.

## F) A2UI Integration (Terminal + Inspector)

During run:
- stream `ProgressCards` for steps (Plan, Retrieve, Extract, Synthesize, Patch)
- emit cards:
  - `ResearchPlanCard` (or `GenericCard`)
  - `SourceSetCard` (list docs + actions)
  - `EvidenceTableCard` (table preview + Open CSV)
  - `SynthesisMemoCard` (open memo artifact)
  - `PatchProposalsCard` (apply/reject each)

Actions are allowlisted:
- `open_artifact`
- `pin_to_context_set`
- `open_document_at_location`
- `apply_patch` / `reject_patch`

## G) Model Routing Rules (Phase 1)

Default:
- Planning + terminal orchestration: Magistral

Escalate to Qwen for:
- multi-step orchestration or outline-heavy planning

Use GPT-OSS only for:
- long-form memo generation OR long patch generation
- and only when local tier supports it (per profile)

## H) Online Deep Research (Phase 2 placeholder)

When `project_mode == online`:
- allow tools:
  - `web_search`
  - `fetch_url`
  - `parse_pdf_from_url`
- enforce `cloud_send_policy`:
  - `context_sets_only` default
- store downloaded sources as vault artifacts with provenance

## I) Acceptance Criteria (Phase 1)

1. `deep_research.run` produces at least:
  - `ResearchPlanArtifact`
  - `SourceSetArtifact`
  - `EvidenceTableArtifact` (CSV)
  - `SynthesisMemoArtifact`
2. All claims in `SynthesisMemo` either cite `excerpt_ids` or are labeled `Interpretation`.
3. All artifacts are stored encrypted and linked to `run_id` with audit events.
4. No network calls occur in Confidential projects.
5. Terminal displays progress + A2UI cards; user can open artifacts and apply patches.
6. Cancelling a run stops further tool calls and leaves partial artifacts marked as partial with status.
