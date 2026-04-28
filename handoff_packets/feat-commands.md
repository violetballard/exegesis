# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: metadata-only reviewer-fix finalization
- Packet traceability note: review the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this packet update only tightens handoff metadata and does not expand review beyond the command-catalog slice.
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser surface drifts from the catalog.
- Risk reason: command-contract work affects the operator-facing CLI compatibility surface while Textual lanes remain disabled.

### Plan Alignment

- Roadmap alignment: Milestone 3 CLI compatibility and migration-safe entrypoints for the engine-first workflow loop.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface; command-surface drift must be explicit and traceable.
- Architecture alignment: keeps command handlers thin and contract-oriented inside `src/qual/commands/**`; no provider routing, persistence, Textual, A2UI schema, or engine business-logic changes are claimed.
- MVP blocker statement: parser/catalog drift validation is needed now because the CLI is still the active way to continue through the engine-side MVP loop. If parser tokens silently diverge from the catalog, operators can lose deterministic access to follow-on commands before Textual or other UI lanes are enabled. This is a compatibility blocker for continuing the loop, not general CLI polish.

### Canonical Demo-Path Mapping

- Task 1 advances `continue working`: validating canonical-name consistency keeps follow-on command dispatch deterministic after an operator starts the MVP loop.
- Task 2 advances `continue working`: returning the validated canonical tuple prevents a second, divergent command order from changing later operator turns.
- Task 3 advances `continue working`: focused regression coverage fails fast if parser/catalog drift would break the stable command surface used between engine-side steps.
- Task 4 advances `continue working`: refreshed metadata pins the exact command-catalog review basis so reviewer/integrator handoff can proceed without scope ambiguity.
- Final demo-path statement: this handoff most directly makes `continue working without losing context` more real by ensuring the CLI command contract remains deterministic between engine-side workflow steps.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`
- Budget status for reviewed implementation slice: within high-risk task and file-count limits.

### Tasks Completed

1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift. Canonical demo-path step: `continue working`.
2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly. Canonical demo-path step: `continue working`.
3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection. Canonical demo-path step: `continue working`.
4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and uses the current roadmap, vision, ownership, and canonical demo-path labels. Canonical demo-path step: `continue working`.

### Files Changed

#### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

#### Metadata-only handoff files

- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

### Shared / Integrator-Locked Accounting

- Shared-by-approval test edit: yes, `tests/unit/test_commands_catalog.py`, covered by the approved shared-test exception for this handoff.
- Integrator-locked edits in the reviewed implementation slice: no.
- Shared/integrator-locked runtime edits in the reviewed implementation slice: no.
- Ownership detail: runtime implementation is limited to owned path `src/qual/commands/catalog.py`; the only non-owned reviewed implementation path is the approved shared-by-approval unit test.

### Commands Run + Outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

### Risks / Blockers

- Risk: high. This is command-contract work and must remain pinned to the narrow reviewed command-catalog slice.
- Blockers: none.

### Required Fix Satisfaction

1. Required fix 1 is satisfied by naming the canonical demo-path step on every completed task.
2. Required fix 2 is satisfied by the MVP blocker statement explaining why parser/catalog drift validation is needed while the CLI is the active engine-side operator surface.
3. Required fix 3 is satisfied by distinguishing the approved shared-by-approval test edit from integrator-locked edits and stating that no integrator-locked files changed in the reviewed implementation slice.
4. Required fix 4 is satisfied by keeping the reviewed implementation basis pinned to `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and limiting the packet to the command-catalog slice.
