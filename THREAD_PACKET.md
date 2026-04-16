## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `metadata-only reviewer-fix finalization`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh commit: `df05d063dfec3d8ed15a625a0044f090853a9011`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt, provenance, and evidence output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the narrowed slice. The reviewed implementation commit removes the PageIndex fallback from `fetch_excerpt`, keeping excerpt lookup on the canonical FTS-only path, while approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`. PageIndex and embeddings remain non-required compatibility paths in this slice.

## Canonical demo-path step advanced
- `retrieve relevant material`: this handoff explicitly advances that canonical demo-path step by enforcing FTS-only excerpt resolution with deterministic provenance on the canonical retrieval surface. Retrieval hits, excerpt lookup payloads, and downstream evidence/provenance bundles now stay deterministic and auditable on the FTS-first path.

## AGENTS.md handoff packet
- Risk reason: shared/high-risk work because the reviewed implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Required checkpoint status notes:
  - `plan complete`: the packet is now anchored to the narrowed reviewed implementation head and reviewed range in the reviewer packet.
  - `first green local tests`: the required gate sweep is rerun on the metadata-only packet correction commit.
  - `before risky/shared file edit`: no new risky/shared implementation files were edited in this fixer pass; the reviewed implementation range still includes the approved shared regression file.
  - `ready for handoff`: the packet traceability is internally consistent and required gates are rerun.
- Tasks completed:
  1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves through the canonical FTS-only path.
  2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt IDs fail closed with `KeyError`.
- Files changed:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`

## Commands run with results
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risks: high, because the narrowed reviewed range includes approved shared regression coverage.
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
