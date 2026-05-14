# Exegesis MVP Sprint Activation Plan

This document defines the development sprint order for activating disabled milestone lanes. A sprint is the unit of parallel work: enable the lanes in a sprint together, integrate them against one shared outcome, and do not move to the next sprint until the current sprint's exit criteria are met.

## Sprint 0: Standing Core

Status: active now

Lanes:
- `feat-context-storage`
- `feat-commands`
- `feat-retrieval-fts`
- `feat-engine-runs`
- `feat-a2ui-contract`

Goal:
- Make one engine-first Exegesis loop stand before expanding feature scope.

Shared integration target:
- Open a project/document.
- Retrieve relevant material.
- Promote or gather context into the basket.
- Produce a plan or revision.
- Preview and apply or reject a patch.
- Persist document, basket, session, and audit state.
- Continue without losing context, using notebook compaction when raw history grows beyond the request budget.

Exit criteria:
- The canonical engine loop works through CLI/app-service paths.
- Retrieval returns structured results suitable for basket/context promotion.
- Plan/draft/revise/apply-reject actions are stable enough for client consumption.
- Notebook context compaction preserves raw history while assembling budgeted model requests for long sessions.
- A2UI contracts are stable enough for later Textual integration.
- No later sprint is activated before this loop is real.

## Sprint 1: Import And Knowledge Foundation

Activate together:
- `feat-ocr-import`
- `feat-literature-import`
- `feat-rag-index`
- `feat-zotero-import`

Goal:
- Build the intake and knowledge substrate: Markdown/PDF/Zotero in, normalized documents and metadata stored, useful retrieval out.

Shared integration target:
- Import Markdown directly.
- OCR non-Markdown sources into editable Markdown with provenance.
- Import literature with metadata.
- Import Zotero literature as the preferred metadata path.
- Skip initial metadata classification for Zotero attachments when Zotero metadata is complete.
- Index normalized documents and retrieve chunks that can be promoted into the basket.

Exit criteria:
- Literature folder works as a durable project-level literature library.
- Zotero one-way import is usable for metadata and attached files.
- OCR-derived and Zotero-derived documents are searchable/retrievable.
- RAG can retrieve from imported, OCRed, and Zotero-sourced material.
- Citations/export lanes remain disabled until this metadata foundation is stable.

## Sprint 2: Writing And Analysis Workspace

Activate together:
- `feat-qual-coding`
- `feat-editor-basics`
- `feat-formatting-bar`

Goal:
- Make the workspace feel safe and useful for real qualitative reading, markup, organization, and drafting.

Shared integration target:
- Select text and apply a code.
- Inspect code appearances, frequencies, parent/child code information, and related documents.
- Organize documents, folders, codes, and parent codes.
- Use copy, paste, undo, redo, and basic Markdown formatting without breaking document state.

Exit criteria:
- Coding selected text works with stable document offsets/content hashes.
- Project browser folders and one-level parent codes are usable.
- Undo/redo protects coding, formatting, and basic edit operations.
- Formatting controls insert predictable Markdown.
- The workspace is safe enough for dogfooding real reading and coding sessions.

## Sprint 3: Scholarly Output

Activate together:
- `feat-citations`
- `feat-export`

Goal:
- Turn Exegesis work into credible scholarly artifacts.

Shared integration target:
- Insert citations from the project literature library.
- Render citations as document links while storing Pandoc-compatible Markdown.
- Require LLM-used literature to be cited in generated output.
- Export raw Markdown, APA PDF, and APA DOCX with a reference list.

Exit criteria:
- Literature metadata from Sprint 1 can produce reliable citations.
- Draft author/institution/export metadata can be captured and edited.
- APA PDF/DOCX exports include references from cited literature.
- Raw Markdown export remains available for transparent portability.

## Sprint 4: Python/Textual Distribution

Activate together:
- `feat-developer-provider-config`
- `feat-project-transfer`
- `feat-desktop-packaging`

Goal:
- Make the Python/Textual Developer and Lite builds installable and usable outside the development repo.

Shared integration target:
- Developer build supports BYOK/BYOM provider setup through command-palette flows.
- Lite build uses fixed remote Mistral Small 4 and managed Nanonets OCR-3 provider paths.
- API keys and local endpoint credentials use OS credential storage.
- Project export/import creates portable zip archives for moving projects between machines.
- Project archives never include credentials, provider keys, local endpoints, license tokens, or managed Lite secrets.
- Packaged Python/Textual app launches as a desktop app without terminal or localhost exposure.
- This is the cross-platform Python runtime path; macOS-only native Studio is handled later through the XPC sidecar bridge specs.

