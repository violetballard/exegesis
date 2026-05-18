# Exegesis MVP Milestones

This file expands the canonical roadmap in `/Users/doctor-violet/projects/exegesis/ROADMAP.md`.

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

Notebook context compaction:
- implement against `/Users/doctor-violet/projects/exegesis/docs/NOTEBOOK_CONTEXT_COMPACTION_SPEC.md`
- preserve raw notebook transcript history while assembling compacted model requests
- keep pinned entries, unresolved rewrite cards, current document context, and basket source-type labels verbatim
- store compaction blocks with source entry IDs, token counts, validation status, and restore support

Status:
- In progress

## Milestone 4: Dogfooding readiness

Outcome:
- The engine contract and the future Textual client surface are stable enough for real writing sessions.

Deliverables:
- persistence for document/basket/session state
- save-to-project workflow output paths
- readable, durable workflow cards
- notebook compaction cards and audit state for long sessions
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

## Milestone 5A: MVP trust substrate

Outcome:
- After the demo path stands, Exegesis gains the trust substrate needed for real MVP use before broad import/RAG/coding expansion.

Deliverables:
- encrypted SQLite-backed storage for durable app/project metadata, sessions, workflow artifacts, provenance, audit events, notebook compaction records, and generated A2UI promotion candidates
- portable Markdown documents and assets remain outside opaque storage where appropriate
- provenance/tracking for retrieval hits, query/filter/ranking metadata, basket promotion, model request context assembly, generated outputs, rewrite proposals, patch apply/reject decisions, citations, imports, notebook compactions, and A2UI-generated surface candidates
- full MVP A2UI protocol compatibility beyond the current shim: handshake, capability negotiation, primitive blocks, known cards, unknown-card fallback, typed action allowlist, payload validation, streaming event shape, and engine-side policy revalidation
- generated A2UI drafts captured as reviewable CoP/beta promotion candidates with source prompt/context, model/provider, client capability set, allowed actions, usage outcome, user feedback, review status, and promotion status

Status:
- MVP planned and disabled until Milestone 5 stands
- This is a post-demo MVP gate before Milestone 6 OCR/import/RAG activation
- Uses the existing engine lanes when activated rather than starting speculative UI polish

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
- Zotero attachments skip the normal starting metadata classification flow when Zotero metadata is complete
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
- image-as-figure insertion with title, caption, alt text, and project-managed asset reference
- Markdown table title/caption metadata for APA-ready export
- document and selection word counts in the inspector alongside LLM token estimates
- document and selection word counts in draft/rewrite request context so the LLM can follow human length instructions
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
- Developer builds can configure BYOK/BYOM providers through command-palette actions while Lite builds use managed defaults.

Deliverables:
- provider setup commands for OpenAI, Claude, Mistral, Nanonets, and local OpenAI-compatible endpoints
- secure OS credential-store abstraction
- default online provider plus model and supported reasoning-level selection
- connection test and clear-stored-credentials commands
- Developer/Lite command visibility and backend rejection rules

Status:
- Planned and disabled
- Lane state: disabled (`feat-developer-provider-config`)

## Milestone 16: Project Transfer Export/Import

Outcome:
- Users can move Exegesis projects between machines with a portable zip archive without transferring credentials or machine-bound license state.

Deliverables:
- project zip archive manifest with schema version, app version, project ID, content hashes, and export timestamp
- export coverage for documents, basket, summaries, transcripts, literature metadata, citations, codes, datasets, provenance, and project settings
- explicit exclusion of credentials, provider keys, local endpoints, managed Lite secrets, license tokens, and machine caches
- import preview with validation, conflict handling, and safe restore behavior
- licensing boundary: licenses are per user/account, not per machine or project archive

Status:
- MVP planned and disabled
- Lane state: disabled (`feat-project-transfer`)

## Milestone 17: Desktop packaging for Developer and Lite

Outcome:
- Developer and Lite can eventually ship as normal desktop apps around the local Textual UI while remaining separate from macOS-only Studio Workstation.

Deliverables:
- pywebview desktop shell around the local Textual server
- bundled Python runtime, SQLite app data, local server startup/shutdown, and GitHub Release artifacts
- Briefcase cross-platform packaging
- packaged Developer/Lite executables that do not depend on system Python
- Cloudflare R2-backed update checks, unobtrusive update button, and `Check for Updates` menu command
- required-update gate that blocks confidential project creation/open until the app is fully updated
- Developer profile wired to BYOK/BYOM provider commands
- Lite profile wired to hosted License Gateway and managed provider access
- Lite local Python services called directly inside the packaged app, with the hosted License Gateway reserved for managed remote credentials, license refresh, Paddle, and Nanonets accounting
- cross-platform Developer/Lite packaging plan independent from Studio

