# Future Import, OCR, Literature Metadata, and RAG Specs

This document defines disabled future work for import normalization, literature metadata, and retrieval indexing. It is specification scaffolding only: no runtime OCR, literature metadata extraction, RAG indexing, shell import filtering, or inspector editing behavior should be active until the relevant lane is explicitly enabled.

Implementation rule:
- Each milestone below is written so its lane can be enabled in batches later without another planning pass.
- OCR import must be implemented before literature import because most literature arrives as PDF or other OCR-backed source files.
- Literature import must be specified before RAG is activated because chunk metadata should preserve literature references and citation metadata.
- Keep FTS as the baseline retrieval path; vector retrieval is additive and must not replace literal search.

## Shared Import And Indexing Conventions

Document type set:
- `draft`
- `memo`
- `summary`
- `transcript`
- `literature`

Import source classes:
- Markdown-direct: `md`, `markdown`.
- OCR-backed imports: `pdf`, `png`, `jpg`, `jpeg`, `tiff`, `tif`, `docx`, `txt`, `csv`, `xls`, `xlsx`.
- Unsupported extensions must be rejected before reading file contents, with a clear UI error.

Normalized document rule:
- Every imported file becomes editable Markdown in project storage.
- The original file is referenced through provenance, not treated as the primary editable document.
- Import should be idempotent by content hash where practical; repeated import of the same original should warn and offer duplicate or replace behavior.

Provenance baseline:
- original filename
- source extension and MIME type when available
- original file content hash
- normalized Markdown content hash
- import provider and model when OCR/model processing is used
- created/imported timestamp
- page, image, sheet, or segment index when applicable
- warnings and confidence values when available

Failure behavior:
- Failed OCR or metadata extraction should preserve an import failure record with enough detail for retry.
- Partial OCR results should be reviewable before save when possible.
- No import path should silently create empty documents.

## Milestone 6: OCR Import

Lane: `feat-ocr-import` (disabled)

Intent:
- Keep Markdown import direct and editable without OCR.
- Route non-Markdown imports through OCR into normalized editable Markdown.
- Make OCR provenance durable enough for later audit, metadata extraction, export, and RAG indexing.

Model targets:
- Online OCR: Nanonets OCR-3.
- Local/offline OCR: Nanonets OCR2.

