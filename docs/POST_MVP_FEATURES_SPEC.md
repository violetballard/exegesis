# Post-MVP Feature Specs

This document defines disabled post-MVP work that should not be activated until the summer MVP and CoP launch gate have produced real usage feedback.

Current post-MVP lanes:
- Milestone 18: `feat-browser-pdf-capture`
- Milestone 19: `feat-open-access-deep-research`
- Milestone 20: `feat-quant-analysis`

Activation rule:
- These lanes remain disabled in router config.
- Do not schedule, implement, or polish these features until explicitly enabled after the MVP launch gate.
- Runtime browser extension, native bridge, import handoff, packaging behavior, open web search, multi-agent research orchestration, source ranking, import-batch behavior, CSV dataset analysis, statistical testing, and plot generation must remain inactive until the relevant lane is intentionally activated.

## Milestone 18: Browser PDF Capture Extension

Lane: `feat-browser-pdf-capture` (disabled)

Intent:
- Add a very small browser extension for Chrome, Firefox, and Safari whose only user-facing job is sending the current PDF tab to Exegesis.
- Keep the extension as a capture button, not a Zotero clone, translator system, scraper, or standalone product surface.
- Let Exegesis own authenticated/direct fetch, import, OCR, metadata extraction, project placement, deduping, and indexing.
- Package browser-extension artifacts with the desktop app so users do not need a separate download.

Non-activation rule:
- This milestone is post-MVP specification and lane scaffolding only.
- Do not implement runtime extension code, browser install helpers, local capture endpoints, native messaging hosts, protocol handlers, or Exegesis import behavior until this lane is explicitly enabled.

### Product Boundary

The browser extension owns only:
- determining whether the active tab looks like a PDF or PDF viewer tab
- showing one action: `Add PDF to Exegesis`
- sending the current tab URL, title, browser metadata, and source context to Exegesis
- showing a small success/error state after handoff

Exegesis owns everything else:
- direct URL fetch where possible
- future browser-assisted relay for authenticated PDFs when needed
- file import and normalized Markdown creation
- OCR via the existing OCR pipeline
- literature metadata extraction via the existing literature import pipeline
- project placement and import confirmation
- deduplication against existing project literature
- RAG indexing when the RAG lane exists
- import audit/provenance records

Non-goals:
- no link detection on arbitrary pages
- no page scraping
- no translator system
- no citation extraction inside the browser extension
- no browser-side PDF parsing
- no browser-side OCR
- no browser-side metadata classification
- no browser-side project browser
- no account, license, or provider configuration UI in the extension

### Supported Browsers

Initial target browsers:
- Chrome
- Firefox
- Safari

Implementation approach:
- Use one small WebExtension source tree for Chrome and Firefox.
- Generate browser-specific manifests from a shared base manifest when needed.
- Provide Safari through a Safari Web Extension wrapper as part of the macOS desktop package.
- Edge can follow the Chrome build path later, but Edge support is not required for Milestone 18 acceptance.

Packaging expectation:
- Desktop packages include the extension artifacts for Chrome, Firefox, and Safari.
- Install/enable flows are launched from Exegesis onboarding or first-run packaging helpers.
- The product should avoid a separate manual extension download.
- Browser security rules still apply: if Chrome, Firefox, or Safari requires user confirmation or extension enablement, Exegesis must guide that confirmation rather than trying to bypass it.
- Safari extension delivery is bundled with the macOS app and enabled through Safari's extension controls.
- Chrome and Firefox extension artifacts must be signed or distributed through the browser-approved channel required by the target release process.

### Extension UI

Popup states:
- PDF detected:
  - primary button: `Add PDF to Exegesis`
  - optional secondary link after success: `Open in Exegesis`
- Not a PDF:
  - message: `This tab is not a PDF.`
  - no import action
- Exegesis unavailable:
  - message: `Exegesis is not running.`
  - action: `Open Exegesis`
- Handoff accepted:
  - message: `PDF sent to Exegesis.`
  - action: `Open in Exegesis`
- Handoff rejected or failed:
  - show one short actionable error from the handoff endpoint

The popup should not include:
- project pickers
- metadata forms
- citation controls
- OCR controls
- browser history lists
- settings
- provider/key configuration

Toolbar behavior:
- The browser action icon is always available.
- The popup decides whether the current tab is a PDF.
- Optional badge states may be added later, but are not required.

### PDF Detection

Detection inputs:
- active tab URL
- tab title
- browser-reported MIME/content type where available
- URL path/query signals such as `.pdf`
- known browser PDF viewer URL patterns when the original PDF URL can be recovered

Detection policy:
- The extension should classify a tab as PDF only when it has strong evidence.
- If detection is uncertain but the URL is sendable, the extension may show `Add PDF to Exegesis` with app-side validation required.
- Exegesis must always validate that the submitted URL resolves to a PDF or importable PDF-like resource before processing.
- Restricted browser pages such as `chrome://`, `about:`, extension pages, local browser-internal pages, and empty tabs are never sendable.

Do not overbuild detection:
- no page scanning
- no link discovery
- no DOM scraping
- no parsing embedded viewers beyond recovering the active PDF URL when the browser exposes it cleanly

### Handoff Architecture

Preferred MVP handoff:
- Extension sends a JSON POST to a loopback Exegesis capture endpoint while Exegesis is running.
- Endpoint binds only to `127.0.0.1`.
- Endpoint accepts only browser-extension origins or native-bridge messages that match the installed extension IDs.
- Endpoint creates a pending browser import in Exegesis and returns a small status response.

Fallback handoff:
- If Exegesis is not running, the extension may open a registered `exegesis://` protocol URL with the PDF URL encoded.
- The desktop app registers the custom protocol during packaging.
- Protocol payloads must be size-limited and validated exactly like loopback handoffs.

Later formal bridge option:
- Native messaging can replace or augment loopback HTTP if browser/security requirements make it necessary.
- Native messaging is not required for the first Milestone 18 implementation unless loopback handoff fails acceptance criteria.

Local endpoint contract:

```http
POST http://127.0.0.1:<capture-port>/api/browser-capture/pdf
Content-Type: application/json
Origin: <browser-extension-origin>
```

Request body:

```json
{
  "schema_version": 1,
  "capture_kind": "pdf_tab",
  "url": "https://example.edu/article.pdf",
  "tab_title": "Article Title",
  "source_page_url": "https://example.edu/article.pdf",
  "browser": "chrome",
  "extension_id": "<browser-extension-id>",
  "captured_at": "2026-05-06T12:00:00Z",
  "metadata": {
    "tab_id": 123,
    "window_id": 456,
    "mime_hint": "application/pdf",
    "detection_reason": "url_extension"
  }
}
```

Response body:

```json
{
  "status": "accepted",
  "pending_import_id": "browser_import_123",
  "message": "PDF sent to Exegesis."
}
```

Failure responses:
- `not_running`: extension could not contact local Exegesis endpoint
- `not_pdf`: Exegesis could not validate the submitted resource as a PDF
- `unsupported_url`: browser page or URL scheme cannot be imported
- `duplicate`: PDF already appears to exist in the target project, with app-side dedupe/review state
- `needs_app_attention`: Exegesis accepted the capture but needs user placement or metadata confirmation
- `error`: generic sanitized failure

### Exegesis Import Flow

On accepted handoff:
1. Create a pending browser import record.
2. If an Exegesis project is open, open the normal import review flow with the PDF URL prefilled.
3. If no project is open, prompt the user to open or create a project before import.
4. Default import type to `literature` for PDF captures, but keep the existing import type picker editable.
5. Fetch the PDF directly from the URL when possible.
6. Route non-Markdown content through Milestone 6 OCR import behavior when OCR is active.
7. Route literature PDFs through Milestone 7 literature metadata extraction when literature import is active.
8. Deduplicate before saving by DOI, URL, title/author/year, and content hash where available.
9. Save normalized Markdown, original-source provenance, and metadata into the project.
10. Queue indexing through Milestone 8 RAG indexing when RAG is active.

