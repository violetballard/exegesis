# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the CLI contract reuses the canonical `command_names()` ordering and raises if the parser surface drifts from the command catalog, then added focused regression coverage for canonical-order alignment and drift rejection in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path mapping sentence: this slice specifically strengthens `preview and apply or reject a patch` in the current CLI-first Milestone 3 loop because the operator reaches that step through the `diff-preview` and `diff` patch-review entrypoints, and those entrypoints now fail fast if the parser surface drifts from the canonical catalog instead of silently changing the command contract while Textual remains disabled.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the patch-review CLI surface from the catalog while leaving the contract seemingly valid, which weakened the deterministic command path the operator uses to reach patch review and apply-or-reject follow-up work.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

## Tasks Completed
1. Hardened `command_cli_contract()` so it validates canonical command names against `command_names()` instead of rebuilding a divergent list from parser lookup output.
2. Preserved canonical CLI contract ordering by returning the validated catalog-order tuple directly.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.
4. Refreshed the lane handoff metadata so it names the exact canonical demo-path step advanced and cites the traceable shared-test approval source.
5. Re-ran the required gates for the command-catalog slice.

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

## Risks / Blockers
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the `diff-preview` and `diff` patch-review entrypoints stay deterministic.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop` because this slice preserves CLI compatibility while the migration continues by making the patch-review command contract deterministic and drift-resistant.
- `ROADMAP.md` canonical demo path because the concrete operator step protected is `preview and apply or reject a patch`, where the `diff-preview` and `diff` entrypoints now stay tied to the canonical catalog and fail fast on drift.
- `ROADMAP.md` lane mapping `feat-commands` because this lane owns CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because the active CLI operator surface now rejects parser/catalog drift before it can silently change the patch-review command contract.
- `PRODUCT_VISION.md` near-term product truth because the CLI remains the active operator surface while Textual is disabled, and this change hardens a real operator path rather than abstract CLI metadata.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Shared-by-approval regression path: `tests/unit/test_commands_catalog.py`
- Approval source: `scripts/scope-check.sh` branch allowlist for `codex/feat-commands*`, which explicitly permits `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
