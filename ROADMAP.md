# Exegesis MVP Roadmap

This file is the canonical milestone tracker for the staged Exegesis MVP migration.

Detailed milestone breakdown lives in `/Users/doctor-violet/projects/exegesis/docs/milestones.md`.
Detailed lane/task mapping lives in `/Users/doctor-violet/projects/exegesis/docs/TASKS.md`.
Sprint activation plan lives in `/Users/doctor-violet/projects/exegesis/docs/MVP_SPRINT_PLAN.md`.
MVP notebook context compaction spec lives in `/Users/doctor-violet/projects/exegesis/docs/NOTEBOOK_CONTEXT_COMPACTION_SPEC.md`.
Future import, OCR, literature metadata, and RAG specs live in `/Users/doctor-violet/projects/exegesis/docs/FUTURE_IMPORT_RAG_SPEC.md`.
Future summer MVP feature specs live in `/Users/doctor-violet/projects/exegesis/docs/FUTURE_MVP_FEATURES_SPEC.md`.
Post-MVP feature specs live in `/Users/doctor-violet/projects/exegesis/docs/POST_MVP_FEATURES_SPEC.md`.

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
- define notebook context compaction for long sessions so the engine can continue without losing raw history
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
- notebook context compaction can preserve raw transcript history while assembling budgeted model requests
- CLI can still execute the MVP loop while Textual remains disabled

## Milestone 4: Dogfooding readiness

Status: planned

Scope:
- finish persistence and audit hooks needed for real writing sessions
- expose visible notebook compaction/audit behavior for long writing sessions
- keep command palette/useful workflow actions mapped in the engine contract now
- reserve UI polish and keyboard-first validation for the disabled Textual lanes later

Exit criteria:
- engine state survives repeated sessions
- workflow artifacts are stable enough to support real writing use
- notebook sessions can compact old context without deleting raw history or losing pinned decisions
- the future client surface is unblocked by engine contract gaps

## Milestone 5: YC demo readiness

Status: planned

Scope:
- create one reproducible demo flow for retrieve -> basket -> plan -> revise -> apply
- keep this as cross-lane/integrator work rather than a dedicated feature lane

Exit criteria:
- one clean 60-180 second demo path exists
- the app reads as a writing environment rather than a terminal trick

## Milestone 5A: MVP trust substrate

Status: MVP planned, disabled until Milestone 5 stands

Scope:
- add richer encrypted SQLite-backed storage for durable MVP app/project state, while keeping Markdown documents and project assets portable
- make provenance/tracking first-class for retrieval, basket promotion, model request assembly, generated outputs, rewrite proposals, patch apply/reject decisions, citations, imports, notebook compactions, and A2UI promotion candidates
- move beyond shim-level A2UI by implementing full MVP protocol compatibility: handshake, capability negotiation, primitive block schemas, known card schemas, unknown-card fallback, typed action allowlist, payload validation, streaming event shape, and engine-side policy revalidation
- capture generated A2UI draft surfaces as reviewable promotion candidates in trusted CoP/beta dogfooding, without executing arbitrary generated code
- add privacy-preserving A2UI promotion intake through the hosted License Gateway for opted-in CoP/beta builds
- add local/admin review access for promotion candidates through CLI-first listing/export plus rough static HTML rendering of safe A2UI primitives
- keep generated A2UI constrained to declarative data rendered through shipped clients and mapped only to typed allowlisted engine actions

Lane mapping:
- `feat-context-storage`: owns encrypted SQLite storage and migration/recovery design when this gate is activated
- `feat-a2ui-contract`: owns full A2UI protocol compatibility and generated-surface promotion records when this gate is activated
- `feat-engine-runs`: owns model-request/output/patch provenance hooks when this gate is activated
- `feat-retrieval-fts`: owns retrieval and basket-promotion provenance hooks when this gate is activated
- `feat-cop-lite-licensing`: owns hosted promotion intake endpoints and admin export/review access when the Lite Gateway lane is activated

