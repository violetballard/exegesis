# Lane Kickoff: feat-retrieval-fts

- Branch: `codex/feat-retrieval-fts`
- Lane/owned paths: `src/qual/retrieval/service.py`
- Scope goal: Canonicalize query constraints in `src/qual/retrieval/service.py` so equivalent retrieval requests normalize to stable doc-type and date-range fingerprints.
- Scope completed: The reviewed commit `e3d489aa19f925d44264e6e8ad38e4f620a32771` updates `src/qual/retrieval/service.py` only; it adds deterministic canonicalization for query doc types and date-range constraints inside retrieval query normalization.

### Priority outcomes
1. Normalize query doc types and date ranges in one place so equivalent requests compare and fingerprint the same way.
2. Keep the retrieval service contract deterministic for downstream matching and fingerprinting.
3. Avoid implying engine/retrieval policy, PageIndex, ingestion, or provider-routing work in this promotion.

### Guardrails
- Keep the change limited to retrieval query normalization and test-hardening.
- Preserve commit accuracy between the packet, lane metadata, and git history.
- Do not reference unreviewed retrieval source files or unrelated retrieval MVP scope.
