# Exegesis MVP Roadmap

This file is the canonical milestone tracker for the staged Exegesis MVP migration.

Detailed milestone breakdown lives in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/milestones.md`.
Detailed lane/task mapping lives in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/TASKS.md`.
Sprint activation plan lives in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/MVP_SPRINT_PLAN.md`.
Future import, OCR, literature metadata, and RAG specs live in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/FUTURE_IMPORT_RAG_SPEC.md`.
Future summer MVP feature specs live in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/FUTURE_MVP_FEATURES_SPEC.md`.
Post-MVP feature specs live in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/POST_MVP_FEATURES_SPEC.md`.

## Product target

The Textual writing client is the MVP product target.

Current engine work is the enabling path for that client, not a separate product roadmap.
The CLI remains first-class while Textual stays scaffolded and disabled.

## Milestone 1: Standing shell

Status: standing (mockup only)

Scope:
- define the 5-pane Textual shell
- lock focus model and keyboard shortcuts
- define shortcut bar and command palette scaffold
- stand up the shell as a believable writing-environment mockup
- keep UI lanes disabled for engine integration until the engine contract is ready

Exit criteria:
- shell boundaries are documented and scaffolded
- the shell stands in Textual/browser as a stable mockup baseline
- the shell is explicitly not yet wired to live engine state/actions
- pane ownership is clear
- UI lanes remain disabled until explicitly activated

## Milestone 2: Core pane interactions

Status: planned

Scope:
- define project/document/workflow/basket/inspector interactions
- define the selection model and inspector-follow-selection rule
- define command palette coverage for the MVP loop

Exit criteria:
- pane interaction contract is documented
- engine contract exposes the state/actions those panes will need

## Milestone 3: Real workflow loop

Status: in progress

Scope:
- expose canonical engine state models
- keep retrieval/search FTS-first and structured
- expose plan/draft/revise/apply-reject through the canonical app service
- preserve CLI compatibility while the package/layout migration lands
- move A2UI contracts into `shared` while keeping renderers outside `shared`

Lane mapping:
- `feat-retrieval-fts`: retrieval/search
- `feat-engine-runs`: plan/draft/revise/apply-reject workflow actions
- `feat-context-storage`: persistent basket/document/session state
- `feat-a2ui-contract`: shared card/action contracts and selection models
- `feat-commands`: CLI compatibility and migration-safe entrypoints

Exit criteria:
- engine can persist project/document/basket/session state
- retrieval returns structured results suitable for basket promotion
- plan/draft/revise/apply-reject flows operate through the canonical app service
- CLI can still execute the MVP loop while Textual remains disabled

## Milestone 4: Dogfooding readiness

Status: planned

Scope:
- finish persistence and audit hooks needed for real writing sessions
- keep command palette/useful workflow actions mapped in the engine contract now
- reserve UI polish and keyboard-first validation for the disabled Textual lanes later

Exit criteria:
- engine state survives repeated sessions
- workflow artifacts are stable enough to support real writing use
- the future client surface is unblocked by engine contract gaps

## Milestone 5: YC demo readiness

Status: planned

Scope:
- create one reproducible demo flow for retrieve -> basket -> plan -> revise -> apply
- keep this as cross-lane/integrator work rather than a dedicated feature lane

Exit criteria:
- one clean 60-180 second demo path exists
- the app reads as a writing environment rather than a terminal trick

## Milestone 6: OCR import

Status: planned, disabled

Scope:
- define typed import support for Markdown and OCR-backed source files
- keep Markdown import direct without OCR
- route future non-Markdown imports through OCR into normalized editable Markdown
- target Nanonets OCR-3 online and Nanonets OCR2 local/offline
- preserve OCR provenance for later audit and RAG indexing

Lane mapping:
- `feat-ocr-import`: disabled until explicitly activated

Exit criteria:
- OCR import contract is specified
- supported source formats and provenance fields are defined
- no runtime OCR behavior is active until the lane is enabled

## Milestone 7: Literature import

Status: planned, disabled

Scope:
- treat literature as an import type selected inside the import modal
- run metadata extraction for Markdown literature and OCR-derived literature
- prefer deterministic metadata signals before model-assisted candidate extraction
- support editable literature metadata approval before save and later inspector editing

Lane mapping:
- `feat-literature-import`: disabled until explicitly activated

