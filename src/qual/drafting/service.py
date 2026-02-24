from __future__ import annotations

import difflib
from dataclasses import dataclass


@dataclass(frozen=True)
class DiffOrchestration:
    before_text: str
    after_text: str
    before_lines: list[str]
    after_lines: list[str]


@dataclass(frozen=True)
class DiffSummary:
    changed: bool
    added_lines: int
    removed_lines: int
    net_line_delta: int
    total_changed_lines: int
    hunk_count: int
    changed_line_ratio: float
    line_coverage_ratio: float
    change_intensity: str


class DraftingService:
    """Draft revision scaffold service."""

    def propose_diff(self, original: str, proposed: str) -> str:
        orchestration = self.orchestrate_diff(original, proposed)
        if not self.has_meaningful_change(orchestration=orchestration):
            return ""
        return self._build_unified_diff(
            orchestration.before_lines,
            orchestration.after_lines,
        )

    def orchestrate_diff(self, original: str, proposed: str) -> DiffOrchestration:
        before_text = self._normalize_for_diff(original)
        after_text = self._normalize_for_diff(proposed)
        return DiffOrchestration(
            before_text=before_text,
            after_text=after_text,
            before_lines=before_text.splitlines(keepends=True),
            after_lines=after_text.splitlines(keepends=True),
        )

    def summarize_diff(self, original: str, proposed: str) -> DiffSummary:
        orchestration = self.orchestrate_diff(original, proposed)
        return self.summarize_orchestration(orchestration)

    def has_meaningful_change(
        self,
        *,
        original: str | None = None,
        proposed: str | None = None,
        orchestration: DiffOrchestration | None = None,
    ) -> bool:
        active = orchestration or self.orchestrate_diff(
            original=original or "",
            proposed=proposed or "",
        )
        return active.before_text != active.after_text

    def summarize_orchestration(self, orchestration: DiffOrchestration) -> DiffSummary:
        if not self.has_meaningful_change(orchestration=orchestration):
            return self._empty_summary()
        diff_text = self._build_unified_diff(
            orchestration.before_lines,
            orchestration.after_lines,
        )
        added, removed, hunk_count = self._parse_diff_metrics(diff_text)
        return self._summary_from_metrics(
            added_lines=added,
            removed_lines=removed,
            hunk_count=hunk_count,
            before_line_count=len(orchestration.before_lines),
            after_line_count=len(orchestration.after_lines),
        )

    @staticmethod
    def _build_unified_diff(before: list[str], after: list[str]) -> str:
        return "".join(difflib.unified_diff(before, after, fromfile="original", tofile="proposed"))

    @staticmethod
    def _parse_diff_metrics(diff_text: str) -> tuple[int, int, int]:
        added = 0
        removed = 0
        hunk_count = 0
        for line in diff_text.splitlines():
            if line.startswith("@@"):
                hunk_count += 1
                continue
            if line.startswith("+++") or line.startswith("---"):
                continue
            if line.startswith("+"):
                added += 1
            elif line.startswith("-"):
                removed += 1
        return added, removed, hunk_count

    @staticmethod
    def _empty_summary() -> DiffSummary:
        return DiffSummary(
            changed=False,
            added_lines=0,
            removed_lines=0,
            net_line_delta=0,
            total_changed_lines=0,
            hunk_count=0,
            changed_line_ratio=0.0,
            line_coverage_ratio=0.0,
            change_intensity="none",
        )

    @staticmethod
    def _summary_from_metrics(
        *,
        added_lines: int,
        removed_lines: int,
        hunk_count: int,
        before_line_count: int,
        after_line_count: int,
    ) -> DiffSummary:
        total_changed = added_lines + removed_lines
        baseline_lines = max(before_line_count, after_line_count)
        ratio = 0.0 if baseline_lines == 0 else total_changed / baseline_lines
        coverage_ratio = DraftingService._line_coverage_ratio(
            total_changed_lines=total_changed,
            before_line_count=before_line_count,
            after_line_count=after_line_count,
        )
        intensity = DraftingService._classify_change_intensity(ratio=ratio)
        return DiffSummary(
            changed=True,
            added_lines=added_lines,
            removed_lines=removed_lines,
            net_line_delta=added_lines - removed_lines,
            total_changed_lines=total_changed,
            hunk_count=hunk_count,
            changed_line_ratio=ratio,
            line_coverage_ratio=coverage_ratio,
            change_intensity=intensity,
        )

    @staticmethod
    def _classify_change_intensity(*, ratio: float) -> str:
        if ratio <= 0.25:
            return "low"
        if ratio <= 0.75:
            return "medium"
        return "high"

    @staticmethod
    def _line_coverage_ratio(
        *,
        total_changed_lines: int,
        before_line_count: int,
        after_line_count: int,
    ) -> float:
        total_lines = before_line_count + after_line_count
        if total_lines == 0:
            return 0.0
        return total_changed_lines / total_lines

    @staticmethod
    def _normalize_newlines(value: str) -> str:
        normalized = value.replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.replace("\u2028", "\n").replace("\u2029", "\n")
        return normalized.replace("\u0085", "\n")

    @classmethod
    def _normalize_for_diff(cls, value: str) -> str:
        normalized = cls._normalize_newlines(value)
        had_trailing_newline = normalized.endswith("\n")
        parts = normalized.split("\n")
        if had_trailing_newline:
            parts = parts[:-1]
        cleaned = [line[1:] if line.startswith("\ufeff") else line for line in parts]
        cleaned = [line.rstrip(" \t") for line in cleaned]
        result = "\n".join(cleaned)
        if result and not result.endswith("\n"):
            result += "\n"
        elif had_trailing_newline:
            result += "\n"
        return result