Pending import record fields:
- `id`
- `source`: `browser_extension`
- `capture_kind`: `pdf_tab`
- `url`
- `tab_title`
- `source_page_url`
- `browser`
- `extension_id`
- `status`: pending, fetching, imported, duplicate_review, failed, cancelled
- `target_project_id`: nullable until user chooses project
- `target_document_type`: default `literature`
- `dedupe_candidates`
- `error_message`
- `created_at`, `updated_at`

Provenance fields:
- original URL
- browser name
- captured timestamp
- tab title
- direct fetch URL after redirects
- response content type
- response content length if known
- content hash
- OCR provider/model if OCR is used
- metadata extraction provider/method if metadata extraction is used

### Authenticated PDF Strategy

MVP behavior:
- Support directly fetchable PDF URLs first.
- If the PDF requires an authenticated browser session that Exegesis cannot access, fail gracefully with an app-side message.
- Preserve the submitted URL and browser metadata so the user can retry later or import manually.

Required error copy:
- `Exegesis could not fetch this PDF directly. Save the PDF locally and import it, or retry when browser-assisted PDF fetch is available.`

Future extension-assisted relay hook:
- Add a later mode where the extension fetches the active PDF with browser session cookies and streams the PDF bytes to Exegesis.
- This mode must be explicitly permissioned, size-limited, user-initiated, and never used for non-PDF pages.
- Relay mode is not part of the first acceptance path unless direct-fetch-only proves insufficient during testing.

### Security And Privacy

Endpoint security:
- Bind capture endpoint to loopback only.
- Validate extension origin or native-message sender.
- Reject non-PDF and unsupported URL schemes before import.
- Do not accept arbitrary webpage POSTs as trusted browser captures.
- Sanitize all user-visible error text.
- Do not log full signed URLs or sensitive query strings unless explicitly redacted.
- Do not send browser cookies, headers, or page contents in the MVP direct-fetch path.

Extension security:
- Request the smallest practical permissions.
- Use `activeTab`/tabs permission only for the current user-activated tab flow.
- Avoid broad persistent host permissions unless a browser requires them for PDF detection or relay mode.
- Do not store PDF contents, tokens, cookies, or credentials in extension storage.
- Do not call cloud services directly from the extension.

Import privacy:
- Developer builds use local/provider configuration already selected in Exegesis.
- Lite builds use managed Lite provider flows only through Exegesis, not through the extension.
- Confidential-mode project rules remain enforced by Exegesis after handoff.
- The extension must not bypass project mode or provider policy.

### Manifest And Source Layout

Recommended source layout:

```text
/browser-extension
  /src
    background.ts
    popup.html
    popup.ts
    pdf-detect.ts
    exegesis-client.ts
    browser-api.ts
  /assets
    icon-16.png
    icon-32.png
    icon-48.png
    icon-128.png
  manifest.base.json
  manifest.chrome.json
  manifest.firefox.json
  /safari
    README.md
    wrapper-notes.md
  /tests
    pdf-detect.test.ts
    exegesis-client.test.ts
  package.json
  tsconfig.json
```

Manifest requirements:
- MV3-style extension where supported.
- Browser action popup.
- Active-tab/tab metadata access.
- Loopback host permission for `http://127.0.0.1/*` or the fixed Exegesis capture port.
- Browser-specific extension IDs declared in build/release config, not scattered through code.

Shared TypeScript modules:
- `pdf-detect.ts`
  - classifies active tab as PDF, possible PDF, or not PDF
- `exegesis-client.ts`
  - sends the capture payload to loopback endpoint or protocol fallback
- `browser-api.ts`
  - wraps Chrome/Firefox/Safari API differences
- `popup.ts`
  - drives the small popup state machine

### Packaging And Install Integration

Packaging responsibilities:
- Milestone 16 desktop packaging must include extension artifacts when Milestone 18 is active.
- Build scripts produce Chrome, Firefox, and Safari deliverables from the shared extension source.
- First-run onboarding checks browser-extension install/enable status and offers browser-specific setup.
- The app can re-open setup from the command palette, e.g. `Install Browser PDF Capture Extension`.

Install constraints:
- Do not rely on silent extension installation if the browser disallows it.
- If a browser requires store signing, user confirmation, or enabling in settings, Exegesis guides that flow.
- Successful packaging means the user does not separately hunt for the extension; not that browser security prompts are bypassed.

Command-palette additions:
- `Install Browser PDF Capture Extension`
- `Check Browser Extension Status`
- `Open Browser Extension Help`

Browser status fields:
- browser name
- installed: yes/no/unknown
- enabled: yes/no/unknown
- extension version
- last successful capture timestamp
- last error summary

### Implementation Batches

1. Spec and lane scaffolding
   - Add docs, disabled lane registration, ownership, lane profile, and scope policy.
2. Shared handoff contract
   - Define capture request/response models and pending import records.
3. Local capture endpoint
   - Add loopback-only endpoint, extension-origin validation, and app-side pending import creation.
4. Extension MVP
   - Build popup, active-tab PDF detection, loopback client, and success/error states for Chrome and Firefox from shared source.
5. Safari wrapper
   - Add Safari Web Extension packaging wrapper and macOS enablement guidance.
6. Exegesis import integration
   - Wire pending browser imports into the normal import review flow, direct fetch, dedupe, OCR, literature metadata, and indexing hooks.
7. Packaging integration
   - Bundle artifacts, add install/status commands, add first-run browser-extension setup.
8. Security, redaction, and acceptance tests
   - Harden URL handling, origin validation, logging, and browser compatibility tests.

### Edge Cases

- Current tab is not a PDF: popup says so and disables import.
- Current tab URL is browser-internal or restricted: disable import.
- Exegesis is not running: offer `Open Exegesis` through custom protocol fallback.
- Exegesis is running but no project is open: create pending capture and prompt for project selection.
- Direct fetch returns HTML login page: reject as not directly fetchable PDF and show authenticated-PDF message.
- Direct fetch follows redirects: store final URL and validate final content type/content hash.
- PDF URL has sensitive query params: redact logs and display shortened URL in UI.
- Same PDF already exists: show duplicate review in Exegesis, not in the extension.
- Browser extension sends malformed payload: reject and log sanitized validation error.
- Extension version is older than endpoint schema: return upgrade-required message.
- Endpoint schema is newer than extension: use schema version negotiation or friendly failure.
- User has multiple Exegesis windows: the running app owns the pending import and brings the correct window forward if possible.
- Confidential project mode rejects online OCR/metadata: Exegesis enforces that after handoff.
- Browser-assisted relay later exceeds size cap: abort safely and instruct local file import.

### Test Plan

Scaffolding tests:
- `feat-browser-pdf-capture` exists in lane defaults and profiles.
- `feat-browser-pdf-capture` is disabled in router config and example config.
- Scope-check policy allows only browser-extension, desktop packaging integration, browser-capture engine/client/shared paths, and browser-capture docs when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is post-MVP and not part of Sprint 0-5.

Extension unit tests:
- URL ending in `.pdf` is classified as PDF.
- PDF viewer tab with recoverable original PDF URL is classified as PDF.
- HTML page, blank tab, and browser-internal tab are not classified as PDF.
- Capture payload includes URL, title, browser, extension ID, timestamp, and detection reason.
- Exegesis unavailable state maps to `Open Exegesis` popup action.
- Rejected/unsupported URL responses show short user-facing errors.

Endpoint tests:
- Loopback endpoint rejects unsupported origins/senders.
- Loopback endpoint rejects malformed payloads.
- Loopback endpoint creates pending import for valid PDF capture payloads.
- Loopback endpoint rejects unsupported URL schemes.
- Endpoint response uses stable schema version.
- Sensitive query strings are redacted in logs.

