# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Packet refresh status: reviewer-fix packet refresh regenerated on 2026-04-24 for the exact reviewed implementation slice, with roadmap/vision mapping narrowed to Milestone 3 CLI compatibility while the Textual lanes remain disabled.
- Reviewed implementation commit: `dbb8e0155a647bd0eb7f442a1799136ee4d591f4` (`fix(commands): harden parser surface drift checks`).
- Packet refresh traceability:
  - the current branch tip for re-review is a packet-only refresh above `dbb8e0155a647bd0eb7f442a1799136ee4d591f4`; no implementation files beyond the reviewed slice changed in this refresh
- Reviewed implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Packet-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`
- Reviewed implementation scope:
  - fail fast when the live default parser entrypoints drift from the command catalog by locking the parser surface to `_CLI_ENTRYPOINTS` and proving real drift cases against that source of truth
  - explicitly reject the token-level drift where `diff-preview` disappears from the parser surface while `diff` still resolves to the same canonical command
- Primary canonical demo-path step advanced now:
  - `project-open` (`bootstrap` the session)
- Required handoff field now called out explicitly:
  - `Canonical demo-path step advanced: project-open (bootstrap the session)`
- Explicit re-review statement:
  - this slice advances the canonical `project-open` bootstrap step first, and it does so by locking the public parser surface that opens the engine-first CLI loop
- Primary-step scope note:
  - this packet advances `project-open` first while hardening the shared parser contract used across the rest of the loop
- Current engine-first MVP path statement:
  - the current CLI-first smoke route stays `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff`, with `bootstrap --project demo` as the parser-ready entry for the `project-open` step
- One-line plan alignment:
  - this change makes `project-open` more real by ensuring the bootstrap command surface cannot silently drift to alias-only entrypoints while still resolving through lookup
- Concrete reviewer-example coverage:
  - the shared regression suite now includes the exact parser drift shape where the public `diff-preview` token is removed, `diff` still resolves to `diff-preview`, canonical ordering still matches, and `command_cli_contract()` still fails fast
- Active MVP operator path strengthened:
  - the existing CLI smoke route entrypoint into `project-open -> retrieval -> patch-review -> apply-patch/reject-patch -> persist -> export-handoff` by keeping the default parser verb contract catalog-locked
- Direct plan-alignment statement:
  - this change makes `project-open` more real by preventing silent parser-surface drift at the bootstrap entrypoint and by failing fast before the operator starts the loop with the wrong public verb set
- Concrete smoke-test evidence:
  - `tests/unit/test_commands_catalog.py` keeps the canonical `project-open` smoke argv at `("bootstrap", "--project", "demo")` and keeps both trusted MVP workflow branches rooted at that same parser-ready bootstrap invocation
- Traceability note:
  - `dbb8e0155a647bd0eb7f442a1799136ee4d591f4` is the reviewed implementation tip for the parser-surface fix set; this packet refresh commit records the updated re-review mapping and gate results on top of it
- Concrete blocker removed for the current CLI smoke route:
  - the active CLI smoke route no longer allows `bootstrap` or other canonical parser entrypoints to be swapped for still-resolvable aliases without an immediate contract failure, which removes silent drift at the entrypoint to the operator-visible loop
- Scope-tightening note:
  - this reviewed slice hardens only parser-surface drift detection for the command catalog plus focused regression coverage; it does not claim new retrieval, patch application, persistence, or export behavior
- Why this is milestone-worthy now:
  - Milestone 3 is where user-facing contracts are locked and documented intentionally, so preventing silent drift in the bootstrap-facing parser surface is direct operator-surface hardening rather than second-order cleanup
- Roadmap / vision alignment for this reviewed slice:
  - `ROADMAP.md` Milestone 3 `Real workflow loop`: harden the CLI-first operator contract for the current engine loop while Textual stays scaffolded and disabled
  - `ROADMAP.md` Milestone 3 scope: preserve CLI compatibility while the package/layout migration lands, applied here only to the parser contract for the `project-open` smoke-route entrypoint
  - `ROADMAP.md` Milestone 3 exit criteria: `CLI can still execute the MVP loop while Textual remains disabled`, protected here by failing closed on parser-surface drift
  - `ROADMAP.md` Active now: `feat-commands` is active while `feat-console-shell` and `feat-console-workflow` remain disabled, so no UI-lane scope is claimed here
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`: keep the CLI bootstrap surface deterministic because CLI compatibility is required while Textual remains disabled
  - `PRODUCT_VISION.md` capability 6 `Auditable state and workflow`: make parser/catalog drift explicit instead of silently changing the operator-facing entrypoint
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
  - these gates were rerun on 2026-04-24 against the packet-refresh workspace state whose only changed files above `dbb8e0155a647bd0eb7f442a1799136ee4d591f4` are `THREAD.md` and `THREAD_PACKET.md`
