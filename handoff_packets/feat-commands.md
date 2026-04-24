# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Reviewed implementation basis:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Scope completed: hardened `command_cli_contract()` for the current engine-first CLI smoke path by protecting the `project-open` / `retrieval` / `patch-review` command surface so the parser-derived canonical command names stay locked to the declared command catalog and fail fast on drift.
- Canonical demo-path step(s) advanced: `open project/document`, `retrieve`, `preview and apply or reject a patch`
- Required packet statement: this change makes `open project/document`, `retrieve`, and `preview and apply or reject a patch` more real by forcing the public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set on the current engine-first `project-open` / `retrieval` / `patch-review` smoke path.
- Concrete blocker removed: parser or catalog drift can no longer silently change the canonical command contract, which keeps the current CLI fallback deterministic across the `project-open` / `retrieval` / `patch-review` path.
- Route-coverage evidence anchor: `tests/unit/test_commands_catalog.py` keeps the CLI-first claim pinned to the tested patch-review route entry `("patch-review", "diff-preview", ("diff-preview", "diff"))` in the smoke-route summary and route-contract assertions.
- Plan-alignment statement: this is one CLI smoke-path contract-hardening slice inside the active engine-first MVP path. Deterministic CLI contract validation preserves the operator-facing bootstrap, context-basket, and diff-preview command surface for the current `project-open` / `retrieval` / `patch-review` smoke path while Textual remains disabled and interactive clients stay secondary. It does not claim new retrieval internals, patch application, persistence, export, audit-path, or broader workflow behavior.
- `AGENTS.md` compliance statement: every active lane task in this packet is tied to the canonical `open project/document`, `retrieve`, or `preview and apply or reject a patch` steps, and the packet now states the concrete blocker removed on that path.
- Current roadmap alignment statement: this slice stays aligned to the current canonical roadmap by narrowing its claim to command and diff-preview hardening under Milestone 1 and CLI fallback reliability at the `project-open` / `retrieval` / `patch-review` contract boundary while Textual remains disabled. `terminal` and `export-handoff` remain outside the review basis for this packet and appear here only as incidental aliases inside the shared catalog contract. It does not claim retrieval internals, persistence, export, audit-path, or broader workflow behavior.
- Packet refresh traceability: later `docs(commands)` commits are metadata-only and update only `handoff_packets/feat-commands.md`, `THREAD_PACKET.md`, and `THREAD.md`.
- High-risk kickoff context:
  - lane/owned paths: `src/qual/commands/**`
  - scope goal: make the canonical `open project/document`, `retrieve`, and `preview and apply or reject a patch` steps more real by keeping the operator-visible command contract locked to the parser/catalog boundary so the CLI fallback stays deterministic across the `project-open` / `retrieval` / `patch-review` smoke path while interactive clients stay secondary
  - risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file
  - planned scope: 4-task high-risk slice limited to command-contract hardening, shared regression coverage, packet correction, and required gate reruns
  - early review triggers: before first edit to any shared or integrator-locked file, before changing public interfaces or command contracts, and before touching provider routing or config behavior
  - stop triggers: unresolved test, lint, or typecheck failure after `2` focused fix attempts, unresolved `make scope-check`, or budget, size, or time limit hit
- Roadmap item(s) affected:
  - `ROADMAP.md` active lane: `feat-commands`
  - `ROADMAP.md` Milestone 1 scope: `Command and diff-preview behavior hardening`
  - roadmap relevance is limited to the `project-open` / `retrieval` / `patch-review` segment of the CLI-first MVP loop; `terminal` and `export-handoff` are not part of this packet's approval basis
- Vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
  - `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`
  - specific requirements advanced:
    - `CLI remains a first-class surface for development and reliability.`
    - `CLI remains able to render a text fallback of the same underlying artifacts.`
  - no claim against persistence, audit hooks, retrieval internals, or workflow trace records; this diff does not add them
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or integrator-locked entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. `open project/document`, `retrieve`, `preview and apply or reject a patch`: locked the live CLI command contract to the command catalog so canonical-name drift fails closed before the operator reaches the `project-open`, `retrieval`, or `patch-review` verb sets.
2. `open project/document`, `retrieve`, `preview and apply or reject a patch`: added focused regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:1) covering canonical-order alignment and command-catalog drift rejection for the current CLI smoke surface.
3. `open project/document`, `retrieve`, `preview and apply or reject a patch`: updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1), [THREAD_PACKET.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD_PACKET.md:1), and [THREAD.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD.md:1) so the re-review packet points to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, names the hardened smoke-path steps explicitly, and ties each completed task to that path.
4. `open project/document`, `retrieve`, `preview and apply or reject a patch`: recorded the completed high-risk kickoff context, including the risk reason for the shared-test exception and command-contract touchpoint, so the 4-task cap remains auditable against the same reviewed implementation scope.

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
- Verification rerun timestamp: `2026-04-24T09:40:00Z UTC`

## Risks / Blockers
- Risks: future command-surface changes now need to keep the CLI lookup-table behavior and the shared regression suite aligned so the canonical command contract stays catalog-locked.
- Residual scope risk: because `command_cli_contract()` validates the shared catalog, a later `terminal` or `export-handoff` alias edit can still trip the guard even though those runtime semantics are intentionally excluded from this handoff's approval basis.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval basis: `THREAD_OWNERSHIP.md` marks the test path as non-owned shared coverage rather than an integrator-locked path, and `scripts/scope-check.sh` `is_approved_shared_test()` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: `none`