Import integration tests:
- Accepted PDF capture opens import review flow when a project is open.
- No open project prompts project selection before import.
- Directly fetchable PDF imports through the normal import/OCR/literature pipeline.
- Login-page/HTML response is rejected with authenticated-PDF copy.
- Duplicate candidate creates app-side duplicate review state.
- Confidential-mode provider restrictions are enforced after capture.

Packaging tests:
- Chrome extension artifact is built and included in desktop release assets.
- Firefox extension artifact is built and included in desktop release assets.
- Safari extension wrapper is included in macOS release assets.
- First-run/onboarding can launch browser-specific install or enablement flow.
- Command palette can check browser extension status.

Acceptance criteria:
- User opens a directly fetchable PDF in Chrome and sends it to Exegesis.
- User opens a directly fetchable PDF in Firefox and sends it to Exegesis.
- User opens a directly fetchable PDF in Safari and sends it to Exegesis.
- Non-PDF tabs do not offer import.
- Exegesis validates the resource before import.
- Exegesis, not the extension, handles project placement, OCR, metadata, dedupe, and indexing.
- Extension remains small enough that future browser changes are easy to maintain.

## Milestone 19: Multi-Agent Open Access Deep Research

Lane: `feat-open-access-deep-research` (disabled)

Intent:
- Add a post-MVP source-discovery workflow that helps users find possible literature and web sources for review, import, summary, and synthesis inside Exegesis.
- Start with already-owned Exegesis knowledge by searching the current project and other local Exegesis projects before going out to the open web.
- Use a small multi-agent research architecture inspired by LangChain Open Deep Research and LangGraph-style supervisor/researcher patterns, but stop at candidate discovery and import review.
- Present deduped source candidates as a batch that flows into the standard Exegesis import protocol.
- Do not generate final synthesis reports, research summaries, or answer-style deep research output in this milestone.

Non-activation rule:
- This milestone is post-MVP specification and lane scaffolding only.
- Do not implement runtime web search, local project search fan-out, provider API calls, browser scraping, source ranking, import batch creation, or shell UI behavior until this lane is explicitly enabled.

### Product Boundary

This milestone owns:
- research-intent intake from the user
- local Exegesis project/source discovery
- open web source discovery through configured search providers
- provider-normalized source candidate records
- URL/document deduplication and canonicalization
- light candidate ranking and confidence labeling
- user-reviewable source batches
- handoff into the mature import/OCR/literature metadata/RAG pipeline
- provenance for how each source candidate was found

Existing or earlier milestones own:
- PDF import and OCR normalization through Milestone 6
- literature metadata detection/approval through Milestone 7
- RAG indexing and retrieval through Milestone 8
- Zotero literature import through Milestone 13
- browser PDF capture through Milestone 18
- summaries, drafting, citation insertion, export, and synthesis in their respective lanes

Non-goals:
- no generated literature review
- no final research report
- no automatic synthesis paragraphs
- no automatic claims added to drafts
- no autonomous citation insertion into drafts
- no browser automation or arbitrary page scraping in the first implementation
- no downloading paywalled or unauthorized sources
- no bypassing institutional authentication
- no Zotero write-back
- no automatic import without user approval

### Architecture Inspiration

The architecture should borrow the useful parts of LangChain Open Deep Research without copying its product behavior:
- a supervisor decomposes the research request into source-discovery subqueries
- several researcher workers can search in parallel
- providers are modular and configurable
- results are normalized into a shared state object
- dedupe/ranking happens before presenting results
- state is checkpointable, auditable, and resumable

Exegesis-specific differences:
- Exegesis does not write a final report in this lane.
- Exegesis does not synthesize findings in this lane.
- Exegesis starts from local project knowledge before open web discovery.
- Exegesis returns importable source candidates, not prose answers.
- Exegesis uses the existing import pipeline as the point of truth for OCR, metadata, dedupe, project placement, and indexing.

Reference architecture sources:
- LangChain Open Deep Research: https://github.com/langchain-ai/open_deep_research
- LangChain deep research docs: https://docs.langchain.com/oss/javascript/deepagents/deep-research
- LangGraph multi-agent patterns: https://www.langchain.com/blog/langgraph-multi-agent-workflows
- Tavily Search API: https://docs.tavily.com/api-reference/endpoint/search
- Tavily introduction: https://docs.tavily.com/guides/introduction
- Exa Search API: https://docs.exa.ai/reference/search
- Brave Search API: https://brave.com/search/api/
- OpenAlex works and OA locations: https://docs.openalex.org/api-entities/works/work-object
- OpenAlex full-text PDFs: https://developers.openalex.org/download-all-data/full-text-pdfs
- Semantic Scholar Academic Graph API: https://www.semanticscholar.org/product/api
- arXiv API manual: https://arxiv.org/help/api/user-manual
- CORE API documentation: https://core.ac.uk/documentation/api
- Europe PMC RESTful Web Service: https://europepmc.org/RestfulWebService

### User Workflow

Primary flow:
1. User opens a project.
2. User starts `Deep Research Source Discovery` from the command palette or research/search surface.
3. User enters a research topic, guiding question, keywords, or source criteria.
4. Exegesis searches current project sources first.
5. Exegesis searches other selected local Exegesis projects second.
6. Exegesis expands to configured open web and open-access PDF/full-text providers.
7. Exegesis normalizes and dedupes all candidate sources.
8. Exegesis presents a source-review batch.
9. User selects candidates to import.
10. Selected candidates enter the normal import protocol.
11. Import protocol handles PDF fetch, OCR, metadata approval, dedupe, project placement, and later indexing.

The user should always be able to:
- cancel a running research job
- inspect provider/source provenance for each candidate
- deselect any candidate before import
- manually edit candidate type or metadata before import where the standard import protocol supports it
- save the source batch for later review without importing immediately

### Search Order

Search order is opinionated:
1. Current project
2. Other local Exegesis projects selected by the user or configured as searchable
3. Zotero-imported literature already present in Exegesis projects
4. Open web search providers
5. Open-access scholarly providers that expose PDF or full-text locations
6. Optional provider-specific follow-up to confirm PDF/full-text availability for high-confidence candidates

Rationale:
- Exegesis should respect the user's existing intellectual workspace before adding new external noise.
- Previously imported literature and project notes are likely to be more relevant than open web results.
- Open web search is valuable, but it should not drown out the researcher's own corpus.

### Agent Roles

`ResearchSupervisor`
- validates the user request
- decides whether clarification is needed before search
- creates a bounded search plan
- assigns local and provider searches
- enforces budget, provider, and project-mode constraints
- merges worker outputs into one candidate set
- sends normalized candidates to dedupe/ranking

`LocalProjectResearcher`
- searches the current project first
- searches other Exegesis projects when allowed
- returns existing documents, literature records, notes, summaries, transcripts, and prior imported PDFs matching the request
- never mutates source projects
- preserves source project/document provenance

`WebSearchResearcher`
- runs provider queries against Tavily, Brave, and Exa
- returns URL-level leads with snippets and provider scores
- confirms direct PDF or open full-text availability before a lead becomes a selectable source candidate
- does not fetch full content unless the provider returns safe snippets as part of the search response or the user approves import
- respects provider budgets and rate limits

`OpenAccessSourceResearcher`
- searches scholarly/open-access providers only when they can return, filter for, or verify actual PDF/full-text locations
- target providers include OpenAlex, Semantic Scholar, arXiv, CORE, and Europe PMC where licensing and API terms allow
- provider adapters must reject metadata-only records unless a PDF URL, full-text URL, or direct importable source URL is present
- prioritizes DOI, title, author, abstract, publication venue, date, and PDF/full-text location data
- does not replace the later literature metadata import pipeline; it only feeds sources that can enter import