Exit criteria:
- literature metadata contract is specified
- approval/editing flow is specified
- no runtime metadata extraction behavior is active until the lane is enabled

## Milestone 8: RAG indexing and retrieval

Status: planned, disabled

Scope:
- index normalized Markdown, including OCR-derived documents
- define chunk records with source, type, metadata, offsets, token estimates, and content hashes
- keep FTS as the retrieval baseline while vector retrieval becomes additive
- target Mistral `mistral-embed` online and Qwen3-Embedding-0.6B locally

Lane mapping:
- `feat-rag-index`: disabled until explicitly activated

Exit criteria:
- chunking and embedding contract is specified
- FTS-plus-vector retrieval shape is specified
- no runtime RAG behavior is active until the lane is enabled

## Milestone 9: Basic qualitative coding

Status: planned, disabled

Scope:
- add first-class qualitative codes to project state and storage
- apply one code to selected text with a simple color highlight
- add `New Folder` in the project browser
- make document-section folders organizational and code-section folders parent codes
- support draggable folders and codes with one level of parent codes
- show code details, parent/child info, frequencies, and clickable document appearances in the inspector and code view
- add dedicated coding shortcuts for adding/deleting codes and folder-related coding actions

Lane mapping:
- `feat-qual-coding`: disabled until explicitly activated

Exit criteria:
- qualitative coding contract is specified
- project/code folder semantics are specified
- no runtime coding behavior is active until the lane is enabled

## Milestone 10: Editor basics

Status: planned, disabled

Scope:
- add copy, paste, undo, and redo support
- keep editor basics separate from coding/project taxonomy behavior
- add dedicated copy/paste/undo/redo shortcut row
- register editor basics in the command palette

Lane mapping:
- `feat-editor-basics`: disabled until explicitly activated

Exit criteria:
- editor basics contract is specified
- shortcut and command-palette coverage is specified
- no runtime editor basics behavior is active until the lane is enabled

## Milestone 11: Zotero import

Status: planned, disabled

Scope:
- make Zotero the preferred MVP path for importing literature and high-quality metadata
- add Zotero as a one-way literature import source
- support Zotero login/key workflow through in-app or browser-based authentication
- store Zotero credentials securely
- import Zotero metadata and attached literature files through the normal literature/OCR import pipeline
- treat the project literature folder as a durable project-level literature library, not just a loose file list
- use Zotero metadata as authoritative initial metadata so Zotero attachments skip the normal starting metadata classification flow after OCR
- explicitly defer writeback, bidirectional sync, collection management, and deep-research export into Zotero

Lane mapping:
- `feat-zotero-import`: disabled until explicitly activated

Exit criteria:
- one-way Zotero import/auth contract is specified
- Zotero metadata-to-literature mapping is specified
- Zotero attachment import skips initial metadata classification when Zotero metadata is complete
- no runtime Zotero behavior is active until the lane is enabled

## Milestone 12: Citation support

Status: planned, disabled

Scope:
- insert manual literature citations with optional page numbers or locators
- require literature used by the LLM to be cited in generated output
- store citations in Pandoc-compatible Markdown while rendering them as links to literature in the document pane
- place citation in the document top row next to basket commands and before export

Lane mapping:
- `feat-citations`: disabled until explicitly activated

Exit criteria:
- citation storage/rendering contract is specified
- manual and model-used citation behavior is specified
- no runtime citation behavior is active until the lane is enabled

## Milestone 13: Export support

Status: planned, disabled

Scope:
- export raw Markdown, APA PDF, and APA DOCX
- include reference lists from cited literature
- capture draft author/institution metadata on create/import
- keep APA identity metadata editable in the inspector and export confirmation modal
- scaffold CSL/Pandoc-backed future formats such as MLA, Chicago, and institution-specific styles

Lane mapping:
- `feat-export`: disabled until explicitly activated

Exit criteria:
- export format contract is specified
- APA metadata and reference-list requirements are specified
- no runtime export behavior is active until the lane is enabled

## Milestone 14: Formatting bar

Status: planned, disabled

Scope:
- add basic Markdown formatting controls for bold, italic, underline where supported, and heading levels
- add image-as-figure insertion with title, caption, alt text, and project-managed asset references
- add title/caption metadata for Markdown tables so APA export can render table titles and notes
- insert Markdown syntax rather than creating WYSIWYG document state
- prefer semantic headings over manual visual formatting
- add dedicated formatting shortcut row and command-palette entries

