# Roadmap

This file is the canonical in-repo milestone tracker.
See `PRODUCT_VISION.md` for non-negotiable end-goal alignment.

## Milestone 0: Foundation (Complete)

Status: complete

Scope:
- Quality baseline scripts (`format`, `lint`, `test`, `typecheck`)
- CI workflow and `make ci` entrypoint
- Ownership and integration runbooks

Exit criteria:
- Local gates pass reliably
- CI path is stable
- Lane ownership rules are enforced

## Milestone 1: Bootstrap Flow Stabilization (In Progress)

Status: in progress

Scope:
- Command and diff-preview behavior hardening
- Context basket and vault persistence hardening
- UX flow readability and startup context preview polish
- Integrator promotion from approved feature lanes

Exit criteria:
- Approved feature-lane deltas merged through integrator
- `make ci` green on integrator and main for final combined state
- Manual CLI smoke flow remains stable

## Milestone 2: Test Hardening (In Progress)

Status: in progress

Scope:
- Add focused unit coverage for core behaviors
- Keep command-level probes for integration confidence

Completed so far:
- Added unit-test harness and initial focused tests for diff preview and storage recovery

Remaining:
- Add missing targeted cases identified during reviews (parser edges, persistence edge cases)

## Milestone 3: Product Readiness (Planned)

Status: planned

Scope:
- Define and lock user-facing output contracts
- Expand end-to-end verification scenarios
- Prepare release notes and operator runbook for first publish
- Define generation provenance contract (retrieval evidence attached to outputs)
- Define and lock encryption-at-rest default behavior and key lifecycle policy
- Define role-based auto-routing contract and power-user override policy
- Define localhost-only gating for OpenAI-compatible override endpoints
- Add provider-compatibility probe contract for OpenAI-compatible runtimes (`exegesis doctor`)
- Lock shared Engine/Studio config schema (`exegesis.yml`) and precedence rules

Exit criteria:
- Contract changes documented and intentional
- Reproducible release candidate checklist
- Main branch in publishable state
- Encryption-by-default is enforced for persistent local state
- Override behavior is deterministic, localhost-gated, and auditable
- Provider capability detection and fallback behavior are explicit, testable, and operator-visible
- Config source-of-truth and override precedence are explicit and testable

## Milestone 4: Retrieval Layer (Planned)

Status: planned

Scope:
- FTS-first ingestion/index path for context/vault documents
- Retrieval orchestration in engine before drafting/diff generation
- Source-attribution model for retrieved chunks
- Defer PageIndex/embeddings until after the demo push

Exit criteria:
- Agent uses retrieved chunks by default for generation flows
- Retrieval paths are auditable and deterministic
- RAG behavior is documented as part of output contracts

## Milestone 5: A2UI Presentation Layer (In Progress)

Status: in_progress

Scope:
- Define `A2UI` output contract for agent-produced presentation artifacts
- Add agent-side card/section/action payload generation with deterministic schemas
- Provide CLI rendering fallback for the same structured payloads
- Keep the surface client-agnostic so `Exegesis Console` can consume it next
- Add capabilities handshake and composable `GenericCard` primitives with safe unknown-card fallback
- Enforce typed/allowlisted actions with engine-authoritative `PolicyGate`
- Defer dedicated web-console work

Exit criteria:
- A2UI schema/versioning is documented and stable
- Core workflows can emit A2UI payloads and CLI fallback views
- Output contracts are test-covered and backward-compatible by policy
- CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate
- A2UI output is stable enough for the first `Exegesis Console` build

## MVP Focus Through 2026-05-04

Current active implementation emphasis:
- `feat-commands`
- `feat-context-storage`
- `feat-retrieval-fts`
- `feat-a2ui-contract`
- `feat-engine-runs`

Defined but not active:
- `feat-console`

Deferred/paused for the current MVP push:
- `feat-console`
- `feat-ux-flow`

## Milestone 6: Studio Readiness Handoff (Planned)

Status: planned

Scope:
- Freeze Engine contracts required by UI clients
- Define Engine-to-Studio boundary and repo split handoff package
- Prepare integration docs for separate `Exegesis Studio` project bootstrapping
- Add final-document preview/export contract (`export.preview`/`export.final`) with encrypted preview artifacts and TTL cleanup
- Keep `Exegesis Console` thin and engine-driven while preserving A2UI parity for Studio handoff

Exit criteria:
- Engine contracts are ready for external client consumption
- Explicit handoff bundle exists for Studio implementation startup
- Repository split plan is approved and documented

## Milestone 7: Qualitative Coding Support (Planned)

Status: planned

Dependency:
- Starts after base writing engine milestones are stable (Milestones 1 through 4 complete enough for production use).

Scope:
- Add codebook management primitives (codes, definitions, versioned edits)
- Add coding operations over source excerpts and retrieved chunks
- Add agreement/coverage metrics and audit trails for coding actions
- Expose coding artifacts in both CLI and A2UI payloads

Exit criteria:
- Users can apply, revise, and review qualitative codes in normal workflows
- Coding operations are auditable and retrieval-aware
- Coding outputs are consumable by future `Exegesis Studio` clients

## Sprint Cadence

Current sprint model:
- Short parallel feature lanes with strict ownership
- Review-first promotion into integrator
- Integrator finalizes into main after full gates

If this cadence changes, update this section and `INTEGRATION.md` together.