`CandidateNormalizer`
- converts provider-specific results into `ResearchCandidate` records
- canonicalizes URLs and DOI strings
- attaches source type, provider, confidence, and provenance
- labels candidate import path hints such as `literature_pdf`, `literature_web`, `web_article`, or `existing_project_document`

`DeduperRanker`
- merges duplicates across local projects, search providers, DOI metadata, PDFs, canonical URLs, title/author/year, and content hashes where available
- preserves all discovery provenance on the merged candidate
- ranks candidates for review using transparent heuristics
- flags uncertainty instead of hiding it

`ImportBatchBuilder`
- creates a user-reviewable import batch from deduped candidates
- separates candidates that are ready to import from candidates needing metadata/source confirmation
- hands approved candidates to the standard import protocol

### Data Model

`ResearchJob`:

```python
class ResearchJob:
    id: str
    project_id: str
    created_by_user_id: str
    query: str
    status: Literal[
        "draft",
        "planning",
        "searching_local",
        "searching_web",
        "deduping",
        "awaiting_review",
        "importing",
        "completed",
        "failed",
        "cancelled",
    ]
    search_scope: ResearchSearchScope
    provider_config: ResearchProviderConfig
    budgets: ResearchBudget
    plan: ResearchPlan | None
    candidate_batch_id: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
```

`ResearchSearchScope`:

```python
class ResearchSearchScope:
    current_project_id: str
    include_current_project: bool
    include_other_projects: bool
    included_project_ids: list[str]
    include_zotero_imported_literature: bool
    include_open_web: bool
    include_pdf_full_text_sources: bool
    allowed_document_types: list[str]
    project_mode_policy: Literal["confidential", "online_allowed", "lite_managed"]
```

`ResearchPlan`:

```python
class ResearchPlan:
    normalized_question: str
    subqueries: list[ResearchSubquery]
    local_queries: list[str]
    provider_queries: dict[str, list[str]]
    pdf_full_text_queries: list[str]
    exclusion_terms: list[str]
    must_include_terms: list[str]
    created_by_model: str | None
```

`ResearchSubquery`:

```python
class ResearchSubquery:
    id: str
    query: str
    intent: Literal[
        "background",
        "theory",
        "methodology",
        "empirical_study",
        "policy",
        "counterpoint",
        "recent_work",
        "source_followup",
    ]
    priority: int
    providers: list[str]
```

`ResearchCandidate`:

```python
class ResearchCandidate:
    id: str
    job_id: str
    source_kind: Literal[
        "existing_project_document",
        "existing_literature_record",
        "web_page",
        "pdf",
        "open_access_record",
        "zotero_record",
    ]
    import_kind_hint: Literal[
        "literature_pdf",
        "literature_web",
        "web_article",
        "existing_project_document",
        "unknown",
    ]
    title: str | None
    authors: list[str]
    year: str | None
    venue: str | None
    doi: str | None
    url: str | None
    canonical_url: str | None
    pdf_url: str | None
    full_text_url: str | None
    abstract_or_snippet: str | None
    provider_scores: dict[str, float]
    confidence: Literal["high", "medium", "low"]
    dedupe_key: str | None
    duplicate_candidate_ids: list[str]
    provenance: list[ResearchCandidateProvenance]
    requires_user_review: bool
    rejection_reason: str | None
    importable_source_confirmed: bool
    excluded_metadata_only: bool
    created_at: datetime
    updated_at: datetime
```

`ResearchCandidateProvenance`:

```python
class ResearchCandidateProvenance:
    provider: str
    provider_result_id: str | None
    query: str
    rank: int | None
    score: float | None
    snippet: str | None
    source_project_id: str | None
    source_document_id: str | None
    captured_at: datetime
```

`ResearchImportBatch`:

```python
class ResearchImportBatch:
    id: str
    job_id: str
    project_id: str
    status: Literal["awaiting_review", "partially_imported", "imported", "cancelled"]
    candidate_ids: list[str]
    selected_candidate_ids: list[str]
    imported_document_ids: list[str]
    created_at: datetime
    updated_at: datetime
```

### Provider Abstraction

Define a small provider interface:

```python
class ResearchSearchProvider(Protocol):
    name: str
    supports_web_search: bool
    supports_pdf_or_full_text_sources: bool
    supports_content_snippets: bool
    supports_pdf_filter: bool

    def search(self, query: str, options: ResearchSearchOptions) -> list[RawResearchResult]: ...
```

Provider adapter requirements:
- normalize provider response fields immediately
- capture provider request ID where available
- expose rate-limit and quota errors as typed failures
- never leak API keys into logs, transcripts, project files, or candidate records
- support per-provider enablement through Developer BYOK/BYOM configuration or Lite gateway policy, depending on build type

Initial provider candidates:
- `tavily`: primary LLM-oriented web search provider
- `brave`: independent web index provider
- `exa`: neural web search provider for semantically similar sources
- `openalex`: open-access scholarly discovery with `best_oa_location`, `locations`, `pdf_url`, and downloadable PDF filters
- `semantic_scholar`: scholarly paper discovery where `openAccessPdf` or equivalent open full-text links are present
- `arxiv`: preprint discovery with direct arXiv PDF links
- `core`: open-access repository discovery with downloadable PDFs/full text
- `europe_pmc`: life-sciences discovery where open full text or PDF/full-text links are available

Provider selection rules:
- Tavily is the default online web provider when configured.
- Brave and Exa are additive broad-discovery providers, not hard dependencies.
- Open-access scholarly providers are included only when they can return, filter for, or verify actual PDF/full-text locations.
- Metadata enrichment is allowed only as support for importing a real source, not as a standalone candidate type.
- Developer builds use user-provided keys and configured local/remote providers.
- Lite builds can only use providers exposed through the Lite Gateway policy.
- Confidential projects cannot send project text, draft text, private notes, or basket content to open web providers unless the user explicitly enables online research for that project.

Candidate inclusion rules:
- A candidate can enter the user-facing review batch only if it is already an Exegesis source, has a direct PDF URL, has an open full-text URL, or can be resolved to an importable source URL during provider follow-up.
- Metadata-only provider records must be discarded from the main candidate batch unless they enrich an already importable candidate.
- Tavily, Brave, and Exa are broad discovery providers; their results must still pass the importable-source gate before showing as selectable source candidates.
- OpenAlex, Semantic Scholar, arXiv, CORE, and Europe PMC adapters must prefer provider-side PDF/full-text filters where available.
- If a provider finds a promising source but cannot confirm PDF/full-text availability, keep it only in the audit/debug trail and show a count such as `7 metadata-only leads were excluded`.

### Query Planning

Query planning inputs:
- user research question
- active project title and document types
- optional selected document/excerpt text if the user explicitly includes it
- local project metadata and titles
- optional user-selected project scope

Query planning outputs:
- 3-8 subqueries by default
- local search queries
- provider search queries
- PDF/full-text source queries
- exclusions and must-have terms
- source-type priorities

Query planning constraints:
- keep queries short enough for provider APIs
- avoid sending private document content unless allowed by project policy
- prefer user-visible terms over opaque model-generated paraphrases
- store the plan so the user can audit what was searched

Clarification behavior:
- If the query is too broad, the supervisor may ask one concise clarification before searching.
- The user can bypass clarification with `Search broadly`.
- Clarification must not become a long chat workflow.

### Local Exegesis Project Search

Local search corpus:
- current project documents
- current project literature records
- current project summaries/memos/transcripts
- current project RAG index when available
- other selected Exegesis projects
- imported Zotero records already inside Exegesis
- prior research candidate batches saved in projects

Local search behavior:
- use FTS first
- use vector retrieval when Milestone 8 RAG/vector indexing is active
- include document type and project provenance in results
- return existing documents as candidates that can be opened or copied into the current project
- do not mutate other projects
- do not expose inaccessible projects

