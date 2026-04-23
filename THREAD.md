# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Review the real `codex/feat-commands` branch tip, not a cherry-picked subset of commits.
- Truthful implementation basis:
  - merge base with `codex/quality-baseline`: `60136caf9ee4e1ff08d35e2da2922af78e7974d5`
  - reviewed implementation tip before this metadata-only fixer refresh: `434c8a33f82fd53da97445ebb41b5a329a748245`
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
- Plan alignment:
  - canonical demo-path steps advanced: primary step 2 `retrieve relevant material`; dependent step 3 `preview and apply or reject a patch`; no new step 1 workflow coverage is claimed beyond preserving the CLI `open project/document` entrypoint into retrieval
  - concrete blocker removed: parser/catalog drift can no longer silently change the retrieval or preview CLI operator contract, which removes a deterministic smoke-coverage blocker for the current engine-first MVP loop while Textual remains disabled
  - explicit Milestone 3 tie: this keeps the exit criterion `CLI can still execute the MVP loop while Textual remains disabled` concrete by preserving a deterministic, smoke-testable, operator-visible command path for step 2 retrieval and the immediate step 3 preview/apply-or-reject follow-on
  - scope framing: this is narrow CLI compatibility support for the current engine-first MVP loop, not generic command-catalog hardening or broader workflow progress
- Reviewer fix closure:
  - the handoff now explicitly states which canonical demo-path steps this work advances and keeps that claim narrow to deterministic CLI compatibility support for the existing Milestone 3 loop.
  - `2026-04-23T20:26:28Z` fixer verification rerun confirmed the packet still keeps `Vision capability affected` narrowed to CLI compatibility / canonical engine contract scope on the current branch tip.
  - ready for handoff on `2026-04-23T20:26:28Z`: the current branch tip keeps the step 2 retrieval CLI route and the immediate step 3 preview/apply-or-reject CLI route deterministic, smoke-testable, and operator-visible, and the recorded verification rerun passed on that same tip.
- Canonical demo-path steps advanced:
  - primary: `retrieve relevant material`, via the CLI-side `open project/document` and retrieval entrypoints that must keep their canonical routing in the engine-first MVP loop
  - dependent: `preview and apply or reject a patch`, via the CLI `diff-preview` entrypoint that must retain operator-visible no-diff review context
  - out of scope: no new `open project/document` workflow coverage is claimed beyond preserving CLI compatibility into retrieval
- Concrete blocker removed from the CLI-first MVP loop:
  - parser/catalog drift can no longer silently change the retrieval or preview CLI operator contract, which removes a deterministic smoke-coverage blocker for the Milestone 3 engine-first loop while Textual remains disabled.
  - the packet now states that this is narrow CLI compatibility support for the current engine-first MVP loop, not generic catalog hardening or a broader workflow or UI milestone.
- Shared-path approval basis:
  - current policy allowlist for the truthful full-delta shared tests now lives in `scripts/scope-check.sh` under the `codex/feat-commands*` lane-specific shared-test exception block:
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
  - branch-history traceability for those shared tests remains:
    - `tests/unit/test_a2ui_contract.py`: `21e84fb5`
    - `tests/unit/test_bulk_draft_routing.py`: `d80d1559`, `d4a85bbc`, `2c7db0ca`
    - `tests/unit/test_commands_catalog.py`: `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50`, `c3a66bb580772d65201a630d673a8de1d4a63776`
    - `tests/unit/test_context_storage_recovery.py`: `fce8968e`, `a87d10ba`
    - `tests/unit/test_diff_preview.py`: `8a38d7bde29da3ecfb3da905ff78416034b151b7`, `2afa0f7f2f23c2d73773cc9c5a2fc0007ba19be3`, `51279575df18d44dc112129f561f2dcb7743e70f`
    - `tests/unit/test_docindex_pageindex.py`: `3824b2b4`, `57a0c7b4`
    - `tests/unit/test_export_preview_flow.py`: `27135550`
    - `tests/unit/test_metrics_module.py`: `39535aa6`
    - `tests/unit/test_terminal_chat_routing.py`: `b5d97889`
    - `tests/unit/test_unified_retrieval.py`: `2e8c75f6`
- Current packet verification rerun:
  - `make scope-check`, `SCOPE_WINDOW=full make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` all passed on the current branch tip on `2026-04-23T20:26:28Z`.
- This fixer pass is verification-only metadata and limited to `THREAD.md` and `THREAD_PACKET.md`.
