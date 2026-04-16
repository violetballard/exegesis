## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `feature implementation + handoff packet`
- Reviewed implementation head: `25c2d2093ea0b302f0d64985831f2f679bb62b29`
- Reviewed implementation range: `c55390593445b97a28a5b4520641c2c26b70788f..25c2d2093ea0b302f0d64985831f2f679bb62b29`

## Scope completed
- Hardened engine retrieval payload reconstruction so sparse `retrieval_doc_bundle` and `retrieval_excerpt_bundle` snapshots are backfilled from the surrounding canonical payload instead of remaining partially populated.
- Kept the lane FTS-first and retrieval-owned by limiting the implementation change to `src/qual/engine/retrieval/payload.py`.
- Preserved deterministic downstream retrieval output shapes for basket promotion and engine workflow consumers when callers provide partial bundle snapshots.

## Canonical demo-path step advanced
- `retrieve relevant material`: sparse retrieval bundle snapshots now reconstruct deterministically from the canonical retrieval payload, which keeps excerpt/doc provenance packaging stable for downstream engine generation flows.

## AGENTS.md handoff packet
- Risk reason: low-risk retrieval-owned payload helper hardening only; no shared or integrator-locked product files were edited in the implementation commit.
- Task budget: `8`
- Required checkpoint status notes:
  - `plan complete`: scope was narrowed to retrieval-owned payload reconstruction for the FTS-first lane before editing.
  - `first green local tests`: `./tests/unit.sh tests/unit/test_unified_retrieval.py` passed before the final gate sweep.
  - `before risky/shared file edit`: no risky/shared implementation files were edited for the retrieval change.
  - `ready for handoff`: required gates passed and the reviewed implementation commit is recorded below.
- Tasks completed:
  1. Backfilled sparse retrieval doc bundles from the surrounding canonical payload when callers provide only partial `retrieval_doc_bundle` snapshots.
  2. Backfilled sparse retrieval excerpt bundles from the surrounding canonical payload when callers provide only partial `retrieval_excerpt_bundle` snapshots.
  3. Re-ran the retrieval regression surface and full required gates to confirm the FTS-first downstream contract stayed green.
- Files changed:
  - `src/qual/engine/retrieval/payload.py`
  - `THREAD_PACKET.md`

## Commands run with results
- `./tests/unit.sh tests/unit/test_unified_retrieval.py`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/blockers
- Risks: low; the change is limited to payload backfill helpers and preserves the existing FTS-first retrieval policy and canonical engine surface.
- Blockers: none

## Roadmap item(s) affected
- `ROADMAP.md`: `Milestone 4: Retrieval Layer`
- `ROADMAP.md`: `Milestone 3: Product Readiness`

## Vision capability affected
- `PRODUCT_VISION.md`: `2. Retrieval-first context handling`
- `PRODUCT_VISION.md`: `3. Auditable generation`

## Routing/provider impact note
- None

## Proposed README.md patch text
- None
