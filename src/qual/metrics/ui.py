from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.qual.metrics.db import MetricsDB
from src.qual.metrics.exporter import compute_diff_accept_rate
from src.qual.metrics.schema import WEEKLY_SUMMARY_FIELDS


@dataclass(frozen=True)
class UsageIntegrityScreen:
    last_four_weeks: list[dict[str, Any]]
    t_first_export_hours: int | None
    t_first_accept_hours: int | None
    cohort_code: str | None
    privacy_statement: str


class UsageIntegrityService:
    def __init__(self, db: MetricsDB) -> None:
        self._db = db

    def build_screen(self) -> UsageIntegrityScreen:
        rows = self._db.get_weeks(limit=4, descending=True)
        summary_rows: list[dict[str, Any]] = []
        for row in rows:
            summary = {
                "week_start": row["week_start"],
                "writing_sessions": int(row["writing_sessions"]),
                "writing_minutes": int(row["writing_minutes"]),
                "context_sets_created": int(row["context_sets_created"]),
                "context_items_pinned_total": int(row["context_items_pinned_total"]),
                "agent_runs_total": int(row["agent_runs_total"]),
                "diff_accept_rate": compute_diff_accept_rate(
                    diff_accept_count=int(row["diff_accept_count"]),
                    diff_reject_count=int(row["diff_reject_count"]),
                ),
                "exports_total": int(row["exports_total"]),
            }
            summary_rows.append(summary)
        install = self._db.get_install()
        return UsageIntegrityScreen(
            last_four_weeks=summary_rows,
            t_first_export_hours=install.t_first_export_hours,
            t_first_accept_hours=install.t_first_accept_hours,
            cohort_code=install.cohort_code,
            privacy_statement="Stored locally. Nothing is sent automatically.",
        )

    @staticmethod
    def allowed_screen_fields() -> tuple[str, ...]:
        return WEEKLY_SUMMARY_FIELDS
