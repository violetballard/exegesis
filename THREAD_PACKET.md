# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix handoff narrowing`
- Review scope: narrow Milestone 3 CLI-contract hardening in `src/qual/commands/catalog.py`, plus focused regression coverage in `tests/unit/test_commands_catalog.py`.
- Canonical demo-path step advanced: the Milestone 3 CLI-first control surface for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch`
- Canonical MVP flow advanced: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` for the manual CLI smoke flow, via `bootstrap`/`project-open` for open, `context-basket` for retrieval staging, and `diff-preview`/`review-patch` for patch preview
- AGENTS.md alignment note: this packet explicitly names the exact roadmap MVP flow advanced by the reviewed slice and ties the claim to the current AGENTS handoff packet and checkpoint requirements.
- Required mapping statement: this `feat-commands` slice is not internal contract cleanup for its own sake; it protects the Milestone 3 CLI-first operator path by making `command_cli_contract()` fail fast when parser/catalog drift would otherwise silently break the command surface used for `open project/document`, `retrieve relevant material`, and `preview and apply or reject a patch` while Textual remains disabled.
- Demo-path sentence: this change makes the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop more real for the CLI-first MVP path because the concrete parser-backed command entrypoints an operator runs now fail fast if parser drift changes the canonical catalog contract.
- Concrete blocker removed: before this slice, parser drift could change the accepted CLI surface without a hard failure, so an operator could attempt the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop through a CLI contract that had silently drifted away from the canonical catalog.
- Review basis scope: keep implementation and approval claims pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and its two implementation files only: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the manual CLI smoke flow deterministic by locking the parser-backed CLI contract to the canonical command catalog for `project-open -> retrieval -> patch-review`.
- Risk reason: this touches a public command contract in `src/qual/commands/catalog.py` and one focused regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Harden `command_cli_contract()` so the canonical-name projection is validated against the canonical catalog order instead of trusting derived lookup order.
2. Add regression coverage proving live parser/catalog drift raises a hard failure.
3. Refresh the handoff packet so it names the exact canonical demo-path step protected by this contract and explains why the work is in-plan Milestone 3 CLI-first hardening rather than second-order cleanup.
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
- Before risky/shared file edit: scope was rechecked against reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` so the refreshed handoff only describes `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Ready for handoff: this packet now carries the reviewer-requested exact roadmap flow mapping and explicit Milestone 3 CLI-first justification without implying any broader lane scope.

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
- Focused regression path: `tests/unit/test_commands_catalog.py`
- Approval/source note: the reviewed implementation claim is pinned to commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and only the two implementation files it touched.
- Integrator-locked edits: `none`
- Scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata only.
- Scope clarification: this is command-contract hardening only; it does not add new command behavior, new persistence or auditability mechanisms, or a new workflow capability.

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this narrow `feat-commands` command-catalog hardening slice keeps the manual CLI smoke flow `open project/document -> retrieve relevant material -> preview and apply or reject a patch` stable while Textual remains disabled.
- `ROADMAP.md` Milestone 3 exit criterion `CLI can still execute the MVP loop while Textual remains disabled`: this is why the work is in-plan rather than second-order cleanup, because it prevents silent parser/catalog drift from breaking the operator-facing CLI control surface the MVP loop depends on.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the active CLI surface now rejects parser/catalog drift before it can silently change the command contract the operator relies on for `open project/document -> retrieve relevant material -> preview and apply or reject a patch`.
