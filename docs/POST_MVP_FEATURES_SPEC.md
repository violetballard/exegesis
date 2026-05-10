# Post-MVP Feature Specs

This document defines disabled post-MVP work that should not be activated until the summer MVP and CoP launch gate have produced real usage feedback.

Current post-MVP lanes:
- Milestone 19: `feat-browser-pdf-capture`
- Milestone 20: `feat-python-sidecar-api`
- Milestone 21: `feat-native-workstation`
- Milestone 22: `feat-open-access-deep-research`
- Milestone 23: `feat-quant-analysis`
- Milestone 24: `feat-advanced-qual-visuals`
- Milestone 25: `feat-confidential-collaboration`
- Milestone 26: `feat-ipad-native-lite`

Activation rule:
- These lanes remain disabled in router config.
- Do not schedule, implement, or polish these features until explicitly enabled after the MVP launch gate.
- Runtime browser extension, native bridge, import handoff, packaging behavior, Python sidecar API behavior, PyInstaller sidecar packaging, Studio Workstation supervision, native Workstation packaging/signing/distribution, open web search, multi-agent research orchestration, source ranking, import-batch behavior, CSV dataset analysis, statistical testing, plot generation, advanced qualitative coding visualizations, codebook generation, confidential collaboration/sync behavior, and native iPad Lite behavior must remain inactive until the relevant lane is intentionally activated.

## Milestone 19: Browser PDF Capture Extension

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
- Edge can follow the Chrome build path later, but Edge support is not required for Milestone 19 acceptance.

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
- Native messaging is not required for the first Milestone 19 implementation unless loopback handoff fails acceptance criteria.

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
- Milestone 17 desktop packaging must include extension artifacts when Milestone 19 is active.
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


## Milestone 20: Python Backend Sidecar API

Lane: `feat-python-sidecar-api` (disabled)

Intent:
- Add a localhost-only FastAPI sidecar for Python-backed Exegesis features so the native Workstation can run, monitor, and talk to the Python backend without embedding Python directly.
- Package the sidecar as a standalone binary with PyInstaller for Developer and Lite desktop distributions.
- Make the sidecar the required HTTP boundary for Python features added after this milestone.
- Keep the sidecar small, local, observable, and boring: it should be easy for Workstation to start, health-check, stop, and restart.

Non-activation rule:
- This milestone is post-MVP specification and lane scaffolding only.
- Do not implement runtime FastAPI endpoints, PyInstaller builds, Workstation process management, or feature endpoint migration until this lane is explicitly enabled.

### Product Boundary

The sidecar owns:
- localhost-only FastAPI application startup
- stable health and readiness endpoints
- local feature endpoint routing for Python-backed features
- request/response schemas for Python feature calls
- lightweight process metadata for Workstation monitoring
- graceful shutdown behavior for the desktop app
- sanitized structured logging suitable for local diagnostics

The native Studio Workstation owns:
- launching the packaged sidecar binary
- selecting an ephemeral or configured localhost port
- passing startup configuration and secrets through the approved secure channel
- monitoring sidecar health
- restarting the sidecar when it fails within configured limits
- presenting user-facing local backend status when needed

The engine owns:
- actual feature implementation behind sidecar routes
- SQLite/project storage access rules
- confidential-mode enforcement
- provider/key resolution through Developer or Lite configuration boundaries
- audit events for feature actions

Non-goals:
- no remote server exposure
- no public network binding
- no browser-accessible unauthenticated broad API surface
- no cloud hosting
- no replacement for the Lite License Gateway
- no general plugin marketplace runtime
- no attempt to make every old internal engine function an endpoint in the first batch
- no WebSocket requirement unless a later feature explicitly needs streaming progress

### Localhost Security Model

Binding:
- The sidecar binds only to `127.0.0.1` by default.
- `0.0.0.0`, LAN addresses, and public interfaces are rejected in packaged builds.
- Developer debug builds may allow explicit loopback aliases only through a documented flag.

Authentication:
- Workstation generates a per-launch random bearer token or equivalent local session secret.
- All non-health endpoints require the token.
- The token is passed to the sidecar through process environment, stdin, or another local-only secure startup channel.
- The token must not be written to logs, project files, transcripts, or crash reports.

Origin and CORS:
- CORS is disabled by default.
- If a local UI bridge or webview needs browser-origin access, allow only the exact local origin selected by Workstation.
- Reject unknown origins for browser-reachable endpoints.

Request boundaries:
- Enforce request size limits per endpoint.
- Enforce path normalization for any file/path inputs.
- Do not accept arbitrary filesystem paths from the UI bridge without Workstation/engine validation.
- Redact API keys, license tokens, local bearer tokens, and file paths where logs could become user-shareable.

### Required Endpoints

Health endpoints:
- `GET /healthz`
  - unauthenticated liveness check
  - returns process is alive and event loop can answer
- `GET /readyz`
  - authenticated readiness check
  - verifies engine initialization, project storage availability when configured, and provider configuration sanity without making paid model calls
- `GET /version`
  - authenticated version/build metadata
  - includes app version, sidecar schema version, build flavor, and feature route versions

Process endpoints:
- `POST /shutdown`
  - authenticated graceful shutdown requested by Workstation
  - refuses requests without local token
- `GET /features`
  - authenticated route capability manifest
  - lists available feature groups and route schema versions

Minimum response contracts:

```json
{
  "status": "ok",
  "sidecar_schema_version": "1",
  "uptime_seconds": 12.4
}
```

```json
{
  "status": "ready",
  "engine_initialized": true,
  "storage_ready": true,
  "build_flavor": "developer",
  "feature_routes": {
    "imports": "1",
    "rag": "1",
    "research": "1"
  }
}
```

### Feature Endpoint Rule After This Milestone

All Python-backed feature additions or behavior changes after Milestone 20 must include sidecar exposure when the feature is reachable from Studio Workstation or the native SwiftUI client.

Required for each later Python feature:
- route group under `/features/{feature_name}/...` or another documented stable prefix
- request and response schema in shared contracts
- authentication and request size policy
- confidential-mode/provider boundary checks
- local audit event or status entry when the feature mutates project state
- unit tests for schemas and handlers
- integration test showing Workstation or SwiftUI-facing client code can call the sidecar route
- version entry in `GET /features`

Applies immediately to later post-MVP specs:
- Milestone 22 Deep Research must expose job creation, status, cancellation, candidate batch retrieval, and import-batch handoff through the sidecar.
- Milestone 23 Quantitative Analysis is native Swift/IMSL by default, not Python-backed by default. It must use the Python sidecar only if a later implementation adds Python-backed preprocessing or artifact generation.
- Milestone 24 Advanced Qualitative Coding Visualizations must expose aggregation, matrix, graph, comparison, and codebook-generation data through the sidecar when those features need Python-backed processing.
- Milestone 25 Confidential Collaboration must expose only local Studio Workstation coordination, health, audit, and sync-status hooks through the sidecar; any networked collaboration service contracts must be designed separately in that lane before implementation.
- Any later OCR, RAG, import, export, citation, or provider-backed Python feature touched after this point must either expose its Workstation-facing behavior through the sidecar or explicitly document why it remains internal-only.

### PyInstaller Packaging

Packaging target:
- build a standalone macOS sidecar binary for Studio Workstation
- include it in the macOS Studio app bundle
- Studio Workstation starts the binary directly rather than requiring users to run Python

Build inputs:
- FastAPI app entrypoint
- engine package modules required by sidecar routes
- pydantic/shared schema modules
- runtime assets required for local feature execution
- PyInstaller spec files per platform if needed

Build outputs:
- macOS sidecar binary bundled inside the Studio `.app`

Packaging rules:
- sidecar binary version must match the desktop app version or pass a compatibility matrix check
- Workstation refuses to start incompatible sidecar schema versions with a clear error
- crash logs are local and sanitized
- packaged sidecar must not contain Developer user API keys, Lite managed provider keys, local bearer tokens, or project data

### Workstation Supervision Contract

Startup flow:
1. Workstation selects a free loopback port.
2. Workstation generates local auth token.
3. Workstation launches the sidecar binary with port, token, build flavor, app data directory, and log directory.
4. Workstation polls `/healthz` until live or timeout.
5. Workstation polls `/readyz` until ready or shows a local backend error.
6. Workstation provides sidecar URL and token only to trusted in-process UI/client code.

