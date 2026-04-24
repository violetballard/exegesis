# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review scope: branch-tip Milestone 3 CLI compatibility facade for the canonical workflow loop, exposing the stable `command_workflow_*` contract/lookup/invocation APIs plus review follow-up compatibility tables
- Canonical demo-path steps advanced: `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch`
- Explicit re-review statement: the current branch tip is the review target, and this slice specifically makes `open project/document` more real by exporting one stable public workflow facade that can bootstrap the canonical CLI loop while Textual remains disabled; `promote or gather context into the basket` and `preview and apply or reject a patch` remain in scope as downstream steps because the same facade now exposes canonical transitions and review follow-up compatibility tables.
- Concrete blocker removed: callers no longer need to reach into `command_mvp_*` internals or reconstruct workflow tables themselves to enter the canonical loop from `open project/document` and continue into review/apply-or-reject follow-ups.
- Traceability note: reviewed implementation commit is `35d93429`; this metadata refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`.
- Canonical roadmap/vision mapping: `ROADMAP.md` Milestone 3 `Real workflow loop` plus `PRODUCT_VISION.md` capability 3 `Canonical engine contract`, because the CLI remains the active operator surface while Textual is disabled.

## Reviewed Files

- `src/qual/commands/__init__.py`
- `src/qual/commands/workflow.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Required Gates

- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_public_workflow_contract_aliases_track_the_current_mvp_contract`
- `python3 -m unittest tests.unit.test_commands_catalog.CommandCatalogTests.test_public_workflow_next_action_aliases_track_the_current_mvp_contract`
- `make scope-check`
- `./quality-format.sh --check`
- `./quality-lint.sh`
- `./quality-test.sh`
- `./typecheck-test.sh`
- `make ci`
