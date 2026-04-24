# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: remove the parser/catalog drift blocker on the canonical `preview and apply or reject a patch` demo-path step by locking the parser-backed review/apply command surface to the canonical catalog in `src/qual/commands/catalog.py`, without adding new engine behavior.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so drift at operator-facing CLI entrypoints would directly weaken the current manual CLI smoke flow.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Harden `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Preserve canonical command ordering in the CLI contract by returning the validated canonical tuple directly instead of rebuilding a divergent list.
3. Add regression coverage for parser/catalog drift hard-failure paths, including alias-level or ordering drift that could preserve canonical names while still changing the parser surface.
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

- plan complete: scope stayed pinned to the reviewed implementation slice in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice
- before risky/shared file edit: the only shared path in scope was the approved regression file `tests/unit/test_commands_catalog.py`
- ready for handoff: this packet explicitly maps the reviewed slice to the canonical `preview and apply or reject a patch` step, states that parser/catalog drift on the review/apply loop was the direct blocker removed for that step, and adds the direct Milestone 3 CLI-compatibility claim that the MVP loop remains executable through the CLI fallback while Textual stays disabled

### Handoff Packet

- branch name: `codex/feat-commands`
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
  2. Preserved canonical command ordering in the CLI contract by returning the validated canonical tuple directly instead of rebuilding a divergent list.
  3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection and canonical-order alignment, including alias-level drift that preserves canonical command names and direct mutation of the live CLI parser entrypoint constant.
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
  - revalidation note: all required gates were rerun on `2026-04-24`, and the alias-substitution regression still raises `ValueError: Command CLI canonical names are inconsistent`, confirming the packet stays narrowed to command-catalog CLI compatibility for the exact drift concern raised in review
- traceability:
  - reviewed implementation slice: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
  - implementation commit pinned by the reviewer packet: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  - packet refresh commit called out in the reviewer packet as metadata-only: `3cb7da7865dd9c926f6387cc75ad556d7b833441`
  - current packet refresh files: `THREAD_PACKET.md` and `handoff_packets/feat-commands.md`
  - gate rerun verification for this handoff pass was repeated before the metadata refresh commit in this turn
- risks/blockers:
  - risk: future command-surface edits still need to preserve deterministic ordering and fast-fail parser/catalog drift detection so the patch-review CLI contract stays stable throughout the current manual operator flow
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 CLI compatibility while Textual remains disabled: this slice hardens the current manual CLI-first loop specifically at the `preview and apply or reject a patch` step by keeping the review/apply entrypoints deterministic and migration-safe while `feat-console` stays disabled and the MVP continues to rely on the CLI fallback surface
- canonical demo-path step advanced: `preview and apply or reject a patch` on the active MVP engine-first path (`Engine stability`, `FTS-first retrieval`, `A2UI contracts with CLI fallback`)
- Milestone 3 exit-criterion mapping: this slice keeps the CLI/operator fallback able to execute the current MVP review/apply loop while Textual remains disabled by making the `preview`, `apply`, and `reject` command surface deterministic and drift-checked
- concrete canonical mapping: this slice advances the canonical `preview and apply or reject a patch` step in the current engine-first MVP path `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff` by hardening the exact review/apply parser surface the operator must use before `persist -> export-handoff`, while `feat-console` stays disabled and the MVP continues to depend on the CLI fallback surface
- concrete canonical-path blocker removed: before this change, alias or ordering drift could let the operator reach the `preview`, `apply`, or `reject` entrypoints through parser surfaces that no longer matched the canonical catalog even though canonical command names still looked stable; this slice removes that direct blocker on `preview and apply or reject a patch` by forcing the CLI fallback review/apply step to fail fast on parser/catalog drift
- non-claim boundary: this handoff does not claim broader CLI polish, new workflow branches, persistence progress, auditable-state/workflow progress, A2UI contract work, provider routing work, public workflow-wrapper exposure, or any new engine behavior
- vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: this slice is limited to CLI compatibility for the existing engine-facing review/apply contract at `preview`, `apply`, and `reject`, so parser/catalog drift fails fast and the current fallback surface remains deterministic while `feat-console` stays disabled; it does not claim auditable-state/workflow progress or broader operator-surface expansion
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- traceability note:
  - reviewed implementation approval stays pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
  - implementation commit `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` is the reviewed command-catalog slice
  - packet refresh commit `3cb7da7865dd9c926f6387cc75ad556d7b833441` is metadata-only per the reviewer packet
  - packet metadata files `THREAD_PACKET.md` and `handoff_packets/feat-commands.md` were refreshed in earlier docs-only commits on this branch and are regenerated here to keep the written handoff aligned with that history
- scope/ownership note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - focused regression path: `tests/unit/test_commands_catalog.py`
  - approval/source note: the reviewed implementation claim is pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata-only refreshes and do not broaden the approval basis beyond deterministic command-catalog CLI contract hardening for migration-safe entrypoints
  - shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`
  - integrator-locked edits: none
