# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Verified implementation basis SHA: `077764032`
- Submitted tip note: this handoff refresh may add a metadata-only packet commit on top of that verified implementation basis
- Lane/owned paths: `src/qual/commands/**` with approved shared/runtime touchpoints in `src/qual/cli.py` and shared test/scope-check coverage required to make the branch reviewable
- Scope goal: submit the actual branch tip for review as a command-surface hardening lane that adds an authoritative command catalog, binds the live CLI parser entrypoints to that catalog, exposes current-MVP workflow and patch-loop wrappers, and hardens the `diff-preview` output contract with matching unit coverage.
- Risk reason: this is a high-risk command-contract handoff because it changes the operator-facing parser surface, patch-review/apply-or-reject flow shims, and a shared CLI entrypoint file.

### Scope / Plan Alignment

- Canonical demo-path step advanced: `patch` in the CLI MVP flow `vault -> context -> run -> patch -> export`.
- Explicit handoff sentence: this handoff advances the canonical `patch` step by making the operator-facing `patch-review` plus `apply-patch` / `reject-patch` command surface explicit, parser-checked, compatibility-mapped, and smoke-testable on the same branch tip being submitted for merge.
- Roadmap alignment: `ROADMAP.md` Milestone 1 command and diff-preview behavior hardening, plus Milestone 5 CLI fallback coverage for the `patch` leg of the MVP flow.
- Vision alignment: `PRODUCT_VISION.md` capability 3 `Canonical engine contract` only.
- Non-claim boundary: this handoff does not claim provider routing changes, storage behavior changes, audit trail changes, or UI-console work.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: original high-risk target was `<=8 files`, `<=300 net LOC`; actual merge-candidate branch tip exceeds that target and this packet reports the real submitted footprint instead of claiming a narrowed slice
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Add the authoritative command catalog and current-MVP workflow/path wrappers used to resolve `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff`.
2. Bind the live parser entrypoints in `src/qual/cli.py` to the catalog contract and keep the lane reviewable through the scope-check/shared-test allowances carried on this branch.
3. Harden `src/qual/commands/diff_preview.py` with labeled output, JSON mode, fingerprint metadata, and stable no-diff payload behavior.
4. Cover the branch-tip command and diff-preview contracts in unit tests, then re-run the required gates and report them against the same merge candidate branch tip.

### Early Review Triggers

- before first edit to any shared/integrator-locked file
- before changing public interfaces or command contracts
- before touching provider routing/config behavior

### Stop Triggers

- unresolved test/lint/typecheck after 2 attempts
- unresolved `make scope-check`
- budget/size/time limit hit

### Checkpoint Cadence (short updates)

- plan complete: packet scope is now pinned to the actual branch tip instead of a historical narrowed SHA, and the tasks map to the `patch` leg of the MVP CLI flow
- first green tests: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci` were rerun for the merge candidate branch tip
- before risky/shared file edit: this branch includes approved shared parser work in `src/qual/cli.py` plus shared test/scope-check changes required to keep the command lane reviewable
- ready for handoff: the packet truthfully describes the full branch-tip command surface, names one concrete MVP path step, and reports files/tasks/gates for the same merge candidate being submitted

### Handoff Packet

- branch name: `codex/feat-commands`
- scope completed:
  - added the authoritative command catalog in `src/qual/commands/catalog.py` and re-exported the stable catalog/workflow helpers through `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, and `src/qual/commands/workflow.py`
  - bound the live parser surface in `src/qual/cli.py` to the catalog contract through exported parser entrypoints and startup validation, so parser drift now fails fast against the authoritative command surface
  - exposed the current-MVP `patch-review` loop, transition, compatibility, trusted-surface, and invocation-plan helpers that make `project-open -> retrieval -> patch-review -> apply/reject -> persist -> export-handoff` deterministic and smoke-testable
  - hardened `src/qual/commands/diff_preview.py` with labeled file headers, JSON output, fingerprint metadata, and stable no-diff payloads
  - added and updated regression coverage in `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, and carried the branch’s scope-check allowances needed for approved shared tests and handoff packet paths
- tasks completed (numbered implementation work only; metadata-only packet refreshes excluded):
  1. Added the authoritative command catalog plus stable command, flow, path, transition, compatibility, and trusted-surface helpers for the current CLI MVP loop.
  2. Hardened the live parser contract in `src/qual/cli.py` and catalog validation so command entrypoint drift is rejected against the authoritative branch-tip surface.
  3. Expanded `diff-preview` into a stable output contract with labeled text output, JSON mode, fingerprint support, and deterministic no-diff behavior.
  4. Added branch-tip unit coverage for command-surface and diff-preview behavior, and reran the required gates against the same merge candidate branch tip.
- files changed:
  - branch-tip implementation: `scripts/scope-check.sh`
  - branch-tip implementation: `src/qual/cli.py`
  - branch-tip implementation: `src/qual/commands/__init__.py`
  - branch-tip implementation: `src/qual/commands/canonical.py`
  - branch-tip implementation: `src/qual/commands/catalog.py`
  - branch-tip implementation: `src/qual/commands/diff_preview.py`
  - branch-tip implementation: `src/qual/commands/workflow.py`
  - branch-tip implementation: `tests/unit/test_commands_catalog.py`
  - branch-tip implementation: `tests/unit/test_diff_preview.py`
  - metadata-only handoff refresh: `THREAD.md`
  - metadata-only handoff refresh: `THREAD_PACKET.md`
  - metadata-only handoff refresh: `handoff_packets/feat-commands.md`
- size/accounting note:
  - actual branch-tip delta versus `main` spans 12 files and a large command-surface addition; this re-review packet is intentionally truthful about that full submitted scope
- commands run + outcomes:
  - rerun on implementation basis SHA `077764032` on `2026-04-24`
  - packet refresh commits after that basis are metadata-only and do not change the reviewed implementation scope
  - `make scope-check` -> passed
  - `./quality-format.sh --check` -> passed
  - `./quality-lint.sh` -> passed
  - `./quality-test.sh` -> passed
  - `./typecheck-test.sh` -> passed
  - `make ci` -> passed
- risks/blockers:
  - risk: future parser or compatibility-token edits must update both the authoritative catalog and `src/qual/cli.py` entrypoint projection together, or the fail-fast contract will reject the surface
  - risk: future patch-loop alias additions must preserve the deterministic `patch-review -> apply/reject -> persist -> export-handoff` transition tables and their smoke/default argv coverage
  - blockers: none
- roadmap item(s) affected:
  - `ROADMAP.md` Milestone 1 command and diff-preview behavior hardening
  - `ROADMAP.md` Milestone 5 CLI can execute the MVP flow (`vault -> context -> run -> patch -> export`) against the same engine PolicyGate
- vision capability affected:
  - `PRODUCT_VISION.md` capability 3 `Canonical engine contract`
- routing/provider impact note:
  - none; this change does not touch routing or provider configuration
- approved exception note:
  - this branch includes approved shared parser work in `src/qual/cli.py` and approved shared-test/scope-check coverage needed to keep the lane reviewable
- reviewer-fix satisfaction note:
  - this packet is reissued against the actual merge candidate implementation basis `077764032`, tightens the claim to the branch’s real command-surface and diff-preview work, names the concrete `patch` step it advances, and makes explicit that any newer tip from this handoff refresh is metadata-only instead of hidden implementation drift
