from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.exporting.service import (
    ExportConfidentiality,
    ExportInclude,
    ExportLimits,
    ExportMetadata,
    ExportOptions,
    ExportScope,
    ExportService,
)


class _CountingBackend:
    def __init__(self, *, network: bool = False) -> None:
        self.calls = 0
        self._network = network

    def uses_network(self) -> bool:
        return self._network

    def render(self, **kwargs) -> dict[str, bytes]:
        self.calls += 1
        output_formats = kwargs["output_formats"]
        out: dict[str, bytes] = {}
        for fmt in output_formats:
            out[fmt] = f"{fmt}-render-{self.calls}".encode("utf-8")
        return out


class ExportPreviewFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.audit = AuditLog(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_preview_always_returns_pdf_for_docx_request(self) -> None:
        backend = _CountingBackend()
        svc = ExportService(self.root, audit_log=self.audit, renderer=backend)
        artifact = svc.preview(self._options(output_format="docx"))
        self.assertEqual(artifact.output_format, "pdf")
        self.assertEqual(backend.calls, 1)
        data = svc.get_preview_pdf_bytes(artifact.artifact_id)
        self.assertTrue(data.startswith(b"pdf-render"))

    def test_preview_cache_uses_same_fingerprint_without_rerender(self) -> None:
        backend = _CountingBackend()
        svc = ExportService(self.root, audit_log=self.audit, renderer=backend)
        first = svc.preview(self._options())
        second = svc.preview(self._options())
        self.assertEqual(first.artifact_id, second.artifact_id)
        self.assertEqual(backend.calls, 1)

    def test_preview_blob_is_encrypted_at_rest(self) -> None:
        backend = _CountingBackend()
        svc = ExportService(self.root, audit_log=self.audit, renderer=backend)
        artifact = svc.preview(self._options())
        blob_path = self.root / "preview_blobs" / artifact.storage_ref
        blob_bytes = blob_path.read_bytes()
        self.assertNotIn(b"pdf-render", blob_bytes)

    def test_confidential_profile_blocks_network_backend(self) -> None:
        svc = ExportService(self.root, audit_log=self.audit, renderer=_CountingBackend(network=True))
        with self.assertRaises(PermissionError):
            svc.preview(self._options(confidentiality_profile="confidential"))

    def test_final_export_requires_explicit_approval_in_confidential(self) -> None:
        backend = _CountingBackend()
        svc = ExportService(self.root, audit_log=self.audit, renderer=backend)
        out_path = self.root / "out" / "manuscript.docx"
        with self.assertRaises(PermissionError):
            svc.final(
                self._options(output_format="docx", confidentiality_profile="confidential"),
                destination_path=out_path,
                export_approved=False,
            )
        self.assertFalse(out_path.exists())
        result = svc.final(
            self._options(output_format="docx", confidentiality_profile="confidential"),
            destination_path=out_path,
            export_approved=True,
        )
        self.assertEqual(result.output_format, "docx")
        self.assertTrue(out_path.exists())

    def test_cleanup_removes_expired_preview_artifacts(self) -> None:
        now = datetime(2026, 2, 23, 18, 0, tzinfo=UTC)
        backend = _CountingBackend()
        svc = ExportService(self.root, audit_log=self.audit, renderer=backend, now_fn=lambda: now)
        artifact = svc.preview(self._options())
        self.assertEqual(svc.cleanup_expired_previews(), 0)
        now = now + timedelta(hours=3)
        removed = svc.cleanup_expired_previews()
        self.assertEqual(removed, 1)
        with self.assertRaises(KeyError):
            svc.get_preview_pdf_bytes(artifact.artifact_id)

    def test_styles_and_templates_support_custom_entries(self) -> None:
        svc = ExportService(self.root, audit_log=self.audit, renderer=_CountingBackend())
        before_styles = {x.item_id for x in svc.list_styles()}
        before_templates = {x.item_id for x in svc.list_templates()}
        style_id = svc.add_style(b"<csl/>", "Uni CSL")
        template_id = svc.add_template(b"docx-bytes", "Uni Docx")
        after_styles = {x.item_id for x in svc.list_styles()}
        after_templates = {x.item_id for x in svc.list_templates()}
        self.assertIn(style_id, after_styles - before_styles)
        self.assertIn(template_id, after_templates - before_templates)

    def test_audit_events_record_without_destination_path_leak(self) -> None:
        svc = ExportService(self.root, audit_log=self.audit, renderer=_CountingBackend())
        out_path = self.root / "final" / "paper.pdf"
        svc.preview(self._options())
        svc.final(
            self._options(output_format="pdf", confidentiality_profile="standard"),
            destination_path=out_path,
            export_approved=True,
        )
        lines = (self.root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()
        names = [json.loads(line)["name"] for line in lines]
        self.assertIn("preview_render_requested", names)
        self.assertIn("preview_render_completed", names)
        self.assertIn("final_export_requested", names)
        self.assertIn("final_export_completed", names)
        for line in lines:
            payload = json.loads(line)
            self.assertNotIn(str(out_path), json.dumps(payload, sort_keys=True))

    @staticmethod
    def _options(
        *,
        output_format: str = "pdf",
        confidentiality_profile: str = "standard",
    ) -> ExportOptions:
        return ExportOptions(
            style_id="apa",
            template_id="default",
            output_format=output_format,
            scope=ExportScope(type="section", id="sec-1"),
            include=ExportInclude(
                title_page=True,
                toc=False,
                figures_tables_list=False,
                bibliography=True,
            ),
            metadata=ExportMetadata(title="Sample"),
            confidentiality=ExportConfidentiality(profile=confidentiality_profile),
            engine_limits=ExportLimits(max_render_seconds=60, max_output_bytes=50 * 1024 * 1024),
        )


if __name__ == "__main__":
    unittest.main()
