# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `8c9e22903ec7048ecfee2cb18709894c1daf8f41` (`feat(commands): stabilize command catalog contracts`)
  - `552bec58f1a19643b4797d770b0a8896443b9279` (`Add command parser surface lookup helpers`)
  - `ad1f61fc1d7e35025b5b1865953340b7a14c7fa7` (`Fix bounded diff preview truncation`)
  - `9c48585385f07f6861f5646663da8622714e8d73` (`Add MVP command smoke contract`)
  - `81cbb95200a4bf3a5e66a1bc927596fc59d6445f` (`fix(commands): align handoff and catalog tests`)
  - `1abb3bc1245cfd652ed0d26159f3bc78d85fcabe` (`fix(commands): validate CLI parser surface`)
  - `26658f398b5487455c4a14f9eb7e6d89fc4c72d6` (`Add command CLI shim contract`)
  - `8b52002c3f963820bb1b3efe7698c7f97c952ae5` (`fix(commands): reject parser surface drift`)
- Docs-only alignment commit(s):
  - Numerous packet-only `docs(commands): ...` commits touched `THREAD_PACKET.md` between the implementation commits above.
  - This fixer pass updates `THREAD_PACKET.md` only so the handoff packet matches the real branch-tip implementation at `8b52002c3f963820bb1b3efe7698c7f97c952ae5`.

## Reviewer-fix resubmission note
- This packet no longer narrows review to `f8d860ed...` alone. It covers the full branch-tip implementation lineage through `8b52002c3f963820bb1b3efe7698c7f97c952ae5`.
- The implementation scope under review is the actual branch-tip runtime and test surface changed after `f8d860ed...`: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, and `tests/unit/test_commands_catalog.py`.
- The concrete blocker removed is silent drift in the CLI `patch-review` surface: without these follow-on validations and smoke-contract helpers, parser/catalog divergence can change the operator contract for `preview and apply or reject a patch` without a fast failure in smoke tests.
- The focused regression additions include the concrete drift cases requested in review: alias-for-canonical substitution and CLI entrypoint reordering.

## Branch-tip traceability
- `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` introduced the original command-catalog drift guard in `src/qual/commands/catalog.py` and the focused regression coverage in `tests/unit/test_commands_catalog.py`.
- `8c9e22903ec7048ecfee2cb18709894c1daf8f41` expanded the branch-tip implementation in `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py` with deterministic CLI surface, route, and invocation contracts.
- `552bec58` added parser-surface lookup helpers and expanded contract coverage in `tests/unit/test_commands_catalog.py`.
- `ad1f61fc` tightened bounded diff preview truncation in `src/qual/commands/diff_preview.py`, which keeps the `patch-review` step stable under output limits.
- `9c485853` added the MVP smoke contract so the CLI-first smoke route stays machine-checkable from the same canonical catalog.
- `81cbb952` aligned the branch-tip tests and handoff packet with that implementation so the reviewed branch tip remains internally consistent.
- `1abb3bc1` added parser-surface validation so declared per-command CLI entrypoints must match the validated CLI surface.
- `26658f39` added the CLI shim contract so compatibility imports stay aligned with the expanded command surface.
- `8b52002c` completed the reviewer-fix series by rejecting parser-surface drift when validated CLI entrypoints no longer match the canonical contract.
- Additional `docs(commands): ...` commits between these implementation commits update `THREAD_PACKET.md` only and do not change the implementation files above.

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
- Hardened `command_cli_contract()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) so canonical CLI names must match `command_names()` and declared per-command CLI entrypoints must match the validated parser surface, with drift raising `ValueError`.
- Expanded the command catalog contract in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) to model explicit per-command CLI entrypoints, deterministic route tokens, invocation-plan metadata, parser-surface lookup helpers, and the MVP smoke contract from the same canonical catalog.
- Exported the expanded catalog contract surface from [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py) so compatibility imports stay aligned with the branch-tip implementation.
- Fixed bounded diff preview truncation in [src/qual/commands/diff_preview.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/diff_preview.py) so the `patch-review` step stays deterministic when CLI output must be truncated.
- Added and retained focused regression coverage in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py) for canonical-order alignment, alias-substitution and reorder parser-drift rejection, explicit CLI token handling, route-token determinism, invocation-plan consistency, parser-surface lookup helpers, and MVP smoke-contract behavior.
- Reissued the handoff packet so the review basis, files changed list, demo-path field, and AGENTS mapping now match the full branch-tip implementation on this branch.

## Kickoff budget/limits compliance
- High-risk/shared-file handoff: the implementation stayed within the `4`-task cap and the file-count cap.
- The full branch-tip implementation under review changed `4` implementation files plus `THREAD_PACKET.md`, with one approved non-owned shared test path.
- This full branch-tip recovery handoff does not fit the original high-risk net-size guideline: the implementation diff from `f8d860ed...` to `8b52002c...` is `1718` insertions and `112` deletions across the implementation files, plus `80` insertions and `35` deletions in `THREAD_PACKET.md`.
- This packet is intentionally reporting that broader branch-tip scope instead of restating the earlier narrowed one-file slice.

## Approved exception note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Locked the CLI contract to canonical command ordering and fail-fast parser-drift validation.
2. Stabilized per-command CLI token, route token, parser lookup, invocation-plan, and MVP smoke contracts directly from the command catalog.
3. Fixed bounded diff preview truncation and exported the expanded command contract API from `src/qual/commands/__init__.py` so compatibility imports match the branch-tip implementation.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the deterministic contract, parser surface helpers, smoke route, and route/invocation helpers.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py` (non-owned test path; explicit approved exception recorded in this handoff)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
- Revalidated on `2026-04-12` in this traceability-fix pass.
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
- CLI compatibility now depends on one deterministic command catalog that defines parser entrypoints, parser lookup helpers, route ordering, smoke-route metadata, and invocation metadata without allowing silent parser/catalog drift.
- This specifically hardens the canonical demo-path step `preview and apply or reject a patch` by keeping the `patch-review` operator entrypoint, smoke route, and bounded diff output stable and smoke-testable while Textual remains disabled.

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
