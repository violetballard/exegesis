from __future__ import annotations

from typing import List, Optional

try:
    from typing import Literal, TypedDict
except ImportError:
    from typing_extensions import Literal, TypedDict  # type: ignore[assignment]


class ContextBasketOutcome(TypedDict):
    """Resolved context/basket action outcome from an engine-loop event sequence."""

    action_id: str
    status: str
    sequence: int


class EngineLoopOutcome(TypedDict):
    """Typed summary of an engine-loop event sequence.

    Returned by ``summarize_engine_loop_sequence_outcome``.
    Stable interface for CLI fallback and future Textual client consumers.

    ``status`` values:
    - ``"pending"`` – no events yet (empty sequence).
    - ``"waiting_for_action"`` – engine published a card and is awaiting user action.
    - ``"waiting_for_resolution"`` – an action is in-flight (selected but not resolved).
    - ``"complete"`` – terminal state; no action is in-flight and any patch is resolved.
    """

    run_id: Optional[str]
    patch_id: Optional[str]
    patch_outcome: Optional[str]
    inflight_action_id: Optional[str]
    event_count: int
    last_sequence: Optional[int]
    context_basket_outcomes: List[ContextBasketOutcome]
    status: Literal["pending", "waiting_for_action", "waiting_for_resolution", "complete"]
