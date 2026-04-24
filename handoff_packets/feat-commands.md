# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the CLI contract reuses the canonical `command_names()` ordering and raises if the parser surface drifts from the command catalog, then added focused regression coverage for canonical-order alignment and drift rejection in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: `continue working without losing context` in the CLI-first engine loop.
- Canonical demo-path mapping sentence: this Milestone 3 CLI-contract hardening slice directly strengthens `continue working without losing context` by keeping the active CLI command contract deterministic while Textual remains disabled.
- Concrete blocker removed: before this change, parser drift could silently desynchronize the CLI surface from the catalog while leaving the contract seemingly valid, which meant an operator could hit `continue working without losing context` against a CLI contract that had drifted away from the canonical MVP path without an immediate failure.
- Traceability note: reviewed implementation commit is `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

## Tasks Completed
1. Hardened `command_cli_contract()` so it validates canonical command names against `command_names()` instead of rebuilding a divergent list from parser lookup output.
2. Preserved canonical CLI contract ordering by returning the validated catalog-order tuple directly.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and parser/catalog drift rejection.
4. Refreshed the lane handoff metadata so it names the exact canonical demo-path step advanced, cites the traceable shared-test approval source, and records the re-run gate results for the command-catalog slice.

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
- Risks: future command-surface edits still need to preserve the parser/catalog lock so the engine-first CLI loop stays deterministic from `project-open` through `continue working`.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop` because this slice removes a concrete blocker in the active CLI-first operator path by keeping the command surface deterministic at `continue working without losing context`.
- `ROADMAP.md` canonical demo path because the concrete operator step strengthened is `continue working without losing context`, and this CLI-contract hardening slice keeps that step's active command contract deterministic while Textual remains disabled.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because the active CLI operator surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on at `continue working without losing context`.
- `PRODUCT_VISION.md` near-term product truth because the CLI remains the active operator surface while Textual is disabled, and this change hardens one real operator step rather than claiming broader command reachability.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Shared-by-approval regression path: `tests/unit/test_commands_catalog.py`
- Approval source: `scripts/scope-check.sh` branch allowlist for `codex/feat-commands*`, which explicitly permits `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
