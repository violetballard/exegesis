# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Verified implementation basis SHA: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: submit the reviewed command-catalog slice only, keeping the handoff limited to deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the approved shared regression coverage in `tests/unit/test_commands_catalog.py`.
- Risk reason: this is a high-risk command-contract handoff because it touches the operator-facing CLI contract and uses an approved shared test file outside the lane-owned path.

### Scope / Plan Alignment

- Canonical demo-path step advanced: `preview and apply or reject a patch` in the engine-first demo path `open document -> retrieve relevant material -> gather context -> plan or revise -> preview and apply or reject a patch -> save and continue`.
- Explicit handoff sentence: this handoff strengthens the active CLI fallback for the `preview and apply or reject a patch` step by making the command catalog contract deterministic, canonical-order aligned, and fail-fast when the parser surface drifts while Textual remains disabled.
- Roadmap alignment: `ROADMAP.md` Milestone 3 CLI compatibility for the real workflow loop, specifically the deterministic CLI fallback surface that remains stable while the package/layout migration lands.
- Vision alignment: `PRODUCT_VISION.md` capability 3 `Canonical engine contract` and capability 6 `Auditable state and workflow`.
- Non-claim boundary: this handoff does not claim parser-entrypoint rewrites, workflow-wrapper additions, diff-preview output work, provider routing changes, storage changes, or UI-console work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep `command_cli_contract()` aligned to the canonical command order by reusing `command_names()` directly.
2. Reject parser/catalog drift with a fail-fast validation when the CLI contract surface diverges from the catalog.
3. Add focused regression coverage in the approved shared test file for canonical-order alignment and drift rejection.
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
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it reuses the canonical `command_names()` ordering instead of rebuilding a divergent list
  - added fail-fast validation in `src/qual/commands/catalog.py` so parser/catalog canonical-name drift raises `ValueError` instead of silently changing the CLI contract
  - added focused regression coverage in the approved shared test file `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection
  - refreshed the handoff packet so the review claim, roadmap mapping, and file list match the reviewed command-catalog slice exactly
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Hardened `command_cli_contract()` to validate canonical-name consistency against `command_names()`.
  2. Preserved canonical command ordering in the returned CLI contract by using the canonical names tuple directly.
  3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
  4. Refreshed the packet metadata to satisfy the reviewer’s required fixes without widening the implementation claim.
- files changed:
  - reviewed implementation: `src/qual/commands/catalog.py`
  - reviewed implementation: `tests/unit/test_commands_catalog.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - reviewed implementation basis SHA `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` from the reviewer packet on `2026-04-24`
  - rerun on current tip `0ba2eb03fca6dfc377208d7757c9a71221b3652e` on `2026-04-24`; this tip is metadata-only and does not change the reviewed implementation scope
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: future parser token or alias changes that affect canonical-name projection must keep `command_names()` and `command_cli_lookup_table()` aligned, or the fail-fast contract will reject the surface
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3: preserve CLI compatibility while the package/layout migration lands
  - `ROADMAP.md` lane mapping for `feat-commands`: CLI compatibility and migration-safe entrypoints
- vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
  - `PRODUCT_VISION.md` capability 6 `Auditable state and workflow`
- routing/provider impact note:
  - none; this change only hardens local command-catalog validation and focused command-catalog tests
- approved exception note:
  - approved shared-test exception for `tests/unit/test_commands_catalog.py`; no other non-owned implementation paths are part of this handoff
- reviewer-fix satisfaction note:
  - this packet adds the missing canonical demo-path mapping, includes the high-risk `Risk reason`, and keeps the approval basis scoped to `src/qual/commands/catalog.py` plus the approved shared test file `tests/unit/test_commands_catalog.py`
