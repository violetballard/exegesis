# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the handoff aligned to the reviewed command-catalog slice only by documenting explicit CLI parser-surface validation in `src/qual/commands/catalog.py` with focused token-level drift coverage in `tests/unit/test_commands_catalog.py`.
- Risk reason: this is a high-risk command-contract handoff because it touches the operator-facing CLI catalog contract and uses one approved shared test path.

### Scope / Plan Alignment

- Canonical demo-path step advanced: `preview and apply or reject a patch`.
- Explicit handoff sentence: this handoff advances the canonical demo-path step `preview and apply or reject a patch` by keeping the operator-facing CLI parser surface deterministic and making alias or token drift fail fast before the operator relies on that contract.
- Roadmap alignment: `ROADMAP.md` Milestone 3 CLI compatibility while Textual remains disabled, specifically the migration-safe `feat-commands` entrypoint contract.
- Vision alignment: `PRODUCT_VISION.md` capability 3 `Canonical engine contract` only.
- Non-claim boundary: this handoff does not claim persistence progress, audit/workflow tracing progress, new workflow branches, provider changes, or new engine behavior.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep `src/qual/commands/catalog.py` authoritative for the explicit CLI parser surface and canonical command ordering.
2. Make `command_cli_contract()` reject alias-only or token-level parser drift, not just canonical-name drift.
3. Cover extra-alias and missing-alias parser-surface drift in `tests/unit/test_commands_catalog.py`.
4. Re-run the required gates and record the outcomes for this narrow handoff slice.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: scope stayed pinned to `src/qual/commands/catalog.py`, the approved shared test exception in `tests/unit/test_commands_catalog.py`, and the required handoff metadata refresh
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` passed for this handoff slice
- before risky/shared file edit: no additional shared runtime edits were required in this fixer pass
- ready for handoff: the packet now states one exact canonical demo-path step, documents the explicit parser-surface guard, and keeps the roadmap/vision mapping limited to the reviewed command-catalog slice

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the full explicit CLI parser-entrypoint projection, tokens, and lookup table against the command catalog and raises `ValueError` on alias-only or token-level drift
  - preserved canonical contract ordering while deriving the exported CLI contract from the validated parser surface instead of a weaker canonical-name-only projection
  - added focused regression coverage in `tests/unit/test_commands_catalog.py` for extra-alias and missing-alias parser-surface drift, including cases where canonical command order would otherwise stay unchanged
  - reissued the handoff packet so it stays limited to the reviewed implementation scope and plan mapping
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Hardened `command_cli_contract()` to validate the full parser-entrypoint projection and fail fast on alias-only or token-level drift.
  2. Preserved canonical command ordering in the CLI contract while deriving it from the validated parser surface.
  3. Added regression coverage in `tests/unit/test_commands_catalog.py` for extra-alias and missing-alias parser-surface drift.
- files changed:
  - reviewed implementation: `src/qual/commands/catalog.py`
  - reviewed implementation: `tests/unit/test_commands_catalog.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: future command-surface edits still need to preserve the explicit parser-entrypoint projection and fail-fast alias/token drift detection so the CLI contract remains deterministic
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 CLI compatibility while Textual remains disabled
  - `feat-commands` migration-safe entrypoints for the engine-first MVP loop
- vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- approved exception note:
  - `tests/unit/test_commands_catalog.py` is the approved shared-test exception for this handoff
- reviewer-fix satisfaction note:
  - this packet keeps the reviewed scope to `src/qual/commands/catalog.py` plus `tests/unit/test_commands_catalog.py`, names the single canonical demo-path step, documents the explicit parser-surface guard, and records token-level alias drift coverage without expanding into workflow/audit claims
