## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main` (`9abf31c55f420be74389af72b7e4707bb5132790`)
- Corrected candidate: final branch tip after this fixer commit.
- Scope goal: remove off-scope branch-tip contamination and resubmit a traceable A2UI contract handoff.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

## Tasks Completed

1. Restored the corrected candidate content to match `main` for unrelated Textual, retrieval, daemon/tooling, docs, shared-contract, planner, and broad source paths.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; removes off-lane runtime contamination so the A2UI contract handoff can be reviewed against the patch-preview/apply support surface only.
2. Verified the intended A2UI action canonicalization behavior is already present in the corrected `main` target baseline.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; confirms the deterministic A2UI action payload behavior needed by CLI fallback rendering is already available to the demo path.
3. Updated this handoff packet so the files changed, shared/locked status, tasks, risks, and command outcomes describe the exact corrected merge candidate.
   Canonical demo-path step advanced: `preview and apply or reject a patch`; removes the concrete review blocker where stale packet claims could cause an off-scope or misleading patch candidate to be applied.

## Files Changed In Corrected Merge Diff

Expected final diff against current `main`:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`
- `THREAD_PACKET.md`

No `client-textual/`, retrieval runtime, daemon/tooling source, broad docs, packet planner source, or shared-contract files are intentionally included in the corrected final merge diff.

## Shared / Locked Status

- Integrator-locked files changed in corrected final diff: none.
- Shared-by-approval files changed in corrected final diff: none.
- Runtime/source files changed in corrected final diff: none.
- Packet-only files changed in corrected final diff: `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/packet_planner/state.json`, `THREAD_PACKET.md`.
- Explicit approval note for off-lane packet metadata: the reviewer-required fixer packet instructs this pass to correct inaccurate packet claims and allows handoff-file correction as the source of truth. The remaining `.codex` changes are packet/planner metadata only, not packet planner/tooling source changes, and are included solely as handoff metadata for this corrected A2UI review candidate.

## Runtime Scope Note

The isolated runtime change reviewed at `b929fe6c7a1159c7882acedd247aca31a93cd123` canonicalized materialized A2UI action order and added focused test coverage. Current `main` already contains that behavior in the A2UI contract implementation and tests, so the corrected merge candidate does not reintroduce additional runtime/source changes. `codex_packet_handoff/tools/planner.py` is not changed in this corrected candidate; its `tasks_completed` fallback behavior remains exactly as it exists on the branch and no removal is claimed here. `tests/unit/test_packet_planner.py` is not present in this tree and is not claimed as coverage.

## Commands Run

Required gates for this corrected merge candidate:

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 511 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed; 511 tests passed inside CI.

## Risks / Blockers

- `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json` remain packet/planner metadata changes in the corrected final diff because this sandbox rejects direct writes to `.codex` paths.
- Merge risk is otherwise low for the corrected final diff because all broad source/runtime contamination has been removed from the branch tip.
