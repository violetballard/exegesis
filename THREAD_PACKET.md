# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Implementation commit range: `8c9e2290fefb92bb07ff99681421a666cbbe4e0f..177e04efcc51b2ee95015ce2096ff0be49caa820`
- Key implementation tip commits:
  - `8c9e2290fefb92bb07ff99681421a666cbbe4e0f` (`feat(commands): stabilize command catalog contracts`)
  - `4c5bc538bd2d5325ce198183d31d6bc3c2d63c68` (`Fix diff preview summary fingerprint contract`)
  - `cb93dafa2c451893778b1c7f0c2e23f16090d8b5` (`feat(commands): harden demo path contract`)
  - `621dc00a194f79ae52611d240a8521853cd374e2` (`fix(commands): reject parser surface drift`)
  - `177e04efcc51b2ee95015ce2096ff0be49caa820` (`Tighten single-token command resolution`)
- Prior command-catalog anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Docs-only alignment commits after the implementation tip: none

## Packet Traceability Note

- This re-review packet is scoped to the full current command-surface implementation on the branch tip through `177e04efcc51b2ee95015ce2096ff0be49caa820`.
- The earlier narrow packet that treated later commits as metadata-only was inaccurate: substantive command-surface changes landed after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, including trusted demo-path contract helpers, demo/MVP entrypoint wrappers, and the parser-surface drift rejection finalized in `621dc00a194f79ae52611d240a8521853cd374e2`.
- The implementation under review is therefore the full code-bearing command-surface range from `8c9e2290fefb92bb07ff99681421a666cbbe4e0f` through `177e04efcc51b2ee95015ce2096ff0be49caa820`, plus this packet refresh.
- Reviewer-fix follow-up on the current branch tip tightens the default catalog contract further by requiring canonical commands to remain the primary parser entrypoints in canonical order, preserving deterministic single-token command resolution, and carrying regression coverage for canonical-token removal, alias substitution, and parser-order drift.
- This packet refresh explicitly satisfies the reviewer-requested `AGENTS.md` demo-path mapping requirement and keeps the new fixer change scoped to handoff metadata only.

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
- Scope-tightening note: this packet is limited to deterministic canonical command ordering, parser/catalog drift detection, parser-surface validation, and the existing CLI compatibility helpers already present on this branch tip. It does not claim new commands, new flags, new aliases, broader CLI-surface expansion, or engine behavior changes.

## Canonical Demo-Path Mapping

- Explicit canonical demo-path step advanced by this lane: `open project/document`.
- Operator-surface note: this change also strengthens stable command execution across the rest of the CLI-first loop while Textual remains disabled, but its most direct canonical demo-path contribution is the `open project/document` entry step.
- This change makes the CLI-first `open project/document` step more real by keeping the operator-facing command contract deterministic, validating parser/catalog drift instead of silently accepting it, and preserving stable command resolution for the existing CLI fallback.
- Concrete blocker removed: the command surface now rejects parser/catalog mismatches before they can silently change the operator entry contract, which keeps the existing CLI entry step deterministic enough for smoke checks while Textual remains disabled.
- Milestone 3 scope-tightening note: this is a direct enabler for the CLI-first engine loop because the MVP cannot reliably enter the existing `open project/document` step if parser drift can silently rewrite the accepted command surface; it is not a general CLI cleanup, UX expansion, or new-command effort.

## Definition Of Done Alignment

- Core engine actions remain reachable through stable commands.
- Command behavior remains deterministic and smoke-testable.
- Compatibility with the canonical engine contract is preserved while UI lanes stay disabled.
- Command handlers remain thin and delegate real behavior to engine code.

## Lane / Ownership

