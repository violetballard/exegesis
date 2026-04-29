# Feature -> Review Packet

- Lane: `feat-commands`
- Branch: `codex/feat-commands`
- Commit: branch tip after fixer prompt `20260429T044747Z`
- Review basis: branch tip after this fixer commit, not `f8d860ed9f6299f0169c4f21321ac5f37c949fd3` alone.
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`
- Packet refresh role: reviewer-fix handoff correction after prompt `20260429T044747Z`

## Packet Traceability Note

- Fixer prompt `20260429T035831Z` requested reviewer-required fixes for exact parser-token validation, same-canonical drift coverage, canonical demo-path handoff mapping, and gate reruns.
- Fixer prompt `20260429T040101Z` requested a metadata-only handoff refresh so every completed task names the canonical demo-path step it supports and states the concrete blocker removed by the command-catalog work.
- Fixer prompt `20260429T040347Z` requested the same reviewer-required fixes against the actual branch tip, including current review-basis accounting, exact parser-surface validation, same-canonical drift coverage, demo-path mapping, gate reruns, and a new commit.
- Fixer prompt `20260429T040701Z` requested the reviewer-required fixes again with emphasis on full parser-surface drift rejection, regression coverage for extra/missing/substituted/ordered same-canonical drift, exact review-basis accounting, and complete metadata file listing.
- Fixer prompt `20260429T040923Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T041242Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T041540Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T041829Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T042108Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T042332Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T042639Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T042935Z` requested the same reviewer-required fixes against the current branch tip and requires a new commit with refreshed gate evidence.
- Fixer prompt `20260429T043211Z` requested review-basis fixes against the current branch tip: unambiguous branch-tip target, every post-anchor non-metadata implementation commit, final implementation file set, gate evidence for the selected target, and a scope-completed restatement against the selected code.
- Fixer prompt `20260429T043434Z` requested the reviewer-required fixes again against the current branch tip: unambiguous branch-tip target, full parser-surface validation, same-canonical drift coverage, and fresh gate evidence.
- Fixer prompt `20260429T043529Z` requested the same numbered reviewer-required fixes against the current branch tip, with a new commit and full required gate rerun.
- Fixer prompt `20260429T043929Z` requested the same numbered reviewer-required fixes against the current branch tip, with a new commit, full required gate rerun, and final HEAD SHA.
- Fixer prompt `20260429T044208Z` requested the same numbered reviewer-required fixes against the current branch tip, with a new commit, full required gate rerun, and final HEAD SHA.
- Fixer prompt `20260429T044433Z` requested the same numbered reviewer-required fixes against the current branch tip, with a new commit, full required gate rerun, and final HEAD SHA.
- Fixer prompt `20260429T044747Z` requested the same numbered reviewer-required fixes against the current branch tip, with a new commit, full required gate rerun, and final HEAD SHA.
- The reviewable branch-tip implementation is narrowed to the command-catalog slice:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- `scripts/scope-check.sh` had drifted after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`; this fixer restores it to the submitted baseline so it is no longer a branch-tip implementation change.
- `THREAD.md` and `THREAD_PACKET.md` are metadata-only handoff files.

## Branch-Tip Review Basis

- Review target: branch tip after fixer prompt `20260429T044747Z`.
- Prior implementation anchor: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
- Review range: `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`.
- Matching changed-file scope:
  - `THREAD.md`
  - `THREAD_PACKET.md`
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Branch-tip implementation files:
  - `src/qual/commands/catalog.py`
  - `tests/unit/test_commands_catalog.py`
- Branch-tip metadata-only files:
  - `THREAD.md`
  - `THREAD_PACKET.md`

## Post-Anchor Implementation Commit Ledger

- Ledger source command: `git log --format='- \`%h\` %s' --reverse f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD -- src/qual/commands/catalog.py tests/unit/test_commands_catalog.py`
- Ledger count through the latest implementation/test fixer commit: `193` non-metadata implementation/test commits touched the final implementation file set after the prior implementation anchor.
- Final implementation file set for all listed commits: `src/qual/commands/catalog.py`, `tests/unit/test_commands_catalog.py`.
- No other branch-tip implementation files are part of the selected review target.
- The current fixer commit after prompt `20260429T044747Z` refreshes the handoff packet against the latest branch tip and reruns the required gates; it does not add any new implementation files.

