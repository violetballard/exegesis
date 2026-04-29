## Thread Handoff Packet

- Branch/lane: `codex/feat-retrieval-fts` / `feat-retrieval-fts`
- Packet purpose: branch-tip retrieval feature handoff for FTS-first retrieval and auditable basket promotion references. This packet is the writable source of truth for re-review because `.codex` packet mirrors could not be edited by the sandbox in this fixer pass.
- Merge candidate: the current branch tip after this fixer commit.
- Authoritative merge-review range: `378cf9a74a3658058079a32f186fcd254c4a4034..HEAD` on `codex/feat-retrieval-fts`.
- Branch-tip correction: this packet includes `6d3ca5d75d517b508fd6dfb954ac83bcc8c85591`, `3f09ca2f4132eff22bd3faa0e8a3e1f5411482f5`, and packet-refresh commits through `04ad10a5d` in the reviewed branch-tip range. The handoff no longer claims that the candidate ends at `adfa8cdadd43747ffbcb612e4151e262b13e52ca`, and it does not label implementation commits as metadata-only.
- Code-bearing branch-tip commits in scope:
  - `adfa8cdadd43747ffbcb612e4151e262b13e52ca`: FTS-only excerpt lookup and deterministic retrieval payload behavior.
  - `6d3ca5d75d517b508fd6dfb954ac83bcc8c85591`: stable document and excerpt references for basket promotion in retrieval evidence.
  - `3f09ca2f4132eff22bd3faa0e8a3e1f5411482f5`: exposes normalized basket-promotion refs through retrieval source/context/downstream payload reconstruction.
  - final fixer commit: packet traceability correction for the actual branch-tip candidate.
- Final proposed merge HEAD SHA: reported in the final fixer response after commit creation.

## Scope Completed

This branch-tip handoff keeps SQLite FTS authoritative for MVP retrieval. It adds deterministic FTS-only excerpt lookup behavior, stable retrieval query/result fingerprints, deterministic source/provenance/citation payloads, and fail-closed handling for unsupported non-FTS excerpt paths.

The current branch tip also keeps basket promotion auditable: retrieval evidence carries stable document and excerpt refs, source bundles preserve normalized `retrieval_basket_promotion_refs`, and downstream payload reconstruction rehydrates those refs without requiring PageIndex or embeddings.

PageIndex and embeddings remain deferred/fallback-only compatibility surfaces; they are not required paths for this handoff.

The canonical demo path advanced by this range is:

1. Retrieve relevant material through the FTS-first retrieval path.
2. Promote selected retrieved docs/excerpts into the context basket using stable refs.
3. Carry retrieved context forward to later draft/revise/apply steps through deterministic payloads.

## Tasks Completed

1. Made FTS-only excerpt retrieval the branch-tip retrieval contract and preserved deterministic query/result fingerprints, citation snapshots, and provenance on FTS hits.
   - Demo-path step advanced: retrieve relevant material.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 output contract readiness and Milestone 4 FTS-first retrieval/source attribution.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
2. Normalized retrieval payloads, source bundles, provenance bundles, sparse backfills, and missing-value handling so downstream engine flows rehydrate canonical retrieval context deterministically.
   - Demo-path step advanced: carry retrieval context forward to later draft/revise/apply steps.
   - Roadmap mapping: `ROADMAP.md` Milestone 4 retrieval orchestration and deterministic auditable retrieval.
   - Product vision mapping: capability 5, Agent-to-UI protocol, because CLI/A2UI fallback consumers receive stable structured payloads.
3. Added branch-tip basket promotion reference behavior through `6d3ca5d75d517b508fd6dfb954ac83bcc8c85591`: stable doc/excerpt refs are built from FTS hits, normalized in retrieval evidence, exposed as `retrieval_basket_promotion_refs`, and preserved through source-bundle/downstream reconstruction.
   - Demo-path step advanced: promote retrieved docs/excerpts into the basket using auditable refs.
   - Roadmap mapping: `ROADMAP.md` Milestone 3 generation provenance contract and Milestone 4 source-attribution model for retrieved chunks.
   - Product vision mapping: capability 2, Retrieval-first context handling, and capability 3, Auditable generation.
