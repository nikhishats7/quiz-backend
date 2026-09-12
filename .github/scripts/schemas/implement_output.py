from __future__ import annotations
from pydantic import BaseModel


class FileChange(BaseModel):
    """A single file written to the branch."""

    path: str
    """Relative path from repo root."""

    content: str
    """Full file content (UTF-8). We use full-file replacement, not patches,
    because Java class structure makes partial patches fragile."""


class ImplementOutput(BaseModel):
    """Structured output from Stage 3 — Implement Agent."""

    branch_name: str
    """Name of the branch the changes were committed to,
    e.g. "ai/implement-42"."""

    commit_sha: str
    """SHA of the commit that was pushed."""

    diff_summary: str
    """Plain-language description of what was changed."""

    files_changed: list[str]
    """Relative paths of all files that were created or modified."""

    deviations_from_plan: list[str]
    """Any meaningful ways the implementation deviated from the plan.
    Empty list if it followed the plan exactly. Must NOT be silently empty
    if deviations exist — this is an audit field."""

    diff_size_lines: int
    """Approximate total lines added + removed across all changed files."""
