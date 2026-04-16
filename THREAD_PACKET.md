# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Review target: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: `reviewer-fix packet refresh`

## Review Basis

- This packet is intentionally narrowed to the command-catalog implementation at `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Treat later packet-refresh commits on this branch as metadata-only unless a future handoff packet says otherwise.
- This refresh exists only to satisfy the reviewer-requested AGENTS plan-alignment fix; it does not widen implementation scope and it does not claim any new code changes.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses canonical command order, and fails fast if the parser surface drifts from the command catalog.
- Exact canonical demo-path step advanced by this slice: `preview and apply or reject a patch`.
- Concrete blocker removed for that step: the live `diff-preview` / `patch-review` CLI contract can no longer silently drift from the catalog through parser/catalog mismatch.

## Canonical Demo-Path Step Advanced

- Primary step advanced: `preview and apply or reject a patch`
- Required explicit handoff mapping: this packet exists to state directly that the command-catalog slice strengthens the current CLI `patch-review` step of the canonical demo path.
- Why this is first-order MVP work: the active CLI-first MVP still relies on the `diff-preview` command surface for the patch-review step, so deterministic catalog-backed ordering and fast drift rejection keep that operator contract stable while Textual remains disabled.
- Scope control: this slice does not add new workflow behavior; it only hardens the existing CLI compatibility contract for the active patch-review step.

## Lane / Ownership

- Owned runtime path: `src/qual/commands/**`
- Approved shared-test exception: `tests/unit/test_commands_catalog.py`
- No integrator-locked implementation files were edited.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Kept the returned CLI contract aligned with canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment and drift rejection.
- Tied this scope explicitly to the `preview and apply or reject a patch` demo-path step so the Milestone 3 plan alignment is explicit rather than inferred.

## Files Changed

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD_PACKET.md`

## Tasks Completed

1. Hardened `command_cli_contract()` so the active `patch-review` CLI surface fails fast on parser/catalog drift.
2. Preserved canonical command ordering in the CLI contract for the live `preview and apply or reject a patch` step.
3. Added regression coverage for canonical-order alignment and drift rejection in the approved shared test file.
4. Refreshed the handoff packet so the scope completed/tasks completed sections explicitly map this slice to the canonical `preview and apply or reject a patch` step.

## Kickoff Budget / Limits Compliance

- High-risk/shared-file template applies because of the approved shared test edit in `tests/unit/test_commands_catalog.py`.
- This handoff stays within the `4`-task cap for the implementation slice under review.
- Runtime edits stay within lane-owned paths; the only non-owned implementation file is the approved shared test above.

## Commands Run With Results

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Residual risk: low. Runtime behavior remains confined to the command catalog plus focused regression coverage for the approved shared test path.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` because this keeps the CLI `patch-review` step deterministic while the package/layout migration lands.
- `feat-commands` because this hardens the stable CLI command surface for the engine-first MVP loop.
- Exact demo-path mapping: this slice makes `preview and apply or reject a patch` more real by keeping the `diff-preview` contract stable and drift-resistant.

### Vision capability affected

- `Canonical engine contract` because the active CLI compatibility surface remains stable and deterministic while Textual stays disabled.
- `Auditable state and workflow` because parser/catalog drift now fails loudly instead of silently mutating the operator-facing patch-review contract.

### Routing/provider impact note

- None. This change only affects local command-catalog validation and focused command-catalog test coverage.

### Proposed README.md patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Shared edit is limited to the approved test exception `tests/unit/test_commands_catalog.py`.