4. Added and maintained approved shared regression coverage in `tests/unit/test_unified_retrieval.py` for the FTS-first retrieval contract, sparse payload reconstruction, citation/provenance helpers, and FTS-only excerpt behavior.
   - Demo-path step advanced: verifies the FTS-first retrieval path is reproducible for the canonical demo.
   - Roadmap mapping: MVP engine stability and retrieval contract readiness.
   - Product vision mapping: auditable, deterministic workflow state.

## Files Changed

- `THREAD_PACKET.md`
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`
- `tests/unit/test_unified_retrieval.py`

Historical branch-tip packet metadata also references `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json`, but this sandbox rejected writes to `.codex` during this fixer pass (`writing outside of the project; rejected by user approval settings`). Those mirrors are stale and should not override this `THREAD_PACKET.md`; this handoff packet is the updated review source for the actual merge candidate.

No integrator-owned `README.md`, `INTEGRATION.md`, `src/main.py`, `src/qual/cli.py`, or `src/qual/app.py` changes are included.

## Budget / Size Accounting

- Risk: high/shared because the actual merge-review range includes the approved shared regression file `tests/unit/test_unified_retrieval.py`.
- Task budget: `4/4` under the AGENTS high-risk/shared cap.
- File budget: `4/8` high-risk files changed in this branch-tip fixer packet.
- Shared-file edits: approved regression coverage in `tests/unit/test_unified_retrieval.py`.
- Integrator-locked files: none.
- Scope remains tight to Milestone 3/4 retrieval: FTS-first retrieval, structured/auditable basket promotion refs, and no required PageIndex/embeddings path.

## Roadmap / Vision

- Roadmap items affected:
  - `ROADMAP.md` Milestone 3: output contract readiness and generation provenance contract.
  - `ROADMAP.md` Milestone 4: FTS-first retrieval orchestration, source attribution, deterministic auditable retrieval, and deferred PageIndex/embeddings.
- Vision capabilities affected:
  - Product Vision capability 2, Retrieval-first context handling.
  - Product Vision capability 3, Auditable generation.
  - Product Vision capability 5, Agent-to-UI protocol, for stable retrieval payloads consumable by CLI/A2UI fallback flows.
- Routing/provider impact: none.
- Textual/UI impact: none.
- Alternate retrieval-mode impact: none. PageIndex and embeddings remain deferred/fallback-only.
- Proposed `README.md` patch text: none.

## Commands Run

Required gates were re-run for this fixer pass against the actual branch-tip merge candidate:

- `make scope-check`: PASS; scope-check passed for branch `codex/feat-retrieval-fts`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS, shell syntax and trailing whitespace checks passed.
- `./quality-test.sh`: PASS, smoke plus 124 unit tests.
- `./typecheck-test.sh`: PASS, Python sources in `src/` compile.
- `make ci`: PASS, including setup verification, scope-check, format, lint, compileall/typecheck, smoke, and 124 unit tests.

Prior useful local check in this fixer pass:

- `pytest tests/unit/test_unified_retrieval.py -q`: not run; `pytest` is not installed on PATH in this shell.

## Risks / Blockers

- No current runtime blocker.
- `.codex/kickoff_packets/feat-retrieval-fts.md` and `.codex/lane_meta/feat-retrieval-fts.json` could not be regenerated in this sandbox because `.codex` is not writable (`Operation not permitted`). `THREAD_PACKET.md` has been regenerated to align the review candidate with the actual branch tip.
- Merge risk is high only because the handoff includes approved shared regression coverage; there are no integrator-locked file edits.
- The branch intentionally does not add embeddings, PageIndex requirements, UI rendering behavior, or alternate retrieval modes.
