# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Reviewed implementation basis:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
- Scope completed: hardened `command_cli_contract()` for the canonical `preview and apply or reject a patch` step so the parser-derived canonical command names stay locked to the declared command catalog and fail fast on drift.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Required AGENTS sentence: this change makes `preview and apply or reject a patch` more real by forcing the public command surface to stay catalog-locked and fail closed before the operator reaches the wrong CLI verb set.
- Concrete blocker removed: parser or catalog drift can no longer silently change the canonical command contract, which keeps the CLI fallback deterministic at the patch-review step of the current engine-first MVP loop.
- Plan-alignment statement: this is one engine-first MVP review-step contract-hardening slice inside the current Milestone 3 loop. Deterministic CLI contract validation preserves the operator-facing command surface while the package/layout migration is in flight. It does not claim new retrieval, persistence, export, audit-path, or broader workflow behavior.
- Packet refresh traceability: later `docs(commands)` commits are metadata-only and update only `handoff_packets/feat-commands.md`, `THREAD_PACKET.md`, and `THREAD.md`.
- High-risk kickoff context:
  - lane/owned paths: `src/qual/commands/**`
  - scope goal: make the canonical `preview and apply or reject a patch` step more real by keeping the operator-visible command contract locked to the parser/catalog boundary during the current engine-first CLI loop while Textual remains disabled
  - risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file
  - planned scope: 4-task high-risk slice limited to command-contract hardening, shared regression coverage, packet correction, and required gate reruns
- Roadmap item(s) affected:
  - `ROADMAP.md` MVP focus active lane: `feat-commands`
  - `ROADMAP.md` Milestone 3: `preserve CLI compatibility while the package/layout migration lands`
  - `ROADMAP.md` lane mapping: `feat-commands`: `CLI compatibility and migration-safe entrypoints`
- Vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
  - specific requirement advanced: `CLI compatibility is required while Textual remains disabled.`
  - no claim against persistence, audit hooks, or workflow trace records; this diff does not add them
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
- Verification rerun timestamp: `2026-04-24T09:13:47Z UTC`

## Risks / Blockers
- Risks: future command-surface changes now need to keep the CLI lookup-table behavior and the shared regression suite aligned so the canonical command contract stays catalog-locked.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval basis: `THREAD_OWNERSHIP.md` marks the test path as non-owned shared coverage rather than an integrator-locked path, and `scripts/scope-check.sh` `is_approved_shared_test()` explicitly allowlists `tests/unit/test_commands_catalog.py` for `codex/feat-commands*`
- Integrator-locked edits: `none`
