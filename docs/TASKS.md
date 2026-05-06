# Exegesis MVP Tasks

This file expands the canonical roadmap and lane mapping while the Textual lanes are disabled.

## Active now

### `feat-commands`
- keep `src/main.py` and the CLI surface stable during package migration
- preserve bootstrap, diff-preview, basket, and terminal command compatibility
- keep canonical imports available without breaking `src/qual/*`

### `feat-context-storage`
- land canonical state models and storage adapters under `engine/src/exegesis_engine`
- keep basket/document/session persistence deterministic
- preserve current `src/qual/context/*` and `src/qual/storage/*` flows through shims or wrappers

### `feat-retrieval-fts`
- keep the FTS-first retrieval path authoritative
- expose retrieval through the canonical engine contract
- keep structured results suitable for workflow cards and basket promotion

### `feat-a2ui-contract`
- move card/action contracts and selection types into `shared/src/exegesis_shared`
- keep terminal/CLI rendering outside the shared package
- preserve `src/qual/ui/a2ui.py` as a compatibility layer while the migration settles

### `feat-engine-runs`
- expose the canonical app service surface
- keep plan/draft/revise/apply/reject reachable through the engine contract
- preserve engine-first dependency direction during the migration

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
- single-code selected-text highlight contract
- project-browser `New Folder` behavior for document organization and parent codes
- drag-and-drop behavior for folders and codes
- inspector code details, frequencies, parent/child info, and clickable appearances
- code-focused document view with summaries and document excerpts
- coding shortcut row and command-palette entries

Activation rule:
- disabled until the current engine/demo loop is stable enough to expand into real coding workflows

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-editor-basics`
Own later:
- copy, paste, undo, and redo editor contracts
- editor history and clipboard interaction boundaries
- copy/paste/undo/redo shortcut row
- command-palette entries for editor basics

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
- default online provider and default model selection
- connection testing and credential clearing commands
- macOS Keychain, Windows Credential Manager/DPAPI-backed storage, and Linux Secret Service/libsecret credential-store modes
- backend provider-router integration for developer BYOK/BYOM setup
- packaged-distro command hiding and backend rejection

Activation rule:
- disabled until developer-version provider configuration is intentionally activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-desktop-packaging`
Own later:
- Developer and Lite desktop distribution profiles
- pywebview native shell around the locally served Textual UI
- bundled Python runtime, Engine, Textual local server, and SQLite local storage
- Briefcase packaging for macOS `.dmg`, Windows `.msi`, and Linux Flatpak
- platform app-data directory handling for database, project files, cache, and logs
- loopback-only local server startup, port collision handling, and shutdown coordination
- GitHub Release artifact collection and checksum generation
- Developer profile integration with Milestone 15 BYOK/BYOM provider commands
- Lite profile integration with remote Mistral Small 4 and managed Nanonets OCR-3

Activation rule:
- disabled until desktop packaging work is intentionally activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

### `feat-cop-lite-licensing`
Own later:
- initial CoP unlimited Lite course access with no seat cap
- Developer/Lite boundary where Developer never uses hosted Lite workflows
- Lite-only hosted License Gateway for license invites, claim, refresh, managed provider proxy, Paddle webhooks, and Nanonets page state
- Nanonets page ledger with 150-page default initial CoP balance
- fixed Nanonets top-up packages of 150, 500, and 1000 pages
- transaction-safe OCR page reservation, consumption, release, refund, and idempotent callback handling
- Lite import-window Nanonets balance, estimated-page count, insufficient-balance, and top-up package behavior
- future Tally/manual approval/Claude cowork license-generation hooks

Activation rule:
- disabled until Lite licensing and hosted gateway work is intentionally activated

Implementation batches:
- use `docs/FUTURE_MVP_FEATURES_SPEC.md` as the lane-ready build sheet

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
- runtime desktop packaging behavior
- runtime Lite license gateway behavior
- runtime CoP course licensing behavior
- runtime Nanonets page-credit metering or Paddle top-ups
- shell import filtering changes
- shell import-window Nanonets balance behavior
- inspector metadata editing behavior
- tabs, live preview, collaboration, sync, drag-and-drop
- native workstation shell work
