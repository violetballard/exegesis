from __future__ import annotations

import json
import os
import unittest
from contextlib import contextmanager

from src.qual.commands.diff_preview import (
    INCLUDE_FINGERPRINT_ENV,
    INCLUDE_SUMMARY_ENV,
    MAX_DIFF_OUTPUT_CHARS_ENV,
    OUTPUT_FORMAT_ENV,
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
            output = run_diff_preview(DiffPreviewInput("a\nold\n", "a\nnew\n"))

        payload = json.loads(output)
        self.assertIsNone(payload["fingerprint"])
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["labels"],
            {
                "applied": True,
                "original": "original",
                "proposed": "proposed",
            },
        )
        self.assertEqual(
            payload["summary"]["stats"],
            {"added": 1, "changed": 2, "hunks": 1, "net": 0, "removed": 1},
        )
        self.assertEqual(payload["summary"]["text"], "Diff summary: +1 -1 (hunks: 1)")
        self.assertIn("--- original", payload["diff"])

    def test_json_output_includes_fingerprint_when_flag_enabled(self) -> None:
        with _env(
            **{
                OUTPUT_FORMAT_ENV: "json",
                INCLUDE_FINGERPRINT_ENV: "1",
                INCLUDE_SUMMARY_ENV: "1",
            }
        ):
            output = run_diff_preview(DiffPreviewInput("a\nold\n", "a\nnew\n"))

        payload = json.loads(output)
        self.assertEqual(payload["fingerprint"]["algorithm"], "sha256")
        self.assertEqual(payload["fingerprint"]["char_count"], len(payload["diff"]))
        self.assertEqual(payload["fingerprint"]["line_count"], len(payload["diff"].splitlines()))
        self.assertTrue(payload["fingerprint"]["sha256"])


if __name__ == "__main__":
    unittest.main()
