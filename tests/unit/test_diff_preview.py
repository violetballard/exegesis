from __future__ import annotations

import json
import os
import unittest
from contextlib import contextmanager

from src.qual.commands.diff_preview import (
    INCLUDE_SUMMARY_ENV,
    MAX_DIFF_OUTPUT_CHARS_ENV,
    OUTPUT_FORMAT_ENV,
    ORIGINAL_LABEL_ENV,
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

    def test_custom_file_labels_are_sanitized_and_bounded(self) -> None:
        noisy_original = "--- \x1b[31m Original\tDocument \nName " + ("x" * 200)
        noisy_proposed = "+++ Proposed\x07Document"
        with _env(
            **{
                ORIGINAL_LABEL_ENV: noisy_original,
                PROPOSED_LABEL_ENV: noisy_proposed,
            }
        ):
            output = run_diff_preview(DiffPreviewInput("a\n", "b\n"))
        header_lines = output.splitlines()[:2]
        self.assertEqual(header_lines[0], f"--- {'Original Document Name ' + ('x' * 97)}")
        self.assertEqual(header_lines[1], "+++ Proposed Document")

    def test_blank_custom_file_labels_fall_back_to_defaults(self) -> None:
        with _env(**{ORIGINAL_LABEL_ENV: " \t ", PROPOSED_LABEL_ENV: "\n"}):
            output = run_diff_preview(DiffPreviewInput("a\n", "b\n"))
        self.assertTrue(output.startswith("--- original\n+++ proposed\n"))

    def test_summary_only_does_not_override_no_diff_messages(self) -> None:
        with _env(**{SUMMARY_ONLY_ENV: "1"}):
            both_empty = run_diff_preview(DiffPreviewInput("", ""))
            identical = run_diff_preview(DiffPreviewInput("same\n", "same\n"))
        self.assertEqual(both_empty, "No diff: both inputs are empty.")
        self.assertEqual(identical, "No diff: inputs are identical after normalization.")

    def test_json_output_reports_structured_diff_metadata(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_SUMMARY_ENV: "1",
                MAX_DIFF_OUTPUT_CHARS_ENV: "12",
                ORIGINAL_LABEL_ENV: "before.txt",
                PROPOSED_LABEL_ENV: "after.txt",
            }
        ):
            output = run_diff_preview(DiffPreviewInput("alpha\n", "beta\ngamma\n"))
        payload = json.loads(output)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["truncated"])
        self.assertFalse(payload["summary_only"])
        self.assertEqual(payload["labels"]["original"], "before.txt")
        self.assertEqual(payload["labels"]["proposed"], "after.txt")
        self.assertEqual(payload["summary"]["stats"], {"added": 2, "changed": 3, "hunks": 1, "net": 1, "removed": 1})
        self.assertIn("Diff summary: +2 -1 (hunks: 1)", payload["summary"]["text"])
        self.assertIn("truncation_strategy", payload["options"])

    def test_json_output_preserves_no_diff_status(self) -> None:
        with _env(**{OUTPUT_FORMAT_ENV: "json"}):
            both_empty = json.loads(run_diff_preview(DiffPreviewInput("", "")))
            identical = json.loads(run_diff_preview(DiffPreviewInput("same\n", "same\n")))
        self.assertEqual(both_empty["status"], "no_diff")
        self.assertEqual(both_empty["message"], "No diff: both inputs are empty.")
        self.assertEqual(identical["status"], "no_diff")
        self.assertEqual(identical["message"], "No diff: inputs are identical after normalization.")


if __name__ == "__main__":
    unittest.main()
