# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: reviewer-fix packet refresh regenerated on 2026-04-24 for the exact reviewed implementation slice, with roadmap/vision mapping narrowed to the current CLI-first contract surface in `ROADMAP.md` Milestone 3 and `PRODUCT_VISION.md` capability 4.
- Reviewed implementation commit: `6890b8c6ea9b6dcd9cd58eb7cdbd9f68356f47ac` (`test(commands): lock parser drift regressions to live entrypoints`).
- Packet refresh traceability:
  - the current branch tip for re-review is a packet-only refresh above `6890b8c6ea9b6dcd9cd58eb7cdbd9f68356f47ac`; no implementation files beyond the reviewed slice changed in this refresh
- Post-fixer verification note:
  - 2026-04-24 UTC gate rerun confirmed the packet still matches the branch state after this fixer pass; no implementation files changed in this verification refresh
- Reviewed implementation files:
  - `tests/unit/test_commands_catalog.py`
  - implementation basis retained on branch: `src/qual/commands/catalog.py`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Reviewed implementation scope:
  - fail fast when the live default parser entrypoints drift from the command catalog by locking the parser surface to `_CLI_ENTRYPOINTS` and proving real drift cases against that source of truth
  - explicitly reject the token-level drift where `diff-preview` disappears from the parser surface while `diff` still resolves to the same canonical command
- Primary canonical demo-path step advanced now:
  - `patch-review` (`diff-preview` on the public CLI surface)
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: patch-review (diff-preview on the public CLI surface)`
- Explicit re-review statement:
  - this slice advances the canonical `patch-review` step by locking the public parser surface for `diff-preview` and failing fast when that operator-visible token drifts to alias-only or reordered shapes
- Primary-step scope note:
  - this packet advances `patch-review` specifically while hardening the shared parser contract reused by downstream compatibility and workflow surfaces
- Current engine-first MVP path statement:
  - the current CLI-first smoke route stays `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`, with `bootstrap --project demo` as the parser-ready entry for the `project-open` step
- One-line plan alignment:
  - this change makes `patch-review` more real by ensuring the public `diff-preview` command surface cannot silently drift to alias-only entrypoints while still resolving through lookup
- Concrete reviewer-example coverage:
  - the shared regression suite now includes the exact parser drift shape where the public `diff-preview` token is removed, `diff` still resolves to `diff-preview`, canonical ordering still matches, and `command_cli_contract()` still fails fast
- Active MVP operator path strengthened:
  - the existing CLI smoke route entrypoint into `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff` by keeping the default parser verb contract catalog-locked
- Direct plan-alignment statement:
  - this change makes `patch-review` more real by preventing silent parser-surface drift at the `diff-preview` entrypoint and by failing fast before the operator reaches the review step with the wrong public verb set
- Concrete smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` now proves the live parser surface stays `("diff-preview", "diff")` for the `patch-review` step and fails fast when `diff-preview` disappears while `diff` still resolves to the same canonical command
- Traceability note:
  - `6890b8c6ea9b6dcd9cd58eb7cdbd9f68356f47ac` is the reviewed implementation tip for the parser-surface fix set; this packet refresh commit records the updated re-review mapping and gate results on top of it
- Concrete blocker removed for the current CLI smoke route:
  - the active CLI smoke route no longer allows the public `diff-preview` parser token for `patch-review` to disappear or be reordered behind alias-only tokens without an immediate contract failure
- Scope-tightening note:
  - this reviewed slice hardens only parser-surface drift detection for the command catalog plus focused regression coverage; it does not claim new retrieval, patch application, persistence, or export behavior
- Why this is milestone-worthy now:
  - `ROADMAP.md` Milestone 3 is where user-facing contracts are defined and locked intentionally; preventing silent drift in the `patch-review` parser surface is direct CLI contract hardening for that release-readiness milestone.
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3 `Product Readiness`: this slice narrows to the CLI-first contract surface that must be defined and locked intentionally before release
  - `ROADMAP.md` Milestone 3 scope: `Define and lock user-facing output contracts`, applied here only to parser-surface drift detection for the public `diff-preview` and companion CLI tokens in the `patch-review` step
  - `ROADMAP.md` Milestone 3 exit criteria: `Contract changes documented and intentional`, protected here by failing closed when the live `patch-review` parser entrypoints drift from the catalog
  - `ROADMAP.md` MVP focus: `feat-commands` is an active implementation lane, while `feat-console` remains deferred and no UI-lane scope is claimed here
  - `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: keep the CLI `patch-review` surface deterministic so the current operator-facing review entrypoint stays stable for both manual smoke runs and downstream structured-output consumers
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
  - these gates were rerun on 2026-04-24 against the packet-refresh workspace state whose only changed files above `6890b8c6ea9b6dcd9cd58eb7cdbd9f68356f47ac` are `THREAD.md` and `THREAD_PACKET.md`
