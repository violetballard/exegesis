# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: actual submitted branch tip, including all implementation files listed below and the final fresh-gate evidence commit. Do not review against the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- Implementation-file accounting basis: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..8ef82873046f003a2ecf241dae3d0b5c352796be`, plus follow-up handoff evidence and this final reviewer-fix closure commit.
- Lane/owned paths: `src/qual/commands/**`
- Shared / integrator-locked ownership statement:
  - Integrator-locked edit: `src/qual/cli.py`, explicitly listed as shared-by-approval for `codex/feat-commands*` in `THREAD_OWNERSHIP.md`; this handoff includes it because the live argparse surface must expose the same CLI entrypoint projection validated by the command catalog.
  - No other integrator-locked files were touched.
  - Shared support edit: `scripts/scope-check.sh`, included only to keep scope enforcement aware of the approved shared command test path used by this lane.
  - Approved shared test edits: `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, both used as command-surface regression coverage for this lane.
- Scope goal: harden the CLI command contract for the engine-first MVP loop by keeping command entrypoints deterministic, validating live parser tokens against the catalog, and covering the command diff-preview/workflow surfaces without starting disabled Textual lanes.
- Risk reason: this is high-risk command-contract work because it touches operator-facing CLI entrypoints and the shared `src/qual/cli.py` parser surface.

### Scope / Plan Alignment

- Roadmap alignment: `ROADMAP.md` Milestone 1 `Command and diff-preview behavior hardening` / `Manual CLI smoke flow remains stable`, Milestone 2 remaining parser-edge coverage, Milestone 3 output-contract intentionality, and the active MVP emphasis on `feat-commands`.
- Vision alignment: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`; CLI remains a first-class development and reliability surface with deterministic text fallback behavior.
- Exact capability delivered: deterministic CLI command-surface hardening for the existing engine-first command path. This does not claim retrieval, persistence, provider routing, apply/reject engine execution, or Textual UI progress.
- Parser-surface drift fix: `command_cli_contract()` now validates the full grouped CLI entrypoint projection, token tuple, canonical-name tuple, and lookup table against the declared catalog and the argparse-derived live parser surface, so alias-only token drift is rejected even when canonical command names stay stable.
- Actual-tip traceability: this packet intentionally reviews the real branch tip and includes every implementation file changed since the older reviewer basis, instead of treating later commits as metadata-only.

### Canonical Demo-Path Mapping

- Task 1 advances `continue working`: stable parser/catalog contracts keep command dispatch deterministic across follow-up operator turns.
- Task 2 advances `continue working`: alias-only parser drift now fails fast before an operator continues through a changed command surface.
- Task 3 advances `plan/revise` and `apply/reject patch`: command workflow and diff-preview regression coverage preserves the command surfaces used to revise plans and inspect patch choices.
- Task 4 advances `continue working`: refreshed handoff metadata gives reviewer/integrator the exact review basis needed to keep the branch moving without scope ambiguity.
- Final demo-path statement: this handoff most directly makes `continue working` more real by hardening the CLI command contract that preserves deterministic follow-on operation in the engine-first MVP loop.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: exceeded by existing branch history before this fixer pass; this packet makes the overage explicit for reviewer/integrator risk assessment rather than hiding implementation files behind a metadata-only claim.
- Size accounting: `12 files changed, 12820 insertions(+), 982 deletions(-)` across `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..8ef82873046f003a2ecf241dae3d0b5c352796be`; this final commit only records fresh gate evidence.
- Exception route: high-risk branch-size overage requires reviewer/integrator exception; this handoff is not claiming normal high-risk size compliance.
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep `command_cli_contract()` aligned to the canonical command order while validating the full parser token projection.
2. Reject parser/catalog drift when aliases are added, removed, reordered, or substituted while canonical names remain stable.
3. Cover the command diff-preview and workflow command surfaces with focused unit tests.
4. Refresh handoff metadata so review scope, file list, size overage, shared exceptions, and roadmap/vision mapping match the actual submitted tip.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: the handoff is scoped to CLI command-contract hardening for the current engine-first MVP focus and reviews the actual branch tip.
- first green tests: focused command-catalog tests passed on `2026-04-28T19:24:34Z`; the full required gates were rerun after the final packet refresh for this fixer pass.
- before risky/shared file edit: risky/shared paths are listed above with the approval rationale.
- ready for handoff: this packet names the full implementation set and records the latest gate results.

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates declared catalog entrypoints, live parser entrypoints, canonical-name order, accepted CLI tokens, and token-to-command lookup rows.
  - preserved deterministic command ordering for the CLI contract and command helper exports.
  - derived `src/qual/cli.py` parser entrypoint metadata from the actual argparse subparser surface so argparse token drift is checked before dispatch.
  - added command workflow and diff-preview helpers under `src/qual/commands/**` while keeping command handlers thin and CLI-oriented.
  - updated scope-check handling for the approved shared command test paths.
  - added regression tests for canonical-order alignment, the explicit alias-only parser projection drift matrix, exported parser constant alias substitution with stable canonical names, live parser constant drift, real argparse subparser drift, parse_args fail-fast behavior under parser constant drift, diff-preview behavior, and command workflow contracts.
  - refreshed `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` so the handoff reviews the actual tip rather than an older narrow slice.
