# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`

## Scope goal
- Harden `diff_preview` output contracts so the emitted diff payload, summary-only mode, and SHA-256 fingerprint stay deterministic and verifiable for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_diff_preview.py`

## Scope completed
- Made the emitted diff string a first-class value in `diff_preview` so the JSON `diff` field and the reported fingerprint are computed from the same exact payload.
- Added focused regression coverage for text summary-only fingerprinting so the empty emitted payload remains verifiable.
- Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta on the branch.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta changes 5 files, centered on the lane-owned `diff_preview` command and one approved shared test.
- The change stays centered on the command contract itself and the approved regression coverage needed to verify it.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_diff_preview.py`.

## Tasks completed (numbered)
1. Made the emitted diff string a first-class value in `diff_preview` so the JSON payload and fingerprint are derived from the same emitted text.
2. Added a regression that covers text summary-only fingerprinting against the empty emitted diff payload.
3. Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta.

## Files changed
- `.codex/kickoff_packets/feat-commands.md`
- `.codex/lane_meta/feat-commands.json`
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 3 - Product readiness: lock the emitted diff fingerprint to the exact user-visible artifact so downstream CLI and automation consumers can verify what the command returned.

### Vision capability affected
- 3. Auditable generation - The emitted SHA-256 now verifies the exact diff payload returned by the command, including summary-only behavior.
- 4. Operator-first control surface - CLI remains a first-class surface while exposing a stable command contract and a verifiable JSON shape.

### Routing/provider impact note
- None. This change only affects local diff-preview formatting, fingerprinting, and focused regression coverage; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
