## Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Handoff type: `retrieval feature handoff for the FTS-first retrieval lane`
- Packet HEAD role: `packet-only reviewer-fix refresh after the implementation head`
- Packet refresh trace anchor before this fixer commit: `2e28b1b3a18045003a4c837b9177ec7fa6852e7e`
- Reviewed implementation head: `e8b19940cfc70e123d53c63d5846efaaa64287aa`
- Reviewed implementation range: `d7fd5d200358287fa42a18d39e2b277463b9b69f..e8b19940cfc70e123d53c63d5846efaaa64287aa`

## Scope goal
- Complete the FTS-first retrieval MVP for engine flows with deterministic excerpt and provenance output.

## Scope completed
- SQLite FTS remains the authoritative MVP retrieval path in the delivered retrieval implementation range.
- Retrieval payloads, provenance snapshots, fingerprints, and sparse bundle backfills are normalized so downstream engine consumers receive deterministic and auditable retrieval data.
- Excerpt lookup now stays on the canonical FTS path, including confidentiality-aware lookup metadata, stable lookup fingerprints, and fail-closed handling for PageIndex-only excerpt IDs.
- PageIndex and embeddings remain deferred compatibility identifiers, not required runtime retrieval paths for the MVP contract.

## Canonical Demo-Path Step Advanced
- Canonical demo-path step advanced: `retrieve relevant material`
- `fetch_excerpt` now resolves only through the canonical FTS path, which makes the retrieval step more deterministic and auditable for downstream basket/workflow use.

## Reviewer-Required Fixes Addressed
1. The handoff is regenerated around the actual delivered retrieval implementation head `e8b19940cfc70e123d53c63d5846efaaa64287aa` instead of the older narrowed slice ending at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
2. The packet no longer labels `e8b19940cfc70e123d53c63d5846efaaa64287aa` as metadata-only; it is treated as the reviewed implementation head and its retrieval/test changes are included in the scope summary and file list.
3. `Scope completed` and `Files changed` now reflect the real delivered retrieval state through `e8b19940cfc70e123d53c63d5846efaaa64287aa`, while the current packet tip is described separately as a packet-only refresh.
4. The packet explicitly states which canonical demo-path step this lane advances.
5. The canonical demo-path note is stated as a standalone handoff field so re-review can verify AGENTS alignment without inferring it from the broader scope summary.

## AGENTS.md Handoff Packet
- Risk reason: shared/high-risk work because the delivered implementation range includes the approved shared regression surface `tests/unit/test_unified_retrieval.py`.
- Task budget: `4`
- Tasks completed:
  1. Kept retrieval FTS-first across the canonical retrieval facades while hardening FTS cache normalization, shortlist scanning, and collection/scope handling.
  2. Normalized retrieval payloads, sparse bundle backfills, strategy snapshots, and query/provenance metadata so downstream engine consumers receive deterministic retrieval artifacts.
  3. Stabilized excerpt lookup behavior with confidentiality-aware metadata, title-hint handling, lookup fingerprints, provenance fingerprints, rank fields, and the generic excerpt fetch aliases on the canonical FTS path.
  4. Added and updated approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the delivered FTS-first retrieval contract.
- Files changed in reviewed implementation:
  - `src/qual/engine/retrieval/__init__.py`
  - `src/qual/engine/retrieval/embeddings_strategy.py`
  - `src/qual/engine/retrieval/fts_strategy.py`
  - `src/qual/engine/retrieval/interface.py`
  - `src/qual/engine/retrieval/pageindex_strategy.py`
  - `src/qual/engine/retrieval/payload.py`
  - `src/qual/retrieval/__init__.py`
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Packet files refreshed for this fixer pass:
  - `THREAD_PACKET.md`

## Commands Run With Results
- `make scope-check`: PASS
- `./quality-format.sh --check`: PASS
- `./quality-lint.sh`: PASS
- `./quality-test.sh`: PASS
- `./typecheck-test.sh`: PASS
- `make ci`: PASS

## Risks/Blockers
- Risk: `HIGH`
- Blockers: none

## Roadmap Item(s) Affected
- `Milestone 3: Real workflow loop`
- `feat-retrieval-fts - authoritative FTS-first retrieval feeding the engine loop`

## Vision Capability Affected
- `Retrieval-first context handling`
- `Auditable state and workflow`

## Routing/Provider Impact Note
- None

## Proposed README.md Patch Text
- None

## Scope-Check / Ownership Note
- Shared/integrator-locked edits: `YES`
- The only reviewed non-owned file in the delivered implementation range is the approved shared regression surface `tests/unit/test_unified_retrieval.py`.

## Traceability Note
- The current branch tip after this fix remains a packet refresh, but the reviewed implementation head for retrieval scope is `e8b19940cfc70e123d53c63d5846efaaa64287aa`.
- Re-review should read the retrieval implementation against `d7fd5d200358287fa42a18d39e2b277463b9b69f..e8b19940cfc70e123d53c63d5846efaaa64287aa`.
- The mirrored `.codex` packet files are readable in this worktree but not writable under the current sandbox restrictions, so this fixer commit updates the authoritative `THREAD_PACKET.md` only.
