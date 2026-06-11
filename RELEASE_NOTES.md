# Exegesis 0.1.0.dev2 Release Notes

This Developer preview expands the first public build with the app action registry, notebook-driven actions, multi-provider support, and local confidential projects.

## Highlights

- Mac Apple Silicon packaging path for `Exegesis.app`.
- Textual shell launched through a bundled terminal runtime while presenting as Exegesis.
- Multi-provider model settings and live calls for Mistral, Claude, Google, OpenAI, and local OpenAI-compatible endpoints with secure keyring storage.
- Local confidential project mode for loopback OpenAI-compatible endpoints.
- App action registry support for shared button, shortcut, command palette, A2UI card, and notebook conversation actions.
- File-backed demo-grade writing workflow with project browser, imports, trash, basket, inspector, notebook, summaries, draft/rewrite, search, and compaction UI.
- Packaged writer system prompt integrity check.

## Known Gaps

- Unsigned/ad-hoc preview build.
- Local confidential mode is preview-grade and still file-backed; it is not a substitute for the planned encrypted SQLite/provenance store.
- File-backed storage, not encrypted SQLite.
- No release-channel update flow yet.
