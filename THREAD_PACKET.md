## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Pre-fixer branch-tip SHA: `02c1833d22ee0039876a4793b22def21629e71d7`
- Final HEAD SHA: reported in the fixer final response because a commit cannot contain its own SHA.
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..02c1833d22ee0039876a4793b22def21629e71d7`
- Reviewed implementation head: `02c1833d22ee0039876a4793b22def21629e71d7`
- Handoff classification: high-risk/shared because the reviewed range includes approved shared regression coverage and packet-planner support outside lane-owned retrieval paths.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260430T003729Z.prompt.txt` required the packet to cover every branch-tip code/test change, including retrieval tests and branch-tip retrieval implementation commits.

## Required Fixes Addressed

1. Regenerated this packet so the reviewed implementation range includes every non-metadata code/test change that will merge through `02c1833d22ee0039876a4793b22def21629e71d7`.
2. Reclassified `02c1833d22ee0039876a4793b22def21629e71d7` and other post-`adfa8cd` commits accurately: branch-tip commits that modify retrieval code or tests are implementation commits, not metadata-only commits.
3. Updated task accounting, files changed, risk, shared-file exception notes, and canonical demo-path mapping against the actual reviewed range.
4. Re-ran the required gates on the final merge candidate after the packet refresh; outcomes are recorded below.

## Scope Completed

The reviewed merge candidate completes the FTS-first retrieval MVP for engine flows. SQLite FTS remains the authoritative retrieval path, PageIndex and embeddings are importable compatibility shims that do not participate in the active path, retrieval facades export canonical query and bundle helpers, payload/source/context snapshots are deterministic, basket-promotion references survive sparse downstream reconstruction, and FTS cache state is invalidated after document updates.

The packet planner changes are included in this reviewed range because they affect handoff traceability: planner packets can now use an explicit reviewed implementation head/range instead of treating packet-refresh branch tips as the implementation boundary.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: make SQLite FTS the active retrieval strategy, expose canonical query and retrieval facade helpers, and keep PageIndex/embeddings fallback-only.
2. Canonical demo-path step `retrieve relevant material`: produce deterministic retrieval payloads, provenance, source bundles, context bundles, citations, fingerprints, and FTS-only excerpt lookup behavior for engine downstream use.
3. Canonical demo-path step `retrieve relevant material`: add basket-promotion context references and preserve item IDs, citation refs, ranks, fingerprints, and nested context refs through sparse payload/source/context reconstruction.
4. Canonical demo-path step `retrieve relevant material`: harden branch-tip correctness with FTS cache invalidation after document upserts, byte-safe candidate doc IDs, approved shared regression coverage, and packet-planner traceability support for reviewed implementation ranges.

## Files Changed

- `.codex/kickoff_packets/feat-retrieval-fts.md`: present in the reviewed range; direct mirror refresh was blocked by filesystem permissions, so this `THREAD_PACKET.md` is the authoritative corrected packet.
- `.codex/lane_meta/feat-retrieval-fts.json`: present in the reviewed range; direct mirror refresh was blocked by filesystem permissions, so stale `adfa8cd` cutoff claims there are superseded by this packet.
- `THREAD_PACKET.md`: regenerates the authoritative handoff packet for actual branch-tip review.
- `codex_packet_handoff/tools/planner.py`: supports explicit reviewed implementation heads/ranges when emitting feature packets.
- `src/qual/engine/retrieval/__init__.py`: exports canonical retrieval query and bundle helper surface.
- `src/qual/engine/retrieval/embeddings_strategy.py`: adds fallback-only embeddings compatibility shim.
- `src/qual/engine/retrieval/fts_strategy.py`: implements FTS strategy behavior, cache isolation, and explicit cache invalidation.
- `src/qual/engine/retrieval/pageindex_strategy.py`: adds fallback-only PageIndex compatibility shim.
- `src/qual/engine/retrieval/payload.py`: normalizes deterministic retrieval payload/source/context/excerpt bundles and basket-promotion fields.
- `src/qual/retrieval/__init__.py`: exports retrieval facade helpers for FTS and auto retrieval paths.
- `src/qual/retrieval/service.py`: implements FTS-first service behavior, provenance/citation/basket payloads, excerpt lookup, and cache invalidation after document updates.
- `tests/unit/test_packet_planner.py`: covers reviewed-head packet planner traceability.
- `tests/unit/test_unified_retrieval.py`: covers FTS-first retrieval, deterministic payloads, fallback boundaries, excerpt lookup, basket promotion, and cache invalidation.

## Post-`adfa8cd` Implementation Accounting

The following post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` commits are implementation/test changes and are included in the reviewed branch-tip range:

- `2871ebf7d`: retrieval code/test changes while narrowing the merge candidate.
- `7fdc76aee`: basket promotion payload support in retrieval payload/service code.
- `798639e00`: basket promotion payload enrichment in retrieval service code.
- `bd44dd163`: basket payload reconstruction in retrieval payload code.
- `c573b77fd`: sparse payload basket ID derivation in retrieval payload code.
- `02c1833d2`: FTS cache invalidation after document updates plus regression coverage.

The intervening commits that only edit `THREAD_PACKET.md` remain metadata-only packet refreshes. They are included in the branch history but are not used to hide or exclude the implementation commits above.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; the cumulative reviewed range is folded into four meaningful tasks under the high-risk cap.
- Changed files in reviewed range: `13`; this exceeds the high-risk `<=8` guideline and is explicitly called out for re-review because the packet must cover the actual branch tip rather than hide implementation commits.
- Net LOC in reviewed range: `1959 insertions(+), 272 deletions(-)`; this exceeds the high-risk `<=300` guideline and is explicitly called out for integrator risk assessment.
- Integrator-locked files touched: none.
- Shared-by-approval files touched: `codex_packet_handoff/tools/planner.py`, `tests/unit/test_packet_planner.py`, and `tests/unit/test_unified_retrieval.py`.
- Lane-owned implementation files touched: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`.
- Routing/provider impact: none; no model routing or provider configuration is touched.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Real workflow loop, with Milestone 4 Retrieval Layer groundwork.
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

- No implementation blocker is known.
- The reviewed range is larger than the high-risk size guideline because the branch already contains post-`adfa8cd` retrieval implementation commits; this packet now exposes that risk instead of classifying those commits as metadata-only.
- Direct writes to `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` were blocked by filesystem permissions in this worktree, so the corrected packet source of truth is `THREAD_PACKET.md`.
