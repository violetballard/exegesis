from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from exegesis_shared.models.engine_loop_outcome import EngineLoopOutcome


@dataclass(frozen=True)
class PatchReviewState:
    """Typed, engine-authoritative representation of in-progress patch review state.

    Encapsulates the state dict produced by ``advance_patch_review_state`` and
    consumed by ``validate_patch_review_execution_state``.  Callers may round-trip
    through ``as_dict`` / ``from_dict`` when crossing serialisation boundaries.
    """

    patch_id: str
    previewed: bool = False
    resolved: bool = False
    resolved_as: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.patch_id, str) or not self.patch_id.strip():
            raise ValueError("PatchReviewState.patch_id must be a non-empty string")
        if self.patch_id != self.patch_id.strip():
            raise ValueError("PatchReviewState.patch_id must be normalized")
        if not isinstance(self.previewed, bool):
            raise ValueError("PatchReviewState.previewed must be a bool")
        if not isinstance(self.resolved, bool):
            raise ValueError("PatchReviewState.resolved must be a bool")
        if self.resolved_as is not None and not isinstance(self.resolved_as, str):
            raise ValueError("PatchReviewState.resolved_as must be a string or None")
        if self.resolved and self.resolved_as not in {"apply", "reject"}:
            raise ValueError(
                "PatchReviewState.resolved_as must be 'apply' or 'reject' when resolved"
            )
        if self.resolved and not self.previewed:
            raise ValueError(
                "PatchReviewState cannot be resolved without previewed=True"
            )
        if not self.resolved and self.resolved_as is not None:
            raise ValueError(
                "PatchReviewState.resolved_as must be None when not resolved"
            )

    @classmethod
    def from_dict(cls, state: dict[str, Any]) -> PatchReviewState:
        """Construct from the dict produced by ``advance_patch_review_state``."""
        if not isinstance(state, dict):
            raise ValueError("Patch review state must be a dict")
        unexpected_keys = set(state) - {"patch_id", "previewed", "resolved", "resolved_as"}
        if unexpected_keys:
            field_list = ", ".join(sorted(unexpected_keys))
            raise ValueError(f"Unsupported PatchReviewState field(s): {field_list}")
        patch_id = state.get("patch_id")
        if not isinstance(patch_id, str):
            raise ValueError("Patch review state patch_id must be a string")
        previewed = state.get("previewed", False)
        if not isinstance(previewed, bool):
            raise ValueError("Patch review state previewed must be a bool")
        resolved = state.get("resolved", False)
        if not isinstance(resolved, bool):
            raise ValueError("Patch review state resolved must be a bool")
        resolved_as = state.get("resolved_as")
        if resolved_as is not None and not isinstance(resolved_as, str):
            raise ValueError("Patch review state resolved_as must be a string or None")
        return cls(
            patch_id=patch_id,
            previewed=previewed,
            resolved=resolved,
            resolved_as=resolved_as,
        )


    def as_dict(self) -> dict[str, Any]:
        """Return the state dict compatible with ``validate_patch_review_execution_state``."""
        result: dict[str, Any] = {
            "patch_id": self.patch_id,
            "previewed": self.previewed,
            "resolved": self.resolved,
        }
        if self.resolved_as is not None:
            result["resolved_as"] = self.resolved_as
        return result

    def is_pending(self) -> bool:
        """True when no control has been executed yet."""
        return not self.previewed and not self.resolved

    def is_previewed(self) -> bool:
        """True when preview has completed but no decision has been made."""
        return self.previewed and not self.resolved

    def is_resolved(self) -> bool:
        return self.resolved

    def is_applied(self) -> bool:
        """True when the patch review has resolved as applied."""
        return self.resolved and self.resolved_as == "apply"

    def is_rejected(self) -> bool:
        """True when the patch review has resolved as rejected."""
        return self.resolved and self.resolved_as == "reject"

    def resolved_control(self) -> str | None:
        return self.resolved_as

    def available_controls(self) -> tuple[str, ...]:
        """Return the controls the engine loop may offer next, in canonical order.

        Returns ``("preview",)`` when pending, ``("apply", "reject")`` when
        preview has completed but no decision has been made, and ``()`` when
        the review is already resolved.  The engine loop should use this instead
        of re-implementing the state machine locally.
        """
        if self.resolved:
            return ()
        if self.previewed:
            return ("apply", "reject")
        return ("preview",)

    def available_action_ids(self) -> tuple[str, ...]:
        """Return action IDs corresponding to ``available_controls()``, in canonical order.

        Convenience for engine-loop dispatch: avoids re-implementing the
        control → action_id mapping at every call site.
        """
        _map: dict[str, str] = {
            "preview": "preview_patch",
            "apply": "apply_patch",
            "reject": "reject_patch",
        }
        return tuple(_map[c] for c in self.available_controls())

    @property
    def patch_outcome(self) -> Literal["previewed", "applied", "rejected"] | None:
        """Return the patch outcome status corresponding to this state.

        Matches the `patch_outcome` field value of `EngineLoopOutcome`.
        Values:
        - ``None``          – pending (not previewed and not resolved)
        - ``"previewed"``   – previewed but not resolved
        - ``"applied"``     – resolved as apply
        - ``"rejected"``    – resolved as reject
        """
        if self.resolved:
            return "applied" if self.resolved_as == "apply" else "rejected"
        if self.previewed:
            return "previewed"
        return None

    @property
    def engine_status(self) -> Literal["pending", "waiting_for_action", "complete"]:
        """Return the engine-vocabulary status string for this state.

        Maps local boolean fields to the same status vocabulary used by
        ``EngineLoopOutcome["status"]`` so CLI and Textual clients can call
        ``state.engine_status`` instead of mapping booleans manually.

        Values:
        - ``"pending"``            – no action taken yet (awaiting preview)
        - ``"waiting_for_action"`` – previewed; awaiting apply or reject
        - ``"complete"``           – resolved (applied or rejected)

        Note: ``"waiting_for_resolution"`` (engine-loop in-flight state) is not
        representable here because ``PatchReviewState`` does not track inflight
        actions; use ``EngineLoopOutcome["status"]`` when that distinction matters.
        """
        if self.resolved:
            return "complete"
        if self.previewed:
            return "waiting_for_action"
        return "pending"

    def next_action_hints(self) -> list[dict[str, Any]]:
        """Return structured next-action hints for this state, in canonical order.

        Returns a list of ``{"action_id": str, "label": str}`` dicts compatible
        with ``action_ref_from_next_action_hint`` and
        ``engine_loop_outcome_next_action_hints``.  Callers that hold a typed
        ``PatchReviewState`` (e.g. after ``advance_patch_review_state_typed``) can
        produce hints directly without reconstructing an ``EngineLoopOutcome``.

        Returns ``[]`` when the review is already resolved.
        """
        _labels: dict[str, str] = {
            "preview_patch": "Preview",
            "apply_patch": "Apply",
            "reject_patch": "Reject",
        }
        return [{"action_id": aid, "label": _labels[aid]} for aid in self.available_action_ids()]

    def advance(self, control: str) -> "PatchReviewState":
        """Return a new PatchReviewState after executing *control* from this state.

        Delegates to ``advance_patch_review_state_typed`` so the engine loop
        can transition state without a separate import::

            state = state.advance("preview")
            state = state.advance("apply")

        Raises ``ValueError`` for unknown controls or a mismatched patch_id.
        Raises ``PermissionError`` when the transition is not allowed (e.g. apply
        before preview, or any control after the review is already resolved).
        """
        # Deferred to avoid circular import: models ← contracts.actions ← models.
        from exegesis_shared.contracts.actions import advance_patch_review_state_typed

        return advance_patch_review_state_typed(
            patch_id=self.patch_id,
            control=control,
            current_state=self,
        )

    def can_advance(self, control: str) -> bool:
        """Return True if the state can be transitioned using *control*.

        Accepts: "preview", "apply", "reject", or matching action IDs:
        "preview_patch", "apply_patch", "reject_patch".
        Does not raise exceptions. Returns False for unknown or invalid controls,
        or when preconditions are not met.
        """
        try:
            cleaned = str(control).strip().lower()
        except (ValueError, TypeError):
            return False
        _action_to_control = {
            "preview_patch": "preview",
            "apply_patch": "apply",
            "reject_patch": "reject",
        }
        cleaned = _action_to_control.get(cleaned, cleaned)
        return cleaned in self.available_controls()

    @classmethod
    def from_engine_loop_outcome(cls, outcome: "EngineLoopOutcome") -> "PatchReviewState | None":
        """Derive a PatchReviewState from a summarized EngineLoopOutcome.

        Returns None when the outcome contains no patch_id (e.g. a retrieval-only
        run).  Engine-runs polling loops should call this after
        ``summarize_engine_loop_sequence_outcome`` to get a typed state view
        without re-implementing the patch_outcome → state mapping locally.

        Raises ValueError if outcome.patch_id is set but patch_outcome is an
        unrecognised value (guards against contract drift between engine-runs and
        this shared model).
        """
        if not isinstance(outcome, dict):
            raise ValueError("outcome must be an EngineLoopOutcome dict")
        from exegesis_shared.contracts.events import validate_engine_loop_outcome
        validate_engine_loop_outcome(outcome)
        patch_id = outcome.get("patch_id")
        if patch_id is None:
            return None
        if not isinstance(patch_id, str) or not patch_id.strip():
            raise ValueError("outcome.patch_id must be a non-empty string when present")
        patch_outcome = outcome.get("patch_outcome")
        _VALID_OUTCOMES = {None, "previewed", "applied", "rejected"}
        if patch_outcome not in _VALID_OUTCOMES:
            raise ValueError(
                f"outcome.patch_outcome {patch_outcome!r} is not a recognised value; "
                f"expected one of {sorted(str(v) for v in _VALID_OUTCOMES if v is not None)!r} or None"
            )
        if patch_outcome == "applied":
            return cls(patch_id=patch_id, previewed=True, resolved=True, resolved_as="apply")
        if patch_outcome == "rejected":
            return cls(patch_id=patch_id, previewed=True, resolved=True, resolved_as="reject")
        if patch_outcome == "previewed":
            return cls(patch_id=patch_id, previewed=True, resolved=False)
        # patch_outcome is None: patch was published but no action resolved yet
        return cls(patch_id=patch_id, previewed=False, resolved=False)

    def validate_consistency_with_outcome(
        self, outcome: "EngineLoopOutcome | dict[str, Any]"
    ) -> None:
        """Assert that this state is consistent with an EngineLoopOutcome.

        Checks that both reference the same patch_id and that their resolution
        status agrees (e.g. outcome says "applied" → state must be resolved with
        resolved_as="apply").  Raises ValueError on any inconsistency so the
        engine loop can detect drift between the shared state machine and the
        summarized event sequence before presenting results to the CLI surface.

        Expected pairings:
        - ``patch_outcome=None``        → state may be pending or previewed
        - ``patch_outcome="previewed"`` → state.previewed must be True
        - ``patch_outcome="applied"``   → state.resolved must be True, resolved_as="apply"
        - ``patch_outcome="rejected"``  → state.resolved must be True, resolved_as="reject"
        """
        if not isinstance(outcome, dict):
            raise ValueError("outcome must be an EngineLoopOutcome dict")
        from exegesis_shared.contracts.events import validate_engine_loop_outcome
        validate_engine_loop_outcome(outcome)
        outcome_patch_id = outcome.get("patch_id")
        if outcome_patch_id is None:
            raise ValueError(
                "EngineLoopOutcome carries no patch_id; cannot validate consistency with PatchReviewState"
            )
        if not isinstance(outcome_patch_id, str) or not outcome_patch_id.strip():
            raise ValueError("EngineLoopOutcome.patch_id must be a non-empty string")
        if outcome_patch_id != outcome_patch_id.strip():
            raise ValueError("EngineLoopOutcome.patch_id must be normalized")
        if outcome_patch_id != self.patch_id:
            raise ValueError(
                f"patch_id mismatch: PatchReviewState has {self.patch_id!r} but "
                f"EngineLoopOutcome has {outcome_patch_id!r}"
            )
        patch_outcome = outcome.get("patch_outcome")
        expected_outcome = self.patch_outcome
        if patch_outcome == "applied":
            if expected_outcome != "applied":
                raise ValueError(
                    f"EngineLoopOutcome.patch_outcome is 'applied' but PatchReviewState is not "
                    f"resolved as 'apply' (resolved={self.resolved}, resolved_as={self.resolved_as!r})"
                )
        elif patch_outcome == "rejected":
            if expected_outcome != "rejected":
                raise ValueError(
                    f"EngineLoopOutcome.patch_outcome is 'rejected' but PatchReviewState is not "
                    f"resolved as 'reject' (resolved={self.resolved}, resolved_as={self.resolved_as!r})"
                )
        elif patch_outcome == "previewed":
            if expected_outcome != "previewed":
                raise ValueError(
                    f"EngineLoopOutcome.patch_outcome is 'previewed' but PatchReviewState.previewed is False"
                )
        elif patch_outcome is None:
            if expected_outcome is not None and self.resolved:
                raise ValueError(
                    f"EngineLoopOutcome.patch_outcome is None but PatchReviewState is already resolved "
                    f"(resolved_as={self.resolved_as!r}); outcome may be stale"
                )
        else:
            raise ValueError(
                f"EngineLoopOutcome.patch_outcome {patch_outcome!r} is not a recognised value"
            )