Monitoring:
- poll `/healthz` on a short interval while active
- poll `/readyz` less frequently or when project/provider state changes
- restart on unexpected exit with exponential backoff and a maximum restart count
- surface clear status: starting, ready, unhealthy, restarting, stopped, incompatible, failed

Shutdown:
- use `POST /shutdown` first
- after timeout, terminate the sidecar process
- avoid orphaned sidecar processes after Workstation exits

### Logging and Diagnostics

Log requirements:
- structured local logs with timestamp, route group, request id, duration, status, and sanitized error class
- no request bodies in logs by default
- no secrets or provider keys in logs
- no full document text in logs
- optional debug logging only in Developer mode and still redacted

Diagnostics:
- `GET /version` reports sidecar and engine build metadata
- Workstation can include sidecar health/version in a support bundle
- support bundles must redact local auth token, provider keys, and project content

### Developer/Lite Boundary

Developer:
- sidecar uses BYOK/BYOM provider configuration from Milestone 15
- local OpenAI-compatible endpoints remain available through Developer configuration
- sidecar never calls Lite License Gateway managed-provider proxy endpoints

Lite:
- sidecar uses Lite gateway-mediated provider access where Lite features require managed remote services
- managed provider keys remain server-side in the License Gateway and never ship in the sidecar
- sidecar can call the Lite Gateway only through authenticated Lite app flows

Common:
- both builds use the same health, ready, version, shutdown, and feature manifest contracts
- feature-specific route availability may differ by build flavor and license state

### Implementation Batches

1. Spec and lane scaffolding
   - Add docs, disabled lane registration, ownership, lane profile, and scope policy.
2. Shared sidecar contracts
   - Add health, readiness, version, feature manifest, error, and route metadata schemas.
3. FastAPI skeleton
   - Add app factory, local binding validation, auth middleware, request IDs, and health endpoints.
4. Engine startup adapter
   - Initialize engine config, storage handles, provider config checks, and graceful shutdown hooks.
5. Workstation supervision contract
   - Add process launch, port selection, token generation, health polling, shutdown, and restart contracts.
6. PyInstaller packaging
   - Add sidecar build specs/scripts and packaging integration checks for macOS Studio builds.
7. Feature manifest and route versioning
   - Add `/features` route and compatibility/version negotiation.
8. Security and diagnostics hardening
   - Add CORS/origin rules, log redaction, size limits, support-bundle fields, and failure copy.
9. Acceptance tests
   - Validate local-only binding, auth, health/readiness, shutdown, packaging metadata, and Workstation supervision.

### Lane Wiring Plan

Add disabled lane:
- `feat-python-sidecar-api`

Owned paths:
- `engine/src/exegesis_engine/sidecar/**`
- `shared/src/exegesis_shared/sidecar/**`
- `desktop-shell/sidecar/**`
- `scripts/sidecar/**`
- `docs/sidecar/**`

Scope policy:
- lane may edit only the above owned paths once activated.
- roadmap/spec/config scaffolding remains integrator-owned during this planning pass.

Lane profile:
- risk: `HIGH`
- routing impact: none while disabled
- roadmap item: Milestone 20

### Test Plan

Scaffolding tests:
- `feat-python-sidecar-api` exists in lane defaults and profiles.
- `feat-python-sidecar-api` is disabled in router config and example config.
- Scope-check policy allows only sidecar docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is post-MVP and not part of Sprint 0-5.

Endpoint tests:
- `/healthz` answers without auth and never exposes secrets.
- `/readyz` requires auth and reports readiness without paid provider calls.
- `/version` requires auth and reports schema/build metadata.
- `/features` requires auth and reports feature route versions.
- `/shutdown` requires auth and initiates graceful shutdown.
- non-health endpoints reject missing/invalid tokens.
- unknown origins are rejected when browser-origin access is configured.

Security tests:
- packaged builds reject non-loopback host binding.
- request size limits are enforced.
- logs redact local auth tokens, provider keys, and document text.
- malformed JSON returns stable error payloads without stack traces.

Workstation supervision tests:
- Workstation can launch the sidecar binary with port and token.
- health polling transitions starting to ready.
- incompatible schema version blocks startup with clear error.
- unexpected exit triggers bounded restart.
- shutdown does not leave orphaned sidecar processes.

Packaging tests:
- PyInstaller build includes the sidecar app entrypoint and required engine/shared modules.
- macOS Studio package contains the sidecar binary.
- packaged sidecar does not include user credentials or managed Lite provider keys.

Acceptance criteria:
- Workstation can start, health-check, ready-check, and stop the sidecar locally.
- The sidecar binds only to localhost in packaged builds.
- The sidecar exposes stable health/version/feature contracts.
- Later Python features have a clear required path for sidecar route exposure.
- No runtime sidecar behavior is active until this lane is explicitly enabled.


## Milestone 21: Native Workstation and Signed Distribution

Lane: `feat-native-workstation` (disabled)

Intent:
- Define the macOS-only Studio Workstation sprint that turns the local Exegesis runtime into a signed, distributable desktop product.
- Treat this as a conceptual and interactive sprint rather than a normal daemon-driven implementation lane.
- Package the native macOS shell, SwiftUI interface surface, local project storage, and Milestone 20 sidecar into one desktop app.
- Prepare web-distributed macOS builds with signing, notarization, update channels, crash/log handling, and install/uninstall behavior.

Non-activation rule:
- This milestone is post-MVP specification and planning scaffolding only.
- Do not implement native shell runtime, signing workflows, updater behavior, website distribution, or sidecar bundle integration until this milestone is explicitly enabled.
- When enabled, this sprint should be run interactively with direct human review because packaging, signing, and OS trust flows are high-friction and platform-specific.

### Product Boundary

The native Studio Workstation owns:
- native app window and app lifecycle
- native SwiftUI interface hosting and app-shell strategy
- native document editor strategy, with STTextView as the preferred AppKit-backed editor candidate inside SwiftUI
- launch and supervision of the Milestone 20 Python sidecar binary
- app data directory selection and migration handling
- native menus, file-open hooks, and app-level command routing where needed
- packaging, signing, notarization, installer, and updater behavior
- first-run/onboarding surfaces for local runtime readiness
- local backend status surfaces when the sidecar is unhealthy or incompatible

The sidecar owns:
- Python-backed feature endpoints
- local health/readiness/version/feature manifest
- engine initialization and provider/storage checks
- Python feature execution behind authenticated loopback routes

The engine owns:
- project state, SQLite storage, imports, providers, retrieval/indexing, and workflow behavior

Non-goals:
- no broad feature expansion beyond making the app distributable
- no deep research, quantitative analysis, or new research workflow implementation
- no app store submission requirement in the first pass
- no collaboration/sync architecture
- no hosted Lite License Gateway changes beyond consuming existing Lite contracts
- no replacing the sidecar with embedded Python

### Native Editor Foundation

Preferred editor substrate to evaluate:
- STTextView embedded in the native SwiftUI Workstation as the document editing core.
- The Workstation sprint should treat STTextView as the first candidate because Exegesis needs a real macOS text editor foundation rather than a custom textarea-style widget.
- This is a conceptual architecture decision for the native Workstation sprint; it does not activate runtime editor replacement in this planning pass.

Required plugin surface to plan:
- annotations
- Markdown highlighting
- inline and side-by-side diffs
- citations rendered as navigable links into project literature
- figures with title/caption metadata
- Markdown tables with title/caption metadata for APA/Pandoc export

Design expectations:
- plugins must preserve editable Markdown as the source of truth.
- plugin rendering should not destroy source offsets needed by citations, comments, coding, diffs, or patch application.
- annotations, citations, figures, and tables must remain export-aware rather than purely visual decorations.
- diff rendering should support the existing apply/reject revision model and later collaboration review.
- the editor architecture should leave room for qualitative coding highlights, search highlights, and future collaboration markers without hardcoding those features into the base editor.

### Distribution Model

Initial distribution target:
- macOS download from Exegesis website or GitHub Releases style release backend
- no terminal required
- user launches a native app, not localhost manually
- app bundles the sidecar and all required local runtime assets
- Windows and Linux Studio builds are out of scope

Platform target:
- macOS signed and notarized app/dmg only

