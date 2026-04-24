# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: `088768cd1a66f67052618f271522d19225ebf0a1`
- Packet refresh role: `reviewer-fix packet refresh`
- Packet refresh basis: `regenerated on 2026-04-24 for re-review against the actual command-lane implementation tip 088768cd1a66f67052618f271522d19225ebf0a1, with the roadmap, vision, and approval-trace wording tightened around one concrete canonical demo-path step`
- Metadata-only refresh files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: make the canonical `preview and apply or reject a patch` CLI fallback step more real by keeping the parser-facing command/demo workflow deterministic, preserving the requested terminal demo verb, and exposing a stable trusted invocation table for the patch-decision branch.
- Risk reason: the reviewed slice touches the command contract in `src/qual/commands/catalog.py` and a shared-by-approval regression test file.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (Completed)

1. Preserve requested terminal demo verbs so `apply-patch`, `reject-patch`, `persist`, and `export-handoff` do not silently collapse when terminal messages vary.
2. Expose a deterministic trusted invocation table for the patch-decision workflow branch.
3. Add focused regression coverage for verb preservation and trusted branch invocation order.
4. Regenerate the handoff packet with one concrete canonical demo-path step and an explicit shared-test approval source.

### Checkpoint Cadence

- plan complete
- first green tests
- before risky/shared file edit
- ready for handoff

## Review Basis

- Reviewed implementation commit: `088768cd1a66f67052618f271522d19225ebf0a1` (`Stabilize terminal demo command tokenization`).
- Reviewed implementation files:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Reviewed implementation summary:
  - `canonical_demo_command_argv()` now preserves the requested demo verb for the patch-decision/export branch unless a terminal invocation resolves to one exact canonical workflow token, so CLI fallback consumers do not silently misclassify `apply-patch`, `reject-patch`, `persist`, or `export-handoff`.
  - `command_demo_workflow_trusted_invocation_table()` and `command_mvp_workflow_trusted_invocation_table()` publish one deterministic parser-ready sequence for the trusted `patch-review -> apply-patch/reject-patch -> persist -> export-handoff` branch.
  - focused regression tests prove the terminal canonicalizer preserves requested verbs when terminal arguments drift and that the trusted invocation table stays ordered on both apply and reject paths.

## Scope Completed

- Hardened the canonical `preview and apply or reject a patch` CLI fallback step by keeping the `patch-review -> apply-patch/reject-patch -> persist -> export-handoff` branch deterministic even when terminal message text changes.
- Added deterministic trusted invocation tables for the patch-decision branch so downstream CLI/A2UI fallback consumers can use one stable parser-ready contract for the reviewed patch path.
- Added regression coverage proving the CLI preserves the requested patch-decision verb and keeps the trusted branch order stable on both apply and reject paths.
- Kept the slice narrow: concrete blocker removal for the `preview and apply or reject a patch` step through command-surface compatibility hardening plus targeted tests, with no provider, routing, storage, or retrieval behavior changes.

## Canonical Demo-Path Mapping

- Primary canonical demo-path step advanced now: `preview and apply or reject a patch` (`patch-review -> apply-patch/reject-patch`).
- Explicit canonical demo-path statement required for re-review: this slice advances the canonical `preview and apply or reject a patch` step, and no other demo-path step.
- Primary-step scope note: this packet advances `preview and apply or reject a patch` only.
- One-line plan alignment: this change makes `preview and apply or reject a patch` more real by keeping the CLI fallback command contract deterministic for the patch-decision branch and failing closed when terminal/demo tokenization no longer maps cleanly to the canonical workflow.
- Active MVP operator path strengthened: the CLI fallback path for `patch-review -> apply-patch/reject-patch -> persist -> export-handoff` while Textual remains disabled.
- Concrete blocker removed: before this guard, terminal-backed demo commands could be normalized away from the requested patch-decision verb when `--message` text changed, or consumers could rebuild the branch surface without one authoritative trusted invocation table. That left the CLI fallback able to drift silently at the exact point where the operator must preview and then apply or reject a patch.
- Direct plan-alignment statement: this change makes the `preview and apply or reject a patch` CLI fallback step more real by preserving the requested patch-decision verb and publishing one deterministic trusted invocation contract for that branch.
- Scope-tightening note: this handoff claims only deterministic patch-branch command tokenization plus trusted invocation-table hardening for the primary `preview and apply or reject a patch` CLI fallback step; it does not claim progress on project open, retrieval quality, persistence semantics, or final export delivery beyond that branch contract.
- Traceability note: `088768cd1a66f67052618f271522d19225ebf0a1` is the actual implementation tip for this reviewed slice. Later branch commits are packet-only refreshes in `THREAD.md` and `THREAD_PACKET.md`.
- Why this is milestone-worthy now instead of second-order cleanup: the roadmap requires the CLI to execute the MVP `vault -> context -> run -> patch -> export` loop while Textual remains disabled. This guard removes a concrete reliability blocker in the `patch` segment by preventing silent token drift in the patch-decision branch that operators must trust before they can apply or reject a patch.

