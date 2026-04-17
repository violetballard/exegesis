# Thread Packet Pointer

This file exists for compatibility with older lane and fixer prompts.

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Reviewer Fix Alignment

- This packet refresh is for the active `codex/feat-commands` branch state.
- Review the command-catalog implementation in
  `src/qual/commands/catalog.py` together with the focused shared-test
  coverage in `tests/unit/test_commands_catalog.py`.
- For this re-review, use the reviewer packet as the scope source of truth and
  keep the reviewed implementation pinned to that command-catalog slice unless
  a new feature packet is explicitly generated.
- This refresh corrects handoff metadata only and does not expand the
  requested re-review scope beyond that command-catalog slice.
- The reviewed implementation remains pinned to
  `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; later metadata-only refreshes
  do not expand scope.
- This metadata-only refresh fully accounts for both `THREAD_PACKET.md` and
  `THREAD.md` in the handoff `Files Changed` traceability.
- This is a Milestone 3 CLI compatibility contract hardening refresh for
  `feat-commands`, not a broader workflow-surface or UI-surface change.
- This re-review refresh is specifically for the reviewer-requested packet fix:
  state explicitly which canonical demo-path step the work makes more real,
  while keeping the implementation review pinned to the same command-catalog
  slice.
- Slice-level approval basis only: the reviewed change hardens
  `command_cli_contract()` ordering and drift validation for the active CLI
  `open`, `retrieve`, and `patch-review` path; it does not newly claim that
  broader lane-level command coverage was delivered by this slice.
- Reviewer-required fix satisfied on this branch by:
  - explicit canonical demo-path step mapping in `THREAD_PACKET.md`
  - a reviewer-requested tie-back to the Milestone 3 requirement that the CLI
    must keep the MVP loop executable while Textual remains disabled
- Feature-fixer validation on `2026-04-17`: the required local gates were
  rerun and passed on this metadata-refresh branch tip:
  - `SCOPE_ALLOW_SHARED=1 make scope-check`
  - `make scope-check`
  - `./quality-format.sh --check`
  - `./quality-lint.sh`
  - `./quality-test.sh`
  - `./typecheck-test.sh`
  - `make ci`
- This fixer refresh keeps the implementation scope narrow while making the
  handoff accurately describe the code and tests that now satisfy the
  reviewer-required fixes on this branch.
- Shared-test approval audit trail: the reviewed implementation slice includes
  `tests/unit/test_commands_catalog.py`, which is a `feat-commands`
  shared-by-approval path, so this refresh now records the explicit
  approval-bearing scope gate invocation `SCOPE_ALLOW_SHARED=1 make
  scope-check` alongside the plain required gates.
- Concrete blocker-removal statement for AGENTS alignment: while the CLI is
  still the active operator surface, the engine-first MVP loop cannot stay
  dependable if the `bootstrap`, `context-basket`, and `diff-preview`
  entrypoints can drift away from the declared canonical command order
  without failing fast. This handoff now states that blocker explicitly.
- Canonical demo-path step impact: this slice makes the CLI `open
  project/document`, `retrieve relevant material`, and `preview and apply or
  reject a patch` steps, and the ongoing CLI operator path that must remain
  executable while Textual stays disabled, more reliable by keeping the
  `bootstrap`, `context-basket`, and `diff-preview` entrypoints aligned with
  the canonical command catalog and rejecting parser-surface drift before it
  can silently change the operator-facing contract.
