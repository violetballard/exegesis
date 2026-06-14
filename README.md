# Exegesis Developer Preview

Exegesis is a local-first AI writing workstation for high-trust qualitative research and other traceable knowledge work. It combines a Textual-based writing shell, explicit context basket, project browser, notebook chat, provenance-oriented file handling, and provider-backed model actions.

This Developer preview is source-available proof, not the full commercial product. The recommended path is to download the current Mac release from GitHub. Technical early adopters can also inspect the source, run a manual local build, and follow active development.

For a public overview of the AI-native development workflow behind Exegesis, see
`CONTRIBUTORS.md`.

## What This Preview Includes

- A Mac Apple Silicon Developer preview build path for `Exegesis.app`.
- File-backed projects stored by default in `~/Documents/Exegesis`.
- Multi-provider model settings and live model calls for Mistral, Claude, Google, OpenAI, and local OpenAI-compatible endpoints, with secure API-key storage through Python `keyring`.
- Project-level local confidential mode for loopback OpenAI-compatible endpoints, with confidential projects locked to the local provider profile.
- Document browser, trash/restore/delete flow, import flow, basket context, inspector summaries, notebook chat/search/draft/rewrite/compaction, and transcript guardrails for non-confidential projects.
- App action registry support so visible buttons, shortcuts, command palette actions, A2UI cards, and notebook conversations share one action surface.
- A bundled system prompt with hash validation before model calls.

## Current Limitations

- Mac Apple Silicon first; Windows support is planned later.
- This Developer preview is ad-hoc/unsigned, so macOS may require manual approval to open it.
- Storage is file-backed. It is useful for evaluation, but it is not the final encrypted SQLite/provenance store.
- Local confidential mode requires a loopback OpenAI-compatible endpoint such as LM Studio, Ollama, or another localhost server. It is a Developer preview, not the final encrypted storage system.
- Release channels, signing/notarization, and full update infrastructure are not included yet.

## Recommended Install

1. Open the latest release on GitHub.
2. Download `Exegesis-0.1.0.dev2-macos-arm64-developer-preview.app.zip`.
3. Unzip it and move `Exegesis.app` to `Applications` or another local folder.
4. On first launch, macOS may require approval because this preview is not signed or notarized yet.
5. Open `Model Settings`, choose a provider, enter that provider's API key, and test the connection.

GitHub also provides automatic source archives for each release as `.zip` and `.tar.gz` files. Exegesis does not publish a separate source archive asset for this preview.

## Model Setup

1. Create or use an existing API key for Mistral, Claude, Google, or OpenAI, or configure a local OpenAI-compatible endpoint.
2. Launch Exegesis.
3. Open `Model Settings` from the command palette if it does not open automatically.
4. Paste the key when needed, choose a provider/model/reasoning/context budget, and use `Test connection`.
5. Save the settings.

API keys are not stored in project files or settings JSON. They are stored in the OS secure credential store through Python `keyring` using service `exegesis.developer.providers` and provider-specific accounts such as `mistral`, `claude`, `google`, `openai`, and `local_openai`. The local OpenAI-compatible profile defaults to the placeholder key `local` because most local servers ignore API keys.

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

- Encrypted SQLite storage with durable provenance, history, annotation, code, and basket anchors.
- Notarized Mac releases and a real release channel with update checks.
- Windows packaging after the Apple Silicon preview path is stable.

## Contributing

Exegesis is not accepting pull requests during this Developer preview stage. The public source is available for inspection, learning, and local experimentation, but product development is still moving through an internal roadmap and review process.

Users are welcome to report issues through GitHub Issues. Bug reports, installation problems, confusing workflows, and thoughtful feedback are useful. Please do not include API keys, private research data, transcripts, participant information, or other sensitive material in public issue reports.
