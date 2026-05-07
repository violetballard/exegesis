# Thread Ownership Map

Use these branch lanes to avoid duplicate work and keep the staged migration coherent.

Detailed task breakdown lives in `/Users/doctor-violet/Library/CloudStorage/Box-Box/projects/qual/docs/TASKS.md`.

## Active engine lanes

- `codex/feat-commands*`
  - Owned paths:
    - `src/qual/commands/**`
  - Shared by approval only:
    - `src/main.py`
    - `src/qual/cli.py`
    - `src/qual/app.py`
    - `tests/unit/test_commands_catalog.py`
    - `tests/unit/test_diff_preview.py`

- `codex/feat-context-storage*`
  - Owned paths:
    - `src/qual/context/**`
    - `src/qual/storage/**`
    - `engine/src/exegesis_engine/state/**`
    - `engine/src/exegesis_engine/storage/**`
  - Shared by approval only:
    - `src/qual/config.py`

- `codex/feat-retrieval-fts*`
  - Owned paths:
    - `src/qual/retrieval/**`
    - `src/qual/engine/retrieval/**`
    - `engine/src/exegesis_engine/retrieval/**`
  - Shared by approval only:
    - `tests/unit/test_unified_retrieval.py`

- `codex/feat-a2ui-contract*`
  - Owned paths:
    - `src/qual/ui/a2ui.py`
    - `shared/src/exegesis_shared/contracts/**`
    - `shared/src/exegesis_shared/models/**`
    - `shared/src/exegesis_shared/types/**`

- `codex/feat-engine-runs*`
  - Owned paths:
    - `src/qual/engine/**`
    - `src/qual/drafting/**`
    - `engine/src/exegesis_engine/api/**`
    - `engine/src/exegesis_engine/workflow/**`
    - `engine/src/exegesis_engine/patches/**`
    - `engine/src/exegesis_engine/audit/**`
    - `engine/src/exegesis_engine/services/**`

## Defined but disabled UI lanes

- `codex/feat-console-shell*`
  - Owned paths:
    - `client-textual/src/exegesis_textual/app/**`
    - `client-textual/src/exegesis_textual/layout/**`
    - `client-textual/src/exegesis_textual/panes/**`
    - `client-textual/src/exegesis_textual/commands/**`
    - `client-textual/src/exegesis_textual/shortcuts/**`
    - `client-textual/src/exegesis_textual/inspectors/**`
    - `client-textual/src/exegesis_textual/theme/**`
  - Current status:
    - disabled until the Textual dependency is intentionally added

- `codex/feat-console-workflow*`
  - Owned paths:
    - `client-textual/src/exegesis_textual/workflow/**`
    - `client-textual/src/exegesis_textual/cards/**`
    - `client-textual/src/exegesis_textual/events/**`
  - Current status:
    - disabled until the Textual dependency is intentionally added

## Defined but disabled future feature lanes

- `codex/feat-ocr-import*`
  - Owned paths:
    - `src/qual/imports/**`
    - `src/qual/ocr/**`
    - `engine/src/exegesis_engine/imports/**`
    - `engine/src/exegesis_engine/ocr/**`
  - Current status:
    - disabled until OCR import is intentionally activated

- `codex/feat-literature-import*`
  - Owned paths:
    - `src/qual/literature/**`
    - `engine/src/exegesis_engine/literature/**`
  - Current status:
    - disabled until literature metadata import is intentionally activated

- `codex/feat-rag-index*`
  - Owned paths:
    - `src/qual/rag/**`
    - `engine/src/exegesis_engine/rag/**`
    - `engine/src/exegesis_engine/retrieval/rag/**`
  - Current status:
    - disabled until RAG indexing and vector retrieval are intentionally activated

- `codex/feat-qual-coding*`
  - Owned paths:
    - `src/qual/coding/**`
    - `src/qual/project_folders/**`
    - `engine/src/exegesis_engine/coding/**`
    - `engine/src/exegesis_engine/project_folders/**`
    - `client-textual/src/exegesis_textual/coding/**`
  - Current status:
    - disabled until qualitative coding is intentionally activated

