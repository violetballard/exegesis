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
  - `82fb2cd0576d0ded9e0790908a266d9f3634d39f` (`docs(commands): tighten patch-review demo path mapping`) is the prior docs-only branch tip before this refresh and does not change the implementation scope.
  - `0113bb75c4b22b80dfbaaf0850ea3205a2b6d104` (`docs(commands): refresh reviewer fix packet tip`) remained packet-only and kept the review basis anchored to the full branch-tip implementation lineage.
- This follow-up fixer refresh also updates `THREAD_PACKET.md` only after rerunning the full required gate set on `2026-04-16`; it does not change the implementation scope.
- This final feature-fixer closure pass on `2026-04-16` adds focused regression coverage for the existing deterministic command-resolution helpers in `tests/unit/test_commands_catalog.py` and refreshes this packet after a green gate rerun.
- This re-review refresh on `2026-04-16` is packet-only: it preserves the same implementation scope, keeps the reviewer-requested demo-path mapping explicit, and records a fresh required-gates rerun on the current branch tip before resubmission.

## Reviewer-required fixes closure
- Required fix `1`: the packet is anchored to branch tip rather than `f8d860ed...` alone, and it lists the non-metadata implementation commits and implementation files changed after that earlier slice.
- Required fix `2`: the stale claim that later commits were metadata-only has been removed; only the packet-only `docs(commands): ...` commits are treated as docs-only alignment commits.
- Required fix `3`: the canonical demo-path step advanced is stated explicitly below and mapped to the Milestone 3 CLI-first loop.
- Required fix `4`: the commands-run and budget/limits notes below are stated against the same current branch-tip scope named in this packet.
- Fixer verification on `2026-04-16`: reran the full required gate set in this lane worktree during this closure pass. The reviewed implementation scope remains the same branch-tip command-contract lineage named above, with this final pass adding focused regression coverage for the existing deterministic resolution helpers without widening the lane-owned runtime surface.
- Final reviewer-fix closure on `2026-04-16`: this refresh preserves the explicit canonical demo-path mapping to `preview and apply or reject a patch`, with secondary support for `continue working`, and records the final command-resolution helper coverage used to keep that CLI surface deterministic.
- Re-review refresh on `2026-04-16`: the packet remains anchored to the current branch-tip implementation lineage, and this packet-only commit does not widen scope beyond the already-reviewed command-contract and shared-test files.

