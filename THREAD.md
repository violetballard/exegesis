# Thread Packet Pointer

Canonical handoff contract lives in `THREAD_PACKET.md`.

## Current Review Focus

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Review basis: actual `codex/feat-commands` branch tip for the `20260429T022329Z` reviewer-fix pass.
- Previous implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Scope: command-catalog contract hardening for the current engine-first MVP focus without starting `feat-console`.
- Roadmap alignment: Milestone 3 CLI compatibility for the engine-first workflow loop, and `feat-commands` as the command-surface compatibility lane.
- Vision alignment: canonical engine contract stability while the CLI remains the active operator surface.

## Reviewed Files

- `src/qual/commands/catalog.py`
- `src/qual/commands/__init__.py`
- `src/qual/commands/canonical.py`
- `src/qual/commands/diff_preview.py`
- `tests/unit/test_commands_catalog.py`
- `tests/unit/test_diff_preview.py`

## Shared / Approval Notes

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Approved shared-by-approval test edits: `tests/unit/test_commands_catalog.py`, `tests/unit/test_diff_preview.py`.
- Shared-by-approval edits: yes, `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` under approved exception.
- Integrator-locked edits: no.
- Gate-policy edits: no net review change after this fixer pass; `scripts/scope-check.sh` matches the branch review baseline and is absent from the net `main...HEAD` review diff.
- Metadata-only handoff files: `THREAD.md`, `THREAD_PACKET.md`.

## Canonical Demo-Path Mapping

- This command contract hardening strengthens the CLI surface for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` by keeping those parser routes deterministic and drift-checked.
- This makes the open/retrieve/basket/patch-review CLI smoke path more real by keeping the parser-visible command contract deterministic and failing fast when parser tokens drift from the command catalog.

## Reviewer Packet `20260429T012436Z` Fix Satisfaction

1. Review basis now points to the current branch tip instead of a stale `f8d860e` slice.
2. Post-`f8d860e` implementation and test commits are included in review rather than classified as metadata-only.
3. Parser-surface drift coverage includes added aliases, removed aliases, same-canonical substitutions such as replacing `bootstrap` with `open` or `diff-preview` with `diff`, token reordering, lookup-table shape/order drift, and declared-surface drift.
4. Ownership/accounting lists the approved shared test edits and keeps `scripts/scope-check.sh` out of the net `main...HEAD` review diff.

## Reviewer Packet `20260429T013303Z` Fix Satisfaction

1. `command_cli_contract()` validates the full parser-visible token surface through canonical tokens, canonical lookup-table shape, and grouped parser-surface checks.
2. Same-canonical substitutions are covered by focused tests, including `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview` drift.
3. The handoff basis now points at the actual branch tip and does not classify test-changing commits as metadata-only.
4. Ownership accounting identifies `tests/unit/test_commands_catalog.py` and `tests/unit/test_diff_preview.py` as approved shared-by-approval test edits, with no integrator-locked edits.
5. The canonical demo-path mapping explicitly names the protected `project-open`, `retrieval`, `patch-review`, and `export-handoff` command steps.

## Reviewer Packet `20260429T013535Z` Fix Satisfaction

1. Demo-path alignment now states that this command contract hardening strengthens `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` by keeping those parser routes deterministic and drift-checked.
2. Metadata-only handoff files include both `THREAD.md` and `THREAD_PACKET.md`.
3. Implementation scope is unchanged by this reviewer-fix pass.

## Fixer Packet `20260429T013834Z` Validation

1. The branch already contains the required parser-surface drift guard and focused same-canonical alias drift tests.
2. Required gates were rerun for this fixer pass: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
3. This pass is metadata-only; implementation scope remains unchanged.

## Fixer Packet `20260429T014157Z` Validation

1. The branch tip remains the single review basis and includes the post-`f8d860e` command package and test changes.
2. The required parser-surface drift fixes are already present in `src/qual/commands/catalog.py` and covered by focused `_CLI_ENTRYPOINTS`, declared-surface, and lookup-table regressions.
3. Required gates were rerun for this fixer pass: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Fixer Packet `20260429T014429Z` Validation

1. `command_cli_contract()` still validates the full parser-visible CLI surface, including canonical tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order.
2. Focused tests still cover `_CLI_ENTRYPOINTS` additions, removals, reordering, and same-canonical substitutions such as `bootstrap` -> `open`, `diff-preview` -> `diff`, and `diff` -> `diff_preview`.
3. Demo-path mapping remains explicit for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
4. Required gates were rerun for this fixer pass: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Fixer Packet `20260429T014718Z` Validation

1. Latest required fixes remain satisfied by the branch-tip command contract: parser-visible tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order are all validated before returning `CommandCliContract`.
2. Focused regressions still patch `_CLI_ENTRYPOINTS` for same-canonical substitutions, token removal, token addition, and token reordering.
3. The handoff packet continues to use the actual branch tip as review basis and keeps the canonical demo-path mapping explicit for the open/retrieve/basket/patch-review CLI smoke path.
4. Required gates were rerun for this fixer pass: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Fixer Packet `20260429T015007Z` Validation

1. Latest required fixes remain satisfied by the branch-tip command contract: parser-visible tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order are all validated before returning `CommandCliContract`.
2. Focused regressions still patch `_CLI_ENTRYPOINTS` for added alias tokens, removed tokens, token reordering, and same-canonical substitutions such as `bootstrap` -> `open` and `diff-preview` -> `diff`.
3. The handoff packet continues to name the actual branch tip as review basis, list all branch-tip implementation files, and keep the canonical demo-path mapping explicit for `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
4. Required gates were rerun for this fixer pass: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260429T015607Z` Fix Satisfaction

1. The handoff now selects one review basis: the actual `codex/feat-commands` branch tip for this fixer pass.
2. Post-`f8d860e` commits are explicitly included as implementation-bearing and test-bearing rather than metadata-only.
3. Branch-tip file accounting includes `THREAD.md`, `THREAD_PACKET.md`, `src/qual/commands/__init__.py`, `src/qual/commands/canonical.py`, `src/qual/commands/catalog.py`, `src/qual/commands/diff_preview.py`, `tests/unit/test_commands_catalog.py`, and `tests/unit/test_diff_preview.py`.
4. Gate attribution is branch-tip based: exact `make scope-check` and `make ci` are blocked by scope policy on the existing approved shared-test edit, while `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, and `./typecheck-test.sh` pass.
5. Roadmap and vision mapping remains explicit for Milestone 3 CLI compatibility and canonical engine contract stability, with the canonical demo-path steps named in `THREAD_PACKET.md`.