References:
- [Nanonets OCR-3](https://nanonets.com/research/nanonets-ocr-3)
- [Nanonets supported file formats](https://docs.nanonets.com/docs/file-formats)
- [Nanonets OCR2-3B](https://huggingface.co/nanonets/Nanonets-OCR2-3B)

### Data Model

Add import concepts:
- `ImportJob`
  - `id`
  - `project_id`
  - `source_path` or source file handle reference
  - `source_filename`
  - `source_extension`
  - `mime_type`: optional
  - `source_content_hash`
  - `selected_document_type`
  - `status`: pending, processing, needs_review, completed, failed, canceled
  - `provider`: markdown_direct, nanonets_ocr_3, nanonets_ocr2, manual_retry
  - `provider_mode`: online or local
  - `warnings`
  - `error_message`: optional
  - `created_at`, `updated_at`
- `NormalizedImportDocument`
  - `id`
  - `import_job_id`
  - `project_id`
  - `document_id`: optional until saved
  - `title`
  - `document_type`
  - `markdown_content`
  - `markdown_content_hash`
  - `provenance_entries`
- `OcrProvenanceEntry`
  - `source_filename`
  - `source_extension`
  - `source_content_hash`
  - `provider`
  - `model`
  - `page_index`: optional
  - `sheet_index`: optional
  - `segment_index`: optional
  - `confidence`: optional
  - `markdown_start_offset`
  - `markdown_end_offset`
  - `warnings`

Storage rules:
- Store provenance alongside the normalized document, not only in logs.
- OCR provenance should survive document rename and folder moves.
- Original binary storage is optional for MVP; if not stored, provenance must still record the original filename and hash.

### Engine/API Surface

Add import actions:
- `list_supported_import_formats() -> SupportedImportFormats`
- `create_import_job(project_id, source_file, document_type) -> ImportJob`
- `run_import_job(import_job_id, provider_preference) -> ImportJobResult`
- `preview_normalized_import(import_job_id) -> NormalizedImportDocument`
- `approve_import(import_job_id, edited_markdown?, title?, document_type?) -> DocumentRef`
- `cancel_import(import_job_id) -> ImportJob`
- `retry_import(import_job_id, provider_preference?) -> ImportJob`

Provider preference:
- `auto`: use local provider when offline/confidential mode requires it; use online only when project policy allows cloud processing.
- `local`: force Nanonets OCR2.
- `online`: force Nanonets OCR-3 if project policy allows online processing.

Markdown-direct import:
- Bypasses OCR.
- Creates `ImportJob` with `provider=markdown_direct`.
- Still creates provenance with source filename/hash and normalized Markdown hash.

OCR-backed import:
- Creates one normalized Markdown document from the source file.
- Multi-page/sheet inputs should preserve page/sheet boundaries in Markdown with lightweight headings or comments that do not harm editing.
- Tables should be preserved as Markdown tables when practical.
- Images without recognized text should create a warning and optional placeholder rather than empty content.

### UI And Commands

Import modal:
- Show document type picker before file selection or alongside it.
- File picker filters to supported extensions.
- Markdown files are labeled as direct import.
- Non-Markdown supported files are labeled as OCR import.
- Unsupported file types are not selectable where the platform allows filtering; otherwise show a clear rejection.

Review modal:
- OCR-backed imports open a centered preview/approval modal before save.
- Preview shows editable normalized Markdown.
- Shows provenance summary: provider/model, original filename, page/sheet count, warnings.
- User can edit title, document type, and Markdown before saving.

Project browser:
- Approved imports are saved into the selected document type section.
- If Milestone 9 folders are active later, import can target a folder; before then, save to section root.

Command palette:
- `Import File`
- `Retry Import`
- `Approve Import`
- `Cancel Import`

### Implementation Batches

1. Format registry and import job model
   - Add supported extension registry, `ImportJob`, normalized document, and provenance data structures.
   - Add rejection behavior for unsupported extensions.
2. Markdown-direct path
   - Implement direct Markdown import with provenance and approval/save behavior.
3. OCR provider adapter contract
   - Add provider abstraction for Nanonets OCR-3 and OCR2 without hardwiring UI logic to provider details.
4. OCR normalization
   - Convert provider output into editable Markdown with page/sheet provenance and warnings.
5. Review/approval flow
   - Add preview modal contract, edited Markdown approval, and save-to-project behavior.
6. Retry and failure handling
   - Store failed jobs, support retry provider selection, and prevent silent empty documents.

### Edge Cases

- Duplicate file hash: warn and offer duplicate or replace.
- Empty OCR result: fail or require manual confirmation with warning.
- Partially failed multi-page OCR: preserve successful pages and mark failed pages.
- Spreadsheet import: each sheet becomes a Markdown section with sheet provenance.
- Large source file: show progress and allow cancellation.
- Confidential project: online OCR is blocked unless policy explicitly allows cloud processing.

### Test Plan

- Supported format registry includes Markdown and OCR-backed formats.
- Unsupported extension is rejected before import work starts.
- Markdown import bypasses OCR and still records provenance.
- PDF import uses OCR provider adapter and produces normalized Markdown.
- Multi-page import preserves page provenance offsets.
- Spreadsheet import preserves sheet provenance offsets.
- OCR warnings are visible in preview.
- User-edited preview Markdown is what gets saved.
- Duplicate source hash warns before creating duplicate document.
- Confidential/local-only project blocks online OCR and uses local provider.
- Failed import can be retried.
- Command palette contains import/retry/approve/cancel commands.

## Milestone 7: Literature Import

Lane: `feat-literature-import` (disabled)

Intent:
- Treat literature as a selected import type inside the import modal.
- Run metadata extraction for Markdown literature as well as OCR-derived literature.
- Keep literature metadata editable at approval time and later in the inspector.
- Preserve enough metadata for citation, export, and RAG chunk metadata.

### Data Model

Add literature metadata concepts:
- `LiteratureMetadata`
  - `id`
  - `project_id`
  - `document_id`
  - `title`
  - `authors`: ordered list of author names
  - `venue_or_publication`: optional
  - `year`: optional
  - `date`: optional
  - `DOI`: optional
  - `URL`: optional
  - `abstract`: optional
  - `citation_string`: optional
  - `citation_key`: stable key for Pandoc/citation support
  - `metadata_confidence`: optional per-field confidence map
  - `metadata_source`: deterministic, model_assisted, user_edited, zotero, or mixed
  - `created_at`, `updated_at`
- `LiteratureMetadataCandidate`
  - same metadata fields as above
  - `field_sources`: per-field source explanation
  - `warnings`
  - `requires_user_approval`: true by default

Citation key default:
- Generate from first author last name + year + short title slug where possible.
- Ensure uniqueness within project by suffixing when needed.
- Citation key remains editable before save and in inspector.

### Extraction Pipeline

Input sources:
- Markdown literature: skip OCR, run metadata extraction directly on Markdown.
- OCR-derived literature: use Milestone 6 OCR output first, then run metadata extraction on normalized Markdown plus OCR provenance.
- Metadata-only imports from later Zotero support should still flow through approval/editing.

Deterministic extraction order:
1. Frontmatter fields.
2. BibTeX blocks or citation metadata blocks.
3. DOI regex and DOI metadata lookup hook if later available.
4. Markdown headings/title block.
5. First-page or first-section heuristics.
6. URL patterns.
7. Abstract heading/section detection.

Model-assisted extraction:
- Runs only after deterministic extraction.
- Fills missing candidate fields or proposes alternatives.
- Must not overwrite deterministic fields without marking uncertainty.
- Must preserve uncertainty as editable candidate metadata rather than inventing missing values.

### Engine/API Surface

Add literature actions:
- `create_literature_import_candidate(import_job_or_document_id) -> LiteratureMetadataCandidate`
- `extract_literature_metadata(document_id, strategy) -> LiteratureMetadataCandidate`
- `approve_literature_metadata(document_id, edited_metadata) -> LiteratureMetadata`
- `update_literature_metadata(document_id, metadata_patch) -> LiteratureMetadata`
- `get_literature_metadata(document_id) -> LiteratureMetadata`
- `generate_citation_key(project_id, metadata) -> str`

Strategy values:
- `deterministic_only`
- `model_assisted`
- `manual_only`

Validation:
- Title is required before approval.
- Authors should be optional but warned if missing.
- Citation key is required before citation/export lanes use the record.
- DOI and URL should be normalized but not required.

### UI And Commands

Import modal:
- Literature remains a document type selected inside the import modal.
- Markdown literature import skips OCR but still opens metadata approval.
- Non-Markdown literature import runs OCR first, then metadata approval.

Metadata approval modal:
- Centered modal after import normalization.
- Editable fields: title, authors, venue/publication, year/date, DOI, URL, abstract, citation string, citation key.
- Show field-level confidence/source notes when available.
- User can approve, edit and approve, or cancel.

Inspector:
- When literature is open, show editable metadata fields.
- Saving inspector edits updates `LiteratureMetadata` without changing document body unless explicitly requested later.

Document pane:
- Literature document body remains editable Markdown.
- Metadata is shown in inspector, not injected into the body by default.

Command palette:
- `Extract Literature Metadata`
- `Edit Literature Metadata`
- `Approve Literature Metadata`
- `Regenerate Citation Key`

### Implementation Batches

1. Metadata model and citation key helper
   - Add metadata/candidate structures, validation, and uniqueness rules.
2. Deterministic extraction
   - Implement frontmatter, DOI, BibTeX, heading/title, first-page, URL, and abstract heuristics.
3. Approval/edit flow
   - Add editable approval modal contract and inspector edit contract.
4. Model-assisted candidate fill
   - Add model-assisted strategy after deterministic extraction.
5. Import integration
   - Wire Markdown literature and OCR-derived literature into the same approval path.

### Edge Cases

- Missing title: require user entry before approval.
- Multiple plausible titles: prefer deterministic title but show alternatives in warnings.
- Multiple DOIs: keep first high-confidence DOI and warn.
- Unknown authors: allow save with warning; citations/export later warn more strongly.
- OCR noise in title/abstract: allow correction before approval.
- Duplicate citation key: suffix and warn.
- Metadata edit after citations exist: update metadata but preserve citation key unless user explicitly changes it.

### Test Plan

- Markdown literature skips OCR and opens metadata approval.
- PDF literature routes through OCR first, then metadata approval.
- Frontmatter metadata is extracted deterministically.
- DOI regex extracts DOI and normalizes casing/prefix.
- BibTeX block maps to metadata fields.
- Heading/title heuristic proposes title when frontmatter is absent.
- Abstract section is detected when present.
- Model-assisted extraction fills missing fields without overwriting deterministic fields silently.
- Approval requires title and citation key.
- Inspector edits metadata and persists changes.
- Duplicate citation key receives a unique suffix.
- Command palette contains metadata extraction/edit/approval commands.

## Milestone 8: RAG Indexing and Retrieval

Lane: `feat-rag-index` (disabled)

Intent:
- Index normalized Markdown from direct Markdown imports and OCR-derived documents.
- Keep FTS as the baseline retrieval path.
- Add vector retrieval as an additive path once indexing is enabled.
- Return retrieval results in a shape that can promote chunks into the basket later.

Embedding targets:
- Online embeddings: Mistral `mistral-embed`.
- Local embeddings: Qwen3-Embedding-0.6B.

References:
- [Mistral Embed](https://docs.mistral.ai/models/model-cards/mistral-embed-23-12)
- [Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)

### Data Model

Add RAG/index concepts:
- `DocumentIndexRecord`
  - `id`
  - `project_id`
  - `document_id`
  - `document_type`
  - `document_title`
  - `document_content_hash`
  - `index_status`: pending, indexed, stale, failed
  - `indexed_at`
  - `chunk_count`
  - `embedding_provider`: optional
  - `warnings`
- `ChunkRecord`
  - `id`
  - `project_id`
  - `document_id`
  - `document_type`
  - `literature_metadata_id`: optional
  - `heading_path`: list of headings
  - `source_start_offset`
  - `source_end_offset`
  - `token_estimate`
  - `content_hash`
  - `chunk_text`
  - `provenance_refs`: OCR page/sheet provenance IDs when applicable
- `EmbeddingRecord`
  - `chunk_id`
  - `provider`: mistral_embed or qwen3_embedding_0_6b
  - `provider_mode`: online or local
  - `model`
  - `vector_ref` or vector bytes depending on storage adapter
  - `content_hash`
  - `created_at`
- `RetrievalHit`
  - `document_id`, `document_title`, `document_type`
  - `chunk_id`: optional for document-level FTS hits
  - `snippet`
  - `score`
  - `score_source`: fts, vector, or blended
  - `heading_path`
  - `token_estimate`
  - `literature_metadata`: optional compact metadata

### Chunking Contract

Defaults:
- Target 350-500 tokens per chunk.
- Use 75-100 token overlap.
- Preserve tables and code blocks when practical.
- Never split inside a Markdown table unless the table exceeds the chunk target by itself.
- Never split inside fenced code blocks unless the block exceeds the chunk target by itself.
- Keep heading path attached to every chunk.
- OCR page/sheet boundaries should be preserved as provenance even if chunks span boundaries.

Content hashing:
- Chunk hash is computed from normalized chunk text plus document ID and source offsets.
- Reindex only changed documents/chunks when content hash changes.
- Mark index records stale when document content hash no longer matches.

### Engine/API Surface

Add indexing actions:
- `schedule_document_index(project_id, document_id) -> DocumentIndexRecord`
- `index_document(project_id, document_id, options?) -> DocumentIndexRecord`
- `index_project(project_id, options?) -> IndexRunSummary`
- `get_document_index_status(document_id) -> DocumentIndexRecord`
- `mark_document_index_stale(document_id, reason) -> DocumentIndexRecord`
- `delete_document_index(document_id) -> DeleteResult`

Add retrieval actions:
- `search_project(query, filters?, mode?) -> RetrievalResultSet`
- `search_chunks(query, filters?, mode?) -> list[RetrievalHit]`
- `promote_chunk_to_basket(chunk_id) -> BasketEntry`

Mode values:
- `fts`: literal/FTS only.
- `vector`: vector only, enabled only when embeddings are available.
- `hybrid`: FTS baseline plus vector additive merge.

Filters:
- document type
- folder ID when Milestone 9 exists
- code ID when Milestone 9 exists
- literature metadata fields such as author/year/DOI when Milestone 7 exists
- date range when available

### Retrieval Behavior

FTS baseline:
- Always available for indexed Markdown.
- Literal query terms should produce deterministic results.
- Current FTS-first retrieval path remains authoritative until hybrid mode is stable.

Vector additive path:
- Uses Mistral online embeddings only when project policy allows cloud processing.
- Uses Qwen3-Embedding-0.6B locally for confidential/local mode.
- Vector failures should not break FTS retrieval; return FTS results with vector warning.

Hybrid merge:
- Run FTS first.
- Run vector if embeddings are available and policy allows.
- Deduplicate by chunk content hash and document ID.
- Prefer exact FTS hits when scores are close.
- Return score source and warnings so UI can explain why results appeared.

Retrieval cards:
- Show query, result count, provider/mode summary, and warnings.
- Each result row shows document title, document type, snippet, token estimate, and heading path.
- Chunk results can be promoted into basket as excerpt entries with document type and source metadata.

### UI And Commands

Indexing UI:
- For MVP, indexing can be automatic on import/save and visible through status only.
- Inspector may show index status for the selected document once lane is enabled.
- Failed/stale index states should show `Reindex Document`.

Search/retrieval UI:
- Existing search/retrieval cards should evolve to consume `RetrievalHit` records.
- Basket promotion from retrieval cards creates excerpt entries tied to chunk provenance.

Command palette:
- `Index Document`
- `Index Project`
- `Reindex Document`
- `Search Project`
- `Promote Chunk to Basket`

### Implementation Batches

1. Chunk model and Markdown chunker
   - Add chunk records, heading-path extraction, offset mapping, table/code preservation, and tests.
2. FTS index integration
   - Store chunks in FTS index and expose chunk-level retrieval hits.
3. Index lifecycle
   - Add stale detection, incremental reindex, delete index, and status reporting.
4. Embedding adapter contract
   - Add Mistral and Qwen provider abstractions with policy gating.
5. Hybrid retrieval merge
   - Merge FTS/vector hits with deduplication and score-source reporting.
6. Retrieval card and basket promotion contract
   - Return chunk payloads suitable for clickable cards and basket excerpt promotion.

### Edge Cases

- Empty document: create zero chunks and indexed status with warning.
- Very short document: create one chunk.
- Huge table/code block: keep intact and mark oversize warning.
- OCR-derived document: preserve OCR page/sheet provenance in chunks.
- Document edit after indexing: mark index stale by content hash mismatch.
- Embedding provider unavailable: keep FTS results and report vector warning.
- Confidential project: block online embeddings and use local embeddings when available.
- Duplicate chunks: deduplicate by content hash during retrieval display.

### Test Plan

- Markdown chunker creates 350-500 token target chunks with overlap.
- Heading path is attached to every chunk.
- Tables and fenced code blocks are preserved when practical.
- OCR provenance refs survive chunking.
- Index status becomes stale after document content hash changes.
- Reindex updates stale chunks and preserves unchanged chunk IDs where possible.
- FTS search returns deterministic chunk hits.
- Vector search is policy-gated for online/local mode.
- Hybrid search deduplicates duplicate FTS/vector hits.
- Vector provider failure returns FTS results with warning.
- Retrieval hits include document type, snippet, heading path, token estimate, and score source.
- Promoting a chunk to basket creates an excerpt with source document type and chunk provenance.
- Command palette contains indexing/search/promotion commands.