- tasks completed (numbered):
  1. Validated `command_cli_contract()` against the full parser entrypoint projection and lookup table, including alias-only drift cases where canonical names remain stable. Canonical demo-path step: `continue working`.
  2. Kept deterministic command ordering and helper exports aligned with the canonical command catalog. Canonical demo-path step: `continue working`.
  3. Added focused command catalog, parser fail-fast, workflow, and diff-preview regression coverage. Canonical demo-path steps: `plan/revise` and `apply/reject patch`.
  4. Regenerated handoff metadata to include every actual implementation file, real size overage, shared/integrator-locked exception, gate result, and canonical demo-path mapping. Canonical demo-path step: `continue working`.
- files changed:
  - implementation: `scripts/scope-check.sh`
  - implementation, shared-by-approval: `src/qual/cli.py`
  - implementation: `src/qual/commands/__init__.py`
  - implementation: `src/qual/commands/canonical.py`
  - implementation: `src/qual/commands/catalog.py`
  - implementation: `src/qual/commands/diff_preview.py`
  - implementation: `src/qual/commands/workflow.py`
  - tests, approved shared path: `tests/unit/test_commands_catalog.py`
  - tests, approved shared path: `tests/unit/test_diff_preview.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- commands run + outcomes:
  - latest fixer evidence timestamp: `2026-04-28T19:24:34Z`
  - `python -m unittest tests.unit.test_commands_catalog` -> passed
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: high. This branch already exceeds the normal high-risk size budget and touches the shared CLI parser surface; the packet now makes that explicit for review instead of narrowing the claimed basis.
  - blockers: none.
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 1 scope item `Command and diff-preview behavior hardening`.
  - `ROADMAP.md` Milestone 1 exit criterion `Manual CLI smoke flow remains stable`.
  - `ROADMAP.md` Milestone 2 remaining parser-edge coverage.
  - `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional`.
  - `ROADMAP.md` MVP Focus active implementation emphasis `feat-commands`.
- vision capability affected:
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`.
  - `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)` only insofar as CLI text fallback remains compatible with structured command output; this handoff does not add A2UI schemas.
- routing/provider impact note:
  - none; this change does not touch model routing or provider configuration.
- reviewer-fix satisfaction note:
  1. Required fix 1 is satisfied by `src/qual/commands/catalog.py` and `src/qual/cli.py`: `command_cli_contract()` validates the declared catalog entrypoint projection, argparse-derived live parser entrypoint projection, canonical-name order, accepted CLI token tuple, token-to-command lookup table, and reconstructed grouped projection.
  2. Required fix 2 is satisfied by `tests/unit/test_commands_catalog.py`: regression coverage rejects the explicit alias-only parser projection drift matrix, including token removal, token substitution, token reorder, extra aliases, live parser constant drift, real argparse subparser drift, and stable-canonical-name drift cases.
  3. Required fix 3 is satisfied by `src/qual/cli.py` and `src/qual/commands/catalog.py`: the live argparse surface is exported through `parser_cli_entrypoints()`, `command_cli_contract()` validates that parser-derived projection, and `parse_args()` invokes the contract before dispatch.
  4. Required fix 4 is satisfied by this actual-tip handoff packet: implementation files, approved shared-test exceptions, the shared/integrator-locked CLI parser exception, and the claimed parser-surface drift protection all match the current branch tip.
  5. Required fix 5 is satisfied by the canonical demo-path mapping above and by the numbered completed tasks, each of which names the demo-path step it supports.
- reviewer-fix closure note:
  - This closure keeps the actual submitted branch tip as the only review basis, preserves the full alias-only parser drift protection already present in the branch, and records fresh gate evidence for the final metadata state.
