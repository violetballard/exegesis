# Feature -> Review Packet

## Thread Kickoff (High-Risk)

- Branch: `codex/feat-commands`
- Lane/owned paths: `src/qual/commands/**`
- Scope goal: correct the handoff so it truthfully describes the real current `feat-commands` branch tip, explicitly maps that tip to the named CLI-fallback MVP steps it advances, and cites the concrete shared-path approval basis already present in branch history.
- Risk reason: this fixer edits shared handoff metadata for a lane whose current tip includes both owned command files and shared test files.

### Budget

- Task budget: `4`
- Time budget: `30m`
- Size limits: `<=8 files`, `<=300 net LOC`
- Max fix attempts per failing gate: `2`

### Planned Tasks (max 4)

1. Replace the stale narrow-slice traceability note with the truthful current-tip implementation set.
2. Add the missing canonical demo-path mapping and concrete CLI-loop blocker removal required by the reviewer.
3. Replace the vague shared-test note with the concrete current and historical approval trail.
4. Re-run `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

### Early Review Triggers

- Before first edit to any shared or integrator-locked file.
- Before changing public interfaces or command contracts.
- Before touching provider routing or config behavior.

### Stop Triggers

- Unresolved test, lint, or typecheck failure after `2` focused fix attempts.
- Unresolved `make scope-check`.
- Budget, size, or time limit hit.

### Checkpoint Cadence (Short Updates)

- Plan complete: truthify the handoff to the real branch tip instead of a stale narrow slice.
- First green tests: recorded after the required gate rerun on `2026-04-23`.
- Before risky/shared file edit: this fixer only edits `THREAD.md` and `THREAD_PACKET.md`.
- Ready for handoff: the packet now matches the current branch tip and names the current CLI-fallback MVP steps it advances.

## Packet Traceability Note

- Review basis for re-review is the actual current branch-tip implementation set:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` (`feat(commands): lock CLI contract to command catalog`)
  - `1e04f9633c4abc4988dcb991944680b86f94f753` (`Fix command shim subcommand routing`)
  - `5c89ce987fc78ed158d378a988b3e211ce93145d` (`feat(commands): stabilize no-diff diff-preview payload`)
- This fixer adds one metadata-only packet refresh on top of that current implementation tip.
- The earlier claim that post-`f8d860ed...` commits were metadata-only was false because the branch tip also contains `src/qual/commands/diff_preview.py` and `tests/unit/test_diff_preview.py`; this packet corrects that traceability error instead of trying to hide it.

## Reviewer Required Fixes Satisfied

1. The handoff now names the real reviewed commit set at the current branch tip, including the additional `diff_preview` implementation the reviewer called out.
2. `Scope completed`, `Files changed`, and the handoff narrative now match that reviewed tip instead of a stale command-catalog-only slice.
3. The packet now states the exact named CLI-fallback MVP steps this work advances: step 1 `open project/document`, step 2 `retrieve relevant material`, and step 3 `preview and apply or reject a patch`, via the current CLI fallback surfaces while Textual remains disabled.
4. The vague shared-test exception note is replaced with a concrete approval trail:
   - current scope-check policy explicitly allows `tests/unit/test_commands_catalog.py`
   - that approval is traceable to `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` and `c3a66bb580772d65201a630d673a8de1d4a63776`, both authored by `Violet Ballard`
   - historical branch approval for `tests/unit/test_diff_preview.py` was recorded in `e00623f0be7934383d64df46fdaec99d9f92f13c`, `8a38d7bde29da3ecfb3da905ff78416034b151b7`, and `9e6b2206d7a37fc28b1233569ed2ac473e61f15a`

## Scope Completed

- Hardened `command_cli_contract()` in `src/qual/commands/catalog.py` so the default CLI contract reuses canonical command order and fails fast when the parser surface drifts from the command catalog.
- Fixed command shim subcommand routing in `src/qual/commands/catalog.py` so routed CLI fallback steps preserve explicit subcommands such as `context-basket search`.
- Stabilized the no-diff JSON payload in `src/qual/commands/diff_preview.py` so `diff-preview` returns the effective labels and option state even when no diff is emitted.
- Added focused regression coverage in `tests/unit/test_commands_catalog.py` for parser-surface drift rejection, canonical ordering, and routed subcommand preservation.
- Added focused regression coverage in `tests/unit/test_diff_preview.py` for no-diff JSON payload shape, effective labels, and effective options.
- Refreshed `THREAD.md` and `THREAD_PACKET.md` so the handoff truthfully matches the actual current branch tip, the active CLI-fallback MVP path it hardens, and the traceable shared-test approval record.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the `4`-task cap, `30m` budget, and metadata-only fixer scope.
- This fixer pass only edits `THREAD.md` and `THREAD_PACKET.md`.

## Approved Exception Note

