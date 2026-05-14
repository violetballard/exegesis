## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main` (`9abf31c55f420be74389af72b7e4707bb5132790`)
- Authoritative review target: the branch tip submitted for re-review, reviewed only as the current `main..HEAD` merge diff.
- Do not review `b929fe6c7a1159c7882acedd247aca31a93cd123..HEAD`; that historical range includes superseded branch cleanup and is not the integration candidate.
- Scope goal: resubmit a clean A2UI contract handoff whose integration diff is limited to the intended A2UI packet metadata plus the reviewer-required packet-planner fallback fix and regression coverage.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

## High-Risk / Off-Lane Framing

- Risk reason: this fixer pass keeps `codex_packet_handoff/tools/planner.py` and `tests/unit/test_lane_profiles.py` in scope to satisfy reviewer-required fixes for packet-planner behavior, outside the normal A2UI lane-owned runtime paths.
- Budget used for the corrected fixer scope: high-risk cap of `4` meaningful tasks, including the packet-only corrections needed to resubmit the handoff coherently.
- Approval/scope basis: the reviewer packet explicitly required either removing planner changes from scope or providing explicit approval/scope justification; this packet chooses the full `main..HEAD` review target and includes the planner source/test changes only for that required correction.

## Tasks Completed

1. Restored the corrected candidate content to match `main` for unrelated Textual, retrieval, daemon/tooling, docs, shared-contract, planner, and broad source paths.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; removes off-lane runtime contamination so the A2UI contract handoff can be reviewed against the patch-preview/apply support surface only.
2. Verified the intended A2UI action canonicalization behavior is already present in the corrected `main` target baseline.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; confirms the deterministic A2UI action payload behavior needed by CLI fallback rendering is already available to the demo path.
3. Removed the synthetic `tasks_completed` fallback from `codex_packet_handoff/tools/planner.py` and clarified generated feature packets so the active engine execution order cannot be read as a hard merge prerequisite unless a packet explicitly lists one.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; prevents generated handoff packets and stale packet claims from inventing completed work or misleading review of the patch-preview/apply support surface.
4. Added packet-planner regression coverage in `tests/unit/test_lane_profiles.py` and reissued this packet with an accurate files-changed list, shared/locked status, runtime scope note, risks, and command outcomes.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; keeps the corrected handoff behavior testable without adding the absent `tests/unit/test_packet_planner.py` file and lets the A2UI contract packet be re-reviewed on its actual diff instead of stale packet claims.

## Files Changed In Corrected Merge Diff

Authoritative final diff against current `main` (`main..HEAD`):

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`
- `THREAD_PACKET.md`
- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_lane_profiles.py`

No `client-textual/`, retrieval runtime, daemon source, broad docs, shared-contract files, or `tests/unit/test_packet_planner.py` are part of the authoritative review target. The packet-planner source and existing planner-adjacent test file are included only for reviewer-required fix 2 and fix 3.

## Shared / Locked Status

- Integrator-locked files changed in corrected final diff: none.
- Shared-by-approval files changed in corrected final diff: `codex_packet_handoff/tools/planner.py` and `tests/unit/test_lane_profiles.py`, changed only to satisfy reviewer-required packet/planner fixes.
- A2UI runtime/source files changed in corrected final diff: none.
- Packet-planner source/test files changed in corrected final diff: `codex_packet_handoff/tools/planner.py`, `tests/unit/test_lane_profiles.py`.
- Packet-only files changed in corrected final diff: `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/packet_planner/state.json`, `THREAD_PACKET.md`.
- Explicit approval note for off-lane packet/planner changes: the reviewer-required fixer packet instructs this pass to correct inaccurate packet claims, remove or reconcile the planner fallback, and add/correct packet-planner regression coverage. The packet-planner source/test changes are included solely to satisfy those required fixes.

## Runtime Scope Note

The isolated runtime change at `b929fe6c7a1159c7882acedd247aca31a93cd123` canonicalized materialized A2UI action order and added focused test coverage in `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`. Current `main` already contains that behavior, so the authoritative review target is the corrected handoff/planner diff in `main..HEAD`, not the historical runtime commit and not the historical `b929fe6c7..HEAD` range. `codex_packet_handoff/tools/planner.py` is changed only to remove the synthetic `tasks_completed` fallback and clarify that engine execution order is planning guidance, not an implicit merge prerequisite. Packet-planner regression coverage lives in `tests/unit/test_lane_profiles.py`; `tests/unit/test_packet_planner.py` is not present in this tree and is not claimed as coverage.

## Demo-Path Mapping

Deterministic A2UI action ordering makes the `preview and apply or reject a patch` step more real by giving the CLI fallback a stable action list for patch preview, apply, and reject affordances. This keeps the engine loop consumable without depending on Textual implementation work.

## Commands Run

Required gates for the authoritative `main..HEAD` corrected merge candidate:

- Revalidated during the `20260514T175633Z` fixer pass after confirming the packet-planner fallback removal and existing regression coverage.
- `python -m pytest tests/unit/test_lane_profiles.py -q`: passed; 7 tests passed.
- `git merge-base --is-ancestor codex/feat-engine-runs main; printf '%s\n' $?`: reproduced the integrator blocker; returned `1`.
- `python -m pytest tests/unit/test_lane_profiles.py -q`: passed; 7 tests passed after the integration-note regression update.
- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 512 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed; 512 tests passed inside CI.

## Risks / Blockers

- `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json` are packet/planner metadata changes only.
- `codex_packet_handoff/tools/planner.py` and `tests/unit/test_lane_profiles.py` are off-lane packet tooling changes required by reviewer fixes; no router source, runtime source, shared contract, or Textual file is in the corrected final diff.
- Merge risk is low to medium for the corrected final diff because broad source/runtime contamination has been removed from the branch tip, while the remaining packet-planner source change is narrow and regression-tested.
- The reproduced predecessor check still returns `1`; the fix is that generated A2UI feature packets now explicitly say engine execution order is planning guidance, not a merge prerequisite unless the packet declares one.
- Final packet reissue commits are handoff-only; reviewer-required packet-planner source/test changes are in the preceding fixer commit and remain listed in the full `main..HEAD` review surface above.
