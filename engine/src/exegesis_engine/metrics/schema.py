from __future__ import annotations

WEEKLY_COUNTER_FIELDS: tuple[str, ...] = (
    "waw",
    "writing_sessions",
    "writing_minutes",
    "context_sets_created",
    "context_items_pinned_total",
    "context_items_pinned_excerpt",
    "context_items_pinned_memo",
    "context_items_pinned_literature",
    "agent_runs_total",
    "agent_runs_draft",
    "agent_runs_revise",
    "agent_runs_ask",
    "diff_proposals_count",
    "diff_accept_count",
    "diff_reject_count",
    "exports_total",
    "exports_docx",
    "exports_pdf",
    "exports_latex",
    "exports_md",
)

INSTALL_FIELDS: tuple[str, ...] = (
    "t_first_export_hours",
    "t_first_accept_hours",
    "cohort_code",
    "install_uuid",
    "include_install_uuid_default",
)

WEEKLY_SUMMARY_FIELDS: tuple[str, ...] = (
    "week_start",
    "writing_sessions",
    "writing_minutes",
    "context_sets_created",
    "context_items_pinned_total",
    "agent_runs_total",
    "diff_accept_rate",
    "exports_total",
)

EXPORT_TOP_LEVEL_KEYS_WITHOUT_INSTALL_UUID: tuple[str, ...] = (
    "schema_version",
    "app_version",
    "os_major",
    "cohort_code",
    "t_first_export_hours",
    "t_first_accept_hours",
    "weeks",
)

EXPORT_TOP_LEVEL_KEYS_WITH_INSTALL_UUID: tuple[str, ...] = (
    "schema_version",
    "app_version",
    "os_major",
    "cohort_code",
    "install_uuid",
    "t_first_export_hours",
    "t_first_accept_hours",
    "weeks",
)
