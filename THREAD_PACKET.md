# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix final verification rerun refresh`
- Review scope: narrow command-contract hardening in `src/qual/commands/catalog.py`, plus focused regression coverage in `tests/unit/test_commands_catalog.py`, with the guardrail explicitly enforcing full parser-surface projection consistency rather than only canonical-name/order consistency.
- Canonical demo-path step advanced: step 1 of the canonical demo path, `open project/document` via the CLI, by tightening the existing parser/catalog contract for the operator-facing command surface that starts `open project/document -> retrieve relevant material -> preview and apply or reject a patch` while Textual remains disabled rather than expanding loop reachability
- Canonical MVP flow context: `open project/document -> retrieve relevant material -> preview and apply or reject a patch` remains the same manual CLI smoke flow, and this slice only hardens the parser-backed CLI command surface that starts and therefore gates that path so the CLI can still execute the MVP loop while Textual remains disabled
- Causal link: the CLI-first MVP loop cannot begin unless `open project/document` still resolves through the canonical command surface, so making parser/catalog drift fail fast hardens that exact first step and keeps the downstream retrieval and patch-review steps reachable through the same deterministic CLI path.
- AGENTS.md alignment note: this packet explicitly names the exact canonical demo-path step protected by the reviewed slice and ties the claim to the current AGENTS handoff packet and checkpoint requirements.
- Required mapping statement: this `feat-commands` slice is not claiming new workflow reachability; it is migration-safe compatibility hardening for the existing command catalog because `command_cli_contract()` now fails fast when parser/catalog drift would otherwise silently change the operator-facing CLI contract through alias substitution, missing canonical entrypoints, reordered grouped entrypoints, or extra parser-only aliases on the existing `open project/document` entry surface that starts the `open project/document -> retrieve relevant material -> preview and apply or reject a patch` loop, preserving the CLI compatibility required while Textual remains disabled and the Milestone 3 exit criterion that `CLI can still execute the MVP loop while Textual remains disabled`.
- Demo-path sentence: this change makes the existing CLI-first MVP path safer to rely on because the concrete parser-backed command entrypoints an operator already uses to open project or document state can no longer silently drift away from the canonical catalog through alias-level or ordering changes, which keeps the downstream `retrieve relevant material` and `preview and apply or reject a patch` steps reachable through the same deterministic CLI loop while Textual remains disabled.
- Concrete blocker removed: before this slice, parser drift could change the accepted CLI surface without a hard failure, so an operator could begin the manual MVP flow through an `open project/document` surface that no longer matched the canonical command catalog.
- Review basis scope: keep implementation and approval claims pinned to reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and its two implementation files only: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Final fixer note: this packet refresh exists only to align the handoff scope language with the already-landed full parser-surface guardrail and to record the green rerun of the required gates from this fixer pass; the reviewed implementation commit remains `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Final verification note: this metadata-only fixer pass on `2026-04-24` revalidated the corrected handoff packet and reran the full required gate set from the current branch tip without widening implementation scope.
- Gate rerun confirmation: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed again from the current branch tip in this metadata-only fixer handoff.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the existing manual CLI `open project/document` entry surface deterministic by locking the parser-backed CLI contract to the canonical command catalog without adding new commands or new engine behavior.
- Risk reason: this touches a public command contract in `src/qual/commands/catalog.py` and one focused regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Harden `command_cli_contract()` so the full grouped parser-surface projection is validated against the canonical catalog instead of trusting derived canonical-name order alone.
2. Add regression coverage proving live parser/catalog drift raises a hard failure, including alias-level drift that preserves canonical command names.
3. Refresh the handoff packet so it names the exact canonical demo-path step protected by this contract, explains why the work is migration-safe compatibility hardening rather than second-order cleanup, and makes the alias-level parser-surface-drift scope explicit even when canonical names stay stable.
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

- Plan complete: scope stayed pinned to the reviewed implementation slice in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, with no expansion beyond deterministic CLI-contract hardening for the existing command surface.
- First green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice.
- Before risky/shared file edit: scope was rechecked against reviewed commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` so the refreshed handoff only describes `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- Ready for handoff: this packet now carries the reviewer-requested exact demo-path mapping and explicit migration-safe compatibility justification without implying any broader lane scope.

## Review Basis

- Implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`

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
- Shared-test approval owner: the integrator-managed branch policy for `codex/feat-commands`.
- Shared-test approved by: the integrator/release ownership gate for `codex/feat-commands`.
- Shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`, which is the auditable local approval source for this handoff's only non-owned implementation path.
- Shared-test approval scope: the exception is limited to focused regression coverage in `tests/unit/test_commands_catalog.py`; no other shared or integrator-locked implementation paths are claimed in this slice.
- Integrator-locked edits: `none`
- Scope note: the implementation under review is limited to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata only.
- Scope clarification: this is command-contract hardening only; it does not add new commands, new engine behavior, new persistence or auditability mechanisms, or a new workflow capability.

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 3 lane mapping `feat-commands: CLI compatibility and migration-safe entrypoints`: this slice hardens the existing command catalog contract without adding new CLI workflow reachability.
- `ROADMAP.md` Milestone 3 exit criterion `CLI can still execute the MVP loop while Textual remains disabled`: deterministic parser/catalog alignment hardens the exact `open project/document` entry step that gates the rest of the CLI-first loop.
- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the active CLI surface now rejects parser/catalog drift before it can silently change the deterministic command contract the operator relies on while `Exegesis Console` remains a later client on top of the same engine contracts.