Lane mapping:
- `feat-formatting-bar`: disabled until explicitly activated

Exit criteria:
- formatting bar contract is specified
- figure/table metadata authoring contract is specified
- formatting shortcut behavior is specified
- no runtime formatting behavior is active until the lane is enabled

## Milestone 15: Developer provider configuration

Status: planned, disabled

Scope:
- add developer-version-only command-palette flows for bring-your-own-key and bring-your-own-model setup
- support a Lite distribution mode that uses remote Mistral Small 4 and managed Nanonets OCR-3 by default with no user key setup
- configure OpenAI, Claude, Mistral, Nanonets, and local OpenAI-compatible endpoint credentials
- store all secrets securely through the detected OS credential store
- use macOS Keychain, Windows Credential Manager/DPAPI-backed storage, or Linux Secret Service/libsecret as appropriate
- set default online provider and default model without a dedicated settings window or config file
- test current connection and clear stored credentials
- hide and reject developer provider mutation commands outside developer builds
- keep Lite managed Nanonets credentials cross-platform in app-managed remote service infrastructure, not hardcoded into the app, repo, project files, or user keychain

Lane mapping:
- `feat-developer-provider-config`: disabled until explicitly activated

Exit criteria:
- developer-only provider command contract is specified
- Lite remote Mistral Small 4 provider contract is specified
- Lite managed Nanonets OCR-3 provider contract is specified
- cross-platform secure credential storage contract is specified
- backend provider-router integration is specified
- no runtime developer provider configuration behavior is active until the lane is enabled

## Milestone 16: Desktop packaging for Developer and Lite

Status: planned, disabled

Scope:
- package Exegesis as a normal local desktop app with no terminal or localhost exposure for end users
- support both Developer and Lite distributions
- target macOS `.dmg`, Windows `.msi`, and Linux Flatpak release artifacts
- bundle Python runtime, Exegesis Engine, Textual local server, pywebview native shell, and SQLite local storage
- initialize app data and SQLite from platform-appropriate user app data directories
- use Briefcase for platform packaging and GitHub Releases for binary distribution
- keep Developer builds wired for Milestone 15 BYOK/BYOM provider configuration
- keep Lite builds wired for remote Mistral Small 4 and managed Nanonets OCR-3 without user credential setup
- coordinate startup and shutdown across engine, local server, pywebview, and SQLite

Lane mapping:
- `feat-desktop-packaging`: disabled until explicitly activated

Exit criteria:
- Developer and Lite packaging architecture is specified for macOS, Windows, and Linux
- desktop runtime startup/shutdown contract is specified
- platform app-data and SQLite packaging behavior is specified
- Briefcase/GitHub Release artifact flow is specified
- no runtime packaging behavior is active until the lane is enabled

## Milestone 17: CoP Launch Gate

Status: planned, disabled

Scope:
- add initial Community of Practice unlimited Lite course access with no seat cap
- keep Developer builds fully separate from hosted Lite workflows
- add a Lite-only hosted License Gateway for license claim/refresh, managed Lite provider access, Paddle webhooks, and Nanonets page-credit state
- route Lite remote Mistral Small 4 and Nanonets OCR-3 through gateway-managed credentials
- keep Nanonets online OCR page-metered with a 150-page default balance for the initial CoP
- allow fixed top-up packages of 150, 500, and 1000 pages through manual admin top-up and future Paddle checkout
- specify ledger-based Nanonets page accounting, transaction-safe reservations, and idempotent job/webhook handling
- show Nanonets page balance and estimated import page count in the Lite import window before OCR-backed import
- define future Tally/manual approval/Claude cowork license-generation hooks without implementing them

Lane mapping:
- `feat-cop-lite-licensing`: disabled until explicitly activated

Exit criteria:
- Lite-only hosted License Gateway contract is specified
- Developer/Lite boundary is specified so Developer never calls hosted Lite workflows
- initial CoP Lite access and course-access rules are specified
- Nanonets page ledger, fixed top-ups, Paddle webhook, and import-window balance behavior are specified
- no runtime licensing, gateway, Paddle, OCR metering, or shell behavior is active until the lane is enabled

## Milestone 18: Browser PDF Capture Extension

Status: post-MVP planned, disabled

