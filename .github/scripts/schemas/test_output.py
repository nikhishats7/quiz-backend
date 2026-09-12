from __future__ import annotations
from pydantic import BaseModel


class TestOutput(BaseModel):
    """Structured output from Stage 4 — Test Agent."""

    passed: bool
    """True if all tests passed (mvn test exited 0)."""

    failure_summary: str | None = None
    """AI-generated plain-language summary of what failed and why.
    Null when passed=True."""

    full_log_url: str
    """URL to the uploaded GitHub Actions artifact containing the full
    Surefire/Maven logs."""

    tests_run: int
    """Total number of test methods executed."""

    tests_failed: int
    """Number of test methods that failed or errored."""

    raw_log_excerpt: str = ""
    """First 4000 characters of the raw test output log, for quick inline
    inspection by the implement agent on retry."""
