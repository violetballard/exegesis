# Handoff Packet: feat-commands

- Branch name: `codex/feat-commands`
- Scope completed: tightened the preview-entry CLI contract for the canonical `preview and apply or reject a patch` step so it validates the real `diff-preview` parser token surface and fails fast if that public review-step entrypoint drifts to alias-only, missing-canonical-token, reordered, or extra-token shapes.
- Canonical demo-path step advanced: `preview and apply or reject a patch`
- Demo-path mapping: this slice makes the canonical `preview and apply or reject a patch` step more real by keeping the operator-facing `diff-preview` preview entrypoint stable before operators enter the existing apply-or-reject branch of the current CLI smoke route.
- Concrete blocker removed: parser/catalog drift can no longer silently drop the public `diff-preview` token and leave only the still-resolvable alias `diff`, which would otherwise change the operator-visible review step without any fail-fast signal during CLI smoke tests.
- Plan-alignment statement: this is a single CLI smoke-route hardening step, not a general CLI cleanup. It makes the preview entrypoint for `preview and apply or reject a patch` deterministic and does not claim new retrieval, patch-apply, persistence, or export behavior.
- Roadmap item(s) affected: `ROADMAP.md` Milestone 3 `Real workflow loop`, specifically `preserve CLI compatibility while the package/layout migration lands`, applied here only to the public preview entrypoint for `preview and apply or reject a patch` so CLI compatibility at that review step fails closed when the surface drifts.
- Vision capability affected: `PRODUCT_VISION.md` capability 4 `Operator-first control surface`, applied narrowly to the CLI-first preview contract within `preview and apply or reject a patch` so parser/catalog drift cannot silently change the public `diff-preview` entrypoint while Textual remains disabled.
- Routing/provider impact note: none; this slice does not touch model routing, provider configuration, or shared entrypoints.
- Proposed `README.md` patch text: none.

## Tasks Completed
1. Tightened `_validate_command_cli_contract()` in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:553) so the command contract validates the authoritative parser projection against the declared CLI entrypoint surface instead of only comparing deduplicated canonical command names.
2. Added parser-surface regressions in [tests/unit/test_commands_catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/tests/unit/test_commands_catalog.py:494) that patch the real parser surface and prove alias-only, missing-canonical-token, reordered, and extra-token drift fail fast, including the critical `diff-preview` removed while `diff` still resolves case.
3. Added the review-step branch-contract helpers in [src/qual/commands/catalog.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/catalog.py:3687) and [src/qual/commands/__init__.py](/Users/doctor-violet/.codex/worktrees/5494/qual/src/qual/commands/__init__.py:24) so the apply/reject branch for the review step can be consumed through explicit contract exports without changing provider, routing, or broader workflow scope.
4. Updated [handoff_packets/feat-commands.md](/Users/doctor-violet/.codex/worktrees/5494/qual/handoff_packets/feat-commands.md:1), [THREAD_PACKET.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD_PACKET.md:1), and [THREAD.md](/Users/doctor-violet/.codex/worktrees/5494/qual/THREAD.md:1) so the re-review packet names the exact canonical demo-path step this slice advances, states the concrete blocker removed, and keeps the roadmap and vision mapping narrow.
5. Ran the required gate suite and scope check.

## Files Changed
- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`
- `handoff_packets/feat-commands.md`

## Commands Run With Results
- `python -m unittest tests.unit.test_commands_catalog -q` -> passed
- `make scope-check` -> passed
- `./quality-format.sh --check` -> passed
- `./quality-lint.sh` -> passed
- `./quality-test.sh` -> passed
- `./typecheck-test.sh` -> passed
- `make ci` -> passed
- Verification rerun timestamp: `2026-04-24T07:33:10Z`

## Risks / Blockers
- Risks: future parser-surface changes now need to keep the declared CLI entrypoints, authoritative parser projection, and packet metadata aligned; the updated regressions are intended to fail fast if they drift.
- Blockers: none.

## Scope-Check / Ownership Note
- Shared-by-approval edit: `tests/unit/test_commands_catalog.py`
- Approval note: `THREAD_OWNERSHIP.md` shared-file exception retained for the required parser-surface regression coverage.
