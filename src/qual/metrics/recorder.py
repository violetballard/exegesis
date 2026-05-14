from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Callable

from src.qual.metrics.db import MetricsDB

_PIN_KINDS = {"excerpt", "memo", "literature", "analysis"}
_AGENT_KINDS = {"draft", "revise", "ask"}
_EXPORT_FORMATS = {"docx", "pdf", "latex", "md"}


class MetricsRecorder:
    def __init__(self, db: MetricsDB, *, now_fn: Callable[[], datetime] | None = None) -> None:
        self._db = db
        self._now_fn = now_fn or (lambda: datetime.now(UTC))

    def mark_writing_session_started(self) -> None:
        self._inc_week({"writing_sessions": 1}, set_waw=True)

    def add_writing_minutes(self, minutes_active: int) -> None:
        if not isinstance(minutes_active, int) or minutes_active < 0:
            raise ValueError("minutes_active must be a non-negative integer")
        rounded = _round_to_nearest_five(minutes_active)
        self._inc_week({"writing_minutes": rounded})

    def context_set_created(self) -> None:
        self._inc_week({"context_sets_created": 1})

    def context_item_pinned(self, *, kind: str) -> None:
        if kind not in _PIN_KINDS:
            raise ValueError("kind must be one of: excerpt, memo, literature, analysis")
        increments = {"context_items_pinned_total": 1}
        if kind == "excerpt":
            increments["context_items_pinned_excerpt"] = 1
        elif kind == "memo":
            increments["context_items_pinned_memo"] = 1
        elif kind == "literature":
            increments["context_items_pinned_literature"] = 1
        self._inc_week(increments)

    def agent_run_completed(self, *, kind: str) -> None:
        if kind not in _AGENT_KINDS:
            raise ValueError("kind must be one of: draft, revise, ask")
        self._inc_week(
            {
                "agent_runs_total": 1,
                f"agent_runs_{kind}": 1,
            }
        )

    def diff_proposal_created(self) -> None:
        self._inc_week({"diff_proposals_count": 1})

    def diff_decision(self, *, accepted: bool) -> None:
        field = "diff_accept_count" if accepted else "diff_reject_count"
        self._inc_week({field: 1})

    def export_completed(self, *, format: str) -> None:
        if format not in _EXPORT_FORMATS:
            raise ValueError("format must be one of: docx, pdf, latex, md")
        self._inc_week(
            {
                "exports_total": 1,
                f"exports_{format}": 1,
            }
        )

    def set_first_export_now_if_unset(self) -> None:
        self._db.set_first_export_hours_if_unset(self._db.hours_since_install(now=self._now()))

    def set_first_accept_now_if_unset(self) -> None:
        self._db.set_first_accept_hours_if_unset(self._db.hours_since_install(now=self._now()))

    def _inc_week(self, increments: dict[str, int], *, set_waw: bool = False) -> None:
        week_start = _week_start(self._now().date())
        self._db.increment_week(week_start=week_start.isoformat(), increments=increments, set_waw=set_waw)

    def _now(self) -> datetime:
        now = self._now_fn()
        if now.tzinfo is None:
            return now.replace(tzinfo=UTC)
        return now.astimezone(UTC)


def _week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def _round_to_nearest_five(value: int) -> int:
    return ((value + 2) // 5) * 5
