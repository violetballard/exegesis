# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Review target: `f85970321a39c5d2151a72143ce740fdfbfeb69f`
- Prior command-catalog anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`

## Packet Traceability Note

- This re-review packet is scoped to the current command-surface implementation at `f85970321a39c5d2151a72143ce740fdfbfeb69f`.
- The earlier narrow packet that treated later commits as metadata-only was inaccurate: substantive command-surface changes landed after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, including trusted demo-path contract helpers and demo/MVP entrypoint wrappers.
- This packet refresh is docs-only and does not change the implementation scope described below.
- This packet refresh explicitly satisfies the reviewer-requested `AGENTS.md` demo-path mapping requirement and keeps the fix scoped to packet metadata only.

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the existing Milestone 3 CLI command contract for the current engine-first MVP loop so the command surface stays deterministic, smoke-testable, and aligned with the canonical command catalog.
- Scope-tightening note: this packet is limited to deterministic canonical command ordering, parser/catalog drift detection, and the existing CLI compatibility helpers already present on this branch tip. It does not claim new commands, new flags, new aliases, broader CLI-surface expansion, or engine behavior changes.

## Canonical Demo-Path Mapping

- Explicit canonical demo-path step advanced by this lane: `open project/document`.
- Operator-surface note: this change also strengthens stable command execution across the rest of the CLI-first loop while Textual remains disabled, but its most direct canonical demo-path contribution is the `open project/document` entry step.
- This change makes the CLI-first `open project/document` step more real by keeping the operator-facing command contract deterministic, validating parser/catalog drift instead of silently accepting it, and preserving stable command resolution for the existing CLI fallback.
- Concrete blocker removed: the command surface now rejects parser/catalog mismatches before they can silently change the operator entry contract, which keeps the existing CLI entry step deterministic enough for smoke checks while Textual remains disabled.

## Definition Of Done Alignment

- Core engine actions remain reachable through stable commands.
- Command behavior remains deterministic and smoke-testable.
- Compatibility with the canonical engine contract is preserved while UI lanes stay disabled.
- Command handlers remain thin and delegate real behavior to engine code.

## Lane / Ownership

- Owned runtime paths: `src/qual/commands/**`
- Approved shared-test path:
  - `tests/unit/test_commands_catalog.py`
- Shared/integrator-locked edits: `YES`
- Shared edits are limited to the approved `feat-commands` shared-test path listed above.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it compares CLI canonical names against `command_names()` and raises `ValueError` if the parser surface drifts from the catalog.
- Added deterministic parser-surface helpers for CLI shims, parser-ready argv rewriting, smoke invocations, trusted demo-path routing, and command resolution so the existing CLI-first MVP loop stays stable and smoke-testable.
- Exposed the public command exports needed for the command catalog, canonical wrapper, demo/MVP helper entrypoints, and smoke/resolution contracts from `src/qual/commands/__init__.py` and `src/qual/commands/canonical.py`.
- Tightened `src/qual/commands/diff_preview.py` so summary-only output keeps a fingerprint tied to the reviewed diff and truncation remains bounded without corrupting the header-aware preview contract.
- Expanded `tests/unit/test_commands_catalog.py` with focused regression coverage for canonical-order alignment, parser drift rejection, shim/surface contracts, smoke argv helpers, deterministic resolution, and demo/MVP path helpers.
- Regenerated the handoff packet so re-review targets the real implementation tip instead of the earlier incorrect metadata-only framing.

## Tasks Completed

1. Hardened the command-catalog contract to reject parser drift and preserve canonical command ordering.
2. Added deterministic parser-surface, shim, smoke, and resolution helpers for the CLI-first MVP command path.
3. Published trusted demo/MVP command-path helpers and public exports needed by the compatibility surface.
4. Tightened diff-preview truncation and fingerprint behavior to keep patch-review output stable.
5. Added and updated focused regression coverage in `tests/unit/test_commands_catalog.py` for the expanded command-surface contract.
6. Corrected the handoff packet so review scope and demo-path mapping match the actual branch tip.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the `4`-task cap for the original narrow command-catalog slice, but the current branch tip now carries a broader command-surface implementation.
- Current implementation scope remains within owned command paths plus the approved shared test file.
- Files changed in implementation scope: `5`

## Files Changed

### Reviewed implementation files

- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff file

- `THREAD_PACKET.md`

## Commands Run With Results

- `python -m unittest tests.unit.test_commands_catalog -q`: PASS
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Residual risk: medium; this branch tip is larger than the original `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` catalog-only slice, so re-review should evaluate the full command-surface contract listed above.
- Scope note: this is command-surface validation and compatibility work for the existing CLI loop, not a broader workflow-engine or audit-capability change.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` by preserving CLI compatibility while the package/layout migration lands.
- `feat-commands` by keeping the existing migration-safe CLI entrypoints deterministic, smoke-testable, and aligned with the engine-first MVP loop.

### Vision capability affected

- `Canonical engine contract` because the CLI compatibility surface remains stable while Textual stays disabled.

### Routing/provider impact note

- None. This change only affects local command-contract validation, command-surface helpers, diff-preview stability, and focused command-catalog test coverage.

### Proposed README.md patch text

- None.