Release artifacts should include:
- native Workstation app
- bundled Milestone 20 sidecar binary
- SwiftUI/native UI assets
- engine/shared/client assets needed at runtime
- license notices
- release manifest with version, platform, architecture, checksums, and sidecar compatibility

### Signing and Trust Requirements

macOS:
- Developer ID signing
- notarization
- stapled ticket where applicable
- hardened runtime if required by bundled binaries
- Gatekeeper-friendly install path and launch behavior

Out of scope:
- non-macOS Studio distribution

macOS release:
- publish SHA256 checksums
- release manifest is tamper-evident or signed
- sidecar binary compatibility is checked at app startup
- app refuses to run a mismatched or untrusted sidecar bundle

### Packaging Architecture

Milestone 17 establishes the basic desktop packaging plan. This milestone is the post-sidecar production distribution sprint:
- integrate sidecar bundle into the native app package
- verify signing survives bundled sidecar binaries
- verify sidecar can start from inside the signed app bundle/install path
- verify updater/install flows preserve app data and do not orphan sidecars
- verify app can recover from missing, quarantined, or incompatible sidecar binary

Preferred architecture:
1. Workstation launches.
2. Workstation locates bundled sidecar binary.
3. Workstation verifies version/signature/compatibility.
4. Workstation starts sidecar on loopback with per-launch auth token.
5. Workstation opens the local UI surface.
6. Workstation monitors sidecar and UI lifecycle.
7. Workstation shuts down sidecar on app exit.

### Web Distribution and Updates

Minimum release flow:
- build macOS artifacts for supported Apple Silicon/Intel architecture targets
- sign macOS artifacts
- notarize macOS artifacts
- generate release manifest and checksums
- publish artifacts to web download location
- smoke-test install on clean macOS machines

Update behavior:
- v1 may use manual update checks only.
- If auto-update is added, it must verify signatures/checksums before applying updates.
- Update flow must preserve projects, local config, credentials, logs, and Lite license cache.
- Update flow must not leave old sidecar processes running.

Download page requirements:
- clearly label Developer and Lite builds if both exist
- show platform/architecture
- show version and release date
- link checksums or verification details
- provide uninstall/reset instructions
- provide basic troubleshooting for sidecar startup failures

### Workstation Runtime Requirements

Startup status states:
- app starting
- sidecar starting
- sidecar ready
- UI ready
- sidecar unhealthy
- sidecar incompatible
- app update required
- app failed to start local backend

Minimum native affordances:
- app title and icon
- standard quit behavior
- restore last window size/position if practical
- app menu entries for about, check for updates, reveal logs, reset local backend, quit
- command or menu action to show local backend status

Failure handling:
- if sidecar fails to start, show clear local backend error with retry and reveal logs
- if sidecar version is incompatible, instruct update/reinstall
- if port binding fails, retry with another loopback port
- if bundled sidecar is missing/quarantined, provide reinstall guidance
- if app data migration fails, do not destroy existing user projects

### Workstation System Requirements And OCR Routing

Minimum supported memory tiers:
- Lite minimum: 8 GB.
- Studio minimum: 8 GB when managed cloud OCR fallback is available.
- Pro minimum: 16 GB when managed cloud OCR fallback is available.
- Local OCR availability is based on current available memory, not just installed memory.
- Studio can use local Nanonets OCR2 when at least 16 GB of memory is currently available for the OCR process without hurting responsiveness.
- Studio on an 8 GB machine is online-OCR only.
- Pro can use local Nanonets OCR2 under the same current-memory availability rule, but Pro's product minimum remains 16 GB.
- Local confidential mode minimum: 128 GB total system memory.

Edition behavior:
- Studio and Pro licenses remain valid on machines below 128 GB, but local confidential mode must be unavailable on those machines.
- Users below 128 GB can still use non-confidential Studio/Pro features that their license grants.
- Pro-only features remain entitlement-gated by `pro_feature_access`; hardware limitations should not be reported as license failures.
- Hardware capability checks must be local and privacy-preserving.

OCR provider selection:
- Markdown-direct import never uses OCR or consumes managed OCR pages.
- Studio and Pro should try local Nanonets OCR2 first only when current available memory is sufficient.
- If current available memory is too low to load local OCR safely, Studio and Pro should fall back to managed Nanonets OCR-3 when the project allows cloud processing.
- Studio managed cloud OCR fallback has a 250-page monthly subscription bucket.
- Pro managed cloud OCR fallback has a 500-page monthly subscription bucket.
- If local OCR is available, prefer it to avoid burning cloud OCR pages.
- If the project is confidential, managed cloud OCR fallback is blocked even if the user has pages remaining.
- Confidential projects can only use offline/local OCR.

### Local Confidential Runtime

Runtime:
- Use MLX Swift as the local confidential LLM runtime for macOS Studio/Pro.
- Local confidential mode is available only on machines with at least 128 GB total system memory.
- Confidential mode uses downloaded local quants only; it must not call managed cloud model or cloud OCR providers.
- The runtime selector should be native Swift-facing and should not require the Python sidecar for core local confidential inference.

Confidential quant tiers:
- 128 GB: `Balanced` with Q4 quant.
- 192 GB: `Enhanced` with Q5 quant.
- 256 GB: `Advanced` with Q6 quant.
- 384 GB: `Ultra` with Q8 quant.
- 512 GB: `Max` with F16 weights.

Quant selection rules:
- Each machine can select its highest supported tier or any lower tier.
- The default recommendation should be the highest tier that leaves enough memory for the app, OCR, sidecar, and normal user activity.
- A user may choose a lower tier for speed, thermals, disk, or responsiveness.
- If a user chooses a higher tier than the machine supports, block the selection with clear copy instead of attempting a failing download.

Model download behavior:
- When a confidential project is started for the first time, Workstation determines the highest supported tier and selected tier, then just-in-time downloads the matching model package.
- If the user later changes the confidential runtime tier in the UI, Workstation downloads the newly selected quant on demand.
- Downloads are served from Cloudflare R2 behind the License Gateway entitlement check.
- Model packages should be split into parts to support resumable partial downloads, retry after network failure, and future delta/update behavior.
- Download state must survive app restart and should support pause/resume/cancel.
- License checks gate access to model packages but downloaded local model files are never embedded in project transfer archives.

Confidential project rules:
- Confidential project mode is selected at project creation.
- A project cannot be changed from confidential to non-confidential or from non-confidential to confidential after creation.
- Confidential projects cannot import documents from non-confidential projects.
- Non-confidential projects cannot import documents from confidential projects.
- Exception: literature may be imported across project confidentiality boundaries when the literature itself is not marked confidential and the user confirms the transfer.
- Confidential project import flows must not call online OCR, managed cloud model providers, or open-web search.
- Confidential project metadata should clearly indicate that cloud fallback is unavailable by design, not broken.

User-facing copy:
- `Local OCR is unavailable right now, so this import can use your cloud OCR pages if project policy allows cloud processing.`
- `Local confidential mode requires 128 GB of memory. Your license is active, but this machine does not meet that local-confidential requirement.`
- `Cloud OCR pages remaining this month: {pagesRemaining}`
- `This project is confidential. Online OCR and cloud model fallback are disabled.`
- `This machine supports {highestTier}. You can use {highestTier} or any lower confidential runtime tier.`
- `Changing confidential runtime tier will download the selected local model before it can be used.`

### Developer/Lite Boundary

Developer build:
- exposes BYOK/BYOM configuration from Milestone 15
- includes sidecar and local endpoint support
- does not call hosted managed provider proxy workflows unless explicitly running as a licensed Lite, Studio, or Pro build that allows those managed workflows

Lite build:
- hides Developer BYOK/BYOM controls
- uses Lite license/gateway flow where required
- still runs local Workstation plus local sidecar for local project behavior
- bundles no managed provider secrets

Studio/Pro licensing boundary:
- Studio and Pro subscriptions are validated through the shared License Gateway entitlement model from Milestone 18.
- Active Studio and Pro subscriptions include Lite client access for secondary-machine use.
- Studio validates `studio_app_access` and, for Pro-only features, `pro_feature_access`; it must not depend on the Lite client to validate Studio/Pro access.
- Lite validates inherited `lite_client_access` from Studio/Pro through the same claim/refresh flow used for direct Lite licenses.
- Studio/Pro subscription state, refresh tokens, and signed caches are never embedded in project transfer archives.
- Quantitative Analysis and Advanced Qualitative Coding Visualizations are Pro-only and require `pro_feature_access`.
- Studio-only licenses must not unlock Pro-only feature surfaces.
- Studio cloud OCR fallback uses the Studio 250-page monthly subscription bucket.
- Pro cloud OCR fallback uses the Pro 500-page monthly subscription bucket.

