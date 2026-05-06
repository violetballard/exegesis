# Exegesis MVP Milestones

This file expands the canonical roadmap in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/ROADMAP.md`.

## Milestone 1: Standing shell

Outcome:
- A 5-pane Textual shell stands as a stable mockup baseline in Textual/browser, but it is not yet wired to live engine state or actions. The implementation lanes remain disabled until the engine contract is stable enough to consume.

Deliverables:
- standing shell mockup baseline
- 3-column shell layout definition
- Project / Document / Workflow / Context Basket / Inspector pane boundaries
- Focus model and shortcut bar plan
- Command palette scaffold plan

Status:
- Standing (mockup only; not engine-wired)
- Lane state: disabled for product-real integration (`feat-console-shell`, `feat-console-workflow`)

## Milestone 2: Core pane interactions

Outcome:
- The Textual shell stops being static once the UI lanes are activated.

Deliverables:
- project item listing and open flow
- document edit/save flow
- basket add/remove/select/clear
- inspector follows selection
- workflow pane accepts commands and renders selectable cards

Status:
- Planned
- Lane state: disabled until engine contract is ready

## Milestone 3: Real workflow loop

Outcome:
- The repo exposes a complete engine-side contract for retrieve -> basket -> plan -> revise -> patch -> document.

Active engine ownership:
- `feat-retrieval-fts`: retrieval/search
- `feat-engine-runs`: plan, draft, revise, apply/reject flows
- `feat-context-storage`: persistent basket/document/session state
- `feat-a2ui-contract`: shared card/action contracts
- `feat-commands`: CLI compatibility while the package/layout migration is underway

Status:
- In progress

## Milestone 4: Dogfooding readiness

Outcome:
- The engine contract and the future Textual client surface are stable enough for real writing sessions.

Deliverables:
- persistence for document/basket/session state
- save-to-project workflow output paths
- readable, durable workflow cards
- keyboard-first interaction plan carried through the client
- minimal audit/proposal logging

Status:
- Split work: active in engine lanes now, deferred in disabled UI lanes

## Milestone 5: YC demo readiness

Outcome:
- One clean, reproducible demo path exists for retrieve -> basket -> plan -> revise -> apply.

Deliverables:
- demo project
- repeatable retrieval and basket build
- repeatable plan and revision scenario
- stable pane labels and core actions
- no broken states on the recorded flow

Status:
- Planned
- Owned as cross-lane/integrator work, not a dedicated feature lane

Current operating rule:
- Until this milestone is standing, all active engine work should be evaluated against one canonical demo path:
  - open project/document
  - retrieve relevant material
  - promote or gather context into the basket
  - produce a plan or revision
  - preview and apply or reject a patch
  - persist updated document/session state
  - continue working
- Code churn, contract cleanup, or infra work do not count toward this milestone unless they directly unblock or harden that specific path.

## Milestone 6: OCR import

Outcome:
- The project can eventually import non-Markdown source files by OCR-normalizing them into editable Markdown, while Markdown import remains direct.

Deliverables:
- Markdown direct-import contract
- OCR-backed import contract for PDF, image, document, spreadsheet, and text formats
- online OCR target: Nanonets OCR-3
- local/offline OCR target: Nanonets OCR2
- OCR provenance model for source file, provider/model, page or sheet, content hash, and confidence when available

Status:
- Planned and disabled
- Lane state: disabled (`feat-ocr-import`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 7: Literature import

Outcome:
- Literature can eventually be selected as an import type and saved with editable metadata, regardless of whether the source was Markdown or OCR-derived.

Deliverables:
- import-modal type selection for literature
- metadata extraction contract for Markdown literature
- metadata extraction contract for OCR-derived literature
- editable metadata approval modal before save
- inspector editing contract for saved literature metadata
- metadata fields for title, authors, venue/publication, year/date, DOI, URL, abstract, and citation string

Status:
- Planned and disabled
- Lane state: disabled (`feat-literature-import`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 8: RAG indexing and retrieval

Outcome:
- The project can eventually index normalized Markdown, including OCR-derived documents, and retrieve relevant chunks through FTS plus additive vector search.

Deliverables:
- Markdown-aware chunking contract
- chunk metadata for document ID, document type, literature metadata reference, heading path, offsets, token estimate, content hash, and chunk text
- online embedding target: Mistral `mistral-embed`
- local embedding target: Qwen3-Embedding-0.6B
- retrieval-card contract for basket promotion

Status:
- Planned and disabled
- Lane state: disabled (`feat-rag-index`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 9: Basic qualitative coding

Outcome:
- The project can eventually support one-code-at-a-time qualitative coding over selected document text, with simple highlights and navigable code summaries.

Deliverables:
- code type in project state and storage/database models
- single-code selection highlight behavior
- `New Folder` support in the project browser
- organizational folders under document sections
- parent-code folders under the code section
- drag-and-drop for folders and codes
- one level of parent/child codes
- inspector code details for selected coded text
- code-focused document view with summary, frequencies, parent/child info, and document excerpts
- coding shortcut row for add/delete code and folder-related coding actions

Status:
- Planned and disabled
- Lane state: disabled (`feat-qual-coding`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 10: Editor basics

Outcome:
- The document editor can eventually provide expected text-editing primitives without mixing them into coding or project taxonomy work.

Deliverables:
- copy selected text
- paste clipboard text
- undo document edits
- redo document edits
- shortcut row for copy, paste, undo, and redo
- command-palette entries for editor basics

Status:
- Planned and disabled
- Lane state: disabled (`feat-editor-basics`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 11: Zotero import

Outcome:
- Zotero becomes the preferred MVP path for importing literature and high-quality metadata into the project literature library.

Deliverables:
- one-way Zotero import option for literature
- in-app or browser-based Zotero login/key workflow
- secure credential storage requirement
- Zotero metadata import into literature metadata
- literature folder treated as a durable project-level literature library that feeds citations, RAG, drafting, and context promotion
- no writeback, bidirectional sync, collection management, or deep-research export into Zotero
- Zotero attached-file import through the standard literature/OCR pipeline

Status:
- Planned and disabled
- Lane state: disabled (`feat-zotero-import`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 12: Citation support

Outcome:
- Drafts can eventually cite literature manually or through model-assisted writing while preserving Pandoc-compatible source citations.

Deliverables:
- manual literature citation insertion
- optional page number or locator entry
- LLM-used literature citation requirement
- Pandoc-compatible citation storage
- document-pane citation rendering as links to literature
- citation action in the document top row next to basket commands and before export

Status:
- Planned and disabled
- Lane state: disabled (`feat-citations`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 13: Export support

Outcome:
- Drafts can eventually export raw Markdown, APA PDF, and APA DOCX with generated reference lists.

Deliverables:
- raw Markdown export
- APA PDF export
- APA DOCX export
- reference list generated from cited literature
- draft author/institution metadata captured on create/import
- APA metadata editing in inspector and export confirmation modal
- CSL/Pandoc scaffolding for MLA, Chicago, and institution-specific formats later

Status:
- Planned and disabled
- Lane state: disabled (`feat-export`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 14: Formatting bar

Outcome:
- The editor can eventually offer familiar formatting controls while still writing semantic Markdown.

Deliverables:
- formatting bar for bold, italic, underline where supported, and heading levels
- direct Markdown syntax insertion/wrapping
- semantic heading controls preferred over manual styling
- formatting shortcut row
- command-palette entries for formatting actions

Status:
- Planned and disabled
- Lane state: disabled (`feat-formatting-bar`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 15: Developer provider configuration

Outcome:
- Developer builds can eventually configure bring-your-own-key and bring-your-own-model providers through command-palette flows only, while Lite builds use fixed cross-platform remote Mistral Small 4 and managed Nanonets OCR-3 profiles.

Deliverables:
- command-palette commands for OpenAI, Claude, Mistral, Nanonets, local OpenAI-compatible endpoint, default provider/model, connection testing, and credential clearing
- developer-version gating so non-developer builds hide and reject credential/provider mutation commands
- Lite distribution mode with fixed remote Mistral Small 4, managed Nanonets OCR-3, and no user API-key setup
- Lite managed Nanonets credentials provided by app-managed remote service infrastructure, not hardcoded into the app, repo, project files, or user keychain
- secure credential-store abstraction for macOS Keychain, Windows Credential Manager/DPAPI-backed storage, and Linux Secret Service/libsecret
- backend provider-router integration for default online provider, default model, and confidential-mode local endpoint
- no dedicated settings window
- no user-editable config file

Status:
- Planned and disabled
- Lane state: disabled (`feat-developer-provider-config`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 16: Desktop packaging for Developer and Lite

Outcome:
- Developer and Lite builds can eventually ship as normal local desktop apps for macOS, Windows, and Linux, with native windows, bundled runtime, local storage, and GitHub Release artifacts.

Deliverables:
- pywebview desktop shell for a native window around the locally served Textual UI
- bundled Python runtime, Exegesis Engine, Textual local server, and SQLite app-data storage
- Briefcase packaging configuration for Developer and Lite variants
- macOS `.dmg`, Windows `.msi`, and Linux Flatpak release targets
- platform app-data directory handling for SQLite, project files, cache, and logs
- loopback-only local server startup with port collision handling
- startup/shutdown coordination across engine, Textual server, pywebview, and SQLite
- GitHub Release artifact collection with checksums
- Developer packaging profile wired to Milestone 15 BYOK/BYOM provider commands
- Lite packaging profile wired to remote Mistral Small 4 and managed Nanonets OCR-3 without user credential setup

Status:
- Planned and disabled
- Lane state: disabled (`feat-desktop-packaging`)
- This milestone is spec scaffolding only until explicitly activated

## Milestone 17: CoP Launch Gate

Outcome:
- Lite builds can eventually grant initial Community of Practice users unlimited Lite course access while tracking finite Nanonets online OCR pages through a hosted Lite License Gateway.

Deliverables:
- initial CoP unlimited Lite course license with no seat cap
- Developer/Lite boundary that prevents Developer builds from using hosted Lite workflows
- Lite-only hosted License Gateway for license invites, claim, refresh, managed provider proxy, Paddle webhooks, and Nanonets page state
- Nanonets page ledger with 150-page initial CoP balance
- fixed Nanonets top-up packages of 150, 500, and 1000 pages
- Paddle webhook contract for paid top-ups
- transaction-safe reservation/consumption/release/refund rules for Nanonets OCR jobs
- Lite import-window balance and estimated-page display before OCR-backed import
- future hooks for Tally request intake, manual approval, and Claude cowork license-link generation

Status:
- Planned and disabled
- Lane state: disabled (`feat-cop-lite-licensing`)
- This milestone is spec scaffolding only until explicitly activated