## Reviewer Packet `20260429T015948Z` Fix Confirmation

1. Reviewer verdict: `APPROVED`.
2. Required fixes before re-review: none.
3. This fixer pass records the approval/no-fix outcome only; implementation scope remains unchanged.
4. Pre-commit gate rerun for this fixer pass: `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, and `./typecheck-test.sh` pass; exact `make scope-check` and `make ci` are blocked before this metadata commit by scope policy on the existing approved shared-test edit `tests/unit/test_commands_catalog.py`.

## Reviewer Packet `20260429T021315Z` Fix Satisfaction

1. Required fix 1 is satisfied by the branch-tip `command_cli_contract()` implementation validating the full parser-visible CLI surface: canonical parser tokens, lookup-table shape, grouped parser surface, declared surface, and canonical command order.
2. Required fix 2 is satisfied by focused tests that patch `_CLI_ENTRYPOINTS` for `bootstrap` -> `open`, token removal, extra parser token addition, and parser token order drift, plus existing same-canonical `diff-preview` -> `diff` coverage.
3. Required fix 3 remains satisfied because this pass stays scoped to focused command-catalog test coverage plus packet metadata; no unrelated paths are introduced.
4. Required fix 4 remains satisfied by the canonical demo-path mapping in `THREAD_PACKET.md`, which names `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
5. Required fix 5 remains satisfied by separating approved shared-by-approval test edits from integrator-locked edits; integrator-locked edits remain `NO`.
6. Required gates were rerun for this fixer pass and passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260429T021537Z` Fix Satisfaction

1. `THREAD_PACKET.md` now maps each completed task to the protected canonical demo-path command steps: `project-open`, `retrieval`, `patch-review`, and `export-handoff`.
2. The packet includes the concise statement that this work makes `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` more real by guaranteeing parser-visible CLI tokens stay aligned with the command catalog.
3. The ownership note separates approved shared-by-approval test edits from integrator-locked edits; integrator-locked edits remain `NO`.
4. The packet keeps the review basis on the actual branch tip because post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command/test commits are implementation-bearing.
5. Required gates were rerun for this fixer pass and passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260429T022017Z` Fix Satisfaction

1. `command_cli_contract()` validates the parser-visible token surface against the canonical CLI surface before returning `CommandCliContract`; it checks tokens, lookup table shape, grouped surface, declared surface, and canonical command order.
2. Focused `_CLI_ENTRYPOINTS` tests cover token substitution, removal, addition, and ordering drift, including same-canonical alias cases such as `bootstrap` -> `open` and `diff-preview` -> `diff`.
3. `THREAD_PACKET.md` is regenerated against the actual branch tip and does not classify post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` command/test commits as metadata-only.
4. Ownership notes separate approved shared-by-approval test edits from integrator-locked edits; integrator-locked edits remain `NO`.
5. The canonical demo-path mapping states that this keeps `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch` deterministic and drift-checked.
6. Required gates were rerun for this fixer pass and passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.

## Reviewer Packet `20260429T022329Z` Fix Satisfaction

1. The review basis remains singular and true: review the actual `codex/feat-commands` branch tip for this fixer pass, including post-`f8d860ed9f6299f0169c4f21321ac5f37c949fd3` implementation and test commits.
2. `command_cli_contract()` validates the full parser-visible CLI token surface before returning the contract, not just de-duplicated canonical names.
3. Focused tests now include a same-canonical alias-substitution surface where canonical names still match, proving `bootstrap` -> `open` drift is rejected even when the canonical-name tuple is unchanged; existing tests cover token addition, token removal, and token reordering.
4. The handoff packet maps each completed task to the protected demo-path steps: `open project/document`, `retrieve relevant material`, `promote/gather context`, and `preview/apply/reject patch`.
5. Ownership notes continue to separate approved shared-by-approval test edits from integrator-locked edits; integrator-locked edits remain `NO`.
6. Required gates were rerun for this fixer pass and passed: `make scope-check`, `./quality-format.sh --check`, `./quality-lint.sh`, `./quality-test.sh`, `./typecheck-test.sh`, and `make ci`.
