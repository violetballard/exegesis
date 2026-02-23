# Export Preview and Final Render Spec

## Purpose

- Preview output for final document rendering (CSL + DOCX template aware)
- Shared export options for preview and final export
- Encrypted, short-lived preview artifacts with auditability
- PDF preview as universal rendering target

## Core Rules

- Canonical manuscript source is markdown with citekeys
- Preview and final export share identical options and rendering inputs
- Preview artifacts are encrypted at rest and TTL-bound
- Final export writes plaintext only to user-confirmed destination

## Engine API

- `export.preview(options) -> PreviewArtifactRef`
  - always returns PDF preview artifact reference
  - if output format requested is `docx`, engine may also generate `docx` internally but preview remains `pdf`

- `export.final(options, destination_path, export_approved)`
  - writes only requested output format (`pdf`/`docx`/`latex`)
  - confidential profile requires explicit approval flag

- style/template management:
  - `export.styles.list/add`
  - `export.templates.list/add`

## Storage and Security

- Preview bytes stored as encrypted blobs in vault-local storage
- Preview index stored encrypted
- Default preview TTL: 2 hours
- Cleanup run at service init and can run periodically to remove expired artifacts
- Confidential mode blocks network render backends
- Audit logs include render/export events without file paths or content

## Caching

`options_fingerprint = sha256(markdown + bibliography + csl + template + normalized_options_json)`

- cache hit returns existing unexpired preview artifact
- cache miss renders and stores a new preview artifact

