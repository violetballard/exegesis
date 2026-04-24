# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Reviewed implementation basis:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Scope completed: hardened `command_cli_contract()` for `preview and apply or reject a patch` by protecting the CLI patch-review surface so the parser-derived canonical command names stay locked to the declared command catalog and fail fast on drift.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Required packet statement: this change makes `preview and apply or reject a patch` more real by forcing the public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: parser or catalog drift can no longer silently change the canonical command contract, which keeps the CLI fallback deterministic at the patch-review step of the canonical demo path.
- Route-coverage evidence anchor: `tests/unit/test_commands_catalog.py` keeps the CLI-first claim pinned to the tested patch-review route entry `("patch-review", "diff-preview", ("diff-preview", "diff"))` in the smoke-route summary and route-contract assertions.
- Plan-alignment statement: this is one patch-review contract-hardening slice inside the active CLI-first MVP path. Deterministic CLI contract validation preserves the operator-facing command surface while UI work remains secondary. It does not claim new retrieval, persistence, export, audit-path, or broader workflow behavior.
- Current roadmap alignment statement: this slice stays aligned to the current canonical roadmap by narrowing its claim to command and diff-preview hardening under Milestone 1 and CLI fallback reliability under the MVP-flow exit criteria in Milestone 5. It does not claim retrieval, persistence, export, audit-path, or broader workflow behavior.
- Packet refresh traceability: later `docs(commands)` commits are metadata-only and update only `handoff_packets/feat-commands.md`, `THREAD_PACKET.md`, and `THREAD.md`.
- High-risk kickoff context:
  - lane/owned paths: `src/qual/commands/**`
  - scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible command contract locked to the parser/catalog boundary so the CLI can still execute the MVP loop while Textual remains disabled
  - risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file
  - planned scope: 4-task high-risk slice limited to command-contract hardening, shared regression coverage, packet correction, and required gate reruns
  - early review triggers: before first edit to any shared or integrator-locked file, before changing public interfaces or command contracts, and before touching provider routing or config behavior
  - stop triggers: unresolved test, lint, or typecheck failure after `2` focused fix attempts, unresolved `make scope-check`, or budget, size, or time limit hit
- Roadmap item(s) affected:
  - `ROADMAP.md` active lane: `feat-commands`
  - `ROADMAP.md` Milestone 1 scope: `Command and diff-preview behavior hardening`
  - `ROADMAP.md` Milestone 5 exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`
- Vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
  - `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`
  - specific requirements advanced:
    - `CLI remains a first-class surface for development and reliability.`
    - `CLI remains able to render a text fallback of the same underlying artifacts.`
  - no claim against persistence, audit hooks, retrieval progress, or workflow trace records; this diff does not add them
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or integrator-locked entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. `preview and apply or reject a patch`: locked the live CLI command contract to the command catalog so canonical-name drift fails closed before the operator reaches the patch-review verb set.
2. `preview and apply or reject a patch`: added focused regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:1) covering canonical-order alignment and command-catalog drift rejection for the patch-review CLI surface.
3. `preview and apply or reject a patch`: updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1), [THREAD_PACKET.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD_PACKET.md:1), and [THREAD.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD.md:1) so the re-review packet points to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, states the canonical demo-path step explicitly, and ties each completed task to that step.
4. `preview and apply or reject a patch`: recorded the completed high-risk kickoff context, including the risk reason for the shared-test exception and command-contract touchpoint, so the 4-task cap remains auditable against the same reviewed implementation scope.

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
- Verification rerun timestamp: `2026-04-24T09:34:20Z UTC`

## Risks / Blockers
- Risks: future command-surface changes now need to keep the CLI lookup-table behavior and the shared regression suite aligned so the canonical command contract stays catalog-locked.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval basis: `THREAD_OWNERSHIP.md` marks the test path as non-owned shared coverage rather than an integrator-locked path, and `scripts/scope-check.sh` `is_approved_shared_test()` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: `none`