- Current explicit shared-path allowance in repo policy:
  - `tests/unit/test_commands_catalog.py` only is still allowlisted for `codex/feat-commands*` in `scripts/scope-check.sh`
  - Approver / policy author: `Violet Ballard`
  - Approval date: `2026-03-28`
  - Traceable approval source: `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50` added the `codex/feat-commands*` allowlist entry for `tests/unit/test_commands_catalog.py` in `scripts/scope-check.sh`, and `c3a66bb580772d65201a630d673a8de1d4a63776` kept that approval in force while tightening the packet text.
- Historical branch approval trail for additional shared test coverage already present in the reviewed tip:
  - `e00623f0be7934383d64df46fdaec99d9f92f13c` (`Allow feat-commands shared diff preview test`)
  - `8a38d7bde29da3ecfb3da905ff78416034b151b7` (`fix(commands): approve diff preview shared regression`)
  - `9e6b2206d7a37fc28b1233569ed2ac473e61f15a` (`docs(commands): record shared diff_preview test approval`)
- This fixer does not modify scope policy or claim any new shared-path approval beyond that existing trail.

## Handoff Packet

- Branch name: `codex/feat-commands`
- Reviewed implementation commits:
  - `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
  - `1e04f9633c4abc4988dcb991944680b86f94f753`
  - `5c89ce987fc78ed158d378a988b3e211ce93145d`
- Packet refresh commit: this fixer commit (`HEAD` after commit)

### Tasks Completed (Numbered)

1. Hardened `command_cli_contract()` to reject parser-surface drift while preserving canonical command order.
2. Preserved explicit routed subcommands for CLI fallback flows such as `context-basket search`.
3. Stabilized the no-diff `diff-preview` payload so JSON output keeps labels and effective option state when no diff is emitted.
4. Added focused regression coverage in `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` for those behaviors.
5. Refreshed the handoff metadata so the reviewed scope, named demo-path mapping, concrete CLI-loop blocker removal, and shared-path approval basis match the actual current branch tip.

### Files Changed

- `THREAD.md`
- `THREAD_PACKET.md`
- `src/qual/commands/catalog.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

### Commands Run and Outcomes

- `make scope-check`: `PASS`
- `./quality-format.sh --check`: `PASS`
- `./quality-lint.sh`: `PASS`
- `./quality-test.sh`: `PASS`
- `./typecheck-test.sh`: `PASS`
- `make ci`: `PASS`
- Verification date: `2026-04-23`

## Ready For Handoff

- Status: ready for re-review
- Current fixer pass: metadata-only handoff correction with fresh required gate rerun on `2026-04-23`
- No implementation files changed in this fixer pass

### Risks / Blockers

- Risk: `MEDIUM`
- Remaining risk: the reviewed branch tip includes historical shared `diff_preview` test coverage whose approval trail exists in branch history but is no longer reflected in the current `scripts/scope-check.sh` allowlist.
- Blockers: none

## Required Handoff Fields

### Roadmap item(s) affected

- Named current CLI-first MVP demo-path steps advanced by this lane:
  - step 1 `open project/document`
  - step 2 `retrieve relevant material`
  - step 3 `preview and apply or reject a patch`
- `feat-commands` remains one of the current active lanes called out in `ROADMAP.md` under `MVP Focus Through 2026-05-04`.
- Milestone 5 exit criterion support: the reviewed slice hardens the CLI fallback that must stay executable for the MVP flow (`vault -> context -> run -> patch -> export`) while Textual remains disabled.

### Vision capability affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog and `diff-preview` surfaces reject or expose drift in operator-visible behavior before it silently changes the current CLI fallback contract.

### Canonical Demo-Path Step Advanced

- `open project/document` via the CLI fallback `bootstrap` / `project-open` surface
- `retrieve relevant material` via the routed `context-basket search` surface
- `preview and apply or reject a patch` via `diff-preview`
- Concrete blocker removed from the CLI-first MVP loop: after step 1 (`open project/document`), the operator could still lose deterministic routing for step 2 (`retrieve relevant material`) or lose effective-state visibility for step 3 (`preview and apply or reject a patch`) because parser drift, shimmed-subcommand loss, or no-diff payload loss would silently break the fallback CLI contract.
- Explicit handoff statement: this reviewed slice makes step 2 (`retrieve relevant material`) and step 3 (`preview and apply or reject a patch`) more real by locking the command contract that step 1 feeds into, preserving routed retrieval subcommands, and preserving no-diff preview state while Textual remains disabled; it does not claim broader workflow completion beyond those current operator surfaces.

### Routing / Provider Impact Note

- None.

### Proposed `README.md` Patch Text

- None.

## Scope-Check / Ownership Note

- Shared or integrator-locked edits: `YES`
- Ownership detail:
  - lane-owned implementation: `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`
  - current shared-test allowlist in repo policy: `tests/unit/test_commands_catalog.py` approved by `Violet Ballard` in `40cc1e0b014b42df9ef36a8aa3f5466c2c22dd50`, preserved in `c3a66bb580772d65201a630d673a8de1d4a63776`
  - historical shared-test approval trail already present in branch history: `tests/unit/test_diff_preview.py`
  - shared metadata updated for handoff accuracy: `THREAD.md`, `THREAD_PACKET.md`
