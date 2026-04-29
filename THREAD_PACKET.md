## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Merge candidate: current branch tip after this fixer commit.
- Pre-fixer branch-tip SHA: `abba588583dd3701f0c7378f691f45dbb54b44bb`
- Corrected implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Corrected reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewer-referenced packet-refresh commit: `2871ebf7d09fdf8338f5a65994ab63a5dd815307`
- Role for `2871ebf7d09fdf8338f5a65994ab63a5dd815307`: runtime/test drift-removal plus packet refresh.
- Actual requested merge range for the reviewed packet: `378cf9a74a3658058079a32f186fcd254c4a4034..2871ebf7d09fdf8338f5a65994ab63a5dd815307`; runtime/test files at that tip are restored to the corrected implementation head, and later commits in that reviewed packet are retained as packet metadata plus explicit drift-removal.
- Handoff classification: high-risk/shared because the corrected slice includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- Shared-file approval provenance: reviewer packet `fixer__feat-retrieval-fts__20260429T202122Z.prompt.txt`, finding 2, identifies `tests/unit/test_unified_retrieval.py` as the approved shared surface for `feat-retrieval-fts`.

## Required Fixes Addressed

1. The merge candidate is narrowed to the FTS-only excerpt change in `378cf9a7..adfa8cda`; later runtime/test implementation drift has been removed from the final tree instead of being submitted for review.
2. The prior `metadata-only reviewer-fix finalization` label for `2871ebf7d09fdf8338f5a65994ab63a5dd815307` is corrected to `runtime/test drift-removal plus packet refresh`.
3. Scope completed, tasks completed, files changed, risks, and budget accounting below describe the corrected FTS-only merge candidate.
4. The full branch-tip runtime/test diff for the reviewed packet is within the high-risk budget, so no integrator budget exception is needed.
5. Required gates are re-run against the corrected merge-candidate working tree and recorded below.
6. The canonical demo-path step advanced is `retrieve relevant material`.

## Scope Completed

The corrected candidate keeps SQLite FTS as the authoritative excerpt lookup path for the MVP. It removes non-FTS fallback excerpt retrieval, fails closed for unsupported document scopes, normalizes query and document identity inputs for lookup, and records regression coverage for FTS-only excerpt behavior. PageIndex and embeddings remain compatibility surfaces outside the corrected merge candidate.

## Tasks Completed

1. Canonical demo-path step `retrieve relevant material`: make document excerpt lookup use FTS lookup results only.
2. Canonical demo-path step `retrieve relevant material`: fail closed when excerpt lookup cannot be satisfied by the supported FTS-backed document scope.
3. Canonical demo-path step `retrieve relevant material`: normalize document IDs, query text, and max-result handling used by the FTS excerpt lookup path.
4. Handoff/review support: remove post-`adfa8cda` runtime/test drift from the final tree and restate the packet around the corrected reviewed slice.

## Files Changed

Corrected implementation files in `378cf9a7..adfa8cda`:

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Final runtime/test files changed versus `378cf9a7` after this fixer:

- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Metadata files present in `378cf9a7..2871ebf`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`

Actual final file list in `378cf9a7..2871ebf`:

- `.codex/kickoff_packets/feat-retrieval-fts.md`
- `.codex/lane_meta/feat-retrieval-fts.json`
- `THREAD_PACKET.md`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

No `codex_packet_handoff/tools/planner.py` or `tests/unit/test_packet_planner.py` changes are present in `378cf9a7..2871ebf`.

Commit `2871ebf7d09fdf8338f5a65994ab63a5dd815307` itself edits:

- `src/qual/engine/retrieval/fts_strategy.py`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`
- `THREAD_PACKET.md`

The `2871ebf7d09fdf8338f5a65994ab63a5dd815307` runtime/test edits are removals of post-`adfa8cda` drift plus packet refresh work. `git diff adfa8cda..2871ebf -- src/qual/engine/retrieval/fts_strategy.py src/qual/engine/retrieval/payload.py src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py` is empty, so the reviewed runtime behavior remains the `378cf9a7..adfa8cda` implementation slice.

## Budget / Risk

- Risk: high/shared.
- Task budget: `4/4`; within the high-risk task cap.
- Corrected runtime/test file count: `2`; within the high-risk 8-file guideline.
- Corrected runtime/test size in `378cf9a7..adfa8cda`: `28 insertions(+), 31 deletions(-)`, net `-3`; within the high-risk `<=300` guideline.
- Final runtime/test size versus `378cf9a7` after this fixer: `28 insertions(+), 31 deletions(-)`, net `-3`.
- Integrator-locked files: none identified in `THREAD_OWNERSHIP.md`.
- Shared-by-approval files: `tests/unit/test_unified_retrieval.py`.
- Routing/provider impact: none.

## Roadmap / Vision Mapping

- Roadmap items affected: `ROADMAP.md` Milestone 3 Product Readiness and Milestone 4 Retrieval Layer.
- Vision capability affected: `PRODUCT_VISION.md` capability 2, Retrieval-first context handling.
- Canonical demo-path step advanced: `retrieve relevant material`.
- Proposed `README.md` patch text: none.

## Commands Run

- `make scope-check`: PASS.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS, including smoke and 124 unit tests.
- `./typecheck-test.sh`: PASS.
- `make ci`: PASS, including scope-check, format, lint, typecheck, smoke, and 124 unit tests.

## Risks / Blockers

- No implementation blocker is known after narrowing the merge candidate.
- The tracked mirror packet files under `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` still contain stale pre-fixer metadata because this sandbox returns `Operation not permitted` for writes under `.codex`; `THREAD_PACKET.md` is the corrected handoff packet for re-review.
- Re-review should verify `git diff adfa8cda..2871ebf -- src/qual/engine/retrieval/fts_strategy.py src/qual/engine/retrieval/payload.py src/qual/retrieval/service.py tests/unit/test_unified_retrieval.py` remains empty and use `378cf9a7..adfa8cda` as the corrected implementation slice.
