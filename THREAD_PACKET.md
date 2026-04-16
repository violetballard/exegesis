# Thread Handoff Packet

- Branch name: `codex/feat-commands`
- Review target: `9bdddce9308d84fbbe6cee989fc3f45c5dcfe992`
- Packet refresh role: `reviewer-fix traceability refresh`

## Review Basis

- This packet reviews the actual current branch tip at `9bdddce9308d84fbbe6cee989fc3f45c5dcfe992`.
- The implementation under review is the validator hardening in `src/qual/commands/catalog.py` plus the matching regression coverage in `tests/unit/test_commands_catalog.py`.
- This packet refresh commit is metadata-only and exists to align review traceability, scope wording, and handoff fields to that real implementation tip.
- Reviewer-required packet fix addressed here: the handoff now names the exact canonical demo-path step it advances and explains the concrete blocker removed for that step.

## Reviewer Fixes Addressed

- Required fix 1: `command_cli_contract()` now rejects parser-surface drift, not just canonical-name drift, by validating declared CLI entrypoints and their order against the catalog-backed parser surface.
- Required fix 2: `tests/unit/test_commands_catalog.py` now covers parser-surface drift that preserves canonical coverage, including alias substitution and token reordering failure cases.
- Required fix 3: this packet explicitly maps the work to the canonical demo-path step `preview and apply or reject a patch` and names the concrete blocker removed for that step.

## Scope Goal

- Harden the CLI command contract so the parser-facing command surfaces remain deterministic, preserve canonical catalog order, and fail fast when derived CLI contracts drift from the catalog-backed source of truth.
- Exact canonical demo-path step advanced by this slice: `preview and apply or reject a patch`.
- Concrete blocker removed for that step: the live `diff-preview` and `patch-review` CLI contract projections now reject mismatched flow, surface, and shim data before the patch-review operator surface can drift silently.

## Canonical Demo-Path Step Advanced

- Primary step advanced: `preview and apply or reject a patch`
- Required explicit handoff mapping: this slice hardens the current CLI `patch-review` surface used by the canonical demo path while Textual remains disabled.
- Why this is first-order MVP work: the engine-first MVP still relies on deterministic `diff-preview` command routing and smokeable CLI shims for the patch-review step, so validator-backed contract checks keep that operator surface stable.
- Scope control: this slice does not add new workflow behavior; it only tightens validation around the existing CLI compatibility contracts that expose the patch-review step.

## Lane / Ownership

- Owned runtime path: `src/qual/commands/**`
- Approved shared-test path: `tests/unit/test_commands_catalog.py`
- No integrator-locked implementation files were edited.

## Scope Completed

- Hardened `command_cli_flow_contract()` so it validates parser-token to canonical-command and flow-step projections against the catalog-backed CLI contract.
- Hardened `command_cli_surface_contract()` so it rejects inconsistent parser-surface entries instead of returning silently divergent surface metadata.
- Hardened `command_cli_shim_contract()` so it validates shim entries, the shim lookup table, and the primary invocation table before exposing the compatibility shim contract.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for the new flow, surface, and shim validator failure modes.
- Refreshed the handoff packet so the review target, files changed, and demo-path mapping match the real branch tip under review.

## Files Changed

### Reviewed implementation files

- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`

### Metadata-only handoff file

- `THREAD_PACKET.md`

## Tasks Completed

1. Added catalog-backed validation for CLI flow contract entries so `patch-review` flow projections fail fast on drift.
2. Added catalog-backed validation for CLI surface and shim contracts so parser-surface metadata plus compatibility-shim lookup and invocation tables cannot diverge from the catalog.
3. Added regression tests for those validator failure modes in the approved shared test file.
4. Refreshed the handoff packet so the reviewed scope and canonical demo-path mapping describe the actual current tip.

## Kickoff Budget / Limits Compliance

- High-risk/shared-file template applies because of the approved shared test edit in `tests/unit/test_commands_catalog.py`.
- This handoff stays within the `4`-task cap for the implementation slice: flow validation, surface-plus-shim validation, focused regression coverage, and packet refresh.
- Runtime edits stay within lane-owned paths; the only non-owned implementation file is the approved shared test path.

## Commands Run With Results

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / Blockers

- Residual risk: low. Behavior remains confined to command-catalog validation and focused regression coverage for the approved shared test path.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop` via the canonical demo-path step `preview and apply or reject a patch`.
- Exact demo-path mapping: this slice makes `preview and apply or reject a patch` more real by validating the `diff-preview` parser, surface, and shim contracts against the catalog-backed source of truth before patch-review routing can drift silently.
- `feat-commands` contribution for this slice is limited to keeping the CLI patch-review compatibility surface deterministic while the engine-first MVP loop remains CLI-first.

### Vision capability affected

- `Writing-centered workflow` because the patch-review step in the operator trust surface stays deterministic while the MVP loop still runs through the CLI.
- `Canonical engine contract` because the active CLI compatibility surface for patch review remains stable and deterministic while Textual stays disabled.
- Scope tightening: this slice does not add persistence, audit hooks, or workflow artifacts; it is limited to CLI compatibility and deterministic command-contract validation for the patch-review step.

### Routing/provider impact note

- None. This change only affects local command-catalog validation and focused command-catalog test coverage.

### Proposed README.md patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Shared edit is limited to `tests/unit/test_commands_catalog.py`, the approved `feat-commands` shared-test path.
