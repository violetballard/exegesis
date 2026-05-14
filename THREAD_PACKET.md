## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main` (`9abf31c55f420be74389af72b7e4707bb5132790`)
- Authoritative review target: final branch tip after this fixer commit, reviewed only as the current `main..HEAD` merge diff.
- Do not review `b929fe6c7a1159c7882acedd247aca31a93cd123..HEAD`; that historical range includes superseded branch cleanup and is not the integration candidate.
- Scope goal: resubmit a clean A2UI contract handoff whose integration diff is limited to packet metadata and whose runtime behavior is already present in the merge target.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

## Tasks Completed

1. Restored the corrected candidate content to match `main` for unrelated Textual, retrieval, daemon/tooling, docs, shared-contract, planner, and broad source paths.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; removes off-lane runtime contamination so the A2UI contract handoff can be reviewed against the patch-preview/apply support surface only.
2. Verified the intended A2UI action canonicalization behavior is already present in the corrected `main` target baseline.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; confirms the deterministic A2UI action payload behavior needed by CLI fallback rendering is already available to the demo path.
3. Updated this handoff packet so the files changed, shared/locked status, tasks, risks, and command outcomes describe the exact corrected merge candidate.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; removes the concrete review blocker where stale packet claims could cause an off-scope or misleading patch candidate to be applied.

## Files Changed In Corrected Merge Diff

Authoritative final diff against current `main` (`main..HEAD`):

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`
- `THREAD_PACKET.md`

No `client-textual/`, retrieval runtime, daemon/tooling source, broad docs, packet planner source, shared-contract files, `codex_packet_handoff/tools/planner.py`, or `tests/unit/test_packet_planner.py` are part of the authoritative review target.

## Shared / Locked Status

- Integrator-locked files changed in corrected final diff: none.
- Shared-by-approval files changed in corrected final diff: none.
- Runtime/source files changed in corrected final diff: none.
- Packet-only files changed in corrected final diff: `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/packet_planner/state.json`, `THREAD_PACKET.md`.
- Explicit approval note for off-lane packet metadata: the reviewer-required fixer packet instructs this pass to correct inaccurate packet claims and allows handoff-file correction as the source of truth. The remaining `.codex` changes are packet/planner metadata only, not packet planner/tooling source changes, and are included solely as handoff metadata for this corrected A2UI review candidate.

## Runtime Scope Note

The isolated runtime change at `b929fe6c7a1159c7882acedd247aca31a93cd123` canonicalized materialized A2UI action order and added focused test coverage in `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`. Current `main` already contains that behavior, so the authoritative review target is the corrected packet-metadata handoff diff in `main..HEAD`, not the historical runtime commit and not the historical `b929fe6c7..HEAD` range. `codex_packet_handoff/tools/planner.py` is not changed in this corrected candidate. `tests/unit/test_packet_planner.py` is not present in this tree and is not claimed as coverage.

## Demo-Path Mapping

Deterministic A2UI action ordering makes the `preview and apply or reject a patch` step more real by giving the CLI fallback a stable action list for patch preview, apply, and reject affordances. This keeps the engine loop consumable without depending on Textual implementation work.

## Commands Run

Required gates for the authoritative `main..HEAD` corrected merge candidate:

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 511 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed; 511 tests passed inside CI.

## Risks / Blockers

- `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json` are packet/planner metadata changes only; no packet planner source, router source, runtime source, shared contract, or Textual file is in the corrected final diff.
- Merge risk is low for the corrected final diff because all broad source/runtime contamination has been removed from the branch tip.
