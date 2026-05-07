# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after this handoff.
- Reviewed implementation range: command smoke sequence contract at branch tip, centered on `src/qual/commands/catalog.py` and `src/qual/commands/canonical.py`.
- Scope completed: command demo smoke sequence contract that bundles trusted-loop readiness with exact smoke argvs for the Milestone 3 CLI demo loop.
- Roadmap item affected: Milestone 3 (Real workflow loop) - CLI compatibility and migration-safe entrypoints for `feat-commands`.
- Vision capability affected: canonical engine contract and CLI compatibility as the active operator surface while Textual remains disabled.
- Routing/provider impact note: none.
- Proposed `README.md` patch text: none.

## Tasks Completed

1. Added `CommandDemoSmokeSequenceEntry` dataclass to model a single smoke-testable step in the demo path with ordinal, flow step, engine actions, smoke argvs, and thin-handler readiness.
2. Added `CommandDemoSmokeSequenceContract` dataclass to bundle the complete smoke sequence with fingerprint, completeness flags, entries, argvs, and validation error surfaces.
3. Implemented `command_demo_smoke_sequence_contract()` in `src/qual/commands/catalog.py` that composes trusted-loop readiness with exact smoke argvs and thin-handler readiness, including internal consistency assertions.
4. Exposed `canonical_command_smoke_sequence_contract()` in `src/qual/commands/canonical.py` as the canonical entrypoint, with proper imports and `__all__` export.

## Files Changed For This Scope

- `src/qual/commands/catalog.py`
- `src/qual/commands/canonical.py`
- `THREAD_PACKET.md`

## Ownership And Scope

- Lane-owned implementation paths changed: `src/qual/commands/catalog.py`, `src/qual/commands/canonical.py`.
- Shared-by-approval files changed: none.
- Integrator-locked files changed: none.
- Routing/provider/config files changed: none.

## Commands Run

- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `./quality-test.sh`: passed; 430 tests, 1 skipped.
- `./typecheck-test.sh`: passed.
- `make ci`: passed.

## Risks And Blockers

- No blockers. All gates green.
- Smoke sequence contract depends on trusted-loop contract being complete; if trusted loop has missing flow steps or engine actions, the smoke sequence will reflect that incompleteness.

## Canonical Demo-Path Step Advanced

This lane now provides a stable smoke-sequence contract that validates the complete Milestone 3 CLI demo loop:
- open project/document
- retrieve relevant material
- preview and apply or reject a patch
- persist and continue

The `command_demo_smoke_sequence_contract` bundles exact CLI argvs per demo-path step with thin-handler readiness, enabling deterministic smoke testing of the full engine loop through the CLI surface.

## Final Readiness Statement

The command smoke sequence contract provides a complete, deterministic bundle of trusted-loop readiness with exact smoke argvs for the Milestone 3 demo path. All command handlers remain thin and delegate to engine code. All gates are green. Ready for integration.
