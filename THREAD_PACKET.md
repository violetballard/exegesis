# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `2afa0f7f2f23c2d73773cc9c5a2fc0007ba19be3`

## Scope goal
- Harden `diff_preview` output contracts so the emitted diff payload, summary-only mode, and SHA-256 fingerprint stay deterministic and verifiable for CLI-first operator use.

## Lane/owned paths
- `src/qual/commands/**`
- Approved shared tests:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Shared policy support:
  - `scripts/scope-check.sh`

## Scope completed
- Extended the command catalog exports and canonicalization helpers so the `feat-commands` surface stays internally consistent.
- Made the emitted diff string a first-class value in `diff_preview` so the JSON `diff` field and the reported fingerprint are computed from the same exact payload.
- Added focused regression coverage for command catalog contracts and text summary-only fingerprinting so the reviewed shared tests remain verifiable.
- Restored the scope-check policy allowance for the approved shared command regressions so the branch gates accept the reviewed shared tests.
- Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta on the branch.

## Kickoff budget/limits compliance
- Stayed within the default lane budget. The branch delta changes 10 files, centered on the lane-owned command surface, two approved shared tests, and the matching scope-check policy allowance.
- The change stays centered on the command contract itself and the approved regression coverage needed to verify it.

## Approved exception note
- Approved shared-file exceptions for `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`; matching scope-check policy allowance restored in `scripts/scope-check.sh`.

## Tasks completed (numbered)
1. Made the emitted diff string a first-class value in `diff_preview` so the JSON payload and fingerprint are derived from the same emitted text.
2. Added regression coverage for the command catalog surface and text summary-only fingerprinting so the reviewed shared tests remain verifiable.
3. Restored the scope-check policy allowance for the approved shared command regressions so the branch gates accept the reviewed shared tests.
4. Regenerated the handoff packet and lane metadata so the review evidence matches the actual code/test delta.

## Files changed
- `.codex/kickoff_packets/feat-commands.md`
- `.codex/lane_meta/feat-commands.json`
- `THREAD_PACKET.md`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `scripts/scope-check.sh`
- `tests/unit/test_commands_catalog.py`
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
- Milestone 3 - Product Readiness (Planned): define and lock user-facing output contracts, including the command output and fingerprint behavior that downstream CLI and automation consumers verify.

### Vision capability affected
- 3. Auditable generation - The emitted SHA-256 now verifies the exact diff payload returned by the command, including summary-only behavior.
- 4. Operator-first control surface - CLI remains a first-class surface while exposing a stable command contract and a verifiable JSON shape.

### Routing/provider impact note
- None. This change only affects local diff-preview formatting, fingerprinting, focused regression coverage, and the matching branch scope policy for the approved shared test; no routing/provider files change.

### Proposed README patch text
- None.

## Scope-check / ownership note
- Shared/integrator-locked edits: `YES`
