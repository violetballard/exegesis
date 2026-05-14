from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PatchProposal:
    patch_id: str
    target_document_id: str
    target_range: tuple[int, int]
    original_text: str
    proposed_text: str
    metadata: dict[str, Any] = field(default_factory=dict)
