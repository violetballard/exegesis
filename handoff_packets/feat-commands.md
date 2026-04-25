# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Verified implementation basis SHA: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Submitted tip note: any newer tip created by this handoff refresh is metadata-only packet bookkeeping on top of that verified implementation basis
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: submit the reviewed command-catalog slice only, keeping the handoff limited to deterministic `command_cli_contract()` behavior in `src/qual/commands/catalog.py` plus the repo-policy-allowlisted shared regression coverage in `tests/unit/test_commands_catalog.py`.
- Risk reason: this is a high-risk command-contract handoff because it touches the operator-facing CLI contract and uses a repo-policy-allowlisted shared test file outside the lane-owned path.
- Final validated packet tip before this metadata-only refresh: `621fcc4204a4c0fba0918cc9d9c563dab6638585`

### Scope / Plan Alignment

- Canonical demo-path steps advanced: stable CLI command reachability for `project-open`, `retrieval`, `patch-review`, and `export-handoff` while Textual remains disabled.
- Explicit handoff sentence: This work makes the current engine-first CLI fallback path more real by keeping the catalog-driven parser contract deterministic for the canonical `project-open`, `retrieval`, `patch-review`, and `export-handoff` command surfaces, so parser/catalog drift fails fast instead of silently mutating those operator entrypoints.
- MVP focus tie-in: this is Milestone 3 CLI-compatibility hardening for the existing engine-first CLI fallback path, not new workflow capability or surface-area expansion.
- Concrete blocker removed: without this guard, parser/catalog drift could silently reorder, add, or drop CLI tokens on the existing engine-first fallback path, which would make `project-open`, `retrieval`, `patch-review`, or `export-handoff` command reachability drift away from the real engine contract.
- Reviewer fix closure:
  1. `command_cli_contract()` remains aligned to the canonical command order and raises `ValueError` if the parser surface drifts from the catalog.
  2. `tests/unit/test_commands_catalog.py` covers canonical-order alignment and parser/catalog drift rejection for the reviewed command-catalog slice.
  3. This packet explicitly maps the change to the current engine-first CLI fallback steps above and names the concrete CLI-contract blocker it removes.
- Verified re-review tip before this packet refresh: `621fcc4204a4c0fba0918cc9d9c563dab6638585`
- Final validated handoff tip before this packet refresh: `621fcc4204a4c0fba0918cc9d9c563dab6638585`
- Roadmap alignment: `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional` only; this handoff is a narrow canonical engine contract and CLI-compatibility hardening change for the existing engine-first CLI fallback path while Textual remains disabled and without claiming broader workflow coverage.
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface` only; this change hardens the current parser/catalog contract that the CLI fallback depends on for `project-open`, `retrieval`, `patch-review`, and `export-handoff` and does not claim audit-state or broader workflow progress.
- Non-claim boundary: this handoff claims only deterministic CLI catalog ordering and fail-fast parser-surface drift detection for the existing CLI fallback command surfaces; it does not claim parser-entrypoint rewrites, workflow-wrapper additions, diff-preview output work, provider routing changes, storage changes, reachability expansion, or UI-console work.

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

- plan complete: the handoff is narrowed to the reviewed `command_cli_contract()` slice and explicitly mapped to Milestone 3 CLI-compatibility hardening for the existing `project-open`, `retrieval`, `patch-review`, and `export-handoff` fallback surfaces
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` passed for the reviewed implementation basis and are rerun on the current branch for this packet refresh
- before risky/shared file edit: the only non-owned path is the repo-policy-allowlisted shared test file `tests/unit/test_commands_catalog.py`
- ready for handoff: the packet names the exact reviewed files, includes the canonical demo-path mapping, and records the metadata-only refresh scope for the reviewed implementation basis

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog
  - preserved canonical command ordering in the CLI contract by reusing the canonical names tuple instead of rebuilding a divergent list
  - added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection
  - refreshed the handoff packet so the review claim, canonical CLI fallback step mapping, and file list match the reviewed command-catalog slice exactly
- tasks completed (numbered):
  1. Hardened `command_cli_contract()` to verify canonical-name consistency against `command_names()` and fail fast on parser drift.
  2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly.
  3. Added regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
  4. Regenerated the handoff packet so the branch metadata stays scoped to the command-catalog slice and uses the current roadmap and vision labels.
- files changed:
  - reviewed implementation: `src/qual/commands/catalog.py`
  - reviewed implementation: `tests/unit/test_commands_catalog.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - reviewed implementation basis SHA `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  - packet refresh commit preserved as metadata-only scope on tip `621fcc4204a4c0fba0918cc9d9c563dab6638585`
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: future parser token changes must keep the catalog aligned with the canonical CLI fallback command surfaces, or the fail-fast contract will reject `project-open`, `retrieval`, `patch-review`, or `export-handoff` reachability
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional`: preserve deterministic CLI compatibility for the existing engine-first fallback command surfaces while Textual remains disabled
- vision capability affected:
  - primary: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`
- routing/provider impact note:
  - none; this change only hardens local command-catalog validation and focused command-catalog tests
- approved exception note:
  - approved shared-test exception for `tests/unit/test_commands_catalog.py`
  - no other non-owned implementation paths are part of this handoff
- reviewer-fix satisfaction note:
  - required fix 1 is satisfied by naming the exact engine-first CLI fallback command surfaces this contract hardening protects: `project-open`, `retrieval`, `patch-review`, and `export-handoff`
  - required fix 2 is satisfied by narrowing the roadmap and vision mapping to Milestone 3 CLI compatibility and `Operator-first control surface` only, without claiming broader progress
  - required fix 3 is satisfied by preserving the reviewed implementation basis `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` and keeping `621fcc4204a4c0fba0918cc9d9c563dab6638585` explicit as a metadata-only packet refresh