Existing-project candidate actions:
- `Open source project document`
- `Copy into current project`
- `Add to basket`
- `Skip`

Cross-project copy rules:
- copying into the current project creates a new local document/literature record with provenance pointing back to the source project/document
- imported copies get new IDs in the target project
- dedupe should warn if the source is already present in the target project

### Open Web Discovery

Open web search behavior:
- run provider searches in parallel within configured concurrency limits
- use `filetype:pdf` or provider-specific PDF filters when looking for PDF literature
- use domain filters when the user asks for specific institutions, journals, organizations, or public agencies
- collect enough snippet/source-location metadata for user review, not a final answer
- confirm PDF or open full-text availability before a result can be selected for import
- avoid fetching full content until the user approves candidates for import

Result fields shown to the user:
- title
- source/provider
- source type hint
- authors/year/venue if known
- DOI if known
- URL or canonical URL
- PDF availability indicator
- full-text availability indicator when the source is an importable HTML/open repository page rather than a PDF
- snippet or abstract
- why it matched
- duplicate/near-duplicate badge if applicable
- import readiness: `Ready`, `Needs source confirmation`, `Needs metadata review`, `Likely duplicate`, `Excluded metadata-only lead`

### Deduplication

Dedupe keys in priority order:
1. DOI normalized to lowercase without URL prefix
2. canonical URL after redirect normalization and tracking-param stripping
3. PDF content hash after import/fetch where available
4. title + first author + year normalized
5. title + venue + year normalized
6. provider-specific IDs mapped to known identifiers

Deduplication must:
- merge provider provenance into a single candidate
- preserve all discovered URLs/PDF URLs as alternates
- mark low-confidence merges for user review
- never silently discard local project matches
- distinguish exact duplicate from near duplicate

Tracking parameters to strip:
- common analytics parameters such as `utm_*`, `fbclid`, `gclid`, `mc_cid`, `mc_eid`
- provider redirect wrappers when safely unwrap-able

### Ranking And Review

Ranking factors:
- already present in local Exegesis project or related project
- DOI exists and a PDF/full-text location is available or likely importable
- PDF/full text availability
- recent enough for query intent when the user asks for recent sources
- source type match to requested intent
- multiple providers found the same source
- strong title/snippet match
- reputable scholarly/public/institutional source signals
- not already imported in target project

The ranker should return explainable labels:
- `Strong match: DOI found and PDF available`
- `Strong match: open full text available`
- `Local match: already in Data Memo project`
- `Possible duplicate: similar title already imported`
- `Needs review: metadata incomplete`
- `Excluded: metadata-only lead without PDF or full text`

### Import Batch UI Contract

The source batch should be rendered as a reviewable card/list in the Textual interface when that UI path is active.

Batch header:
- research query
- number of candidates
- number selected
- providers used
- local projects searched
- duplicate count
- provider errors, if any

Candidate row:
- checkbox/selection state
- title
- source kind
- document/literature type hint
- authors/year/venue/DOI if known
- provider/local provenance chips
- snippet/abstract preview
- duplicate/readiness badges
- actions: `Open`, `Import`, `Skip`, `Add to basket` where applicable

Batch actions:
- `Import selected`
- `Save batch for later`
- `Run more searches`
- `Export candidate list as Markdown`
- `Cancel`

Import handoff:
- selected PDF/web candidates become standard import requests
- selected local project documents can be copied or linked according to the existing import/copy protocol
- metadata-only leads cannot be selected for import unless they have been resolved to an importable PDF/full-text source
- import progress must be visible per candidate

### Standard Import Protocol Handoff

For each selected candidate, create an import request:

```python
class ResearchCandidateImportRequest:
    source: Literal["deep_research_candidate"]
    candidate_id: str
    project_id: str
    target_document_type: Literal["literature", "memo", "summary", "transcript", "draft"]
    url: str | None
    pdf_url: str | None
    full_text_url: str | None
    metadata: LiteratureMetadataDraft | None
    provenance: list[ResearchCandidateProvenance]
    duplicate_candidate_ids: list[str]
    user_confirmed: bool
```

Import protocol expectations:
- PDF URLs route through OCR/literature import as needed.
- Open full-text web pages route through the import protocol's supported web/document path when available.
- Metadata-only leads are excluded before import request creation.
- RAG indexing runs only after import succeeds and Milestone 8 is active.
- Import failures remain per-candidate failures and do not fail the whole batch.

### Project Mode, Privacy, And Credentials

Confidential mode:
- local project search is allowed
- open web search using only the user's query is allowed if the user explicitly permits it
- private project text, document excerpts, basket contents, transcripts, and unpublished notes must not be sent to open web providers without explicit project-level online research enablement

Developer build:
- uses Milestone 15 provider credential storage
- user configures Tavily/Brave/Exa and optional PDF/full-text scholarly provider keys as available
- no hosted Lite provider calls unless explicitly using Lite build behavior

Lite build:
- uses the Lite Gateway for any managed provider access
- provider budgets and allowed providers are controlled by the gateway
- no provider keys are stored in the app bundle or project files

Credential handling:
- never store search API keys in project files
- never include provider keys in logs or transcripts
- redact signed URLs and sensitive query parameters
- provider request IDs are safe to store when they do not leak credentials

### Rate Limits, Budgets, And Cancellation

Budget defaults:
- max subqueries: 6
- max providers per job: 3
- max results per provider query: 10
- max total raw results: 200
- max deduped candidates shown by default: 50
- max job runtime before user confirmation: 5 minutes
- max concurrent provider calls: configurable, default 4

Budget behavior:
- user can choose a small, standard, or broad search preset
- broad search should warn about provider cost/latency
- provider failures should produce partial results if at least one provider succeeds
- cancellation stops new provider calls and marks the job cancelled
- already-created import batches remain reviewable if cancellation happens after candidates are available

### Error Handling

Typed errors:
- `provider_not_configured`
- `provider_quota_exhausted`
- `provider_rate_limited`
- `provider_timeout`
- `provider_schema_changed`
- `project_scope_denied`
- `online_research_not_allowed`
- `no_candidates_found`
- `dedupe_failed`
- `import_batch_failed`

User-facing copy:
- `No source candidates were found. Try broader terms or enable additional search providers.`
- `Open web search is disabled for this confidential project.`
- `Tavily is not configured. Configure a search provider or run local project search only.`
- `Some providers failed, but Exegesis found candidates from other sources.`
- `This source may already be in the project. Review the duplicate before importing.`

### Auditing And Provenance

Every research job should preserve:
- original user query
- generated search plan
- local projects searched
- providers used
- provider query strings
- provider errors
- candidate provenance
- dedupe decisions
- ranking explanation
- user selection decisions
- import request IDs
- resulting document IDs

Audit storage must support:
- reopening a saved candidate batch
- explaining why a source appeared
- rerunning the same search later
- comparing candidate batches over time

### Command And API Surface

Command palette entries:
- `Start Open Access Deep Research`
- `Open Saved Research Batches`
- `Configure Research Search Providers`
- `Cancel Running Research Job`

CLI/API concepts:

```bash
exegesis research start --project <project-id> --query "..." --scope current-and-selected-projects --providers tavily,brave,exa
exegesis research status <job-id>
exegesis research candidates <job-id>
exegesis research import <batch-id> --selected <candidate-id>...
exegesis research cancel <job-id>
```

Backend service boundaries:
- `research/planner.py`
- `research/supervisor.py`
- `research/providers/tavily.py`
- `research/providers/brave.py`
- `research/providers/exa.py`
- `research/providers/scholarly.py`
- `research/local_project_search.py`
- `research/normalizer.py`
- `research/dedupe.py`
- `research/ranking.py`
- `research/import_batch.py`
- `research/audit.py`

