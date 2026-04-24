# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: tighten the reviewed slice to catalog/parser determinism only by proving the existing CLI contract in `src/qual/commands/catalog.py` fails fast when canonical command ordering or parser-surface tokens drift at `src/qual/cli.py::parse_args()` and `src/main.py::_dispatch()`, including alias-level drift such as dropping `diff` or adding `context`, without adding new engine behavior.
- Risk reason: this is a high-risk command-contract handoff because it relies on the public command contract in `src/qual/commands/catalog.py` and the approved shared regression path `tests/unit/test_commands_catalog.py`, and drift at operator-facing CLI entrypoints would directly weaken the current manual CLI smoke flow.

### Scope / Plan Alignment

- Canonical demo-path step made more real: `preview and apply or reject a patch`, because this slice proves the current CLI fallback rejects catalog/parser drift from `src/main.py::_dispatch()` before the operator reaches the existing review/apply entrypoints that Milestone 3 still depends on while Textual remains disabled.
- Explicit handoff sentence: this handoff advances the canonical demo-path step `preview and apply or reject a patch` by proving the current CLI fallback rejects catalog/parser drift before an operator reaches `preview`, `apply`, or `reject` from the real `_dispatch() -> parse_args()` path.
- High-risk planned-task framing: prove the real operator path exercises the existing `parse_args()` guard, keep `src/qual/commands/catalog.py` authoritative for canonical command ordering and parser-surface drift detection, add focused regression coverage for alias/token-surface drift rejection, and rerun the required gates for this narrow CLI-compatibility slice.
- Reviewer example coverage note: the active regression coverage explicitly rejects the reviewer-called parser-surface mutations of dropping `diff`, adding `context`, and reordering or otherwise altering the explicit CLI entrypoint list while canonical command names stay the same.
- Per-task canonical demo-path mapping:
  - task 1 -> `preview and apply or reject a patch`: prove the real operator entrypoint reaches the existing parser/catalog guard before the operator reaches patch review/apply.
  - task 2 -> `preview and apply or reject a patch`: keep the catalog authoritative for the exact review/apply CLI surface the operator must use.
  - task 3 -> `preview and apply or reject a patch`: add regression proof that drift is rejected from the real patch-review operator path, not only from helper-level checks.
  - task 4 -> `preview and apply or reject a patch`: rerun the required gates so the handoff records current evidence for this exact blocker-removal slice.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Advance the canonical demo-path step `preview and apply or reject a patch` by proving the existing command-catalog CLI contract in `src/qual/cli.py::parse_args()` is exercised by the real operator entrypoint `src/main.py::_dispatch()`.
