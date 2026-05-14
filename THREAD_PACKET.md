## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main` (`9abf31c55f420be74389af72b7e4707bb5132790`)
- Corrected candidate: final branch tip after this fixer commit.
- Scope goal: remove off-scope branch-tip contamination and resubmit a traceable A2UI contract handoff.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

## Tasks Completed

1. Restored the corrected candidate content to match `main` for unrelated Textual, retrieval, daemon/tooling, docs, shared-contract, planner, and broad source paths.
2. Verified the intended A2UI action canonicalization behavior is already present in the corrected `main` target baseline.
3. Updated this handoff packet so the files changed, shared/locked status, tasks, risks, and command outcomes describe the exact corrected merge candidate.

## Files Changed In Corrected Merge Diff

Expected final diff against current `main`:

- `THREAD_PACKET.md`

No `client-textual/`, retrieval, daemon/tooling, broad docs, planner metadata, or shared-contract files are intentionally included in the corrected final merge diff.

## Shared / Locked Status

- Integrator-locked files changed in corrected final diff: none.
- Shared-by-approval files changed in corrected final diff: none.
- Runtime/source files changed in corrected final diff: none.
- Packet-only files changed in corrected final diff: `THREAD_PACKET.md`.

## Runtime Scope Note

The isolated runtime change reviewed at `b929fe6c7a1159c7882acedd247aca31a93cd123` canonicalized materialized A2UI action order and added focused test coverage. Current `main` already contains that behavior in the A2UI contract implementation and tests, so the corrected merge candidate does not reintroduce additional runtime/source changes. The branch-tip correction is packet-only relative to current `main`.

## Commands Run

Required gates for this corrected merge candidate:

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 511 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed; 511 tests passed inside CI.

## Risks / Blockers

- `.codex/kickoff_packets/feat-a2ui-contract.md` and `.codex/packet_planner/state.json` still differ from current `main`; this sandbox rejects direct writes to `.codex` paths, so those metadata differences could not be restored here.
- Merge risk is otherwise low for the corrected final diff because all broad source/runtime contamination has been removed from the branch tip.
