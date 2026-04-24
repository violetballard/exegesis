# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix handoff metadata refresh`
- Review scope: command-catalog Milestone 3 CLI compatibility slice that hardens `command_cli_contract()` against parser-surface drift and keeps the returned contract in canonical command order
- Canonical demo-path step advanced: `patch-review` in the CLI-first `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff` MVP loop
- AGENTS.md alignment note: this packet explicitly names the single canonical demo-path step advanced by the reviewed slice, rather than only citing Milestone 3 or broad lane ownership.
- Required mapping statement: this slice directly makes `patch-review` more real in the current CLI-first MVP loop because `command_cli_contract()` now emits the validated canonical parser-entrypoint projection sourced from `_validated_cli_entrypoints_for()` and `_cli_entrypoints_by_name()` in `src/qual/commands/catalog.py` for the operator-facing `diff-preview` and `diff` surface, and the imported regression surface in `tests/unit/test_commands_catalog.py` covers both the catalog-order expectation and the parser-drift rejection path so the live patch-review contract fails fast instead of silently changing while Textual remains disabled.
- Concrete blocker removed: before this slice, parser drift could change the accepted patch-review CLI surface without a hard failure, which meant the operator could open a project or document and progress through retrieval only to land on a patch-review step that had drifted away from the canonical demo loop.
- Traceable shared-edit approval: `tests/unit/test_commands_catalog.py` is permitted for `codex/feat-commands*` by the explicit allowlist entry in `scripts/scope-check.sh` (`codex/feat-commands*` case, `tests/unit/test_commands_catalog.py) return 0 ;;`).

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the Milestone 3 CLI command contract deterministic by locking the parser-backed CLI contract to the canonical command catalog.
- Risk reason: this touches a public command contract in `src/qual/commands/catalog.py` and one shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Harden `command_cli_contract()` so the canonical-name projection is validated against the catalog instead of being rebuilt from parser lookup output.
2. Add regression coverage proving catalog/parser drift raises a hard failure.
3. Refresh the handoff packet so it names the exact canonical demo-path step protected by this contract and cites the shared-test approval source.
4. Re-run the required gates and record the results.

## Review Basis

- Implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

## Ownership Note

- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Shared-by-approval regression path: `tests/unit/test_commands_catalog.py`
- Approval source: `scripts/scope-check.sh` allowlist entry for branch pattern `codex/feat-commands*`, which explicitly allows `tests/unit/test_commands_catalog.py`
- Integrator-locked edits: `none`
- Scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata only.

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this change removes a concrete blocker in the active CLI-first operator path by keeping `patch-review` deterministic after the operator opens a project/document and advances through retrieval.
- `ROADMAP.md` canonical demo path: the concrete operator step protected is `patch-review` in `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff`, because `command_cli_contract()` now inherits the canonical catalog projection from `_validated_cli_entrypoints_for()` and `_cli_entrypoints_by_name()` in `src/qual/commands/catalog.py`, and the regression coverage imported in `tests/unit/test_commands_catalog.py` proves that patch-review now fails fast on drift instead of silently changing behavior.
- `ROADMAP.md` active lane mapping: `feat-commands` owns CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the active CLI operator surface now rejects parser/catalog drift before it can silently change the patch-review command contract.
- `PRODUCT_VISION.md` near-term product truth: while Textual remains disabled, the CLI is the real operator surface, so hardening the patch-review entrypoint protects the live Milestone 3 workflow path instead of abstract CLI behavior.
