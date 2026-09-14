"""
github_client.py — Thin wrapper around the GitHub REST API.

All methods raise requests.HTTPError on non-2xx responses.
The token used here is the short-lived GitHub App installation token
(never a personal token or repo secret).
"""

from __future__ import annotations
import base64
import time
from typing import Any

import requests

BASE = "https://api.github.com"
TIMEOUT = 30


class GitHubClient:
    def __init__(self, token: str, owner: str, repo: str) -> None:
        self.token = token
        self.owner = owner
        self.repo = repo
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    # ── Issue helpers ─────────────────────────────────────────────────────────

    def get_issue(self, issue_number: int) -> dict:
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/issues/{issue_number}",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def get_issue_comments(self, issue_number: int) -> list[dict]:
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments",
            params={"per_page": 100},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    def post_issue_comment(self, issue_number: int, body: str) -> dict:
        r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments",
            json={"body": body},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    # ── File / tree helpers ───────────────────────────────────────────────────

    def get_file_content(self, path: str, ref: str = "main") -> str:
        """Return decoded UTF-8 content of a file at the given ref."""
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/contents/{path}",
            params={"ref": ref},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")

    def get_tree(self, ref: str = "main") -> list[dict]:
        """Return the recursive file tree for the repo at the given ref."""
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/trees/{ref}",
            params={"recursive": "1"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json().get("tree", [])

    def get_readme(self, ref: str = "main") -> str:
        try:
            return self.get_file_content("README.md", ref=ref)
        except requests.HTTPError:
            return ""

    # ── Branch helpers ────────────────────────────────────────────────────────

    def get_default_branch_sha(self) -> str:
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/ref/heads/main",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()["object"]["sha"]

    def create_branch(self, branch_name: str, from_sha: str) -> None:
        r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/refs",
            json={"ref": f"refs/heads/{branch_name}", "sha": from_sha},
            timeout=TIMEOUT,
        )
        # 422 = branch already exists — acceptable on retry
        if r.status_code not in (201, 422):
            r.raise_for_status()

    def commit_files(
        self,
        branch_name: str,
        files: list[dict],  # [{"path": ..., "content": ...}]
        commit_message: str,
    ) -> str:
        """
        Create a commit with the given files on branch_name.
        Uses the low-level Git Data API (blob → tree → commit → ref update).
        Returns the new commit SHA.
        """
        # 1. Get current commit SHA for the branch
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/ref/heads/{branch_name}",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        base_commit_sha = r.json()["object"]["sha"]

        # 2. Get base tree SHA
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/commits/{base_commit_sha}",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        base_tree_sha = r.json()["tree"]["sha"]

        # 3. Create blobs for each file
        tree_entries = []
        for f in files:
            blob_r = self._session.post(
                f"{BASE}/repos/{self.owner}/{self.repo}/git/blobs",
                json={
                    "content": base64.b64encode(f["content"].encode()).decode(),
                    "encoding": "base64",
                },
                timeout=TIMEOUT,
            )
            blob_r.raise_for_status()
            tree_entries.append(
                {
                    "path": f["path"],
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_r.json()["sha"],
                }
            )

        # 4. Create tree
        tree_r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/trees",
            json={"base_tree": base_tree_sha, "tree": tree_entries},
            timeout=TIMEOUT,
        )
        tree_r.raise_for_status()
        new_tree_sha = tree_r.json()["sha"]

        # 5. Create commit
        commit_r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/commits",
            json={
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [base_commit_sha],
            },
            timeout=TIMEOUT,
        )
        commit_r.raise_for_status()
        new_commit_sha = commit_r.json()["sha"]

        # 6. Update branch ref
        ref_r = self._session.patch(
            f"{BASE}/repos/{self.owner}/{self.repo}/git/refs/heads/{branch_name}",
            json={"sha": new_commit_sha},
            timeout=TIMEOUT,
        )
        ref_r.raise_for_status()
        return new_commit_sha

    # ── PR helpers ────────────────────────────────────────────────────────────

    def create_draft_pr(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
    ) -> dict:
        r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/pulls",
            json={
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch,
                "draft": True,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    
    def update_pr_body(
            self, pr_number: int, 
            body: str
        ) -> dict:
            r = self._session.patch(
                f"{BASE}/repos/{self.owner}/{self.repo}/pulls/{pr_number}",
                json={"body": body},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
    
    def get_open_pr_for_branch(self, branch: str) -> dict | None:
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/pulls",
            params={"head": f"{self.owner}:{branch}", "state": "open"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        prs = r.json()
        return prs[0] if prs else None
    
    def ensure_label(self, label_name: str, color: str = "0075ca") -> None:
        """Create label if it doesn't exist."""
        r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/labels",
            json={"name": label_name, "color": color},
            timeout=TIMEOUT,
        )
        if r.status_code not in (201, 422):  # 422 = already exists
            r.raise_for_status()

    def add_labels_to_pr(self, pr_number: int, labels: list[str]) -> None:
        r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/issues/{pr_number}/labels",
            json={"labels": labels},
            timeout=TIMEOUT,
        )
        r.raise_for_status()

    def request_pr_reviewers(self, pr_number: int, teams: list[str]) -> None:
        # Strip "@org/" prefix if present; GitHub API wants just the slug
        clean_teams = [t.lstrip("@").split("/")[-1] for t in teams]
        r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/requested_reviewers",
            json={"team_reviewers": clean_teams},
            timeout=TIMEOUT,
        )
        # Ignore 422 — team may not have access, log and continue
        if r.status_code == 422:
            print(f"[WARN] Could not request team review: {r.text}")
        else:
            r.raise_for_status()

    # ── Workflow helpers ──────────────────────────────────────────────────────

    def trigger_workflow(
        self,
        workflow_file: str,
        ref: str,
        inputs: dict[str, str],
    ) -> int:
        """
        Dispatch a workflow and return the new run ID.
        Polls the runs list to find the run that just started.
        """
        before = self._latest_run_id(workflow_file)

        r = self._session.post(
            f"{BASE}/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_file}/dispatches",
            json={"ref": ref, "inputs": inputs},
            timeout=TIMEOUT,
        )
        r.raise_for_status()

        # Poll until a new run appears (up to 30s)
        for _ in range(15):
            time.sleep(2)
            run_id = self._latest_run_id(workflow_file)
            if run_id != before:
                return run_id
        raise TimeoutError("Timed out waiting for workflow run to start.")

    def _latest_run_id(self, workflow_file: str) -> int | None:
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_file}/runs",
            params={"per_page": 1},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        runs = r.json().get("workflow_runs", [])
        return runs[0]["id"] if runs else None

    def wait_for_run(self, run_id: int, timeout_minutes: int = 15) -> dict:
        """Poll a workflow run until it completes. Returns the run dict."""
        deadline = time.time() + timeout_minutes * 60
        while time.time() < deadline:
            r = self._session.get(
                f"{BASE}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}",
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            run = r.json()
            if run["status"] == "completed":
                return run
            time.sleep(20)
        raise TimeoutError(f"Workflow run {run_id} did not complete within {timeout_minutes}m")

    def get_run_artifacts(self, run_id: int) -> list[dict]:
        r = self._session.get(
            f"{BASE}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/artifacts",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json().get("artifacts", [])
