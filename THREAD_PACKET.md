# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Current branch tip: `50b15f7823e0237ba0469a53194a84c0d63e4a1f`
- Packet role at branch tip: `metadata-only reviewer-fix handoff alignment`
- Reviewed implementation head: `82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7`
- Metadata-only post-implementation range: `82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7..50b15f7823e0237ba0469a53194a84c0d63e4a1f`

## Scope goal

- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.
- Risk reason: the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Checkpoint Status

- `plan complete`: refreshed all retrieval handoff artifacts to point at the real implementation head and actual packet-only tail.
- `first green tests`: all required gates were rerun on the branch tip for this fixer pass.
- `before risky/shared file edit`: the only shared implementation file in scope remains the approved regression surface `tests/unit/test_unified_retrieval.py`.
- `ready for handoff`: packet traceability, scope, files changed, and high-risk framing now match the branch being proposed.

## Budget classification

- Shared/high-risk handoff under the `4`-task cap because the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- The post-implementation span `82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7..50b15f7823e0237ba0469a53194a84c0d63e4a1f` is metadata-only in this worktree and changes only `THREAD_PACKET.md`.

## Scope completed

- Kept SQLite FTS as the authoritative retrieval path for the MVP branch scope.
- Exported and normalized the canonical retrieval helpers and payload snapshots through the retrieval facades used by the engine compatibility surface.
- Removed PageIndex as a required excerpt lookup path so canonical excerpt fetches fail closed on FTS-backed identifiers.
- Hardened retrieval evidence, provenance, and cache isolation so downstream basket-promotion and workflow consumers receive deterministic, auditable payloads.

## Canonical demo-path step advanced

- `retrieve relevant material`

This reviewed range makes `retrieve relevant material` more real by keeping excerpt lookup, result payloads, and provenance deterministic on the FTS-first path that downstream basket-promotion consumers use.

## Required reviewer fixes addressed

1. Regenerated the handoff against the actual review target by naming the real branch tip `50b15f7823e0237ba0469a53194a84c0d63e4a1f`, the real implementation head `82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7`, and the implementation range `378cf9a74a3658058079a32f186fcd254c4a4034..82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7`.
2. Corrected the traceability note so the packet no longer claims runtime-changing commits after `adfa8cdadd43747ffbcb612e4151e262b13e52ca` are metadata-only.
3. Recomputed `Scope completed` and `Files changed` against the corrected implementation head and packet-only tail.
4. Reconciled the AGENTS framing so all handoff artifacts treat the approved shared test edit as shared/high-risk work under the `4`-task cap.

## Tasks completed

1. Exported canonical retrieval helpers and normalized retrieval payload contracts through the retrieval facades used by the engine compatibility surface.
2. Kept retrieval FTS-first, including FTS-only excerpt lookup behavior and compatibility shims that fail closed instead of restoring PageIndex as a required path.
3. Hardened deterministic provenance, source/context bundles, and cache isolation for downstream engine and basket-promotion flows.
4. Added and kept approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval contract.

## Files changed

- Reviewed implementation files:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Reviewed packet-alignment files within the implementation range:
  - `.codex/kickoff_packets/feat-retrieval-fts.md`
  - `.codex/lane_meta/feat-retrieval-fts.json`
  - `THREAD_PACKET.md`
- Metadata-only post-implementation file changes on the current branch tip:
  - `THREAD_PACKET.md`

## Traceability note

- Re-review should anchor retrieval implementation scope to `378cf9a74a3658058079a32f186fcd254c4a4034..82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7`.
- The current branch tip is `50b15f7823e0237ba0469a53194a84c0d63e4a1f`.
- In this worktree, the post-implementation span `82fe746eb8d59ecb591e4fec5ad0c0373f8cd9b7..50b15f7823e0237ba0469a53194a84c0d63e4a1f` is metadata-only and changes only `THREAD_PACKET.md`.
- If a later branch tip changes retrieval runtime files or `tests/unit/test_unified_retrieval.py`, the packet must be regenerated before approval.

## Commands run with results

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`

## Risks / blockers

- Risk: `HIGH`
- Blockers: none

## Required handoff fields

### Roadmap item(s) affected

- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts`

### Vision capability affected

- `Retrieval-first context handling`
- `Auditable state and workflow`

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
