# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Review the real `codex/feat-commands` branch tip, not a cherry-picked subset of commits.
- Truthful implementation basis:
  - merge base with `codex/quality-baseline`: `60136caf9ee4e1ff08d35e2da2922af78e7974d5`
  - reviewed tip before this verification-only fixer commit: `025ed0b77951e7d94a5d950f52227433581c0e19`
- The truthful merge-base-to-tip changed file set for the command handoff pathset (`src/qual/commands`, `tests/unit`, `THREAD*`) is:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_a2ui_contract.py`
  - `tests/unit/test_bulk_draft_routing.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_context_storage_recovery.py`
  - `tests/unit/test_diff_preview.py`
  - `tests/unit/test_docindex_pageindex.py`
  - `tests/unit/test_export_preview_flow.py`
  - `tests/unit/test_metrics_module.py`
  - `tests/unit/test_terminal_chat_routing.py`
  - `tests/unit/test_unified_retrieval.py`
  - `THREAD.md`
  - `THREAD_PACKET.md`
- The packet no longer claims that post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` work is metadata-only. Later implementation is present, including `1e04f9633c4abc4988dcb991944680b86f94f753`, `5c89ce987fc78ed158d378a988b3e211ce93145d`, and `b3be9f0c12e6fd3ecd52f1b8af2bd1b6d890e1a0`.
- The command-focused review claim is narrower than that full changed-file set:
  - the lane-owned implementation remains `src/qual/commands/**`
  - the extra `tests/unit/*` files above are branch-carried shared regression coverage for adjacent MVP slices that still appear in the truthful tip-level delta
  - this handoff does not pretend those shared tests are absent; it states them explicitly and carries the residual approval risk forward
- Canonical demo-path steps advanced:
  - primary: `retrieve relevant material`
  - dependent: `preview and apply or reject a patch`
- Concrete blocker removed from the CLI-first MVP loop:
  - the operator no longer depends on fragile parser drift behavior, dropped routed subcommands, or missing no-diff preview state for the current CLI fallback path.
  - the packet now states that this is narrow Milestone 3 command-contract hardening, not a broader workflow or UI milestone.
- Shared-path approval basis:
  - current policy allowlist for `tests/unit/test_commands_catalog.py`: `scripts/scope-check.sh`, traced through `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` and `c3a66bb580772d65201a630d673a8de1d4a63776`
  - branch-history approval trail for `tests/unit/test_diff_preview.py`: `8a38d7bde29da3ecfb3da905ff78416034b151b7`, `2afa0f7f2f23c2d73773cc9c5a2fc0007ba19be3`, and `51279575df18d44dc112129f561f2dcb7743e70f`
  - shared branch-history origin for the remaining truthful tip-level shared tests:
    - `tests/unit/test_a2ui_contract.py`: `21e84fb5`
    - `tests/unit/test_bulk_draft_routing.py`: `d80d1559`, `d4a85bbc`, `2c7db0ca`
    - `tests/unit/test_context_storage_recovery.py`: `fce8968e`, `a87d10ba`
    - `tests/unit/test_docindex_pageindex.py`: `3824b2b4`, `57a0c7b4`
    - `tests/unit/test_export_preview_flow.py`: `27135550`
    - `tests/unit/test_metrics_module.py`: `39535aa6`
    - `tests/unit/test_terminal_chat_routing.py`: `b5d97889`
    - `tests/unit/test_unified_retrieval.py`: `2e8c75f6`
  - only `tests/unit/test_commands_catalog.py` has a current `feat-commands` scope-check allowlist entry; the rest remain truthful branch-carried shared paths and are an explicit residual review risk
- Current packet verification rerun:
  - `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the current branch tip on `2026-04-23`.
- This fixer pass is verification-only metadata and limited to `THREAD.md` and `THREAD_PACKET.md`.
