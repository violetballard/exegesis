## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Pre-fixer branch-tip SHA: `02c1833d22ee0039876a4793b22def21629e71d7`
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..02c1833d22ee0039876a4793b22def21629e71d7`
- Handoff classification: high-risk/shared because the actual merge candidate includes retrieval implementation changes and approved shared retrieval regression coverage.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260430T003729Z.prompt.txt` requires the packet to include all non-metadata code/test changes through the branch tip, including `tests/unit/test_unified_retrieval.py`.

## Required Fixes Addressed

1. Regenerated the review packet so the reviewed implementation range includes every non-metadata code/test change through `02c1833d22ee0039876a4793b22def21629e71d7`, the pre-fixer branch tip.
2. Reclassified `02c1833d22ee0039876a4793b22def21629e71d7` and other post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` retrieval commits as implementation scope, not metadata-only packet refreshes.
3. Updated tasks completed, files changed, risk, shared-file exception notes, and canonical demo-path mapping against the actual reviewed range.
4. Re-ran the required gates on the final merge candidate and recorded outcomes below.

## Scope Completed

SQLite FTS is the authoritative retrieval path for the MVP. The actual branch-tip candidate exports the canonical query constructor and retrieval helpers through both retrieval facades, keeps PageIndex and embeddings as fallback/compatibility surfaces, normalizes query, policy, provenance, hit, citation, basket-promotion, and context-bundle payloads deterministically, fails closed for unsupported or noncanonical excerpt lookups, audits failed FTS attempts, preserves promotion-ready retrieval references for downstream engine flows, and clears FTS cache state after document updates.

The packet now treats all post-`adfa8cd` code/test commits through `02c1833d22ee0039876a4793b22def21629e71d7` as reviewed implementation scope. Metadata-only packet commits are not used to exclude retrieval code that will merge.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: made SQLite FTS the primary retrieval path with deterministic query construction, cache normalization, scope gating, excerpt lookup behavior, and document-update cache invalidation.
2. Canonical demo-path step `retrieve relevant material`: stabilized retrieval payload reconstruction for doc hits, excerpt hits, provenance, citations, source bundles, context bundles, policy metadata, fingerprints, and basket-promotion snapshots.
3. Canonical demo-path step `retrieve relevant material`: kept PageIndex and embeddings fallback-only while exposing compatibility shims, engine-facade exports, fail-closed excerpt behavior, and audit records for unsupported retrieval scopes.
4. Canonical demo-path step `retrieve relevant material`: added and maintained unit coverage for unified retrieval behavior, packet planner demo-path wording, cache invalidation, sparse payload rehydration, facade exports, citation/provenance helpers, basket promotion, and FTS-only excerpt contracts.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`: prior kickoff metadata file present in the reviewed range; this `THREAD_PACKET.md` is the authoritative corrected review packet for the actual branch-tip range.
- `.codex/lane_meta/feat-retrieval-fts.json`: prior lane metadata file present in the reviewed range; this `THREAD_PACKET.md` supersedes stale `adfa8cd` cutoff claims for reviewer traceability.
- `THREAD_PACKET.md`: refreshes this handoff with branch-tip scope and gate outcomes.
- `codex_packet_handoff/tools/planner.py`: carries canonical demo-path wording into generated packet metadata.
- `src/qual/engine/retrieval/__init__.py`: exports canonical retrieval query and facade helpers.
- `src/qual/engine/retrieval/embeddings_strategy.py`: adds fallback-only embeddings strategy compatibility surface.
- `src/qual/engine/retrieval/fts_strategy.py`: hardens FTS query normalization, hit snapshots, scope checks, cache behavior, and invalidation.
- `src/qual/engine/retrieval/pageindex_strategy.py`: adds fallback-only PageIndex compatibility surface.
- `src/qual/engine/retrieval/payload.py`: normalizes deterministic retrieval payload, provenance, citation, context, source-bundle, and basket-promotion snapshots.
- `src/qual/retrieval/__init__.py`: exports canonical retrieval facade types and helpers.
- `src/qual/retrieval/service.py`: implements FTS-first retrieval service behavior, excerpt lookup, promotion/context payloads, audit metadata, and cache invalidation.
- `tests/unit/test_packet_planner.py`: covers generated packet demo-path metadata.
- `tests/unit/test_unified_retrieval.py`: covers unified retrieval, FTS-only lookup, sparse payloads, promotion/context provenance, and cache invalidation regressions.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; within the high-risk cap by grouping the cumulative branch-tip implementation into four meaningful, testable tasks.
- Changed files in reviewed range: `13`; exceeds the normal high-risk `<=8` file guideline and is explicitly surfaced for reviewer/integrator decision rather than hidden as metadata-only drift.
- Net LOC in reviewed range: `+1687`; exceeds the normal high-risk `<=300` guideline and is explicitly surfaced because the reviewer required packet traceability over removing or hiding post-`adfa8cd` implementation commits.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `tests/unit/test_unified_retrieval.py` only.
- Lane-owned implementation files touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Packet tooling/test files touched: `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3, Real workflow loop; `ROADMAP.md` Milestone 4, Retrieval Layer.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling, and capability 6, Auditable state and workflow.
- Canonical demo-path step advanced: `retrieve relevant material`.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; smoke passed and 125 unit tests passed.
- `./typecheck-test.sh`: PASS; Python sources under `src/` compile.
- `make ci`: PASS; setup, scope-check, format, lint, compile/typecheck, smoke, and 125 unit tests completed successfully.

## Risks / Blockers

- The reviewed implementation range is intentionally branch-tip-wide through `02c1833d22ee0039876a4793b22def21629e71d7`; reviewers should not use `adfa8cdadd43747ffbcb612e4151e262b13e52ca` as the implementation cutoff.
- The cumulative branch-tip range exceeds high-risk size guidelines. This is now explicit packet risk, not a traceability ambiguity.
- Direct writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` were blocked by filesystem permissions in this worktree, so the corrected packet source of truth is `THREAD_PACKET.md`.
