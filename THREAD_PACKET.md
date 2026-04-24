# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Packet role: `reviewer-fix canonical retrieval contract`
- Current branch tip before this fixer commit: `791668c7935f920034a09bc83827e3e2d4df1d0d`
- Canonical demo-path step advanced: `retrieve relevant material`
- Canonical demo-path statement: This fixer pass makes `retrieve relevant material` more real on the engine-facing MVP path by fail-closing non-FTS retrieval metadata on the canonical source-bundle/context-bundle reconstruction helpers that feed structured results and basket/workflow promotion. It does not claim new retrieval wiring; it hardens the existing canonical contract so stale PageIndex-style metadata cannot leak back into downstream payloads.
- Shared-file approval basis: `tests/unit/test_unified_retrieval.py` remains the only approved shared-by-approval regression surface for this lane under `THREAD_OWNERSHIP.md`.

## Scope Goal

- Keep this fix on the canonical engine-first retrieval surface by tightening `src/qual/engine/retrieval/payload.py` and proving the behavior with shared retrieval regressions in `tests/unit/test_unified_retrieval.py`.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: harden canonical retrieval source/context bundle reconstruction so downstream structured payloads stay FTS-first and auditable.
- Risk reason: the fix uses approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Tighten the canonical payload normalizers so non-FTS retrieval metadata fails closed instead of surviving source-bundle reconstruction.
2. Rebuild context-bundle downstream payloads from the canonical source bundle when both are present so stale top-level metadata cannot override FTS-first state.
3. Add shared regression coverage proving the structured result and basket/workflow payloads stay canonical when sparse inputs inject PageIndex-style metadata.
4. Rerun the required gate stack and refresh the handoff packet so it states explicitly that this advances `retrieve relevant material`.

### Checkpoint Status

- `plan complete`: the reviewer gap was confirmed on `src/qual/engine/retrieval/payload.py`, not on the compatibility `fetch_excerpt()` surface.
- `first green tests`: targeted unified-retrieval regressions and the full `tests.unit.test_unified_retrieval` suite passed after the payload/context-bundle fixes.
- `before risky/shared file edit`: shared edits remained limited to approved regression coverage in `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: the runtime changes, shared regression proof, and required gate results all agree on the same canonical retrieval-contract story.

## Scope Completed

- Fail-closed canonical retrieval metadata in [src/qual/engine/retrieval/payload.py](/Users/doctor-violet/.codex/worktrees/rfts/qual/src/qual/engine/retrieval/payload.py) so source-bundle, hit, provenance, citation, and basket-promotion reconstruction paths keep `source_strategy=fts`, `retrieval_backend=sqlite_fts`, and `retrieval_mode=fts_first` instead of preserving stale non-FTS values.
- Changed context-bundle reconstruction to rebuild `retrieval_downstream_payload` from the canonical source bundle when available, so the engine-facing structured-result path used before basket/workflow promotion no longer trusts stale top-level metadata.
- Added shared regression coverage in [tests/unit/test_unified_retrieval.py](/Users/doctor-violet/.codex/worktrees/rfts/qual/tests/unit/test_unified_retrieval.py) proving source-bundle and context-bundle helpers fail closed when `pageindex`-style metadata is injected into sparse inputs.

## Tasks Completed

1. Restricted canonical payload normalization to the FTS-first MVP contract in `src/qual/engine/retrieval/payload.py`.
2. Rebuilt context-bundle downstream payloads from canonical source bundles so structured retrieval results prefer canonical engine data over stale top-level snapshots.
3. Added regressions proving the basket/workflow-facing payload helper and context-bundle helper reject non-canonical metadata drift.
4. Reran `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Canonical Step Task Mapping

- Task 1 advances `retrieve relevant material` by ensuring the structured retrieval contract remains SQLite FTS-first even when sparse payloads carry stale metadata.
- Task 2 advances `retrieve relevant material` by keeping the engine-facing context/source bundle path authoritative before basket promotion consumes it.
- Task 3 advances `retrieve relevant material` by proving the canonical structured results and basket/workflow payloads fail closed instead of regressing toward PageIndex-style routing.
- Task 4 advances `retrieve relevant material` by documenting and rerunning the exact gates on the strengthened canonical path.

## Files Changed

- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

## Commands Run With Results

- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_fail_closes_noncanonical_basket_metadata tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_fail_closes_noncanonical_hit_metadata tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_downstream_payload_helper_normalizes_nested_citation_fields`: `PASS`
- `python3 -m unittest tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_fetch_excerpt_requires_an_fts_lookup_hit tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieve_fts_source_bundle_matches_result_snapshot tests.unit.test_unified_retrieval.UnifiedRetrievalTests.test_retrieval_context_bundle_helper_packages_payload_and_bundles`: `PASS`
- `python3 -m unittest tests.unit.test_unified_retrieval`: `PASS` (`214 tests`)
- `make scope-check`: `PASS` (`no policy for branch 'codex/feat-retrieval-fts'; skipping`)
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Reviewer Fix Closure

1. The packet now states explicitly that this work advances the canonical demo-path step `retrieve relevant material`.
2. The fail-closed behavior and proof now live on the actual canonical engine-facing retrieval reconstruction surface in `src/qual/engine/retrieval/payload.py`, not only on the compatibility `fetch_excerpt()` path.
3. The shared regressions now demonstrate stronger behavior on the structured-result, source-bundle, context-bundle, and basket/workflow-facing helpers instead of only on PageIndex-only excerpt lookups.

## Risks / Blockers

- Remaining risks: none identified beyond the approved shared-test surface already called out above.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- `Milestone 3: Product Readiness`
- `feat-retrieval-fts`

### Canonical demo-path step advanced

- `retrieve relevant material`
- This fix keeps the canonical engine-facing retrieval payload deterministic and FTS-first before basket/workflow promotion consumes the result.

### Vision capability affected

- `2. Retrieval-first context handling`
- `3. Auditable generation`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Shared-file approval basis remains limited to `tests/unit/test_unified_retrieval.py`.
- No provider or routing surfaces were changed.
