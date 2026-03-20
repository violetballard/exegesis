# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Verified branch head before this fix commit: `338e5a1e49e331ecab7c476fd4e5b7c68e05a476`
- Branch head note: this tracked packet is part of the submitted fix commit, so the final exact HEAD SHA is reported in the accompanying handoff response to avoid self-referential SHA drift inside the committed file itself.

## Scope goal
- Harden the `diff_preview` command contract so text and JSON responses stay deterministic, verifiable, and ready for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`

## Scope completed
- Corrected `diff_preview` output contracts so JSON and text both flow through the same `QUAL_DIFF_INCLUDE_FINGERPRINT` gate, returning `fingerprint: null` when disabled and the structured fingerprint object when enabled.
- Removed the out-of-lane `scripts/scope-check.sh` policy change from this lane so the submitted branch no longer changes repository scope policy.
- Removed the shared `tests/unit/test_diff_preview.py` delta so the submitted branch stays inside the `feat-commands` ownership boundary.
- Regenerated this handoff packet from the corrected post-fix `codex/integrator...HEAD` branch delta.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The submitted branch delta is 2 files total: one lane-owned command file and this packet.

## Tasks completed (numbered)
1. Updated `src/qual/commands/diff_preview.py` so JSON output follows the same fingerprint gate as text output and returns `fingerprint: null` when disabled.
2. Removed the out-of-lane `scripts/scope-check.sh` policy change from the lane so the submitted branch no longer alters repository ownership enforcement.
3. Removed the shared `tests/unit/test_diff_preview.py` delta so the submitted branch stays inside lane-owned paths only.
4. Regenerated the feature handoff packet so the submitted branch delta, scope statement, and gate outcomes match the corrected branch state.

## Files changed for submitted branch delta
- `THREAD_PACKET.md`
- `src/qual/commands/diff_preview.py`

## Commands run and outcomes
- Validation date: `2026-03-20`
- Gate evidence note: the files listed above are the corrected full `codex/integrator...HEAD` branch delta after this fix commit removes the out-of-lane `scripts/scope-check.sh` edit and shared test-file delta.
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers
- Risk: `LOW`
- Blockers: none
- Note: No routing/provider behavior changed.

## Required handoff fields
### Roadmap item(s) affected
- Milestone 1 - Bootstrap Flow Stabilization: add the targeted `diff_preview` JSON fingerprint contract behavior identified during review.
- Milestone 3 - Product Readiness: define and lock the user-facing `diff_preview` fingerprint contract across text and JSON output.

### Vision capability affected
- Capability 3 - Auditable generation: the command makes fingerprint metadata explicitly optional in both text and JSON formats, avoiding silent metadata leakage when the gate is disabled.
- Capability 4 - Operator-first control surface: `diff_preview` keeps a stable CLI-first/JSON contract by making the disabled fingerprint shape explicit.

### Routing/provider impact note
- None. This change affects local `diff_preview` output formatting only; no routing/provider behavior changed.

## Scope-check / ownership note
- Shared/integrator-locked edits: `NO`
- Shared-file exception note: none
