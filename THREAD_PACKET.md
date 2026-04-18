# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: keep the CLI-first MVP command surface deterministic and smoke-testable by ensuring the live parser, exported command helpers, and diff-preview workflow contracts stay aligned on the current `feat-commands` branch tip.
- Risk reason: the review target includes the approved shared test paths `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`, so this fixer pass stays on the high-risk template.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Validate the live `codex/feat-commands` branch tip instead of the stale `f8d860ed` packet anchor.
2. Re-run the required gates on that exact tree and confirm the reviewer-reported import failure does not reproduce.
3. Refresh the packet so it names the real implementation review range and actual in-scope command files.
4. Leave a packet-only fixer commit for re-review.

### Early Review Triggers

- Before first edit to any shared/integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing/config behavior.

### Stop Triggers

- Unresolved test/lint/typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (short updates)

- Plan complete: validated that the current worktree already exports the reviewer-cited `src.qual.commands` symbols and that re-review must target the live branch tip.
- First green tests: `python -m unittest tests.unit.test_commands_catalog -q` passed on `2026-04-18`.
- Before risky/shared file edit: only `THREAD.md` and `THREAD_PACKET.md` are being edited in this fixer pass.
- Ready for handoff: the packet now reflects the real review target and all required gates passed on the exact tree being handed off.

## Packet Traceability Note

- Current review target: branch tip `07bec2928350f3e1a69d9f93a05b2f431e94ee4b`.
- Current implementation review range: `eda0197b..07bec2928350f3e1a69d9f93a05b2f431e94ee4b`.
- Why this range: `eda0197b` is the previously consumed `feat-commands` merge (`merge: consume approved feat-commands f8d860ed`). Everything after that merge in the command lane is the live unreviewed implementation being handed off now.
- Metadata rule for this resubmission: there is no claim that later implementation commits are metadata only. This packet names the live review target directly and includes the real in-scope implementation files below.

## Reviewer Required Fixes Satisfied

1. The packet is regenerated against the real review target: live branch tip `07bec2928350f3e1a69d9f93a05b2f431e94ee4b`, with implementation range `eda0197b..07bec2928350f3e1a69d9f93a05b2f431e94ee4b`.
2. The stale `f8d860ed`-only narrative and the false “metadata-only reviewer-fix finalization” claim are removed.
3. The current branch tip was revalidated directly. The reviewer-observed import failure does not reproduce here: `python -m unittest tests.unit.test_commands_catalog -q` passes on this tree.
4. Scope mapping now explicitly includes the retrieval-compatibility and `diff_preview` command-surface work that is present in the live lane, rather than claiming a command-catalog-only slice.

## Scope Completed

- The current `feat-commands` tip preserves a deterministic command contract across exported helpers, parser-facing CLI entrypoints, compatibility shims, route tables, and smoke/demo path contracts in `src/qual/commands/**`.
- The current tip includes the command catalog drift protections and the broader parser-surface regression coverage in `tests/unit/test_commands_catalog.py`.
- The current tip also includes the `diff_preview` command-surface work and its focused regression coverage in `tests/unit/test_diff_preview.py`, which were missing from the stale packet scope.
- This fixer pass does not change command implementation. It corrects packet traceability and records fresh validation for the tree actually being handed off.
- Canonical demo-path step advanced: this slice makes the operator-facing `open project/document` and `preview and apply or reject a patch` CLI steps more reliable by keeping the existing command catalog and parser surface deterministic for `bootstrap` and `diff-preview`.
- Scope boundary: this slice hardens the existing CLI contract only. It does not add new command behavior, new flags, or any non-MVP command surface.

## Kickoff Budget / Limits Compliance

- High-risk fixer pass stayed within the `4`-task cap, `30m` budget, and lane size limits.
- This fixer pass changed only `THREAD.md` and `THREAD_PACKET.md`.

## Approved Exception Note

- Approved shared-test paths for this lane:
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Approval source: lane policy in `THREAD_OWNERSHIP.md` and scope enforcement for the lane-specific shared-test allowance.

## Handoff Packet

- Branch name: `codex/feat-commands`

### Tasks Completed (Numbered)

1. Validated the live branch tip `07bec2928350f3e1a69d9f93a05b2f431e94ee4b` as the real re-review target and removed the stale `f8d860ed`-only traceability claim.
2. Confirmed the reviewer-reported `src.qual.commands` import failure does not reproduce on this worktree by running `python -m unittest tests.unit.test_commands_catalog -q`.
3. Re-ran the required gate suite on the exact tree being handed off and recorded the current outcomes below.
4. Refreshed the handoff packet so the review scope includes the actual command-lane implementation files present in `eda0197b..07bec2928350f3e1a69d9f93a05b2f431e94ee4b`.

### Files Changed

- Implementation files in the current review range:
  - `src/qual/commands/__init__.py`
  - `src/qual/commands/canonical.py`
  - `src/qual/commands/catalog.py`
  - `src/qual/commands/diff_preview.py`
  - `tests/unit/test_commands_catalog.py`
  - `tests/unit/test_diff_preview.py`
- Metadata-only files changed in this fixer pass:
  - `THREAD.md`
  - `THREAD_PACKET.md`

### Commands Run and Outcomes

- `python -m unittest tests.unit.test_commands_catalog -q`: `PASS`
- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Verification date: `2026-04-18`

### Risks / Blockers

- Risk: `MEDIUM`
- Remaining risk: the review surface is broader than the stale packet claimed, so re-review needs to examine the full command-lane delta named above rather than a command-catalog-only slice.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Milestone 3: preserve CLI compatibility while the package/layout migration lands by keeping the command surface deterministic, smoke-testable, and migration-safe.
- `feat-commands`: stable CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision capability affected

- Canonical engine contract: the CLI compatibility layer remains a stable operator surface while the future client stays disabled.
- Auditable state and workflow: command-surface drift is exercised explicitly in tests instead of silently changing operator-facing behavior.

### Routing/provider impact note

- None. This lane work remains inside local command contracts, helper exports, and command-surface tests.

### Proposed `README.md` patch text

- None.

## Scope-Check / Ownership Note

- Shared/integrator-locked edits: `YES`
- Ownership detail:
  - owned implementation paths stay inside `src/qual/commands/**`
  - approved shared test paths are `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py`
  - this fixer pass edits only `THREAD.md` and `THREAD_PACKET.md`