- `codex/feat-editor-basics*`
  - Owned paths:
    - `src/qual/editor/**`
    - `engine/src/exegesis_engine/editor/**`
    - `client-textual/src/exegesis_textual/editor/**`
    - `client-textual/src/exegesis_textual/shortcuts/editor/**`
  - Current status:
    - disabled until editor basics are intentionally activated

- `codex/feat-citations*`
  - Owned paths:
    - `src/qual/citations/**`
    - `engine/src/exegesis_engine/citations/**`
    - `shared/src/exegesis_shared/citations/**`
    - `client-textual/src/exegesis_textual/citations/**`
  - Current status:
    - disabled until citation support is intentionally activated

- `codex/feat-export*`
  - Owned paths:
    - `src/qual/export/**`
    - `engine/src/exegesis_engine/export/**`
    - `client-textual/src/exegesis_textual/export/**`
  - Current status:
    - disabled until export support is intentionally activated

- `codex/feat-zotero-import*`
  - Owned paths:
    - `src/qual/zotero/**`
    - `engine/src/exegesis_engine/zotero/**`
    - `client-textual/src/exegesis_textual/zotero/**`
  - Current status:
    - disabled until Zotero import is intentionally activated

- `codex/feat-formatting-bar*`
  - Owned paths:
    - `src/qual/formatting/**`
    - `engine/src/exegesis_engine/formatting/**`
    - `client-textual/src/exegesis_textual/formatting/**`
  - Current status:
    - disabled until formatting bar work is intentionally activated

- `codex/feat-developer-provider-config*`
  - Owned paths:
    - `src/qual/providers/**`
    - `src/qual/credentials/**`
    - `engine/src/exegesis_engine/providers/**`
    - `engine/src/exegesis_engine/credentials/**`
    - `client-textual/src/exegesis_textual/providers/**`
    - `client-textual/src/exegesis_textual/commands/provider_config/**`
  - Current status:
    - disabled until developer provider configuration is intentionally activated

- `codex/feat-desktop-packaging*`
  - Owned paths:
    - `desktop-shell/**`
    - `scripts/packaging/**`
    - `scripts/release/**`
    - `docs/packaging/**`
  - Current status:
    - disabled until desktop packaging is intentionally activated

- `codex/feat-cop-lite-licensing*`
  - Owned paths:
    - `engine/src/exegesis_engine/licensing/**`
    - `engine/src/exegesis_engine/lite_gateway/**`
    - `engine/src/exegesis_engine/nanonets_usage/**`
    - `client-textual/src/exegesis_textual/licensing/**`
    - `client-textual/src/exegesis_textual/imports/**`
    - `shared/src/exegesis_shared/licensing/**`
    - `shared/src/exegesis_shared/nanonets_usage/**`
    - `docs/licensing/**`
  - Current status:
    - disabled until Lite licensing and Nanonets page-credit work is intentionally activated

- `codex/feat-browser-pdf-capture*`
  - Owned paths:
    - `browser-extension/**`
    - `engine/src/exegesis_engine/browser_capture/**`
    - `client-textual/src/exegesis_textual/browser_capture/**`
    - `shared/src/exegesis_shared/browser_capture/**`
    - `desktop-shell/browser_extension/**`
    - `scripts/browser_extension/**`
    - `docs/browser_extension/**`
  - Current status:
    - disabled until post-MVP browser PDF capture work is intentionally activated

## Retired planning targets

- `codex/feat-ux-flow*`
- `codex/feat-console*`

These legacy lanes are superseded by the staged `engine / client-textual / shared` split and should not be restarted.

## Integrator-locked files

Only integrator/release work should edit these unless explicitly approved:
- `README.md`
- `INTEGRATION.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `PRODUCT_VISION.md`
- `THREAD_OWNERSHIP.md`
- `src/main.py`
- `src/qual/cli.py`
- `src/qual/app.py`

## Enforcement

- Run `make scope-check` before handoff.
- `make ci` runs scope-check automatically.
- Shared-file exceptions for approved edits can be passed as:
  - `SCOPE_ALLOW_SHARED=1 make scope-check`
