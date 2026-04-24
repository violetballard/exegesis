# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: exported the full stable `command_workflow_*` facade for the current MVP loop through `src/qual/commands/workflow.py` and `src/qual/commands/__init__.py`, including canonical workflow lookup/invocation/transition tables plus review follow-up compatibility helpers, and added regression coverage proving those public aliases still match the current MVP contract.
- Canonical demo-path mapping sentence: this slice specifically makes `open project/document` more real because callers can now enter the canonical CLI loop through one stable public `command_workflow_*` facade instead of importing `command_mvp_*` internals; `promote or gather context into the basket` and `preview and apply or reject a patch` remain covered as downstream steps because the same facade now exposes the canonical transitions and review next-action compatibility tables that keep the MVP loop executable while Textual remains disabled.
- Concrete blocker removed: before this change, external callers of `src.qual.commands` could not obtain the full stable workflow contract, lookup table, invocation table, transition targets, and review next-action compatibility mappings from the public facade, so bootstrapping the demo loop from `open project/document` required MVP-specific imports or local table reconstruction.
- Traceability note: reviewed implementation commit is `35d93429`; this packet refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.

## Tasks Completed
1. Expanded `src/qual/commands/workflow.py` to export the stable current-MVP workflow contract, tokens, lookup table, invocation table, transition targets, workflow compatibility tables, and review next-action compatibility helpers through the public `command_workflow_*` facade.
2. Re-exported the new workflow facade helpers from `src/qual/commands/__init__.py` so downstream callers can import them from the package root.
3. Extended `tests/unit/test_commands_catalog.py` to prove the public workflow facade aliases still track the current MVP workflow contract, transition tables, and review next-action compatibility mappings.
4. Refreshed the lane handoff metadata so this work is explicitly mapped to the concrete canonical demo-path step it advances and the blocker it removes.
5. Re-ran the required gates for the updated workflow-facade slice.

## Files Changed
- `src/qual/commands/__init__.py`
- `src/qual/commands/workflow.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_public_workflow_contract_aliases_track_the_current_mvp_contract` -> passed
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_public_workflow_next_action_aliases_track_the_current_mvp_contract` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- Risks: future command-surface changes still need to keep the public `command_workflow_*` facade aligned with the underlying `command_mvp_*` tables and the shared alias tests.
- Blockers: none.

## Roadmap Item(s) Affected
- `ROADMAP.md` Milestone 3 `Real workflow loop` because this slice keeps the CLI compatibility surface complete for the engine-first MVP loop while Textual remains disabled.
- `ROADMAP.md` canonical demo path steps because the direct operator-visible step advanced is `open project/document`, while `promote or gather context into the basket` and `preview and apply or reject a patch` stay covered by the same exported workflow transitions and review-next-action compatibility tables.
- `ROADMAP.md` lane mapping `feat-commands` because this lane owns CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

## Vision Capability Affected
- `PRODUCT_VISION.md` capability 3 `Canonical engine contract` because downstream consumers now obtain the workflow contract from the stable public commands facade instead of MVP-specific internals.
- `PRODUCT_VISION.md` near-term product truth because the CLI remains the active operator surface, and this change removes a concrete bootstrap blocker on that active path.

## Routing / Provider Impact Note
- None. This change does not touch routing or provider configuration.

## Scope / Ownership Note
- Lane-owned implementation paths: `src/qual/commands/__init__.py`, `src/qual/commands/workflow.py`
- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approval mechanism: `scripts/scope-check.sh` branch allowlist for `codex/feat-commands*`
- Integrator-locked edits: none
- Branch-tip scope note: the implementation under review is limited to `src/qual/commands/__init__.py`, `src/qual/commands/workflow.py`, and `tests/unit/test_commands_catalog.py`; `THREAD.md`, `THREAD_PACKET.md`, and this handoff file are metadata only.
