from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Protocol

from src.qual.audit import AuditLog
from src.qual.metrics.crypto import decrypt_bytes, encrypt_bytes

_KEY_FILE = "export_v1.key"
_STYLE_DIR = "export_styles"
_TEMPLATE_DIR = "export_templates"
_PREVIEW_BLOB_DIR = "preview_blobs"
_PREVIEW_INDEX_FILE = "preview_artifacts_v1.enc.json"

_BUNDLED_STYLES: dict[str, bytes] = {
    "apa": b"csl:apa-v1",
    "mla": b"csl:mla-v1",
    "chicago-author-date": b"csl:chicago-author-date-v1",
}
_DEFAULT_TEMPLATE_BYTES = b"docx-template:default-v1"


class RenderBackend(Protocol):
    def uses_network(self) -> bool:
        ...

    def render(
        self,
        *,
        markdown_bytes: bytes,
        bibliography_bytes: bytes,
        csl_bytes: bytes,
        template_bytes: bytes,
        output_formats: tuple[str, ...],
        options_json: bytes,
    ) -> dict[str, bytes]:
        ...


class LocalDeterministicRenderBackend:
    def uses_network(self) -> bool:
        return False

    def render(
        self,
        *,
        markdown_bytes: bytes,
        bibliography_bytes: bytes,
        csl_bytes: bytes,
        template_bytes: bytes,
        output_formats: tuple[str, ...],
        options_json: bytes,
    ) -> dict[str, bytes]:
        seed = hashlib.sha256(
            b"|".join([markdown_bytes, bibliography_bytes, csl_bytes, template_bytes, options_json])
        ).hexdigest()
        out: dict[str, bytes] = {}
        for fmt in output_formats:
            body = (
                f"render-format:{fmt}\n"
                f"seed:{seed}\n"
                f"markdown-bytes:{len(markdown_bytes)}\n"
                f"bibliography-bytes:{len(bibliography_bytes)}\n"
            )
            out[fmt] = body.encode("utf-8")
        return out


@dataclass(frozen=True)
class ExportScope:
    type: str
    id: str


@dataclass(frozen=True)
class ExportInclude:
    title_page: bool
    toc: bool
    figures_tables_list: bool
    bibliography: bool


@dataclass(frozen=True)
class ExportMetadata:
    title: str | None = None
    author: str | None = None
    institution: str | None = None
    running_head: str | None = None
    date: str | None = None


@dataclass(frozen=True)
class ExportConfidentiality:
    profile: str  # confidential | standard


@dataclass(frozen=True)
class ExportLimits:
    max_render_seconds: int = 60
    max_output_bytes: int = 50 * 1024 * 1024


@dataclass(frozen=True)
class ExportOptions:
    style_id: str
    template_id: str
    output_format: str
    scope: ExportScope
    include: ExportInclude
    metadata: ExportMetadata
    confidentiality: ExportConfidentiality
    engine_limits: ExportLimits


@dataclass(frozen=True)
class PreviewArtifactRef:
    artifact_id: str
    output_format: str
    size_bytes: int
    expires_at: str
    options_fingerprint: str
    storage_ref: str


@dataclass(frozen=True)
class ExportArtifactRef:
    artifact_id: str
    output_format: str
    size_bytes: int
    content_hash: str


@dataclass(frozen=True)
class StyleTemplateItem:
    item_id: str
    name: str
    source: str  # bundled|custom