### Post-Anchor Implementation Commits

- `8c9e22903` feat(commands): stabilize command catalog contracts
- `552bec587` Add command parser surface lookup helpers
- `9c485853e` Add MVP command smoke contract
- `81cbb9529` fix(commands): align handoff and catalog tests
- `1abb3bc16` fix(commands): validate CLI parser surface
- `26658f395` Add command CLI shim contract
- `8b52002c3` fix(commands): reject parser surface drift
- `cea5da359` Add invocation metadata to command smoke contract
- `1c579bad3` Add deterministic command shim argv helpers
- `87c41dfce` Add deterministic command resolution helpers
- `adffc42fa` fix(commands): close reviewer packet fixes
- `d71711d73` Add parser-ready command entrypoint argv helper
- `2edf67f71` feat(commands): classify legacy aliases correctly
- `f3e88eb90` Add runnable smoke argv for commands
- `c21223758` fix(commands): reject parser surface drift
- `95b3a1428` Fix parser-ready retrieval command argv
- `e723d68ee` feat(commands): publish smoke argv contract
- `b2883f2ea` Tighten command smoke invocation defaults
- `9bdddce93` Harden command contract validation
- `b8797deee` feat(commands): expose smoke argv in resolution contract
- `17b1ddb79` feat(commands): expose trusted demo path contract
- `f85970321` feat(commands): add demo path helper entrypoints
- `cb93dafab` feat(commands): harden demo path contract
- `621dc00a1` fix(commands): reject parser surface drift
- `4e993d374` feat(commands): add deterministic demo handoff shims
- `177e04efc` Tighten single-token command resolution
- `46f5f4689` Fix command smoke shim resolution
- `8d2e010a3` feat(commands): preserve shim defaults for alias argv
- `5ca68748a` Tighten command shim routing defaults
- `a271eba17` Stabilize default command smoke argv routing
- `0af3da3ae` feat(commands): expose demo path invocation plan
- `e724470e3` Stabilize demo path command shims
- `c95f2e643` Tighten command shim override parsing
- `6b635ee98` Normalize repeated command shim options
- `5f79dabac` Pin terminal shim operation kinds
- `cdbd80913` Harden default command shim pinning
- `b644f9ce0` feat(commands): make retrieval shims parser-ready
- `5fb0987e6` fix(commands): reject parser surface drift
- `88a8b91ce` test(commands): cover extra parser drift case
- `5e1555c6e` feat(commands): expose routed surface tokens
- `1c14fe7cb` Fix parser-ready command alias argv
- `4318eb83c` Tighten demo command surface invocations
- `58b74ba1f` fix(commands): align demo route with mvp path
- `1bf99c36f` feat(commands): include export handoff in demo flow
- `3e97d729b` feat(commands): add patch action compatibility aliases
- `506544f7f` feat(commands): split parser and smoke entry argv
- `35d77e99b` Add demo command shim wrappers
- `72edce647` feat(commands): stabilize terminal argv resolution
- `50b2a281c` Tighten terminal command resolution
- `6eafb0dae` feat(commands): normalize terminal demo entrypoint
- `1c066dc87` feat(commands): separate parser-native demo invocations
- `fb8f9515f` feat(commands): normalize document open aliases
- `05c2050f2` fix(commands): normalize document-open aliases
- `fd780f6a9` feat(commands): expose full command surface aliases
- `c99d67784` fix(commands): cover parser surface drift regressions
- `6dc2ddbcf` fix(commands): refresh reviewer-fix handoff packet
- `4d451643d` fix(commands): refresh reviewer handoff packet
- `b29332c36` Tighten demo command smoke contract
- `a68e4b386` Harden demo command path validation
- `8333cbed7` Stabilize demo flow command resolution
- `378f0c35b` Stabilize demo command resolution defaults
- `36a360a94` feat(commands): expose demo surface invocation table
- `9374dab03` Tighten demo command surface contract
- `7e248ed16` feat(commands): stabilize export handoff demo surface
- `ea00422c0` feat(commands): harden shim argv merging
- `da34f00c9` feat(commands): lock demo loop command contract
- `19ab31af4` feat(commands): expose demo loop contract helpers
- `4eda73af7` Add demo loop surface invocation helpers
- `e1b5aa442` Harden demo loop command fallbacks
- `3a4077039` feat(commands): add demo-path compatibility shims
- `e2e1c437b` Add demo command compatibility contract
- `e63c406f9` Preserve demo compatibility command tokens
- `90aada8a3` feat(commands): model demo loop transitions
- `ea6351e03` feat(commands): keep demo entry args smoke-ready
- `4ceecdfeb` Add demo command compatibility shims
- `79cc54440` Add deterministic demo transition helpers
- `ee4017af1` feat(commands): stabilize demo alias smoke defaults
- `d115b40ce` feat(commands): normalize demo compatibility argv
- `f985b52b1` feat(commands): align preferred demo loop verbs
- `e148af5fe` Add export handoff demo compatibility verbs
- `360f5da63` Harden demo command compatibility wrappers
- `b4f7e0c2e` Add command workflow contract
- `ea30327c8` Tighten demo transition token lookup
- `f87cfd210` Fix demo command fallback routing
- `543632d59` fix(commands): reject cli token drift
- `801532e08` Add workflow compatibility invocation table
- `edff6d8f1` Harden demo command compatibility variants
- `0f4de989f` fix(commands): satisfy reviewer required fixes
- `f7689ab0f` Tighten workflow preferred command tokens
- `82f9f3c79` Add trusted demo next-action command contract
- `802b61876` Tighten demo workflow preferred commands
- `7991f9b72` Normalize demo command compatibility variants
- `fff6b0d24` Add demo workflow entry lookup helpers
- `bc662b7f6` feat(commands): publish demo compatibility variants
- `423adf3c0` feat(commands): preserve demo surface verbs
- `f42c2a9b9` Fix preferred command workflow aliases
- `3f4d46e08` fix(commands): publish next-action compatibility tables
- `984860f57` feat(commands): add trusted demo command surface
- `cba120b30` Add trusted command surface contract
- `7f1d3e7b9` feat(commands): expose preferred next-action invocations
- `6e3889793` feat-commands: stabilize retrieval compatibility surface
- `3e0be5cbf` feat(commands): add trusted surface lookup helpers
- `1e04f9633` Fix command shim subcommand routing
- `b3be9f0c1` feat(commands): enrich trusted surface metadata
- `520d3e027` fix(commands): enforce parser surface contract
- `ab835355e` feat(commands): add token-aware demo workflow plans
- `1fd971590` feat(commands): expose demo path next steps
- `78623946e` feat(commands): preserve demo resolver flow steps
- `c28151d88` fix(commands): refresh parser-surface review packet
- `06540160d` fix(commands): preserve demo flow steps for shim tokens
- `7fe699292` feat(commands): canonicalize demo argv workflow tokens
- `f06839804` docs(commands): narrow cli contract scope wording
- `7a9048df5` feat(commands): harden trusted surface workflow contract
- `6c8d54c79` Harden demo terminal command canonicalization
- `2f6929c11` Fix demo argv flow-step alignment
- `5c5980e88` Add trusted command workflow plan helpers
- `538095c47` test(commands): cover diff parser surface drift
- `11d94ad7e` fix(commands): canonicalize terminal demo verbs
- `86e7450a8` feat(commands): normalize persist-and-continue
- `f629705aa` feat-commands: expose trusted workflow smoke table
- `8565d17fe` feat(commands): preserve demo argv canonicalization
- `088768cd1` Stabilize terminal demo command tokenization
- `aef67223f` fix(commands): lock parser surface contract
- `dbb8e0156` fix(commands): harden parser surface drift checks
- `6890b8c6f` test(commands): lock parser drift regressions to live entrypoints
- `bd118a6cb` test(commands): cover cached parser surface drift
- `11555cb90` feat(commands): add demo persist and export aliases
- `2761b0974` feat(commands): expose workflow branch tokens
- `408430c35` feat(commands): add trusted workflow contract
- `3e1e7d7f9` Add command demo branch contract helpers
- `4cd1d6b48` feat(commands): expose default workflow aliases
- `8e747334f` feat(commands): validate full CLI token projection
- `6952aa212` feat(commands): reject parser projection drift
- `744c0fefc` feat(commands): fail on parser surface drift
- `2c5e1e6ee` fix(commands): derive CLI contract from live parser projection
- `46f340036` Add stable workflow facade helpers
- `b551c0786` fix(commands): harden cli parser surface contract
- `14cb4cde1` fix(commands): harden cli parser surface contract
- `4a4d47048` fix(commands): cover alias-level cli contract drift
- `35d934297` feat(commands): expand workflow facade
- `beaf91853` Fix live CLI contract validation
- `ae1455630` Add workflow transition wrapper helpers
- `dcdca199f` feat-commands: expose trusted workflow surface helpers
- `eeea69811` Add workflow next-action facade helpers
- `2446deb4b` test(commands): cover live parser surface drift
- `75fa7e987` feat(commands): expose workflow smoke surface
- `6d027d03c` test(commands): pin exported parser alias drift
- `9328a0ffe` Fix workflow surface exports
- `de2841102` feat(commands): expose workflow next-action surface lookup
- `526075a09` fix(commands): fail fast on cli parser drift
- `426f2fe5e` test(commands): prove cli drift guard from dispatch path
- `077764032` test(commands): cover context alias drift explicitly
- `3ede0bbf8` fix(commands): prove live parser contract coverage
- `b96781ea3` Add stable command workflow loop surface helpers
- `30b42af0d` Tighten command lookup token discovery
- `9ee534867` Add canonical workflow path surface helpers
- `726ba75a1` fix(feat-commands): align handoff with parser drift fixes
- `75c725bad` fix(commands): finalize parser drift review fixes
- `d5bebedd0` fix(commands): complete parser drift review fixes
- `8ef828730` Derive command contract from live parser
- `aa68932e7` Fix command parser drift review notes
- `9df1a4e32` fix(commands): enforce full CLI contract drift checks
- `445ae9e8d` fix(commands): narrow review tree to catalog slice
- `ea0ab36b4` fix(commands): enforce parser surface drift checks
- `d90bda4f1` fix(commands): close parser drift review fixes
- `e34064479` fix(commands): complete parser drift review fixes
- `18c7c627a` fix(commands): cover declared CLI surface drift
- `01dc806a5` fix(commands): cover lookup table alias drift
- `186cd0109` fix(commands): satisfy parser surface review
- `8b3e51bd8` fix(commands): address 222227 reviewer packet
- `f9d8664aa` fix(commands): address command catalog review fixes
- `daccd1b62` Fix command catalog handoff mapping
- `d54ddede5` fix(commands): address parser surface review
- `4f9cd1263` fix(commands): address 233410 reviewer packet
- `0b3105988` fix(commands): satisfy 235008 reviewer packet
- `5c06ce2f2` fix(commands): cover declared CLI alias order drift
- `1053b093d` fix(commands): finalize CLI surface review packet
- `96b4b4339` fix(commands): satisfy 001026 reviewer packet
- `697e4936d` fix(commands): satisfy 001026 reviewer packet
- `3c9967578` fix(commands): satisfy 002214 reviewer packet
- `8c7cfbea1` fix commands parser surface drift validation
- `02651cbe4` fix(commands): cover same-canonical CLI drift
- `dd3fed5eb` test(commands): cover CLI parser drift examples
- `443b91a18` Fix command parser surface drift coverage
- `8a55375ea` fix(commands): satisfy 022329 reviewer packet
- `4b9044114` fix(commands): satisfy 022926 reviewer packet
- `0715067e8` docs(commands): record 024711 reviewer fixes
- `40332a6ed` fix(commands): address 031719 reviewer packet
- `4bfd780d3` test(commands): cover 035830 parser drift fix
- `b3ebb47ac` test(commands): address 041242 parser drift review

