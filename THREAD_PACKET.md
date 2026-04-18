# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: harden the CLI command contract and trusted next-action compatibility contract so command ordering, accepted parser entrypoints, and follow-up compatibility aliases all stay deterministic.
- Risk reason: this slice uses the approved shared-test exception for `tests/unit/test_commands_catalog.py`, so it stays on the high-risk template even though implementation remains command-catalog-only.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Publish the next-action compatibility tables from the command catalog and package exports.
2. Extend tests so the trusted next-action compatibility surface is covered alongside the parser-drift regressions.
3. Regenerate the handoff packet so it reflects one exact implementation anchor instead of the older mixed review basis.
4. Keep the explicit canonical demo-path step mapping required by `AGENTS.md` and rerun the required local gates.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: this fixer pass anchors the implementation in one commit, then regenerates the packet against that exact SHA.
- First green tests: satisfied by the full gate rerun recorded below.
- Before risky/shared file edit: the only shared-file scope remains the approved test exception `tests/unit/test_commands_catalog.py`.
- Ready for handoff: satisfied by this refreshed packet and the full gate rerun recorded below.

## Packet Traceability Note

- Unambiguous review anchor for re-review: `3f4d46e08beea5cc877f5d37cde393eaf8226427`.
- Review basis choice: this packet refresh is metadata only, so re-review should evaluate the exact implementation state captured by `3f4d46e08beea5cc877f5d37cde393eaf8226427`.
- The earlier review anchor `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` is out of scope for this re-review packet.
- Implementation files in scope at that anchor:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Metadata-only handoff files for this fixer refresh:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Reviewer Required Fixes Satisfied

1. Tightened the CLI contract so parser-surface drift is rejected against the declared catalog-backed parser surface, not just against deduplicated canonical names.
2. Exposed the next-action compatibility lookup and invocation tables from the command catalog so the trusted follow-up action contract exports the accepted compatibility surface explicitly.
3. Added regression coverage for next-action compatibility tables plus alias substitution, token reordering, extra entrypoints, removed entrypoints, and normalized alias drift in `tests/unit/test_commands_catalog.py`.
4. Kept the explicit canonical demo-path mapping required by `AGENTS.md`: this work advances the Milestone 3 engine-first step `open project/document`.
5. Regenerated this packet so re-review evaluates one review basis only: implementation anchor `3f4d46e08beea5cc877f5d37cde393eaf8226427`, then re-ran the required gate suite.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Canonical Demo-Path Step Advanced

- Primary Milestone 3 engine-first demo-path step advanced: `open project/document`.
- Why this step: `feat-commands` owns the CLI operator surface that starts the current MVP loop, and the branch’s command-surface contract work keeps that entry step deterministic and smoke-testable while Textual remains disabled.
- Concrete effect: `command_cli_contract()` now preserves canonical command order and rejects parser-surface drift such as alias-for-canonical substitution, token reordering, added entrypoints, or removed expected entrypoints, and the next-action contract now exports compatibility lookups deterministically, so the operator-facing command contract for starting and continuing the workflow cannot silently change.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates the full accepted parser surface against the command catalog and raises `ValueError` if canonical entrypoints, alias entrypoints, or entrypoint order drift.
- Kept the returned contract aligned with the canonical command order by reusing the canonical names tuple instead of rebuilding a divergent list.
- Added explicit next-action compatibility lookup and invocation tables to `src/qual/commands/catalog.py` and re-exported them from `src/qual/commands/__init__.py`.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for canonical-order alignment, parser-surface drift rejection, and the trusted next-action compatibility tables.
- Refreshed the handoff packet so re-review evaluates implementation anchor `3f4d46e08beea5cc877f5d37cde393eaf8226427` with explicit Milestone 3 demo-path alignment.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff stayed within the `4`-task cap, `30m` time budget, and the lane size limits.
- The implementation slice remains limited to two owned command files plus one approved shared test file, with packet metadata refreshed for re-review.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Confirmed the live branch already contains the reviewer-requested parser-surface hardening in `src/qual/commands/catalog.py`.
2. Published the next-action compatibility lookup and invocation tables from the command catalog and package exports.
3. Extended `tests/unit/test_commands_catalog.py` to verify those compatibility tables and keep the existing alias-substitution drift coverage intact.
4. Regenerated the handoff packet so it maps this work explicitly to the Milestone 3 `open project/document` step and uses `3f4d46e08beea5cc877f5d37cde393eaf8226427` as the only review basis.
5. Re-ran the required local gates and recorded outcomes for this fixer pass.

### Files Changed

- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Verification date: `2026-04-18`

### Risks / Blockers

- Risk: `LOW`
- Remaining risk: future parser-surface or next-action compatibility changes still require the catalog exports and command tests to be updated together by design.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: Product Readiness - define and lock user-facing output contracts, specifically the `open project/document` entry step of the engine-first MVP path.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop, specifically the `open project/document` operator entry contract and its next-action compatibility surface.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable and deterministic while Textual stays disabled.
- Auditable state and workflow - the command surface now fails loudly on parser/catalog drift instead of silently changing the operator contract.

### Routing/provider impact note

- None. This change only affects local command-contract validation, next-action compatibility exports, and focused command-catalog test coverage.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - owned implementation paths stay inside `src/qual/commands/**`
  - approved shared test path is `tests/unit/test_commands_catalog.py`
