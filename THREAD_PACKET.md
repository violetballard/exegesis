# Thread Handoff Packet

- Branch name: `codex/feat-retrieval-fts`
- Current branch head before this fixer commit: `926e36c9281b4b60cdf9fe4165ca825fd9a42daa`
- Reviewed implementation head: `adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Reviewed implementation range: `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`
- Packet refresh role: `metadata-only reviewer-fix finalization`

## Scope goal

- Tighten the narrowed FTS-first excerpt lookup contract so only FTS-backed excerpt ids resolve through the public retrieval surface.

## Budget classification

- Shared/high-risk handoff under the `4`-task cap because the reviewed implementation range includes approved shared regression coverage in `tests/unit/test_unified_retrieval.py`.
- This metadata-only fixer commit updates the handoff packet only; it does not broaden the reviewed implementation range.

## Scope completed

- SQLite FTS remains the authoritative MVP retrieval path in this narrowed slice.
- The reviewed implementation removes the PageIndex fallback from `fetch_excerpt`, so FTS-only excerpt lookup on the canonical retrieval surface now fails closed instead of silently resolving PageIndex-only excerpt ids.
- Approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proves PageIndex-only excerpt IDs now raise `KeyError`.
- AGENTS mapping: this narrowed slice directly advances the canonical `retrieve relevant material` step by forcing FTS-only excerpt lookup through the FTS-backed contract on the canonical retrieval surface and failing closed on non-FTS excerpt ids.
- Basket-promotion rationale: because only FTS-backed excerpt ids can be re-fetched, downstream basket promotion and later revise/apply steps receive deterministic, auditable excerpt payloads instead of silently accepting PageIndex-only fallback data.
- Reviewer-fix note: this packet remains intentionally narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and does not broaden scope beyond the FTS-only excerpt lookup contract and its regression coverage.
- Source-of-truth note: this `THREAD_PACKET.md` handoff is the re-review packet for this fixer pass on top of `926e36c9281b4b60cdf9fe4165ca825fd9a42daa`; `.codex` packet mirrors in this worktree are filesystem-protected and are not required to evaluate the narrowed retrieval scope.

## Required reviewer fixes addressed

1. This handoff now explicitly states that the canonical demo-path step advanced is `retrieve relevant material`, matching the AGENTS requirement called out in review.
2. The packet remains tightly scoped to the narrowed retrieval slice `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca` and ties that scope to FTS-only excerpt lookup on the canonical retrieval surface with deterministic provenance preserved for downstream basket and workflow use.
3. The packet does not claim new basket-promotion, workflow-card, or broader engine-surface progress in this slice because the reviewed range only changes the `fetch_excerpt` fallback contract and its approved shared regression coverage.
4. This metadata-only fixer commit keeps the operative packet in `THREAD_PACKET.md` aligned with the reviewer-required AGENTS demo-path mapping for this narrowed slice.
5. The operative handoff now carries that AGENTS mapping in a dedicated `Canonical demo-path step advanced` section so re-review no longer depends on implied plan alignment.

## Packet mirror status

- `THREAD_PACKET.md` is the operative re-review handoff in this worktree.
- The tracked `.codex` packet mirrors for this lane are present for traceability but are filesystem-protected in this environment, so this fixer pass does not mutate them.
- Re-review should use this operative packet as the source of truth for the reviewer-required AGENTS demo-path mapping and narrowed implementation scope.

## Tasks completed

1. Removed the PageIndex fallback from `fetch_excerpt` so the public excerpt lookup surface now resolves only through the canonical FTS-backed lookup path.
2. Added approved shared regression coverage in `tests/unit/test_unified_retrieval.py` proving PageIndex-only excerpt ids fail closed with `KeyError`.

## Files changed

- Reviewed implementation files:
  - `src/qual/retrieval/service.py`
  - `tests/unit/test_unified_retrieval.py`
- Metadata-only fixer packet file:
  - `THREAD_PACKET.md`

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

- `Milestone 3: Real workflow loop` by keeping excerpt lookup on the FTS-first retrieval contract used by the engine loop.
- `feat-retrieval-fts` by preserving the authoritative FTS-first retrieval path at the public excerpt lookup surface.

### Vision capability affected

- `Retrieval-first context handling` through an FTS-only excerpt lookup contract at the public retrieval surface.
- `Auditable state and workflow` by failing closed instead of silently accepting PageIndex-only excerpt payloads.

### Canonical demo-path step advanced

- `retrieve relevant material`
- Explicit AGENTS mapping: this narrowed slice makes the canonical `retrieve relevant material` step more real by forcing excerpt lookup through the FTS-backed contract and failing closed instead of accepting PageIndex-only excerpt ids.
- Explicit downstream effect: the stricter FTS-only excerpt contract keeps the excerpt payload that basket promotion consumes deterministic and auditable before later revise/apply workflow steps.
- Packet regeneration note: this re-review packet now carries the required canonical demo-path mapping directly in the operative handoff file instead of leaving plan alignment implicit.
- Reviewer source-of-truth note: this handoff follows the reviewer packet's narrowed excerpt-only range and should be re-reviewed against that exact slice rather than the broader branch-level retrieval history.
- Re-review anchor: keep the reviewed implementation scope narrowed to `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`; this metadata-only fixer commit does not broaden that slice.

### Routing/provider impact note

- None

### Proposed `README.md` patch text

- None

## Scope-check / ownership note

- Shared/integrator-locked edits: `YES`
- Approved shared exception: `tests/unit/test_unified_retrieval.py` is the sole shared-by-approval file in the reviewed implementation range.
- Metadata-only packet refresh edits do not expand the reviewed implementation range beyond `378cf9a74a3658058079a32f186fcd254c4a4034..adfa8cdadd43747ffbcb612e4151e262b13e52ca`.