## Current Program Focus

- Close the engine-side Milestone 3 workflow loop before activating any Textual UI lanes.

## Current Engine Execution Order

1. `feat-context-storage` - Persistence floor for document, basket, vault, and session state.
2. `feat-commands` - Stable command surface for the CLI-first MVP loop.
3. `feat-retrieval-fts` - Authoritative FTS-first retrieval for engine runs.
4. `feat-engine-runs` - Close the plan, revise, patch, and apply loop in the engine.
5. `feat-a2ui-contract` - Support the engine loop with stable shared contracts, not UI ambition.

## Scope Goal

- Harden the CLI command contract so `command_cli_contract()` stays deterministic, uses the canonical command order, and fails fast if the parser token surface drifts from the catalog.

## Priority Outcomes

1. Keep command behavior deterministic and easy to smoke-test.
2. Prefer thin command entrypoints over embedded business logic.
3. Preserve compatibility with the canonical engine contract while UI lanes stay disabled.

## Definition Of Done For This Lane

- Core engine actions are reachable through stable commands.
- Command behavior is deterministic and smoke-testable.
- Compatibility shims keep old command surfaces working where required.
- Command handlers stay thin and delegate real behavior to engine code.

## Do Not Spend Time On

- Fancy CLI UX that does not support the MVP loop.
- New command flags that do not help open, retrieve, basket, revise, patch, or save.
- Embedding engine behavior directly in command handlers.

