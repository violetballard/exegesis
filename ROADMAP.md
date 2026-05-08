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
- add command-palette configuration for Developer BYOK/BYOM providers
- support OpenAI, Claude, Mistral, Nanonets, and local OpenAI-compatible endpoints
- store keys securely through the OS credential-store abstraction
- keep Lite managed provider defaults separate from Developer keys

Lane mapping:
- `feat-developer-provider-config`: disabled until explicitly activated

Exit criteria:
- provider commands, credential storage, provider defaults, connection tests, and clear-credential behavior are specified
- Developer and Lite provider boundaries are specified
- no runtime provider configuration behavior is active until the lane is enabled

## Milestone 16: Project Transfer Export/Import

Status: MVP planned, disabled

Scope:
- add portable project export/import through a zip archive so users can move projects between machines
- include project documents, basket entries, metadata, citations, codes, datasets, summaries, transcripts, literature records, provenance, and local project settings
- exclude credentials, provider keys, local endpoints, managed Lite secrets, license refresh tokens, and machine-specific caches
- include a manifest, schema version, content hashes, archive validation, and import preview before restore
- support conflict handling for importing into an existing project or onto a machine that already has a project with the same identity
- integrate with licensing: licenses are per user/account, not per machine and not bundled into the zip

Lane mapping:
- `feat-project-transfer`: disabled until explicitly activated as an MVP support feature

Exit criteria:
- export/import archive format, validation, preview, and restore rules are specified
- credential/license exclusion and per-user licensing boundaries are specified
- no runtime project export/import behavior is active until the lane is enabled

## Milestone 17: Desktop packaging for Developer and Lite

Status: planned, disabled

Scope:
- package Developer and Lite as normal local desktop apps around the locally served Textual UI
- use pywebview, bundled Python runtime, SQLite app data, local server startup/shutdown, and GitHub Release artifacts
- keep Lite managed-provider secrets outside the bundle and routed through the hosted License Gateway
- keep Developer builds wired to Milestone 15 BYOK/BYOM provider configuration
- keep cross-platform Developer/Lite packaging separate from the later macOS-only Studio Workstation

Lane mapping:
- `feat-desktop-packaging`: disabled until explicitly activated

Exit criteria:
- Developer and Lite packaging architecture is specified
- local runtime startup, shutdown, storage, release artifact, and profile boundaries are specified
- no runtime desktop packaging behavior is active until the lane is enabled

## Milestone 18: Lite Website Licensing and CoP Launch Gate

Status: planned, disabled

Scope:
- add individual paid Lite licensing through the website and Paddle
- add Studio and Pro subscription license inheritance so active Studio/Pro subscribers also receive Lite access for secondary machines
- add course licensing through a single self-serve student link that instructors can give to enrolled students
- add a course-license request workflow through a Tally form that Claude cowork can access through MCP for classification, preparation, and manual approval support
- preserve the initial CoP unlimited Lite course access path
- keep Nanonets online OCR page credits separate from course or Lite access
- keep the hosted License Gateway as the Lite-only place for license claim/refresh, managed Mistral/Nanonets access, Paddle webhooks, and Nanonets page-credit state
- make project transfer license-safe: imported project zips require the current user to have a valid license, but licenses are never machine-bound or included in project archives

Lane mapping:
- `feat-cop-lite-licensing`: disabled until explicitly activated as the CoP launch gate

Exit criteria:
- individual paid Lite, Studio/Pro inherited Lite access, course licensing, initial CoP access, and Nanonets page-credit rules are specified
- Paddle website purchase, course-license link, Tally/MCP approval workflow, and License Gateway contracts are specified
- per-user licensing, subscription inheritance, and project-transfer boundaries are specified
- no runtime licensing, gateway, Paddle, OCR metering, or shell behavior is active until the lane is enabled

## Milestone 19: Browser PDF Capture Extension

Status: post-MVP planned, disabled

