from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc

@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    name: str
    timestamp: str
    metadata: dict[str, Any]


class AuditLog:
    """Local audit sink. Stores only event name + timestamp."""

    def __init__(self, app_data_dir: Path) -> None:
        self._path = app_data_dir / "audit_events.jsonl"
        app_data_dir.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        *,
        name: str,
        when: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if when is not None and not isinstance(when, datetime):
            raise TypeError("when must be a datetime or None")
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary or None")
        instant = when if when is not None else datetime.now(UTC)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=UTC)
        payload = metadata if metadata is not None else {}
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            name=name,
            timestamp=instant.isoformat(),
            metadata=payload,
        )
        line = json.dumps(
            {
                "event_id": event.event_id,
                "name": event.name,
                "timestamp": event.timestamp,
                "metadata": event.metadata,
            },
            sort_keys=True,
        )
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.write("\n")
        return event

    def read_events(self, *, name_filter: str | None = None) -> list[AuditEvent]:
        """Return persisted audit events in append order, optionally filtered by name."""
        if not self._path.exists():
            return []
        events: list[AuditEvent] = []
        for raw in self._path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            name = data.get("name", "")
            if name_filter is not None and name != name_filter:
                continue
            events.append(
                AuditEvent(
                    event_id=data.get("event_id", ""),
                    name=name,
                    timestamp=data.get("timestamp", ""),
                    metadata=data.get("metadata", {}),
                )
            )
        return events


__all__ = ["AuditEvent", "AuditLog"]
