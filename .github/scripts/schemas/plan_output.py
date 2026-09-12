from __future__ import annotations
from pydantic import BaseModel
from typing import Literal


class PlanStep(BaseModel):
    """A single atomic change step in the implementation plan."""

    file: str
    """Relative path from repo root, e.g. src/main/java/com/example/demo/service/QuizService.java"""

    action: Literal["create", "modify", "delete"]
    """What to do to this file."""

    description: str
    """Concise human-readable description of the change."""


class PlanOutput(BaseModel):
    """Structured output from Stage 2 — Plan Agent."""

    steps: list[PlanStep]
    """Ordered list of atomic file changes. Prefer the smallest correct change."""

    tests_to_write: list[str]
    """File paths for new or modified test files, e.g.
    ["src/test/java/com/example/demo/QuizServiceTest.java"]
    """

    edge_cases: list[str]
    """Edge cases the implementation must handle, e.g.
    ["empty question list", "null category"]
    """

    plan_narrative: str
    """Prose explanation of the overall approach — what changes and why."""