Exit criteria:
- encrypted SQLite-backed storage exists for durable metadata, sessions, workflow artifacts, provenance, audit events, compaction records, and A2UI promotion candidates
- raw Markdown documents remain portable and project export/import remains possible
- provenance records can explain the context-to-output-to-patch chain for normal writing workflows
- A2UI protocol compatibility is complete enough that future Textual/native clients do not depend on a shim-only contract
- generated A2UI drafts can be stored, reviewed, rejected, or promoted from CoP use without allowing generated code execution
- opted-in CoP/beta builds can upload redacted A2UI promotion bundles to the License Gateway without sending document text, basket content, transcript text, credentials, file paths, or raw prompts by default
- promotion candidates can be examined through an admin CLI/static HTML workbench before any pattern is promoted

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
- add document and selection word counts in the inspector alongside LLM token estimates
- include document and selection word counts in draft/rewrite model request context
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
- support provider, model, and supported reasoning-level selection for Developer BYOK/BYOM routes
- store keys securely through the OS credential-store abstraction
- keep Lite managed provider defaults separate from Developer keys

Lane mapping:
- `feat-developer-provider-config`: disabled until explicitly activated

Exit criteria:
- provider commands, credential storage, provider defaults, model/reasoning selection, connection tests, and clear-credential behavior are specified
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
- use Briefcase as the cross-platform packager
- bundle the Python executable/runtime and app dependencies; packaged Developer/Lite builds must not depend on system Python
- add Cloudflare R2-backed update checks with an unobtrusive update button and a `Check for Updates` menu command
- block confidential project creation/open when the app is not fully updated and the release manifest marks an update required
- keep Lite managed-provider secrets outside the bundle and routed through the hosted License Gateway
- keep Lite local Python services direct inside the packaged app; the License Gateway is for managed remote credentials, license refresh, Paddle, and Nanonets accounting, not for local Python execution
- keep Developer builds wired to Milestone 15 BYOK/BYOM provider configuration
- gate dynamic A2UI generation by distribution profile: Developer and trusted CoP/beta builds may enable it, while public Lite/App Store-oriented builds default to promoted/preapproved A2UI components
- keep cross-platform Developer/Lite packaging separate from the later macOS-only Studio Workstation

Lane mapping:
- `feat-desktop-packaging`: disabled until explicitly activated

Exit criteria:
- Developer and Lite packaging architecture is specified
- local runtime startup, shutdown, storage, update, release artifact, and profile boundaries are specified
- confidential-project version gating is specified for required updates
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
- define Lite/Studio/Pro system tiers: Lite 8 GB, Studio 8 GB with managed cloud OCR, Pro 16 GB, local OCR when enough memory is currently available, and 128 GB for local confidential mode
- define Studio and Pro managed cloud OCR fallback buckets: Studio 250 pages/month and Pro 500 pages/month
- include Pro BYOK/BYOM provider configuration for OpenAI, Claude, Mistral, and local OpenAI-compatible backends with provider/model/reasoning selection for non-confidential projects only
- keep Quantitative Analysis and Advanced Qualitative Coding Visualizations gated to Pro-only `pro_feature_access`
- keep the hosted License Gateway as the place for license claim/refresh, managed Lite Mistral access, managed Nanonets OCR fallback, Paddle webhooks, and Nanonets page-credit state
- include the A2UI promotion intake service in the hosted License Gateway so opted-in CoP/beta clients can submit privacy-preserving generated-surface bundles for review
- make project transfer license-safe: imported project zips require the current user to have a valid license, but licenses are never machine-bound or included in project archives

Lane mapping:
- `feat-cop-lite-licensing`: disabled until explicitly activated as the CoP launch gate

Exit criteria:
- individual paid Lite, Studio/Pro inherited Lite access, course licensing, initial CoP access, and Nanonets page-credit rules are specified
- Pro BYOK/BYOM provider configuration is specified as non-confidential provider routing and remains separate from local confidential mode
- Paddle website purchase, course-license link, Tally/MCP approval workflow, and License Gateway contracts are specified
- A2UI promotion intake, redaction, consent, admin review/export, and candidate-status workflows are specified
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

## Milestone 20: Python Backend Sidecar Bridge

Status: post-MVP planned, disabled

Scope:
- add a macOS-native XPC bridge for Python-backed features used by Studio Workstation
- package the sidecar as a signed, sandboxed, bundled Python worker/XPC service inside the Studio `.app`
- follow stricter App Store-compatible sidecar rules even for direct distribution: bundled code only, signed dependencies, inherited sandbox, no downloaded executable Python packages, no arbitrary generated-code execution, no localhost API for native Studio
- include health, readiness, version, feature manifest, shutdown, request limits, log redaction, code-signature, entitlement, and sidecar lifecycle contracts
- require future Studio Python features to expose Workstation-facing behavior through the sidecar when applicable
- keep Python/Textual Lite separate: it remains the cross-platform Python app path and may call the shared Python service layer directly instead of using the native XPC sidecar