## Lane / Owned Paths

- `src/qual/commands/**`

## Scope Completed

- Strengthened `command_cli_contract()` so it validates the full parser token surface, lookup table, grouped canonical surface, and canonical name order against the declared canonical CLI command surface.
- Added regression coverage for same-canonical drift, unexpected extra accepted aliases, removed expected tokens, token replacement, lookup-table substitution including same-name-set mapping drift, lookup-table ordering drift, and declared-surface drift.
- Narrowed the branch-tip implementation basis by restoring unrelated `scripts/scope-check.sh` drift to baseline.
- Regenerated `THREAD.md` and `THREAD_PACKET.md` so the review packet names the actual branch-tip basis and required-fix satisfaction.

## Kickoff Budget / Limits Compliance

- High-risk shared-file handoff: stayed within the 4-task cap.
- Size stayed within limits: implementation remains one lane-owned command file plus one approved shared test file.

## Approved Exception Note

- Approved shared-test exception for `tests/unit/test_commands_catalog.py`.
- No integrator-locked files are changed.

## Tasks Completed

1. Hardened the CLI contract against full parser-surface drift in `src/qual/commands/catalog.py`; demo-path step supported: stable CLI entrypoints for `open project/document`, `retrieve relevant material`, `promote or gather context into the basket`, `preview and apply or reject a patch`, and `persist/export the updated state`.
2. Added focused tests in `tests/unit/test_commands_catalog.py` for same-canonical drift, canonical-name set drift, missing expected tokens, extra accepted aliases, lookup-table ordering drift, lookup-table substitutions that preserve the canonical-name set, and declared-surface drift; demo-path step supported: repeatable CLI smoke coverage for the same open, retrieve/basket, patch-review, and export command surfaces.
3. Narrowed the branch-tip review basis by restoring unrelated `scripts/scope-check.sh` drift to baseline and documenting only the remaining command-catalog implementation files; demo-path step supported: keeping the `feat-commands` lane focused on command-surface compatibility instead of unrelated scope policy work.
4. Regenerated the handoff packet with canonical demo-path mapping, complete metadata-only file accounting, and reran all required gates; demo-path step supported: auditable Milestone 3 CLI compatibility for the engine-first workflow loop.

