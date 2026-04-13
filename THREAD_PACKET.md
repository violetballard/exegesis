# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `8c9e22903ec7048ecfee2cb18709894c1daf8f41` (`feat(commands): stabilize command catalog contracts`)
- Docs-only alignment commit(s):
  - Current fixer pass updates `THREAD_PACKET.md` only so the handoff matches the actual branch-tip implementation.

## Reviewer-fix resubmission note
- This packet now treats the branch tip `8c9e22903ec7048ecfee2cb18709894c1daf8f41` as implementation work, not as a metadata-only refresh.
- The implementation scope described below matches the real branch-tip files and the earlier test coverage commit that established regression coverage for this lane.
- `src/qual/commands/__init__.py` is included explicitly because the branch tip exports the expanded command-catalog contract surface and is part of the implementation under review.
- The concrete blocker removed is silent drift in the CLI `patch-review` surface: without this guard, parser/catalog divergence can change the operator contract for the canonical `preview and apply or reject a patch` step without a fast failure in smoke tests.

## Branch-tip traceability
- `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` introduced the original command-catalog drift guard in `src/qual/commands/catalog.py` and the focused regression coverage in `tests/unit/test_commands_catalog.py`.
- `8c9e22903ec7048ecfee2cb18709894c1daf8f41` expanded the branch-tip implementation in `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py`; this handoff reviews that implementation commit directly instead of treating it as metadata-only.

## Scope goal
- Harden the CLI command contract so command catalog, parser entrypoints, route ordering, and invocation planning stay deterministic and fail fast if the parser surface drifts from the catalog.
- Keep the `patch-review` command entrypoint stable for the canonical demo-path steps `preview and apply or reject a patch` and `continue working`, so this contract hardening remains first-order Milestone 3 CLI compatibility work instead of generic cleanup.

## Lane/owned paths
- Owned runtime path in this worktree: `src/qual/commands/**`
- Approved non-owned test path for this handoff: `tests/unit/test_commands_catalog.py`

## Canonical demo-path step advanced
- `preview and apply or reject a patch`
- `continue working`
- This work advances the `preview and apply or reject a patch` step in the canonical engine-first demo path from `AGENTS.md` and `ROADMAP.md`.
- It makes that CLI-first Milestone 3 step more real by keeping the `patch-review` command surface, parser entrypoints, and smoke-route ordering deterministic, so the operator contract stays explicit and easy to smoke-test instead of drifting silently between review cycles.

## Scope completed
- Hardened `command_cli_contract()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) so canonical CLI names must match `command_names()` and drift raises `ValueError`.
- Expanded the command catalog contract in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) to model explicit per-command CLI entrypoints, deterministic route tokens, and invocation-plan metadata from the same canonical catalog.
- Exported the expanded catalog contract surface from [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py) so compatibility imports stay aligned with the branch-tip implementation.
- Added and retained focused regression coverage in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py) for canonical-order alignment, parser-drift rejection, explicit CLI token handling, route-token determinism, and invocation-plan consistency.
- Reissued the handoff packet so the review basis, files changed list, and AGENTS mapping now match the actual implementation on this branch.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: stayed within `4` tasks, `30m`, and the lane size limits.
- The implementation stayed in the owned command path plus the one approved non-owned shared test file.

## Approved exception note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Locked the CLI contract to canonical command ordering and fail-fast parser-drift validation.
2. Stabilized per-command CLI token, route token, and invocation-plan contracts directly from the command catalog.
3. Exported the expanded command contract API from `src/qual/commands/__init__.py` so compatibility imports match the branch-tip implementation.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the deterministic contract and route/invocation helpers.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py` (non-owned test path; explicit approved exception recorded in this handoff)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
- Revalidated on `2026-04-12` in this fixer pass.
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `HIGH`
- Blockers: none

## Required handoff fields
### Scope completed
- CLI compatibility now depends on one deterministic command catalog that defines parser entrypoints, route ordering, and invocation metadata without allowing silent parser/catalog drift.
- This specifically hardens the canonical demo-path step `preview and apply or reject a patch` by keeping the `patch-review` operator entrypoint stable and smoke-testable while Textual remains disabled.

### Canonical demo-path step advanced
- `preview and apply or reject a patch`
- Secondary support: `continue working`
- The packet fix is first-order Milestone 3 work because it protects the CLI-first `patch-review` contract used to execute that canonical engine workflow step.

### Roadmap item(s) affected
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by keeping the `patch-review` demo-path step deterministic and smoke-testable.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `Canonical engine contract` - the CLI surface stays stable and machine-checkable while Textual remains disabled.
- `Auditable state and workflow` - parser/catalog drift now fails loudly instead of silently changing the operator contract.

### Routing/provider impact note
- None. This change only affects local command-catalog and CLI contract validation.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (non-owned test path only; no integrator-locked implementation files)
- Non-owned implementation edit recorded explicitly: `tests/unit/test_commands_catalog.py`
- The lane-owned runtime edits remain inside `src/qual/commands/**`.
- This packet does not claim `8c9e22903ec7048ecfee2cb18709894c1daf8f41` is metadata-only; it is an implementation commit and is included above as part of the reviewed branch-tip scope.
