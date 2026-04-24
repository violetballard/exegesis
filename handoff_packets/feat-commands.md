# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the current manual CLI smoke flow deterministic at the patch-review step by locking the parser-backed review command surface to the canonical catalog without adding new commands or new engine behavior.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so parser drift at patch-review entrypoints would directly weaken the current manual CLI smoke flow.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Harden `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Add regression coverage proving live parser/catalog drift raises a hard failure, including alias-level drift that preserves canonical command names and direct mutation of the live parser entrypoint constant.
3. Re-run the required gates and record the results for the narrowed patch-review CLI compatibility slice.

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
- ready for handoff: this packet explicitly names `preview and apply or reject a patch` as the demo-path step advanced, states the exact review/apply CLI blocker removed there, and keeps the claim narrowed to CLI compatibility while Textual remains disabled

### Handoff Packet

- branch name: `codex/feat-commands`
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
  2. Preserved deterministic patch-review CLI entrypoint ordering by rebuilding grouped entrypoints from the public contract and rejecting alias-level or ordering drift that would otherwise keep canonical names stable.
  3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection, including alias-level drift that preserves canonical command names and direct mutation of the live CLI parser entrypoint constant.
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
- traceability:
  - reviewed implementation slice only: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`
  - docs-only refresh commit in branch history: `8391bf07914fffd6fcd29867dc6f21ed25a56ea1` (`docs(thread): pin feat-commands demo-path step`)
  - metadata-only file changed by `8391bf07914fffd6fcd29867dc6f21ed25a56ea1`: `THREAD.md`
  - current packet refresh files: `THREAD_PACKET.md` and `handoff_packets/feat-commands.md`
- risks/blockers:
  - risk: future command-surface edits still need to preserve deterministic ordering and fast-fail parser/catalog drift detection so the patch-review CLI contract stays stable throughout the current manual operator flow
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 `Product Readiness`: this slice helps lock an intentional user-facing CLI contract before publish by keeping the current engine-first loop on deterministic, migration-safe entrypoints while the future console client is still disabled
- canonical demo-path step advanced: `preview and apply or reject a patch`
- concrete canonical mapping: this slice hardens the existing patch-review/apply CLI surface inside `project-open/bootstrap -> retrieval -> plan-or-revise -> apply-or-reject -> export-handoff`, so the operator can still reach the current review/apply step through deterministic, migration-safe entrypoints while Textual remains disabled
- concrete canonical-path blocker removed: deterministic CLI ordering and fast-fail parser/catalog drift detection now cover alias and token-level drift on the existing review/apply command surface, removing the blocker where the current CLI entrypoints could silently diverge before the engine-first loop reaches export handoff
- non-claim boundary: this handoff does not claim broader CLI polish, new workflow reachability, persistence progress, A2UI contract work, provider routing work, or any new engine behavior
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the existing CLI surface now rejects parser/catalog drift before it can silently change the deterministic operator contract that remains first-class in Engine and must stay compatible with future `Exegesis Console` consumption
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- traceability note:
  - reviewed implementation approval stays pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` only
  - docs-only refresh commit `8391bf07914fffd6fcd29867dc6f21ed25a56ea1` changed `THREAD.md` only
  - packet metadata files `THREAD_PACKET.md` and `handoff_packets/feat-commands.md` were refreshed in earlier docs-only commits on this branch and are regenerated here to keep the written handoff aligned with that history
- scope/ownership note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - focused regression path: `tests/unit/test_commands_catalog.py`
  - approval/source note: the reviewed implementation claim is pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata-only refreshes and do not broaden the approval basis beyond deterministic CLI contract hardening for migration-safe entrypoints
  - shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`
  - integrator-locked edits: none
