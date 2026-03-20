# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `c08c6e2b018958a479c363fe653a12dfaa56ac98`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract and keep the reviewer-required focused regression coverage so text and JSON responses stay deterministic, auditable, and CLI-first.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Expanded `src/qual/commands/diff_preview.py` so text and JSON output share the same labeled diff, summary, no-diff, and `QUAL_DIFF_INCLUDE_FINGERPRINT` contract behavior.
- Kept the focused regression coverage in `tests/unit/test_diff_preview.py` for JSON fingerprint-disabled output, labeled JSON fingerprint output, stable no-diff JSON payloads, and summary-only fingerprint behavior.
- Regenerated this handoff packet from the actual `codex/integrator...HEAD` branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget and within the file-count/size limits for this fix pass. The submitted branch delta is 3 files total.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so text and JSON output share one explicit contract for labels, no-diff responses, summaries, and gated fingerprints.
2. Restored the focused regression coverage in `tests/unit/test_diff_preview.py` that exercises the reviewer-called-out JSON fingerprint, no-diff JSON, and custom-label cases.
3. Regenerated `THREAD_PACKET.md` so the handoff fields now match the submitted `codex/integrator...HEAD` delta exactly.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- `make scope-check`: pending
- `./quality-format.sh --check`: pending
- `./quality-lint.sh`: pending
- `./quality-test.sh`: pending
- `./typecheck-test.sh`: pending
- `make ci`: pending

## Risks / blockers
- Risk: `LOW`
- Blockers: none
- Note: No routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: harden `diff_preview` command behavior and keep the CLI-facing diff contract stable.
- Milestone 2 - Test Hardening: add the focused regression coverage for JSON fingerprint, no-diff JSON, summary-only fingerprint, and custom-label cases identified during review.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` output contract for text and JSON consumers.

### Vision capability affected
- Capability 3 - Auditable generation: `diff_preview` exposes an explicit, gated fingerprint contract instead of implicit metadata behavior.
- Capability 4 - Operator-first control surface: the command keeps deterministic text and JSON output that remains suitable for CLI-first use and downstream structured consumers.

### Routing/provider impact note
- None. This change is limited to `diff_preview` command output behavior and its focused regression coverage.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
- Approved exception note: `tests/unit/test_diff_preview.py` is intentionally included as a reviewer-required shared regression test for the submitted `diff_preview` contract change.
