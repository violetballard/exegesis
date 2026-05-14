## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main`
- Selected integration target: current branch tip after this fixer commit, reviewed as a metadata-only correction.
- Target type: metadata-only resubmission; no runtime, shell, planner, packet-planner, or unit-test changes are requested for this target.
- Scope completed: high-risk-compliant metadata handoff correction only, limited to the current `main...HEAD` packet/planner metadata diff and capped at 4 tasks.
- Fixer verification: gates re-run on 2026-05-14 after confirming the selected target remains metadata-only.
- Canonical demo-path step protected by this correction: `preview and apply or reject a patch`, by making the handoff packet accurately describe the reviewed branch diff.
- Required-fix mapping: this packet removes planner/test claims and limits `Tasks completed`, `Files changed`, and gate reporting to the selected metadata-only target.
- Roadmap mapping: `ROADMAP.md` Milestone 3, specifically `move A2UI contracts into shared while keeping renderers outside shared`.
- Product-vision mapping: `PRODUCT_VISION.md` capability 4, `Shared UI contract (A2UI)`, where cards/actions/selection types live in a client-agnostic shared layer and rendering adapters stay outside shared.
- Budget accounting: high-risk packet, capped at `4` completed tasks because residual `.codex` metadata is present in the reviewed branch diff.

## Required Fixes Applied

1. Rewrote `Tasks completed` and `Files changed` to match the selected metadata-only target.
2. Removed planner and packet-planner source/test claims from this handoff. `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py` are not part of this reviewed target.
3. Stated that runtime A2UI work from `b929fe6c7a1159c7882acedd247aca31a93cd123` is not the selected integration target for this re-review.
4. Re-ran and reported the required handoff gates for the corrected metadata-only target.

## Files Changed

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/packet_planner/state.json`
- `THREAD_PACKET.md`

The `.codex` paths are metadata deltas already present in the reviewed `main...HEAD` diff. This target does not request planner/runtime/test review.

## Explicitly Not In This Handoff

- No runtime A2UI source changes.
- No `src/qual/ui/a2ui.py` changes in the selected metadata-only target.
- No `tests/unit/test_a2ui_contract.py` changes in the selected metadata-only target.
- No shell changes.
- No planner or packet-planner source changes.
- No `tests/unit/test_packet_planner.py` claims.

## Tasks Completed

1. Corrected the review packet so the selected target is the metadata-only branch diff currently visible in `main...HEAD`. Canonical demo-path step: `preview and apply or reject a patch`.
2. Removed source/test maintenance claims for planner and packet-planner files that are not present in the reviewed target. Canonical demo-path step: `preview and apply or reject a patch`.
3. Clarified that the runtime A2UI commit `b929fe6c7a1159c7882acedd247aca31a93cd123` is not being submitted as this selected target. Canonical demo-path step: `preview and apply or reject a patch`.
4. Ran the required gates after the handoff packet correction. Canonical demo-path step: `preview and apply or reject a patch`.

This work now makes the canonical demo-path step `preview and apply or reject a patch` more real by keeping the A2UI contract handoff trace accurate for re-review.

## Commands Run And Outcomes

- `git status --short --branch`: PASS; branch `codex/feat-a2ui-contract`.
- `git diff --name-status main...HEAD`: PASS; selected metadata-only target contains `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/packet_planner/state.json`, and `THREAD_PACKET.md`.
- `git show --name-status --oneline --no-renames b929fe6c7a1159c7882acedd247aca31a93cd123`: PASS; confirmed the runtime A2UI commit touched only `src/qual/ui/a2ui.py` and `tests/unit/test_a2ui_contract.py`, but that commit is not the selected target for this metadata-only re-review.
- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; smoke passed and 511 unit tests passed.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS; scope, format, lint, typecheck, smoke, and 511 unit tests passed.

## Risks / Blockers

- Runtime behavior risk: low. This fixer commit only corrects handoff metadata.
- Integration risk: medium. The selected target is metadata-only and intentionally excludes the runtime A2UI source/test commit referenced by the reviewer.
