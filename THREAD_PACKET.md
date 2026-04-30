## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Lane: `feat-retrieval-fts`
- Merge target: current `main`
- Merge-base for re-review: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4`
- Actual branch tip reviewed by the CHANGES_REQUESTED packet: `a12ff6ce00468b15876cdda70eb722da218e4d66`
- Prior fixer branch tip before this required-fixes pass: `4f6c5646eeacecfbbfa25a72d90435e895792a39`
- Final branch tip: reported in the fixer deliverable after this packet commit is created.
- Authoritative reviewed range / complete merge candidate: `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`
- Reviewer-reported stale reviewed range: `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewer-required supplemental implementation delta now covered by this packet: `adfa8cdadd43747ffbcb612e4151e262b13e52ca..e99593b66e`
- Prior packet-metadata refresh delta covered by this packet: `e99593b66e..28b0309be1fb348aaf0e61daf6b9214600c26bee`
- Prior conflict-resolution/packet delta covered by this packet: `28b0309be1fb348aaf0e61daf6b9214600c26bee..a12ff6ce00468b15876cdda70eb722da218e4d66`
- Prior fixer packet-metadata delta covered by this packet: `a12ff6ce00468b15876cdda70eb722da218e4d66..e6f04ffa4dc0a5106e44caf40527eeb47f7e3e17`
- Prior fixer packet-metadata delta covered by this packet: `e6f04ffa4dc0a5106e44caf40527eeb47f7e3e17..4f6c5646eeacecfbbfa25a72d90435e895792a39`
- Prior required-fixes packet delta covered by this packet: `4f6c5646eeacecfbbfa25a72d90435e895792a39..d070ec12fb796af2a582e03ac73c34b33c3855d5`
- Current feature-lane implementation delta covered by this packet: `d070ec12fb796af2a582e03ac73c34b33c3855d5..HEAD`
- Scope classification: high-risk retrieval work because approved shared regression coverage in `tests/unit/test_unified_retrieval.py` is part of the reviewed candidate.

## Scope Completed

This packet chooses the actual branch tip as the merge candidate. The approval target is the complete merge-base-to-HEAD range, not the stale `378cf9a74..adfa8cdadd43747ffbcb612e4151e262b13e52ca` slice and not a metadata-only refresh chain.

The reviewer-cited post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` delta is intentionally included for re-review when it modifies retrieval implementation and shared regression tests. Those changes are not classified as metadata-only. It contains retrieval implementation and shared regression changes in:

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

Source/test implementation stat for `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD`: `5 files changed, 373 insertions(+), 97 deletions(-)`.

Reviewer-required supplemental source/test implementation stat for `adfa8cdadd43747ffbcb612e4151e262b13e52ca..e99593b66e`: `5 files changed, 424 insertions(+), 84 deletions(-)`.

Post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` commit classification for the actual merge candidate:

- Retrieval implementation/test commits in the final `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` candidate are: `bd44dd163`, `c573b77fd`, `02c1833d2`, `d276ca07a`, `0e86dfbb8`, `b65733d6f`, `6bd4f5c67`, `c620f6c71`, `22fbd1236`, `74e550e2b`, `8608095c1`, `5a88788b7`, `a84e12ada`, `8a637b0c3`, `0aea8aed6`, `bf75a8d52`, `a55871203`, `6af5013f0`, `b9eb05813`, `5a3e75759`, `1ea30e71f`, and `c2741f8e5`. These are implementation/test work, not metadata-only.
- `c2741f8e5` is the reviewer-cited post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` implementation/test commit and remains included in the reviewed candidate.
- Packet-only commits from `e99593b66e` through the pre-fixer tip, plus `e6f04ffa4dc0a5106e44caf40527eeb47f7e3e17..4f6c5646eeacecfbbfa25a72d90435e895792a39`, are metadata-only because their effective diff is limited to `THREAD_PACKET.md` and locked `.codex` packet mirrors.
- Any transient post-`adfa8cdadd43747ffbcb612e4151e262b13e52ca` packet-tooling changes are absent from the actual reviewed candidate; `git diff --name-status fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` contains no `codex_packet_handoff/**` or `tests/unit/test_packet_planner.py` entries.
- The prior `4f6c5646eeacecfbbfa25a72d90435e895792a39..d070ec12fb796af2a582e03ac73c34b33c3855d5` required-fixes delta is packet metadata only.
- The current `d070ec12fb796af2a582e03ac73c34b33c3855d5..HEAD` feature-lane delta is retrieval implementation plus packet metadata. It normalizes sparse source-bundle query snapshots in `src/qual/engine/retrieval/payload.py` and updates this handoff packet.

Prior packet-metadata refresh delta for `e99593b66e..28b0309be1fb348aaf0e61daf6b9214600c26bee`: packet metadata only; no source/test implementation files.

Prior conflict-resolution/packet delta for `28b0309be1fb348aaf0e61daf6b9214600c26bee..a12ff6ce00468b15876cdda70eb722da218e4d66`: packet metadata and conflict-resolution state only; no source/test implementation files.

Prior fixer packet-metadata delta for `a12ff6ce00468b15876cdda70eb722da218e4d66..e6f04ffa4dc0a5106e44caf40527eeb47f7e3e17`: packet metadata only; no source/test implementation files.

Prior fixer packet-metadata delta for `e6f04ffa4dc0a5106e44caf40527eeb47f7e3e17..4f6c5646eeacecfbbfa25a72d90435e895792a39`: packet metadata only; no source/test implementation files.

Prior required-fixes packet delta for `4f6c5646eeacecfbbfa25a72d90435e895792a39..d070ec12fb796af2a582e03ac73c34b33c3855d5`: packet metadata only; no source/test implementation files.

Current feature-lane delta for `d070ec12fb796af2a582e03ac73c34b33c3855d5..HEAD`: retrieval implementation and packet metadata; source/test implementation files are limited to `src/qual/engine/retrieval/payload.py`.

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

Packet mirror files could not be updated in this fixer commit because this sandbox returns `Operation not permitted` for writes under `.codex/kickoff_packets/` and `.codex/lane_meta/`. The stale `.codex` mirrors still refer to the older `adfa8cdadd43747ffbcb612e4151e262b13e52ca` boundary and must not be used for this re-review.

Stale locked mirror paths:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

`THREAD_PACKET.md` is the authoritative handoff packet for this re-review.

Merge-conflict resolution status for this required-fixes pass:

- `git status --short --branch` reported a clean `codex/feat-retrieval-fts` worktree at `4f6c5646eeacecfbbfa25a72d90435e895792a39` before this packet edit.
- `git diff --name-only --diff-filter=U` reported no unresolved paths.
- `rg -n "^<{7}|^={7}|^>{7}" src/qual/engine/retrieval src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py THREAD_PACKET.md` reported no conflict markers.
- The reviewer-cited conflicts in `src/qual/engine/retrieval/__init__.py`, `src/qual/engine/retrieval/fts_strategy.py`, `src/qual/engine/retrieval/payload.py`, and `src/qual/retrieval/service.py` are resolved in the actual branch tip and remain part of the complete `fd2ab6ca65ec2f93d1334c9b7df8512439725be4..HEAD` review range.

## Budget/Risk

- Task budget: `4/4` high-risk tasks.
- File budget: `5/8` high-risk source/test files plus packet metadata files.
- Net LOC budget: source/test implementation changes are `5 files changed, 373 insertions(+), 97 deletions(-)`, or +276 net LOC, which remains within the `<=300` high-risk net LOC limit. Packet metadata is accounted separately.
- Size exception required: none.
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

- `python -m compileall -q src/qual/engine/retrieval/payload.py` PASS.
- `make scope-check` PASS for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check` PASS.
- `./quality-lint.sh` PASS.
- `./quality-test.sh` PASS, 125 tests.
- `./typecheck-test.sh` PASS, Python sources under `src/` compile.
- `make ci` PASS, 125 tests; includes scope-check, format, lint, typecheck, and test gates.

Additional fixer probes:

- `python -m pytest tests/unit/test_unified_retrieval.py` could not run because the active Python interpreter does not have `pytest` installed.
- First `./quality-test.sh` run failed one expected-shape assertion in `test_engine_retrieval_tool_returns_canonical_downstream_payload` after citation rows gained query/result fingerprints; the assertion was updated and the full suite passed on rerun.

## Risks/Blockers

Remaining risk is review risk from high-risk retrieval scope and approved shared test coverage. The candidate does not widen retrieval strategy scope, does not make PageIndex or embeddings required paths, does not touch model routing/provider configuration, and keeps Textual UI lanes disabled.
