# Post-MVP Feature Specs

This document defines disabled post-MVP work that should not be activated until the summer MVP and CoP launch gate have produced real usage feedback.

Current post-MVP lane:
- Milestone 18: `feat-browser-pdf-capture`

Activation rule:
- These lanes remain disabled in router config.
- Do not schedule, implement, or polish these features until explicitly enabled after the MVP launch gate.
- Runtime browser extension, native bridge, import handoff, and packaging behavior must remain inactive until the lane is intentionally activated.

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