Shared contract boundaries:
- `shared/src/exegesis_shared/research/contracts.py`
- `shared/src/exegesis_shared/research/models.py`
- `shared/src/exegesis_shared/research/events.py`

Client/Textual boundaries:
- `client-textual/src/exegesis_textual/research/**`
- no runtime UI work until lane activation

### Implementation Batches

1. Spec and lane scaffolding
   - Add docs, disabled lane registration, ownership, lane profile, and scope policy.
2. Research contracts
   - Add job, plan, candidate, provenance, batch, and import request models.
3. Local project search first
   - Search current and selected Exegesis projects through existing FTS/RAG paths.
4. Provider abstraction
   - Add provider interface, typed errors, credential boundaries, and fake provider tests.
5. Tavily provider adapter
   - Implement Tavily search adapter with rate-limit/quota error mapping and source-confirmation gating.
6. Additional provider adapters
   - Add Brave, Exa, OpenAlex, Semantic Scholar, arXiv, CORE, and Europe PMC adapters as configured optional providers, constrained to PDF/full-text-capable results.
7. Supervisor and query planner
   - Add bounded query planning, worker fan-out, cancellation, and checkpoint state.
8. Normalization, dedupe, and ranking
   - Merge candidates across local/project/web/scholarly results with explainable decisions.
9. Import batch builder
   - Present deduped candidates and hand selected items into the standard import protocol.
10. Textual review surface
   - Add source batch review UI once client lanes are active.
11. Security, privacy, and audit hardening
   - Enforce project mode policies, credential redaction, provider budgets, and audit logs.
12. End-to-end acceptance tests
   - Validate local-first discovery, provider fan-out, dedupe, candidate review, and import handoff.

### Test Plan

Scaffolding tests:
- `feat-open-access-deep-research` exists in lane defaults and profiles.
- `feat-open-access-deep-research` is disabled in router config and example config.
- Scope-check policy allows only research/discovery/provider docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is post-MVP and not part of Sprint 0-5.

Planning tests:
- broad query produces bounded subqueries.
- too-broad query can request one clarification.
- confidential project does not send private project text to provider planning.
- generated plan is persisted with provider/local query strings.

Local search tests:
- current project is searched before other projects.
- other selected Exegesis projects are searched when allowed.
- inaccessible projects are not searched.
- local project results include source project/document provenance.
- copying a local result into current project creates a new ID and preserves provenance.

Provider tests:
- Tavily adapter maps search results into raw provider results.
- Brave adapter maps web results into raw provider results.
- Exa adapter maps neural search results into raw provider results.
- open-access scholarly provider adapters map DOI/title/author/year plus PDF/full-text URLs into raw provider results.
- metadata-only provider records are excluded unless they enrich an importable candidate.
- OpenAlex adapter accepts only works with usable `pdf_url`, downloadable PDF content, or open full-text location.
- Semantic Scholar adapter accepts only papers with `openAccessPdf` or equivalent open full-text links.
- arXiv adapter emits direct PDF links.
- CORE adapter emits downloadable PDF/full-text links.
- Europe PMC adapter emits open full-text/PDF-capable records only.
- provider quota/rate-limit/timeouts become typed partial failures.
- provider keys and signed URLs are redacted from logs.

Deduplication tests:
- DOI duplicates merge.
- canonical URL duplicates merge.
- title/author/year near duplicates are marked for review.
- local project matches are never silently discarded.
- merged candidates retain every provider provenance entry.

Ranking/review tests:
- candidates with DOI/PDF/provider agreement rank above weak web-only hits.
- duplicate candidates show duplicate badges.
- incomplete metadata shows `Needs review`.
- empty results render a useful no-results state.

Import handoff tests:
- selected PDF candidate enters standard PDF/OCR/literature import path.
- selected local project document can be copied into the current project.
- per-candidate import failures do not fail the entire batch.
- imported documents preserve research job and candidate provenance.

Privacy/security tests:
- confidential project blocks provider calls that include private project content.
- online research disabled state blocks open web provider fan-out.
- Developer credentials are loaded from secure provider config only.
- Lite provider calls go through the Lite Gateway policy only.
- API keys do not appear in transcripts, logs, project files, or candidate records.

Acceptance criteria:
- User can run local-first source discovery for a research question.
- User can include selected other Exegesis projects in the discovery scope.
- User can expand discovery to Tavily, Brave, and Exa.
- User can include PDF/full-text-capable scholarly providers when configured.
- Exegesis dedupes results across local projects and open web providers.
- Exegesis presents a reviewable source batch with provenance and import readiness.
- Metadata-only leads are not selectable source candidates.
- User can approve selected candidates for standard import.
- Exegesis imports selected candidates through the mature import/OCR/literature/RAG pipeline.
- The milestone does not generate synthesis, summaries, or final reports.

## Milestone 20: Quantitative Analysis

Lane: `feat-quant-analysis` (disabled)

Status: post-MVP planned, disabled

### Summary

Add a first-class, lean quantitative analysis surface for CSV datasets inside Exegesis projects. This milestone is intentionally not a full statistics workbench. It supports basic descriptive statistics, simple inferential tests, a few readable charts, and an analysis transcript that can be saved as a summary artifact.

The goal is to let researchers keep small quantitative checks inside the same project workflow as memos, transcripts, summaries, literature, basket context, and later RAG. It should feel like a notebook sequence for basic tests, not like a replacement for R, SPSS, Stata, Jamovi, or JASP.

This pass is a disabled spec only. It must not activate runtime dataset import, statsmodels execution, plotting, UI widgets, or summary generation until `feat-quant-analysis` is intentionally enabled after the MVP launch gate.

### Product Scope

In scope:
- add `Datasets` as a first-class project browser section.
- import CSV files only.
- store dataset metadata and variable metadata in the project database.
- auto-detect variable type as `categorical`, `ordinal`, or `scale`.
- show raw data in the document view.
- allow changing variable type from the raw-data document view.
- expose analysis selection in the inspector.
- run basic descriptive and inferential analyses through Python.
- generate markdown result tables.
- generate basic charts.
- append analyses to a dataset-specific transcript sequence.
- save the analysis sequence as a summary in the project summaries section.
- explain effect-size interpretation as small, medium, or large in each applicable result.

Out of scope:
- non-CSV imports.
- live spreadsheet editing.
- formula columns.
- weighted survey analysis.
- missing-data imputation beyond clear listwise deletion rules.
- regression beyond simple linear correlation.
- multi-model workflows.
- factor analysis, reliability, mixed models, non-parametric tests, logistic regression, or generalized linear models.
- WYSIWYG chart editing.
- publication-grade plotting controls.
- automatic statistical interpretation prose beyond compact effect-size guidance.
- LLM-generated quantitative conclusions.

### Project Browser Model

Add a first-class `Datasets` section:

```text
Project
  Drafts
  Memos
  Summaries
  Transcripts
  Literature
  Datasets
```

Dataset entries should behave like documents for selection and inspector updates:
- selecting a dataset opens the raw-data view in the document pane.
- selecting a dataset updates the inspector to dataset controls.
- saved analysis summaries appear under `Summaries`.
- analysis transcript records remain attached to the dataset, not mixed into the notebook chat transcript.

### Data Model

Core records:

