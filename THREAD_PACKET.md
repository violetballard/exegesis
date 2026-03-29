# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50`
- Reviewed commit(s):
  - `1d07cbfc371f677959d26a60f3140888d8142eb3`
  - `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50`

## Scope goal
- Harden `diff_preview` output contracts so the emitted diff payload, JSON label metadata, summary-only mode, and SHA-256 fingerprint stay deterministic and verifiable for CLI-first operator use, with the approved shared-test exception encoded in the scope gate.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_diff_preview.py`

## Scope completed
- Made the emitted diff string a first-class value in `diff_preview` so the JSON `diff` field and the reported fingerprint are computed from the same exact payload.
- Corrected the JSON `labels.applied` field so it reports whether file labels were actually applied before optional header suppression.
- Added focused regression coverage for labeled JSON output with suppressed headers, plus the existing summary-only fingerprint coverage.
- Updated the scope-check policy so the approved `tests/unit/test_diff_preview.py` exception is recognized for `feat-commands`.
- Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta on the branch.

## Kickoff budget/limits compliance
- High-risk shared-test handoff: task budget `4`, time budget `30m`, size limits `<=8 files` and `<=300 net LOC`.
- The branch delta changes 6 files, centered on the lane-owned `diff_preview` command, one approved shared test, and the minimal scope-gate policy update needed to encode that approval.
- The change stays centered on the command contract itself, the approved regression coverage needed to verify it, and the scope gate that now recognizes the exception.

## Approved exception note
- Approved shared-file exception for `tests/unit/test_diff_preview.py`, with matching scope-gate support in `scripts/scope-check.sh`.

## Tasks completed (numbered)
1. Made the emitted diff string a first-class value in `diff_preview` so the JSON payload and fingerprint are derived from the same exact text.
2. Corrected the JSON `labels.applied` field so it stays truthful when headers are suppressed.
3. Added a regression that covers labeled JSON output with suppressed headers.
4. Updated the scope-check policy so the approved shared test is recognized for `feat-commands`.
5. Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta.

## Files changed
- `.codex/kickoff_packets/feat-commands.md`
- `.codex/lane_meta/feat-commands.json`
- `THREAD_PACKET.md`
- `scripts/scope-check.sh`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- `make scope-check`: FAIL
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `HIGH`
- Blockers: none

## Required handoff fields
### Roadmap item(s) affected
- Milestone 3 - Product readiness: lock the emitted diff fingerprint to the exact user-visible artifact so downstream CLI and automation consumers can verify what the command returned.
- Milestone 2 - Test hardening: add focused regression coverage for the labeled JSON contract path introduced by the command fix.

### Vision capability affected
- 3. Auditable generation - The emitted SHA-256 now verifies the exact diff payload returned by the command, including summary-only behavior.
- 4. Operator-first control surface - CLI remains a first-class surface while exposing a stable command contract and a verifiable JSON shape.

### Routing/provider impact note
- None. This change only affects local diff-preview formatting, fingerprinting, and focused regression coverage; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
