# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `3dfd014632493cdd66b363c637846596d490e7af`
- Reviewed commit(s):
  - `0df5b4a7adf078c72c7fd93d4ab7730a2655ab05`
  - `4807235db9bc9acc451faa5e1845effdaea9d063`
  - `3dfd014632493cdd66b363c637846596d490e7af`

## Scope goal
- Harden `diff_preview` output contracts so the emitted diff payload, summary-only mode, and SHA-256 fingerprint stay deterministic and verifiable for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_diff_preview.py`

## Scope completed
- Made the emitted diff string a first-class value in `diff_preview` so the JSON `diff` field and the reported fingerprint are computed from the same exact payload.
- Added focused regression coverage for labeled JSON output with suppressed headers, plus the existing summary-only fingerprint coverage.
- Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta on the branch.

## Kickoff budget/limits compliance
- High-risk shared-test handoff: task budget `4`, time budget `30m`, size limits `<=8 files` and `<=300 net LOC`.
- The branch delta changes 5 files, centered on the lane-owned `diff_preview` command and one approved shared test.
- The change stays centered on the command contract itself and the approved regression coverage needed to verify it.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_diff_preview.py`.

## Tasks completed (numbered)
1. Made the emitted diff string a first-class value in `diff_preview` so the JSON payload and fingerprint are derived from the same exact text.
2. Added a regression that covers labeled JSON output with suppressed headers, plus summary-only fingerprint coverage.
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
- Risk: `HIGH`
- Blockers: none

## Required handoff fields
### Scope completed

- Hardened the `diff_preview` command surface so the emitted diff payload, summary-only mode, and SHA-256 fingerprint stay deterministic and verifiable.

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` - lock the emitted diff fingerprint to the exact user-visible artifact so downstream CLI and automation consumers can verify what the command returned.

### Vision capability affected

- `Canonical engine contract` - CLI compatibility remains stable while the command surface exposes a stable command contract and a verifiable JSON shape.
- `Auditable state and workflow` - the emitted SHA-256 now verifies the exact diff payload returned by the command, including summary-only behavior.

### Routing/provider impact note

- None. This change only affects local diff-preview formatting, fingerprinting, and focused regression coverage; no routing/provider files change.

### Proposed README patch text

- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved shared-file exception covers `tests/unit/test_diff_preview.py` only.
