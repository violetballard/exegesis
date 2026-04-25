# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Verified implementation basis SHA: `0777640324e7d3a54dba191135bd2d867c32d399`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: submit the reviewed command-catalog slice only, keeping the handoff limited to deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the approved shared regression coverage in `tests/unit/test_commands_catalog.py`.
- Risk reason: this is a high-risk command-contract handoff because it touches the operator-facing CLI contract and uses an approved shared test file outside the lane-owned path.

### Scope / Plan Alignment

- Canonical demo-path step advanced: Milestone 5 CLI MVP-flow step `patch` in the exit-criteria sequence `vault -> context -> run -> patch -> export`, specifically the operator path that previews a patch and then applies or rejects it from the CLI while the Textual client remains disabled.
- Explicit handoff sentence: this handoff makes the existing CLI fallback for the `patch` step more real by keeping the parser-facing command catalog deterministic and failing fast when parser entrypoint tokens drift from that catalog before an operator reaches patch preview/apply-or-reject.
- MVP focus tie-in: this is CLI-fallback contract hardening in support of the current MVP emphasis on `A2UI` contracts with CLI fallback, not new surface-area expansion.
- Concrete blocker removed: without this guard, parser/catalog drift could silently reorder, add, or drop the operator-facing CLI tokens that invoke the patch preview/apply-or-reject leg, so the current MVP loop could present a stale smoke-check contract while the real CLI path for `patch` no longer matches the catalog.
- Reviewer fix closure:
  1. `command_cli_contract()` validates the full grouped parser-entrypoint projection, not only the deduplicated canonical-name sequence.
  2. `tests/unit/test_commands_catalog.py` exercises token-level parser drift cases where canonical-name order still matches.
  3. This packet explicitly names the canonical demo-path step advanced and why the contract hardening removes a concrete blocker for that step.
- Roadmap alignment: `ROADMAP.md` Milestone 3 `Product Readiness` requires user-facing output contracts to be defined and locked, and `ROADMAP.md` Milestone 5 requires that `CLI can execute the MVP flow (vault -> context -> run -> patch -> export)` against the same engine contracts; this handoff is a narrow contract-hardening change that protects the existing `patch` step without claiming new flow coverage.
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface` and capability 5 `Agent-to-UI protocol (A2UI)` because the same engine-authored command contract must stay reliable for the CLI fallback surface that operators use today.
- Non-claim boundary: this handoff claims only deterministic CLI catalog ordering and fail-fast parser-surface drift detection for the existing command surface; it does not claim parser-entrypoint rewrites, workflow-wrapper additions, diff-preview output work, provider routing changes, storage changes, reachability expansion, or UI-console work.

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

- plan complete: the handoff is narrowed to the reviewed `command_cli_contract()` slice and explicitly mapped to the active Milestone 5 CLI `patch` step
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` passed for the reviewed implementation basis
- before risky/shared file edit: the only non-owned path is the approved shared test file `tests/unit/test_commands_catalog.py`
- ready for handoff: the packet names the exact reviewed files, includes the missing Milestone 5 CLI `patch` mapping, and keeps the approval basis scoped to the catalog slice only

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so deterministic CLI catalog ordering is rebuilt from the grouped parser-entrypoint projection instead of trusting only the deduplicated canonical-name sequence
  - added fail-fast validation in `src/qual/commands/catalog.py` so added, removed, or reordered CLI entrypoint tokens and alias drift raise `ValueError` instead of silently changing the current command surface
  - added focused regression coverage in the approved shared test file `tests/unit/test_commands_catalog.py` for canonical-order alignment plus removed, reordered, and extra alias-token drift rejection on the current parser surface
  - refreshed the handoff packet so the review claim, Milestone 3 and Milestone 5 CLI-fallback mapping, and file list match the reviewed command-catalog slice exactly
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
  - fixer refresh reran the required gates on `2026-04-24` after aligning the handoff packet to the reviewer-requested high-risk fields and the explicit Milestone 5 CLI `patch` mapping; this refresh remains metadata-only and does not change the reviewed implementation scope
  - fixer rerun revalidated implementation tip SHA `491dd5a81631b2138102cf477adf32eccdee3ec8` on `2026-04-24`; the branch tip already contained the required parser-surface contract hardening, token-drift regression coverage, and explicit CLI `patch` mapping before this metadata-only handoff refresh commit
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
  - `ROADMAP.md` Milestone 3 `Product Readiness`: user-facing command/output contracts stay intentional instead of drifting silently
  - `ROADMAP.md` Milestone 5 `A2UI Presentation Layer`: protects the existing CLI-executable `patch` step inside `vault -> context -> run -> patch -> export`; it does not expand that surface
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
  - `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)` via the current CLI fallback surface
- routing/provider impact note:
  - none; this change only hardens local command-catalog validation and focused command-catalog tests
- approved exception note:
  - approved shared-test exception for `tests/unit/test_commands_catalog.py`; no other non-owned implementation paths are part of this handoff
- reviewer-fix satisfaction note:
  - required fix 1 is already satisfied in `src/qual/commands/catalog.py` by validating the full grouped parser-entrypoint projection instead of only deduplicated canonical names
  - required fix 2 is already satisfied in `tests/unit/test_commands_catalog.py` by token-level drift regressions for added, removed, substituted, and reordered parser entrypoints that still preserve canonical-name order
  - required fix 3 is satisfied by the explicit Milestone 3 contract-locking reference, the Milestone 5 CLI `patch` step mapping, the operator-facing blocker statement, and the MVP tie-in stated in this packet; this refresh records a fresh all-gates-green rerun on the current branch tip for re-review