Both builds:
- share native shell/runtime supervision code where possible
- share sidecar health/version contracts
- differ in feature availability, provider controls, and licensing surfaces

### Interactive Sprint Guidance

This milestone should usually not be delegated as a broad unattended daemon lane.

Reasons:
- signing and notarization failures are platform/account specific
- packaging bugs often need live launch testing and visual inspection
- OS trust prompts require human confirmation
- website distribution decisions need product judgment
- native app lifecycle issues are easier to debug interactively

Recommended mode when activated:
- create short manual implementation packets
- test on one platform at a time
- commit small verified packaging steps
- keep the daemon out of broad native packaging edits unless the task is narrow and scriptable

### Lane Wiring Plan

Add disabled lane:
- `feat-native-workstation`

Owned paths:
- `desktop-shell/workstation/**`
- `desktop-shell/native/**`
- `desktop-shell/packaging/**`
- `scripts/workstation/**`
- `scripts/packaging/**`
- `scripts/release/**`
- `docs/workstation/**`
- `docs/packaging/**`

Scope policy:
- lane may edit only the above owned paths once activated.
- roadmap/spec/config scaffolding remains integrator-owned during this planning pass.
- because this is an interactive sprint, enabling the lane does not imply automatic daemon scheduling.

Lane profile:
- risk: `HIGH`
- routing impact: none while disabled
- roadmap item: Milestone 21

### Implementation Batches

1. Concept and platform decision record
   - Choose shell strategy, packaging tools, sidecar bundle location, update strategy, and release artifact types.
2. Workstation app lifecycle prototype
   - Launch native shell, locate sidecar, start/stop sidecar, show status.
3. Sidecar bundle integration
   - Package the Milestone 20 binary inside Workstation and verify compatibility checks.
4. macOS signed distribution
   - Sign, notarize, build dmg, verify clean install and launch.
5. Release manifest and download workflow
   - Generate release metadata, checksums, website/download copy, and troubleshooting notes.
6. Update/manual upgrade path
   - Verify app data preservation, sidecar replacement, and no orphan sidecar processes.
7. macOS smoke matrix
   - Run launch, project open, sidecar health, import path, quit/restart, uninstall/reset checks on clean macOS installs.

### Test Plan

Scaffolding tests:
- `feat-native-workstation` exists in lane defaults and profiles.
- `feat-native-workstation` is disabled in router config and example config.
- Scope-check policy allows only workstation/packaging/release docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is post-MVP and likely interactive, not a default daemon sprint.

Packaging tests:
- macOS artifact is signed and notarized.
- Non-macOS Studio signing and packaging are out of scope.
- bundled sidecar exists and matches the expected sidecar schema version.
- app refuses incompatible sidecar binary with clear error.
- app starts sidecar from the signed/bundled install location.
- app shuts down sidecar on quit.
- update/install flow preserves project data.

Workstation tests:
- clean launch reaches sidecar ready and UI ready states.
- sidecar startup failure shows retry/reveal logs actions.
- port conflict retries with another loopback port.
- missing/quarantined sidecar surfaces reinstall guidance.
- app data migration failure preserves existing data.
- Studio validates `studio_app_access` through the License Gateway entitlement state.
- Pro-only surfaces validate `pro_feature_access`.
- Lite on a secondary machine can refresh inherited `lite_client_access` from the same active Studio/Pro subscription.
- Studio on an 8 GB machine routes OCR-backed imports to managed online OCR when project policy allows.
- Studio with at least 16 GB currently available for OCR offers local Nanonets OCR2.
- Confidential projects block online OCR and cloud model fallback even when managed cloud pages remain.
- Confidential project mode is immutable after project creation.
- Confidential projects reject imports from non-confidential project documents, except eligible non-confidential literature with explicit confirmation.
- Non-confidential projects reject imports from confidential project documents.
- MLX Swift confidential runtime tier selection exposes only supported quant tiers and lower tiers.
- First confidential project startup triggers licensed JIT model download for the selected quant.
- Changing quant tier triggers JIT download of the selected tier without embedding model files in project transfer archives.
- Interrupted multipart R2 model downloads can resume without restarting from byte zero.

Acceptance criteria:
- A user can download, install, and launch a native macOS Studio Workstation build without terminal use.
- The signed Workstation can start and monitor the bundled sidecar.
- The app can pass a basic local project smoke path through the sidecar-backed runtime.
- Studio/Pro subscription entitlement checks align with the Milestone 18 License Gateway spec and include Lite secondary-machine access.
- Studio can run on 8 GB with managed online OCR, while Pro requires 16 GB.
- Local confidential mode is MLX Swift-backed and unavailable below 128 GB.
- Confidential runtime quant tiers, R2 multipart downloads, and immutable confidential project boundaries are specified.
- Release artifacts are signed/checksummed and ready for web distribution.
- Packaging work remains disabled until explicitly activated.

## Milestone 22: Multi-Agent Open Access Deep Research

Lane: `feat-open-access-deep-research` (disabled)

Sidecar rule:
- Because this milestone comes after Milestones 19 and 20, all Workstation/SwiftUI-facing Python behavior for research jobs, provider fan-out, candidate batches, and import-batch handoff must be exposed through the Python Backend Sidecar API.

Intent:
- Add a post-MVP source-discovery workflow that helps users find possible literature and web sources for review, import, summary, and synthesis inside Exegesis.
- Start with already-owned Exegesis knowledge by searching the current project and other local Exegesis projects before going out to the open web.
- Use a small multi-agent research architecture inspired by LangChain Open Deep Research and LangGraph-style supervisor/researcher patterns, but stop at candidate discovery and import review.
- Present deduped source candidates as a batch that flows into the standard Exegesis import protocol.
- Do not generate final synthesis reports, research summaries, or answer-style deep research output in this milestone.

Non-activation rule:
- This milestone is post-MVP specification and lane scaffolding only.
- Do not implement runtime web search, local project search fan-out, provider API calls, browser scraping, source ranking, import batch creation, or native Workstation/SwiftUI behavior until this lane is explicitly enabled.

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
- browser PDF capture through Milestone 19
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

The source batch should be rendered as a reviewable card/list in the native Workstation SwiftUI interface when this lane is active.

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

Native Workstation/SwiftUI boundaries:
- `desktop-shell/workstation/research/**`
- `desktop-shell/workstation/import_batches/**`
- no runtime SwiftUI work until lane activation
- do not touch the Textual shell for this milestone

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
10. SwiftUI review surface
   - Add source batch review UI in the native Workstation once this lane is active.
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

## Milestone 23: Quantitative Analysis

Lane: `feat-quant-analysis` (disabled)

Native statistics rule:
- Quantitative analysis is a native Workstation feature centered on `StatsCore`, `StatsBridge`, and the IMSL C Numerical Library. It should not route through the Python sidecar unless a future implementation adds Python-backed preprocessing or artifact generation.

Licensing rule:
- Quantitative Analysis is Pro-only.
- The feature requires `pro_feature_access` in addition to a native Workstation build that supports the Quantitative Analysis module.
- A Studio-only subscription must not expose dataset import, analysis configuration, chart generation, or analysis-sequence save behavior.
- A Pro user on a machine below the local confidential-mode hardware tier can still use Quantitative Analysis, because the core statistics engine runs locally and does not require local confidential LLM mode.

Status: post-MVP planned, disabled

### Summary

Add a first-class, lean quantitative analysis surface for CSV datasets inside Exegesis projects. This milestone is intentionally not a full statistics workbench. It supports basic descriptive statistics, simple inferential tests, a few readable charts, and an analysis transcript that can be saved as a summary artifact.

The goal is to let researchers keep small quantitative checks inside the same project workflow as memos, transcripts, summaries, literature, basket context, and later RAG. It should feel like a notebook sequence for basic tests, not like a replacement for R, SPSS, Stata, Jamovi, or JASP.

