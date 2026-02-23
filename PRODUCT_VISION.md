# Product Vision

This file is the non-negotiable product anchor for all lanes.

## Product Names

- `Exegesis Engine`: CLI-first agent runtime (this repository)
- `Exegesis Studio`: commercial writing/research workstation package (future separate project)

## End Goal

Build a local-first workstation agent that helps users run repeatable thinking and drafting workflows with:
- reliable state
- retrieval-backed context (RAG)
- auditable outputs
- deterministic operator controls

This is not only a chat interface. It is an agent runtime + workflow system.

## Required Product Capabilities

1. Local-first state and identity
- Project-scoped vault and context basket with safe recovery behavior.
- Encrypted by default at rest for persisted local state and context artifacts.

2. Retrieval-first context handling
- Source documents are stored in vault/context.
- Generation consumes retrieved chunks, not entire raw document piles.
- RAG sits between storage and generation.

3. Auditable generation
- Draft/diff outputs are traceable to retrieved sources.
- Metrics/audit paths support repeatable analysis.

4. Operator-first control surface
- CLI remains a first-class surface for development and reliability.
- Engine ships a localhost-only OSS web console as a barebones reference/admin client.
- UI can evolve on top without changing core contracts.
- Model routing is automatic by default; user-facing model selection is not the primary control path.

5. Agent-to-UI protocol (`A2UI`)
- Agent emits structured presentation artifacts (cards, sections, actions, metadata).
- Artifacts must be consumable by multiple clients, including future Studio UI.
- CLI remains able to render a text fallback of the same underlying artifacts.

6. Expansion lanes
- Architecture must support future quantitative analysis and coding workflows in addition to writing/research.
- New domains should reuse shared agent/runtime contracts instead of bespoke pipelines.
- Qualitative coding support is a required follow-on once the base writing engine is stable.

7. Power-user provider control (gated)
- Advanced users may bind role-specific models through OpenAI-compatible local endpoints.
- Endpoint policy is localhost-only for overrides to avoid accidental remote provider drift.
- Overrides must preserve routing invariants and audit provenance.

## Product Packaging Strategy

- Build and stabilize `Exegesis Engine` first as the base qualitative research/writing agent.
- Use Engine outputs and contracts to drive UI generation and interaction patterns.
- Create `Exegesis Studio` as a separate project once Engine contracts are stable enough for client consumption.

## Non-Goals

- No hidden cross-module coupling.
- No silent output contract drift.
- No lane work without roadmap/vision mapping.
- No plaintext-by-default storage mode for persistent workstation data.

## Handoff Alignment Rule

Every review/integration handoff must include:
- roadmap item(s) affected (`ROADMAP.md`)
- vision capability affected (one of the four above)

If a change cannot map to these, it should not be promoted.