## Canonical Demo-Path Mapping

1. CLI parser-surface hardening advances `open project/document`, `retrieve`, `basket`, `revise`, `patch apply/reject`, and `save/export` by keeping the operator command entrypoints stable while Textual remains disabled.
2. Drift regression tests make the CLI smoke surface more reliable for the same demo-path steps, especially `open`, `retrieve/basket`, and `patch review`.
3. Branch narrowing keeps this lane focused on the command-surface compatibility step and avoids mixing scope-check policy work into the MVP demo path.
4. Packet regeneration makes the `feat-commands` handoff auditable for Milestone 3 CLI compatibility.

## Demo-Path Step Made More Real

- The CLI-first command surface for the engine loop is more real: the accepted parser tokens for project open, retrieval/basket, patch review, and export handoff now fail loudly if they drift from the canonical command catalog.

## Concrete Blocker Removed

- This removes the blocker where parser drift could silently change the CLI operator surface before Textual is enabled, which would make the Milestone 3 demo path unreliable to smoke-test through commands.

## Files Changed

### Reviewed Implementation Files

- `src/qual/commands/catalog.py` - lane-owned implementation file.
- `tests/unit/test_commands_catalog.py` - approved shared test file.

### Baseline Restoration

- `scripts/scope-check.sh` - restored to the submitted baseline so it is not part of the branch-tip implementation diff.