Status:
- Planned and disabled
- Lane state: disabled (`feat-desktop-packaging`)

## Milestone 18: Lite Website Licensing and CoP Launch Gate

Outcome:
- Lite can support individual paid licenses, Studio/Pro inherited Lite access, course licenses, initial CoP access, Nanonets page credits, and project-transfer-safe per-user licensing through the hosted License Gateway.

Deliverables:
- individual paid Lite purchase flow through the website and Paddle
- Studio and Pro subscription rules that include Lite access for secondary-machine use
- course licensing flow with one self-serve student link distributed by the instructor
- Tally intake form accessible through MCP for Claude cowork-assisted course license classification and manual approval workflow
- initial CoP unlimited Lite course access
- hosted License Gateway for license claim, refresh, managed Mistral/Nanonets access, Paddle webhooks, and Nanonets page state
- 150 default Nanonets pages plus fixed top-ups for 150, 500, and 1000 pages
- Studio 250-page monthly managed cloud OCR bucket and Pro 500-page monthly managed cloud OCR bucket
- Pro BYOK/BYOM provider configuration for OpenAI, Claude, Mistral, and local OpenAI-compatible backends with provider/model/reasoning selection for non-confidential projects only
- edition system tiers: Lite 8 GB, Studio 8 GB with managed cloud OCR, Pro 16 GB, local OCR when current memory allows, and 128 GB for local confidential mode
- Pro-only entitlement gating for Quantitative Analysis and Advanced Qualitative Coding Visualizations
- import-window Nanonets balance and estimated-page display
- licensing boundary: per user/account, not per machine, including Studio/Pro-derived Lite access and never embedded in project transfer archives

Status:
- Planned and disabled
- Lane state: disabled (`feat-cop-lite-licensing`)
- This is the launch gate before starting the CoP

## Milestone 19: Browser PDF Capture Extension

Outcome:
- Exegesis can eventually capture the current browser PDF from Chrome, Firefox, or Safari and hand it to the normal import/OCR/metadata pipeline.

Deliverables:
- minimal WebExtension action: `Add PDF to Exegesis`
- PDF-tab detection, popup states, and handoff contract
- local capture endpoint/custom protocol/native messaging fallback boundaries
- direct-fetch-first import handoff and future authenticated-PDF relay hook

Status:
- Post-MVP planned and disabled
- Lane state: disabled (`feat-browser-pdf-capture`)

## Milestone 20: Python Backend Sidecar Bridge

Outcome:
- Studio can eventually supervise a signed, sandboxed macOS XPC sidecar bridge for Python-backed features.

Deliverables:
- signed-app-only XPC/RPC handler contracts
- health, readiness, version, feature manifest, and shutdown handlers
- signed bundled Python worker/XPC service packaging inside the Studio `.app`
- Workstation launch, monitor, restart, compatibility, signature, entitlement, shutdown, and log-redaction rules
- requirement that future Studio Python features expose behavior through sidecar handlers when applicable
- boundary that Python/Textual Lite is packaged separately and calls the shared Python service layer directly

Status:
- Post-MVP planned and disabled
- Lane state: disabled (`feat-python-sidecar-api`)

## Milestone 21: Native Workstation and Signed Distribution

Outcome:
- Exegesis Studio can eventually ship as a signed, notarized macOS-native Workstation that bundles and supervises the sidecar.

Deliverables:
- native macOS SwiftUI Workstation lifecycle
- native settings for Light, Dark, and Auto appearance modes
- STTextView editor foundation evaluation with plugins for annotations, Markdown highlighting, diffs, citations, figures, and tables
- bundled sidecar launch, health monitoring, compatibility checks, restart, and shutdown
- Workstation memory tiers and OCR routing: Studio 8 GB minimum, Pro 16 GB minimum, local OCR when current memory allows, and 128 GB for local confidential mode
- MLX Swift local confidential runtime with selectable quant tiers from 128 GB Q4 through 512 GB F16
- Pro local model manager for confidential runtime model downloads, storage, deletion, checksums, and tier selection
- licensed R2-backed multipart downloads for confidential model quants
- R2-backed app update checks, unobtrusive update button, and `Check for Updates` menu command
- required-update gate before confidential project creation/open
- creation-time immutable confidential project mode and confidential import boundaries
- macOS signing, notarization, dmg/release artifact, checksums, and web distribution
- release manifest, clean install, manual update/upgrade, and project data preservation
- explicit exclusion of Windows/Linux Studio signing and packaging

