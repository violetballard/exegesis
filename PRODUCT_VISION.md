# Product Vision

This file is the non-negotiable product anchor for the staged Exegesis MVP migration.

## Product surfaces

- `Exegesis Engine`
  - the engine/runtime and CLI compatibility surface in this repository
- `Exegesis Textual Client`
  - the primary MVP interface for real writing and dogfooding
  - scaffolded now, not yet activated
- `Exegesis Studio`
  - future commercial workstation package built after the MVP client teaches us the durable workflow

## End goal

Build a writing environment, not a chatbot and not a dev console.

The user should always understand:
- Project = where I am
- Document = what I am writing
- Workflow = what the system is doing
- Context Basket = what is in play
- Inspector = what the selected thing means

## Required capabilities

1. Writing-centered workflow
- Opening a document, working in it, and continuing after plan/revise/apply loops is the trust surface.

2. Retrieval-first context handling
- Retrieval stays FTS-first for the current MVP.
- Search results must be structured enough to promote into the basket and later into workflow cards.

3. Canonical engine contract
- The future Textual client must be able to consume one clean engine-facing state/action surface.
- CLI compatibility is required while Textual remains disabled.

4. Shared UI contract (`A2UI`)
- Cards/actions/selection types must live in a client-agnostic shared layer.
- Rendering adapters stay outside shared.
- Full MVP A2UI protocol compatibility includes handshake, capability negotiation, primitive blocks, known cards, unknown-card fallback, typed actions, validation, streaming event shape, and promotion tracking for generated declarative surfaces.

5. Keyboard-first client behavior
- The Textual MVP must eventually support pane focus, command palette, basket promotion, patch apply/reject, and inspector-follow-selection from the keyboard.

6. Auditable state and workflow
- Project/document/basket/session state must be persistent enough for real dogfooding.
- Workflow actions must be explicit and traceable.
- Richer encrypted SQLite-backed storage is required for MVP trust state after the demo path stands: provenance, audit events, workflow artifacts, compaction records, A2UI promotion candidates, and durable app/project metadata.
- Full provenance/tracking is a core MVP feature, not later polish. Exegesis must explain what context was used, what was generated, what was promoted, what was applied, and why the user can trust the chain.
- Trusted CoP dogfooding should capture generated A2UI promotion candidates early, alongside human feedback, so useful workflow surfaces can be promoted from real use.
- The first CoP also needs a minimal hosted Cloudflare gateway before broad feature expansion: basic CoP/course access claim and refresh plus privacy-preserving A2UI promotion ingest. Paid licensing and Paddle can arrive later.
- CoP launch support must include redacted diagnostic bundle upload through the gateway, plus clear consent/onboarding/error-state copy; support tooling should not require users to expose research content by default.

## Near-term product truth

- The Textual client is the MVP target.
- Textual is not yet incorporated as a dependency.
- Current work remains engine-first so the future UI lanes can activate against a real contract rather than a speculative one.
- The CLI remains the active operator surface until those UI lanes are enabled.
