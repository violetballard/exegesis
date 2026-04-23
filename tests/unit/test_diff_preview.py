from __future__ import annotations

import hashlib
import json
import os
import unittest
from contextlib import contextmanager

from src.qual.commands.diff_preview import (
    INCLUDE_FINGERPRINT_ENV,
    INCLUDE_SUMMARY_ENV,
    MAX_DIFF_OUTPUT_CHARS_ENV,
    ORIGINAL_LABEL_ENV,
    OUTPUT_FORMAT_ENV,
    PROPOSED_LABEL_ENV,
    SUMMARY_ONLY_ENV,
    SUPPRESS_FILE_HEADERS_ENV,
    DiffPreviewInput,
    run_diff_preview,
)


@contextmanager
def _env(**updates: str | None):
    saved: dict[str, str | None] = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class DiffPreviewBehaviorTests(unittest.TestCase):
    def test_default_output_unchanged_when_env_unset(self) -> None:
        with _env(
            **{
                INCLUDE_SUMMARY_ENV: None,
                SUMMARY_ONLY_ENV: None,
                SUPPRESS_FILE_HEADERS_ENV: None,
                MAX_DIFF_OUTPUT_CHARS_ENV: None,
            }
        ):
            output = run_diff_preview(DiffPreviewInput("a\n", "b\n"))
        self.assertTrue(output.startswith("--- original\n+++ proposed\n"))
        self.assertNotIn("Diff summary:", output)

    def test_summary_counts_and_hunks_are_correct(self) -> None:
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUMMARY_ONLY_ENV: None}):
            output = run_diff_preview(DiffPreviewInput("a\nold\n", "a\nnew1\nnew2\n"))
        self.assertTrue(output.rstrip().endswith("Diff summary: +2 -1 (hunks: 1)"))

    def test_summary_only_takes_precedence(self) -> None:
        with _env(
            **{
                SUMMARY_ONLY_ENV: "true",
                INCLUDE_SUMMARY_ENV: "1",
                MAX_DIFF_OUTPUT_CHARS_ENV: "40",
            }
        ):
            output = run_diff_preview(
                DiffPreviewInput(
                    "\n".join(f"a{i}" for i in range(500)) + "\n",
                    "\n".join(f"b{i}" for i in range(500)) + "\n",
                )
            )
        self.assertTrue(output.startswith("Diff summary: +"))
        self.assertNotIn("diff truncated", output)

    def test_header_suppression_keeps_counts_stable(self) -> None:
        base = DiffPreviewInput("a\nold\n", "a\nnew1\nnew2\n")
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "0"}):
            output_headers = run_diff_preview(base)
        with _env(**{INCLUDE_SUMMARY_ENV: "1", SUPPRESS_FILE_HEADERS_ENV: "yes"}):
            output_suppressed = run_diff_preview(base)
        self.assertTrue(output_headers.startswith("--- original\n+++ proposed\n"))
        self.assertFalse(output_suppressed.startswith("--- original\n+++ proposed\n"))
        self.assertEqual(output_headers.splitlines()[-1], output_suppressed.splitlines()[-1])

    def test_summary_only_does_not_override_no_diff_messages(self) -> None:
        with _env(**{SUMMARY_ONLY_ENV: "1"}):
            both_empty = run_diff_preview(DiffPreviewInput("", ""))
            identical = run_diff_preview(DiffPreviewInput("same\n", "same\n"))
        self.assertEqual(both_empty, "No diff: both inputs are empty.")
        self.assertEqual(identical, "No diff: inputs are identical after normalization.")

    def test_json_output_omits_fingerprint_when_flag_unset(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: None,
                INCLUDE_SUMMARY_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a\nold\n", "a\nnew\n")))
        self.assertEqual(payload["command"], "diff-preview")
        self.assertIsNone(payload["fingerprint"])
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["summary"]["text"], "Diff summary: +1 -1 (hunks: 1)")
        self.assertIn("--- original", payload["diff"])

    def test_json_output_includes_labeled_diff_and_matching_fingerprint(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: "1",
                ORIGINAL_LABEL_ENV: "before.txt",
                PROPOSED_LABEL_ENV: "after.txt",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a\n", "b\n")))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["labels"]["original"], "before.txt")
        self.assertEqual(payload["labels"]["proposed"], "after.txt")
        self.assertTrue(payload["diff"].startswith("--- before.txt\n+++ after.txt\n"))
        self.assertEqual(
            payload["fingerprint"]["sha256"],
            hashlib.sha256(payload["diff"].encode("utf-8")).hexdigest(),
        )

    def test_json_output_marks_labels_applied_before_header_suppression(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                SUPPRESS_FILE_HEADERS_ENV: "1",
                ORIGINAL_LABEL_ENV: "before.txt",
                PROPOSED_LABEL_ENV: "after.txt",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a\n", "b\n")))
        self.assertTrue(payload["labels"]["applied"])
        self.assertFalse(payload["diff"].startswith("--- before.txt\n+++ after.txt\n"))

    def test_json_no_diff_shape_is_stable(self) -> None:
        with _env(**{OUTPUT_FORMAT_ENV: "json"}):
            payload = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(
            payload,
            {
                "command": "diff-preview",
                "diff": "",
                "fingerprint": None,
                "labels": {
                    "applied": False,
                    "original": "original",
                    "proposed": "proposed",
                },
                "message": "No diff: inputs are identical after normalization.",
                "options": {
                    "canonicalize_inline_whitespace": False,
                    "ignore_all_blank_lines": False,
                    "ignore_case": False,
                    "ignore_edge_blank_lines": False,
                    "ignore_trailing_whitespace": False,
                    "include_options_banner": False,
                    "include_summary": False,
                    "max_output_chars": 20000,
                    "strip_ansi": False,
                    "suppress_file_headers": False,
                    "truncation_strategy": "middle",
                },
                "status": "no_diff",
                "summary": None,
                "summary_only": False,
                "truncated": False,
            },
        )

    def test_json_no_diff_summary_only_reflects_env(self) -> None:
        with _env(**{OUTPUT_FORMAT_ENV: "json", SUMMARY_ONLY_ENV: "1"}):
            payload = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(payload["status"], "no_diff")
        self.assertEqual(payload["command"], "diff-preview")
        self.assertTrue(payload["summary_only"])
        self.assertEqual(payload["diff"], "")

    def test_json_no_diff_summary_only_preserves_shape_with_other_flags(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                SUMMARY_ONLY_ENV: "1",
                INCLUDE_SUMMARY_ENV: "1",
                INCLUDE_FINGERPRINT_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(payload["status"], "no_diff")
        self.assertTrue(payload["summary_only"])
        self.assertIsNone(payload["summary"])
        self.assertIsNone(payload["fingerprint"])
        self.assertFalse(payload["labels"]["applied"])
        self.assertEqual(payload["diff"], "")

    def test_json_no_diff_summary_only_ignores_fingerprint_gate(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                SUMMARY_ONLY_ENV: "1",
                INCLUDE_FINGERPRINT_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(payload["status"], "no_diff")
        self.assertTrue(payload["summary_only"])
        self.assertIsNone(payload["fingerprint"])
        self.assertEqual(payload["diff"], "")

    def test_json_no_diff_summary_only_ignores_fingerprint_flag(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                SUMMARY_ONLY_ENV: "1",
                INCLUDE_FINGERPRINT_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(payload["status"], "no_diff")
        self.assertTrue(payload["summary_only"])
        self.assertIsNone(payload["fingerprint"])
        self.assertEqual(payload["message"], "No diff: inputs are identical after normalization.")

    def test_json_no_diff_includes_effective_labels_and_options(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                ORIGINAL_LABEL_ENV: "before.txt",
                PROPOSED_LABEL_ENV: "after.txt",
                INCLUDE_SUMMARY_ENV: "1",
                SUPPRESS_FILE_HEADERS_ENV: "1",
                MAX_DIFF_OUTPUT_CHARS_ENV: "512",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(payload["labels"]["original"], "before.txt")
        self.assertEqual(payload["labels"]["proposed"], "after.txt")
        self.assertFalse(payload["labels"]["applied"])
        self.assertTrue(payload["summary_only"] is False)
        self.assertTrue(payload["options"]["include_summary"])
        self.assertTrue(payload["options"]["suppress_file_headers"])
        self.assertEqual(payload["options"]["max_output_chars"], 512)

    def test_text_fingerprint_matches_emitted_labeled_and_truncated_diff(self) -> None:
        with _env(
            **{
                INCLUDE_FINGERPRINT_ENV: "1",
                ORIGINAL_LABEL_ENV: "old.txt",
                PROPOSED_LABEL_ENV: "new.txt",
                MAX_DIFF_OUTPUT_CHARS_ENV: "80",
            }
        ):
            output = run_diff_preview(
                DiffPreviewInput(
                    "\n".join(f"old{i}" for i in range(50)) + "\n",
                    "\n".join(f"new{i}" for i in range(50)) + "\n",
                )
            )
        diff_output, fingerprint_line = output.rsplit("\n\n", 1)
        self.assertTrue(diff_output.startswith("--- old.txt\n+++ new.txt\n"))
        self.assertEqual(
            fingerprint_line,
            f"Diff fingerprint: sha256:{hashlib.sha256(diff_output.encode('utf-8')).hexdigest()}",
        )

    def test_text_summary_only_fingerprint_matches_reviewed_diff_payload(self) -> None:
        with _env(
            **{
                INCLUDE_FINGERPRINT_ENV: "1",
                SUMMARY_ONLY_ENV: "1",
            }
        ):
            output = run_diff_preview(DiffPreviewInput("a\n", "b\n"))
        self.assertTrue(output.startswith("Diff summary: +"))
        reviewed_diff = "--- original\n+++ proposed\n@@ -1 +1 @@\n-a\n+b\n"
        self.assertTrue(
            output.endswith(
                f"Diff fingerprint: sha256:{hashlib.sha256(reviewed_diff.encode('utf-8')).hexdigest()}"
            )
        )

    def test_summary_only_json_fingerprint_matches_reviewed_diff_payload(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: "1",
                SUMMARY_ONLY_ENV: "1",
            }
        ):
            payload = json.loads(run_diff_preview(DiffPreviewInput("a\n", "b\n")))
        self.assertEqual(payload["diff"], "")
        self.assertTrue(payload["summary_only"])
        reviewed_diff = "--- original\n+++ proposed\n@@ -1 +1 @@\n-a\n+b\n"
        self.assertEqual(
            payload["fingerprint"]["sha256"],
            hashlib.sha256(reviewed_diff.encode("utf-8")).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
