## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main` (`9abf31c55f420be74389af72b7e4707bb5132790`)
- Authoritative runtime review target: `b929fe6c7a1159c7882acedd247aca31a93cd123`.
- Runtime review range: review that commit only, limited to `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`.
- Administrative re-review commits after `b929fe6c7a1159c7882acedd247aca31a93cd123` update packet metadata only; they are included to correct the handoff evidence, not to expand the runtime review surface.
- Fixer re-review note: this packet supersedes the rejected six-task mixed-scope packet and is the only handoff surface for this re-review.
- Scope goal: resubmit a clean runtime-only A2UI contract handoff for deterministic action ordering, with packet-planner maintenance split out of this review surface.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

## High-Risk / Off-Lane Framing

- Risk reason: the rejected packet mixed A2UI runtime claims with off-lane packet-planner maintenance; this fixer pass splits that maintenance out of the authoritative A2UI review surface.
- Budget used for the corrected runtime scope: `2` meaningful tasks, under the high-risk cap of `4`.
- Approval/scope basis: the reviewer packet explicitly required either removing planner changes from scope or providing explicit approval/scope justification; this packet removes the planner source/test files from the corrected A2UI review target.
- No explicit approval is claimed for `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`, or other packet-planner/control-plane maintenance in this A2UI handoff.

## Tasks Completed

1. Canonicalized materialized A2UI action ordering in `src/qual/ui/a2ui.py` by sorting filtered actions by canonical JSON before rendering.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; deterministic action payloads keep CLI fallback patch preview/apply/reject affordances stable.
2. Added focused contract coverage in `tests/unit/test_a2ui_contract.py` for deterministic filtered-action ordering.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; the test proves the runtime contract stays stable for repeated CLI fallback rendering.

## Files Changed In Review Target

Authoritative runtime review target, commit `b929fe6c7a1159c7882acedd247aca31a93cd123`:

- `src/qual/ui/a2ui.py`
- `tests/unit/test_a2ui_contract.py`

Administrative packet-only re-review metadata changed after the runtime target:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`
- `THREAD_PACKET.md`

No `client-textual/`, retrieval runtime, daemon source, broad docs, shared-contract files, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_lane_profiles.py`, or `tests/unit/test_packet_planner.py` are part of the authoritative runtime review target. Packet-planner maintenance has been split out of this A2UI runtime review.

## Shared / Locked Status

- Integrator-locked files changed in authoritative runtime review target: none.
- Shared-by-approval files changed in authoritative runtime review target: none.
- A2UI runtime/source files changed in authoritative runtime review target: `src/qual/ui/a2ui.py`, `tests/unit/test_a2ui_contract.py`.
- Packet-planner source/test files changed in authoritative runtime review target: none.
- Packet-only files changed after the runtime target for administrative re-review metadata: `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/packet_planner/state.json`, `THREAD_PACKET.md`.
- Explicit split note for off-lane packet/planner changes: the reviewer-required fixer packet allowed splitting packet-planner maintenance from the A2UI runtime review; the corrected A2UI review target does that, so no packet-planner source/test files remain in scope.

## Runtime Scope Note

The isolated runtime change at `b929fe6c7a1159c7882acedd247aca31a93cd123` canonicalized materialized A2UI action order and added focused test coverage in `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`. That commit is the authoritative runtime review target. Packet-planner maintenance is not part of this A2UI review; `codex_packet_handoff/tools/planner.py` is not claimed as changed here, and `tests/unit/test_packet_planner.py` is not present in this tree and is not claimed as coverage.

## Demo-Path Mapping

Deterministic A2UI action ordering makes the `preview and apply or reject a patch` step more real by giving the CLI fallback a stable action list for patch preview, apply, and reject affordances. This keeps the engine loop consumable without depending on Textual implementation work.

## Commands Run

Required gates for the corrected runtime-only A2UI packet and administrative packet reissue:

- Fresh fixer gate run: `2026-05-14`.
- `git merge-base --is-ancestor codex/feat-engine-runs main; printf '%s\n' $?`: reproduced the integrator blocker; returned `1`.
- `make scope-check`: passed; scope-check accepted the packet-only branch diff.
- Final HEAD scope note: the runtime review target is `b929fe6c7a1159c7882acedd247aca31a93cd123`; later packet-only commits correct handoff metadata, and packet-planner source/test maintenance is split out of the A2UI review target.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 511 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed; 511 tests passed inside CI.

## Risks / Blockers

- `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json` are administrative packet metadata changes only.
- Packet-planner maintenance has been split out of this A2UI packet; no router source, shared contract, packet-planner source/test, or Textual file is in the authoritative runtime review target.
- Merge risk is low for the runtime review target because broad source contamination and off-lane packet-planner source/test claims have been removed from the handoff.
- The reproduced predecessor check still returns `1`; this packet states that the historical engine execution order is planning guidance, not a merge prerequisite for the corrected A2UI packet-only review target.
- Final packet reissue commits are handoff-only.
