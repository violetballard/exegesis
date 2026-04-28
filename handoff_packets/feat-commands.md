# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Review basis: actual submitted branch tip after this fixer commit, including all implementation files listed below. Do not review against the older `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` slice.
- Lane/owned paths: `src/qual/commands/**`
- Shared/integrator-locked paths with approval note:
  - `src/qual/cli.py` is shared-by-approval for `codex/feat-commands*` in `THREAD_OWNERSHIP.md`; this handoff includes it because the live argparse surface must expose the same CLI entrypoint projection validated by the command catalog.
  - `scripts/scope-check.sh` is included only to keep scope enforcement aware of the approved shared test path used by this lane.
  - `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` are shared test coverage paths approved for this command-surface handoff.
- Scope goal: harden the CLI command contract for the engine-first MVP loop by keeping command entrypoints deterministic, validating live parser tokens against the catalog, and covering the command diff-preview/workflow surfaces without starting disabled Textual lanes.
- Risk reason: this is high-risk command-contract work because it touches operator-facing CLI entrypoints and the shared `src/qual/cli.py` parser surface.

### Scope / Plan Alignment

- Roadmap alignment: `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional`, plus CLI stability for the MVP flow while Textual remains disabled.
- Vision alignment: `PRODUCT_VISION.md` capability 3 `Canonical engine contract`; CLI remains a first-class development and reliability surface with deterministic text fallback behavior.
- Exact capability delivered: deterministic CLI command-surface hardening for the existing engine-first command path. This does not claim retrieval, persistence, provider routing, apply/reject engine execution, or Textual UI progress.
- Parser-surface drift fix: `command_cli_contract()` now validates the full grouped CLI entrypoint projection, token tuple, canonical-name tuple, and lookup table against the declared catalog and the live parser surface, so alias-only token drift is rejected even when canonical command names stay stable.
- Actual-tip traceability: this packet intentionally reviews the real branch tip and includes every implementation file changed since the older reviewer basis, instead of treating later commits as metadata-only.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: exceeded by existing branch history before this fixer pass; this packet makes the overage explicit for reviewer/integrator risk assessment rather than hiding implementation files behind a metadata-only claim.
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Keep `command_cli_contract()` aligned to the canonical command order while validating the full parser token projection.
2. Reject parser/catalog drift when aliases are added, removed, reordered, or substituted while canonical names remain stable.
3. Cover the command diff-preview and workflow command surfaces with focused unit tests.
4. Refresh handoff metadata so review scope, file list, shared exceptions, and roadmap/vision mapping match the actual submitted tip.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: the handoff is scoped to Milestone 3 CLI command-contract hardening and reviews the actual branch tip.
- first green tests: full required gates were rerun on `2026-04-28` for this fixer pass.
- before risky/shared file edit: risky/shared paths are listed above with the approval rationale.
- ready for handoff: this packet names the full implementation set and records the latest gate results.

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so it validates declared catalog entrypoints, live parser entrypoints, canonical-name order, accepted CLI tokens, and token-to-command lookup rows.
  - preserved deterministic command ordering for the CLI contract and command helper exports.
  - aligned `src/qual/cli.py` parser entrypoint metadata with the command catalog so argparse token drift is checked before dispatch.
  - added command workflow and diff-preview helpers under `src/qual/commands/**` while keeping command handlers thin and CLI-oriented.
  - updated scope-check handling for the approved shared command test paths.
  - added regression tests for canonical-order alignment, alias-only parser drift, live parser constant drift, parse_args fail-fast behavior under parser constant drift, diff-preview behavior, and command workflow contracts.
  - refreshed `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md` so the handoff reviews the actual tip rather than an older narrow slice.
- tasks completed (numbered):
  1. Validated `command_cli_contract()` against the full parser entrypoint projection and lookup table, including alias-only drift cases where canonical names remain stable.
  2. Kept deterministic command ordering and helper exports aligned with the canonical command catalog.
  3. Added focused command catalog, parser fail-fast, workflow, and diff-preview regression coverage.
  4. Regenerated handoff metadata to include every actual implementation file, shared exception, gate result, and exact Milestone 3 mapping.
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
  - latest fixer evidence timestamp: `2026-04-28T18:40:59Z`
  - `python -m unittest tests.unit.test_commands_catalog` -> passed (`Ran 163 tests`; `OK`)
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed (`Ran 246 tests`; `OK`)
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed (`CI entrypoint completed`; unit suite reported `Ran 246 tests`; `OK`)
- risks/blockers:
  - risk: high. This branch already exceeds the normal high-risk size budget and touches the shared CLI parser surface; the packet now makes that explicit for review instead of narrowing the claimed basis.
  - blockers: none.
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 3 exit criterion `Contract changes documented and intentional`.
  - `ROADMAP.md` CLI stability for the MVP flow while Textual lanes remain disabled.
- vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`.
  - CLI remains a first-class surface for development and reliability.
- routing/provider impact note:
  - none; this change does not touch model routing or provider configuration.
- reviewer-fix satisfaction note:
  1. Required fix 1 is satisfied by choosing the actual branch tip as the review basis and listing every implementation file changed since the older reviewer basis.
  2. Required fix 2 is satisfied by validating the full CLI token projection, canonical-name projection, and lookup table against declared and live parser entrypoints.
  3. Required fix 3 is satisfied by alias-add/remove/substitution tests in `tests/unit/test_commands_catalog.py` where canonical names remain stable but accepted parser tokens drift, including a `parse_args` regression against live parser constant drift.
  4. Required fix 4 is satisfied by narrowing roadmap/vision mapping to Milestone 3 CLI determinism and `Canonical engine contract`, without claiming broader demo-path, retrieval, provider, or UI progress.
  5. Required fix 5 is satisfied by the full required gate rerun recorded above.
