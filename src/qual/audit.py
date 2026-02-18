from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class AuditEvent:
    name: str
    timestamp: str


class AuditLog:
    """Local audit sink. Stores only event name + timestamp."""

    def __init__(self, app_data_dir: Path) -> None:
        self._path = app_data_dir / "audit_events.jsonl"
        app_data_dir.mkdir(parents=True, exist_ok=True)

    def record(self, *, name: str, when: datetime | None = None) -> AuditEvent:
        instant = when if when is not None else datetime.now(UTC)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=UTC)
        event = AuditEvent(name=name, timestamp=instant.isoformat())
        line = json.dumps({"name": event.name, "timestamp": event.timestamp}, sort_keys=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")
        return event
