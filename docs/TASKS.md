# Exegesis MVP Tasks

This file expands the canonical roadmap and lane mapping while the Textual lanes are disabled.

## Active now

### `feat-commands`
- keep `src/main.py` and the CLI surface stable during package migration
- preserve bootstrap, diff-preview, basket, and terminal command compatibility
- keep canonical imports available without breaking `src/qual/*`
- expose notebook context commands for budget, compact, list compactions, expand, restore raw, pin, and unpin

### `feat-context-storage`
- land canonical state models and storage adapters under `engine/src/exegesis_engine`
- keep basket/document/session persistence deterministic
- preserve current `src/qual/context/*` and `src/qual/storage/*` flows through shims or wrappers
- store raw notebook entries, compaction blocks, pin state, source entry IDs, validation status, and restore metadata from `docs/NOTEBOOK_CONTEXT_COMPACTION_SPEC.md`
- after Milestone 5 stands, implement encrypted SQLite-backed MVP trust storage for durable app/project metadata, sessions, workflow artifacts, document version/diff history, provenance, audit events, notebook compaction records, and generated A2UI promotion candidates
- keep Markdown documents/assets portable while richer trust state lives in SQLite
- include migration, backup/recovery, and clear failure behavior for encrypted SQLite storage
- after Milestone 5 stands, generate redacted support/diagnostic bundles that exclude document content, basket content, transcript text, credentials, file paths, and raw prompts by default
- define first-run/onboarding and recovery/failure-state copy for CoP launch

### `feat-retrieval-fts`
- keep the FTS-first retrieval path authoritative
- expose retrieval through the canonical engine contract
- keep structured results suitable for workflow cards and basket promotion
- support FTS backfill over archived notebook entries and compaction summaries
- after Milestone 5 stands, record provenance for retrieval hits, query/filter/ranking metadata, source documents/chunks, and basket-promotion links

### `feat-a2ui-contract`
- move card/action contracts and selection types into `shared/src/exegesis_shared`
- keep terminal/CLI rendering outside the shared package
- preserve `src/qual/ui/a2ui.py` as a compatibility layer while the migration settles
- define context-budget, compaction-block, and recovered-notebook-context cards/actions
- after Milestone 5 stands, complete full MVP A2UI protocol compatibility: handshake, capability negotiation, primitive block schemas, known card schemas, unknown-card fallback, typed action allowlist, payload validation, streaming event shape, and engine-side policy revalidation
- after Milestone 5 stands, define and persist generated A2UI draft records, usage telemetry, user feedback, review status, and promotion metadata for trusted CoP/beta dogfooding
- after Milestone 5 stands, add CLI-first promotion review commands for list/show/status/export plus a small bearer-token-protected HTML dashboard that renders safe A2UI primitives with inert action chips
- ensure generated A2UI surfaces are declarative data only and cannot execute arbitrary generated Swift, Python, JavaScript, shell, or downloaded code

### `feat-engine-runs`
- expose the canonical app service surface
- keep plan/draft/revise/apply/reject reachable through the engine contract
- preserve engine-first dependency direction during the migration
- implement request budgeting, compaction trigger policy, compaction-mode model calls, and compacted model request assembly
- after Milestone 5 stands, record provenance for each model request, context/basket input, generated output, rewrite proposal, patch preview, apply/reject decision, version history entry, restore action, and save-to-project artifact

## MVP CoP Gateway Lane

