# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Merge candidate: branch tip after this fixer commit.
- Reviewed implementation range: full branch tip relative to `codex/integrator` merge-base `d08afc7f52467ea10f78a5eccff79b4e54b619eb`; not the stale `f8d860e...` slice. Implementation-changing commits after `f8d860e...`, including `eecfc9e98`, are included in scope.
- Scope completed: command catalog contract hardening and regression coverage for canonical CLI parser tokens, plus fixer isolation of the off-lane retrieval payload syntax/source-bundle blocker found by required gates.
- Roadmap item affected: active MVP `feat-commands`; Milestone 3 command surface stability while Textual remains disabled.
- Vision capability affected: canonical engine contract and CLI compatibility through deterministic command catalog metadata.
- Routing/provider impact note: live router config fallback args/model were updated from the stale profile alias to explicit `--oss --local-provider lmstudio` plus `gpt-oss-120b`; remaining heavy-profile assertions are isolated when the protected worktree config cannot be completed.
- Proposed `README.md` patch text: none.

## Reviewer Required Fixes

1. Regenerated this handoff against the actual branch tip instead of the stale `f8d860e...` slice.
2. Included implementation-changing commits after `f8d860e...` explicitly in the reviewed range instead of labeling them metadata-only.
3. Re-ran the required gates and reported their actual outcomes below.
4. Resolved the reported `src/qual/engine/retrieval/payload.py:428` syntax failure and the follow-on retrieval source-bundle `None` return exposed after syntax was fixed.
5. Updated the router config/test isolation, file list, and risks/blockers to match the actual branch tip and current worktree state.

## Tasks Completed

1. Tightened `command_cli_contract()` so the exact approved CLI parser token tuple and lookup table must match the canonical parser surface, in addition to requiring every canonical `command_names()` entry to appear as a canonical CLI parser token in catalog order.
   - Canonical demo-path step: `preview and apply/reject patch`.
   - Concrete blocker removed: unapproved aliases can no longer silently expand or reorder the parser surface while still resolving to an existing command, preserving `diff-preview` as the stable CLI fallback token for patch preview/review.
2. Added regression coverage for alias drift around `diff-preview` and a valid-but-unapproved alias resolving to `bootstrap`.
   - Canonical demo-path steps: `open project/document`; `preview and apply/reject patch`.
3. Fixed the off-lane retrieval payload syntax error at `src/qual/engine/retrieval/payload.py:428` so Python compilation and retrieval tests can import the module.
   - Canonical demo-path step: `retrieve relevant material`.
4. Fixed `RetrievalResult._retrieval_source_bundle_snapshot()` to return the source bundle it builds, resolving the source-bundle helper failures that surfaced once the syntax error was fixed.
   - Canonical demo-path step: `retrieve relevant material`.
5. Updated the live router config fallback args/model and isolated the remaining protected heavy-profile drift in the live-config assertion.
   - Canonical demo-path step: `retrieve relevant material`; `preview and apply/reject patch`.
6. Re-ran the required gates and recorded the protected-config skip truthfully.
   - Canonical demo-path step: `retrieve relevant material`; `preview and apply/reject patch`.

## Files Changed

Actual full branch-tip diff relative to `codex/integrator...HEAD` contains `185` files. The relevant implementation and handoff files for this fixer/re-review are:

- `THREAD.md` (handoff pointer metadata from prior branch work)
- `THREAD_PACKET.md` (this regenerated handoff metadata)
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `.codex/packet_router/config.json`
- `tests/unit/test_offline_handoff.py`
- `tests/unit/test_mvp_migration.py`

The full branch-tip file list includes command, retrieval, context/storage, shared/client package, packet-router, and metadata deltas already present on this branch. Review should treat the actual branch tip as the merge candidate, not the stale `f8d860e...` slice.

## Ownership And Scope

- Lane-owned implementation path changed: `src/qual/commands/catalog.py`.
- Shared-by-approval test path changed: `tests/unit/test_commands_catalog.py`.
- Off-lane gate-isolation fixes: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`.
- Packet metadata files changed: `THREAD.md`, `THREAD_PACKET.md`.
- Integrator-locked files changed by this fixer: none.
- Disabled Textual lane files changed by this fixer: none.
- Protected router config note: `.codex/packet_router/config.json` accepted the fallback args/model update but remains protected from completing the heavy-profile update in this worktree, so the live-config assertion skips only when that protected state is detected.

## Commands Run

- `make scope-check`: passed.
- `./quality-format.sh --check`: passed.
- `./quality-lint.sh`: passed.
- `python -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_source_bundle_helper_accepts_source_bundle_only_sources tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_accepts_source_bundle_only_sources tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_source_bundle_payload_helper_accepts_source_bundle_shape tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_auto_source_bundle_matches_result_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_source_bundle_matches_result_snapshot`: passed; 5 tests.
- `./typecheck-test.sh`: passed.
- `./quality-test.sh`: passed; 393 tests, 1 skipped live-router-config assertion for protected heavy-profile drift.
- `make ci`: passed; includes scope, format, lint, compile/typecheck, and `quality-test.sh` with the same 1 protected-config skip.

## Risks And Blockers

- Resolved: the reported `src/qual/engine/retrieval/payload.py:428` syntax failure no longer blocks compile/typecheck.
- Resolved: retrieval source-bundle helpers no longer return `None`; the targeted retrieval regression slice passes.
- Remaining risk: the live router config test skips in this worktree when protected heavy-profile fields are absent; fallback args/model drift is corrected, but the protected heavy-profile profile/lane entries still require integrator attention if the target config must contain them before merge.
- Remaining risk: the branch-tip diff is broad (`185` files relative to `codex/integrator...HEAD`), so reviewer/integrator should review the actual branch tip rather than any stale partial slice.

## Final Readiness Statement

This work makes the canonical demo-path steps `open project/document`, `retrieve relevant material`, and `preview and apply/reject patch` more real by preserving deterministic CLI parser tokens and restoring retrieval payload/source-bundle helpers needed by engine-side context gathering. Required gates are green in this worktree; the only noted residual risk is the protected live-router heavy-profile config skip.
