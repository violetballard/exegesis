# Exegesis Developer Preview

Exegesis is a local-first AI writing workstation for high-trust qualitative research and other traceable knowledge work. It combines a Textual-based writing shell, explicit context basket, project browser, notebook chat, provenance-oriented file handling, and Mistral-backed model actions.

This Developer preview is source-available proof, not the full commercial product. The recommended path is to download the current Mac release from GitHub. Technical early adopters can also inspect the source, run a manual local build, and follow active development.

## What This Preview Includes

- A Mac Apple Silicon Developer preview build path for `Exegesis.app`.
- File-backed projects stored by default in `~/Documents/Exegesis`.
- Mistral-only model settings with secure API-key storage through Python `keyring`.
- Document browser, trash/restore/delete flow, import flow, basket context, inspector summaries, notebook chat/search/draft/rewrite/compaction, and transcript guardrails for non-confidential mode.
- A bundled system prompt with hash validation before model calls.

## Current Limitations

- Mac Apple Silicon first; Windows support is planned later.
- The first preview is ad-hoc/unsigned, so macOS may require manual approval to open it.
- Storage is file-backed. It is useful for evaluation, but it is not the final encrypted SQLite/provenance store.
- Only Mistral is supported in the first preview. OpenAI, Claude, custom OpenAI-compatible endpoints, and local confidential projects are planned follow-ups.
- Release channels, signing/notarization, and full update infrastructure are not included yet.

## Recommended Install

1. Open the latest release on GitHub.
2. Download `Exegesis-0.1.0.dev1-macos-arm64-developer-preview.app.zip`.
3. Unzip it and move `Exegesis.app` to `Applications` or another local folder.
4. On first launch, macOS may require approval because this preview is not signed or notarized yet.
5. Open `Model Settings`, enter a Mistral API key, and test the connection.

GitHub also provides automatic source archives for each release as `.zip` and `.tar.gz` files. Exegesis does not publish a separate source archive asset for this preview.

## Mistral Setup

1. Create or use an existing Mistral API key.
2. Launch Exegesis.
3. Open `Model Settings` from the command palette if it does not open automatically.
4. Paste the key, choose a Mistral model, and use `Test connection`.
5. Save the settings.

API keys are not stored in project files or settings JSON. They are stored in the OS secure credential store through Python `keyring` using service `exegesis.developer.providers` and account `mistral`.

## File-Backed Storage Warning

This preview stores project documents as local files. Do not use it as the system of record for sensitive research data yet. The encrypted SQLite/provenance layer is coming next and is the intended foundation for confidential research workflows.

## Building The Mac Developer Preview

Manual builds are mainly for developers who want to inspect or modify the source before running the app. From a clean checkout on Apple Silicon macOS:

```bash
scripts/release/build_macos_developer_preview.sh
```

The build script regenerates the app icon from `packaging/macos/AppIcon.iconset`, downloads the pinned WezTerm runtime, verifies its SHA256, runs Briefcase, patches visible app identity to `Exegesis`, exports the public source tree used by the public branch, and writes release hashes for the app artifact.

Build output is written under `packaging/release/artifacts/macos-developer-preview/`.

## License

This Developer preview source is available under MIT plus Commons Clause. You may inspect, run, modify, and redistribute the source, but you may not sell Exegesis or a product/service whose value derives substantially from this software without a separate commercial license from Violet Ballard.

## Coming Next

- Multi-provider model setup for OpenAI, Claude, and custom OpenAI-compatible endpoints.
- Local confidential preview mode for localhost model endpoints.
- Encrypted SQLite storage with durable provenance, history, annotation, code, and basket anchors.
- A real release channel with signing, notarization, and update checks.

## Contributing

Exegesis is not accepting pull requests during this Developer preview stage. The public source is available for inspection, learning, and local experimentation, but product development is still moving through an internal roadmap and review process.

Users are welcome to report issues through GitHub Issues. Bug reports, installation problems, confusing workflows, and thoughtful feedback are useful. Please do not include API keys, private research data, transcripts, participant information, or other sensitive material in public issue reports.