## Reviewer-fix resubmission note
- This packet no longer narrows review to `f8d860ed...` alone. It covers the full current branch-tip lineage: implementation through `cea5da3599799e72b24ed5f3e88474f3e275846a`, then packet-only docs refreshes through prior tip `0113bb75c4b22b80dfbaaf0850ea3205a2b6d104`, plus this current reviewer-fix closure pass.
- The implementation scope under review is the actual branch-tip runtime and test surface changed after `f8d860ed...`: `src/qual/commands/__init__.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, and `tests/unit/test_commands_catalog.py`.
- The concrete blocker removed is silent drift in the CLI `patch-review` surface: without these follow-on validations and smoke-contract helpers, parser/catalog divergence can change the operator contract for `preview and apply or reject a patch` without a fast failure in smoke tests.
- The focused regression additions include the concrete drift cases requested in review: alias-for-canonical substitution and CLI entrypoint reordering.
- The protected CLI-first smoke route is stated explicitly for re-review: `project-open -> retrieval -> patch-review -> export-handoff`.
- This resubmission commit is packet-only and keeps that same protected smoke route and reviewer-requested mapping intact on the current branch tip.

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
- Additional `docs(commands): ...` commits after `cea5da35` through `0113bb75` update `THREAD_PACKET.md` only and do not change the implementation files above.
- This current feature-fixer closure pass updates `tests/unit/test_commands_catalog.py` and `THREAD_PACKET.md` after rerunning the required handoff gates.

## Scope goal
- Harden the CLI command contract so command catalog, parser entrypoints, route ordering, and invocation planning stay deterministic and fail fast if the parser surface drifts from the catalog.
- Keep the `patch-review` command entrypoint stable for the canonical demo-path step `preview and apply or reject a patch`, with downstream support for `continue working`, so this contract hardening remains first-order Milestone 3 CLI compatibility work instead of generic cleanup.
- High-risk rationale for this handoff: the implementation includes one approved shared test edit in `tests/unit/test_commands_catalog.py`; no integrator-locked runtime entrypoints, provider surfaces, or routing/config files were changed.

## Risk reason
- High-risk/shared-file template is used because this handoff touches the approved shared test path `tests/unit/test_commands_catalog.py` and hardens the public CLI command-contract surface that must stay deterministic for the CLI-first MVP loop.

## Lane/owned paths
- Owned runtime path in this worktree: `src/qual/commands/**`
- Approved non-owned test path for this handoff: `tests/unit/test_commands_catalog.py`

## Canonical demo-path step advanced
- Exact demo-path mapping for re-review: this command-catalog hardening makes `preview and apply or reject a patch` more real by preventing silent parser/catalog drift in the CLI `patch-review` surface, with secondary support for `continue working`.
- Primary step advanced: `preview and apply or reject a patch`
- Secondary step supported: `continue working`
- Reviewer exact mapping: this hardens the `patch-review` CLI contract and the surrounding `continue working` operator surface while Textual remains disabled.
- This work advances the canonical engine-first demo path from `AGENTS.md` and `ROADMAP.md` by hardening the CLI operator contract for the patch-preview/apply-reject portion of the MVP loop while Textual remains disabled.
- It makes that CLI-first Milestone 3 step more real by ensuring parser drift cannot silently change the command contract a user depends on to preview and apply or reject a patch and continue working through the same stable command surface.

## Scope completed
- Hardened `command_cli_contract()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) so canonical CLI names must match `command_names()` and declared per-command CLI entrypoints must match the validated parser surface, with drift raising `ValueError`.
- Expanded the command catalog contract in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) to model explicit per-command CLI entrypoints, deterministic route tokens, invocation-plan metadata, parser-surface lookup helpers, and the MVP smoke contract from the same canonical catalog.
- Added deterministic command-resolution helpers in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py) so CLI surface tokens resolve to canonical command metadata and primary invocation argv from the same validated route catalog.
- Exported the expanded catalog contract surface from [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py) so compatibility imports stay aligned with the branch-tip implementation.
- Fixed bounded diff preview truncation in [src/qual/commands/diff_preview.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/diff_preview.py) so the `patch-review` step stays deterministic when CLI output must be truncated.
- Added and retained focused regression coverage in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py) for canonical-order alignment, alias-substitution and reorder parser-drift rejection, explicit CLI token handling, route-token determinism, invocation-plan consistency, parser-surface lookup helpers, deterministic command resolution, MVP smoke-contract behavior, and deterministic smoke invocation metadata.
- Reissued the handoff packet so the review basis, files changed list, demo-path field, and AGENTS mapping now match the full branch-tip implementation on this branch.
- Refreshed the handoff packet for final reviewer-fix closure without changing the implementation scope.

## Kickoff budget/limits compliance
- High-risk/shared-file handoff by approved shared-test exception only: the implementation stayed within the `4`-task cap and the file-count cap.
- The full branch-tip implementation under review changed `4` implementation files plus `THREAD_PACKET.md`, with one approved non-owned shared test path.
- The broader reviewed branch-tip scope from `f8d860ed...` through pre-refresh tip `16ef7c91...` still exceeds the original high-risk net-size guideline, so this packet reports the real recovered scope instead of restating the earlier narrowed one-file slice.

## Approved exception note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Tasks completed (numbered)
1. Made the canonical demo-path step `preview and apply or reject a patch` more real by locking the `patch-review` CLI contract to canonical command ordering and fail-fast parser-drift validation.
2. Stabilized per-command CLI token, route token, parser lookup, invocation-plan, and MVP smoke contracts directly from the command catalog.
3. Strengthened the same `preview and apply or reject a patch` step, with secondary support for `continue working`, by fixing bounded diff preview truncation, adding deterministic invocation metadata to the smoke contract, and exporting the expanded command contract API from `src/qual/commands/__init__.py` so compatibility imports match the branch-tip implementation.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the deterministic contract, parser surface helpers, deterministic command resolution, smoke route, route helpers, and smoke invocation metadata.

## Files changed
### Implementation files changed
- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py` (non-owned test path; explicit approved exception recorded in this handoff)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
- Revalidated on `2026-04-16` in this feature-fixer closure pass; the reviewed implementation scope remains the same branch-tip command-contract lineage named above, with the additional deterministic command-resolution helper coverage in the current commit.
- Revalidated again on `2026-04-16` in this packet-only re-review refresh; no implementation files changed in this commit, and the reviewed scope remains the same branch-tip command-contract lineage named above.
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS (`159` tests + smoke)
- `./typecheck-test.sh`: PASS (`python3 -m compileall -q src`)
- `make ci`: PASS

## Risks / blockers
- Risk: `MEDIUM`
- Risk note: the only non-owned implementation path is `tests/unit/test_commands_catalog.py` under the approved shared-test exception; no integrator-locked files or provider/routing surfaces changed.
- Blockers: none

## Required handoff fields
### Scope completed
- CLI compatibility now depends on one deterministic command catalog that defines parser entrypoints, parser lookup helpers, route ordering, smoke-route metadata, and invocation metadata without allowing silent parser/catalog drift.
- This specifically hardens the canonical demo-path step `preview and apply or reject a patch`, with direct support for `continue working`, by keeping the `patch-review` CLI contract and the smoke route `project-open -> retrieval -> patch-review -> export-handoff` stable and smoke-testable while Textual remains disabled.
- Scope boundary: this change only hardens command-catalog and CLI-contract determinism; it does not add new commands, new flags, or CLI-side business logic.

### Canonical demo-path step advanced
- Primary step advanced: `preview and apply or reject a patch`
- Secondary step supported: `continue working`
- The packet fix is first-order Milestone 3 work because it protects the stable CLI operator surface used to preview and apply or reject a patch and then keep using the engine-first loop without silent parser/catalog drift.

### Roadmap item(s) affected
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by keeping the CLI-first smoke route `project-open -> retrieval -> patch-review -> export-handoff` deterministic and smoke-testable, with direct protection for the demo-path step `preview and apply or reject a patch`.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the stable operator surface that carries patch review and supports continuing work through it.

### Vision capability affected
- `Canonical engine contract` - the CLI surface for `project-open -> retrieval -> patch-review -> export-handoff` stays stable and machine-checkable while Textual remains disabled, especially at `patch-review` and the surrounding continue-working flow.
- `Auditable state and workflow` - parser/catalog drift now fails loudly instead of silently changing the operator contract for that CLI-first smoke route.

### Routing/provider impact note
- None. This change only affects local command-catalog and CLI contract validation, with no new commands, flags, or CLI-side business logic.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (approved non-owned shared test only; no integrator-locked implementation files)
- Non-owned implementation edit recorded explicitly: `tests/unit/test_commands_catalog.py`
- The lane-owned runtime edits remain inside `src/qual/commands/**`.
- No provider surfaces, routing/config behavior, or core CLI entrypoints such as `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` were edited in the reviewed implementation scope.
- This packet does not claim `8c9e22903ec7048ecfee2cb18709894c1daf8f41` is metadata-only; it is an implementation commit and is included above as part of the reviewed branch-tip scope.
- Approval basis remains explicit and unchanged: the reviewed implementation scope is limited to `src/qual/commands/catalog.py`, `src/qual/commands/__init__.py`, `src/qual/commands/diff_preview.py`, and the approved shared test exception `tests/unit/test_commands_catalog.py`; this packet refresh does not expand the command-surface scope beyond those files.
