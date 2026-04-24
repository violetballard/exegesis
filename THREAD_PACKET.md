# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Verified implementation basis SHA: `0777640324e7d3a54dba191135bd2d867c32d399`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: submit the reviewed command-catalog slice only, keeping the handoff limited to deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the approved shared regression coverage in `tests/unit/test_commands_catalog.py`.
- Risk reason: this is a high-risk command-contract handoff because it touches the operator-facing CLI contract and uses an approved shared test file outside the lane-owned path.

### Scope / Plan Alignment

- Canonical demo-path step advanced: `preview and apply or reject a patch` in the engine-first demo path `open document -> retrieve relevant material -> gather context -> plan or revise -> preview and apply or reject a patch -> save and continue`.
- Explicit handoff sentence: this handoff strengthens the active CLI fallback for the `preview and apply or reject a patch` step by making the command catalog contract deterministic, canonical-order aligned, and fail-fast when the parser surface drifts while Textual remains disabled.
- Roadmap alignment: `ROADMAP.md` Milestone 2 remaining parser-edge coverage and `ROADMAP.md` Milestone 5 CLI fallback for the MVP loop, specifically the patch-review/apply-or-reject step that must stay stable while Textual remains disabled.
- Vision alignment: `PRODUCT_VISION.md` capability 3 `Canonical engine contract` and capability 6 `Auditable state and workflow`.
- Non-claim boundary: this handoff does not claim parser-entrypoint rewrites, workflow-wrapper additions, diff-preview output work, provider routing changes, storage changes, or UI-console work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep `command_cli_contract()` aligned to the canonical command order by reusing the canonical parser projection directly.
2. Reject full parser-surface drift with a fail-fast validation when added, removed, or reordered CLI entrypoint tokens diverge from the catalog.
3. Add focused regression coverage in the approved shared test file for canonical-order alignment plus alias-level parser-surface drift rejection.
4. Refresh the handoff packet so review scope, roadmap mapping, and file list match the reviewed implementation slice exactly.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: the handoff is narrowed to the reviewed `command_cli_contract()` slice and explicitly mapped to the active CLI demo-path step
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` passed for the reviewed implementation basis
- before risky/shared file edit: the only non-owned path is the approved shared test file `tests/unit/test_commands_catalog.py`
- ready for handoff: the packet names the exact reviewed files, includes the missing demo-path mapping, and keeps the approval basis scoped to the catalog slice only

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it rebuilds and validates the grouped parser-entrypoint projection instead of trusting only the deduplicated canonical-name sequence
  - added fail-fast validation in `src/qual/commands/catalog.py` so added, removed, or reordered CLI entrypoint tokens and alias drift raise `ValueError` instead of silently changing the CLI contract
  - added focused regression coverage in the approved shared test file `tests/unit/test_commands_catalog.py` for canonical-order alignment plus removed, reordered, and extra alias-token drift rejection
  - refreshed the handoff packet so the review claim, roadmap mapping, and file list match the reviewed command-catalog slice exactly
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Hardened `command_cli_contract()` to validate the full grouped parser-entrypoint projection against the catalog.
  2. Preserved canonical command ordering in the returned CLI contract while rejecting added, removed, or reordered parser tokens that would otherwise preserve canonical-name order.
  3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and alias-level parser-surface drift rejection.
- files changed:
  - reviewed implementation: `src/qual/commands/catalog.py`
  - reviewed implementation: `tests/unit/test_commands_catalog.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - reviewed implementation basis SHA `0777640324e7d3a54dba191135bd2d867c32d399` on `2026-04-24`
  - fixer refresh reran the required gates on `2026-04-24` after aligning the handoff packet to the reviewer-requested high-risk fields and canonical demo-path mapping; this refresh remains metadata-only and does not change the reviewed implementation scope
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: future parser token or alias changes must keep the grouped parser-entrypoint projection aligned with the catalog, or the fail-fast contract will reject the surface
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 2 Remaining: add missing targeted parser-edge cases identified during reviews
  - `ROADMAP.md` Milestone 5 Exit Criteria: keep the MVP CLI fallback stable enough to execute the patch-review leg of the workflow loop against the same engine contract while Textual remains disabled
- vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
  - `PRODUCT_VISION.md` capability 6 `Auditable state and workflow`
- routing/provider impact note:
  - none; this change only hardens local command-catalog validation and focused command-catalog tests
- approved exception note:
  - approved shared-test exception for `tests/unit/test_commands_catalog.py`; no other non-owned implementation paths are part of this handoff
- reviewer-fix satisfaction note:
  - this packet adds the missing canonical demo-path mapping, includes the high-risk `Risk reason`, and keeps the approval basis scoped to `src/qual/commands/catalog.py` plus the approved shared test file `tests/unit/test_commands_catalog.py`