Status:
- Post-MVP planned and disabled
- Lane state: disabled (`feat-native-workstation`)
- This sprint is expected to be interactive rather than broad daemon-only work

## Milestone 22: Multi-Agent Open Access Deep Research

Outcome:
- Studio Pro can eventually discover possible open-access sources by searching Exegesis projects first and then the open web, handing deduped candidates to the import pipeline.

Deliverables:
- local-first project search and provider fan-out
- Tavily, Brave, Exa, and PDF/full-text-capable scholarly source adapters
- LangChain-inspired supervisor/researcher source discovery without synthesis/report writing
- candidate normalization, dedupe, ranking, provenance, and audit records
- native Studio SwiftUI source batch review and standard import-protocol handoff

Status:
- Studio Pro planned and disabled
- Lane state: disabled (`feat-open-access-deep-research`)

## Milestone 23: Quantitative Analysis

Outcome:
- Studio Pro can eventually support lean CSV-based quantitative analysis as a first-class project workflow.

Deliverables:
- native Studio `Datasets` project browser section
- Pro-only `pro_feature_access` requirement
- CSV-only dataset import with provenance, row/column guardrails, and project storage
- variable type auto-detection and editable overrides
- lean dataset preparation for filtering, row/column removal, one-hot encoding, manual categorical/ordinal quantization, and keyed dataset unions
- descriptive statistics, frequency and contingency tables, t-test, ANOVA, chi-squared, and linear correlation
- p-values, effect sizes, and small/medium/large guidance
- basic charts and saveable analysis sequences
- native `StatsCore` Swift package, `StatsBridge` C shim, and IMSL C Numerical Library backend isolation
- IMSL vendor feasibility checklist for macOS, Apple Silicon, redistribution, linking mode, and Swift/Xcode use

Status:
- Studio Pro planned and disabled
- Lane state: disabled (`feat-quant-analysis`)

## Milestone 24: Advanced Qualitative Coding Visualizations

Outcome:
- Studio Pro can eventually provide advanced qualitative coding visualization and codebook tools after basic coding exists.

Deliverables:
- browsable code graphs for parent/child structures, co-occurrence, and document/code relationships
- Pro-only `pro_feature_access` requirement
- code/document matrices and distribution tables
- visual comparisons across documents, document types, participants, folders, and codes
- codebook generation from code definitions, frequencies, examples, and audit history
- native Studio SwiftUI browse, filter, compare, and export surfaces

Status:
- Studio Pro conceptual and disabled
- Lane state: disabled (`feat-advanced-qual-visuals`)

## Milestone 25: Confidential Collaboration

Outcome:
- After Studio and the Pro feature families are in place, Exegesis can eventually support confidential shared project work for teams, cohorts, and research groups.

Deliverables:
- conceptual threat model for shared confidential projects
- shared project membership, invitations, roles, permissions, and audit-event concepts
- encrypted/local-first sync or secure collaboration-service architecture decision
- collaboration data concepts for operations, comments, review decisions, conflicts, sync checkpoints, and device identity
- account-based collaboration entitlement rules, including Lite participation for higher-licensed users on secondary machines
- native Studio SwiftUI collaboration surfaces for sharing status, members, activity, review, comments, conflicts, and sync health
- clear boundary between Studio-only collaboration management and constrained Lite participation
- activation prerequisites for splitting this work into smaller implementation lanes

Status:
- Post-Pro conceptual and disabled
- Lane state: disabled (`feat-confidential-collaboration`)
- This milestone is a later company-wide collaboration design sprint, not near-term implementation work

## Milestone 26: Native iPad Lite

Outcome:
- Exegesis can eventually offer a native iPadOS Lite client for eligible users, after enough Studio/Pro Swift-native infrastructure exists to avoid depending on the macOS Python sidecar model.

Deliverables:
- iPadOS Lite product boundary and secondary-machine entitlement model
- Python-backed or macOS-sidecar-dependent workflow inventory for Lite behavior that must become Swift-native, gateway-backed, deferred, or unavailable on iPad
- reuse plan for mature Studio/Pro Swift-native editor, project, import, license, and collaboration components
- project archive import/export, offline cache, license refresh, and file provider/share sheet boundaries
- constrained iPad Lite collaboration participation without Studio-only management or Pro-only feature surfaces
- activation prerequisites for splitting this long-term conceptual client work into implementation lanes

Status:
- Long-term conceptual and disabled
- Lane state: disabled (`feat-ipad-native-lite`)
- This milestone comes after confidential collaboration and should wait for mature Studio/Pro native code to reuse
