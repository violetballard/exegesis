## Thread Handoff Packet

- Branch name: `codex/feat-a2ui-contract`
- Lane: `feat-a2ui-contract`
- Merge target: current `main` (`004285b8b7f046156ea0d391bee6ac629df84e56`)
- Authoritative review target: branch tip `HEAD` against current `main` using `main..HEAD`.
- Merge surface: review the corrected branch-tip diff only; do not use prior mixed-scope packets as the review surface.
- Fixer re-review note: this packet supersedes the rejected packet and is the only handoff surface for this re-review.
- Scope goal: correct the A2UI handoff metadata so the submitted review surface is auditable and aligned with the canonical demo path.
- Canonical demo-path step advanced: `preview and apply or reject a patch`.

## High-Risk / Off-Lane Framing

- Risk reason: the rejected packet mixed contradictory review-surface claims and unsupported packet-planner file claims.
- Budget used for this fixer pass: `4` metadata correction tasks, under the high-risk cap of `4`.
- Approval/scope basis: this corrected packet removes unsupported claims about packet-planner/control-plane maintenance and reverts the remote monitoring, router, launcher, related test, spec, and docs changes from the branch review surface.
- No explicit approval is claimed for remote monitoring, router, launcher, or packet-planner/control-plane maintenance in this A2UI handoff because no such files are part of the corrected branch-tip merge surface.

## Tasks Completed

1. Reverted remote monitoring, router, launcher, related test, spec, and docs changes from this `feat-a2ui-contract` review surface.
2. Regenerated the handoff packet around the corrected branch-tip merge surface.
3. Removed unsupported changed-file claims for non-A2UI packet-planner, remote-monitoring, router, launcher, and related test/spec/docs paths.
4. Set the handoff review target to one corrected branch-tip merge surface: `HEAD` against `main`.

## Files Changed In Review Target

Authoritative branch-tip review target, `main..HEAD`:

- `.codex/kickoff_packets/feat-a2ui-contract.md`
- `.codex/lane_meta/feat-a2ui-contract.json`
- `THREAD_PACKET.md`

No `REMOTE_MONITORING_SPEC.md`, `docs/remote_monitoring/iphone_shortcuts.md`, `codex_packet_handoff/tools/*`, `tests/unit/test_remote_monitor.py`, `client-textual/`, retrieval runtime, daemon source, shared-contract source, `.codex/packet_planner/state.json`, packet-planner source/test, or runtime A2UI file is part of the corrected branch-tip merge surface.

## Shared / Locked Status

- Integrator-locked files changed in branch-tip review target: none.
- Shared-by-approval files changed in branch-tip review target: none.
- A2UI runtime/source files changed in branch-tip review target: none.
- Remote monitoring, router, launcher, packet-planner source/test/state files changed in branch-tip review target: none.
- Packet metadata files changed in branch-tip review target: `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/lane_meta/feat-a2ui-contract.json`, `THREAD_PACKET.md`.

## Review Surface Note

The corrected review target is branch tip `HEAD` against current `main` using `main..HEAD`. The merge surface is metadata-only and consists of `.codex/kickoff_packets/feat-a2ui-contract.md`, `.codex/lane_meta/feat-a2ui-contract.json`, and `THREAD_PACKET.md`. Prior packets that described remote monitoring, router, launcher, related tests/spec/docs, runtime commits, or unsupported packet-planner changes are stale and superseded by this handoff.

## Demo-Path Mapping

This corrected A2UI handoff supports the canonical demo-path step `preview and apply or reject a patch` by making the review evidence for the CLI fallback patch-action contract auditable. It does not add runtime scope beyond the branch-tip metadata correction, and it leaves all non-A2UI remote monitoring and router work outside this lane.

## Commands Run

Required gates for the corrected branch-tip packet:

- Fresh fixer gate run: `2026-05-15` after removing off-lane remote-monitoring and router/tooling paths from the active review surface.
- `make scope-check`: passed; scope-check accepted branch `codex/feat-a2ui-contract`.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 514 tests passed.
- `./typecheck-test.sh`: passed.
- `make ci`: passed; 514 tests passed inside CI.

## Risks / Blockers

- Merge risk is limited to packet and lane metadata because the branch-tip merge surface is metadata-only.
- No remote monitoring source/spec/docs, router source, launcher source, shared contract source, packet-planner state/source/test, Textual file, or runtime A2UI file is in the branch-tip merge surface.
- Fresh required gates are green on the corrected branch-tip packet.
- Remaining risk is that this handoff is metadata-only; it makes review evidence truthful but does not itself add runtime A2UI behavior.