This pass is a disabled spec only. It must not activate runtime dataset import, IMSL execution, chart rendering, SwiftUI views, or summary generation until `feat-quant-analysis` is intentionally enabled after the MVP launch gate.

### Product Scope

In scope:
- add `Datasets` as a first-class project browser section.
- import CSV files only.
- store dataset metadata and variable metadata in the project database.
- auto-detect variable type as `categorical`, `ordinal`, or `scale`.
- show raw data in the native Workstation dataset view.
- allow changing variable type from the native Workstation raw-data view.
- expose analysis selection in the native Workstation inspector/sidebar.
- run basic descriptive and inferential analyses through native `StatsCore` APIs backed by a narrow IMSL bridge.
- generate markdown result tables.
- generate basic native chart artifacts.
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
- accept `.csv` only for Milestone 23.
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
- native Workstation raw-data view exposes the current type for each column.
- user changes set `userOverriddenType`.
- analyses use `userOverriddenType` when present, otherwise `detectedType`.

### Native Workstation Dataset View

Dataset view:
- shows a raw-data table.
- freezes or clearly labels column headers.
- shows variable type controls in the header or a compact variable metadata panel.
- supports changing variable type for one column at a time.
- does not perform spreadsheet editing.
- does not modify cell values.
- supports selecting a variable or cell enough to update the inspector.

The native Workstation dataset view should remain simple and truthful:
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
- because Milestone 23 intentionally stays lean, basic tests may show covariates as unavailable with copy: `Covariates are not available for this basic test.`
- do not silently ignore selected covariates.

### Native Statistics Architecture

Milestone 23 should buy a mature statistical engine without letting a proprietary numerical library own the app architecture.

Preferred stack:

```text
SwiftUI Workstation
  -> StatsCore Swift package
     - public Swift APIs
     - native dataset and variable models
     - Swift DataFrame-compatible table adapters
     - result structs
     - validation
     - Codable outputs
  -> StatsBridge C target
     - stable C functions owned by Exegesis
     - Swift-friendly array and metadata conversion
     - IMSL calls isolated behind the bridge
     - normalized IMSL status/error codes
  -> IMSL C Numerical Library
```

Rules:
- use IMSL C Numerical Library directly through C, not IMSL Fortran bindings.
- do not let IMSL symbols leak into SwiftUI, project storage, import/export, or inspector code.
- expose clean Swift types from `StatsCore`: `Dataset`, `DatasetVariable`, `DescriptiveStats`, `InferentialTestResult`, `RegressionSummary`, `CorrelationResult`, `ModelResult`, `ChartSpec`, and `AnalysisSequence`.
- make all public `StatsCore` outputs `Codable` so results can be stored, exported, and rendered consistently.
- keep Swift native DataFrame-compatible table structures as the app-facing model for raw data display, variable typing, validation, and simple built-in calculations.
- use simple native calculations where they make the UI more responsive, but treat `StatsCore` plus the IMSL-backed engine as the canonical analysis path for saved inferential results.
- define a narrow `StatsEngineBackend` protocol so IMSL can be swapped if licensing, platform support, CI, or redistribution becomes a blocker.

Vendor due diligence must happen before implementation:
- confirm IMSL C Numerical Library support for macOS, including Apple Silicon `arm64` and any required `x86_64` compatibility path.
- confirm whether IMSL can be redistributed inside an internal or commercial macOS desktop application.
- confirm whether static linking is permitted or whether dynamic linking is required.
- confirm whether IMSL has restrictions for Swift/Xcode applications.
- document CI, signing, notarization, and license-file implications before any runtime code depends on IMSL.

### Analysis Support

Use `StatsCore` as the public Swift API and `StatsBridge` as the only IMSL boundary.

Implementation defaults:
- IMSL C Numerical Library performs the canonical statistical calculations where applicable.
- Swift native DataFrame-compatible adapters own CSV-derived table loading, variable metadata, raw-data display, and validation.
- `StatsCore` emits markdown-ready result tables, effect-size records, and deterministic `ChartSpec` values.
- native Workstation rendering turns `ChartSpec` values into static bar, density, and scatter artifacts.
- no statsmodels, pandas, numpy, matplotlib, or seaborn dependency is part of the default Milestone 23 implementation.

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

Do not implement post-hoc tests in Milestone 23.

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
- do not implement Fisher's exact test in Milestone 23.

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

Do not implement regression models in Milestone 23.

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

Shortcut rows are not required in Milestone 23 unless later UI planning decides dataset analysis needs dedicated shortcuts.

### Workstation API and CLI Contracts

Minimum command/service contracts:

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
- `StatsCore`
- `StatsBridge`
- `StatsEngineBackend`
- `IMSLStatsEngineBackend`

Sidecar contract:
- no default Python sidecar route is required for Milestone 23.
- if a future implementation adds Python-backed preprocessing or artifact generation, that part must expose Workstation-facing behavior through the Milestone 20 sidecar and document why it cannot stay in native `StatsCore`.

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
- `StatsCore`, `StatsBridge`, and IMSL run locally inside the native Workstation distribution.
- chart artifacts are rendered locally from deterministic `ChartSpec` values.
- saved summaries stay in the project.
- LLM interpretation is out of scope for Milestone 23.

Edition boundary:
- Production Quantitative Analysis is available only when `pro_feature_access` is active.
- Studio-only and Lite clients must not expose the Quantitative Analysis feature surface.
- Developer/internal builds may compile or test the module with a developer override, but the production entitlement rule remains Pro-only.
- Lite managed provider credentials are not involved.
- no OCR usage, online model calls, or Lite gateway calls are needed for quantitative analysis.

### Lane Wiring Plan

Add disabled lane:
- `feat-quant-analysis`

Owned paths:
- `desktop-shell/workstation/StatsCore/**`
- `desktop-shell/workstation/StatsBridge/**`
- `desktop-shell/workstation/datasets/**`
- `desktop-shell/workstation/quant_analysis/**`
- `shared/src/exegesis_shared/datasets/**`
- `shared/src/exegesis_shared/quant_analysis/**`
- `docs/quant_analysis/**`

Scope policy:
- lane may edit only the above owned paths once activated.
- roadmap/spec/config scaffolding remains integrator-owned during this planning pass.

Lane profile:
- risk: `MEDIUM`
- routing impact: none while disabled
- roadmap item: Milestone 23

### Implementation Batches

1. Spec and lane scaffolding
   - Add docs, disabled lane registration, ownership, lane profile, and scope policy.
2. IMSL feasibility gate
   - Confirm Perforce support for macOS, Apple Silicon, redistribution, linking mode, Swift/Xcode use, CI, signing, and notarization.
3. `StatsCore` contracts
   - Add Swift dataset, variable, result, effect-size, chart-spec, and sequence models with Codable outputs.
4. `StatsBridge` and backend isolation
   - Add the C shim contract, IMSL error/status normalization, and `StatsEngineBackend` swappability before any IMSL-dependent implementation.
5. CSV import
   - Add CSV loader, validation, provenance, hash, row/column guardrails, and tests.
6. Variable type detection
   - Add categorical/ordinal/scale detection and override persistence.
7. Raw dataset SwiftUI view contract
   - Add DataFrame-compatible table read model and variable-type editing contract for the native Workstation once this lane is active.
8. Descriptive and frequency analysis
   - Add descriptive, frequency, contingency tables, markdown output, and tests.
9. Inferential tests
   - Add t-test, ANOVA, chi-squared, and Pearson correlation with p-values and effect sizes.
10. Chart artifacts
   - Add native bar, density, and scatter chart artifact generation with deterministic artifact storage.
11. Analysis sequence
   - Add appendable sequence entries, status entries, and ordered display contracts.
12. Save sequence as summary
   - Add markdown summary creation and project summary registration.
13. SwiftUI inspector/sidebar controls
   - Add analysis picker, variable selectors, split-by controls, and sequence actions in the native Workstation once this lane is active.
14. End-to-end acceptance tests
   - Validate CSV import, variable typing, analyses, charts, sequence, and summary save.

### Test Plan

Scaffolding tests:
- `feat-quant-analysis` exists in lane defaults and profiles.
- `feat-quant-analysis` is disabled in router config and example config.
- Scope-check policy allows only dataset/quant-analysis docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is post-MVP and not part of Sprint 0-5.
- Docs clearly state this is a Pro-only feature requiring `pro_feature_access`.

