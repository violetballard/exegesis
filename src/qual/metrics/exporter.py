from __future__ import annotations

import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.qual.audit import AuditLog
from src.qual.metrics.db import MetricsDB
from src.qual.metrics.schema import (
    EXPORT_TOP_LEVEL_KEYS_WITH_INSTALL_UUID,
    EXPORT_TOP_LEVEL_KEYS_WITHOUT_INSTALL_UUID,
    WEEKLY_COUNTER_FIELDS,
)


def build_os_major() -> str:
    system = platform.system() or "UnknownOS"
    release = platform.release() or "0"
    major = release.split(".")[0]
    return f"{system} {major}"


def compute_diff_accept_rate(*, diff_accept_count: int, diff_reject_count: int) -> float:
    total = diff_accept_count + diff_reject_count
    if total <= 0:
        return 0.0
    return round(diff_accept_count / total, 2)


class MetricsExporter:
    def __init__(self, db: MetricsDB) -> None:
        self._db = db

    def build_summary(
        self,
        *,
        app_version: str,
        os_major: str,
        include_cohort_code: bool,
        include_install_uuid: bool,
    ) -> dict[str, Any]:
        install = self._db.get_install()
        weeks_rows = self._db.get_weeks()
        weeks: list[dict[str, Any]] = []
        for row in weeks_rows:
            week = {"week_start": row["week_start"]}
            for key in WEEKLY_COUNTER_FIELDS:
                week[key] = int(row[key])
            week["diff_accept_rate"] = compute_diff_accept_rate(
                diff_accept_count=int(row["diff_accept_count"]),
                diff_reject_count=int(row["diff_reject_count"]),
            )
            weeks.append(week)

        summary: dict[str, Any] = {
            "schema_version": "metrics_summary_v1",
            "app_version": app_version,
            "os_major": os_major,
            "cohort_code": install.cohort_code if include_cohort_code else None,
            "t_first_export_hours": install.t_first_export_hours,
            "t_first_accept_hours": install.t_first_accept_hours,
            "weeks": weeks,
        }
        if include_install_uuid:
            summary["install_uuid"] = install.install_uuid
        return summary

    @staticmethod
    def to_json(summary: dict[str, Any]) -> str:
        return json.dumps(summary, indent=2, ensure_ascii=True) + "\n"

    @staticmethod
    def to_csv(summary: dict[str, Any]) -> str:
        rows = list(summary.get("weeks", []))
        columns = ["week_start", *WEEKLY_COUNTER_FIELDS, "diff_accept_rate"]
        header = ",".join(columns)
        csv_lines = [header]
        for row in rows:
            values = [str(row.get(col, "")) for col in columns]
            csv_lines.append(",".join(values))
        return "\n".join(csv_lines) + "\n"


@dataclass(frozen=True)
class MetricsExportPlan:
    include_cohort_code: bool
    include_install_uuid: bool
    include_csv: bool


class MetricsExportFlow:
    def __init__(self, exporter: MetricsExporter, audit_log: AuditLog, *, app_version: str) -> None:
        self._exporter = exporter
        self._audit_log = audit_log
        self._app_version = app_version

    def preview(self, plan: MetricsExportPlan) -> str:
        summary = self._build_summary(plan)
        self._validate_summary_keys(summary, include_install_uuid=plan.include_install_uuid)
        return self._exporter.to_json(summary)

    def confirm_and_write(
        self,
        *,
        json_path: Path,
        plan: MetricsExportPlan,
        csv_path: Path | None = None,
    ) -> list[Path]:
        summary = self._build_summary(plan)
        self._validate_summary_keys(summary, include_install_uuid=plan.include_install_uuid)
        json_path.write_text(self._exporter.to_json(summary), encoding="utf-8")
        written = [json_path]
        if plan.include_csv and csv_path is not None:
            csv_path.write_text(self._exporter.to_csv(summary), encoding="utf-8")
            written.append(csv_path)
        self._audit_log.record(name="metrics_exported")
        return written

    def _build_summary(self, plan: MetricsExportPlan) -> dict[str, Any]:
        return self._exporter.build_summary(
            app_version=self._app_version,
            os_major=build_os_major(),
            include_cohort_code=plan.include_cohort_code,
            include_install_uuid=plan.include_install_uuid,
        )

    @staticmethod
    def _validate_summary_keys(summary: dict[str, Any], *, include_install_uuid: bool) -> None:
        allowed = (
            set(EXPORT_TOP_LEVEL_KEYS_WITH_INSTALL_UUID)
            if include_install_uuid
            else set(EXPORT_TOP_LEVEL_KEYS_WITHOUT_INSTALL_UUID)
        )
        keys = set(summary.keys())
        if keys != allowed:
            extra = sorted(keys - allowed)
            missing = sorted(allowed - keys)
            raise ValueError(f"invalid export keys extra={extra} missing={missing}")