### `feat-cop-lite-licensing` early CoP Gateway MVP profile
- activate only after Milestone 5A trust substrate stands
- stand up the minimal Cloudflare Workers/D1/R2 License Gateway needed for first CoP beta use
- implement admin-issued Initial CoP/course invite creation, revocation, claim, activation, and license refresh
- collect minimal claim identity, such as display name and email when available, without adding a full username/password account system
- support manual activation-code entry and optional `exegesis://claim?token=...` custom URL handoff after installer download
- store refresh tokens in the OS credential store and preserve access across normal app updates
- return signed Lite entitlement payloads without storing provider secrets or Paddle state in the client
- ingest redacted A2UI promotion bundles from opted-in CoP/beta builds
- ingest redacted support/diagnostic bundles from CoP/beta builds
- reject confidential-project promotion uploads
- provide bearer-token-protected HTML admin review/export/status dashboard for promotion candidates
- keep Paddle checkout, paid Lite subscriptions, Studio/Pro inherited Lite access, and OCR top-up purchases out of this early profile
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` Milestone 5B as the lane-ready build sheet

## Defined but disabled

### `feat-console-shell`
Own later:
- `client-textual/src/exegesis_textual/app/**`
- `client-textual/src/exegesis_textual/layout/**`
- `client-textual/src/exegesis_textual/panes/**`
- `client-textual/src/exegesis_textual/commands/**`
- `client-textual/src/exegesis_textual/shortcuts/**`
- `client-textual/src/exegesis_textual/inspectors/**`
- `client-textual/src/exegesis_textual/theme/**`

### `feat-console-workflow`
Own later:
- `client-textual/src/exegesis_textual/workflow/**`
- `client-textual/src/exegesis_textual/cards/**`
- `client-textual/src/exegesis_textual/events/**`
- render notebook compaction cards and controls once Textual workflow lanes are enabled

### `feat-ocr-import`
Own later:
- OCR import specs and contracts for Markdown-direct and OCR-backed imports
- source-format allowlist for future import filtering
- OCR provenance shape for normalized Markdown outputs
- online target: Nanonets OCR-3
- local/offline target: Nanonets OCR2

Activation rule:
- disabled until explicitly enabled after the current engine/demo loop is stable

Implementation batches:
- use `docs/FUTURE_IMPORT_RAG_SPEC.md` as the lane-ready build sheet

### `feat-literature-import`
Own later:
- literature import type semantics inside the import modal
- metadata extraction contract for Markdown and OCR-derived literature
- editable metadata approval modal spec
- inspector metadata editing spec
- literature metadata fields and uncertainty handling

Activation rule:
- disabled until `feat-ocr-import` is specified and explicitly enabled for implementation

Implementation batches:
- use `docs/FUTURE_IMPORT_RAG_SPEC.md` as the lane-ready build sheet

### `feat-rag-index`
Own later:
- Markdown-aware chunking and chunk metadata contract
- FTS-plus-vector retrieval design
- retrieval-card payloads suitable for basket promotion
- online embeddings with Mistral `mistral-embed`
- local embeddings with Qwen3-Embedding-0.6B

Activation rule:
- disabled until OCR/import normalization and literature metadata specs are ready for implementation

Implementation batches:
- use `docs/FUTURE_IMPORT_RAG_SPEC.md` as the lane-ready build sheet

### `feat-qual-coding`
Own later:
- qualitative code project/database model
- document-local annotation model that does not appear in the project browser
- single-code selected-text highlight contract using blue highlights
- annotation selected-text highlight contract using yellow highlights
- code/annotation overlap rendering contract using green highlights
- project-browser `New Folder` behavior for document organization and parent codes
- drag-and-drop behavior for folders and codes
- inspector code details, frequencies, parent/child info, and clickable appearances
- inspector annotation details when an annotated range is selected
- code-focused document view with summaries and document excerpts
- coding/annotation shortcut row and command-palette entries

Activation rule:
- disabled until the current engine/demo loop is stable enough to expand into real coding workflows

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-editor-basics`
Own later:
- copy, paste, undo, and redo editor contracts
- editor history and clipboard interaction boundaries
- user-facing document version history over human edits, generated diffs, imports, and restores
- diff preview and restore-prior-version flow that creates a new current version without deleting newer history
- copy/paste/undo/redo shortcut row
- command-palette entries for editor basics and version history

Activation rule:
- disabled until qualitative coding and client/editor ownership are explicitly ready for implementation

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-zotero-import`
Own later:
- one-way Zotero as the preferred MVP literature import source
- Zotero browser/login or API-key workflow
- secure credential storage requirements
- Zotero metadata import into literature metadata
- literature folder as durable project-level literature library for citations, RAG, drafting, and context promotion
- skip initial metadata classification for Zotero attachments when Zotero metadata is complete
- no writeback, bidirectional sync, collection management, or deep-research export into Zotero
- attached-file import through the literature/OCR pipeline

Activation rule:
- disabled until OCR/import normalization and literature metadata contracts are ready

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-citations`
Own later:
- manual literature citation insertion
- optional page number or locator entry
- Pandoc-compatible citation storage
- citation rendering as document-pane links to literature
- LLM-used literature citation requirements
- citation top-row button and command-palette entries

Activation rule:
- disabled until literature metadata import is specified enough to provide citable literature records

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-export`
Own later:
- raw Markdown export
- APA PDF and DOCX export
- reference-list generation from cited literature
- draft author/institution metadata capture on draft create/import
- inspector and export-modal editing for APA identity metadata
- CSL/Pandoc scaffolding for future MLA, Chicago, and institution-specific formats

Activation rule:
- disabled until citation support and draft metadata contracts are ready

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-formatting-bar`
Own later:
- formatting bar for bold, italic, underline where supported, and heading levels
- image-as-figure insertion with title, caption, alt text, stable block ID, and project-managed asset reference
- Markdown table title/caption metadata wrapping for APA-ready export
- document and selection word counts in inspector reading metrics and draft/rewrite request context
- Markdown syntax insertion/wrapping behavior
- semantic heading preference for export/retrieval compatibility
- formatting shortcut row and command-palette entries

Activation rule:
- disabled until editor/client implementation lanes are explicitly activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-developer-provider-config`
Own later:
- developer-version-only command-palette provider configuration
- Lite remote Mistral Small 4 provider profile
- Lite managed Nanonets OCR-3 provider profile with cross-platform app-managed remote service credentials
- OpenAI, Claude, Mistral, Nanonets, and local OpenAI-compatible endpoint setup
- default online provider plus model and supported reasoning-level selection
- connection testing and credential clearing commands
- macOS Keychain, Windows Credential Manager/DPAPI-backed storage, and Linux Secret Service/libsecret credential-store modes
- backend provider-router integration for developer BYOK/BYOM setup
- packaged-distro command hiding and backend rejection

Activation rule:
- disabled until developer-version provider configuration is intentionally activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-project-transfer`
Own later:
- project export/import through portable zip archives
- archive manifest, schema version, content hashes, and safe path validation
- export of documents, basket, summaries, transcripts, literature metadata, citations, annotations, codes, document version/diff history, datasets, assets, provenance, and safe project settings
- explicit exclusion of credentials, provider keys, local endpoints, managed Lite secrets, license refresh tokens, and machine caches
- import preview, validation, conflict handling, and import-as-new restore behavior
- licensing integration: licenses are per user/account, not per machine or project archive

Activation rule:
- disabled until MVP project transfer work is intentionally activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-desktop-packaging`
Own later:
- Developer and Lite desktop distribution profiles
- pywebview native shell around the locally served Textual UI
- bundled Python runtime, Engine, Textual local server, and SQLite local storage
- Briefcase packaging for macOS `.dmg`, Windows `.msi`, and Linux Flatpak
- packaged Developer/Lite executables that do not depend on system Python
- platform app-data directory handling for database, project files, cache, and logs
- loopback-only local server startup, port collision handling, and shutdown coordination
- GitHub Release artifact collection and checksum generation
- Cloudflare R2 release manifest, update checks, unobtrusive update button, and `Check for Updates` menu command
- required-update gate that blocks confidential project creation/open until the app is fully updated
- Developer profile integration with Milestone 15 BYOK/BYOM provider commands
- Lite profile integration with remote Mistral Small 4 and managed Nanonets OCR-3
- Lite local Python services called directly inside the packaged app, with the hosted License Gateway reserved for managed remote credentials, license refresh, Paddle, and Nanonets accounting

Activation rule:
- disabled until desktop packaging work is intentionally activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-cop-lite-licensing` paid expansion profile
Own later, after the Milestone 5B CoP Gateway MVP is standing:
- individual paid Lite licensing through website checkout and Paddle webhooks
- Studio and Pro subscription licensing that includes Lite access for secondary-machine use
- course licensing through one instructor-distributed self-serve student link
- Tally intake form accessible through MCP for Claude cowork-assisted classification and manual approval preparation
- initial CoP unlimited Lite course access with no seat cap
- Developer/Lite boundary where Developer never uses hosted Lite workflows
- extensions to the hosted License Gateway for managed Lite provider proxy, Studio/Pro managed OCR fallback, Paddle webhooks, and Nanonets page state
- preserve the Cloudflare Workers/D1/R2 hosting target from Milestone 5B
- preserve the hosted A2UI promotion intake service and bearer-token admin dashboard from Milestone 5B
- consent, redaction, pseudonymous install/license identifiers, and confidential-project upload prohibition for A2UI promotion intake
- Nanonets page ledger with 150-page default initial CoP balance
- Studio managed cloud OCR bucket of 250 pages per month and Pro managed cloud OCR bucket of 500 pages per month
- Pro BYOK/BYOM provider configuration for OpenAI, Claude, Mistral, and local OpenAI-compatible backends, including provider/model/reasoning selection for non-confidential projects only
- edition hardware tiers: Lite 8 GB, Studio 8 GB with online OCR, Pro 16 GB, local OCR when current memory allows, and 128 GB for local confidential mode
- Pro-only entitlement gating for Quantitative Analysis and Advanced Qualitative Coding Visualizations
- fixed Nanonets top-up packages of 150, 500, and 1000 pages
- per-user/account licensing boundaries integrated with project transfer
- transaction-safe OCR page reservation, consumption, release, refund, and idempotent callback handling
- Lite import-window Nanonets balance, estimated-page count, insufficient-balance, and top-up package behavior
- effective entitlement refresh that accepts Lite access from individual Lite, course Lite, CoP Lite, Studio, or Pro sources
- future Tally/manual approval/Claude cowork license-generation hooks

Activation rule:
- disabled until Lite licensing and hosted gateway work is intentionally activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-browser-pdf-capture`
Own later:
- minimal Chrome, Firefox, and Safari browser extension for current-tab PDF capture only
- popup states for PDF detected, not PDF, Exegesis unavailable, accepted handoff, and rejected handoff
- current-tab PDF detection without page scraping, translator behavior, link discovery, or browser-side OCR
- loopback Exegesis capture endpoint contract and custom protocol/native messaging fallback hooks
- pending browser import record and import-review handoff into Exegesis
- direct-fetch-first PDF handling, authenticated-PDF graceful failure, and future browser-assisted relay hook
- packaging artifacts and browser install/enable guidance bundled with desktop releases
- command-palette entries for browser extension install, status, and help

Activation rule:
- disabled until explicitly enabled after the MVP launch gate and real CoP usage feedback

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-python-sidecar-api`
Own later:
- signed, sandboxed macOS XPC Python sidecar bridge for Python-backed Studio features
- bundled Python worker/XPC service packaging inside the signed Studio `.app`
- baseline `healthz`, `readyz`, `version`, `features`, and `shutdown` RPC handler contracts
- signed-app-only sidecar channel, sandbox inheritance, request size limits, file-access validation, and log redaction
- macOS Studio Workstation launch, health polling, bounded restart, compatibility/signature/entitlement checks, and graceful shutdown contract
- sidecar handler manifest and schema/version negotiation for feature groups
- requirement that later Workstation/SwiftUI-facing Python features expose their behavior through sidecar handlers
- boundary that Python/Textual Lite reuses the shared Python service layer directly and does not adopt the native XPC sidecar

Activation rule:
- disabled until explicitly enabled after the MVP launch gate and real CoP usage feedback

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-native-workstation`
Own later:
- macOS Studio Workstation app lifecycle, window/runtime boundary, and local UI hosting strategy
- native settings for Light, Dark, and Auto appearance modes
- STTextView as preferred native editor foundation candidate, with plugin planning for annotations, Markdown highlighting, diffs, citations, figures, and tables
- bundled Milestone 20 sidecar launch, health monitoring, compatibility checks, restart, and shutdown
- Workstation memory tiers and local/confidential capability checks
- Pro local model manager for confidential runtime model downloads, storage, deletion, checksums, and tier selection
- local OCR preference with managed cloud OCR fallback when current available memory is insufficient and project policy allows cloud processing
- signed web-distributed macOS Studio artifact
- macOS signing/notarization and checksums
- explicit exclusion of Windows/Linux Studio signing and packaging
- release manifest, checksums, web download flow, and troubleshooting copy
- Cloudflare R2-backed update checks, unobtrusive update button, `Check for Updates` menu command, and required-update confidential project gate
- update/manual upgrade behavior that preserves project data and does not orphan sidecars
- local backend status and failure surfaces for sidecar startup/incompatibility issues
- interactive sprint guidance because native packaging/signing should not be blindly daemon-scheduled

Activation rule:
- disabled until explicitly enabled after the MVP launch gate and real CoP usage feedback
- activation should be managed interactively, with daemon work limited to narrow scriptable tasks

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the conceptual sprint build sheet

### `feat-open-access-deep-research`
Own later:
- local-first multi-agent source discovery for possible literature and web sources
- current-project search, selected-other-project search, then open web/scholarly provider fan-out
- LangChain Open Deep Research-inspired supervisor/researcher architecture without report writing or synthesis
- Tavily provider adapter as default when configured, with Brave, Exa, and PDF/full-text-capable scholarly adapters as additive sources
- provider-normalized source candidate records with provenance, confidence, import hints, and review status
- DOI, canonical URL, title/author/year, provider ID, and future content-hash dedupe
- explainable candidate ranking and import readiness labels
- native Studio Workstation SwiftUI source batch cards/lists that hand selected candidates to the standard import protocol
- sidecar handlers for research job creation, status, cancellation, candidate batch retrieval, and import-batch handoff
- native Studio Workstation/SwiftUI only; no Textual shell implementation
- privacy/project-mode/credential controls so confidential project content is not sent to open web providers without explicit permission
- audit trail for search plan, providers, queries, candidates, dedupe decisions, selections, and import request IDs

Activation rule:
- disabled until explicitly enabled after the MVP launch gate and real CoP usage feedback

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-quant-analysis`
Own later:
- first-class native Studio Workstation `Datasets` project browser section
- Pro-only entitlement requirement through `pro_feature_access`
- CSV-only dataset import with provenance, row/column guardrails, and dataset storage
- variable metadata and auto-detection for categorical, ordinal, and scale variables
- native Studio Workstation raw-data view with variable type override controls
- lean dataset preparation transforms: filtering, row removal, column removal, one-hot encoding, manual categorical/ordinal quantization, and keyed dataset union
- inspector-driven analysis picker and variable selectors
- descriptive statistics overall and split by categorical/ordinal variables
- frequency and contingency tables
- t-test, ANOVA, chi-squared, and linear correlation
- p-values and effect sizes for inferential tests
- small/medium/large effect-size guidance
- markdown result tables
- bar chart, density curve, and scatter plot artifacts
- ordered analysis sequence transcript for tests
- save analysis sequence as a project summary
- native `StatsCore` Swift APIs with Codable result structs and DataFrame-compatible table adapters
- narrow `StatsBridge` C shim that isolates IMSL C Numerical Library calls and normalizes status/error codes
- vendor feasibility gate for IMSL macOS, Apple Silicon, redistribution, linking mode, Swift/Xcode use, CI, signing, and notarization
- optional sidecar exposure only if future Python-backed preprocessing or artifact generation is intentionally added
- native Studio Workstation/SwiftUI only; no Textual shell implementation
- local-only Swift/IMSL execution boundaries

Activation rule:
- disabled until explicitly enabled after the MVP launch gate and real CoP usage feedback

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-advanced-qual-visuals`
Own later:
- Studio Pro browsable code graphs for parent/child code structure, co-occurrence, and document/code relationships
- Pro-only entitlement requirement through `pro_feature_access`
- code-by-document, code-by-document-type, code-by-folder, and parent/child matrices
- distribution tables for frequencies, coverage, code density, and parent/child rollups
- visual comparisons across selected documents, document types, participants, folders, groups, and codes
- codebook generation from code metadata, definitions, frequencies, representative excerpts, and audit history
- native Studio Workstation SwiftUI graph, matrix, comparison, and codebook surfaces
- sidecar handler contracts for aggregation and artifact generation where Python-backed processing is needed
- explicit Textual shell exclusion

Activation rule:
- disabled until Studio Pro advanced qualitative coding visualization work is intentionally activated after native Studio is available

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the conceptual build sheet

### `feat-confidential-collaboration`
Own later:
- conceptual threat model and privacy boundary for shared confidential projects
- shared project membership, invitations, roles, permissions, and audit events
- encrypted/local-first sync or secure collaboration-service architecture decision
- collaboration data concepts for operations, comments, review decisions, conflicts, sync checkpoints, and device identity
- account-based collaboration licensing and entitlement refresh rules, not machine-based licensing
- Lite participation boundaries for higher-licensed users working from secondary machines
- native Studio Workstation SwiftUI collaboration surfaces for sharing status, members, activity, review, comments, conflicts, and sync health
- Studio-only collaboration management boundaries so Lite participation does not unlock Pro/admin surfaces
- sidecar/service boundary for local coordination, sync health, audit queries, and future hosted relay contracts
- project-mode preservation, provider allowlists, and cloud-send policy boundaries
- explicit current Textual shell exclusion while preserving a future Lite participation spec
- implementation-lane split after the conceptual architecture is accepted

Activation rule:
- disabled until explicitly enabled after Studio Pro usage feedback
- expected to be handled as a design-first company-wide sprint before broad daemon execution

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the conceptual build sheet

### `feat-ipad-native-lite`
Own later:
- native iPadOS Lite product boundary after confidential collaboration
- inventory of Python-backed or macOS-sidecar-dependent workflows that must become Swift-native, gateway-backed, deferred, or unavailable on iPad
- reuse plan for mature Studio/Pro Swift-native editor, project, import, license, and collaboration components
- account-based Lite entitlement refresh on iPad, including inherited Lite access for Studio/Pro subscribers
- project archive import/export, offline cache, file provider, document picker, and share sheet boundaries
- constrained iPad Lite collaboration participation without Studio-only management or Pro-only surfaces
- activation prerequisites for splitting this long-term client work into implementation lanes

Activation rule:
- disabled until explicitly enabled after confidential collaboration and mature Studio/Pro native foundations
- expected to be handled as a conceptual client-architecture sprint before implementation

Implementation batches:
- use `docs/POST_MVP_FEATURES_SPEC.md` as the conceptual build sheet

## Explicitly not now
- Textual dependency installation
- Textual widget implementation
- runtime OCR implementation
- runtime literature metadata extraction
- runtime RAG indexing or vector retrieval
- runtime qualitative coding behavior
- runtime editor copy/paste/undo/redo behavior
- runtime citation behavior
- runtime export behavior
- runtime Zotero import behavior
- runtime formatting bar behavior
- runtime developer provider configuration behavior
- runtime project transfer export/import behavior
- runtime desktop packaging behavior
- runtime Lite license gateway behavior
- runtime CoP course licensing behavior
- runtime Nanonets page-credit metering or Paddle top-ups
- runtime browser extension, local browser-capture endpoint, native bridge, or PDF capture behavior
- runtime Python sidecar API behavior
- runtime native Workstation packaging/signing/distribution behavior
- runtime open web search, multi-agent research orchestration, provider API calls, candidate ranking, or research import-batch behavior
- runtime advanced qualitative coding visualization, matrix, graph, comparison, or codebook behavior
- runtime confidential collaboration, sync, invitation, shared project, or SwiftUI collaboration behavior
- runtime native iPad Lite, App Store packaging, Swift-native sidecar replacement, or iPadOS client behavior
- shell import filtering changes
- shell import-window Nanonets balance behavior
- inspector metadata editing behavior
- tabs, live preview, collaboration, sync, drag-and-drop
- native workstation shell work
