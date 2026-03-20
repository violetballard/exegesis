# Product Vision

This file is the non-negotiable product anchor for all lanes.

## Product Names

- `Exegesis Engine`: CLI-first agent runtime (this repository)
- `Exegesis Console`: future Textual-based operator surface for Engine
- `Exegesis Studio`: commercial writing/research workstation package (future separate project)

## End Goal

Build a local-first workstation agent that helps users run repeatable thinking and drafting workflows with:
- reliable state
- retrieval-backed context (FTS-first for the current MVP)
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
- SQLite FTS is the current MVP retrieval path.
- PageIndex and embeddings are deferred until after the demo push.

3. Auditable generation
- Draft/diff outputs are traceable to retrieved sources.
- Metrics/audit paths support repeatable analysis.

4. Operator-first control surface
- CLI remains a first-class surface for development and reliability.
- Engine emits structured outputs that can be consumed by CLI now and `Exegesis Console` next.
- `Exegesis Console` is the intended first interactive operator client, but the engine contracts come first.
- UI can evolve on top without changing core contracts.
- Model routing is automatic by default; user-facing model selection is not the primary control path.

5. Agent-to-UI protocol (`A2UI`)
- Agent emits structured presentation artifacts (cards, sections, actions, metadata).
- Artifacts must be consumable by CLI first, then `Exegesis Console`, then future Studio UI.
- CLI remains able to render a text fallback of the same underlying artifacts.

6. Expansion lanes
- Architecture must support future quantitative analysis and coding workflows in addition to writing/research.
- New domains should reuse shared agent/runtime contracts instead of bespoke pipelines.
- Qualitative coding support is a required follow-on once the base writing engine is stable.

7. Power-user provider control (gated)
- Advanced users may bind role-specific models through OpenAI-compatible local endpoints.
- Endpoint policy is localhost-only in confidential mode to avoid accidental remote provider drift.
- Overrides must preserve routing invariants and audit provenance.
- Advanced config editing should remain in engine/operator tooling, not Studio model-pickers.
- Provider compatibility probing (`exegesis doctor`) is required so fallback modes are explicit to operators.

## Current Capability Alignments

- Current MVP emphasis is on Engine output contracts, FTS-backed retrieval, and A2UI cards/actions that can be rendered in CLI now and `Exegesis Console` next.
- Dedicated web console work has been retired; the future interactive surface is `Exegesis Console`, built later on top of the same engine/A2UI contracts.

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
- vision capability affected (one of the required capabilities above)

If a change cannot map to these, it should not be promoted.