Lane mapping:
- `feat-python-sidecar-api`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- sidecar XPC/RPC schema, security, lifecycle, packaging, and supervision contracts are specified
- macOS Studio sidecar signing, sandboxing, entitlement, and packaging expectations are specified
- no runtime sidecar bridge or signed service/helper packaging behavior is active until the lane is enabled

## Milestone 21: Native Workstation and Signed Distribution

Status: post-MVP planned, disabled

Scope:
- define the macOS-only native Workstation, branded as Studio, after the sidecar milestone
- package the native SwiftUI interface, project storage, and Milestone 20 sidecar into a signed and notarized macOS distribution
- evaluate STTextView as the preferred native editor foundation, with plugins for annotations, Markdown highlighting, diffs, citations, figures, and tables
- add native settings for Light, Dark, and Auto appearance modes
- enforce Workstation system tiers: Studio minimum 8 GB, Pro minimum 16 GB, local confidential mode minimum 128 GB, and local OCR only when enough memory is currently available
- route OCR locally when enough memory is currently available, otherwise fall back to managed cloud OCR when policy allows and the project is not confidential
- define MLX Swift as the local confidential runtime and specify confidential quant tiers from 128 GB Q4 through 512 GB F16
- specify Pro local model manager behavior for confidential runtime model downloads, storage, deletion, checksums, and tier selection
- define R2-backed licensed multipart model downloads and first-confidential-project just-in-time model acquisition
- define R2-backed app update checks with an unobtrusive update button and `Check for Updates` menu command
- require the latest required update before creating or opening confidential projects
- allow direct-distribution Studio/Pro builds to enable dynamic A2UI only through the fixed declarative renderer and promotion rules; App Store-oriented builds stay on promoted/preapproved A2UI unless current Apple policy explicitly allows more
- lock project confidentiality at creation and restrict confidential-project imports to confidential sources except literature
- ship through web distribution with checksums, release manifest, clean install, update/manual upgrade, crash/diagnostic, and data preservation guidance
- remove Windows and Linux signing from this milestone; those are not Studio targets
- keep this as a likely interactive sprint rather than broad daemon-driven packaging work

Lane mapping:
- `feat-native-workstation`: disabled until explicitly activated after the MVP launch gate

Exit criteria:
- macOS Studio lifecycle, signing, notarization, R2-backed distribution/update, and sidecar supervision are specified
- required-update confidential project gates are specified
- native editor foundation and STTextView plugin expectations are specified at a conceptual level
- native appearance settings and Pro local model manager behavior are specified
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
- require Pro-only `pro_feature_access`
- include lean dataset preparation: filtering, row/column removal, one-hot encoding, manual categorical/ordinal quantization, and keyed unions across datasets
- support descriptive statistics, frequency and contingency tables, t-test, ANOVA, chi-squared, and linear correlation
- show p-values, effect sizes, and compact small/medium/large guidance
- implement dataset views, analysis configuration, and result sequences only in Studio's native SwiftUI interface
- implement statistics through native `StatsCore` Swift APIs, a narrow `StatsBridge` C shim, and IMSL C Numerical Library rather than Python/statsmodels

Lane mapping:
- `feat-quant-analysis`: disabled until explicitly activated after Studio is available

Exit criteria:
- dataset import, variable typing, dataset preparation transforms, analysis contracts, chart artifacts, sequence transcript, and summary export are specified
- `StatsCore`, `StatsBridge`, IMSL isolation, Swift DataFrame-compatible adapters, and vendor feasibility gates are specified
- local-only privacy/provider boundaries are specified
- no runtime CSV import, statistical testing, chart generation, dataset UI, or analysis-summary behavior is active until the lane is enabled

## Milestone 24: Advanced Qualitative Coding Visualizations

Status: Studio Pro conceptual, disabled

Scope:
- add advanced qualitative coding visualizations after Studio and basic coding are available
- require Pro-only `pro_feature_access`
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
- assume promoted/preapproved declarative A2UI only on iPad until Apple policy and a Swift-native renderer explicitly support dynamic generated task surfaces
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
  - continue working with compacted notebook context when the raw history grows too large
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