```ts
type DatasetDocument = {
  id: string;
  projectId: string;
  title: string;
  slug: string;
  sourceFilename: string;
  sourceContentHash: string;
  rowCount: number;
  columnCount: number;
  importedAt: string;
  updatedAt: string;
};

type DatasetVariableType = "categorical" | "ordinal" | "scale";

type DatasetVariable = {
  id: string;
  datasetId: string;
  name: string;
  originalName: string;
  variableType: DatasetVariableType;
  detectedType: DatasetVariableType;
  userOverriddenType: DatasetVariableType | null;
  missingCount: number;
  distinctCount: number;
  examples: string[];
  createdAt: string;
  updatedAt: string;
};

type DatasetAnalysisRun = {
  id: string;
  datasetId: string;
  sequenceId: string;
  analysisType: DatasetAnalysisType;
  label: string;
  variableIds: string[];
  groupingVariableIds: string[];
  covariateVariableIds: string[];
  parameters: Record<string, unknown>;
  resultMarkdown: string;
  effectSizeMarkdown: string | null;
  chartArtifactIds: string[];
  createdAt: string;
};

type DatasetAnalysisSequence = {
  id: string;
  datasetId: string;
  title: string;
  runs: DatasetAnalysisRun[];
  createdAt: string;
  updatedAt: string;
};

type DatasetChartArtifact = {
  id: string;
  datasetId: string;
  analysisRunId: string;
  chartType: "bar" | "density" | "scatter";
  artifactPath: string;
  altText: string;
  createdAt: string;
};
```

`DatasetAnalysisType`:

```ts
type DatasetAnalysisType =
  | "descriptive"
  | "frequency_table"
  | "contingency_table"
  | "t_test"
  | "anova"
  | "chi_squared"
  | "linear_correlation";
```

### CSV Import

CSV import rules:
- accept `.csv` only for Milestone 20.
- use UTF-8 by default, with a clear error for unreadable files.
- preserve original column names but create normalized internal variable names.
- require a header row.
- reject empty files.
- reject files with no usable columns.
- store the original file hash for dedupe and provenance.
- cap initial MVP dataset size with a configurable row/column guardrail.

Suggested initial guardrails:

```ts
MAX_DATASET_ROWS = 100000;
MAX_DATASET_COLUMNS = 250;
```

If the file exceeds a guardrail, show a clear message and do not import silently.

### Variable Type Detection

Auto-detect each variable as `categorical`, `ordinal`, or `scale`.

Detection heuristics:
- `scale`
  - mostly numeric values.
  - enough distinct values to behave continuously.
  - examples: age, score, income, time, percentage.
- `ordinal`
  - values match common ordered labels or numeric low-cardinality rating scales.
  - ordered labels include patterns like `strongly disagree` to `strongly agree`, `low` to `high`, `never` to `always`.
  - low-cardinality integer scales such as 1-5, 1-7, 0-10 should default to `ordinal`.
- `categorical`
  - strings without clear order.
  - booleans.
  - low-cardinality nominal values.

Detection must be editable:
- raw-data document view exposes the current type for each column.
- user changes set `userOverriddenType`.
- analyses use `userOverriddenType` when present, otherwise `detectedType`.

### Document View

Dataset document view:
- shows a raw-data table.
- freezes or clearly labels column headers.
- shows variable type controls in the header or a compact variable metadata panel.
- supports changing variable type for one column at a time.
- does not perform spreadsheet editing.
- does not modify cell values.
- supports selecting a variable or cell enough to update the inspector.

The document view should remain simple and truthful:
- raw rows.
- variable names.
- variable types.
- missing-value counts where practical.

### Inspector Workflow

When a dataset is selected, the inspector shows:
- dataset title.
- row count.
- column count.
- selected variable metadata if a variable is selected.
- analysis type selector.
- dependent variable selector when applicable.
- independent/grouping variable selector when applicable.
- covariate selector only for analysis types that support covariates.
- split-by selector for descriptive statistics.
- `Add Test to Sequence` action.
- current sequence summary.

Covariate rule:
- v1 includes the selector contract but only enables it for analyses that explicitly support covariates.
- because Milestone 20 intentionally stays lean, basic tests may show covariates as unavailable with copy: `Covariates are not available for this basic test.`
- do not silently ignore selected covariates.

### Analysis Support

Use `statsmodels` for statistical tests where applicable and a standard Python plotting tool for charts. Preferred plotting stack:
- `matplotlib` for stable artifact generation.
- optional `seaborn` for density curves if already accepted by packaging constraints.

Use `pandas` and `numpy` for dataset preparation and descriptive calculations.

#### Descriptive Statistics

For scale variables, compute:
- N
- mean
- median
- mode
- standard deviation
- standard error
- min
- max
- skew
- kurtosis

Descriptive split support:
- no split: overall statistics.
- split by one categorical variable.
- split by one ordinal variable.

Output:
- markdown table.
- optional density curve for one scale variable.
- optional bar chart when grouped counts are requested.

No p-value is required for descriptive-only output.

#### Frequency Tables

For categorical or ordinal variables:
- counts.
- valid percent.
- missing count.

Output:
- markdown table.
- optional bar chart.

No p-value is required unless the user runs a chi-squared test.

#### Contingency Tables

For two categorical or ordinal variables:
- cross-tab counts.
- row percentages.
- column percentages.
- total percentages where useful.

Output:
- markdown table.
- optional grouped or stacked bar chart.

No p-value is required unless the user runs a chi-squared test.

#### t-test

Supported tests:
- one-sample t-test for one scale variable against a specified comparison mean.
- independent-samples t-test for one scale dependent variable split by a two-level categorical/ordinal grouping variable.

Output:
- N by group where applicable.
- mean by group where applicable.
- t statistic.
- degrees of freedom.
- p-value.
- Cohen's d.
- small/medium/large effect-size interpretation.

Default missing-data rule:
- listwise deletion for selected variables.

#### ANOVA

Supported test:
- one-way ANOVA for one scale dependent variable by one categorical/ordinal grouping variable with two or more groups.

Output:
- N by group.
- mean by group.
- F statistic.
- degrees of freedom.
- p-value.
- eta squared.
- small/medium/large effect-size interpretation.

Do not implement post-hoc tests in Milestone 20.

#### Chi-Squared

Supported test:
- chi-squared test of independence for two categorical or ordinal variables.

Output:
- contingency table.
- chi-squared statistic.
- degrees of freedom.
- p-value.
- Cramer's V.
- small/medium/large effect-size interpretation.

Warn when expected-cell assumptions are weak:
- show expected count warning when too many expected cells are below 5.
- do not implement Fisher's exact test in Milestone 20.

#### Linear Correlation

Supported test:
- Pearson correlation for two scale variables.

Output:
- N.
- Pearson r.
- p-value.
- r-squared as effect/context measure.
- small/medium/large effect-size interpretation for `r`.
- scatter plot.

Do not implement regression models in Milestone 20.

### Effect Size Guidance

Every inferential result should include compact interpretation context:

```md
Effect size guide: small, medium, and large are conventional benchmarks, not proof of practical importance.
```

Default benchmark table:

| Effect size | Small | Medium | Large |
| --- | ---: | ---: | ---: |
| Cohen's d | 0.20 | 0.50 | 0.80 |
| eta squared | 0.01 | 0.06 | 0.14 |
| Cramer's V | 0.10 | 0.30 | 0.50 |
| Pearson r | 0.10 | 0.30 | 0.50 |

The result should label the observed effect:

```md
Effect size: Cohen's d = 0.42, conventionally between small and medium.
```

### Charting

Supported chart types only:
- bar chart.
- density curve.
- scatter plot for linear correlation.

Chart rules:
- generated as static image artifacts.
- stored as project artifacts.
- referenced from the analysis run.
- include alt text.
- avoid theme complexity.
- no interactive plotting in v1.

Chart generation must be deterministic enough for tests:
- fixed figure size.
- stable labels.
- stable output path pattern.

### Analysis Transcript Sequence

Each dataset has one or more analysis sequences.

Sequence behavior:
- user configures an analysis in the inspector.
- user clicks `Add Test to Sequence`.
- Exegesis runs the analysis.
- result table, effect-size guidance, and chart reference are appended to the sequence.
- user can add more tests in order.
- sequence is visible like a transcript under the dataset context.

Sequence entries should be structured, not just a flat blob:

```ts
type DatasetSequenceEntry =
  | { kind: "analysis_run"; runId: string }
  | { kind: "note"; markdown: string }
  | { kind: "status"; message: string };
```

