from __future__ import annotations

import unittest

from exegesis_textual.panes.document_pane import (
    PendingRewritePreview,
    apply_preview_to_content,
    clean_generated_rewrite_text,
    render_review_document_rich,
    render_review_document_text,
    review_preview_start_location,
)
from exegesis_textual.workflow.rewrite_adapter import MockRewriteSessionAdapter


class RewriteFlowTests(unittest.TestCase):
    def test_mock_rewrite_adapter_creates_patch_from_selection(self) -> None:
        adapter = MockRewriteSessionAdapter()
        adapter.set_selection(
            document_id="current-draft",
            start=5,
            end=16,
            selected_text="first draft",
        )
        proposal = adapter.revise_selection(
            document_id="current-draft",
            instruction_text="tighten this phrase",
            source_chat_slug="chat-main",
        )
        self.assertEqual(proposal.document_id, "current-draft")
        self.assertEqual(proposal.target_range, (5, 16))
        self.assertEqual(proposal.original_text, "first draft")
        self.assertNotEqual(proposal.proposed_text, proposal.original_text)

    def test_render_review_document_text_replaces_selected_span_with_review_block(self) -> None:
        content = "alpha bravo charlie delta"
        preview = PendingRewritePreview(
            patch_id="patch-1",
            document_slug="current-draft",
            target_range=(6, 13),
            original_text="bravo c",
            proposed_text="better text",
            instruction_text="tighten this phrase",
            source_chat_slug="chat-main",
        )
        rendered = render_review_document_text(content, preview)
        self.assertIn("Revision Proposal", rendered)
        self.assertIn("Original", rendered)
        self.assertIn("│ - bravo c", rendered)
        self.assertIn("Proposed", rendered)
        self.assertIn("│ + better text", rendered)
        self.assertNotIn("Instruction:", rendered)

    def test_render_review_document_rich_styles_original_and_proposed_lines(self) -> None:
        content = "alpha bravo charlie delta"
        preview = PendingRewritePreview(
            patch_id="patch-1",
            document_slug="current-draft",
            target_range=(6, 13),
            original_text="bravo c",
            proposed_text="better text",
            instruction_text="tighten this phrase",
            source_chat_slug="chat-main",
        )

        rendered = render_review_document_rich(content, preview)

        self.assertIn("bravo c", rendered.plain)
        self.assertIn("better text", rendered.plain)
        self.assertNotIn("tighten this phrase", rendered.plain)
        self.assertTrue(any(span.style == "white on #14532d" for span in rendered.spans))
        self.assertTrue(any(span.style == "white on #7f1d1d" for span in rendered.spans))

    def test_clean_generated_rewrite_text_removes_proposal_scaffolding(self) -> None:
        document_text = "# Existing Heading\n\nBody"
        generated_text = """Revision Proposal

Instruction: tighten this section

Original
Old text

Proposed
Existing Heading

New text
"""

        self.assertEqual(clean_generated_rewrite_text(document_text, generated_text), "New text")

    def test_apply_preview_to_content_swaps_in_proposed_text(self) -> None:
        content = "alpha bravo charlie delta"
        preview = PendingRewritePreview(
            patch_id="patch-1",
            document_slug="current-draft",
            target_range=(6, 19),
            original_text="bravo charlie",
            proposed_text="revised section",
            instruction_text="rewrite",
            source_chat_slug="chat-main",
        )
        self.assertEqual(apply_preview_to_content(content, preview), "alpha revised section delta")

    def test_review_preview_start_location_targets_review_block(self) -> None:
        content = "\n".join(f"line {index}" for index in range(30))
        start = content.index("line 20")
        preview = PendingRewritePreview(
            patch_id="patch-1",
            document_slug="current-draft",
            target_range=(start, start + len("line 20")),
            original_text="line 20",
            proposed_text="line twenty",
            instruction_text="rewrite",
            source_chat_slug="chat-main",
        )
        self.assertEqual(review_preview_start_location(content, preview), (21, 0))


if __name__ == "__main__":
    unittest.main()
