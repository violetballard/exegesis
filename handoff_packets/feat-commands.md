# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: remove the parser/catalog drift blocker on the canonical `preview and apply or reject a patch` demo-path step by enforcing the catalog-backed contract from the active `parse_args()` CLI path in `src/qual/cli.py`, without adding new engine behavior.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the active CLI entry path in `src/qual/cli.py`, relies on the public command contract in `src/qual/commands/catalog.py`, and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so drift at operator-facing CLI entrypoints would directly weaken the current manual CLI smoke flow.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Enforce the command-catalog CLI contract from the active `parse_args()` path so the real operator entrypoint fails fast if parser/catalog drift is detected.
2. Keep the command-catalog validation as the authoritative grouped parser-surface check behind that active CLI entry path.
3. Add regression coverage proving drift is rejected from `parse_args()` itself, not only from a direct helper call.
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

- plan complete: scope stayed pinned to the active CLI enforcement slice in `src/qual/cli.py`, the command-catalog contract in `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice
- before risky/shared file edit: the reviewer-required implementation change touches `src/qual/cli.py`, which is a shared-by-approval and integrator-locked path, so this handoff records that the shared edit was required to move fail-fast enforcement onto the active CLI surface
- ready for handoff: this packet explicitly maps the reviewed slice to the canonical `preview and apply or reject a patch` step, states that parser/catalog drift on the active review/apply CLI loop was the direct blocker removed for that step, and adds the direct Milestone 3 CLI-compatibility claim that the MVP loop remains executable through the CLI fallback while Textual stays disabled

### Handoff Packet

- branch name: `codex/feat-commands`
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Enforced the command-catalog CLI contract from `src/qual/cli.py::parse_args()` so the active operator entrypoint fails fast when the parser surface drifts from the canonical catalog.
  2. Kept `src/qual/commands/catalog.py` as the authoritative grouped parser-surface contract behind that active CLI check.
  3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` proving parser/catalog drift is rejected from `parse_args()` itself, alongside the existing helper-level catalog drift checks.
- files changed:
  - reviewed implementation: `src/qual/cli.py`
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
  - revalidation note: all required gates were rerun on `2026-04-24`, and the alias-substitution regression still raises `ValueError: Command CLI canonical names are inconsistent`, confirming the packet stays narrowed to command-catalog CLI compatibility for the exact drift concern raised in review
- traceability:
  - reviewed implementation slice: `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
  - implementation commit note for this fixer pass: final HEAD SHA is reported with the handoff deliverable after the active-CLI-path hardening commit is created
  - current packet refresh files: `THREAD_PACKET.md` and `handoff_packets/feat-commands.md`
  - packet reissue purpose: this fixer refresh aligns the handoff with the reviewer-required active-CLI-path enforcement point and preserves the explicit canonical demo-path step statement plus the narrowed CLI-compatibility mapping
  - gate rerun verification for this handoff pass was repeated after the active-CLI-path fix in this turn
- risks/blockers:
  - risk: future command-surface edits still need to preserve deterministic ordering and fast-fail parser/catalog drift detection so the patch-review CLI contract stays stable throughout the current manual operator flow
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 CLI compatibility while Textual remains disabled: this slice hardens the current manual CLI-first loop specifically at the `preview and apply or reject a patch` step by making the active `parse_args()` review/apply entry path deterministic and migration-safe while `feat-console` stays disabled and the MVP continues to rely on the CLI fallback surface
- canonical demo-path step advanced: `preview and apply or reject a patch` on the active MVP engine-first path (`Engine stability`, `FTS-first retrieval`, `A2UI contracts with CLI fallback`)
- Milestone 3 exit-criterion mapping: this slice keeps the CLI/operator fallback able to execute the current MVP review/apply loop while Textual remains disabled by making the active `preview`, `apply`, and `reject` `parse_args()` surface deterministic and drift-checked
- concrete canonical mapping: this slice advances the canonical `preview and apply or reject a patch` step in the current engine-first MVP path `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff` by hardening the exact `parse_args()` review/apply surface the operator must use before `persist -> export-handoff`, while `feat-console` stays disabled and the MVP continues to depend on the CLI fallback surface
- concrete canonical-path blocker removed: before this change, alias or ordering drift could let the operator reach the `preview`, `apply`, or `reject` entrypoints through parser surfaces that no longer matched the canonical catalog even though canonical command names still looked stable; this slice removes that direct blocker on `preview and apply or reject a patch` by forcing the active CLI fallback path to fail fast on parser/catalog drift
- non-claim boundary: this handoff does not claim broader CLI polish, new workflow branches, persistence progress, auditable-state/workflow progress, A2UI contract work, provider routing work, public workflow-wrapper exposure, or any new engine behavior
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: this slice is limited to CLI compatibility for the existing engine-facing review/apply contract at `preview`, `apply`, and `reject`, so parser/catalog drift fails fast on the active CLI entry path and the current fallback surface remains deterministic while `feat-console` stays disabled; it does not claim auditable-state/workflow progress or broader operator-surface expansion
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- traceability note:
  - reviewed implementation approval stays pinned to `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`
  - this fixer-turn packet refresh exists to reissue the narrowed handoff packet requested in review with the actual active-CLI enforcement point
  - packet metadata files `THREAD_PACKET.md` and `handoff_packets/feat-commands.md` were refreshed in earlier docs-only commits on this branch and are regenerated here to keep the written handoff aligned with that history
- scope/ownership note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - reviewer-required shared implementation path: `src/qual/cli.py`
  - focused regression path: `tests/unit/test_commands_catalog.py`
  - approval/source note: the reviewed implementation claim is pinned to `src/qual/cli.py`, `src/qual/commands/catalog.py`, and `tests/unit/test_commands_catalog.py`; the `src/qual/cli.py` touch is required by the reviewer packet's active-CLI-path fix request; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata-only refreshes and do not broaden the approval basis beyond deterministic CLI contract hardening for migration-safe entrypoints
  - shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`
  - integrator-locked edits: `src/qual/cli.py` updated by explicit reviewer-required active-CLI-path enforcement