### Save As Summary

At the bottom of the sequence, provide:

```text
Save Sequence as Summary
```

Saved summary content:
- summary title.
- dataset title and row/column counts.
- test listing.
- result markdown tables.
- effect-size guidance.
- chart references or embedded figure links.
- clear note that results are basic statistical output, not an LLM interpretation.

The saved summary appears in the project `Summaries` section.

### Command Palette and Shortcuts

Add command palette entries:
- `Import Dataset CSV`
- `Open Dataset`
- `Change Variable Type`
- `Add Analysis to Sequence`
- `Save Analysis Sequence as Summary`

Shortcut rows are not required in Milestone 20 unless later UI planning decides dataset analysis needs dedicated shortcuts.

### Engine API and CLI Contracts

Minimum CLI/API contracts:

```bash
exegesis dataset import --project <project-id> --file <path.csv>
exegesis dataset variables <dataset-id>
exegesis dataset set-variable-type <dataset-id> <variable-name> --type categorical|ordinal|scale
exegesis dataset analyze <dataset-id> --type descriptive --dependent <var> [--split-by <var>]
exegesis dataset analyze <dataset-id> --type t-test --dependent <var> [--group <var>] [--comparison-mean <number>]
exegesis dataset analyze <dataset-id> --type anova --dependent <var> --group <var>
exegesis dataset analyze <dataset-id> --type chi-squared --x <var> --y <var>
exegesis dataset analyze <dataset-id> --type linear-correlation --x <var> --y <var>
exegesis dataset sequence append <sequence-id> <analysis-run-id>
exegesis dataset sequence save-summary <sequence-id>
```

Internal service contracts:
- `DatasetImportService`
- `VariableTypeDetector`
- `DatasetAnalysisService`
- `EffectSizeInterpreter`
- `DatasetChartService`
- `DatasetSequenceService`
- `DatasetSummaryExportService`

### Error Handling

User-facing errors:
- `Only CSV datasets are supported in this version.`
- `This CSV file could not be read as UTF-8.`
- `This CSV file does not contain a header row.`
- `This dataset is too large for the current quantitative analysis lane.`
- `Choose a scale variable for this analysis.`
- `Choose a categorical or ordinal grouping variable for this analysis.`
- `This test requires exactly two groups.`
- `This test needs at least two non-missing values per selected variable.`
- `Covariates are not available for this basic test.`

All analysis errors should append a status entry to the sequence only when the user explicitly tried to add a test.

### Privacy and Provider Boundaries

Quantitative analysis is local-first:
- CSV contents are not sent to online providers.
- statsmodels and plotting run locally.
- saved summaries stay in the project.
- LLM interpretation is out of scope for Milestone 20.

Developer/Lite boundary:
- Developer and Lite builds use the same local analysis engine for CSV datasets.
- Lite managed provider credentials are not involved.
- no Paddle, License Gateway, OCR usage, or online model calls are needed for quantitative analysis.

### Lane Wiring Plan

Add disabled lane:
- `feat-quant-analysis`

Owned paths:
- `engine/src/exegesis_engine/datasets/**`
- `engine/src/exegesis_engine/quant_analysis/**`
- `client-textual/src/exegesis_textual/datasets/**`
- `shared/src/exegesis_shared/datasets/**`
- `shared/src/exegesis_shared/quant_analysis/**`
- `docs/quant_analysis/**`

Scope policy:
- lane may edit only the above owned paths once activated.
- roadmap/spec/config scaffolding remains integrator-owned during this planning pass.

Lane profile:
- risk: `MEDIUM`
- routing impact: none while disabled
- roadmap item: Milestone 20

### Implementation Batches

1. Spec and lane scaffolding
   - Add docs, disabled lane registration, ownership, lane profile, and scope policy.
2. Dataset contracts
   - Add dataset, variable, analysis run, sequence, and chart artifact models.
3. CSV import
   - Add CSV loader, validation, provenance, hash, row/column guardrails, and tests.
4. Variable type detection
   - Add categorical/ordinal/scale detection and override persistence.
5. Raw dataset document view contract
   - Add table read model and variable-type editing contract once client lanes are active.
6. Descriptive and frequency analysis
   - Add descriptive, frequency, contingency tables, markdown output, and tests.
7. Inferential tests
   - Add t-test, ANOVA, chi-squared, and Pearson correlation with p-values and effect sizes.
8. Chart artifacts
   - Add bar, density, and scatter plot generation with deterministic artifact storage.
9. Analysis sequence
   - Add appendable sequence entries, status entries, and ordered display contracts.
10. Save sequence as summary
   - Add markdown summary creation and project summary registration.
11. Textual inspector controls
   - Add analysis picker, variable selectors, split-by controls, and sequence actions once client lanes are active.
12. End-to-end acceptance tests
   - Validate CSV import, variable typing, analyses, charts, sequence, and summary save.

### Test Plan

Scaffolding tests:
- `feat-quant-analysis` exists in lane defaults and profiles.
- `feat-quant-analysis` is disabled in router config and example config.
- Scope-check policy allows only dataset/quant-analysis docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is post-MVP and not part of Sprint 0-5.

CSV import tests:
- CSV import creates a dataset under `Datasets`.
- non-CSV import is rejected.
- empty CSV is rejected.
- CSV without header is rejected.
- row/column guardrails reject oversized datasets.
- source filename and content hash are preserved.

Variable detection tests:
- numeric continuous values detect as `scale`.
- low-cardinality rating values detect as `ordinal`.
- ordered labels detect as `ordinal`.
- nominal labels detect as `categorical`.
- user override wins over detected type.

Document view tests:
- dataset selection opens raw data.
- variable type can be changed without modifying raw cell values.
- inspector updates when a dataset variable is selected.

Descriptive tests:
- overall descriptive statistics compute N, mean, median, mode, SD, SE, min, max, skew, and kurtosis.
- descriptive statistics can split by categorical variable.
- descriptive statistics can split by ordinal variable.
- frequency tables output counts and percentages.
- contingency tables output cross-tab counts and percentages.

Inferential tests:
- one-sample t-test outputs t, df, p-value, Cohen's d, and effect-size guidance.
- independent-samples t-test requires exactly two groups.
- ANOVA outputs F, df, p-value, eta squared, and effect-size guidance.
- chi-squared outputs chi-squared, df, p-value, Cramer's V, and effect-size guidance.
- linear correlation outputs Pearson r, p-value, r-squared, and effect-size guidance.
- missing values are handled by explicit listwise deletion for selected variables.

Chart tests:
- bar chart artifact is generated for frequency/grouped output.
- density curve artifact is generated for scale descriptive output.
- scatter plot artifact is generated for correlation output.
- chart artifacts include alt text.

Sequence tests:
- adding a test appends a structured analysis run entry.
- failed user-triggered analyses append a status entry.
- multiple tests remain ordered.
- saving a sequence creates a summary document under `Summaries`.
- saved summary includes test listing, markdown tables, effect-size guidance, and chart references.

Privacy tests:
- CSV data is not sent to online providers.
- Lite gateway endpoints are not called for quantitative analysis.
- summaries persist locally in project storage.

Acceptance criteria:
- User can import a CSV into the `Datasets` project section.
- Exegesis auto-detects variable types and lets the user override them.
- User can inspect raw data in the document view.
- User can run descriptive statistics overall and split by categorical/ordinal variables.
- User can run frequency and contingency tables.
- User can run t-test, ANOVA, chi-squared, and linear correlation.
- Inferential results show p-values and effect sizes.
- Effect sizes include small/medium/large guidance.
- User can generate basic bar, density, and scatter plots.
- User can build a sequence of tests.
- User can save the sequence as a summary.
- No runtime dataset analysis behavior is active until the lane is enabled.