- Owned runtime paths: `src/qual/commands/**`
- Approved shared-test path:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Shared/integrator-locked edits: `YES`
- Shared edits are limited to the approved `feat-commands` shared-test paths listed above.
- Approval basis: the reviewer packet for this branch explicitly includes `Approved exception note - Approved shared-test exception for tests/unit/test_commands_catalog.py`, and `scripts/scope-check.sh` allowlists that exact path for `codex/feat-commands*`. The branch-tip implementation kept the reviewer-fix packet's shared command-test scope explicit and auditable.

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the default catalog requires canonical commands to remain the primary parser entrypoints in canonical order, and now raises `ValueError` if canonical CLI tokens are dropped, aliases are substituted ahead of the canonical token, or parser token order drifts from the catalog contract.
- Added deterministic parser-surface helpers for CLI shims, parser-ready argv rewriting, smoke invocations, trusted demo-path routing, and command resolution so the existing CLI-first MVP loop stays stable and smoke-testable.
- Exposed the public command exports needed for the command catalog, canonical wrapper, demo/MVP helper entrypoints, and smoke/resolution contracts from `src/qual/commands/__init__.py` and `src/qual/commands/canonical.py`.
- Tightened `src/qual/commands/diff_preview.py` so summary-only output keeps a fingerprint tied to the reviewed diff and truncation remains bounded without corrupting the header-aware preview contract.
- Expanded `tests/unit/test_commands_catalog.py` with focused regression coverage for canonical-order alignment, parser drift rejection, canonical-token removal, alias-substitution rejection, shim/surface contracts, smoke argv helpers, deterministic resolution, and demo/MVP path helpers.
- Finalized parser-surface drift rejection in `621dc00a194f79ae52611d240a8521853cd374e2` and tightened single-token command resolution in `177e04efcc51b2ee95015ce2096ff0be49caa820` so re-review targets the real branch-tip implementation instead of the earlier incorrect metadata-only framing.
- Regenerated the handoff packet so re-review targets the real implementation tip and records the explicit demo-path mapping and shared-test approval basis requested by the reviewer.

## Tasks Completed

1. Hardened the command catalog and demo-path contracts so parser drift, parser token order, canonical ordering, and trusted route metadata stay deterministic for the CLI-first MVP loop.
2. Added parser-surface, shim argv, smoke argv, and deterministic command-resolution helpers needed by the compatibility surface.
3. Published the public command exports and tightened diff-preview summary behavior so the existing CLI entrypoints stay stable and smoke-testable.
4. Finalized parser-surface drift rejection at the branch tip and corrected the handoff packet so re-review targets the real implementation tip and exact merge scope.

## Task-To-Demo-Path Mapping

1. Task 1 advances `open project/document` by keeping the trusted CLI entry contract deterministic and by rejecting parser/catalog drift, alias substitution, or parser token reordering before the operator entry step can silently change.
2. Task 2 advances `open project/document`, `promote or gather context into the basket`, and `preview and apply or reject a patch` by keeping the existing CLI compatibility wrappers and argv rewriting deterministic across the current engine-first loop.
3. Task 3 advances `open project/document` and `preview and apply or reject a patch` by keeping the published command entrypoints stable and by preserving a smoke-testable diff preview contract for the existing CLI fallback.
4. Task 4 advances `continue working without losing context` from an operator-contract perspective by keeping the reviewed command surface auditable, re-reviewable, and traceable to the real branch tip rather than an incorrect metadata-only slice.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: this packet groups the branch-tip work into `4` meaningful tasks, which matches the high-risk task cap for the actual implementation scope under review.
- Current implementation scope remains within owned command paths plus the approved shared test files.
- Files changed in implementation scope: `6`
- Implementation review target range: `8c9e2290fefb92bb07ff99681421a666cbbe4e0f..177e04efcc51b2ee95015ce2096ff0be49caa820`

## Files Changed

### Reviewed implementation files

- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Metadata-only handoff file

- `THREAD_PACKET.md`

## Commands Run With Results

- `python -m unittest tests.unit.test_commands_catalog tests.unit.test_diff_preview -q`: PASS
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

- `Milestone 3: Real workflow loop` by making the CLI-first `open project/document` entry step deterministic while the package/layout migration lands.
- `feat-commands` by keeping the existing migration-safe CLI entrypoints deterministic, smoke-testable, and aligned with the engine-first MVP loop.

### Vision capability affected

- `Canonical engine contract` because the CLI compatibility surface for `open project/document` remains stable while Textual stays disabled.

### Routing/provider impact note

- None. This change only affects local command-contract validation, command-surface helpers, diff-preview stability, and focused command-catalog test coverage.

### Proposed README.md patch text

- None.
