# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: current branch-tip Milestone 3 CLI compatibility facade for the canonical workflow loop, exposing the stable `command_workflow_*` workflow/transition tables and review follow-up compatibility lookups
- Canonical demo-path steps advanced: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`
- Required mapping statement: this slice specifically makes `open project/document` more real because callers can now bootstrap the canonical CLI loop through one stable public `command_workflow_*` facade instead of importing `command_mvp_*` internals; `promote or gather context into the basket` and `preview and apply or reject a patch` remain protected as downstream steps because the same facade now exports the canonical workflow transitions plus the review follow-up compatibility tables that keep the loop executable while Textual remains disabled.
- Concrete blocker removed: before this slice, external callers of `src.qual.commands` could not obtain the full stable workflow contract, lookup table, invocation table, transition targets, and review next-action compatibility mappings from the public facade, which made the demo loop harder to drive from `open project/document` without reaching into MVP-specific internals.
- Traceability note: reviewed implementation commit is `35d93429`; this metadata refresh changes only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the Milestone 3 CLI compatibility surface stable by exposing the full current-MVP workflow facade through the public `command_workflow_*` API that downstream CLI and future A2UI consumers can call directly.
- Risk reason: this touches exported command-contract surfaces in `src/qual/commands/workflow.py` and `src/qual/commands/__init__.py`, plus a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks

1. Export the stable workflow contract, lookup, invocation, transition, and compatibility tables through `src/qual/commands/workflow.py`.
2. Re-export the new workflow facade helpers from `src/qual/commands/__init__.py`.
3. Extend shared regression coverage to prove the public workflow facade aliases still track the current MVP contract and review next-action compatibility tables.
4. Refresh the handoff packet so it matches the current branch tip, states the concrete canonical demo-path step advanced, and records the required gate results.

## Review Basis

- Implementation files:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/workflow.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `handoff_packets/feat-commands.md`

## Commands Run and Outcomes

- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_public_workflow_contract_aliases_track_the_current_mvp_contract`: `PASSED`
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_public_workflow_next_action_aliases_track_the_current_mvp_contract`: `PASSED`
- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

## Ownership Note

- Lane-owned implementation paths: `src/qual/commands/__init__.py`, `src/qual/commands/workflow.py`
- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval mechanism: `scripts/scope-check.sh` branch allowlist for `codex/feat-commands*`
- Integrator-locked edits: `none`
- Scope note: the current branch tip contains the three implementation files above plus the handoff metadata files in this packet.
- Packet-refresh accounting note: this metadata refresh changes only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

## Roadmap and Vision Mapping

- `ROADMAP.md` Milestone 3 `Real workflow loop`: this change keeps the CLI compatibility layer complete for the engine-first MVP loop while Textual remains disabled.
- `ROADMAP.md` canonical demo path steps: the direct operator-visible step advanced is `open project/document`, because the public workflow facade now exposes the stable entrypoint mappings that bootstrap the loop, while `promote or gather context into the basket` and `preview and apply or reject a patch` stay covered by the same exported transition and review-next-action tables.
- `ROADMAP.md` active lane mapping: `feat-commands` owns CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: downstream consumers now get the workflow contract from the stable public commands facade instead of MVP-specific internals.
- `PRODUCT_VISION.md` near-term product truth: the CLI remains the active operator surface until UI lanes are enabled, so exporting the full workflow facade removes a concrete bootstrap blocker on that active path.
