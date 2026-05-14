## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Handoff type: corrected packet requesting full branch-tip review.
- Authoritative reviewed runtime commit: `b929fe6c7a1159c7882acedd247aca31a93cd123` (`fix(a2ui): canonicalize materialized action order`).
- Review scope correction: prior packets claimed the submitted branch tip was a narrow A2UI runtime slice plus metadata-only follow-up commits. That is not accurate. Because this fixer is not allowed to detach or update refs, this packet explicitly requests review of the full final branch-tip merge range instead of claiming a metadata-only or two-file runtime slice.

## Tasks Completed

1. Preserved the intended A2UI runtime change from `b929fe6c7a1159c7882acedd247aca31a93cd123`: supported actions filtered by the allowlist are sorted by canonical JSON before materialization.
2. Preserved focused unit coverage for deterministic canonical action ordering in `tests/unit/test_a2ui_contract.py`.
3. Replaced the stale/inaccurate handoff packet so the review request no longer claims that later branch-tip commits are metadata-only.

## Files Changed / Review Surface

The intended A2UI runtime slice is:

The actual source-bearing merge candidate for this branch is:

Packet-only handoff correction:

- `THREAD_PACKET.md`

The full branch-tip merge range also contains off-scope `client-textual/`, retrieval, daemon/tooling, broad docs, packet metadata, and shared-contract files from earlier commits. This packet does not claim those are metadata-only; it requests full branch-tip review if the branch is not split or rewritten by the integrator.

## Shared / Locked Status

- Integrator-locked files: full branch-tip review required; not limited to the intended A2UI runtime slice.
- Shared-by-approval files: full branch-tip review required; not limited to the intended A2UI runtime slice.
- Runtime files intentionally in the A2UI scope: `src/qual/ui/a2ui.py`.
- Tests intentionally in the A2UI scope: `tests/unit/test_a2ui_contract.py`.

## Commands Run

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 123 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed.

## Risks / Blockers

- Branch history still contains stale off-scope commits because the packet explicitly forbids detaching or updating refs. This packet corrects the review request by asking for full branch-tip review rather than a narrowed metadata-only review.
- Merge risk remains high unless the integrator splits or rewrites the branch down to the intended A2UI runtime slice.
