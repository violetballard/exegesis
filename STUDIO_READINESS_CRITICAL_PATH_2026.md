# Studio Readiness Critical Path (Feb 25 -> Jul 1, 2026)

This checklist tracks the minimum path to begin Studio UI wiring with low rework risk.
Dates are fixed to 2026 and use pass/fail gates.

## Target Outcomes

- Early UI wiring start: May 2026
- Preferred full wiring start: June 2026
- Contract-stable handoff target: July 1, 2026

## Weekly Execution Checklist

## Week 1 (2026-02-25 to 2026-03-06)

- [ ] Milestone 1 merge blockers reduced:
  - [ ] command + diff-preview hardening merged through integrator
  - [ ] context/vault persistence hardening merged through integrator
  - [ ] startup UX flow polish merged through integrator
- [ ] Integrator `make ci` green after merges
- [ ] CLI smoke flow stable

Gate (must pass by 2026-03-06):
- [ ] Milestone 1 is no longer blocked on obvious merge instability

## Week 2 (2026-03-09 to 2026-03-20)

- [ ] Milestone 2 targeted test gaps closed:
  - [ ] parser edge cases
  - [ ] persistence edge cases
- [ ] Re-run full quality gates:
  - [ ] `./quality-format.sh --check`
  - [ ] `./quality-lint.sh`
  - [ ] `./quality-test.sh`
  - [ ] `./typecheck-test.sh`
  - [ ] `make ci`

Gate (must pass by 2026-03-20):
- [ ] Milestones 1/2 stable enough to stop contract churn from regressions

## Week 3 (2026-03-23 to 2026-04-03)

- [ ] Milestone 3 contract draft freeze v1:
  - [ ] profile/policy gate contracts finalized
  - [ ] cloud-send policy contracts finalized
  - [ ] audit event contracts finalized
- [ ] Contract docs linked and consistent:
  - [ ] `PRODUCT_VISION.md`
  - [ ] `ROADMAP.md`
  - [ ] policy/provider specs

Gate (must pass by 2026-04-03):
- [ ] Engine policy contracts are not changing daily

## Week 4 (2026-04-06 to 2026-04-17)

- [ ] Milestone 5 A2UI contract lock core:
  - [ ] GenericCard + primitive blocks stable
  - [ ] UnknownCard fallback stable
  - [ ] action allowlist + schema validation stable
  - [ ] PolicyGate action enforcement stable

Gate (must pass by 2026-04-17):
- [ ] UI renderer contract is stable for Studio stubs

## Week 5 (2026-04-20 to 2026-05-01)

- [ ] Milestone 4 retrieval contract lock:
  - [ ] unified retrieval shape stable (`fts|pageindex|embeddings`)
  - [ ] provenance fields stable
  - [ ] fallback behavior documented and testable

Gate (must pass by 2026-05-01):
- [ ] Retrieval interface can be consumed by Studio without guessing

## Week 6 (2026-05-04 to 2026-05-15)

- [ ] Start Studio wiring (low-risk surfaces):
  - [ ] read-only views against stable Engine contracts
  - [ ] safe typed action paths only
- [ ] Rule enforced:
  - [ ] no breaking Engine contract changes without explicit versioning note

Gate (must pass by 2026-05-15):
- [ ] Studio can wire initial UI against Engine v1 contracts

## Week 7 (2026-05-18 to 2026-05-29)

- [ ] Milestone 5 completion push:
  - [ ] terminal/A2UI stream behavior stable
  - [ ] proposal review/promotion gating stable
  - [ ] web/admin parity checks complete
- [ ] Output contract coverage:
  - [ ] backward compatibility tests in place

Gate (must pass by 2026-05-29):
- [ ] Milestone 5 is stable enough for broad UI integration

## Week 8 (2026-06-01 to 2026-06-12)

- [ ] Milestone 6 handoff package draft:
  - [ ] Engine-to-Studio boundary document
  - [ ] API/event mapping
  - [ ] compatibility matrix

Gate (must pass by 2026-06-12):
- [ ] Studio team can implement from handoff docs without ambiguity

## Week 9 (2026-06-15 to 2026-06-26)

- [ ] Milestone 6 stabilization:
  - [ ] resolve contract ambiguities
  - [ ] freeze export preview/final contract
  - [ ] final handoff doc edits merged

Gate (must pass by 2026-06-26):
- [ ] Contract freeze candidate approved

## Week 10 (2026-06-29 to 2026-07-01)

- [ ] Final readiness checkpoint
- [ ] Handoff package signed off
- [ ] Studio wiring can proceed with low rework risk

Gate (must pass by 2026-07-01):
- [ ] Studio-readiness achieved

## Hard Deadlines

- [ ] 2026-03-20: Milestones 1/2 stable
- [ ] 2026-05-01: Milestones 3/4 contract surfaces frozen v1
- [ ] 2026-05-29: Milestone 5 contract stability + test coverage
- [ ] 2026-06-26: Milestone 6 handoff package finalized
- [ ] 2026-07-01: Studio-readiness achieved

## Risk Log (Use Weekly)

- [ ] R1: Contract churn (A2UI/retrieval/policy)
- [ ] R2: Integrator backlog delays
- [ ] R3: Test debt reopening Milestones 1/2
- [ ] R4: Export contract instability close to handoff

Mitigation notes:
- Keep lane handoffs small and enforce AGENTS limits.
- Reject unversioned breaking contract changes.
- Prioritize blocker fixes over net-new scope until each gate passes.
