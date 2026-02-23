from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.qual.webconsole.render.safe_html import escape_text, json_compact

_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


@dataclass(frozen=True)
class TerminalPageData:
    session_id: str
    stream_url: str
    send_url: str
    actions_url: str = "/api/actions/execute"
    csrf_token: str | None = None


@dataclass(frozen=True)
class SettingsPageData:
    effective_config: dict[str, Any]
    probe_report: dict[str, Any]
    probe_rerun_url: str = "/api/provider/probe"
    probe_report_url: str = "/api/provider/probe_report"
    csrf_token: str | None = None


def render_terminal_page(data: TerminalPageData) -> str:
    body = _render_template(
        "terminal.html",
        {
            "session_id": data.session_id,
            "stream_url": data.stream_url,
            "send_url": data.send_url,
            "actions_url": data.actions_url,
            "csrf_token": data.csrf_token or "",
        },
    )
    return _render_base("Terminal", body, csrf_token=data.csrf_token)


def render_provider_probe_panel(
    *,
    report: dict[str, Any],
    probe_rerun_url: str,
    probe_report_url: str,
) -> str:
    roles_available = report.get("roles_available")
    role_lines: list[str] = []
    if isinstance(roles_available, dict):
        for role, available in sorted(roles_available.items()):
            status = "available" if bool(available) else "missing"
            role_lines.append(f"<li><strong>{escape_text(role)}</strong>: {escape_text(status)}</li>")

    actions = report.get("recommended_actions")
    action_lines: list[str] = []
    if isinstance(actions, list):
        for action in actions:
            action_lines.append(f"<li>{escape_text(action)}</li>")

    return _render_template(
        "provider_probe_panel.html",
        {
            "provider_base_url": report.get("provider", {}).get("base_url", "<unknown>"),
            "timestamp": report.get("timestamp", "<unknown>"),
            "streaming": str(bool(report.get("streaming", False))).lower(),
            "tool_calling": str(report.get("tool_calling", "unknown")),
            "vision": str(bool(report.get("vision", False))).lower(),
            "role_lines": "\n".join(role_lines) or "<li>No role availability data.</li>",
            "action_lines": "\n".join(action_lines) or "<li>No recommended actions.</li>",
            "probe_rerun_url": probe_rerun_url,
            "probe_report_url": probe_report_url,
            "raw_report_json": json_compact(report),
        },
        raw_keys={"role_lines", "action_lines"},
    )


def render_settings_page(data: SettingsPageData) -> str:
    probe_panel = render_provider_probe_panel(
        report=data.probe_report,
        probe_rerun_url=data.probe_rerun_url,
        probe_report_url=data.probe_report_url,
    )
    body = _render_template(
        "settings.html",
        {
            "effective_config_json": json_compact(data.effective_config),
            "probe_panel_html": probe_panel,
            "csrf_token": data.csrf_token or "",
        },
        raw_keys={"probe_panel_html"},
    )
    return _render_base("Settings / Config", body, csrf_token=data.csrf_token)


def _render_base(title: str, body_html: str, *, csrf_token: str | None) -> str:
    return _render_template(
        "base.html",
        {
            "title": title,
            "content": body_html,
            "csrf_token": csrf_token or "",
        },
        raw_keys={"content"},
    )


def _render_template(
    template_name: str,
    context: dict[str, Any],
    *,
    raw_keys: set[str] | None = None,
) -> str:
    raw = (_TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    allowed_raw = raw_keys or set()
    rendered = raw
    for key, value in context.items():
        token = "{{" + key + "}}"
        replacement = str(value) if key in allowed_raw else escape_text(value)
        rendered = rendered.replace(token, replacement)
    return rendered
