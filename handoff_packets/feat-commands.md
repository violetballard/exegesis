# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: tightened the command CLI contract so it validates the real parser token surface and fails fast if the `patch-review` entrypoint drifts to alias-only, missing-canonical-token, reordered, or extra-token shapes.
- Canonical demo-path step advanced: `patch-review`
- Demo-path mapping: this slice makes the canonical `patch-review` step more real by requiring the public `diff-preview` parser surface to stay intact before operators can enter the existing apply-or-reject, persist, and export-handoff branch.
- Concrete blocker removed: parser/catalog drift can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, which would otherwise make the CLI-first MVP review step non-deterministic to smoke-test during the migration.
- Plan-alignment statement: this is a single engine-first demo-path hardening step, not a general CLI cleanup. It makes the `patch-review` contract deterministic so the downstream apply/reject, persist, and export steps keep starting from one intentional parser surface.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 3 `Product Readiness`, specifically `Define and lock user-facing output contracts` and `Contract changes documented and intentional`, applied here only to the public `patch-review` parser token contract.
- Vision capability affected: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, specifically the engine-contract-first CLI compatibility rule that keeps the `patch-review` entrypoint deterministic, stable, and catalog-locked for the current CLI-first MVP loop while `Exegesis Console` remains deferred.
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or shared entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Tightened `_validate_command_cli_contract()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:553) so the command contract validates the authoritative parser projection against the declared CLI entrypoint surface instead of only comparing deduplicated canonical command names.
2. Added parser-surface regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:494) that patch the real parser surface and prove alias-only, missing-canonical-token, reordered, and extra-token drift fail fast, including the critical `diff-preview` removed while `diff` still resolves case.
3. Updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1) to name the exact `patch-review` demo-path step this slice advances, state the concrete blocker removed, and keep the scope claim tied to that step.
4. Ran the required gate suite and scope check.

## Files Changed
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python -m unittest tests.unit.test_commands_catalog -q` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed

## Risks / Blockers
- Risks: future parser-surface changes now need to keep the declared CLI entrypoints, authoritative parser projection, and packet metadata aligned; the updated regressions are intended to fail fast if they drift.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval note: `THREAD_OWNERSHIP.md` shared-file exception retained for the required parser-surface regression coverage.