class ExportService:
    def __init__(
        self,
        vault_root: Path,
        *,
        audit_log: AuditLog,
        renderer: RenderBackend | None = None,
        now_fn=None,
    ) -> None:
        self._root = vault_root
        self._root.mkdir(parents=True, exist_ok=True)
        self._audit = audit_log
        self._renderer = renderer if renderer is not None else LocalDeterministicRenderBackend()
        self._now_fn = now_fn or (lambda: datetime.now(UTC))
        self._key = self._load_or_create_key()
        (self._root / _STYLE_DIR).mkdir(exist_ok=True)
        (self._root / _TEMPLATE_DIR).mkdir(exist_ok=True)
        (self._root / _PREVIEW_BLOB_DIR).mkdir(exist_ok=True)
        self.cleanup_expired_previews()

    def preview(self, options: ExportOptions) -> PreviewArtifactRef:
        self._validate_options(options)
        self._assert_confidential_offline(options)
        self._audit.record(
            name="preview_render_requested",
            metadata={"scope": f"{options.scope.type}:{options.scope.id}"},
        )

        markdown_bytes = self._materialize_markdown(options.scope)
        bibliography_bytes = self._materialize_bibliography(options.scope)
        csl_bytes = self._load_style_bytes(options.style_id)
        template_bytes = self._load_template_bytes(options.template_id)
        options_json = self._normalized_options_json(options)
        fingerprint = self._compute_fingerprint(
            markdown_bytes=markdown_bytes,
            bibliography_bytes=bibliography_bytes,
            csl_bytes=csl_bytes,
            template_bytes=template_bytes,
            normalized_options_json=options_json,
        )

        cached = self._find_cached_preview(fingerprint)
        if cached is not None:
            return cached

        output_formats: tuple[str, ...] = ("pdf",)
        if options.output_format == "docx":
            output_formats = ("pdf", "docx")

        rendered = self._renderer.render(
            markdown_bytes=markdown_bytes,
            bibliography_bytes=bibliography_bytes,
            csl_bytes=csl_bytes,
            template_bytes=template_bytes,
            output_formats=output_formats,
            options_json=options_json,
        )
        pdf_bytes = rendered["pdf"]
        self._validate_output_size(options, len(pdf_bytes))
        artifact = self._store_preview_artifact(fingerprint=fingerprint, pdf_bytes=pdf_bytes, options=options)
        self._audit.record(
            name="preview_render_completed",
            metadata={"artifact_id": artifact.artifact_id, "size_bytes": artifact.size_bytes},
        )
        return artifact

    def final(
        self,
        options: ExportOptions,
        *,
        destination_path: Path,
        export_approved: bool = False,
    ) -> ExportArtifactRef:
        self._validate_options(options)
        self._assert_confidential_offline(options)
        self._audit.record(
            name="final_export_requested",
            metadata={"format": options.output_format, "scope": f"{options.scope.type}:{options.scope.id}"},
        )
        if options.confidentiality.profile == "confidential" and not export_approved:
            self._audit.record(name="final_export_denied_by_policy", metadata={"reason": "missing_export_approval"})
            raise PermissionError("Confidential profile requires explicit export approval")

        markdown_bytes = self._materialize_markdown(options.scope)
        bibliography_bytes = self._materialize_bibliography(options.scope)
        csl_bytes = self._load_style_bytes(options.style_id)
        template_bytes = self._load_template_bytes(options.template_id)
        options_json = self._normalized_options_json(options)

        rendered = self._renderer.render(
            markdown_bytes=markdown_bytes,
            bibliography_bytes=bibliography_bytes,
            csl_bytes=csl_bytes,
            template_bytes=template_bytes,
            output_formats=(options.output_format,),
            options_json=options_json,
        )
        output = rendered[options.output_format]
        self._validate_output_size(options, len(output))
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_bytes(output)
        content_hash = hashlib.sha256(output).hexdigest()
        artifact = ExportArtifactRef(
            artifact_id=str(uuid.uuid4()),
            output_format=options.output_format,
            size_bytes=len(output),
            content_hash=content_hash,
        )
        self._audit.record(
            name="final_export_completed",
            metadata={"destination_type": "user_selected_path", "format": options.output_format},
        )
        return artifact

    def list_styles(self) -> list[StyleTemplateItem]:
        items = [StyleTemplateItem(item_id=k, name=k.upper(), source="bundled") for k in sorted(_BUNDLED_STYLES)]
        for path in sorted((self._root / _STYLE_DIR).glob("*.enc")):
            payload = self._decrypt_json_file(path)
            items.append(
                StyleTemplateItem(
                    item_id=str(payload["style_id"]),
                    name=str(payload["name"]),
                    source="custom",
                )
            )
        return items

    def add_style(self, csl_bytes: bytes, name: str) -> str:
        if not csl_bytes:
            raise ValueError("csl_bytes is required")
        style_id = f"custom:{uuid.uuid4()}"
        payload = {"style_id": style_id, "name": name.strip() or "Custom Style", "bytes_hex": csl_bytes.hex()}
        self._encrypt_json_file(self._root / _STYLE_DIR / f"{style_id.replace(':', '_')}.enc", payload)
        return style_id

    def list_templates(self) -> list[StyleTemplateItem]:
        items = [StyleTemplateItem(item_id="default", name="Default", source="bundled")]
        for path in sorted((self._root / _TEMPLATE_DIR).glob("*.enc")):
            payload = self._decrypt_json_file(path)
            items.append(
                StyleTemplateItem(
                    item_id=str(payload["template_id"]),
                    name=str(payload["name"]),
                    source="custom",
                )
            )
        return items

    def add_template(self, docx_bytes: bytes, name: str) -> str:
        if not docx_bytes:
            raise ValueError("docx_bytes is required")
        template_id = f"custom:{uuid.uuid4()}"
        payload = {
            "template_id": template_id,
            "name": name.strip() or "Custom Template",
            "bytes_hex": docx_bytes.hex(),
        }
        self._encrypt_json_file(self._root / _TEMPLATE_DIR / f"{template_id.replace(':', '_')}.enc", payload)
        return template_id

    def cleanup_expired_previews(self) -> int:
        index = self._load_preview_index()
        now = self._now_fn()
        kept: list[dict[str, object]] = []
        removed = 0
        for record in index:
            expires_at = datetime.fromisoformat(str(record["expires_at"]))
            if expires_at <= now:
                blob = self._root / _PREVIEW_BLOB_DIR / str(record["storage_ref"])
                blob.unlink(missing_ok=True)
                removed += 1
                continue
            kept.append(record)
        if removed > 0:
            self._save_preview_index(kept)
        return removed

    def get_preview_pdf_bytes(self, artifact_id: str) -> bytes:
        for record in self._load_preview_index():
            if str(record["artifact_id"]) != artifact_id:
                continue
            blob_path = self._root / _PREVIEW_BLOB_DIR / str(record["storage_ref"])
            return decrypt_bytes(blob_path.read_bytes(), self._key)
        raise KeyError(f"preview artifact not found: {artifact_id}")

    def _store_preview_artifact(
        self,
        *,
        fingerprint: str,
        pdf_bytes: bytes,
        options: ExportOptions,
    ) -> PreviewArtifactRef:
        artifact_id = str(uuid.uuid4())
        storage_ref = f"{artifact_id}.blob.enc"
        expires_at = (self._now_fn() + timedelta(hours=2)).isoformat()
        blob_path = self._root / _PREVIEW_BLOB_DIR / storage_ref
        blob_path.write_bytes(encrypt_bytes(pdf_bytes, self._key))
        record = {
            "artifact_id": artifact_id,
            "created_at": self._now_fn().isoformat(),
            "expires_at": expires_at,
            "scope": f"{options.scope.type}:{options.scope.id}",
            "options_fingerprint": fingerprint,
            "output_format": "pdf",
            "size_bytes": len(pdf_bytes),
            "content_hash": hashlib.sha256(pdf_bytes).hexdigest(),
            "storage_ref": storage_ref,
            "status": "ready",
            "error_summary": None,
        }
        index = self._load_preview_index()
        index.append(record)
        self._save_preview_index(index)
        return PreviewArtifactRef(
            artifact_id=artifact_id,
            output_format="pdf",
            size_bytes=len(pdf_bytes),
            expires_at=expires_at,
            options_fingerprint=fingerprint,
            storage_ref=storage_ref,
        )

    def _find_cached_preview(self, fingerprint: str) -> PreviewArtifactRef | None:
        now = self._now_fn()
        for record in self._load_preview_index():
            if str(record.get("status")) != "ready":
                continue
            if str(record.get("options_fingerprint")) != fingerprint:
                continue
            expires_at = datetime.fromisoformat(str(record["expires_at"]))
            if expires_at <= now:
                continue
            return PreviewArtifactRef(
                artifact_id=str(record["artifact_id"]),
                output_format="pdf",
                size_bytes=int(record["size_bytes"]),
                expires_at=str(record["expires_at"]),
                options_fingerprint=str(record["options_fingerprint"]),
                storage_ref=str(record["storage_ref"]),
            )
        return None

    def _validate_options(self, options: ExportOptions) -> None:
        if options.output_format not in {"pdf", "docx", "latex"}:
            raise ValueError("output_format must be one of: pdf, docx, latex")
        if options.scope.type not in {"section", "manuscript"}:
            raise ValueError("scope.type must be section or manuscript")
        if not options.scope.id.strip():
            raise ValueError("scope id is required")
        if options.confidentiality.profile not in {"confidential", "standard"}:
            raise ValueError("confidentiality.profile must be confidential or standard")
        if options.engine_limits.max_render_seconds <= 0:
            raise ValueError("max_render_seconds must be positive")
        if options.engine_limits.max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be positive")

    def _assert_confidential_offline(self, options: ExportOptions) -> None:
        if options.confidentiality.profile != "confidential":
            return
        if self._renderer.uses_network():
            raise PermissionError("Confidential profile blocks network rendering")

    def _validate_output_size(self, options: ExportOptions, size_bytes: int) -> None:
        if size_bytes > options.engine_limits.max_output_bytes:
            raise ValueError("rendered output exceeds max_output_bytes")

    def _load_style_bytes(self, style_id: str) -> bytes:
        if style_id in _BUNDLED_STYLES:
            return _BUNDLED_STYLES[style_id]
        if not style_id.startswith("custom:"):
            raise ValueError(f"unknown style_id: {style_id}")
        path = self._root / _STYLE_DIR / f"{style_id.replace(':', '_')}.enc"
        if not path.exists():
            raise ValueError(f"unknown custom style_id: {style_id}")
        payload = self._decrypt_json_file(path)
        return bytes.fromhex(str(payload["bytes_hex"]))

    def _load_template_bytes(self, template_id: str) -> bytes:
        if template_id == "default":
            return _DEFAULT_TEMPLATE_BYTES
        if not template_id.startswith("custom:"):
            raise ValueError(f"unknown template_id: {template_id}")
        path = self._root / _TEMPLATE_DIR / f"{template_id.replace(':', '_')}.enc"
        if not path.exists():
            raise ValueError(f"unknown custom template_id: {template_id}")
        payload = self._decrypt_json_file(path)
        return bytes.fromhex(str(payload["bytes_hex"]))

    def _materialize_markdown(self, scope: ExportScope) -> bytes:
        # Canonical markdown remains single source of truth.
        text = f"# Scope {scope.type}:{scope.id}\n\nReference [@smith2020]\n"
        return text.encode("utf-8")

    def _materialize_bibliography(self, scope: ExportScope) -> bytes:
        return f"@article{{smith2020,title={{Scope {scope.id}}}}}\n".encode("utf-8")

    def _compute_fingerprint(
        self,
        *,
        markdown_bytes: bytes,
        bibliography_bytes: bytes,
        csl_bytes: bytes,
        template_bytes: bytes,
        normalized_options_json: bytes,
    ) -> str:
        return hashlib.sha256(
            b"".join(
                [
                    markdown_bytes,
                    bibliography_bytes,
                    csl_bytes,
                    template_bytes,
                    normalized_options_json,
                ]
            )
        ).hexdigest()

    def _normalized_options_json(self, options: ExportOptions) -> bytes:
        payload = asdict(options)
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return normalized.encode("utf-8")

    def _preview_index_path(self) -> Path:
        return self._root / _PREVIEW_INDEX_FILE

    def _load_preview_index(self) -> list[dict[str, object]]:
        path = self._preview_index_path()
        if not path.exists():
            return []
        payload = decrypt_bytes(path.read_bytes(), self._key)
        decoded = json.loads(payload.decode("utf-8"))
        if not isinstance(decoded, list):
            return []
        out: list[dict[str, object]] = []
        for item in decoded:
            if isinstance(item, dict):
                out.append(item)
        return out

    def _save_preview_index(self, records: list[dict[str, object]]) -> None:
        path = self._preview_index_path()
        plaintext = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        path.write_bytes(encrypt_bytes(plaintext, self._key))

    def _load_or_create_key(self) -> bytes:
        key_path = self._root / _KEY_FILE
        if key_path.exists():
            raw = key_path.read_bytes()
            if len(raw) < 32:
                raise ValueError("export key file is invalid")
            return raw[:32]
        raw = uuid.uuid4().bytes + uuid.uuid4().bytes
        key = raw[:32]
        key_path.write_bytes(key)
        return key

    def _encrypt_json_file(self, path: Path, payload: dict[str, object]) -> None:
        plaintext = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        path.write_bytes(encrypt_bytes(plaintext, self._key))

    def _decrypt_json_file(self, path: Path) -> dict[str, object]:
        payload = decrypt_bytes(path.read_bytes(), self._key)
        parsed = json.loads(payload.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("encrypted payload is not an object")
        return parsed
