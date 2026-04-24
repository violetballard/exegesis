# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Scope completed: hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the existing CLI contract validates the full grouped parser-surface projection against the canonical catalog, rejects alias substitution, missing canonical entrypoints, reordered grouped entrypoints, and extra parser-only aliases, and raises if the parser-backed catalog surface drifts; added focused regression coverage for that parser-surface drift rejection in `tests/unit/test_commands_catalog.py`.
- Scope summary: this is CLI compatibility hardening for the active MVP loop while Textual remains disabled. It does not add new commands, new engine behavior, or new workflow reachability.
- Canonical demo-path step advanced: canonical step `5 of 7`, `preview and apply or reject a patch`
- Concrete canonical mapping: this slice advances canonical step `5 of 7`, `preview and apply or reject a patch`, inside the current MVP loop by locking the parser-backed patch-review entrypoints to the canonical catalog before review commands run, so the operator moves from `produce a plan or revision` into patch review on a deterministic CLI surface instead of silently accepting parser/catalog drift.
- Current MVP loop note: by hard-failing parser/catalog drift at the patch-review boundary, this change keeps the CLI side of `open project/document`, `retrieve relevant material`, `preview and apply or reject a patch`, and `continue working without losing context` deterministic while Textual remains disabled.
- Concrete canonical-path blocker removed: deterministic CLI ordering and fast-fail parser/catalog drift detection are now enforced at the patch-review boundary, removing the concrete blocker where review/apply commands could silently diverge from the canonical catalog before the operator can safely continue to `persist the updated document/session state` while Textual remains disabled.
- Milestone 3 exit-criteria note: this is not second-order work because `ROADMAP.md` requires the CLI to execute the MVP flow while Textual remains disabled, and this slice directly hardens the command boundary operators must cross to complete that loop safely.
- Canonical demo-path context: `AGENTS.md` defines the engine-side path as `open project/document` -> `retrieve relevant material` -> `promote or gather context into the basket` -> `produce a plan or revision` -> `preview and apply or reject a patch` -> `persist the updated document/session state` -> `continue working without losing context`.
- Roadmap tie-in: this is Milestone 3 CLI compatibility work for the real workflow loop, specifically at the patch-review step while Textual remains disabled.
- Non-claim boundary: this handoff does not claim progress on persistence, A2UI, Textual activation, or any new command reachability.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the existing Milestone 3 CLI compatibility surface deterministic at the patch-review step by locking the parser-backed review command surface to the canonical catalog without adding new commands or new engine behavior.
- Risk reason: this is a high-risk/shared-file handoff because it hardens the public command contract in `src/qual/commands/catalog.py` and uses the explicitly approved shared regression path `tests/unit/test_commands_catalog.py`, so parser drift at canonical patch-review entrypoints would directly weaken the active Milestone 3 CLI compatibility surface.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Harden `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Add regression coverage proving live parser/catalog drift raises a hard failure, including alias-level drift that preserves canonical command names and direct mutation of the live parser entrypoint constant.
3. Re-run the required gates and record the results for the narrowed patch-review CLI compatibility slice.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (Short Updates)

- Plan complete: scope stayed pinned to the reviewed implementation slice in `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`.
- First green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed for this handoff slice.
- Before risky/shared file edit: the only shared path in scope was the approved regression file `tests/unit/test_commands_catalog.py`.
- Ready for handoff: this packet explicitly names `preview and apply or reject a patch` as the protected canonical step, states the exact CLI-surface stability blocker removed there, and keeps the claim narrowed to CLI compatibility hardening for that existing MVP loop step.

## Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` so it validates the full grouped parser-surface projection against the canonical catalog instead of trusting derived canonical-name order alone.
2. Preserved deterministic patch-review CLI entrypoint ordering by rebuilding grouped entrypoints from the public contract and rejecting alias-level or ordering drift that would otherwise keep canonical names stable.
3. Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser/catalog drift rejection, including alias-level drift that preserves canonical command names and direct mutation of the live CLI parser entrypoint constant.

## Packet Scope Notes

- Packet refresh work is intentionally excluded from the numbered task list above; the counted lane work is command-contract hardening plus regression coverage only.
- The counted task total for this handoff is `3` meaningful, testable lane tasks.
- The re-review claim is limited to CLI compatibility hardening for the existing patch-review step in the active MVP loop, not generic command-catalog maintenance.

## Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results

- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers

- Risks: future command-surface edits still need to preserve deterministic ordering and fast-fail parser/catalog drift detection so the patch-review CLI contract stays stable throughout the active Milestone 3 workflow while Textual remains disabled.
- Blockers: none.

## Roadmap Item(s) Affected

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice removes a CLI-surface stability blocker at the patch-review boundary for the CLI-first MVP loop while the package/layout migration lands.
- `ROADMAP.md` Milestone 3 exit criteria `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`: this is not second-order work because parser/catalog drift at patch review would break that CLI loop before operators can finish the run.
- `ROADMAP.md` canonical MVP loop step `preview and apply or reject a patch`: this slice hardens the exact command boundary operators use at that step, after planning/revision output and before persistence/continued work.
- `ROADMAP.md` lane mapping for `feat-commands`: this slice hardens migration-safe CLI entrypoints only and does not claim broader workflow reachability.

## Vision Capability Affected

- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: the existing CLI surface now rejects parser/catalog drift before it can silently change the engine-facing command contract that must remain stable while Textual remains disabled.

## Routing / Provider Impact Note

- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note

- Lane-owned implementation path: `src/qual/commands/catalog.py`
- Focused regression path: `tests/unit/test_commands_catalog.py`
- Approval/source note: the reviewed implementation claim is pinned to `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` are metadata-only refreshes.
- Shared-test approval record: `scripts/scope-check.sh` lists `tests/unit/test_commands_catalog.py` under `is_approved_shared_test()` for branch `codex/feat-commands*`.
- Integrator-locked edits: none.