Architecture tests:
- `StatsCore` public result types are Codable.
- `StatsCore` can operate against a mock `StatsEngineBackend`.
- IMSL symbols are isolated behind `StatsBridge` and do not appear in SwiftUI or storage modules.
- `StatsBridge` normalizes IMSL status/error codes into stable Swift-facing errors.
- DataFrame-compatible table adapters preserve column names, row counts, missing values, and variable metadata.
- the implementation is blocked until IMSL macOS, Apple Silicon, redistribution, linking, and Swift/Xcode constraints are documented.

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
- User can inspect raw data in the native Workstation dataset view.
- User can run descriptive statistics overall and split by categorical/ordinal variables.
- User can run frequency and contingency tables.
- User can run t-test, ANOVA, chi-squared, and linear correlation.
- Inferential results show p-values and effect sizes.
- Effect sizes include small/medium/large guidance.
- User can generate basic bar, density, and scatter plots.
- User can build a sequence of tests.
- User can save the sequence as a summary.
- No runtime dataset analysis behavior is active until the lane is enabled.

## Milestone 24: Advanced Qualitative Coding Visualizations

Lane: `feat-advanced-qual-visuals` (disabled)

Intent:
- Define the Studio Pro advanced qualitative coding visualization layer after basic coding and native Studio are available.
- Make codes browseable and analyzable through graphs, matrices, distribution tables, visual comparisons, and codebook generation.
- Keep this as a conceptual/spec lane until the basic qualitative coding model has real usage.
- Treat Deep Research, Quantitative Analysis, and Advanced Qualitative Coding as the three Studio Pro feature families after native Studio is available.

Licensing rule:
- Advanced Qualitative Coding Visualizations are Pro-only.
- The feature requires `pro_feature_access`.
- Studio-only licenses may use basic qualitative coding if that feature is enabled, but must not unlock advanced graphs, matrices, visual comparison surfaces, or generated codebooks.
- A Pro user on a machine below the local confidential-mode hardware tier can still use advanced qualitative visualizations that do not require local confidential LLM mode.

Non-activation rule:
- This milestone is post-MVP conceptual specification and lane scaffolding only.
- Do not implement runtime graphs, matrices, dashboards, codebook generation, aggregation jobs, SwiftUI visualization views, or export behavior until this lane is explicitly enabled.
- Do not touch the Textual shell for this milestone. Advanced qualitative coding visualizations are native Studio Workstation/SwiftUI only.

### Product Boundary

Advanced qualitative coding visualizations eventually own:
- browsable code graphs
- parent/child code structure views
- code co-occurrence views
- document/code relationship graphs
- code-by-document matrices
- code-by-document-type matrices
- code-by-participant or folder distribution tables when metadata supports it
- visual comparison views across selected documents, groups, folders, codes, or time slices
- code frequency and coverage tables
- codebook generation from code definitions, examples, frequencies, and audit history
- exportable visualization summaries and codebook documents

It does not own:
- creating the basic coding model; that belongs to Milestone 9
- collaboration-aware shared coding; that belongs to the later collaboration milestone
- quantitative statistics over CSV datasets; that belongs to Milestone 23
- open web source discovery; that belongs to Milestone 22
- Textual shell visualization work

### Data Concepts

Future contracts should cover:
- `CodeGraphNode`
- `CodeGraphEdge`
- `CodeCoOccurrence`
- `CodeDistributionTable`
- `CodeMatrix`
- `CodeComparisonSet`
- `CodeAppearanceAggregate`
- `CodebookEntry`
- `GeneratedCodebook`
- `QualVisualizationSpec`
- `QualVisualizationArtifact`

These contracts should derive from existing code assignments and document metadata rather than duplicating source-of-truth code data.

### Visualization Types

Browsable graphs:
- parent/child code graph
- code co-occurrence graph
- document-code bipartite graph
- optional participant/code graph when participant metadata exists

Matrices:
- code by document
- code by document type
- code by folder
- parent code by child code
- code by participant/group when metadata exists

Distribution tables:
- frequency by code
- frequency by document/document type
- coverage by excerpt count and token estimate
- code density by document length
- parent/child rollups

Visual comparisons:
- compare selected documents by code distribution
- compare selected folders/groups by code distribution
- compare parent codes by child-code composition
- compare code frequencies before/after filtering

Codebook generation:
- generate a structured codebook from code names, descriptions, parent/child structure, frequency, representative excerpts, and audit metadata
- allow user review/edit before saving
- save generated codebook as a project summary or exportable Markdown artifact

### Native Studio/SwiftUI Scope

Future Studio surfaces may include:
- code graph browser
- matrix/table browser
- comparison builder
- filter panel for document type, folder, participant, date, and code hierarchy
- representative excerpt drill-down
- codebook preview and save flow
- export/save summary actions

Boundaries:
- use `desktop-shell/workstation/qual_visualizations/**` for native Studio/SwiftUI surfaces.
- use `engine/src/exegesis_engine/qual_visualizations/**` and `engine/src/exegesis_engine/codebook/**` for aggregation and codebook generation logic.
- expose Python-backed aggregation or artifact generation through the sidecar when needed.
- do not create Textual shell visualization views.

### Lane Wiring Plan

Add disabled lane:
- `feat-advanced-qual-visuals`

Owned paths:
- `engine/src/exegesis_engine/qual_visualizations/**`
- `engine/src/exegesis_engine/codebook/**`
- `desktop-shell/workstation/qual_visualizations/**`
- `shared/src/exegesis_shared/qual_visualizations/**`
- `docs/qual_visualizations/**`

Scope policy:
- lane may edit only the above owned paths once activated.
- roadmap/spec/config scaffolding remains integrator-owned during this planning pass.

Lane profile:
- risk: `MEDIUM`
- routing impact: none while disabled
- roadmap item: Milestone 24

### Future Design Batches

1. Aggregate contracts
   - Define graph, matrix, distribution, comparison, and codebook schemas.
2. Query/read model
   - Define aggregation inputs from code assignments, document metadata, folders, document types, and participant metadata.
3. Graph and matrix generation
   - Specify deterministic graph/matrix generation and filters.
4. Distribution and comparison views
   - Specify table and comparison calculations plus drill-down behavior.
5. Codebook generation
   - Specify codebook entry generation, representative excerpt selection, user review, and save/export behavior.
6. Studio SwiftUI surfaces
   - Define graph browser, matrix browser, comparison builder, codebook preview, and save flows.
7. Sidecar exposure
   - Add sidecar route contracts for aggregation and artifact generation if Python-backed execution is needed.
8. Acceptance tests
   - Validate aggregates, filters, representative excerpts, codebook save, and no Textual shell scope.

### Test Plan

Scaffolding tests:
- `feat-advanced-qual-visuals` exists in lane defaults and profiles.
- `feat-advanced-qual-visuals` is disabled in router config and example config.
- Scope-check policy allows only advanced qualitative visualization docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is a Studio Pro feature after native Studio is available.
- Docs clearly state this is a Pro-only feature requiring `pro_feature_access`.

Future acceptance tests, once activated:
- code graph nodes and edges derive from code assignments.
- co-occurrence graph respects selected filters.
- code-by-document matrix counts match source assignments.
- distribution tables include frequency and coverage values.
- visual comparisons update when documents/groups/codes are changed.
- codebook generation includes definitions, parent/child structure, frequencies, representative excerpts, and audit metadata.
- saved codebook creates a project summary or Markdown artifact.
- Textual shell files are not touched.

Acceptance criteria for this disabled spec:
- Milestone 24 is documented as advanced qualitative coding visualizations.
- The lane is registered and disabled everywhere the router and planner expect.
- The feature is positioned as one of the three Studio Pro feature families after native Studio is available.
- The feature is explicitly gated behind `pro_feature_access`.
- Native Studio/SwiftUI is the only planned UI surface.
- Textual shell visualization work is explicitly out of scope.


## Milestone 25: Confidential Collaboration

Lane: `feat-confidential-collaboration` (disabled)

