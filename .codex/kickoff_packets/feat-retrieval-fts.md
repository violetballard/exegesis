# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/engine/retrieval/payload.py`, `src/qual/retrieval/service.py`
- Scope goal: Record the citation-bundle metadata self-description in `src/qual/engine/retrieval/payload.py` and the matching propagation in `src/qual/retrieval/service.py`.
- Scope completed: The reviewed commit `b8a6f9c1649e76e97992687cc81d92561d1e9f18` adds self-describing citation-bundle fields in `src/qual/engine/retrieval/payload.py` and carries that richer metadata through `src/qual/retrieval/service.py`.

### Priority outcomes
1. State clearly that the reviewed change is citation-bundle metadata self-description plus payload propagation.
2. Keep the scope limited to the two reviewed source files.
3. Avoid implying ingestion, routing, PageIndex, embeddings, or broader retrieval-engine changes.

### Tasks
1. Add self-describing citation-bundle metadata in `src/qual/engine/retrieval/payload.py`.
2. Propagate the citation bundle through `src/qual/retrieval/service.py`.
3. Keep the file list and metadata commit-accurate for the reviewed diff.

### Files changed
- `src/qual/engine/retrieval/payload.py`
- `src/qual/retrieval/service.py`

### Guardrails
- Keep the change limited to citation-bundle metadata propagation and payload hardening.
- Preserve commit accuracy between the packet, lane metadata, and git history.
- Do not reference unrelated retrieval MVP scope or files outside the reviewed diff.
