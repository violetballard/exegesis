## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `metadata-only packet trace correction`
- Reviewed implementation head: `58d645da3b690f4c7e653cecb3b98f7d8036de11`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..58d645da3b690f4c7e653cecb3b98f7d8036de11`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and evidence output.

## Scope completed
- Cumulative retrieval handoff for `d7fd5d200358287fa42a18d39e2b277463b9b69f..58d645da3b690f4c7e653cecb3b98f7d8036de11`: SQLite FTS remains authoritative, canonical retrieval helpers are exposed through both retrieval facades, retrieval payload/provenance/evidence snapshots are deterministic for downstream engine flows, sparse source/context/doc/excerpt bundles rehydrate deterministically, and excerpt lookup now fails closed on the canonical FTS-only path when given PageIndex-only IDs. PageIndex and embeddings remain compatibility-only deferred strategies rather than required MVP paths.

## Canonical demo-path step advanced
- `retrieve relevant material`: retrieval hits, excerpt lookup payloads, and downstream evidence/provenance bundles now stay deterministic and auditable on the canonical FTS-first path.

## AGENTS.md handoff packet
- Risk reason: shared/high-risk work because the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Required checkpoint status notes:
  - `plan complete`: the packet is now anchored to the actual reviewed implementation head and cumulative reviewed range on this branch.
  - `first green local tests`: the required gate sweep is rerun on the metadata-only packet correction commit.
  - `before risky/shared file edit`: no new risky/shared implementation files were edited in this fixer pass; the reviewed implementation range still includes the approved shared regression file.
  - `ready for handoff`: the packet traceability is internally consistent and required gates are rerun.
- Tasks completed:
  1. Kept excerpt lookup on the canonical FTS-only path so non-FTS excerpt IDs fail closed instead of falling back to PageIndex.
  2. Canonicalized retrieval payload, provenance, and evidence snapshots, including deterministic backfills for sparse doc/excerpt/source/context bundles.
  3. Stabilized the retrieval facade surface and constraint normalization while keeping PageIndex and embeddings as compatibility-only deferred strategies.
  4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for payload normalization, facade exports, provenance helpers, and the FTS-only excerpt lookup contract.
- Files changed:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
  - `codex_packet_handoff/tools/planner.py`
  - `tests/unit/test_packet_planner.py`

## Commands run with results
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risks: high, because the cumulative reviewed range includes approved shared regression coverage and a wide retrieval surface.
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 3: Real workflow loop`

## Vision capability affected
- `PRODUCT_VISION.md`: `2. Retrieval-first context handling`
- `PRODUCT_VISION.md`: `6. Auditable state and workflow`

## Routing/provider impact note
- None

## Proposed README.md patch text
- None
