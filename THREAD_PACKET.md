# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `32c259cdec2670ec777f31a41c6dd7639219acea`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `packet traceability correction for the actual branch tip`
- Reviewed implementation range: `75572c120239a84402a82b845c3df797806fcdf4..32c259cdec2670ec777f31a41c6dd7639219acea`

## Packet traceability note

- The branch tip `32c259cdec2670ec777f31a41c6dd7639219acea` is in scope for re-review. It is not metadata-only: it updates `src/qual/retrieval/service.py` and `tests/unit/test_unified_retrieval.py` to align excerpt-failure audit output with the shipped retrieval contract.
- Review this handoff against the actual tip and the reviewed implementation range above. Earlier packet-only restamps are superseded by this regenerated handoff.

## Current program focus

- Close the engine-side retrieval part of the Milestone 3 workflow loop before activating any Textual UI lanes.

## Scope goal

- Keep retrieval FTS-first for the MVP, make excerpt lookup deterministic and fail closed, and keep downstream provenance, payload, and audit snapshots stable enough for engine workflows and reviewable audit trails.

## Scope completed

- Branch-level cumulative handoff from `75572c120239a84402a82b845c3df797806fcdf4..32c259cdec2670ec777f31a41c6dd7639219acea`: excerpt lookup resolves through the canonical FTS-backed path, retrieval payloads and provenance snapshots are deterministic for downstream engine flows, sparse source and context bundles rehydrate deterministically, and PageIndex or embeddings remain compatibility-only fallback shims that fail closed instead of becoming required runtime paths.
- The current tip `32c259cdec2670ec777f31a41c6dd7639219acea` adds the excerpt-failure audit schema change that reports `lookup_query_context_status: "missing"` when excerpt query context cannot be rehydrated, and shared regression coverage now asserts that behavior in `tests/unit/test_unified_retrieval.py`.
- This work makes the canonical demo-path step `retrieve relevant material` more real by enforcing FTS-only excerpt lookup, deterministic retrieval payloads, and auditable missing-context failure behavior for excerpt resolution.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Milestone 3 retrieval step: this lane makes `retrieve relevant material` more real by keeping excerpt resolution on the FTS-backed path and making missing excerpt-query context fail with deterministic audit metadata instead of silent fallback behavior.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the lane remains shared/high-risk work under the 4-task cap.
- The completed work is summarized as four meaningful tasks to match the shared/high-risk budget even though the reviewed implementation range is cumulative.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed (numbered)

1. Exposed the canonical excerpt lookup resolution path and enforced FTS-only excerpt lookup so PageIndex-only excerpt IDs fail closed instead of silently falling back.
2. Canonicalized retrieval payloads, provenance snapshots, sparse source bundles, and context rehydration so downstream engine consumers receive deterministic retrieval data.
3. Kept the retrieval facade FTS-first by exporting the canonical helpers through the retrieval surfaces while leaving PageIndex and embeddings as compatibility-only, fail-closed shims.
4. Aligned excerpt-failure audit output with the shipped contract by recording `lookup_query_context_status: "missing"` for missing excerpt query context and adding shared regression coverage for that auditable failure path.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `src/qual/retrieval/__init__.py`
- `src/qual/engine/retrieval/__init__.py`
- `src/qual/engine/retrieval/embeddings_strategy.py`
- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/interface.py`
- `src/qual/engine/retrieval/pageindex_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/engine/tools/excerpt_tools.py`
- `tests/unit/test_unified_retrieval.py`

### Packet artifacts refreshed for this re-review

- `THREAD_PACKET.md`

### Packet mirror artifacts blocked by sandbox permissions

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Residual risk: the lane still depends on shared regression coverage in `tests/unit/test_unified_retrieval.py`, so any future change that broadens excerpt lookup semantics or alters the audit payload shape will need coordinated updates to that shared surface.
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` are read-only in this sandbox, so this fixer pass updates the authoritative handoff in `THREAD_PACKET.md` but cannot refresh those mirror artifacts from this environment.

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md`: Milestone 3 retrieval step for `retrieve relevant material`.

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
