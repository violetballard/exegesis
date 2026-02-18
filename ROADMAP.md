# Roadmap

This file is the canonical in-repo milestone tracker.

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

Exit criteria:
- Contract changes documented and intentional
- Reproducible release candidate checklist
- Main branch in publishable state

## Sprint Cadence

Current sprint model:
- Short parallel feature lanes with strict ownership
- Review-first promotion into integrator
- Integrator finalizes into main after full gates

If this cadence changes, update this section and `INTEGRATION.md` together.
