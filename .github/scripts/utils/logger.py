"""
logger.py — Structured JSON audit logger.

Every agent call logs:
  - stage name
  - issue number
  - attempt number
  - truncated input (first 500 chars)
  - truncated output (first 500 chars)
  - model used
  - token counts

Output goes to stdout → captured verbatim by GitHub Actions logs,
which are retained for 90 days by default.
"""

from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truncate(value: Any, limit: int = 500) -> str:
    s = json.dumps(value) if not isinstance(value, str) else value
    if len(s) > limit:
        return s[:limit] + "…[truncated]"
    return s


def log_stage_start(
    stage: str,
    issue_number: int,
    attempt: int,
    inputs: dict[str, Any],
) -> None:
    record = {
        "ts": _now(),
        "event": "stage_start",
        "stage": stage,
        "issue": issue_number,
        "attempt": attempt,
        "inputs_preview": {k: _truncate(v) for k, v in inputs.items()},
    }
    print(json.dumps(record), flush=True)


def log_stage_end(
    stage: str,
    issue_number: int,
    attempt: int,
    outputs: dict[str, Any],
    model: str = "",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
) -> None:
    record = {
        "ts": _now(),
        "event": "stage_end",
        "stage": stage,
        "issue": issue_number,
        "attempt": attempt,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "outputs_preview": {k: _truncate(v) for k, v in outputs.items()},
    }
    print(json.dumps(record), flush=True)


def log_escalation(
    issue_number: int,
    stage: str,
    reason: str,
) -> None:
    record = {
        "ts": _now(),
        "event": "escalation",
        "stage": stage,
        "issue": issue_number,
        "reason": reason,
    }
    print(json.dumps(record), file=sys.stderr, flush=True)


def log_error(
    issue_number: int,
    stage: str,
    error: str,
) -> None:
    record = {
        "ts": _now(),
        "event": "error",
        "stage": stage,
        "issue": issue_number,
        "error": error,
    }
    print(json.dumps(record), file=sys.stderr, flush=True)


def log_state_transition(
    issue_number: int,
    from_state: str,
    to_state: str,
) -> None:
    record = {
        "ts": _now(),
        "event": "state_transition",
        "issue": issue_number,
        "from": from_state,
        "to": to_state,
    }
    print(json.dumps(record), flush=True)