Scope:
- add a tiny Chrome, Firefox, and Safari browser extension that sends the current PDF tab to Exegesis
- keep the extension as a capture button only; Exegesis owns import, OCR, metadata, dedupe, and indexing
- package browser-extension artifacts with the desktop app where browser security rules allow it

Lane mapping:
- `feat-browser-pdf-capture`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- browser detection, handoff contract, packaging, and import handoff are specified
- no runtime browser extension, local capture endpoint, native bridge, or import behavior is active until the lane is enabled

## Milestone 20: Python Backend Sidecar API

Status: post-MVP planned, disabled

Scope:
- add a localhost-only FastAPI sidecar for Python-backed features
- package the sidecar as a macOS PyInstaller binary for Studio Workstation supervision
- include health, readiness, version, feature manifest, shutdown, local auth, request limits, log redaction, and sidecar lifecycle contracts
- require future Studio Python features to expose Workstation-facing behavior through the sidecar when applicable

Lane mapping:
- `feat-python-sidecar-api`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- sidecar endpoint, schema, security, lifecycle, packaging, and supervision contracts are specified
- macOS Studio sidecar packaging expectations are specified
- no runtime sidecar API or binary packaging behavior is active until the lane is enabled

## Milestone 21: Native Workstation and Signed Distribution

Status: post-MVP planned, disabled

Scope:
- define the macOS-only native Workstation, branded as Studio, after the sidecar milestone
- package the native SwiftUI interface, project storage, and Milestone 20 sidecar into a signed and notarized macOS distribution
- evaluate STTextView as the preferred native editor foundation, with plugins for annotations, Markdown highlighting, diffs, citations, figures, and tables
- ship through web distribution with checksums, release manifest, clean install, update/manual upgrade, crash/diagnostic, and data preservation guidance
- remove Windows and Linux signing from this milestone; those are not Studio targets
- keep this as a likely interactive sprint rather than broad daemon-driven packaging work

Lane mapping:
- `feat-native-workstation`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- macOS Studio lifecycle, signing, notarization, distribution, update, and sidecar supervision are specified
- native editor foundation and STTextView plugin expectations are specified at a conceptual level
- Windows/Linux Studio signing and packaging are out of scope
- no runtime native Workstation, signing, updater, website distribution, or sidecar bundle behavior is active until the lane is enabled

## Milestone 22: Multi-Agent Open Access Deep Research

Status: Studio Pro planned, disabled

Scope:
- add local-first multi-agent source discovery after Studio is available
- search current and selected Exegesis projects first, then open web/PDF-capable providers such as Tavily, Brave, Exa, and scholarly full-text/PDF sources
- present deduped candidates as a reviewable source batch for the standard import protocol
- avoid automated synthesis/report writing; the feature finds sources for user review and Exegesis-supported analysis
- implement the review/control surface only in Studio's native SwiftUI interface

Lane mapping:
- `feat-open-access-deep-research`: disabled until explicitly activated after Studio is available

Exit criteria:
- local-first project search, provider fan-out, source normalization, dedupe, ranking, audit, and import-batch contracts are specified
- privacy/project-mode/credential boundaries are specified
- no runtime web search, multi-agent orchestration, provider API calls, ranking, or import-batch behavior is active until the lane is enabled

## Milestone 23: Quantitative Analysis

Status: Studio Pro planned, disabled

Scope:
- add first-class CSV dataset import, variable typing, lean statistics, basic charts, and saveable analysis sequences after Studio is available
- support descriptive statistics, frequency and contingency tables, t-test, ANOVA, chi-squared, and linear correlation
- show p-values, effect sizes, and compact small/medium/large guidance
- implement dataset views, analysis configuration, and result sequences only in Studio's native SwiftUI interface

Lane mapping:
- `feat-quant-analysis`: disabled until explicitly activated after Studio is available

Exit criteria:
- dataset import, variable typing, analysis contracts, chart artifacts, sequence transcript, and summary export are specified
- statsmodels/pandas/numpy/matplotlib execution boundaries are specified
- local-only privacy/provider boundaries are specified
- no runtime CSV import, statistical testing, chart generation, dataset UI, or analysis-summary behavior is active until the lane is enabled

