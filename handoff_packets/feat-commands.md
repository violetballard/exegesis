# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: tightened `command_cli_contract()` so it validates the full grouped CLI parser surface reconstructed from the contract lookup table, not just canonical command order, and added regression coverage for alias-level drift.
- Canonical demo-path mapping sentence: this slice makes `preview and apply or reject a patch` more real because the patch-review CLI surface for `diff-preview` now fails fast if the parser or contract surface drops or mutates the `diff` alias while the canonical command sequence still appears unchanged.
- Concrete blocker removed: without this change, alias-level parser drift could silently break the `diff-preview` entrypoint used for the patch-review step while `canonical_names` still looked valid, so the CLI operator surface was not deterministically guarded.

## Tasks Completed
1. Hardened `src/qual/commands/catalog.py` so `command_cli_contract()` reconstructs grouped entrypoints from `lookup_table` and verifies that full surface against both the catalog-defined and live parser projections.
2. Added a regression in `tests/unit/test_commands_catalog.py` proving `_validate_command_cli_contract()` raises when the `diff` alias disappears from the contract surface while `canonical_names` stays unchanged.
3. Refreshed the lane handoff metadata so the canonical demo-path step is stated explicitly as `preview and apply or reject a patch`.
4. Re-ran the required gates for the updated command-catalog slice.

## Files Changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_command_cli_contract_rejects_mutated_diff_alias_with_stable_canonical_names` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
- Verification rerun timestamp: `2026-04-24T12:08:15Z`

## Risks / Blockers
- Risks: future command-surface edits still need to keep `_CLI_ENTRYPOINTS`, command specs, and shared contract tests aligned.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop` because this slice preserves CLI compatibility while Textual remains disabled by hardening the `diff-preview` patch-review entrypoint.
- `ROADMAP.md` canonical demo path step `preview and apply or reject a patch` because alias-level parser drift on `diff` now fails fast instead of silently weakening that step's CLI surface.
- `ROADMAP.md` lane mapping `feat-commands` because this lane owns CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because CLI compatibility must remain stable while Textual stays disabled.
- `PRODUCT_VISION.md` near-term product truth because the CLI is still the active operator surface, so this drift check removes a concrete blocker on the patch-review step of the active MVP loop.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval mechanism: `scripts/scope-check.sh` branch allowlist for `codex/feat-commands*`
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
