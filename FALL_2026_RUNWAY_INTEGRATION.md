# Fall 2026 Cohort Runway Integration (Engine Scope)

This document maps the runway checklist onto current Engine milestones and design constraints.
Studio-specific implementation items are tracked as downstream dependencies and are not in-repo deliverables here.

## Scope Policy

- In scope (Engine repo): policy contracts, retrieval/contracts, terminal/A2UI contracts, patch/export contracts, audit/security requirements, docs/runbooks.
- Out of scope (this repo): native Studio UI/editor/runtime packaging implementation details.

## Alignment Summary (Merged / New / Cut)

1. Merged into existing milestones:
- A, B, D, E, F, G (engine-side), L (engine-side guidance/audit)

2. New tracking additions (now explicit in planning docs):
- Runway timeline gates (Now->Aug 15)
- Binary cohort-ready acceptance checklist framing
- Engine-only interpretation of onboarding/demo/alpha/support artifacts

3. Cut/deferred from Engine milestone scope:
- Studio-only editor/runtime UX implementation tasks
- Course licensing/commercial flows (K) in Engine codepath
- Collaboration runtime features for cohort MVP

4. Conflict resolution applied:
- Runway note "no embeddings" is overridden by current canonical design: embeddings are included in MVP retrieval (`fts|pageindex|embeddings`).

## Epic -> Milestone Mapping (Engine)

`A` Define cohort-ready bar
- Milestones: 1, 3
- Engine deliverables:
  - one-page MVP loop contract (`section -> context set -> run -> patch -> export`)
  - binary acceptance checklist in docs/runbook

`B` Confidential-first security foundation
- Milestones: 1, 3
- Engine deliverables:
  - encrypted at-rest requirements across vault artifacts
  - PolicyGate confidential hard blocks for non-local providers and network-required tools
  - export confirmation safety gate
  - audit event coverage (content-free)

`C` Writing-first editor + patch workflow
- Milestones: 1, 5, 6
- Engine deliverables:
  - patch protocol + apply/reject contracts
  - version/checkpoint semantics at artifact/section layer
- Studio-native editor implementation: downstream project

`D` Evidence objects + Context Sets
- Milestones: 1, 4
- Engine deliverables:
  - stable excerpt IDs + provenance spans
  - context set create/pin/attach APIs
  - evidence-used traceability contracts

`E` Terminal + A2UI + tools
- Milestones: 5
- Engine deliverables:
  - interactive terminal stream contracts
  - GenericCard/primitives/UnknownCard safety
  - tool allowlist + schema validation + safe retries
  - core tool contract set

`F` Retrieval v1 (FTS + PageIndex)
- Milestones: 4
- Engine deliverables:
  - FTS + PageIndex strategy orchestration
  - scanned PDF "OCR required" policy/UX signaling contract
  - embeddings kept enabled per current canonical MVP

`G` Export pipeline
- Milestones: 3, 6
- Engine deliverables:
  - preview/final export contracts + confirmation policy
  - template/style contract plumbing
  - citation metadata pipeline contracts
- Studio export UX polish: downstream project

`H` Embedded runtime supervisor (Studio)
- Milestones: 6 (handoff contract only)
- Engine deliverables:
  - doctor/probe and localhost policy contracts
- Studio runtime embedding: downstream project

`I` Onboarding + demo project
- Milestones: 3, 6
- Engine deliverables:
  - demo artifact contract + quickstart/checklist docs
- interactive guided UI flow: downstream project

`J` Private alpha + fixes
- Milestones: 3, 6
- Engine deliverables:
  - blocker triage criteria
  - release candidate gate checklist

`K` Course licensing + alumni discount
- Milestones: deferred outside current Engine launch scope
- Engine stance:
  - no licensing/entitlement coupling in core runtime path for cohort MVP

`L` Cohort hardening + support playbook
- Milestones: 3, 5, 6
- Engine deliverables:
  - progress/error event contracts
  - sanitized support bundle contract (no vault content)
  - IRB-safe guidance docs

## Timeline Integration (Engine-facing)

Now -> late March:
- Milestone 1 closure focus + Milestone 3 security/policy contract slice

April:
- Milestone 4/5 overlap on Context Sets + A2UI/tooling contracts

May:
- Milestone 4 retrieval hardening + Milestone 6 export contract start

June:
- Milestone 6 handoff contracts, runtime probe/doctor hardening, export contract completion

July:
- Milestone 3/6 release-readiness docs, demo artifacts, alpha gate triage

Aug 1-15:
- Cohort hardening pass + release candidate freeze checklist

## Cohort-Ready Binary Checks (Engine)

1. Confidential defaults and hard blocks pass on clean install.
2. Section -> context set -> run -> patch -> export loop is deterministic and auditable.
3. Retrieval returns provenance-linked excerpts with policy-safe fallbacks.
4. Export requires explicit confirmation and audit trace.
5. A2UI fallback safety invariants hold (`GenericCard` + `UnknownCard`, no executable payloads).
6. Telemetry/proposal export remain opt-in, non-content, previewable, and disabled by default.
