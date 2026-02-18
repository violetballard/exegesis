from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from src.qual.audit import AuditLog
from src.qual.metrics.db import MetricsDB
from src.qual.metrics.exporter import (
    MetricsExportFlow,
    MetricsExportPlan,
    MetricsExporter,
    compute_diff_accept_rate,
)
from src.qual.metrics.recorder import MetricsRecorder
from src.qual.metrics.schema import (
    EXPORT_TOP_LEVEL_KEYS_WITHOUT_INSTALL_UUID,
    WEEKLY_COUNTER_FIELDS,
)


class MetricsModuleTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.db = MetricsDB(self.root)
        fixed_now = datetime(2026, 2, 18, 14, 0, tzinfo=UTC)
        self.recorder = MetricsRecorder(self.db, now_fn=lambda: fixed_now)
        self.exporter = MetricsExporter(self.db)
        self.audit = AuditLog(self.root)
        self.flow = MetricsExportFlow(self.exporter, self.audit, app_version="0.3.1")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_export_json_contains_only_allowed_keys(self) -> None:
        self.recorder.mark_writing_session_started()
        self.recorder.add_writing_minutes(9)
        summary = self.exporter.build_summary(
            app_version="0.3.1",
            os_major="macOS 14",
            include_cohort_code=False,
            include_install_uuid=False,
        )
        self.assertEqual(set(summary.keys()), set(EXPORT_TOP_LEVEL_KEYS_WITHOUT_INSTALL_UUID))

        week = summary["weeks"][0]
        expected_week = {"week_start", *WEEKLY_COUNTER_FIELDS, "diff_accept_rate"}
        self.assertEqual(set(week.keys()), expected_week)

        forbidden = {
            "doc_title",
            "file_path",
            "excerpt_text",
            "memo_text",
            "prompt",
            "citations",
            "citekey",
            "model_output",
            "user_text",
        }
        self.assertTrue(forbidden.isdisjoint(summary.keys()))
        self.assertTrue(forbidden.isdisjoint(week.keys()))

    def test_recorder_rejects_invalid_enums(self) -> None:
        with self.assertRaises(ValueError):
            self.recorder.context_item_pinned(kind="bad")
        with self.assertRaises(ValueError):
            self.recorder.agent_run_completed(kind="unknown")
        with self.assertRaises(ValueError):
            self.recorder.export_completed(format="txt")

    def test_writing_minutes_rounding(self) -> None:
        self.recorder.add_writing_minutes(1)
        self.recorder.add_writing_minutes(2)
        self.recorder.add_writing_minutes(3)
        self.recorder.add_writing_minutes(7)
        row = self.db.get_weeks()[0]
        # 1->0, 2->0, 3->5, 7->5 => total 10
        self.assertEqual(int(row["writing_minutes"]), 10)

    def test_diff_accept_rate_derived_and_not_stored(self) -> None:
        self.recorder.diff_decision(accepted=True)
        self.recorder.diff_decision(accepted=False)
        self.recorder.diff_decision(accepted=True)

        row = self.db.get_weeks()[0]
        self.assertNotIn("diff_accept_rate", row)
        self.assertEqual(int(row["diff_accept_count"]), 2)
        self.assertEqual(int(row["diff_reject_count"]), 1)
        self.assertEqual(compute_diff_accept_rate(diff_accept_count=2, diff_reject_count=1), 0.67)

        summary = self.exporter.build_summary(
            app_version="0.3.1",
            os_major="macOS 14",
            include_cohort_code=False,
            include_install_uuid=False,
        )
        self.assertEqual(summary["weeks"][0]["diff_accept_rate"], 0.67)

    def test_only_metrics_tables_exist_in_db(self) -> None:
        self.assertEqual(self.db.list_user_tables(), ["metrics_install", "metrics_weekly"])

    def test_export_output_is_deterministic_for_same_state(self) -> None:
        self.recorder.mark_writing_session_started()
        self.recorder.diff_decision(accepted=True)
        plan = MetricsExportPlan(
            include_cohort_code=False,
            include_install_uuid=False,
            include_csv=True,
        )
        preview_a = self.flow.preview(plan)
        preview_b = self.flow.preview(plan)
        self.assertEqual(preview_a, preview_b)

        json_path = self.root / "metrics-summary.json"
        csv_path = self.root / "metrics-summary.csv"
        self.flow.confirm_and_write(json_path=json_path, csv_path=csv_path, plan=plan)
        disk_json = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(disk_json, json.loads(preview_a))

    def test_analysis_pin_updates_total_only(self) -> None:
        self.recorder.context_item_pinned(kind="analysis")
        row = self.db.get_weeks()[0]
        self.assertEqual(int(row["context_items_pinned_total"]), 1)
        self.assertEqual(int(row["context_items_pinned_excerpt"]), 0)
        self.assertEqual(int(row["context_items_pinned_memo"]), 0)
        self.assertEqual(int(row["context_items_pinned_literature"]), 0)


if __name__ == "__main__":
    unittest.main()
