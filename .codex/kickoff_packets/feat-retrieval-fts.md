# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/**`, `src/qual/engine/retrieval/**`, `engine/src/exegesis_engine/retrieval/**`
- Scope goal: Continue hardening the authoritative FTS-first retrieval path that feeds the engine-side demo loop: open document, retrieve relevant material, promote or gather context, plan/revise, preview/apply patch, persist state, and continue without losing provenance.

### Priority outcomes
1. Keep SQLite FTS as the authoritative MVP retrieval path.
2. Preserve deterministic retrieval payloads, provenance snapshots, source refs, and context bundles for downstream engine runs.
3. Make excerpt lookup and basket promotion fail closed when an excerpt is not backed by the canonical FTS source path.
4. Keep PageIndex and embedding surfaces as compatibility/future shims only unless a task explicitly activates them.

### Guardrails
- Do not touch Textual UI implementation work.
- Do not edit control-plane files from this feature branch.
- Keep retrieval behavior deterministic and auditable; source IDs, document IDs, offsets, and provenance metadata should survive round trips.
- Any shared-by-approval test edits must be narrow and called out in the handoff.
- If a retrieval change requires packet garden, router, planner, or lane ownership changes, stop and report that blocker.

### Current reviewed baseline
- The lane has already shipped an FTS-first retrieval MVP: canonical query construction, deterministic retrieval payloads, provenance snapshots, sparse source/context bundle rehydration, and FTS-only excerpt lookup behavior.
- Approved shared regression coverage has previously existed in `tests/unit/test_unified_retrieval.py`; treat any further shared edits as high-risk and keep them minimal.
- Continue advancing Milestone 3 and Milestone 4 only where retrieval directly supports the canonical engine demo path.

### Planned Tasks
1. Identify the next smallest retrieval blocker on the canonical demo path.
2. Add or tighten one focused retrieval behavior with tests.
3. Verify provenance/source metadata stays deterministic through the retrieval-to-context handoff.
4. Run the required gates or the narrowest available focused tests before handoff.

### Stop Triggers
- Integrator-locked or control-plane files need editing.
- Scope check fails and cannot be resolved cleanly within two focused attempts.
- Test/lint/typecheck failures remain unresolved after two focused attempts.
- The change no longer directly strengthens the canonical engine demo path.

### Handoff Packet
- Branch name
- Tasks completed, numbered
- Files changed
- Commands run and outcomes
- Risks/blockers
- Which canonical demo-path step the work now makes more real
