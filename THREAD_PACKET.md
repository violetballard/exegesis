# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix handoff metadata narrowing`
- Review scope: narrow Milestone 3 CLI-contract hardening in `src/qual/commands/catalog.py` plus focused regression coverage in `tests/unit/test_commands_catalog.py`.
- Canonical MVP flow advanced: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, via `bootstrap`/`project-open` for open, `context-basket` for retrieval staging, and `diff-preview`/`review-patch` for patch preview
- AGENTS.md alignment note: this packet explicitly names the exact roadmap MVP flow advanced by the reviewed slice and ties the claim to the current AGENTS handoff packet and checkpoint requirements.
- Required mapping statement: this `feat-commands` CLI-contract hardening slice strengthens the canonical `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` steps by preserving the operator-facing CLI command catalog contract used by `bootstrap`/`project-open`, `context-basket`, and `diff-preview`/`review-patch` while CLI remains the active first-class surface.
- Demo-path sentence: this change makes the `preview and apply or reject a patch` step more real for the CLI-first MVP loop because the concrete command entrypoints an operator runs now fail fast if parser drift changes the canonical catalog contract.
- Concrete blocker removed: before this slice, parser drift could change the accepted CLI surface without a hard failure, so an operator could attempt the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop through a CLI contract that had silently drifted away from the canonical catalog.
- Traceable shared-edit approval: `tests/unit/test_commands_catalog.py` is permitted for `codex/feat-commands*` by the explicit allowlist entry in `scripts/scope-check.sh` (`codex/feat-commands*` case, `tests/unit/test_commands_catalog.py) return 0 ;;`).

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the manual CLI smoke flow deterministic by locking the parser-backed CLI contract to the canonical command catalog for `project-open -> retrieval -> patch-review -> export-handoff`.
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

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (Short Updates)

- Plan complete: scope stayed pinned to the reviewed implementation slice in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, with no expansion beyond Milestone 3 CLI-contract hardening.
- First green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice.
- Before risky/shared file edit: `tests/unit/test_commands_catalog.py` was confirmed as the approved shared regression path for `codex/feat-commands*` via `scripts/scope-check.sh`, and this fixer records that approval basis before refreshing shared handoff metadata.
- Ready for handoff: this packet now carries the reviewer-requested exact roadmap flow mapping plus explicit approval and checkpoint provenance for the shared regression path.

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
- Approval source: `THREAD_OWNERSHIP.md` marks `tests/unit/test_commands_catalog.py` as shared-by-approval for `codex/feat-commands*`, and `scripts/scope-check.sh` codifies that approval with the branch-specific allowlist entry that explicitly permits the file
- Checkpoint provenance: the high-risk `before risky/shared file edit` checkpoint above records that the shared regression path was verified against the branch allowlist before this fixer refreshed shared handoff metadata
- Integrator-locked edits: `none`
- Scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata only.

## Roadmap and Vision Mapping

- `AGENTS.md` handoff readiness and checkpoint rules: this slice stays within the documented high-risk task budget, records the required shared-file checkpoint, and keeps the claim pinned to one concrete MVP flow instead of a broad lane narrative.
- `ROADMAP.md` Milestone 3 `Real workflow loop`: this narrow `feat-commands` command-catalog hardening slice keeps the manual CLI smoke flow `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stable while Textual remains disabled.
- `ROADMAP.md` exit criterion `CLI can still execute the MVP loop while Textual remains disabled`: this slice helps lock the operator-facing command contract by failing fast when the parser-backed CLI surface drifts from the canonical catalog.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the active CLI surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on for `open project/document -> retrieve relevant material -> preview and apply or reject a patch`.
- `PRODUCT_VISION.md` near-term product truth: this change hardens the current CLI-first operator path without claiming broader surface expansion beyond the existing engine and A2UI contract work.
