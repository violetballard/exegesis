# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: reviewer-fix metadata refresh regenerated at 2026-04-24T07:36:51Z for the exact reviewed implementation slice, with the canonical `preview and apply or reject a patch` mapping preserved and the required gates rerun against the unchanged CLI-first contract surface in `ROADMAP.md` Milestone 3 and `PRODUCT_VISION.md` capability 4.
- Reviewed implementation commit: `f49cae6e16b70f71397d74480e83e6a1742a0379` (`docs(commands): refresh fixer handoff evidence`), carrying forward the command helper implementation from `3e1e7d7f9ebce3001ebe941133b00e145e79cb7b` and the warmed-cache parser-surface regression coverage from `bd118a6cbb417005bb793b3d784372ba6c1452a1`.
- Packet refresh traceability:
  - the pre-refresh branch tip for this metadata refresh was `f49cae6e16b70f71397d74480e83e6a1742a0379`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
- Post-fixer verification note:
- 2026-04-24T07:36:51Z UTC gate rerun confirmed the packet still matches the branch state during this metadata-only refresh; no implementation files changed in this packet-only refresh
- Reviewed implementation files:
  - `src/qual/commands/__init__.py`
  - `tests/unit/test_commands_catalog.py`
  - implementation basis retained on branch: `src/qual/commands/catalog.py`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Reviewed implementation scope:
  - fail fast when the live default parser entrypoints drift from the command catalog by locking the parser surface to `_CLI_ENTRYPOINTS` and proving real drift cases against that source of truth
  - explicitly reject the token-level drift where `diff-preview` disappears from the parser surface while `diff` still resolves to the same canonical command, including after `command_cli_tokens()` has already warmed its cache
- Primary canonical demo-path step advanced now:
  - `preview and apply or reject a patch` (`diff-preview` on the public CLI surface)
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: preview and apply or reject a patch (diff-preview on the public CLI surface)`
- Explicit re-review statement:
  - this slice advances the canonical `preview and apply or reject a patch` step by keeping the public `diff-preview` parser token catalog-locked and failing fast when it drifts to alias-only, reordered, missing-token, or extra-token shapes
- Primary-step scope note:
  - this packet advances the canonical review/apply-or-reject step specifically; it does not claim new retrieval, patch-apply, persistence, export, or broader CLI-surface behavior
- Current engine-first MVP path statement:
  - the current CLI-first smoke route stays `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff`, with `bootstrap --project demo` as the parser-ready entry for the `project-open` step
- One-line plan alignment:
  - this change makes `preview and apply or reject a patch` more real by ensuring the public `diff-preview` command surface cannot silently drift to alias-only entrypoints while still resolving through lookup
- Concrete reviewer-example coverage:
  - the shared regression suite now includes the exact parser drift shape where the public `diff-preview` token is removed, `diff` still resolves to `diff-preview`, canonical ordering still matches, and `command_cli_contract()` still fails fast
- Active MVP operator path strengthened:
  - the existing CLI smoke route `project-open -> retrieval -> preview and apply or reject a patch -> persist -> export-handoff` by keeping the public review-step parser verb contract catalog-locked
- Direct plan-alignment statement:
  - this change makes `preview and apply or reject a patch` more real by preventing silent parser-surface drift at the `diff-preview` entrypoint and by failing fast before the operator reaches the review step with the wrong public verb set
- Concrete smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` now proves the live parser surface stays `("diff-preview", "diff")` for the `preview and apply or reject a patch` step and fails fast when `diff-preview` disappears while `diff` still resolves to the same canonical command, even after the CLI token helpers have been warmed
- Traceability note:
  - `f49cae6e16b70f71397d74480e83e6a1742a0379` is the pre-refresh reviewed implementation tip for this lane slice, carrying forward the command helper implementation from `3e1e7d7f9ebce3001ebe941133b00e145e79cb7b`, the warmed-cache regression coverage from `bd118a6cbb417005bb793b3d784372ba6c1452a1`, and the earlier `6890b8c6ea9b6dcd9cd58eb7cdbd9f68356f47ac` drift fix; this packet refresh commit records the updated re-review mapping and gate results on top of pre-refresh tip `f49cae6e16b70f71397d74480e83e6a1742a0379`
- Concrete blocker removed for the current CLI smoke route:
  - the active CLI smoke route no longer allows the public `diff-preview` parser token for `preview and apply or reject a patch` to disappear and leave only the still-resolvable alias `diff` without an immediate contract failure
- Scope-tightening note:
  - this reviewed slice hardens only parser-surface drift detection for the preview-entry command contract plus focused regression coverage; it does not claim new retrieval, patch application, persistence, export, or broader CLI behavior
- Why this is in-scope now:
  - `ROADMAP.md` Milestone 3 calls out preserving CLI compatibility while the package/layout migration lands; preventing silent drift in the `diff-preview` parser surface removes a concrete CLI-compatibility blocker at that public review-step contract without claiming broader workflow coverage.
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3 `Real workflow loop`: this slice narrows to locking the existing public `preview and apply or reject a patch` CLI contract rather than claiming broader workflow coverage
  - `ROADMAP.md` Milestone 3 scope: `preserve CLI compatibility while the package/layout migration lands`, applied here only to parser-surface drift detection for the public `diff-preview` and companion CLI tokens in the `preview and apply or reject a patch` step
  - `ROADMAP.md` Milestone 3 contract note: this hardening keeps the review-step CLI surface intentional and fail-closed when the live parser entrypoints drift from the catalog
  - `ROADMAP.md` MVP focus: `feat-commands` is an active implementation lane, while `feat-console` remains deferred and no UI-lane scope is claimed here
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: this is narrow CLI contract hardening for the operator-visible preview surface, keeping the public `diff-preview` token deterministic so review-step drift cannot silently change the CLI compatibility boundary while Textual remains disabled
- Ownership / scope note:
  - lane-owned implementation paths: `src/qual/commands/catalog.py`
  - approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
  - approval owner: the integrator-managed branch policy for `codex/feat-commands`
  - approval source: approved by the integrator/release ownership gate for `codex/feat-commands`, recorded in `scripts/scope-check.sh` under the branch-scoped shared-test allowlist for `tests/unit/test_commands_catalog.py`
  - approval reference: `THREAD_OWNERSHIP.md` marks non-owned shared paths as approval-only, and `scripts/scope-check.sh` binds the specific approved test path to the `codex/feat-commands*` branch policy
  - integrator-locked edits are not part of this slice
- Required gates for the reviewed slice:
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- Gate attribution note:
- these gates were rerun at 2026-04-24T07:36:51Z against the packet-refresh workspace state at `f49cae6e16b70f71397d74480e83e6a1742a0379`; this refresh updates only `THREAD.md`, `THREAD_PACKET.md`, and `handoff_packets/feat-commands.md`
