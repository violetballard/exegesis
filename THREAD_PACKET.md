## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Review the full source-bearing A2UI contract/fallback surface currently in `codex/feat-a2ui-contract`, framed as high-risk because the candidate includes lane-owned UI contract/fallback work plus packet-planner handoff metadata behavior outside the lane-owned paths.

## Traceability

- Reviewed source-bearing baseline: `b929fe6c7a1159c7882acedd247aca31a93cd123` was the narrow deterministic action-order commit.
- Current merge candidate includes additional source-bearing commits after that baseline through this fixer commit. Those commits are not metadata-only and are intentionally included in the review scope.
- Source-bearing range to review: `b929fe6c7a1159c7882acedd247aca31a93cd123..HEAD`. This range includes source-bearing A2UI runtime, UI shell tests, packet-planner behavior, typed engine output support, and handoff metadata. It is not a metadata-only resubmission.

## Scope completed

- Canonicalized materialized A2UI action order in `src/qual/ui/a2ui.py` and covered it in `tests/unit/test_a2ui_contract.py` so CLI fallback rendering stays deterministic.
- Stabilized A2UI CLI fallback artifact behavior inside the UI lane, including named artifact payload ordering, stage coverage, fallback safety snapshots, shell fallback behavior, and typed engine output construction.
- Hardened packet-planner handoff metadata handling so roadmap and vision fields remain explicit and auditable instead of being backfilled with placeholders. This is outside the UI lane and is included as an explicit high-risk scope exception for review.
- Updated this packet to declare the full source-bearing review scope rather than describing the branch tip as a metadata-only refresh.

## Files changed

- `src/qual/ui/a2ui.py`
- `src/qual/ui/__init__.py`
- `src/qual/ui/shell.py`
- `src/qual/ui/test_a2ui_fallback_safety.py`
- `tests/unit/test_a2ui_contract.py`
- `tests/unit/test_ui_shell.py`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/lane_meta/feat-a2ui-contract.json`
- `.codex/packet_planner/state.json`
- `.codex/packets/lanes/feat-a2ui-contract/inbox/feature/F__codex-feat-a2ui-contract__aa875cd03ea2a8e092f527610640827baa7b7b5a__20260320T210541Z.md` (removed stale packet)
- `THREAD_PACKET.md`

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop.
  - Scope bullets: lock user-facing output contracts, expand end-to-end verification scenarios, and keep contract changes documented and intentional.
  - Task anchor: current MVP narrowing in `AGENTS.md` names `A2UI contracts with CLI fallback` as one of the active canonical paths.
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface.
  - Engine emits structured outputs that can be consumed by CLI now and `Exegesis Console` next.
  - Renderers remain outside shared contract scope; this candidate preserves CLI fallback as the first renderer without starting console renderer work.
- Canonical demo-path step advanced: `AGENTS.md` active MVP note item `A2UI contracts with CLI fallback`. This work makes that path more real by removing a concrete blocker where equivalent action payloads could render in nondeterministic order, which made CLI snapshots and later contract consumers disagree about the same engine-authored artifact.
- Explicitly deferred from this candidate: Exegesis Console renderer work, Studio renderer work, provider routing changes, and core engine policy changes.

## Tasks completed

1. Updated `src/qual/ui/a2ui.py` to sort filtered actions by canonical JSON before terminal rendering, preserving deterministic CLI fallback output.
2. Added and maintained contract coverage in `tests/unit/test_a2ui_contract.py` for canonical ordering behavior.
3. Stabilized A2UI CLI fallback artifact payloads, named artifact ordering, stage coverage, and fallback safety snapshots in `src/qual/ui/a2ui.py` and `src/qual/ui/test_a2ui_fallback_safety.py`.
4. Updated public UI exports in `src/qual/ui/__init__.py` for the typed engine output API.
5. Covered shell fallback behavior in `src/qual/ui/shell.py` and `tests/unit/test_ui_shell.py`.
6. Hardened packet-planner required handoff field behavior in `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.
7. Corrected handoff traceability and files-changed metadata so all source-bearing branch changes are declared for review.

## Required Handoff Fields

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3: Real workflow loop; current MVP `A2UI contracts with CLI fallback` canonical path
- Vision capability affected: `PRODUCT_VISION.md` Capability 4: Shared UI contract / operator-first control surface
- Canonical demo-path step advanced: `AGENTS.md` active MVP note item `A2UI contracts with CLI fallback`; deterministic A2UI action ordering removes the concrete CLI fallback snapshot/consumer mismatch blocker for that path
- Routing/provider impact note: None
- Scope / approval note: Lane-owned edits are under `src/qual/ui/**`. Test coverage files under `tests/unit/**` support those changes. `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`, and `.codex/**` packet state are outside the UI lane and are submitted as explicit high-risk review scope because they only correct handoff metadata behavior needed for this resubmission; they do not change runtime provider routing or core engine entrypoints. This candidate intentionally exceeds the high-risk 4-task, 8-file, and 300-net-LOC limits and requires integrator approval for that full source-bearing range before merge.

## Commands Run And Outcomes

- `make scope-check`: PASS on fixer re-run (`[devex] scope-check: passed for branch 'codex/feat-a2ui-contract'`)
- `./quality-format.sh --check`: PASS on fixer re-run (`[format] check passed`)
- `./quality-lint.sh`: PASS on fixer re-run (`[lint] passed`)
- `python -m pytest -q src/qual/ui/test_a2ui_fallback_safety.py -k 'engine_output'`: PASS (`12 passed, 412 deselected`)
- `python -m pytest src/qual/ui/test_a2ui_fallback_safety.py tests/unit/test_a2ui_contract.py tests/unit/test_packet_planner.py tests/unit/test_ui_shell.py`: INCONCLUSIVE, process exited with code `-1` after collecting 538 tests and starting `src/qual/ui/test_a2ui_fallback_safety.py`
- `./quality-test.sh`: INCONCLUSIVE on fixer re-run; process exited with code `-1` during `tests/unit.sh` verbose `unittest discover` after `test_engine_contract_manifest_bundles_the_cli_fallback_route_and_entrypoint` started; no assertion failure was reported before termination
- `./typecheck-test.sh`: PASS on fixer re-run (`[typecheck] compiling Python sources in src/`)
- `make ci`: INCONCLUSIVE on fixer re-run; completed scope/format/lint/typecheck sub-gates, then terminated during nested `quality-test.sh` with `make: *** [ci] Terminated: 15`

## Risks / blockers

- Risk: `HIGH`
- Blockers: full `quality-test.sh` / `make ci` unit discovery was terminated by the local command runner before completion, so this packet remains blocked until those gates pass. `.codex/**` metadata files still contain stale Milestone 5 / capability 5 strings, but this sandbox cannot update them because temp-file creation under `.codex` fails with `Operation not permitted`; the reviewer-facing `THREAD_PACKET.md` has been aligned to Milestone 3 / capability 4.