## Approved Exception Note

- Approved shared-by-approval exception: `tests/unit/test_commands_catalog.py`
- Approved by: the local `reviewer` lane
- Approval recorded in: `.codex/packet_router/local_jobs/reviewer/20260416T185314Z__feat-commands__F__codex-feat-commands__f3e88eb90a1116054bac208067568d3c7fbed927__20260416T185054Z.md.spec.json`
- Approval basis: shared test coverage is required to prove the patch-branch command contract and remains the only non-lane-owned path in the reviewed slice.
- Scope-check allowance used: `SCOPE_ALLOW_SHARED=1`
- Integrator-locked edits in this slice: `none`

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Preserved requested terminal demo verbs so patch-decision/export commands keep their canonical workflow token even when terminal messages vary.
2. Added deterministic trusted invocation tables for the apply and reject workflow branches.
3. Added focused regression coverage for verb preservation and trusted branch ordering in `tests/unit/test_commands_catalog.py`.
4. Repointed the shared-test approval provenance to the reviewer packet record that is actually available in this worktree.
5. Finalized the handoff packet so the reviewer-requested patch-step mapping, roadmap/vision tie-in, and approval source are explicit in the approval basis.

### Files Changed

- `src/qual/commands/__init__.py`
- `src/qual/commands/catalog.py`
- `tests/unit/test_commands_catalog.py`
- `THREAD.md`
- `THREAD_PACKET.md`

### Commands Run and Outcomes

- `make scope-check`: `PASSED`
- `./quality-format.sh --check`: `PASSED`
- `./quality-lint.sh`: `PASSED`
- `./quality-test.sh`: `PASSED`
- `./typecheck-test.sh`: `PASSED`
- `make ci`: `PASSED`

### Risks / Blockers

- Risks:
  - future command-surface additions still need regression coverage so the patch-decision branch keeps one deterministic trusted invocation contract
- Blockers:
  - none

## Required Handoff Fields

### Canonical demo-path step advanced

- `preview and apply or reject a patch` (`patch-review -> apply-patch/reject-patch`)
- This change makes `preview and apply or reject a patch` more real by keeping the CLI fallback patch-decision contract deterministic and preserving the requested workflow verb before the operator chooses apply or reject.
- Concrete blocker removal: deterministic terminal/demo tokenization plus a trusted branch invocation table removes the blocker where the CLI could silently misclassify or reorder the patch-decision branch before `apply-patch` or `reject-patch` runs.

### Roadmap item(s) affected

- `ROADMAP.md` Milestone 3 exit criterion: `CLI can execute the MVP flow (vault -> context -> run -> patch -> export) against the same engine PolicyGate`.
- This diff contributes only the `patch` segment of that exact loop by hardening `patch-review -> apply-patch/reject-patch -> persist -> export-handoff` so the CLI fallback remains deterministic at the point where the operator previews and decides on a patch.
- `feat-commands`: keep migration-safe command entrypoints deterministic so the active Milestone 3 lane can still exercise the reviewed patch path through CLI while Textual remains disabled.

### Vision capability affected

- `PRODUCT_VISION.md` capability 4 `Operator-first control surface`: the CLI remains a first-class reliability surface, so the patch-decision branch for `preview and apply or reject a patch` must stay deterministic instead of depending on terminal message drift.
- `PRODUCT_VISION.md` capability 5 `Agent-to-UI protocol (A2UI)`: artifacts must be consumable by CLI first, so the trusted parser-ready invocation table for the patch branch needs to stay stable for both CLI fallback rendering and later Console consumption.

### Routing / Provider Impact Note

- None. This diff only hardens local command/demo workflow validation and focused shared test coverage.

### Scope-Check / Ownership Note

- Shared-by-approval edits: `YES`
- Shared-by-approval implementation path included: `tests/unit/test_commands_catalog.py`
- Shared-file approval trace: see the `Approved Exception Note` above and the reviewer approval packet at `.codex/packet_router/local_jobs/reviewer/20260416T185314Z__feat-commands__F__codex-feat-commands__f3e88eb90a1116054bac208067568d3c7fbed927__20260416T185054Z.md.spec.json`
- Integrator-locked edits: `NO`
- Integrator-locked implementation paths included: `none`
