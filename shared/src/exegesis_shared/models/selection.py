from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from exegesis_shared.types.object_types import OBJECT_TYPES


@dataclass(frozen=True)
class Selection:
    type: str
    id: str
    source_pane: str
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.type, str):
            raise ValueError("Selection.type must be a string")
        if self.type not in OBJECT_TYPES:
            raise ValueError(
                f"Selection.type must be one of {OBJECT_TYPES!r}, got {self.type!r}"
            )
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Selection.id must be a non-empty string")
        if self.id != self.id.strip():
            raise ValueError("Selection.id must be normalized")
        if not isinstance(self.source_pane, str) or not self.source_pane.strip():
            raise ValueError("Selection.source_pane must be a non-empty string")
        if self.source_pane != self.source_pane.strip():
            raise ValueError("Selection.source_pane must be normalized")
        if not isinstance(self.payload, dict):
            raise ValueError("Selection.payload must be a dict")
        from copy import deepcopy
        object.__setattr__(self, "payload", deepcopy(self.payload))
        for key in self.payload:
            if not isinstance(key, str):
                raise ValueError("Selection.payload keys must be strings")
            if not key.strip():
                raise ValueError("Selection.payload keys must be non-empty strings")
            if key != key.strip():
                raise ValueError("Selection.payload keys must be normalized")
        if "query" in self.payload:
            val = self.payload["query"]
            if not isinstance(val, str) or not val.strip():
                raise ValueError("Selection.payload query must be a non-empty string")
            if val != val.strip():
                raise ValueError("Selection.payload query must be normalized")
        if "reason" in self.payload:
            val = self.payload["reason"]
            if not isinstance(val, str) or not val.strip():
                raise ValueError("Selection.payload reason must be a non-empty string")
            if val != val.strip():
                raise ValueError("Selection.payload reason must be normalized")
        if "action_id" in self.payload:
            val = self.payload["action_id"]
            if not isinstance(val, str) or not val.strip():
                raise ValueError("Selection.payload action_id must be a non-empty string")
            if val != val.strip():
                raise ValueError("Selection.payload action_id must be normalized")
        for field_name in (
            "title",
            "description",
            "path",
            "filepath",
            "file_path",
            "message",
            "role",
            "option",
            "value",
            "source_ref",
            "patch_outcome",
            "resolved_as",
            "control",
            "run_id",
            "session_id",
            "client_name",
        ):
            if field_name in self.payload:
                val = self.payload[field_name]
                if not isinstance(val, str) or not val.strip():
                    raise ValueError(
                        f"Selection.payload {field_name} must be a non-empty string"
                    )
                if val != val.strip():
                    raise ValueError(
                        f"Selection.payload {field_name} must be normalized"
                    )

    def as_dict(self) -> dict[str, Any]:
        """Return the dictionary representation of this selection."""
        from copy import deepcopy
        return {
            "type": self.type,
            "id": self.id,
            "source_pane": self.source_pane,
            "payload": deepcopy(self.payload),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Selection:
        """Construct a Selection from a dictionary representation."""
        if not isinstance(data, dict):
            raise ValueError("Selection data must be a dict")
        unexpected_keys = set(data) - {"type", "id", "source_pane", "payload"}
        if unexpected_keys:
            field_list = ", ".join(sorted(unexpected_keys))
            raise ValueError(f"Unsupported Selection field(s): {field_list}")
        for key in ("type", "id", "source_pane"):
            if key not in data:
                raise ValueError(f"Selection data missing required key: {key}")
            if not isinstance(data[key], str):
                raise ValueError(f"Selection.{key} must be a string")
        payload = data.get("payload")
        if payload is not None and not isinstance(payload, dict):
            raise ValueError("Selection.payload must be a dict")
        return cls(
            type=data["type"],
            id=data["id"],
            source_pane=data["source_pane"],
            payload=payload if payload is not None else {},
        )