Intent:
- Define the later company-wide collaboration system after the native Workstation, sidecar, deep research, and quantitative analysis foundations are in place.
- Keep this as a conceptual architecture sprint, not a near-term implementation lane.
- Preserve Exegesis's confidential-first product boundary while allowing future teams, cohorts, and research groups to collaborate safely inside shared projects.
- Define collaboration licensing explicitly: collaboration access is tied to the user's account/license, not a device, so a higher-licensed user can participate from a Lite install on a secondary machine.
- Treat this as a whole level of company-wide development that will likely be handled interactively before broad daemon execution.

Non-activation rule:
- This milestone is post-MVP conceptual specification and lane scaffolding only.
- Do not implement runtime collaboration servers, sync protocols, shared project mutation, invitation flows, SwiftUI collaboration views, or provider-backed collaboration features until this lane is explicitly enabled.
- Do not implement current Textual shell collaboration behavior in this milestone. The activated design must separately decide the minimal Lite participation surface, while full collaboration management remains a Studio/SwiftUI responsibility.

### Product Boundary

Confidential collaboration eventually owns:
- shared project membership and invitations
- workspace, cohort, and research-team roles
- project-level and document-level permissions
- collaboration entitlement and client-access rules across Lite, Studio, course, and future higher-tier licenses
- private local-first editing and review workflows
- encrypted sync or secure exchange of collaboration state
- revision, comment, and decision trails that preserve research provenance
- audit logs for who accessed, changed, exported, imported, or shared project material
- native Workstation SwiftUI collaboration surfaces
- Lite-client participation paths for licensed users on secondary machines

It does not own:
- public social features
- generalized multi-tenant SaaS workspaces detached from confidential project policy
- open web publishing
- course licensing or CoP access approval as sales/onboarding workflows
- payment or page-credit metering
- generic chat-room behavior unrelated to research workflow
- full Studio Pro collaboration management inside the Lite client

### Conceptual Architecture Questions

This lane must answer these before implementation:
- Which licenses unlock collaboration: individual Lite, course Lite, Studio Pro, institutional/course, or separate collaboration add-on?
- Which collaboration actions are available in Lite for a higher-licensed user on a secondary machine, and which require Studio?
- How does a user prove collaboration entitlement after importing/opening a shared project on another device?
- What is the threat model for shared confidential projects?
- Which content can be synced, shared, or exported, and under which project modes?
- Does collaboration use encrypted local-first sync, a hosted relay, peer exchange, or a hybrid?
- Which state is authoritative when two users edit or review the same document?
- Which operations require explicit user approval before being visible to others?
- How are citations, imported literature, OCR artifacts, baskets, codes, datasets, and analysis sequences shared?
- How are offline edits reconciled without losing auditability?
- Which collaboration events must be immutable audit records?
- Which parts can run through the Python sidecar, and which require native Workstation service coordination?
- Which parts must be available through a Lite participation surface, if any, without turning Lite into full Studio?
- What must never be sent to cloud providers during collaboration?

### Licensing And Client Access

Collaboration licensing must be account-centered:
- Collaboration entitlement is tied to the user/account, not a machine.
- A valid higher-tier user should be able to use collaboration from a Lite install on a secondary machine, such as a lightweight MacBook, when their account license permits it.
- Project archives, shared project invitations, and sync state must never carry raw license tokens or grant collaboration access by themselves.
- Opening or importing a shared project on a new machine requires the current user to claim/refresh their own license status.
- Device replacement or secondary-device use must not require a separate machine license.

Client access model to define:
- Studio owns full collaboration administration, member management, permission design, audit inspection, conflict resolution, and advanced review surfaces.
- Lite should support enough collaboration participation for a licensed user to work from a secondary machine.
- Lite participation may include opening shared projects, syncing allowed content, viewing membership state, adding comments/review decisions, and making permitted document edits, subject to the final design.
- Lite should not automatically unlock Studio Pro features such as deep research, quantitative analysis, or advanced qualitative visualizations unless the user's account license includes those entitlements.
- Course Lite collaboration should be explicitly scoped: course access may allow participation in course/project collaboration when enabled, but should not imply unrestricted organization-wide collaboration.

Required future entitlement concepts:
- `collaboration_enabled`
- `collaboration_role`
- `collaboration_client_capabilities`
- `license_tier`
- `device_id`
- `license_refresh_state`

Required copy:
- `Collaboration access is tied to your Exegesis account, not this device.`
- `Refresh your license to use this shared project on this machine.`
- `Your license allows collaboration in Lite, but some management tools require Studio.`

### Data Concepts

Future contracts should cover:
- `WorkspaceMember`
- `ProjectInvite`
- `ProjectRole`
- `ProjectPermission`
- `CollaborationSession`
- `SharedProjectLease`
- `EncryptedSyncEnvelope`
- `CollaborationOperation`
- `CollaborationConflict`
- `ReviewDecision`
- `SharedComment`
- `AuditEvent`
- `SyncCheckpoint`
- `DeviceIdentity`

These are conceptual names for the spec. The activated lane may rename them during detailed design.

### Privacy And Confidentiality Rules

Default rules:
- Confidential project content must not be sent to third-party cloud providers by collaboration code unless the project policy explicitly allows it.
- Shared state must preserve project-mode policy, provider allowlists, and cloud-send policy.
- Collaboration metadata should be minimized, but not at the cost of auditability.
- Any hosted coordination service must avoid plaintext project content where practical.
- Credentials, provider keys, OCR keys, and personal local model endpoints are never shared through collaboration state.
- Exports from shared projects must preserve provenance and citation/reference integrity.

### Native Workstation/SwiftUI Scope

Future Workstation surfaces may include:
- project sharing status
- invite creation and acceptance
- member and role management
- shared document activity
- pending review/approval queues
- comment and decision trails
- sync health and conflict resolution
- audit-event inspection

Boundaries:
- use `desktop-shell/workstation/collaboration/**` for native Studio Workstation/SwiftUI collaboration management surfaces.
- use sidecar or engine routes only for local coordination, sync status, audit queries, and safe handoff to any future collaboration service.
- if Lite participation requires a non-Studio surface, define it as a constrained client capability during the collaboration design sprint rather than as part of current shell mockup work.

### Lane Wiring Plan

Add disabled lane:
- `feat-confidential-collaboration`

Owned paths:
- `engine/src/exegesis_engine/collaboration/**`
- `engine/src/exegesis_engine/confidential_sync/**`
- `desktop-shell/workstation/collaboration/**`
- `shared/src/exegesis_shared/collaboration/**`
- `shared/src/exegesis_shared/confidential_sync/**`
- `docs/collaboration/**`

Scope policy:
- lane may edit only the above owned paths once activated.
- roadmap/spec/config scaffolding remains integrator-owned during this planning pass.

Lane profile:
- risk: `HIGH`
- routing impact: none while disabled
- roadmap item: Milestone 25

### Future Design Batches

This milestone should be handled as a design-first sprint before normal feature threading:
1. Threat model and privacy boundary
   - Define project modes, allowed collaboration metadata, cloud prohibition rules, license/client-access boundaries, and audit expectations.
2. Collaboration data model
   - Specify members, roles, permissions, invites, sessions, operations, conflicts, comments, audit events, and account-level collaboration entitlement state.
3. Sync architecture decision
   - Choose encrypted local-first sync, hosted relay, peer exchange, or hybrid based on privacy and reliability.
4. Conflict and review semantics
   - Define how document edits, coding changes, baskets, citations, datasets, summaries, and exports reconcile.
5. Workstation UX architecture
   - Define the native SwiftUI surfaces for invites, members, activity, review, comments, conflicts, sync health, and Studio-only management.
6. Sidecar and service boundaries
   - Define local sidecar coordination routes, license refresh checks, client capability checks, and any future hosted service API contracts.
7. Security and abuse review
   - Validate encryption, access control, auditability, credential isolation, and project-mode preservation.
8. Implementation lane split
   - Split into smaller development lanes only after the conceptual architecture is accepted.

### Test Plan

Scaffolding tests:
- `feat-confidential-collaboration` exists in lane defaults and profiles.
- `feat-confidential-collaboration` is disabled in router config and example config.
- Scope-check policy allows only collaboration docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is conceptual post-MVP work after Milestone 24.

