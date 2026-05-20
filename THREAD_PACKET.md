## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Source commit(s): `main...481503db5bef705ebf00f644bb4e31b8a14d0794`
- Scope goal: Advance the canonical demo path step where engine-produced A2UI actions and cards must remain usable through the CLI fallback while Textual lanes stay disabled.
- Scope completed: Added deterministic shared action/card/selection contract materialization, wired terminal CLI fallback materialization and rendering for A2UI surfaces, and covered the behavior with focused contract and fallback tests.
- Roadmap item(s) affected (from `ROADMAP.md`): Milestone 3 A2UI/shared-contract support for the engine loop, especially keeping shared contracts in `shared` while renderers remain outside `shared` and preserving CLI execution while Textual is disabled.
- Vision capability affected (from `PRODUCT_VISION.md`): Shared UI contract (`A2UI`) and CLI compatibility while Textual remains disabled.
- Shared/integrator-locked edits: `YES`
- Approval note: The branch edits shared A2UI contract runtime code in `shared/src/exegesis_shared/contracts/**`. This is acknowledged as shared runtime surface, but it is lane-owned for `feat-a2ui-contract` under `THREAD_OWNERSHIP.md:36-43`; no provider routing, core entrypoint, or Textual implementation files were touched.
- Ownership note: Runtime edits stay within the A2UI lane-owned shared contract paths plus CLI fallback UI/tests needed to preserve the engine-first MVP loop.

## Reviewed Merge Surface

The reviewed implementation range is `main...481503db5bef705ebf00f644bb4e31b8a14d0794`.

## Tasks Completed

1. Added deterministic action selection/materialization support in shared A2UI contracts so generated declarative surfaces map to typed, allowlisted engine actions.
2. Added card and unknown-card action selection materialization in shared card contracts so fallback clients can safely preserve action intent.
3. Updated terminal CLI fallback A2UI materialization/rendering so the engine loop can display usable contract surfaces without Textual.
4. Added unit coverage for shared A2UI contract materialization and CLI fallback safety.
5. Kept the work focused on Milestone 3 A2UI support for the engine loop and CLI fallback; this branch does not claim or implement Textual client behavior.

## Files Changed

- `shared/src/exegesis_shared/contracts/__init__.py`
- `shared/src/exegesis_shared/contracts/actions.py`
- `shared/src/exegesis_shared/contracts/cards.py`
- `src/qual/ui/a2ui.py`
- `src/qual/ui/test_a2ui_fallback_safety.py`
- `tests/unit/test_a2ui_contract.py`

## Commands Run With Results

- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Scope / Ownership Notes

- Canonical demo-path step made more real: retrieve/gather context can now produce A2UI contract surfaces whose actions materialize deterministically and still render through the CLI fallback for plan/revise/apply-or-reject work.
- Routing/provider impact note: None. No model routing or provider configuration was touched.
- Textual impact note: None. Textual implementation remains disabled and out of scope.
- Risks / blockers: Moderate integration risk because shared A2UI contract exports and CLI fallback behavior changed; mitigated by focused contract/fallback tests and the full local gate suite above.
