# Product Vision

This file is the non-negotiable product anchor for all lanes.

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

2. Retrieval-first context handling
- Source documents are stored in vault/context.
- Generation consumes retrieved chunks, not entire raw document piles.
- RAG sits between storage and generation.

3. Auditable generation
- Draft/diff outputs are traceable to retrieved sources.
- Metrics/audit paths support repeatable analysis.

4. Operator-first control surface
- CLI remains a first-class surface for development and reliability.
- UI can evolve on top without changing core contracts.

## Non-Goals

- No hidden cross-module coupling.
- No silent output contract drift.
- No lane work without roadmap/vision mapping.

## Handoff Alignment Rule

Every review/integration handoff must include:
- roadmap item(s) affected (`ROADMAP.md`)
- vision capability affected (one of the four above)

If a change cannot map to these, it should not be promoted.
