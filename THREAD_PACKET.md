# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `8c9e22903ec7048ecfee2cb18709894c1daf8f41` (`feat(commands): stabilize command catalog contracts`)
- `552bec587c40cde059a4d329de958e06da5a0460` (`Add command parser surface lookup helpers`)
- `ad1f61fc5f29acc54f230e8361f6b85c776ddea7` (`Fix bounded diff preview truncation`)
- `9c485853ec0689e14bec3c5141e2b556538100f6` (`Add MVP command smoke contract`)
- `81cbb9529642b0647459d447f467a5fcbebdbe2e` (`fix(commands): align handoff and catalog tests`)
- `1abb3bc162bc6e718db82ff79beb8cfadda47d90` (`fix(commands): validate CLI parser surface`)
- `26658f395761421f90e4b843e50883787e60b1d0` (`Add command CLI shim contract`)
  - `8b52002c3f963820bb1b3efe7698c7f97c952ae5` (`fix(commands): reject parser surface drift`)
- `cea5da3599799e72b24ed5f3e88474f3e275846a` (`Add invocation metadata to command smoke contract`)
- Docs-only alignment commit(s):
  - Numerous packet-only `docs(commands): ...` commits touched `THREAD_PACKET.md` between the implementation commits above.
  - `ee88483683f57242406bbd0b5a895dddf7da8537` (`docs(commands): fix handoff traceability packet`) corrected the stale narrowed review basis and re-scoped the packet to the real branch-tip implementation.
  - This fixer pass updates `THREAD_PACKET.md` only so the handoff packet remains anchored to the actual branch-tip scope for re-review after the reviewer requested explicit packet regeneration.

## Reviewer-required fixes closure
- Required fix `1`: the packet is anchored to branch tip rather than `f8d860ed...` alone, and it lists the non-metadata implementation commits and implementation files changed after that earlier slice.
- Required fix `2`: the stale claim that later commits were metadata-only has been removed; only the packet-only `docs(commands): ...` commits are treated as docs-only alignment commits.
- Required fix `3`: the canonical demo-path step advanced is stated explicitly below and mapped to the Milestone 3 CLI-first loop.
- Required fix `4`: the budget/limits note below is stated against the true branch-tip implementation scope rather than the earlier narrowed slice.

## Reviewer-fix resubmission note
- This packet no longer narrows review to `f8d860ed...` alone. It covers the full branch-tip implementation lineage through `cea5da3599799e72b24ed5f3e88474f3e275846a`.
- The implementation scope under review is the actual branch-tip runtime and test surface changed after `f8d860ed...`: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, and `tests/unit/test_commands_catalog.py`.
- The concrete blocker removed is silent drift in the CLI `patch-review` surface: without these follow-on validations and smoke-contract helpers, parser/catalog divergence can change the operator contract for `preview and apply or reject a patch` without a fast failure in smoke tests.
- The focused regression additions include the concrete drift cases requested in review: alias-for-canonical substitution and CLI entrypoint reordering.
- The protected CLI-first smoke route is stated explicitly for re-review: `project-open -> retrieval -> patch-review -> export-handoff`.

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
- `cea5da35` added invocation metadata to the command smoke contract in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, so the CLI-first smoke route also exposes deterministic invocation planning for the canonical `patch-review` step.
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
- It makes that CLI-first Milestone 3 step more real by keeping the `patch-review` command surface, parser entrypoints, and the smoke route `project-open -> retrieval -> patch-review -> export-handoff` deterministic, so the operator contract stays explicit and easy to smoke-test instead of drifting silently between review cycles.

## Scope completed
- Hardened `command_cli_contract()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) so canonical CLI names must match `command_names()` and declared per-command CLI entrypoints must match the validated parser surface, with drift raising `ValueError`.
- Expanded the command catalog contract in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) to model explicit per-command CLI entrypoints, deterministic route tokens, invocation-plan metadata, parser-surface lookup helpers, and the MVP smoke contract from the same canonical catalog.
- Exported the expanded catalog contract surface from [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py) so compatibility imports stay aligned with the branch-tip implementation.
- Fixed bounded diff preview truncation in [src/qual/commands/diff_preview.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/diff_preview.py) so the `patch-review` step stays deterministic when CLI output must be truncated.
- Added and retained focused regression coverage in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py) for canonical-order alignment, alias-substitution and reorder parser-drift rejection, explicit CLI token handling, route-token determinism, invocation-plan consistency, parser-surface lookup helpers, MVP smoke-contract behavior, and deterministic smoke invocation metadata.
- Reissued the handoff packet so the review basis, files changed list, demo-path field, and AGENTS mapping now match the full branch-tip implementation on this branch.

## Kickoff budget/limits compliance
- High-risk/shared-file handoff: the implementation stayed within the `4`-task cap and the file-count cap.
- The full branch-tip implementation under review changed `4` implementation files plus `THREAD_PACKET.md`, with one approved non-owned shared test path.
- This full branch-tip recovery handoff does not fit the original high-risk net-size guideline: the implementation diff from `f8d860ed...` to branch tip `cea5da35...` is `1840` insertions and `147` deletions across `THREAD_PACKET.md`, `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, and `tests/unit/test_commands_catalog.py`.
- This packet is intentionally reporting that broader branch-tip scope instead of restating the earlier narrowed one-file slice.

## Approved exception note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Locked the CLI contract to canonical command ordering and fail-fast parser-drift validation.
2. Stabilized per-command CLI token, route token, parser lookup, invocation-plan, and MVP smoke contracts directly from the command catalog.
3. Fixed bounded diff preview truncation, added deterministic invocation metadata to the smoke contract, and exported the expanded command contract API from `src/qual/commands/__init__.py` so compatibility imports match the branch-tip implementation.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the deterministic contract, parser surface helpers, smoke route, route helpers, and smoke invocation metadata.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py` (non-owned test path; explicit approved exception recorded in this handoff)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
- Revalidated on `2026-04-12` in this reviewer-fix closure pass.
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
- This specifically hardens the canonical demo-path step `preview and apply or reject a patch` by keeping the `patch-review` operator entrypoint, the smoke route `project-open -> retrieval -> patch-review -> export-handoff`, and bounded diff output stable and smoke-testable while Textual remains disabled.

### Canonical demo-path step advanced
- `preview and apply or reject a patch`
- Secondary support: `continue working`
- The packet fix is first-order Milestone 3 work because it protects the CLI-first `patch-review` contract used to execute that canonical engine workflow step.

### Roadmap item(s) affected
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by keeping the CLI-first smoke route `project-open -> retrieval -> patch-review -> export-handoff` deterministic and smoke-testable, with direct protection for the `patch-review` demo-path step.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `Canonical engine contract` - the CLI surface for `project-open -> retrieval -> patch-review -> export-handoff` stays stable and machine-checkable while Textual remains disabled.
- `Auditable state and workflow` - parser/catalog drift now fails loudly instead of silently changing the operator contract for that CLI-first smoke route.

### Routing/provider impact note
- None. This change only affects local command-catalog and CLI contract validation.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (non-owned test path only; no integrator-locked implementation files)
- Non-owned implementation edit recorded explicitly: `tests/unit/test_commands_catalog.py`
- The lane-owned runtime edits remain inside `src/qual/commands/**`.
- This packet does not claim `8c9e22903ec7048ecfee2cb18709894c1daf8f41` is metadata-only; it is an implementation commit and is included above as part of the reviewed branch-tip scope.
