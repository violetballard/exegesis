# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Verified implementation basis SHA: `cafe42ff5e9c5921610b2765a64fb6802a1ee5f5`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: submit the reviewed command-catalog slice only, keeping the handoff limited to deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the repo-policy-allowlisted shared regression coverage in `tests/unit/test_commands_catalog.py`.
- Risk reason: this is a high-risk command-contract handoff because it touches the operator-facing CLI contract and uses a repo-policy-allowlisted shared test file outside the lane-owned path.
- Previous validated packet tip before this metadata-only refresh: `24a930fb600745b1cecc27915f97617e333f93df`

### Scope / Plan Alignment

- Canonical demo-path step advanced: the CLI/operator-contract portion of `open project/document`, keeping the MVP loop executable from the CLI while Textual remains disabled.
- Explicit handoff sentence: This work makes the CLI/operator-contract portion of `open project/document` more real by hardening the catalog-driven parser contract, so parser/catalog drift fails fast instead of silently mutating the operator entrypoint that the engine-first fallback path depends on.
- MVP focus tie-in: this is Milestone 3 CLI-compatibility hardening for the existing engine-first CLI fallback path, not new workflow capability or surface-area expansion.
- Concrete blocker removed: without this guard, parser/catalog drift could silently reorder, add, or drop CLI tokens on the existing engine-first fallback path before the `open project/document` operator contract reaches the real engine path.
- Reviewer fix closure:
  1. `command_cli_contract()` remains aligned to the canonical command order and raises `ValueError` if the parser surface drifts from the catalog.
  2. `tests/unit/test_commands_catalog.py` covers canonical-order alignment and parser/catalog drift rejection for the reviewed command-catalog slice.
  3. This packet explicitly maps the change to the CLI/operator-contract portion of `open project/document` and names the concrete CLI-contract blocker it removes.
- Previous verified re-review tip before this packet refresh: `24a930fb600745b1cecc27915f97617e333f93df`
- Previous validated handoff tip before this packet refresh: `24a930fb600745b1cecc27915f97617e333f93df`
- Current verifier refresh base SHA: `24a930fb600745b1cecc27915f97617e333f93df`
- Latest gate rerun date: `2026-04-24`
- Current fixer refresh purpose: rerun the full required gate set on the current verified tip after confirming the reviewer fixes remain satisfied, then refresh the handoff metadata on top of the verified command-catalog slice.
- Roadmap alignment: `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional` only; this handoff is a narrow canonical engine contract and CLI-compatibility hardening change for the existing engine-first CLI fallback path while Textual remains disabled and without claiming broader workflow coverage beyond the `open project/document` operator contract.
- Vision alignment: `PRODUCT_VISION.md` capability 3 `Canonical engine contract` only; this change hardens the current parser/catalog contract that the CLI fallback depends on for the `open project/document` operator contract and does not claim audit-state, workflow-state, or broader workflow progress.
- Non-claim boundary: this handoff claims only deterministic CLI catalog ordering and fail-fast parser-surface drift detection for the existing CLI fallback path; it does not claim parser-entrypoint rewrites, workflow-wrapper additions, diff-preview output work, provider routing changes, storage changes, reachability expansion, or UI-console work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep `command_cli_contract()` aligned to the canonical command order by reusing the canonical names tuple directly.
2. Reject parser/catalog drift with a fail-fast validation when the CLI parser surface diverges from the catalog.
3. Add focused regression coverage in the allowlisted shared test file for canonical-order alignment and drift rejection.
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

- plan complete: the handoff is narrowed to the reviewed `command_cli_contract()` slice and explicitly mapped to Milestone 3 CLI-compatibility hardening for the `open project/document` operator contract
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` passed for the reviewed implementation basis and are rerun on the current branch for this packet refresh
- before risky/shared file edit: the only non-owned path is the repo-policy-allowlisted shared test file `tests/unit/test_commands_catalog.py`
- ready for handoff: the packet names the exact reviewed files, includes the single-step canonical demo-path mapping, and records the latest full-gate verification pass for the reviewed implementation basis

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the full parser entrypoint projection and lookup table against the catalog and raises `ValueError` if alias-only or token-level parser-surface drift appears
  - preserved canonical command ordering in the CLI contract by reusing the canonical names tuple instead of rebuilding a divergent list
  - added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment plus alias-only parser-surface drift rejection
  - refreshed the handoff packet so the review claim, single-step canonical demo-path mapping, and file list match the reviewed command-catalog slice exactly
- tasks completed (numbered):
  1. Hardened `command_cli_contract()` to verify the parser entrypoint projection and lookup table against the catalog and fail fast on parser drift.
  2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
  3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and alias-only parser-surface drift rejection.
  4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and uses the current roadmap and vision labels.
- files changed:
  - reviewed implementation: `src/qual/commands/catalog.py`
  - reviewed implementation: `tests/unit/test_commands_catalog.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - older reviewer packet implementation basis SHA `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  - current verified branch tip before this metadata-only refresh: `24a930fb600745b1cecc27915f97617e333f93df`
  - verifier rerun base SHA before this metadata-only refresh: `24a930fb600745b1cecc27915f97617e333f93df`
  - latest gate rerun date: `2026-04-24`
  - `python -m unittest tests.unit.test_commands_catalog` -> passed
  - current fixer reran the full required gate set on the verified branch tip before this metadata-only refresh
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: future parser token changes must keep the catalog aligned with the `open project/document` operator contract, or the fail-fast contract will reject the engine-first fallback path before that operator entrypoint reaches the real engine path
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional`: preserve deterministic CLI compatibility for the `open project/document` operator contract while Textual remains disabled
- vision capability affected:
  - primary: `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
- routing/provider impact note:
  - none; this change only hardens local command-catalog validation and focused command-catalog tests
- approved exception note:
  - approved shared-test exception for `tests/unit/test_commands_catalog.py`
  - no other non-owned implementation paths are part of this handoff
- reviewer-fix satisfaction note:
  - required fix 1 is satisfied by naming the `open project/document` operator contract in roadmap terms and explaining how parser/catalog drift would otherwise mutate that operator entrypoint before it reaches the engine path
  - required fix 2 is satisfied by keeping the roadmap and vision mapping tight to Milestone 3 CLI compatibility and `Canonical engine contract` only, without claiming broader progress
  - required fix 3 is satisfied by the live parser-surface drift regressions now present in `tests/unit/test_commands_catalog.py`, including cases where canonical names stay stable but accepted entrypoints drift
  - required fix 4 is satisfied by this refreshed handoff packet, which keeps the scope and Milestone 3 mapping tied to `feat-commands` CLI compatibility while Textual remains disabled