### Metadata-Only Handoff Files

- `THREAD.md`
- `THREAD_PACKET.md`

## Ownership Accounting

- Lane-owned implementation edits: `src/qual/commands/catalog.py`.
- Shared-by-approval implementation/test edits: `tests/unit/test_commands_catalog.py` under the approved shared-test exception.
- Integrator-locked edits: none.
- Metadata-only handoff edits: `THREAD.md`, `THREAD_PACKET.md`.
- Shared/integrator-locked edits: `YES` only because the approved shared-test exception touches `tests/unit/test_commands_catalog.py`; no integrator-locked files are edited.

## Required Fixes Addressed From Fixer Prompt `20260429T035831Z`

1. Validated the full accepted parser token surface against the canonical CLI command surface instead of only checking deduplicated canonical names.
2. Added focused tests for same-canonical parser drift, including removed `diff`, added `open`, `diff_preview` replacement, lookup-table mapping drift that preserves the canonical-name set, and declared-surface drift.
3. Regenerated the handoff packet with explicit canonical demo-path mapping for each completed task and a direct statement of which demo-path step is more real.
4. Reran all required gates after the parser-surface, test, and handoff-packet fixes.

## Required Fixes Addressed From Fixer Prompt `20260429T040101Z`

1. Refreshed the handoff packet to name the exact canonical demo-path steps advanced by the command-catalog contract work.
2. Updated each completed task line to include the demo-path step it supports.
3. Added a concise concrete-blocker statement explaining why this is not speculative second-order hardening.
4. This is a metadata-only handoff refresh after prompt `20260429T040101Z`; no implementation files changed after the already-reviewed command-catalog slice, and the required gates were rerun below.

## Required Fixes Addressed From Fixer Prompt `20260429T040347Z`