2. Advance the canonical demo-path step `preview and apply or reject a patch` by keeping `src/qual/commands/catalog.py` as the authoritative catalog/parser contract for canonical command ordering and parser-surface drift detection behind that active CLI entry path.
3. Advance the canonical demo-path step `preview and apply or reject a patch` by adding regression coverage proving alias/token-surface drift such as dropping `diff` or adding `context` is rejected from `_dispatch()` and `parse_args()`, not only from a direct helper call.
4. Advance the canonical demo-path step `preview and apply or reject a patch` by re-running the required gates and recording the results for the patch-review CLI compatibility slice.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: scope stayed pinned to proving the existing CLI enforcement slice in `src/qual/cli.py`, the top-level operator path in `src/main.py`, the command-catalog contract in `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice
- before risky/shared file edit: no runtime shared-file edit was required because the fail-fast enforcement was already live in `src/qual/cli.py::parse_args()`; this fixer pass stays in the approved shared regression path and metadata packet files
- ready for handoff: this packet explicitly maps the reviewed slice to the canonical `preview and apply or reject a patch` step, and states that parser/catalog drift on the active review/apply CLI loop is proven to fail from the top-level operator path while Textual remains disabled

### Handoff Packet

- branch name: `codex/feat-commands`
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Advanced the canonical demo-path step `preview and apply or reject a patch` by proving the existing command-catalog CLI contract from `src/qual/cli.py::parse_args()` is exercised by the active operator entrypoint `src/main.py::_dispatch()`.
  2. Advanced the canonical demo-path step `preview and apply or reject a patch` by keeping `src/qual/commands/catalog.py` as the authoritative catalog/parser contract for canonical command ordering and parser-surface drift detection behind that active CLI check.
  3. Advanced the canonical demo-path step `preview and apply or reject a patch` by adding focused regression coverage in `tests/unit/test_commands_catalog.py` proving alias/token-surface drift such as dropping `diff` or adding `context` is rejected from `src/main.py::_dispatch()` and `parse_args()`, alongside the existing helper-level catalog drift checks.
- files changed:
  - reviewed implementation evidence: `src/main.py`
  - reviewed implementation evidence: `src/qual/cli.py`
  - reviewed implementation evidence: `src/qual/commands/catalog.py`
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
  - revalidation note: all required gates were rerun on `2026-04-24` in the final fixer pass, and the top-level operator-path regression plus the concrete reviewer examples for dropping `diff`, adding `context`, and reordering or altering the explicit CLI entrypoint list still raise the expected `ValueError`, confirming the packet stays narrowed to catalog/parser determinism for the reviewed CLI drift concern
- traceability:
  - reviewed implementation slice: `src/main.py`, `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
  - implementation commit note for this fixer pass: the operator-path proof landed in `426f2fe5e`, and this final handoff refresh records a clean gate rerun in the final fixer commit before reporting the final HEAD SHA
  - current packet refresh files: `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
  - packet reissue purpose: this final fixer refresh keeps the written handoff aligned with the landed operator-path proof, the explicit canonical demo-path step statement, and the narrowed CLI-compatibility mapping required in review
  - gate rerun verification for this handoff pass was repeated at the current branch tip during the final fixer refresh after adding the explicit `context` alias drift regression
  - final revalidation scope note: this fixer refresh added one focused parser-surface regression in `tests/unit/test_commands_catalog.py` for the reviewer-called `context` alias drift case, then reran all required gates at the post-review-fix branch tip
  - current fixer rerun status: the required gate sequence passed again on `2026-04-24` at the current branch tip, and this metadata-only refresh binds that clean rerun to the new final fixer HEAD without broadening the reviewed implementation claim
- risks/blockers:
  - risk: future command-surface edits still need to preserve deterministic ordering and fast-fail parser/catalog drift detection so the patch-review CLI contract stays stable throughout the current manual operator flow
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 CLI compatibility while Textual remains disabled: this slice hardens the current manual CLI-first loop specifically at the `preview and apply or reject a patch` step by proving the existing `parse_args()` review/apply entry path remains deterministic and migration-safe from the real operator dispatch path while `feat-console` stays disabled and the MVP continues to rely on the CLI fallback surface
- why this is in-bounds under `AGENTS.md`:
  - this is not second-order contract work because the active MVP note explicitly targets `A2UI contracts with CLI fallback`, `feat-console` stays disabled, and the current operator loop still depends on the CLI review/apply surface; hardening that exact fallback step is direct MVP blocker-removal
- reviewer-fix satisfaction note:
  - this reissued handoff now states one exact canonical demo-path step and narrows the vision mapping to CLI compatibility for the existing operator surface; it does not claim workflow/audit progress
- reviewer-required canonical demo-path handoff field: this handoff explicitly advances the canonical demo-path step `preview and apply or reject a patch` by proving the active CLI fallback rejects catalog/parser drift before an operator reaches the `preview`, `apply`, or `reject` entrypoints in the current engine-first MVP loop
- canonical demo-path step advanced: `preview and apply or reject a patch`
- Milestone 3 exit-criterion mapping: this is a narrow Milestone 3 CLI-compatibility safeguard because it keeps the `preview`, `apply`, and `reject` CLI entrypoints deterministic and drift-checked from `src/main.py::_dispatch()` while Textual remains disabled; it does not claim broader command-surface completion.
- concrete canonical mapping: this slice advances `preview and apply or reject a patch` by proving the exact `parse_args()` review/apply surface the operator uses from `_dispatch()` rejects catalog/parser drift before the operator reaches the `preview`, `apply`, or `reject` entrypoints.
- concrete canonical-path blocker removed: before this change, the handoff lacked proof that alias or ordering drift would be rejected from the real operator path before the operator reached the `preview`, `apply`, or `reject` entrypoints even though canonical command names still looked stable; this slice removes that direct blocker on `preview and apply or reject a patch` by proving the active CLI fallback path fails fast on catalog/parser drift.
- non-claim boundary: this handoff does not claim broader CLI polish, new workflow branches, persistence progress, auditable-state/workflow progress, A2UI contract work, provider routing work, public workflow-wrapper exposure, or any new engine behavior
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: this slice is limited to CLI compatibility for the existing `preview`, `apply`, and `reject` contract from the real operator path, keeping the command surface deterministic and drift-checked without claiming persistence, workflow, or audit progress
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- traceability note:
  - reviewed implementation approval stays pinned to `src/main.py`, `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
  - this fixer-turn packet refresh exists to reissue the narrowed handoff packet requested in review with the actual active-CLI enforcement evidence
  - packet metadata files `THREAD_PACKET.md` and `handoff_packets/feat-commands.md` were refreshed in earlier docs-only commits on this branch and are regenerated here to keep the written handoff aligned with that history
- scope/ownership note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - shared runtime evidence path: `src/main.py` and `src/qual/cli.py`
  - focused regression path: `tests/unit/test_commands_catalog.py`
  - approval/source note: the reviewed implementation claim is pinned to `src/main.py`, `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; this fixer pass adds one more parser-surface regression test and refreshes the packet wording, but does not change the existing runtime enforcement point or broaden the approval basis beyond deterministic CLI contract hardening for migration-safe entrypoints
  - shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`
  - integrator-locked edits: none in this fixer pass; runtime enforcement already existed in `src/qual/cli.py::parse_args()`