Scope:
- add a minimal browser extension for Chrome, Firefox, and Safari that only sends the current PDF tab to Exegesis
- keep the extension as a capture button, not a Zotero clone, translator system, scraper, or browser-side product surface
- let Exegesis own direct/authenticated fetch handling, import, OCR, metadata extraction, project placement, deduping, and indexing
- use loopback handoff first, with custom protocol/native messaging hooks available if browser security requires them
- include extension artifacts in desktop packaging and guide browser-required install/enable flows without bypassing browser security prompts
- support direct-fetchable PDFs first and preserve a later hook for browser-assisted authenticated PDF relay

Lane mapping:
- `feat-browser-pdf-capture`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- Chrome, Firefox, and Safari capture flows are specified
- extension popup behavior and PDF detection policy are specified
- Exegesis handoff contract and pending browser import record are specified
- packaging/install integration and browser security limits are specified
- no runtime browser extension, local capture endpoint, native bridge, or import behavior is active until the lane is enabled


## Milestone 19: Multi-Agent Open Access Deep Research

Status: post-MVP planned, disabled

Scope:
- add a local-first, multi-agent source discovery workflow for possible literature and web sources
- search the current Exegesis project first, then selected other Exegesis projects, then configured open web and PDF/full-text scholarly providers
- use a LangChain Open Deep Research-inspired supervisor/researcher architecture without generating final reports, summaries, or synthesis
- support Tavily as the default agentic web provider when configured, with Brave, Exa, and PDF/full-text-capable scholarly providers as additive adapters
- normalize, dedupe, rank, and explain candidate sources before user review
- present source candidates as an import batch that enters the standard import/OCR/literature/RAG pipeline

Lane mapping:
- `feat-open-access-deep-research`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- local-first project search plus open web provider fan-out are specified
- research supervisor, provider adapters, candidate normalization, dedupe, ranking, and audit models are specified
- source batch review and standard import-protocol handoff are specified
- privacy/project-mode/credential boundaries are specified
- no runtime web search, multi-agent orchestration, provider API calls, source ranking, or import-batch behavior is active until the lane is enabled

## Milestone 20: Quantitative Analysis

Status: post-MVP planned, disabled

Scope:
- add `Datasets` as a first-class project browser section
- import CSV files only, with dataset provenance and row/column guardrails
- auto-detect variables as categorical, ordinal, or scale and allow user overrides in the dataset document view
- show raw data in the document pane while the inspector configures analyses
- support descriptive statistics, frequency and contingency tables, t-test, ANOVA, chi-squared, and linear correlation
- generate simple markdown result tables plus bar charts, density curves, and scatter plots
- show p-values and effect sizes for inferential tests with compact small/medium/large guidance
- let users build an ordered analysis sequence and save it as a project summary

Lane mapping:
- `feat-quant-analysis`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- dataset import, variable typing, analysis contracts, chart artifacts, sequence transcript, and summary export are specified
- statsmodels/pandas/numpy/matplotlib execution boundaries are specified
- local-only privacy/provider boundaries are specified
- no runtime CSV import, statistical testing, chart generation, dataset UI, or analysis-summary behavior is active until the lane is enabled

Current operational narrowing:
- Treat the canonical closure target as one engine-first demo path:
  - open project/document
  - retrieve relevant material
  - promote or gather context into the basket
  - produce a plan or revision
  - preview and apply or reject a patch
  - persist the updated document/session state
  - continue working
- Active lane work should be judged against whether it directly advances that path.
- Improvements that do not make that path more real are second-order and should wait until the demo loop stands.

## Active now
- `feat-commands`
- `feat-context-storage`
- `feat-retrieval-fts`
- `feat-a2ui-contract`
- `feat-engine-runs`

## Defined but disabled
- `feat-console-shell`
- `feat-console-workflow`
- `feat-ocr-import`
- `feat-literature-import`
- `feat-rag-index`
- `feat-qual-coding`
- `feat-editor-basics`
- `feat-zotero-import`
- `feat-citations`
- `feat-export`
- `feat-formatting-bar`
- `feat-developer-provider-config`
- `feat-desktop-packaging`
- `feat-cop-lite-licensing`
- `feat-browser-pdf-capture`
- `feat-open-access-deep-research`
- `feat-quant-analysis`

## Retired planning targets
- `feat-ux-flow`
- `feat-console`

These legacy lanes are superseded by the staged engine/client/shared split and should not be restarted.
