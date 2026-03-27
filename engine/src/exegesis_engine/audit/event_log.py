from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


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


__all__ = ["AuditEvent", "AuditLog"]
