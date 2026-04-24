# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Reviewed implementation basis:
  - `8e747334f4da2d5486e15088979a36184c8c9116` (`feat(commands): validate full CLI token projection`)
- Approval basis pin:
  - Re-review remains pinned to implementation commit `8e747334f4da2d5486e15088979a36184c8c9116` and the two implementation files only: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
  - The current packet-refresh commit is metadata-only and is not part of the implementation approval basis.
- Scope completed: hardened `command_cli_contract()` for the current engine-first CLI smoke path by protecting the supporting `project-open` / `retrieval` / `patch-review` command surface so the live parser entrypoints stay locked to the declared command catalog and fail fast on parser-surface drift.
- Primary canonical demo-path step advanced: `continue working without losing context`
- Supporting smoke-path steps strengthened for that primary step: `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`
- Roadmap loop mapping:
  - `open project/document` advances the roadmap loop's `vault` and `context` entry boundary through the `project-open` command surface.
  - `retrieve relevant material` advances the roadmap loop's `context` and `run` handoff boundary through the `retrieval` command surface.
  - `preview and apply or reject a patch` advances the roadmap loop's `patch` boundary through the `patch-review` command surface.
- Required packet statement: this change makes `continue working without losing context` more real by forcing the supporting `project-open` / `retrieval` / `patch-review` public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set on the current engine-first fallback path.
- Reviewer wording trace: this work makes the `open project/document` and broader CLI operator path more real by preventing silent command-surface drift while Textual remains disabled.
- Concrete blocker removed: parser or catalog drift can no longer silently change the canonical command contract, including token-level reorderings, dropped canonical entrypoints, or lookup-table substitutions, which removes a concrete blocker on `continue working without losing context` by keeping the supporting `project-open` / `retrieval` / `patch-review` path deterministic.
- Route-coverage evidence anchor: `tests/unit/test_commands_catalog.py` keeps the CLI-first claim pinned to the tested patch-review route entry `("patch-review", "diff-preview", ("diff-preview", "diff"))` in the smoke-route summary and route-contract assertions.
- Plan-alignment statement: this is one CLI smoke-path contract-hardening slice inside the active engine-first MVP path. Deterministic CLI contract validation preserves the operator-facing bootstrap, context-basket, and diff-preview command surface that supports `continue working without losing context` on the current `project-open` / `retrieval` / `patch-review` smoke path while Textual remains disabled and interactive clients stay secondary. It does not claim new retrieval internals, patch application, persistence, export, audit-path, or broader workflow behavior.
- `AGENTS.md` compliance statement: this packet stays within the high-risk 4-task cap, records the shared-test exception, and includes the required handoff fields from `INTEGRATION.md`.
- Shared-test exception statement: the only non-owned edit is justified by the same `continue working without losing context` mapping claimed here, because `tests/unit/test_commands_catalog.py` is the evidence that the supporting `project-open` / `retrieval` / `patch-review` smoke path stays deterministic on the CLI fallback route instead of silently drifting.
- Current roadmap alignment statement: this slice stays aligned to the current canonical roadmap by narrowing its claim to Milestone 3 `Real workflow loop`, where `feat-commands` is the CLI compatibility and migration-safe entrypoint lane and the relevant exit criterion is that `CLI can still execute the MVP loop while Textual remains disabled`. Deterministic command-contract validation hardens the `project-open` / `retrieval` / `patch-review` boundary while `feat-console` stays deferred. `terminal` and `export-handoff` remain outside the review basis for this packet and appear here only as incidental aliases inside the shared catalog contract. It does not claim retrieval internals, persistence, export, audit-path, or broader workflow behavior.
- Packet refresh traceability: the current packet-refresh commit is metadata-only and updates only `handoff_packets/feat-commands.md`, `THREAD_PACKET.md`, and `THREAD.md`.
- Parser-surface evidence statement: `command_cli_contract()` now validates the full authoritative parser projection and derives `tokens` plus `lookup_table` from that same projection, so the implementation claim is full parser-surface drift detection rather than canonical-name ordering alone.
- Re-review refresh note: packet re-verified on `2026-04-24` after rerunning the full required local gates at `2026-04-24T11:08:30Z` UTC, with the canonical demo-path statement kept explicit for `continue working without losing context`.
- High-risk kickoff context:
  - lane/owned paths: `src/qual/commands/**`
  - scope goal: make the canonical `continue working without losing context` step more real by removing a concrete blocker at the CLI fallback boundary: silent parser/catalog drift on the operator-visible `project-open` / `retrieval` / `patch-review` command surface
  - risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file
  - planned scope: 4-task high-risk slice limited to command-contract hardening, shared regression coverage, packet correction, and required gate reruns
  - early review triggers: before first edit to any shared or integrator-locked file, before changing public interfaces or command contracts, and before touching provider routing or config behavior
  - stop triggers: unresolved test, lint, or typecheck failure after `2` focused fix attempts, unresolved `make scope-check`, or budget, size, or time limit hit
- Roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 `Real workflow loop`
  - `ROADMAP.md` lane mapping: `feat-commands` is the CLI compatibility and migration-safe entrypoint lane
  - `ROADMAP.md` exit criterion: `CLI can still execute the MVP loop while Textual remains disabled`
  - roadmap relevance is limited to the `project-open` / `retrieval` / `patch-review` command surface; `terminal` and `export-handoff` are not part of this packet's approval basis
- Vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
  - specific requirement advanced: `CLI compatibility is required while Textual remains disabled.`
  - no claim against A2UI payloads, persistence, audit hooks, retrieval internals, or workflow trace records; this diff does not add them
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or integrator-locked entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. `continue working without losing context`: locked the live CLI command contract to the command catalog so parser-surface drift fails closed before the operator reaches the wrong `project-open`, `retrieval`, or `patch-review` verb sets on the active CLI fallback path.
2. `continue working without losing context`: added focused regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:1) covering parser-surface alignment and command-catalog drift rejection for the supporting CLI smoke surface.
3. `continue working without losing context`: updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1), [THREAD_PACKET.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD_PACKET.md:1), and [THREAD.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD.md:1) so the re-review packet points to commit `8e747334f4da2d5486e15088979a36184c8c9116`, names the exact primary canonical demo-path step explicitly, and ties each completed task to that step.
4. `continue working without losing context`: recorded the completed high-risk kickoff context, including why the shared-test exception is required as evidence for that same demo-path mapping and command-contract touchpoint, so the 4-task cap remains auditable against the same reviewed implementation scope.

## Files Changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
- Verification rerun timestamp: `2026-04-24T11:08:30Z UTC`

## Risks / Blockers
- Risks: future command-surface changes now need to keep the CLI lookup-table behavior and the shared regression suite aligned so the canonical command contract stays catalog-locked.
- Residual scope risk: because `command_cli_contract()` validates the shared catalog, a later `terminal` or `export-handoff` alias edit can still trip the guard even though those runtime semantics are intentionally excluded from this handoff's approval basis.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval owner: the repo branch policy for `codex/feat-commands*`
- Approval mechanism: `scripts/scope-check.sh` `is_approved_shared_test()` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Approval basis: `THREAD_OWNERSHIP.md` limits lane-owned edits for `codex/feat-commands*` to `src/qual/commands/**`, so `tests/unit/test_commands_catalog.py` remains outside the owned path. The branch-specific shared-test allowlist above is the explicit approved mechanism that covers this one shared-file exception; no separate ad hoc exception was used. That shared-test exception is the evidence for the same `continue working without losing context` mapping claimed by this packet, because it proves the supporting `project-open` / `retrieval` / `patch-review` smoke path stays locked to the declared CLI contract while Textual remains disabled.
- Integrator-locked edits: `none`
