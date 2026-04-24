# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix handoff metadata refresh`
- Review scope: command-catalog Milestone 3 CLI compatibility slice that hardens `command_cli_contract()` against parser-surface drift and keeps the returned contract in canonical command order
- Canonical demo-path step advanced: `continue working without losing context` in the CLI-first engine loop
- AGENTS.md alignment note: this packet explicitly names the single canonical demo-path step advanced by the reviewed slice, rather than only citing Milestone 3 or broad lane ownership.
- Required mapping statement: this Milestone 3 CLI-contract hardening slice directly strengthens `continue working without losing context` by keeping the active CLI command contract deterministic while Textual remains disabled.
- Concrete blocker removed: before this slice, parser drift could change the accepted CLI surface without a hard failure, which meant the operator could keep working through the engine-first loop against a contract that had silently drifted away from the canonical catalog.
- Traceable shared-edit approval: `tests/unit/test_commands_catalog.py` is permitted for `codex/feat-commands*` by the explicit allowlist entry in `scripts/scope-check.sh` (`codex/feat-commands*` case, `tests/unit/test_commands_catalog.py) return 0 ;;`).

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the active CLI command contract for the Milestone 3 operator loop deterministic by locking the parser-backed CLI contract to the canonical command catalog.
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

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice removes a concrete blocker in the current CLI-first operator path by keeping the command surface deterministic at the `continue working without losing context` step.
- `ROADMAP.md` canonical demo path: the concrete operator step strengthened is `continue working without losing context`, because this CLI-contract hardening slice keeps that step's command contract deterministic while Textual remains disabled.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the active CLI operator surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on at the `continue working without losing context` step.
- `PRODUCT_VISION.md` near-term product truth: while Textual remains disabled, the CLI is the real operator surface, so this change hardens the live operator contract for one current MVP step rather than claiming broader command reachability.
