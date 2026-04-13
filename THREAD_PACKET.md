# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit(s):
  - `8c9e22903ec7048ecfee2cb18709894c1daf8f41` (`feat(commands): stabilize command catalog contracts`)
- Docs-only alignment commit(s):
  - None.

## Reviewer-fix resubmission note
- This fixer pass corrects packet traceability for the actual branch tip in this worktree instead of describing the older partial slice at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- The submitted implementation for re-review is the live branch-tip command-contract work in `src/qual/commands/catalog.py` and `src/qual/commands/__init__.py`, plus the focused shared test coverage in `tests/unit/test_commands_catalog.py`.
- This packet removes the stale `docs-only` refresh claim because the current branch tip is implementation work.
- The roadmap and vision mappings below use the current canonical labels from this worktree's planning docs.
- The required local gates were rerun in this worktree on `2026-04-12` before this handoff was finalized, in this order: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Scope goal
- Harden the CLI command contract so command-catalog metadata, parser entrypoints, smoke-route order, and invocation planning stay deterministic and fail fast if the parser surface drifts from the catalog.

## Lane/owned paths
- Owned runtime path in this worktree: `src/qual/commands/**`
- Approved non-owned test path for this handoff: `tests/unit/test_commands_catalog.py`

## Scope completed
- Expanded `src/qual/commands/catalog.py` so CLI entrypoints are declared on `CommandSpec`, validated through the command catalog, and exposed through deterministic CLI, route, surface, and invocation-plan contracts.
- Updated `src/qual/commands/__init__.py` exports so the stabilized command-catalog contract helpers stay available through the lane's public compatibility surface.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment, explicit CLI entrypoints, route tokens, invocation-plan helpers, and drift rejection.
- Regenerated the handoff packet so the review scope matches the actual branch tip and names every implementation file in scope.

## Canonical demo-path mapping
- Demo-path step advanced: `open project/document`.
- This lane makes that step more real by keeping the CLI-first operator contract deterministic: the bootstrap/open command entrypoint, its canonical routing position, and the smoke-route invocation plan now derive from one validated command catalog instead of from drift-prone parallel lists.
- Secondary strengthening: `preview and apply or reject a patch`, because the patch-review command route and primary CLI token are now validated through the same catalog contract.

## Kickoff budget/limits compliance
- High-risk shared-file handoff: stayed within `4` tasks, `30m`, and the lane size limits.
- The implementation slice remained limited to two owned command files plus one focused non-owned test file, so the handoff stayed narrow and reviewable.

## Approved exception note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- This handoff records that path consistently in the task list, files changed list, and scope-check note as the only non-owned implementation edit.

## Scope-policy note
- `tests/unit/test_commands_catalog.py` is the only non-owned implementation file named in this handoff.
- The lane-owned runtime path in this worktree is `src/qual/commands/**`, so this handoff keeps the test path called out separately instead of presenting it as lane-owned.
- This handoff uses the explicit approved exception note in this packet for `tests/unit/test_commands_catalog.py` as the approval basis for the non-owned test edit and does not claim any other exception or local scope-policy expansion.

## Tasks completed (numbered)
1. Moved CLI parser entrypoints into `CommandSpec` and validated them through the canonical command catalog so command resolution and CLI surfaces cannot silently drift.
2. Hardened the command-contract helpers in `src/qual/commands/catalog.py` so canonical command order, route ordering, primary CLI tokens, route lookup tables, and invocation plans all derive from one deterministic source.
3. Updated `src/qual/commands/__init__.py` to export the stabilized command-contract helpers through the compatibility surface used by the current CLI-first MVP lane.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for custom CLI entrypoints, invocation-plan helpers, route-token stability, and parser/catalog drift rejection.

## Files changed
### Implementation files changed
- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py` (non-owned test path; explicit approved exception recorded in this handoff)

### Docs-only alignment files changed
- `THREAD_PACKET.md`

## Commands run with results
- Revalidated on this reviewer-fix pass in the current worktree.
- Revalidation date: `2026-04-12`
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
- CLI command compatibility now has one deterministic command catalog for parser entrypoints, canonical command names, smoke-route order, and invocation planning, so operator-facing command behavior cannot silently drift.

### Roadmap item(s) affected
- `Milestone 3: Real workflow loop` - preserve CLI compatibility while the package/layout migration lands by keeping the command surface deterministic and migration-safe.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected
- `Canonical engine contract` - CLI compatibility remains stable while the command surface rejects parser drift before it can silently change the operator contract.
- `Auditable state and workflow` - the command surface now fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing/provider impact note
- None. This change only affects local command contract validation, CLI routing metadata, and focused command-catalog test coverage.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES` (non-owned test path only; no integrator-locked implementation files)
- Non-owned implementation edit recorded explicitly: `tests/unit/test_commands_catalog.py`
- No integrator-locked file is claimed in the implementation slice.
- The ownership map in this worktree keeps the lane-owned runtime path at `src/qual/commands/**` and does not present `tests/unit/test_commands_catalog.py` as owned, so this packet records that test path separately as an approved non-owned implementation edit rather than as lane-owned.
- This reviewer-fix pass does not change local scope policy or broaden the allowlist; it corrects handoff accuracy for the branch-tip implementation already present in this worktree.
