# Thread Handoff Packet

- Lane: `feat-retrieval-fts`
- Branch: `codex/feat-retrieval-fts`
- Commit: `6e963e1b209cec127e7da6734aa5ca3328a05f88`
- Packet refresh commit: `reported in final fixer handoff`
- Packet refresh role: `packet traceability correction for the actual branch tip`
- Reviewed implementation range: `75572c120239a84402a82b845c3df797806fcdf4..6e963e1b209cec127e7da6734aa5ca3328a05f88`

## Packet traceability note

- The current non-metadata implementation head for this handoff is `6e963e1b209cec127e7da6734aa5ca3328a05f88`, not `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
- The handed-off retrieval implementation range now includes `d31e408e631adf1e3ae1fb660449510a33715de7`, `32c259cdec2670ec777f31a41c6dd7639219acea`, and `6e963e1b209cec127e7da6734aa5ca3328a05f88`, so re-review covers the real in-scope code path through the current implementation tip.
- Earlier packet-only restamps are superseded by this regenerated handoff.
- This fixer pass regenerates the packet artifacts only; use the final fixer handoff for the metadata-only packet refresh commit SHA created by this pass.

## Current program focus

- Close the engine-side retrieval part of the Milestone 3 workflow loop before activating any Textual UI lanes.

## Scope goal

- Keep retrieval FTS-first for the MVP, make excerpt lookup deterministic and fail closed, and keep downstream provenance, payload, and audit snapshots stable enough for engine workflows and reviewable audit trails.

## Scope completed

- Branch-level cumulative handoff from `75572c120239a84402a82b845c3df797806fcdf4..6e963e1b209cec127e7da6734aa5ca3328a05f88`: excerpt lookup resolves through the canonical FTS-backed path, retrieval payloads and provenance snapshots are deterministic for downstream engine flows, sparse source and context bundles rehydrate deterministically, and PageIndex or embeddings remain compatibility-only fallback shims that fail closed instead of becoming required runtime paths.
- The current reviewed implementation head `6e963e1b209cec127e7da6734aa5ca3328a05f88` deep-copies policy snapshots before response shaping so retrieval metadata cannot be mutated through aliasing. The preceding in-scope commits `d31e408e631adf1e3ae1fb660449510a33715de7` and `32c259cdec2670ec777f31a41c6dd7639219acea` keep provenance source bundles canonical and align excerpt-failure audit output to report `lookup_query_context_status: "missing"` when excerpt query context cannot be rehydrated.
- This work makes the canonical demo-path step `retrieve relevant material` more real by enforcing FTS-only excerpt lookup, deterministic retrieval payloads, isolated policy snapshots, and auditable missing-context failure behavior for excerpt resolution.

## Canonical demo-path step advanced

- `retrieve relevant material`
- Canonical demo-path statement: This work makes the `retrieve relevant material` step more real by enforcing FTS-only excerpt lookup, deterministic retrieval payloads, isolated policy snapshots, and auditable missing-context failure behavior for excerpt resolution.

## Reviewer fix reconciliation

- The reviewed implementation range now matches the actual handed-off implementation tip: `75572c120239a84402a82b845c3df797806fcdf4..6e963e1b209cec127e7da6734aa5ca3328a05f88`.
- The scope and tasks now disclose every code/test change still in reviewed scope, including canonical provenance normalization, the excerpt-failure audit schema change `lookup_query_context_status: "missing"`, and policy snapshot deep-copy isolation.
- The packet explicitly names the canonical demo-path step `retrieve relevant material` and states how this work makes that step more real.
- Reviewer and integrator now evaluate the same change set because the reviewed implementation head, files changed, and scope summary all point to the same in-scope retrieval tip.

## Kickoff budget/limits compliance

- This handoff includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`, so the packet is shared/high-risk work and should be read against the 4-task cap.
- The completed work is summarized as four meaningful tasks to match the shared/high-risk budget even though the reviewed implementation range is cumulative.

## Approved exception note

- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the `feat-retrieval-fts` lane; it is the sole shared-by-approval regression surface for the lane and exercises the canonical retrieval contract.

## Tasks completed (numbered)

1. Exposed the canonical excerpt lookup resolution path and enforced FTS-only excerpt lookup so PageIndex-only excerpt IDs fail closed instead of silently falling back.
2. Canonicalized retrieval payloads, provenance snapshots, sparse source bundles, and context rehydration so downstream engine consumers receive deterministic retrieval data.
3. Kept the retrieval facade FTS-first by exporting the canonical helpers through the retrieval surfaces while leaving PageIndex and embeddings as compatibility-only, fail-closed shims.
4. Hardened retrieval reviewability by keeping provenance source bundles canonical, reporting `lookup_query_context_status: "missing"` for missing excerpt query context, and deep-copying policy snapshots before response enrichment.

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

### Metadata-only packet artifacts refreshed by this fixer pass

- `THREAD_PACKET.md`
- `docs/gate_passed.txt`

## Commands run and outcomes

- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks / blockers

- Residual risk: the lane still depends on shared regression coverage in `tests/unit/test_unified_retrieval.py`, so any future change that broadens excerpt lookup semantics or alters the retrieval audit payload shape will need coordinated updates to that shared surface.
- Blockers: mirrored packet files under `.codex/` could not be updated with `apply_patch` in this sandbox even though the repo-visible handoff artifacts were refreshed successfully.

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
