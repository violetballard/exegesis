# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: remove the parser/catalog drift blocker on the canonical `preview and apply or reject a patch` demo-path step by proving the existing catalog-backed guard in `src/qual/cli.py::parse_args()` rejects drift from the top-level operator path `src/main.py::_dispatch()`, without adding new engine behavior.
- Risk reason: this is a high-risk command-contract handoff because it relies on the public command contract in `src/qual/commands/catalog.py` and the approved shared regression path `tests/unit/test_commands_catalog.py`, and drift at operator-facing CLI entrypoints would directly weaken the current manual CLI smoke flow.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Prove the existing command-catalog CLI contract in `src/qual/cli.py::parse_args()` is exercised by the real operator entrypoint `src/main.py::_dispatch()`.
2. Keep `src/qual/commands/catalog.py` as the authoritative grouped parser-surface check behind that active CLI entry path.
3. Add regression coverage proving drift is rejected from `_dispatch()` and `parse_args()`, not only from a direct helper call.
4. Re-run the required gates and record the results for the patch-review CLI compatibility slice.

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
- ready for handoff: this packet explicitly maps the reviewed slice to the canonical `preview and apply or reject a patch` step, states that parser/catalog drift on the active review/apply CLI loop is now proven to fail from the top-level operator path, and adds the direct Milestone 3 CLI-compatibility claim that the MVP loop remains executable through the CLI fallback while Textual stays disabled

### Handoff Packet

- branch name: `codex/feat-commands`
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Proved the existing command-catalog CLI contract from `src/qual/cli.py::parse_args()` is exercised by the active operator entrypoint `src/main.py::_dispatch()`.
  2. Kept `src/qual/commands/catalog.py` as the authoritative grouped parser-surface contract behind that active CLI check.
  3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` proving parser/catalog drift is rejected from `src/main.py::_dispatch()` and `parse_args()`, alongside the existing helper-level catalog drift checks.
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
  - revalidation note: all required gates were rerun on `2026-04-24`, and the top-level operator-path regression plus the alias-substitution regression still raise the expected `ValueError`, confirming the packet stays narrowed to command-catalog CLI compatibility for the exact drift concern raised in review
- traceability:
  - reviewed implementation slice: `src/main.py`, `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
  - implementation commit note for this fixer pass: the operator-path proof landed in `426f2fe5e`, and this final handoff refresh records a clean gate rerun at the current branch tip before reporting the final HEAD SHA
  - current packet refresh files: `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
  - packet reissue purpose: this final fixer refresh keeps the written handoff aligned with the landed operator-path proof, the explicit canonical demo-path step statement, and the narrowed CLI-compatibility mapping required in review
  - gate rerun verification for this handoff pass was repeated at the current branch tip during the final fixer refresh
- risks/blockers:
  - risk: future command-surface edits still need to preserve deterministic ordering and fast-fail parser/catalog drift detection so the patch-review CLI contract stays stable throughout the current manual operator flow
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 CLI compatibility while Textual remains disabled: this slice hardens the current manual CLI-first loop specifically at the `preview and apply or reject a patch` step by proving the existing `parse_args()` review/apply entry path is deterministic and migration-safe from the real operator dispatch path while `feat-console` stays disabled and the MVP continues to rely on the CLI fallback surface
- why this is in-bounds under `AGENTS.md`:
  - this is not second-order contract work because the active MVP note explicitly targets `A2UI contracts with CLI fallback`, `feat-console` stays disabled, and the current operator loop still depends on the CLI review/apply surface; hardening that exact fallback step is direct MVP blocker-removal
- reviewer-fix satisfaction note:
  - this reissued handoff now states the exact canonical demo-path step it advances and narrows the vision mapping to the operator-first CLI compatibility surface only; it does not claim `Auditable state and workflow`
- reviewer-required canonical demo-path handoff field: this handoff explicitly advances the canonical `preview and apply or reject a patch` step by proving the active CLI fallback rejects parser/catalog drift before an operator reaches the `preview`, `apply`, or `reject` entrypoints in the current engine-first MVP loop
- canonical demo-path step advanced: `preview and apply or reject a patch` on the active MVP engine-first path (`Engine stability`, `FTS-first retrieval`, `A2UI contracts with CLI fallback`)
- Milestone 3 exit-criterion mapping: this slice keeps the CLI/operator fallback able to execute the current MVP review/apply loop while Textual remains disabled by proving the active `preview`, `apply`, and `reject` `parse_args()` surface is deterministic and drift-checked from `src/main.py::_dispatch()`
- concrete canonical mapping: this slice advances the canonical `preview and apply or reject a patch` step in the current engine-first MVP path `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff` by proving the exact `parse_args()` review/apply surface the operator must use from `_dispatch()` rejects parser drift before `persist -> export-handoff`, while `feat-console` stays disabled and the MVP continues to depend on the CLI fallback surface
- concrete canonical-path blocker removed: before this change, the handoff lacked proof that alias or ordering drift would be rejected from the real operator path before the operator reached the `preview`, `apply`, or `reject` entrypoints even though canonical command names still looked stable; this slice removes that direct blocker on `preview and apply or reject a patch` by proving the active CLI fallback path fails fast on parser/catalog drift
- non-claim boundary: this handoff does not claim broader CLI polish, new workflow branches, persistence progress, auditable-state/workflow progress, A2UI contract work, provider routing work, public workflow-wrapper exposure, or any new engine behavior
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: this slice is limited to CLI compatibility for the existing engine-facing review/apply contract at `preview`, `apply`, and `reject`, so parser/catalog drift is now proven to fail fast on the active CLI entry path and the current fallback surface remains deterministic while `feat-console` stays disabled; it does not claim auditable-state/workflow progress or broader operator-surface expansion
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
  - approval/source note: the reviewed implementation claim is pinned to `src/main.py`, `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; this fixer pass adds operator-path proof in tests and does not change the existing runtime enforcement point; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata-only refreshes and do not broaden the approval basis beyond deterministic CLI contract hardening for migration-safe entrypoints
  - shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`
  - integrator-locked edits: none in this fixer pass; runtime enforcement already existed in `src/qual/cli.py::parse_args()`
