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
- ready for handoff: this packet explicitly names `preview and apply or reject a patch` as the protected operator step, states the exact CLI-surface stability blocker removed there, and keeps the claim narrowed to CLI compatibility hardening for the current manual smoke flow

### Handoff Packet

- branch name: `codex/feat-commands`
- tasks completed (numbered):
  1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
  2. Preserved deterministic patch-review CLI entrypoint ordering by rebuilding grouped entrypoints from the public contract and rejecting alias-level or ordering drift that would otherwise keep canonical names stable.
  3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection, including alias-level drift that preserves canonical command names and direct mutation of the live CLI parser entrypoint constant.
- files changed:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: future command-surface edits still need to preserve deterministic ordering and fast-fail parser/catalog drift detection so the patch-review CLI contract stays stable throughout the current manual operator flow
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 1 `Bootstrap Flow Stabilization`: this slice removes a command-behavior stability blocker at the patch-review boundary, directly supporting the roadmap's command hardening scope and `Manual CLI smoke flow remains stable` exit criterion
  - `ROADMAP.md` Milestone 2 `Test Hardening`: this slice adds the targeted parser-edge regression coverage the roadmap calls out as remaining review follow-up work
  - canonical demo-path step advanced: canonical step `5 of 7`, `preview and apply or reject a patch`
  - concrete canonical mapping: this slice advances canonical step `5 of 7`, `preview and apply or reject a patch`, by locking the parser-backed patch-review entrypoints to the canonical catalog before review commands run, so the operator moves from `produce a plan or revision` into patch review on a deterministic CLI surface instead of silently accepting parser/catalog drift
  - concrete canonical-path blocker removed: deterministic CLI ordering and fast-fail parser/catalog drift detection are now enforced at the patch-review boundary, removing the concrete blocker where review/apply commands could silently diverge from the canonical catalog before the operator can safely continue the manual smoke flow through export
  - non-claim boundary: this handoff does not claim progress on persistence, A2UI contracts, provider routing, or any new command reachability
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the existing CLI surface now rejects parser/catalog drift before it can silently change the deterministic operator controls that remain first-class in this repository
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- scope/ownership note:
  - lane-owned implementation path: `src/qual/commands/catalog.py`
  - focused regression path: `tests/unit/test_commands_catalog.py`
  - approval/source note: the reviewed implementation claim is pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata-only refreshes
  - shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`
  - integrator-locked edits: none