1. Regenerated this handoff packet against the actual intended branch-tip review target after prompt `20260429T040347Z`.
2. Listed all implementation/test/metadata files changed since `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`, with `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py` as the reviewable implementation/test slice.
3. Preserved the hardened `command_cli_contract()` behavior that validates exact accepted parser tokens, lookup table, grouped canonical surface, declared surface, and canonical command order.
4. Preserved regression coverage for same-canonical parser drift: removed accepted token, added same-canonical alias, replacement alias such as `diff_preview`, lookup-table substitution with the same canonical-name set, and declared-surface drift.
5. Retained the canonical demo-path mapping and explicit statement that the CLI-first command surface for project open, retrieval/basket, patch review, and export handoff is now more reliable to smoke-test.
6. Reran all required gates after this packet refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T040701Z`

1. Confirmed `command_cli_contract()` validates exact accepted parser tokens, lookup table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed regression coverage includes extra known alias drift, missing alias/token drift, substituted same-canonical aliases, parser token ordering drift, lookup-table ordering drift, and declared-surface ordering drift.
3. Regenerated this handoff packet against the current branch-tip review target after prompt `20260429T040701Z`, with `THREAD.md` and `THREAD_PACKET.md` listed as metadata-only files.
4. Kept scope narrowed to `src/qual/commands/**` plus the approved shared test file `tests/unit/test_commands_catalog.py`; no additional shared-path exception is needed.

## Required Fixes Addressed From Fixer Prompt `20260429T040923Z`

1. Confirmed the branch-tip `command_cli_contract()` validates the exact parser surface, including accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for added known aliases, removed tokens, replacement aliases, lookup-table substitutions that preserve the canonical-name set, parser token ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T040923Z` instead of the earlier implementation anchor alone.
4. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
5. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T041242Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Added an explicitly named regression for declared missing accepted-alias drift and preserved coverage for extra known aliases, removed tokens, substituted aliases, parser token ordering drift, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T041242Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T041540Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T041540Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T041829Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T041829Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T042108Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T042108Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T042332Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T042332Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T042639Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T042639Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T042935Z`

1. Confirmed the branch-tip `command_cli_contract()` validates accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order before returning `CommandCliContract`.
2. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for extra same-canonical aliases, missing expected aliases, substituted aliases, parser token ordering drift, lookup-table substitutions that preserve the canonical-name set, lookup-table ordering drift, and declared-surface drift.
3. Refreshed `THREAD.md` and this packet so the reviewer can evaluate the current branch tip after prompt `20260429T042935Z`.
4. Retained complete branch-tip accounting: implementation files are `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
5. Retained the canonical demo-path mapping and concrete-blocker statement: the CLI-first parser surface for project open, retrieval/basket, patch review, and export handoff now fails loudly if it drifts before Textual is enabled.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T043211Z`

1. Regenerated this handoff packet with one unambiguous review target: the current branch tip after the `20260429T043211Z` fixer commit.
2. Listed every post-anchor non-metadata implementation/test commit that touched the final implementation file set after `f8d860ed9f6299f0169c4f21321ac5f37c949fd3`.
3. Kept the final implementation file set explicit: `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`; metadata-only files are `THREAD.md` and `THREAD_PACKET.md`.
4. Restated the selected-code scope as full parser-token surface validation, including accepted parser tokens, lookup-table order, grouped canonical surface, declared CLI surface, and canonical command order.
5. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T043434Z`

1. Regenerated this handoff packet with one unambiguous review target: the current branch tip after the `20260429T043434Z` fixer commit.
2. Kept the branch-tip accounting explicit: review range `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, implementation files `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, metadata-only files `THREAD.md` and `THREAD_PACKET.md`.
3. Confirmed `command_cli_contract()` validates the exact accepted parser token surface and lookup table, not only the deduplicated canonical-name sequence.
4. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for added known alias drift, removed expected token drift, same-canonical alias substitution, parser token ordering drift, and lookup-table substitution.
5. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T043529Z`

1. Regenerated this handoff packet with one unambiguous review target: the current branch tip after the `20260429T043529Z` fixer commit.
2. Kept the branch-tip accounting explicit: review range `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, implementation files `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, metadata-only files `THREAD.md` and `THREAD_PACKET.md`.
3. Confirmed `command_cli_contract()` validates the exact accepted parser token surface, grouped canonical surface, lookup table, and canonical command order.
4. Confirmed regression coverage includes added same-canonical alias drift while canonical names still match, removed tokens, substituted aliases, ordering drift, and lookup-table substitution.
5. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T043929Z`

1. Regenerated this handoff packet with one unambiguous review target: the current branch tip after the `20260429T043929Z` fixer commit.
2. Kept the branch-tip accounting explicit: review range `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, implementation files `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, metadata-only files `THREAD.md` and `THREAD_PACKET.md`.
3. Confirmed `command_cli_contract()` validates the exact accepted parser token surface, grouped canonical surface, lookup table, and canonical command order before returning `CommandCliContract`.
4. Added regression coverage for canonical-name set drift while the parser token and lookup surfaces remain stable, complementing existing removed-token, added-alias, substituted-alias, ordering-drift, lookup-table, and declared-surface drift coverage.
5. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T044208Z`

1. Regenerated this handoff packet with one unambiguous review target: the current branch tip after the `20260429T044208Z` fixer commit.
2. Kept the branch-tip accounting explicit: review range `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, implementation files `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, metadata-only files `THREAD.md` and `THREAD_PACKET.md`.
3. Confirmed `command_cli_contract()` validates the exact accepted parser token surface, grouped canonical surface, lookup table, and canonical command order before returning `CommandCliContract`.
4. Retained regression coverage for added alias, removed expected token, substituted same-canonical alias, parser token ordering drift, and lookup-table substitution, and added coverage for canonical-name set drift while parser token and lookup surfaces remain stable.
5. Restated completed tasks with the canonical demo-path steps they advance and preserved the shared-test approval basis.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T044433Z`

1. Regenerated this handoff packet with one unambiguous review target: the current branch tip after the `20260429T044433Z` fixer commit.
2. Kept the branch-tip accounting explicit: review range `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, implementation files `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, metadata-only files `THREAD.md` and `THREAD_PACKET.md`.
3. Confirmed `command_cli_contract()` validates the exact accepted parser token surface, grouped canonical surface, lookup table, and canonical command order before returning `CommandCliContract`.
4. Added explicit regression coverage for a self-consistent parser projection order drift where parser tokens and lookup table order both move together, complementing the existing added alias, removed token, substituted same-canonical alias, token order, lookup-table substitution, and canonical-name set drift cases.
5. Restated completed tasks with the canonical demo-path steps they advance and preserved the shared-test approval basis.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Required Fixes Addressed From Fixer Prompt `20260429T044747Z`

1. Regenerated this handoff packet with one unambiguous review target: the current branch tip after the `20260429T044747Z` fixer commit.
2. Kept the branch-tip accounting explicit: review range `f8d860ed9f6299f0169c4f21321ac5f37c949fd3..HEAD`, implementation files `src/qual/commands/catalog.py` and `tests/unit/test_commands_catalog.py`, metadata-only files `THREAD.md` and `THREAD_PACKET.md`.
3. Confirmed `command_cli_contract()` validates the exact accepted parser token surface, grouped canonical surface, lookup table, declared CLI surface, and canonical command order before returning `CommandCliContract`.
4. Confirmed focused regression coverage remains in `tests/unit/test_commands_catalog.py` for added alias drift, missing expected token drift, substituted same-canonical alias drift, parser token ordering drift, lookup-table substitution drift, canonical-name set/order drift, and self-consistent parser projection drift.
5. Restated completed tasks with the canonical demo-path steps they advance and preserved the shared-test approval basis.
6. Reran all required gates after this refresh and recorded the outcomes below.

## Commands Run + Outcomes

- `python -m unittest tests.unit.test_commands_catalog`: PASS; ran 76 command-catalog tests.
- `make scope-check`: PASS for branch `codex/feat-commands`.
- `./quality-format.sh --check`: PASS.
- `./quality-lint.sh`: PASS.
- `./quality-test.sh`: PASS; ran smoke tests and 158 unit tests, including full command-catalog parser-surface drift coverage.
- `./typecheck-test.sh`: PASS; compiled Python sources in `src/`.
- `make ci`: PASS; ran scope-check, format, lint, compileall/typecheck, and full quality tests.

## Risks / Blockers

- Risk: `HIGH`.
- Blockers: none.

## Required Handoff Fields

### Branch Name

- `codex/feat-commands`

### Roadmap Item(s) Affected

- Milestone 3: Real workflow loop - preserve CLI compatibility while the package/layout migration lands by keeping the command-catalog contract deterministic and drift-resistant.
- `feat-commands` - CLI compatibility and migration-safe entrypoints for the engine-first MVP loop.

### Vision Capability Affected

- Canonical engine contract - CLI compatibility remains stable while the command-catalog surface rejects parser drift before it can silently change the operator contract.
- Auditable state and workflow - the command surface fails loudly on catalog/parser drift, making the operator-facing contract explicit and traceable.

### Routing / Provider Impact Note

- None. This change only affects local command contract validation and focused command-catalog test coverage.
