# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `32c259cdec2670ec777f31a41c6dd7639219acea`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `metadata-only reviewer-fix finalization`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..32c259cdec2670ec777f31a41c6dd7639219acea`

## Packet traceability note

- The actual reviewed implementation tip for this handoff is `32c259cdec2670ec777f31a41c6dd7639219acea`, not `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- The branch tip being handed off includes the retrieval implementation commits `d31e408e631adf1e3ae1fb660449510a33715de7` and `32c259cdec2670ec777f31a41c6dd7639219acea`, so the reviewed implementation range is regenerated to end at `32c259cdec2670ec777f31a41c6dd7639219acea`.
- The packet-only commits `ef83180f4452742ff97f640a2471e4708d622747`, `cdd3a4c6e6e39ff1efbb1ec62b0f70b64d0af717`, `9d3573f26ede9092b31016b9bf4846e79bae2b5e`, `54e7dc0dd80607108e61477ffe9466328932a78b`, and `6a94334ea3b13e716770e2cf4e8bb17d139e3e9d` remain metadata-only.
- This fixer pass regenerates the packet artifacts only; use the final fixer handoff for the metadata-only packet refresh commit SHA created by this pass.

## Current program focus

- Close the engine-side retrieval path with deterministic, auditable FTS-first behavior before broader engine/demo-path promotion.

## Scope goal

- Keep excerpt lookup on the canonical FTS-only path, keep downstream provenance normalized from canonical source bundles, and keep failure audits schema-aligned for deterministic retrieval behavior. This lane slice makes the canonical demo-path step `retrieve relevant material` more real by enforcing FTS-only excerpt lookup, canonical source-bundle provenance, and deterministic failure audit behavior.

## Scope completed

- `adfa8cdadd43747ffbcb612e4151e262b13e52ca` removes the PageIndex fallback from `fetch_excerpt`, so excerpt lookup now resolves only through the canonical FTS path and PageIndex-only excerpt IDs fail closed.
- `d31e408e631adf1e3ae1fb660449510a33715de7` updates `src/qual/engine/retrieval/payload.py` so engine-facing provenance helpers prefer canonical source-bundle-derived provenance when both provenance surfaces are present, with regression coverage in `tests/unit/test_unified_retrieval.py`.
- `32c259cdec2670ec777f31a41c6dd7639219acea` adds `lookup_query_context_status: "missing"` to failed FTS excerpt lookup audits so failure payloads stay schema-aligned with successful lookup events, with regression coverage in `tests/unit/test_unified_retrieval.py`.
- This work makes the `retrieve relevant material` step more real by enforcing FTS-only excerpt lookup, canonical source-bundle provenance, and deterministic failure audit behavior.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path statement: This work makes the `retrieve relevant material` step more real by enforcing FTS-only excerpt lookup, canonical source-bundle provenance, and deterministic failure audit behavior.

## Reviewer fix reconciliation

- The reviewed implementation range now matches the actual handed-off tip: `378cf9a74a3658058079a32f186fcd254c4a4034..32c259cdec2670ec777f31a41c6dd7639219acea`.
- The scope and tasks now disclose every code/test change still on the handed-off tip, including canonical provenance normalization and the excerpt-failure audit schema change `lookup_query_context_status: "missing"`.
- The packet explicitly names the canonical demo-path step `retrieve relevant material` and states how this work makes that step more real.
- Reviewer and integrator now evaluate the same change set because the reviewed implementation head, files changed, and scope summary all point to the same branch tip.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap. The reviewed implementation for this packet spans 3 files and is summarized as 3 meaningful tasks, which fits the shared/high-risk size budget.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed (numbered)

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path and fails closed for PageIndex-only excerpt IDs.
2. Canonicalized engine retrieval provenance helpers in `src/qual/engine/retrieval/payload.py` to prefer source-bundle-derived provenance when direct compatibility helpers and source bundles are both present.
3. Aligned failed excerpt lookup audits with the successful lookup schema by emitting `lookup_query_context_status: "missing"` for failed FTS lookups and covering that contract in `tests/unit/test_unified_retrieval.py`.

## Files changed

### Reviewed implementation files

- `src/qual/retrieval/service.py`
- `src/qual/engine/retrieval/payload.py`
- `tests/unit/test_unified_retrieval.py`

### Writable packet artifacts refreshed by this fixer pass

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

### Packet mirror artifacts blocked in this environment

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

- Residual risk: this slice still relies on approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so any later retrieval change that broadens excerpt lookup semantics or provenance normalization will need coordinated updates to that shared test surface.
- Blockers: `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be refreshed with `apply_patch` in this environment even though the authoritative handoff files were updated.

## Required handoff fields

### Roadmap item(s) affected

- `ROADMAP.md`: Milestone 4: Retrieval Layer
- `feat-retrieval-fts`: excerpt lookup contract hardening plus canonical provenance/failure-audit normalization on the FTS-backed retrieval path.

### Vision capability affected

- Retrieval-first context handling
- Auditable state and workflow

### Routing/provider impact note

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
