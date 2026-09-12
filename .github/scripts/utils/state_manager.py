"""
state_manager.py — Read/write pipeline run state via a hidden issue comment.

State is stored as a JSON blob in a GitHub issue comment whose body starts
with the sentinel marker <!-- ai-run-state -->.

Schema:
{
  "comment_id": 123456,        # GitHub comment ID (set on first write)
  "state": "analyzing",        # current pipeline state
  "attempt": 1,                # implement→test retry count (resets on human retry)
  "round": 0,                  # number of human /retry rounds
  "stage_outputs": {
    "analysis": {...},
    "plan": {...},
    "implement": {...},
    "test": {...}
  },
  "branch_name": "ai/implement-42",
  "pr_number": null,
  "created_at": "...",
  "updated_at": "..."
}
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any

import requests

SENTINEL = "<!-- ai-run-state -->"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


# ── Read ──────────────────────────────────────────────────────────────────────

def load_state(
    token: str,
    owner: str,
    repo: str,
    issue_number: int,
) -> dict[str, Any]:
    """
    Return the current run state dict, or a fresh default if none exists yet.
    """
    comment = _find_state_comment(token, owner, repo, issue_number)
    if comment is None:
        return _default_state()

    body: str = comment["body"]
    json_part = body[len(SENTINEL):].strip()
    try:
        data = json.loads(json_part)
        data["comment_id"] = comment["id"]
        return data
    except json.JSONDecodeError:
        return _default_state()


def _default_state() -> dict[str, Any]:
    return {
        "comment_id": None,
        "state": "init",
        "attempt": 0,
        "round": 0,
        "stage_outputs": {},
        "branch_name": None,
        "pr_number": None,
        "created_at": _now(),
        "updated_at": _now(),
    }


def _find_state_comment(
    token: str,
    owner: str,
    repo: str,
    issue_number: int,
) -> dict | None:
    """Scan issue comments for the sentinel marker."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    params = {"per_page": 100}
    resp = requests.get(url, headers=_headers(token), params=params, timeout=30)
    resp.raise_for_status()
    for comment in resp.json():
        if comment["body"].startswith(SENTINEL):
            return comment
    return None


# ── Write ─────────────────────────────────────────────────────────────────────

def save_state(
    token: str,
    owner: str,
    repo: str,
    issue_number: int,
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Persist state. Creates the hidden comment on first call; edits it on subsequent calls.
    Returns the updated state dict (with comment_id populated).
    """
    state["updated_at"] = _now()
    body = SENTINEL + "\n" + json.dumps(state, indent=2)

    comment_id = state.get("comment_id")

    if comment_id:
        # Edit existing comment
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}"
        resp = requests.patch(url, headers=_headers(token), json={"body": body}, timeout=30)
        resp.raise_for_status()
    else:
        # Create new hidden comment
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
        resp = requests.post(url, headers=_headers(token), json={"body": body}, timeout=30)
        resp.raise_for_status()
        state["comment_id"] = resp.json()["id"]
        # Minimise the comment so it doesn't clutter the issue thread
        _minimize_comment(token, resp.json()["node_id"])

    return state


def _minimize_comment(token: str, node_id: str) -> None:
    """Collapse the state comment using the GraphQL API (cosmetic only)."""
    query = """
    mutation MinimizeComment($id: ID!) {
      minimizeComment(input: {subjectId: $id, classifier: OFF_TOPIC}) {
        minimizedComment { isMinimized }
      }
    }
    """
    try:
        requests.post(
            "https://api.github.com/graphql",
            headers=_headers(token),
            json={"query": query, "variables": {"id": node_id}},
            timeout=30,
        )
    except Exception:
        pass  # Minimization is cosmetic; don't fail the pipeline over it


# ── Convenience helpers ───────────────────────────────────────────────────────

def transition(state: dict, new_state: str) -> dict:
    """Update state field and return the dict (does not persist)."""
    state["state"] = new_state
    return state


def set_stage_output(state: dict, stage: str, output: Any) -> dict:
    """Store a stage's output in the state dict (does not persist)."""
    if "stage_outputs" not in state:
        state["stage_outputs"] = {}
    state["stage_outputs"][stage] = output
    return state