Future acceptance tests, once split into implementation lanes:
- collaboration entitlement is user/account-based and not machine-based.
- a higher-licensed user can refresh entitlement and access allowed collaboration features from Lite on a secondary machine.
- Lite collaboration participation does not unlock Studio-only management or Pro features.
- project transfer/import does not carry collaboration license tokens.
- invitations require authorization.
- members receive only the permissions assigned to their role.
- confidential project policy blocks unauthorized cloud-provider sharing.
- shared changes produce audit events.
- conflict resolution preserves original and proposed states.
- sync resume does not duplicate operations.
- offline edits reconcile without losing local changes.
- exported shared documents retain citation and provenance metadata.
- credentials and local provider endpoints are not included in shared state.

Acceptance criteria for this disabled spec:
- Milestone 25 is documented as confidential collaboration.
- The lane is registered and disabled everywhere the router and planner expect.
- The scope is explicitly company-wide, post-quant, and later than the current summer grunt-work milestones.
- The spec explicitly handles collaboration licensing and Lite secondary-machine access for appropriately licensed users.
- The spec is conceptual rather than pretending collaboration can be safely batch-implemented immediately.
- Studio/SwiftUI owns full collaboration management, while Lite participation requirements are captured for the future design sprint.

## Milestone 26: Native iPad Lite

Lane: `feat-ipad-native-lite` (disabled)

Intent:
- Define a long-term conceptual milestone for a native iPadOS Lite client after confidential collaboration has been architected.
- Treat iPad Lite as a later client-family expansion, not a near-term MVP, Studio Pro, or Textual shell task.
- Recognize that iPad cannot depend on the packaged Python sidecar model used by macOS Studio Workstation.
- Plan for more Lite behavior to become Swift-native over time as Studio and Pro mature their native Swift components.
- Keep the core product promise: Lite remains a secondary-machine, lower-friction client for users whose account license allows Lite access.

Non-activation rule:
- This milestone is conceptual specification and lane scaffolding only.
- Do not implement runtime iPadOS views, App Store packaging, Swift-native sidecar replacements, sync/client storage, or Lite feature behavior until the lane is explicitly enabled.
- This work should not begin until enough Studio/Pro Swift-native infrastructure exists to reuse rather than rebuild.

### Product Boundary

iPad native Lite eventually owns:
- native iPadOS project browsing and document reading/editing surfaces
- Lite-compatible project open/import/export flows
- license claim and refresh using the same account-based License Gateway model as desktop Lite
- secondary-machine access for eligible Studio/Pro, individual Lite, course Lite, and CoP Lite users
- lightweight annotation, reading, review, drafting, and collaboration participation where the license and client capability matrix allow it
- iPadOS file provider, document picker, share sheet, and local storage behavior
- offline-safe project access boundaries and refresh behavior

iPad native Lite does not own:
- Studio-only or Pro-only management surfaces
- deep research orchestration
- quantitative analysis
- advanced qualitative visualization dashboards
- full confidential collaboration administration
- Python sidecar packaging
- local OpenAI-compatible model hosting
- Developer BYOK/BYOM command-palette workflows
- Textual shell behavior

### Sidecar And Swift-Native Constraint

The architectural constraint is the point of the milestone:
- macOS Studio can supervise a packaged Python sidecar.
- iPadOS Lite cannot rely on that same Python sidecar runtime model.
- Therefore, any iPad-native Lite feature must either be Swift-native, call a safe hosted Lite Gateway endpoint, or use shared portable data/contracts that do not require local Python execution.
- The milestone should inventory which existing sidecar-backed behaviors must be rewritten, deferred, or reduced for iPad Lite.

Likely Swift-native candidates over time:
- project navigation and local document cache
- Markdown document rendering/editing
- license refresh and signed entitlement cache
- project archive import/export validation
- simple basket viewing and context promotion
- citation and literature link navigation
- annotation/review display
- basic sync/client capability checks once collaboration exists

Likely not in first iPad Lite:
- OCR import requiring local Python or Nanonets page-ledger orchestration beyond hosted gateway calls
- local RAG indexing
- quantitative analysis
- deep research provider fan-out
- advanced coding visualizations
- complex patch/rewrite previews unless the native editor stack already supports them

### Dependency On Studio And Pro Native Work

iPad Lite should reuse mature native components rather than invent a second product:
- reuse Studio/Pro Swift data models where practical
- reuse account/license entitlement models from Milestone 18 and Milestone 25
- reuse native editor decisions from Milestone 21 where possible, adapted for iPadOS
- reuse project-transfer archive contracts from Milestone 16
- reuse collaboration client-capability rules from Milestone 25
- reuse import/literature/citation data contracts where they can run without sidecar-only behavior

Activation prerequisites:
- native Studio Workstation has settled the Swift data model and editor direction.
- License Gateway can provide device/account entitlement refresh for Lite.
- collaboration client-capability rules distinguish Lite participation from Studio management.
- project transfer/archive format is stable.
- enough sidecar-backed behavior has been factored into shared contracts or Swift-native components.

### Client Capability Model

iPad Lite should be specified through client capabilities, not product vibes:
- `ipad_lite_client_access`
- `can_open_project_archive`
- `can_refresh_license`
- `can_edit_markdown_document`
- `can_view_literature_metadata`
- `can_add_annotation`
- `can_participate_in_collaboration`
- `can_run_local_sidecar_feature`: expected false
- `requires_gateway_for_remote_feature`: true for hosted Lite-only workflows

The capability matrix should make clear:
- which actions work offline
- which actions require gateway connectivity
- which actions require Studio/Pro subscription
- which actions are unavailable on iPad Lite even when the account has Pro
- which project modes block cloud or hosted workflows

### Lane Wiring Plan

Add disabled lane:
- `feat-ipad-native-lite`

Owned paths:
- `client-ipad/lite/**`
- `client-ipad/shared/**`
- `shared/src/exegesis_shared/ipad_lite/**`
- `docs/ipad_lite/**`

Scope policy:
- lane may edit only the above owned paths once activated.
- roadmap/spec/config scaffolding remains integrator-owned during this planning pass.
- enabling this lane should not imply immediate daemon execution; it is a long-term conceptual client-architecture sprint.

Lane profile:
- risk: `HIGH`
- routing impact: none while disabled
- roadmap item: Milestone 26

### Future Design Batches

1. Product boundary and entitlement matrix
   - Define which Lite workflows belong on iPad and which are desktop-only.
2. Sidecar dependency inventory
   - List every Lite workflow that currently depends on Python sidecar or local Python libraries.
3. Swift-native reuse plan
   - Identify Studio/Pro Swift components that can be reused or generalized for iPad.
4. Data and archive compatibility
   - Specify project open/import/export compatibility and local storage.
5. License and gateway behavior
   - Specify claim, refresh, signed cache, offline grace, and secondary-machine access.
6. Editor and document workflow
   - Define the minimum iPad editor/reader behavior and how it handles Markdown, citations, annotations, figures, and tables.
7. Collaboration participation boundary
   - Define what Lite collaboration participation means on iPad without Studio management surfaces.
8. Implementation split
   - Split into smaller implementation lanes only after the conceptual architecture is accepted.

### Test Plan

Scaffolding tests:
- `feat-ipad-native-lite` exists in lane defaults and profiles.
- `feat-ipad-native-lite` is disabled in router config and example config.
- Scope-check policy allows only iPad Lite docs and implementation paths when the lane is active.
- `status.py` shows the lane disabled.
- Docs clearly state this is post-collaboration, conceptual, and long-term.

Future acceptance tests, once split into implementation lanes:
- iPad Lite can refresh account-based Lite access.
- Studio/Pro subscribers can use inherited Lite access on iPad without buying separate Lite.
- iPad Lite does not attempt to launch or package the Python sidecar.
- iPad Lite blocks or hides sidecar-only features unless a Swift-native or hosted-gateway equivalent exists.
- iPad Lite project archive import does not carry credentials or license tokens.
- offline behavior respects signed license cache and project-mode policy.
- iPad Lite collaboration participation does not unlock Studio-only management or Pro-only features.

Acceptance criteria for this disabled spec:
- Milestone 26 is documented as Native iPad Lite after confidential collaboration.
- The lane is registered and disabled everywhere the router and planner expect.
- The spec clearly states that iPad Lite is long-term because sidecar-dependent behavior must become Swift-native or gateway-backed.
- The spec ties iPad Lite to reuse of mature Studio/Pro Swift-native infrastructure.
- No runtime iPad Lite behavior is active.