## Milestone 24: Advanced Qualitative Coding Visualizations

Status: Studio Pro conceptual, disabled

Scope:
- add advanced qualitative coding visualizations after Studio and basic coding are available
- support browsable graphs, code/document matrices, distribution tables, visual comparisons, and codebook generation
- visualize parent/child code structure, co-occurrence, frequency distributions, examples, and code appearance across documents, document types, participants, and folders
- provide native Studio SwiftUI browse, filter, compare, and export surfaces
- keep Deep Research, Quantitative Analysis, and Advanced Qualitative Coding as the three Studio Pro feature families after Studio is available

Lane mapping:
- `feat-advanced-qual-visuals`: disabled until explicitly activated after Studio is available

Exit criteria:
- graph, matrix, distribution, comparison, and codebook concepts are specified
- aggregation and visualization data contracts are specified
- no runtime advanced coding visualization, matrix, codebook, or Studio Pro UI behavior is active until the lane is enabled

## Milestone 25: Confidential Collaboration

Status: post-Pro conceptual, disabled

Scope:
- define the later company-wide confidential collaboration system after Studio and the major Pro workflows are in place
- preserve confidential-first project boundaries while eventually supporting shared projects, members, roles, permissions, comments, review decisions, and audit trails
- specify encrypted/local-first sync or secure collaboration-service boundaries before implementation
- make collaboration licensing account-based rather than machine-based, so a higher-licensed user can participate from Lite on a secondary machine when their account permits it
- expose full collaboration management through Studio's native SwiftUI interface, while scoping a minimal Lite participation surface for licensed secondary-machine use
- handle this as a design-first architecture sprint before normal daemon feature batching

Lane mapping:
- `feat-confidential-collaboration`: disabled until explicitly activated after Studio Pro usage feedback

Exit criteria:
- conceptual architecture, threat model, privacy boundary, data concepts, and activation prerequisites are specified
- Studio/SwiftUI management surfaces and Lite participation boundaries are scoped
- collaboration entitlement, license refresh, and client-capability rules are specified as account-based, not device-based
- sidecar/service boundaries and auditability expectations are specified at a planning level
- no runtime collaboration server, sync engine, sharing workflow, SwiftUI collaboration surface, or Textual shell collaboration behavior is active until the lane is enabled

## Milestone 26: Native iPad Lite

Status: long-term conceptual, disabled

Scope:
- define a native iPadOS Lite client after confidential collaboration and after enough Studio/Pro Swift-native infrastructure exists to reuse
- account for the fact that iPad Lite cannot depend on the macOS Python sidecar packaging/supervision model
- identify which Lite workflows must become Swift-native, gateway-backed, deferred, or unavailable on iPad
- preserve account-based Lite access, including inherited Lite access for Studio/Pro subscribers on secondary devices
- scope iPad Lite as a constrained secondary-machine client, not a Studio/Pro feature replacement

Lane mapping:
- `feat-ipad-native-lite`: disabled until explicitly activated after the collaboration conceptual milestone and native Studio/Pro foundations mature

Exit criteria:
- iPad Lite product boundary, entitlement model, sidecar limitations, and Swift-native reuse prerequisites are specified
- project archive, license refresh, offline behavior, and collaboration participation boundaries are specified at a conceptual level
- no runtime iPad app, Swift-native Lite client, App Store packaging, or sidecar replacement behavior is active until the lane is enabled

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
- `feat-project-transfer`
- `feat-desktop-packaging`
- `feat-cop-lite-licensing`
- `feat-browser-pdf-capture`
- `feat-python-sidecar-api`
- `feat-native-workstation`
- `feat-open-access-deep-research`
- `feat-quant-analysis`
- `feat-advanced-qual-visuals`
- `feat-confidential-collaboration`
- `feat-ipad-native-lite`

## Retired planning targets
- `feat-ux-flow`
- `feat-console`

These legacy lanes are superseded by the staged engine/client/shared split and should not be restarted.
