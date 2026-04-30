## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Branch tip before this required-fixes packet edit: `2ad0e2489a4e8eab6f81d07f335c65f3bfd65838`
- Prior fixer branch tip before this required-fixes pass: `2ad0e2489a4e8eab6f81d07f335c65f3bfd65838`
- Final branch tip: reported in the fixer deliverable after this packet commit is created.
- Authoritative reviewed range / complete merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`
- Reviewer-reported stale reviewed range: `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Full post-stale-anchor delta classified by this packet: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`
- Current required-fixes packet delta covered by this packet: `2ad0e2489a4e8eab6f81d07f335c65f3bfd65838..HEAD`
- Scope classification: high-risk retrieval work because approved shared regression coverage in `tests/unit/test_unified_retrieval.py` is part of the reviewed candidate.

## Scope Completed

This packet chooses the actual branch tip as the merge candidate. The approval target is the complete merge-base-to-HEAD range, not the stale `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice and not a metadata-only refresh chain.

The reviewer-cited post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` delta is intentionally included for re-review when it modifies retrieval implementation and shared regression tests. Those changes are not classified as metadata-only. The complete post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` delta is classified by path:

- Source/test implementation: any commit after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` that modifies `src/qual/engine/retrieval/**`, `src/qual/retrieval/service.py`, or `tests/unit/test_unified_retrieval.py`.
- Packet metadata only: commits whose effective file changes are limited to `THREAD_PACKET.md`, `.codex/kickoff_packets/feat-retrieval-fts.md`, and `.codex/lane_meta/feat-retrieval-fts.json`.
- Out of scope and absent from the reviewed candidate: transient packet-tooling commits that touched `codex_packet_handoff/**` or `tests/unit/test_packet_planner.py`; the final `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` diff contains no changes to those paths.

The complete post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` source/test implementation delta is in:

The reviewer-cited commit `c2741f8e58b59e8e37240b2271b9b68bbf6141ec` is therefore treated as retrieval implementation, not metadata-only packet refresh work.

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

The merge candidate advances FTS-first retrieval by normalizing engine retrieval boolean constraints and query text/scope snapshots, keeping FTS cache and query snapshots deterministic, carrying date-range constraints into derived FTS shortlist queries and basket-promotion refs, preserving basket-promotion references and provenance, carrying promotion-ready excerpt text/title hints and query context into retrieval evidence fallbacks, deriving missing query fingerprints from canonical query snapshots during sparse payload reconstruction, normalizing sparse source-bundle query snapshots with the same text, scope, intent, confidentiality, max-results, doc-type, citation, section-hint, and exact-match rules used by canonical query fingerprints, adding query/result fingerprints to standalone doc and excerpt citation rows, invalidating stale FTS cache state on document updates, falling back from invalid direct context snapshots to canonical source/payload reconstruction, normalizing reconstructed basket item IDs to stable text IDs for downstream basket gathering, and falling back to excerpt IDs for sparse promotion refs that do not carry item IDs.

The candidate stays inside the active MVP note: FTS-first retrieval, deterministic provenance/excerpts, and basket/workflow-ready structured payloads. It does not include packet-tooling changes, router/provider changes, or Textual UI console work.

## Tasks Completed

1. Canonical demo-path step advanced: `retrieve relevant material`. Normalize engine facade query constraints, boolean flags, date ranges, doc types, required query text/scope snapshots, and derived FTS shortlist snapshots so repeated FTS retrieval is deterministic without cached hit reuse.
2. Canonical demo-path step advanced: `retrieve relevant material`. Keep SQLite FTS authoritative for excerpt lookup, reject non-FTS excerpt normalization, preserve ranked IDs, document identities, confidentiality profiles, section hints, and excerpt provenance.
3. Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket`. Preserve basket-promotion refs, stable text item IDs, citation refs, provenance fingerprints, source/context bundles, excerpt text, title hints, normalized loose query snapshots, date-range context, query fingerprints, and result fingerprints during sparse payload, provenance, citation, and context-bundle reconstruction so retrieved material stays stable for downstream basket gathering, including sparse excerpt promotion refs that omit `item_id`.
4. Canonical demo-path step advanced: `retrieve relevant material`; supports `promote or gather context into the basket`. Harden cache invalidation and fallback reconstruction for document updates, sparse direct context snapshots, and generic context-bundle helpers while keeping PageIndex and embeddings fallback-only. Identical queries after `add_or_update_document` now retrieve updated FTS material rather than stale cached excerpts.

## Canonical Demo Path

- Canonical demo-path step advanced: `retrieve relevant material`.
- Primary step made more real: `retrieve relevant material`.
- Secondary step made more real: `promote or gather context into the basket`, where structured retrieval payloads now carry deterministic excerpt payloads, provenance fingerprints, source/context bundle refs, basket-promotion item refs, stable text item IDs, query context, date-range context, derived query fingerprints, result fingerprints, and citation metadata so downstream workflows can gather the same retrieved material without depending on PageIndex-only or embedding-only paths.

## Files Changed

Complete source/test implementation files for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`:

- `src/qual/engine/retrieval/__init__.py` - lane-owned retrieval facade/export behavior via `src/qual/engine/retrieval/**`; maps to `retrieve relevant material`.
- `src/qual/engine/retrieval/fts_strategy.py` - lane-owned FTS retrieval strategy and cache behavior via `src/qual/engine/retrieval/**`; maps to `retrieve relevant material`.
- `src/qual/engine/retrieval/payload.py` - lane-owned retrieval payload construction, sparse query fingerprint derivation, and sparse basket item ID reconstruction via `src/qual/engine/retrieval/**`; maps to `retrieve relevant material` and `promote or gather context into the basket`.
- `src/qual/retrieval/service.py` - lane-owned retrieval service behavior and standalone citation fingerprints via `src/qual/retrieval/**`; maps to `retrieve relevant material`.
- `tests/unit/test_unified_retrieval.py` - shared-by-approval regression coverage for the canonical retrieval contract; maps to `retrieve relevant material` and `promote or gather context into the basket`.
- `THREAD_PACKET.md` - authoritative handoff packet required by `INTEGRATION.md`.

Source/test implementation stat for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`: `5 files changed, 440 insertions(+), 85 deletions(-)`.

Reviewer-required post-stale-anchor source/test implementation stat for `adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD`: `5 files changed, 440 insertions(+), 85 deletions(-)`.

Post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` commit classification for the actual merge candidate:

- Source/test implementation commits are every post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` commit returned by `git log adfa8cdadd43747ffbcb612e4151e262b13e52ca..HEAD -- src/qual/engine/retrieval src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py`. These commits are implementation/test work and must not be reviewed as metadata-only.
- Packet metadata-only commits are every post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` commit whose changed paths are limited to `THREAD_PACKET.md`, `.codex/kickoff_packets/feat-retrieval-fts.md`, or `.codex/lane_meta/feat-retrieval-fts.json`.
- Out-of-scope transient commits are any post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` commits that touched `codex_packet_handoff/**` or `tests/unit/test_packet_planner.py`; those paths are absent from the final reviewed candidate and are not part of this merge request.
- The reviewer-cited `c2741f8e58b59e8e37240b2271b9b68bbf6141ec` commit modifies retrieval implementation and shared regression coverage, so it is source/test implementation, not metadata-only.
- The current `2ad0e2489a4e8eab6f81d07f335c65f3bfd65838..HEAD` required-fixes delta is packet metadata only until the final commit is created.

Lane-owned source/test files in the reviewed candidate:

- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`

Shared-by-approval source/test files in the reviewed candidate:

- `tests/unit/test_unified_retrieval.py`

Integrator-locked files in the reviewed candidate:

- None.

Out-of-scope files absent from the reviewed candidate:

- `codex_packet_handoff/tools/planner.py`
- `tests/unit/test_packet_planner.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`

`THREAD_PACKET.md` is the authoritative handoff packet for this re-review. The `.codex` mirror files are stale best-effort summaries only; the single authoritative range and commit classification are the fields in this file.

Attempted mirror update during this required-fixes pass was blocked by the filesystem sandbox: editing `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` was rejected as outside the writable project. Reviewers must ignore the stale `.codex` mirror range and use `THREAD_PACKET.md`.

Merge-conflict resolution status for this required-fixes pass:

- `git status --short --branch` reported a clean `codex/feat-retrieval-fts` worktree at `2ad0e2489a4e8eab6f81d07f335c65f3bfd65838` before this packet edit.
- `git diff --name-only --diff-filter=U` reported no unresolved paths.
- `rg -n "^<{7}|^={7}|^>{7}" src/qual/engine/retrieval src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py THREAD_PACKET.md` reported no conflict markers.
- The reviewer-cited conflicts in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, and `src/qual/retrieval/service.py` are resolved in the actual branch tip and remain part of the complete `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` review range.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `5/8` high-risk source/test files plus packet metadata files.
- Net LOC budget: source/test implementation changes are `5 files changed, 440 insertions(+), 85 deletions(-)`, or +355 net LOC, which exceeds the `<=300` high-risk net LOC limit after cumulative reviewer-fix implementation commits. Packet metadata is accounted separately.
- Size exception required: yes; re-review should explicitly accept the +355 source/test net LOC candidate or request a split.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py` only.
- Integrator-locked files: none.
- Routing/provider impact: none.
- PageIndex/embeddings impact: fallback-only; neither is reintroduced as a required retrieval path.
- Merge risk: high until this corrected actual-tip packet is reviewed, because the branch tip includes implementation beyond the stale `adfa8cdad` anchor.

## Roadmap/Vision

- Roadmap items affected: `ROADMAP.md` MVP focus for FTS-first retrieval and Milestone 3 product-readiness provenance/output-contract work.
- Vision capabilities affected: `PRODUCT_VISION.md` capability 2 Retrieval-first context handling and capability 3 Auditable generation.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates re-run for this corrected actual-tip merge candidate:

- `make scope-check` PASS for branch `codex/feat-retrieval-fts`; no branch policy was configured, so scope-check skipped policy enforcement and passed.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS, Python sources under `src/` compile.
- `make ci` PASS, 125 tests; includes scope-check, format, lint, typecheck, and test gates.

Additional fixer probes:

- `git status --short --branch` PASS: clean branch state before packet edit; no unresolved merge/conflict state.
- `rg -n "^<{7}|^={7}|^>{7}" src/qual/engine/retrieval src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py THREAD_PACKET.md` PASS: no conflict markers found.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
