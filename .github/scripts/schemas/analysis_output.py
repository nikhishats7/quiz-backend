from __future__ import annotations
from pydantic import BaseModel, field_validator
from typing import Literal


class AnalysisOutput(BaseModel):
    """Structured output from Stage 1 — Analyze Agent."""

    problem_summary: str
    """Plain-language summary of what the issue is asking for."""

    affected_files: list[str]
    """Best-guess list of repo file paths that need changes.
    E.g. ["src/main/java/com/example/demo/service/QuizService.java"]
    """

    affected_areas: list[str]
    """High-level area labels, e.g. ["service", "controller", "model"]."""

    complexity: Literal["small", "medium", "large"]
    """Estimated implementation complexity."""

    is_scoped_enough: bool
    """False if the issue is too vague or broad to implement safely."""

    sensitive_paths_touched: list[str]
    """Any items from the configured sensitive_paths list that overlap with
    affected_files. Empty list if none."""

    escalation_reason: str | None = None
    """Human-readable reason for escalation, or null if no escalation needed."""

    @field_validator("affected_files", "affected_areas", "sensitive_paths_touched", mode="before")
    @classmethod
    def coerce_list(cls, v: object) -> list:
        if v is None:
            return []
        return v
