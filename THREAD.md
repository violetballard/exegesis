# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Review the real `codex/feat-commands` branch tip, not a cherry-picked subset of commits.
- Truthful implementation basis:
  - merge base with `codex/quality-baseline`: `60136caf9ee4e1ff08d35e2da2922af78e7974d5`
  - reviewed tip before this verification-only fixer commit: `ac54e825427e6eec6cc823703442952be150e363`
- The tip-level implementation diff in scope is:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- The packet no longer claims that post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` work is metadata-only. Later implementation is present, including `1e04f9633c4abc4988dcb991944680b86f94f753`, `5c89ce987fc78ed158d378a988b3e211ce93145d`, and `b3be9f0c12e6fd3ecd52f1b8af2bd1b6d890e1a0`.
- Canonical demo-path steps advanced:
  - primary: `retrieve relevant material`
  - dependent: `preview and apply or reject a patch`
- Concrete blocker removed from the CLI-first MVP loop:
  - the operator no longer depends on fragile parser drift behavior, dropped routed subcommands, or missing no-diff preview state for the current CLI fallback path.
  - the packet now states that this is narrow Milestone 3 command-contract hardening, not a broader workflow or UI milestone.
- Shared-path approval basis:
  - current policy allowlist for `tests/unit/test_commands_catalog.py`: `scripts/scope-check.sh`, traced through `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` and `c3a66bb580772d65201a630d673a8de1d4a63776`
  - branch-history approval trail for `tests/unit/test_diff_preview.py`: `8a38d7bde29da3ecfb3da905ff78416034b151b7`, `2afa0f7f2f23c2d73773cc9c5a2fc0007ba19be3`, and `51279575df18d44dc112129f561f2dcb7743e70f`
- Current packet verification rerun:
  - `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the current branch tip on `2026-04-23`.
- This fixer pass is verification-only metadata and limited to `THREAD.md` and `THREAD_PACKET.md`.
