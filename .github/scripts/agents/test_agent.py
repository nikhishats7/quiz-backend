"""
test_agent.py — Stage 4: Trigger sandboxed Maven tests and parse results.

Action : Dispatch run_tests.yml on the AI branch; poll until complete.
Output : TestOutput (JSON)
"""

from __future__ import annotations
import os

from schemas.implement_output import ImplementOutput
from schemas.test_output import TestOutput
from utils.github_client import GitHubClient
from utils.logger import log_stage_start, log_stage_end
from utils.openai_client import call_llm

_SUMMARIZE_PROMPT = """
You are a Java test analyst. Given raw Maven test output, write a short
plain-language summary of:
1. Which tests failed and why (be specific about class + method names).
2. The root cause (e.g., NullPointerException, assertion mismatch, compilation error).
3. What the implement agent needs to fix.

Output valid JSON only:
{
  "failure_summary": "concise explanation in 3-5 sentences"
}
""".strip()


def run(
    gh: GitHubClient,
    implement_output: ImplementOutput,
    issue_number: int,
    orchestrator_repo: str,
    model: str,
    test_timeout_minutes: int = 15,
    attempt: int = 0,
) -> TestOutput:
    """
    Trigger the reusable run_tests.yml workflow on the AI branch,
    wait for completion, and return structured TestOutput.
    """
    branch = implement_output.branch_name
    owner, repo = orchestrator_repo.split("/")

    log_stage_start(
        stage="test",
        issue_number=issue_number,
        attempt=attempt,
        inputs={"branch": branch},
    )

    # 1. Dispatch run_tests.yml on the TARGET repo via workflow_call
    #    (run_tests.yml lives in the orchestrator repo and is called from there)
    run_id = gh.trigger_workflow(
        workflow_file="run_tests.yml",
        ref="main",  # run_tests.yml is in the orchestrator repo on main
        inputs={
            "branch_name": branch,
            "repo_owner": gh.owner,
            "repo_name": gh.repo,
        },
    )

    # 2. Poll for completion
    run_result = gh.wait_for_run(run_id, timeout_minutes=test_timeout_minutes)
    passed = run_result["conclusion"] == "success"

    # 3. Get artifact URL
    artifacts = gh.get_run_artifacts(run_id)
    log_url = ""
    raw_log_excerpt = ""
    for art in artifacts:
        if "test-logs" in art["name"]:
            log_url = art["archive_download_url"]
            break

    # 4. Parse counts from run outputs (exposed via run_tests.yml outputs)
    #    We fall back to 0 if outputs aren't available
    tests_run = 0
    tests_failed = 0
    try:
        jobs_resp = gh._session.get(
            f"https://api.github.com/repos/{gh.owner}/{gh.repo}/actions/runs/{run_id}/jobs",
            timeout=30,
        )
        if jobs_resp.ok:
            for job in jobs_resp.json().get("jobs", []):
                for step in job.get("steps", []):
                    if "Parse Surefire" in step.get("name", ""):
                        # Outputs aren't directly readable from API; rely on log artifact
                        pass
    except Exception:
        pass

    # 5. If tests failed, summarize with LLM
    failure_summary: str | None = None
    if not passed and raw_log_excerpt:
        try:
            summ = call_llm(
                stage="test_summarize",
                issue_number=issue_number,
                attempt=attempt,
                model=model,
                system_prompt=_SUMMARIZE_PROMPT,
                user_content=f"### Maven test output\n```\n{raw_log_excerpt}\n```",
                max_tokens=512,
            )
            failure_summary = summ.get("failure_summary", "Tests failed. See log for details.")
        except Exception:
            failure_summary = "Tests failed. See the linked artifact log for details."

    output = TestOutput(
        passed=passed,
        failure_summary=failure_summary,
        full_log_url=log_url or run_result.get("html_url", ""),
        tests_run=tests_run,
        tests_failed=tests_failed,
        raw_log_excerpt=raw_log_excerpt,
    )

    log_stage_end(
        stage="test",
        issue_number=issue_number,
        attempt=attempt,
        outputs=output.model_dump(),
    )

    return output
