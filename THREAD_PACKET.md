## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main` (`004285b8b7f046156ea0d391bee6ac629df84e56`)
- Authoritative review target: branch tip `HEAD` against current `main` using `main..HEAD`.
- Merge surface: review the branch-tip diff only; do not use prior mixed-scope packets as the review surface.
- Fixer re-review note: this packet supersedes the rejected packet and is the only handoff surface for this re-review.
- Scope goal: correct the A2UI handoff metadata so the submitted review surface is auditable and aligned with the canonical demo path.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

## High-Risk / Off-Lane Framing

- Risk reason: the rejected packet mixed contradictory review-surface claims and unsupported packet-planner file claims.
- Budget used for this fixer pass: `4` metadata correction tasks, under the high-risk cap of `4`.
- Approval/scope basis: this corrected packet removes unsupported claims about `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`, and `.codex/packet_planner/state.json`.
- No explicit approval is claimed for packet-planner/control-plane maintenance in this A2UI handoff because no such files are part of the branch-tip merge surface.

## Tasks Completed

1. Regenerated the handoff packet around the actual branch-tip merge surface.
2. Removed unsupported changed-file claims for `codex_packet_handoff/tools/planner.py` and `tests/unit/test_packet_planner.py`.
3. Set the handoff review target to one branch-tip merge surface: `HEAD` against `main`.
4. Added the explicit canonical demo-path step advanced: `preview and apply or reject a patch`.

## Files Changed In Review Target

Authoritative branch-tip review target, `main..HEAD`:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `THREAD_PACKET.md`

No `client-textual/`, retrieval runtime, daemon source, shared-contract source, `.codex/packet_planner/state.json`, `codex_packet_handoff/tools/planner.py`, `tests/unit/test_lane_profiles.py`, or `tests/unit/test_packet_planner.py` are part of the branch-tip merge surface.

## Shared / Locked Status

- Integrator-locked files changed in branch-tip review target: none.
- Shared-by-approval files changed in branch-tip review target: none.
- A2UI runtime/source files changed in branch-tip review target: none.
- Packet-planner source/test/state files changed in branch-tip review target: none.
- Packet-only files changed in branch-tip review target: `.codex/kickoff_packets/feat-a2ui-contract.md`, `THREAD_PACKET.md`.

## Review Surface Note

The corrected review target is branch tip `HEAD` against current `main` using `main..HEAD`. The merge surface is metadata-only and consists of `.codex/kickoff_packets/feat-a2ui-contract.md` and `THREAD_PACKET.md`. Prior packets that described a separate runtime commit or unsupported packet-planner changes are stale and superseded by this handoff.

## Demo-Path Mapping

This corrected A2UI handoff supports the canonical demo-path step `preview and apply or reject a patch` by making the review evidence for the CLI fallback patch-action contract auditable. It does not add new runtime scope beyond the branch-tip metadata correction.

## Commands Run

Required gates for the corrected branch-tip packet:

- Fresh fixer gate run: `2026-05-14` after correcting the branch-tip review surface.
- `make scope-check`: passed; scope-check accepted branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 511 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed; 511 tests passed inside CI.

## Risks / Blockers

- Merge risk is limited to packet metadata because the branch-tip merge surface is packet-only.
- No router source, shared contract source, packet-planner state/source/test, Textual file, or runtime A2UI file is in the branch-tip merge surface.
- Fresh required gates are green on the corrected branch-tip packet.
- Control-plane lane metadata has been corrected so regenerated review packets use this narrowed branch-tip surface.
