## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Scope goal: Metadata-only resubmission for the A2UI contract integration-block response.
- Selected integration target: current branch tip after this fixer pass.
- Target type: metadata-only; no runtime, shell, planner, packet-planner, or `.codex` lane-state changes are intended in scope.
- Canonical demo-path step advanced: this A2UI contract handoff advances `preview and apply or reject a patch` by making materialized A2UI actions deterministic for CLI fallback rendering.

## Required Fix Applied

1. Resubmitted one unambiguous integration target: the current branch tip after this fixer commit.
2. Shrunk the runtime/source review surface so the branch no longer carries `src/qual/ui/**`, `tests/unit.sh`, `tests/unit/test_a2ui_contract.py`, `tests/unit/test_packet_planner.py`, `tests/unit/test_ui_shell.py`, or planner source deltas.
3. Split planner and packet tooling out of this A2UI handoff. No planner/tooling changes are retained or justified here.
4. Re-ran the required gates against the resubmitted target and reproduced that local gates are green.
5. Reproduced the remaining mechanical blocker: `.codex/packet_planner/state.json` cannot be restored or rewritten in this sandbox (`Operation not permitted`).

## Files Changed For This Target

- `THREAD_PACKET.md`

Residual protected lane-state paths still present in `git diff --name-status main...HEAD` due sandbox reset blockers:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`

## Explicitly Removed From This Handoff

- `codex_packet_handoff/tools/planner.py`
- `src/qual/ui/__init__.py`
- `src/qual/ui/a2ui.py`
- `src/qual/ui/shell.py`
- `src/qual/ui/test_a2ui_fallback_safety.py`
- `tests/unit.sh`
- `tests/unit/test_a2ui_contract.py`
- `tests/unit/test_packet_planner.py`
- `tests/unit/test_ui_shell.py`

## Plan Alignment

- Roadmap item(s) affected: `ROADMAP.md` Milestone 3 review/integration flow for the current MVP item, `A2UI contracts with CLI fallback`.
- Canonical demo-path step: `preview and apply or reject a patch`.
- Vision capability affected: none in this metadata-only fixer target.
- Routing/provider impact note: none.
- Shared/integrator-locked impact: none intended.
- Scope / approval note: this packet intentionally carries no runtime A2UI, shell, shared contract, provider routing, or planner implementation changes.

## Tasks Completed

1. Re-read the rejection packet and used it as the source of truth.
2. Removed historical runtime, shell, test, planner, and packet-planner deltas from the target.
3. Rewrote the handoff packet to declare a metadata-only branch-tip review.
4. Ran the required gates against the resubmitted target.

## Commands Run And Outcomes

- `git status --short --branch`: PASS; branch `codex/feat-a2ui-contract`.
- `git diff --name-status main...HEAD`: PARTIAL; runtime/planner/test paths removed, but protected `.codex` metadata paths remain.
- `make scope-check`: PASS (`[devex] scope-check: passed for branch 'codex/feat-a2ui-contract'`).
- `./quality-format.sh --check`: PASS (`[format] check passed`).
- `./quality-lint.sh`: PASS (`[lint] passed`).
- `./quality-test.sh`: PASS (smoke passed; 511 unit tests passed).
- `./typecheck-test.sh`: PASS (`[typecheck] compiling Python sources in src/`).
- `make ci`: PASS (`[devex] CI entrypoint completed`).

## Risks / Blockers

- Risk: low for runtime behavior. This is a packet correction and does not change executable A2UI code.
- Blocker: `.codex/packet_planner/state.json` still differs from `main` and cannot be restored in this sandbox. Direct write, `rm`, `touch` in `.codex/packet_planner`, and `git restore` all failed with `Operation not permitted` or index-lock permission errors.