Exit criteria:
- Developer and Lite provider modes are separated and testable.
- Project transfer is license-safe: licenses are per user/account, not per machine or archive.
- Python/Textual macOS packaging path works first, with Windows/Linux specs ready for follow-up.
- SQLite app data, local server startup, pywebview shell, and shutdown are packaged-runtime safe.
- A user can install and launch the app without developer tooling.

## Sprint 5: CoP Launch Gate

Activate alone:
- `feat-cop-lite-licensing`

Goal:
- Let the first Community of Practice actually use Lite, with access and Nanonets usage controlled enough for beta launch.

Shared integration target:
- Individual users can purchase Lite through the website and Paddle.
- Studio and Pro subscribers automatically receive Lite access for secondary-machine use without a separate Lite purchase.
- Instructors can receive course licensing approval and distribute one self-serve link to students.
- Tally intake is available through MCP for Claude cowork-assisted course-license review and manual approval preparation.
- Admin can issue initial CoP Lite access.
- Lite app can claim and refresh license status through the hosted Lite License Gateway.
- Initial CoP has unlimited Lite course access with no seat cap.
- Initial CoP starts with 150 Nanonets pages.
- Top-ups are fixed at 150, 500, and 1000 pages through Paddle/manual admin flow.
- Pro includes BYOK/BYOM provider configuration for OpenAI, Claude, Mistral, and local OpenAI-compatible backends, with provider/model/reasoning selection for non-confidential projects only.
- Lite import window shows Nanonets balance and estimated page count before OCR-backed import.
- Developer builds never use hosted Lite workflows.

Exit criteria:
- Initial CoP can access Lite course materials.
- Individual paid Lite users and course-link students can claim Lite access through the License Gateway.
- Studio/Pro users can refresh inherited Lite access through the License Gateway on secondary machines.
- Nanonets usage is ledger-based and cannot silently overspend.
- Paddle webhook/top-up handling is idempotent.
- Individual/course/CoP Lite access, project transfer, and Nanonets page credits remain separate systems.
- The first CoP can start using Exegesis without per-machine hand-holding.

## Activation Rules

- Activate all lanes in a sprint together unless a hard blocker requires a narrow preparatory packet.
- Do not activate the next sprint until the current sprint's shared integration target works end-to-end.
- Keep disabled lanes disabled in router config until their sprint is intentionally started.
- When a sprint starts, each lane should still use normal packet review/integration gates.
- If a lane needs shared or integrator-locked files, use the high-risk kickoff template and narrow the task budget.
- Prefer one believable end-to-end workflow over broad partial coverage.

## Stop Line

Sprint 5 is the summer launch gate. After Sprint 5, stop adding new planned features until there is real CoP usage feedback.

## Post-MVP Backlog

These lanes are deliberately outside Sprint 0-5 and should not be activated until after the CoP launch gate produces real usage feedback.

- `feat-browser-pdf-capture`
- `feat-python-sidecar-api`
- `feat-native-workstation`
- `feat-open-access-deep-research`
- `feat-quant-analysis`
- `feat-advanced-qual-visuals`
- `feat-confidential-collaboration`
- `feat-ipad-native-lite`

Milestone 19 lives in `docs/POST_MVP_FEATURES_SPEC.md` and specifies a tiny browser PDF capture extension for Chrome, Firefox, and Safari.
Milestone 20 lives in the same post-MVP spec and specifies a signed, sandboxed macOS XPC Python sidecar bridge for Studio Workstation. It reuses the same Python service layer as Python/Textual Lite, but native Studio talks to it through XPC rather than a localhost FastAPI server.
Milestone 21 lives in the same post-MVP spec and specifies the macOS-only native Workstation/Studio distribution sprint for signed web-distributed builds that bundle the sidecar, enforce Workstation memory tiers, provide native Light/Dark/Auto appearance settings, manage Pro local confidential models, and route OCR locally or through managed cloud fallback based on available memory and policy.
Milestone 22 lives in the same post-MVP spec and specifies local-first multi-agent open access source discovery that hands deduped candidates to the standard import protocol through the sidecar.
Milestone 23 lives in the same post-MVP spec and specifies Pro-only first-class CSV dataset import, lean dataset preparation, quantitative analysis, basic charts, and saveable analysis sequences through native `StatsCore`/`StatsBridge`/IMSL rather than the Python sidecar by default.
Milestone 24 lives in the same post-MVP spec and specifies Pro-only advanced qualitative coding visualizations, matrices, distribution tables, comparisons, and codebook generation.
Milestone 25 lives in the same post-MVP spec and specifies the later company-wide confidential collaboration design sprint for Studio/SwiftUI shared project work.
Milestone 26 lives in the same post-MVP spec and specifies long-term native iPad Lite after collaboration, once Studio/Pro Swift-native components can replace sidecar-dependent behavior.
