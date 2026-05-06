# Future Import, OCR, Literature Metadata, and RAG Specs

This document defines disabled future work. It is specification scaffolding only:
no runtime OCR, literature metadata extraction, RAG indexing, shell import filtering,
or inspector editing should be active until the relevant lane is explicitly enabled.

## Milestone 6: OCR Import

Lane: `feat-ocr-import` (disabled)

Intent:
- Keep Markdown import direct and editable without OCR.
- Route non-Markdown imports through OCR into normalized editable Markdown.
- Make OCR provenance durable enough for later audit, metadata extraction, and RAG indexing.

Model targets:
- Online OCR: Nanonets OCR-3.
- Local/offline OCR: Nanonets OCR2.

Supported source formats:
- Markdown: `md`, `markdown`.
- OCR-backed imports: `pdf`, `png`, `jpg`, `jpeg`, `tiff`, `tif`, `docx`, `txt`, `csv`, `xls`, `xlsx`.

Future OCR provenance:
- original filename
- MIME type or extension
- OCR provider and model
- page, image, or sheet index when applicable
- content hash
- confidence when available

References:
- [Nanonets OCR-3](https://nanonets.com/research/nanonets-ocr-3)
- [Nanonets supported file formats](https://docs.nanonets.com/docs/file-formats)
- [Nanonets OCR2-3B](https://huggingface.co/nanonets/Nanonets-OCR2-3B)

## Milestone 7: Literature Import

Lane: `feat-literature-import` (disabled)

Intent:
- Treat literature as a selected import type inside the import modal.
- Run metadata extraction for Markdown literature as well as OCR-derived literature.
- Keep literature metadata editable at approval time and later in the inspector.

Future metadata fields:
- title
- authors
- venue or publication
- year or date
- DOI
- URL
- abstract
- citation string

Extraction order:
- Prefer deterministic signals first: frontmatter, DOI regex, BibTeX, headings, title block, and first-page heuristics.
- Use model-assisted extraction only to fill candidate fields after deterministic parsing.
- Preserve uncertainty as editable candidate metadata rather than inventing missing values.

Future shell behavior:
- Import modal exposes an import-type picker including `literature`.
- Literature import shows a centered metadata approval modal.
- Approval modal fields are editable before save.
- Inspector can edit saved literature metadata after import.

## Milestone 8: RAG Indexing and Retrieval

Lane: `feat-rag-index` (disabled)

Intent:
- Index normalized Markdown from direct Markdown imports and OCR-derived documents.
- Keep FTS as the baseline retrieval path.
- Add vector retrieval as an additive path once indexing is enabled.

Chunking contract:
- Target 350-500 tokens per chunk.
- Use 75-100 token overlap.
- Preserve tables and code blocks when practical.
- Store document ID, document type, literature metadata reference, heading path, source offsets, token estimate, content hash, and chunk text.

Embedding targets:
- Online embeddings: Mistral `mistral-embed`.
- Local embeddings: Qwen3-Embedding-0.6B.

Future retrieval behavior:
- Merge FTS and vector hits.
- Deduplicate by document/chunk hash.
- Return structured retrieval cards suitable for basket promotion.

References:
- [Mistral Embed](https://docs.mistral.ai/models/model-cards/mistral-embed-23-12)
- [Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)
