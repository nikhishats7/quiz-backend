"""
orchestrator.py — The sequential state machine.

States:
  init → analyzing → planning → implementing → testing → pr_open → done
                                     ↑__________________|  (retry loop)
                                                              ↓ (cap exceeded)
                                                         failed / escalated

Entry points:
  - TRIGGER=labeled  : start fresh from "analyzing"
  - TRIGGER=retry    : re-enter at "implementing" (resets attempt counter)
"""

from __future__ import annotations
import os
import sys
import textwrap
import traceback

import yaml

# Add scripts dir to path so relative imports work
sys.path.insert(0, os.path.dirname(__file__))

from agents import analyze_agent, plan_agent, implement_agent, test_agent, pr_agent
from schemas.analysis_output import AnalysisOutput
from schemas.implement_output import ImplementOutput
from schemas.plan_output import PlanOutput
from schemas.test_output import TestOutput
from utils.github_client import GitHubClient
from utils.logger import log_error, log_escalation, log_state_transition
from utils.state_manager import load_state, save_state, set_stage_output, transition


# ── Config loading ─────────────────────────────────────────────────────────────

def load_config() -> dict:
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "config", "pipeline_config.yml"
    )
    with open(config_path) as f:
        return yaml.safe_load(f)


# ── Environment ────────────────────────────────────────────────────────────────

TOKEN           = os.environ["GITHUB_TOKEN"]
GEMINI_API_KEY  = os.environ["GEMINI_API_KEY"]   # consumed by openai library directly
ISSUE_NUMBER    = int(os.environ["ISSUE_NUMBER"])
ISSUE_TITLE     = os.environ.get("ISSUE_TITLE", "")
ISSUE_BODY      = os.environ.get("ISSUE_BODY", "")
TRIGGER         = os.environ.get("TRIGGER", "labeled")   # "labeled" | "retry"
RETRY_COMMENT   = os.environ.get("RETRY_COMMENT", "")
REPO_OWNER      = os.environ["REPO_OWNER"]
REPO_NAME       = os.environ["REPO_NAME"]
ORCHESTRATOR_REPO = os.environ.get("ORCHESTRATOR_REPO", f"{REPO_OWNER}/{REPO_NAME}")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _escalate(gh: GitHubClient, state: dict, reason: str, label: str = "escalated") -> None:
    """Post an escalation comment and mark the run as escalated/failed."""
    comment = textwrap.dedent(f"""
    🚫 **AI Pipeline {label.capitalize()}**

    The automated implementation pipeline has stopped for this issue.

    **Reason:** {reason}

    A human engineer should review this issue and implement it manually,
    or clarify the requirements so the pipeline can retry.
    """).strip()
    gh.post_issue_comment(ISSUE_NUMBER, comment)
    log_escalation(ISSUE_NUMBER, state["state"], reason)
    state = transition(state, label)
    save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)


def _fail(gh: GitHubClient, state: dict, reason: str) -> None:
    _escalate(gh, state, reason, label="failed")


def _post_progress(gh: GitHubClient, stage: str) -> None:
    """Minimally notify the issue that the pipeline is still running."""
    stage_labels = {
        "analyzing":    "🔍 Analyzing the issue…",
        "planning":     "📋 Drafting an implementation plan…",
        "implementing": "⚙️ Writing code…",
        "testing":      "🧪 Running tests…",
        "pr_open":      "🔗 Opening a draft PR…",
    }
    label = stage_labels.get(stage, f"Running stage: {stage}")
    # Only post on first entry (attempt 0) to avoid comment spam
    # (progress updates are visible in Actions logs)
    pass


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    cfg = load_config()
    retry_cap: int          = cfg.get("retry_cap", 3)
    diff_threshold: int     = cfg.get("diff_size_threshold_lines", 500)
    sensitive_paths: list   = cfg.get("sensitive_paths", [])
    senior_reviewer: str    = cfg.get("senior_reviewer", "")
    model: str              = cfg.get("openai_model", "gpt-4o")
    test_timeout: int       = cfg.get("test_timeout_minutes", 15)

    gh = GitHubClient(TOKEN, REPO_OWNER, REPO_NAME)

    # ── Load existing run state ────────────────────────────────────────────────
    state = load_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER)

    # ── Handle triggers ────────────────────────────────────────────────────────
    if TRIGGER == "labeled":
        if state["state"] not in ("init", "failed", "escalated"):
            # Pipeline already running — ignore duplicate label event
            print(f"[INFO] Pipeline already in state '{state['state']}'. Ignoring duplicate label.")
            return
        state = transition(state, "analyzing")
        state["attempt"] = 0
        state["round"] = 0
        state["created_at"] = state.get("created_at", "")

    elif TRIGGER == "retry":
        if state["state"] not in ("pr_open", "done", "failed"):
            print(f"[INFO] /retry received but state is '{state['state']}'. Ignoring.")
            return
        state["attempt"] = 0          # Reset attempt counter for new human-review round
        state["round"] = state.get("round", 0) + 1
        state["retry_comment"] = RETRY_COMMENT
        state = transition(state, "implementing")

    else:
        print(f"[WARN] Unknown trigger: {TRIGGER}")
        return

    save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)

    # ── Stage machine ──────────────────────────────────────────────────────────
    try:
        # ── STAGE 1: Analyze ──────────────────────────────────────────────────
        if state["state"] == "analyzing":
            log_state_transition(ISSUE_NUMBER, "init", "analyzing")
            analysis = analyze_agent.run(
                gh=gh,
                issue_number=ISSUE_NUMBER,
                issue_title=ISSUE_TITLE,
                issue_body=ISSUE_BODY,
                model=model,
                sensitive_paths=sensitive_paths,
                attempt=state["attempt"],
            )

            if analysis.escalation_reason:
                _escalate(gh, state, analysis.escalation_reason)
                return

            state = set_stage_output(state, "analysis", analysis.model_dump())
            state = transition(state, "planning")
            save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)

        # ── STAGE 2: Plan ─────────────────────────────────────────────────────
        if state["state"] == "planning":
            log_state_transition(ISSUE_NUMBER, "analyzing", "planning")
            analysis = AnalysisOutput(**state["stage_outputs"]["analysis"])
            plan = plan_agent.run(
                gh=gh,
                analysis=analysis,
                issue_number=ISSUE_NUMBER,
                model=model,
                attempt=state["attempt"],
            )
            state = set_stage_output(state, "plan", plan.model_dump())
            state = transition(state, "implementing")
            save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)

        # ── STAGES 3+4: Implement → Test (retry loop) ─────────────────────────
        if state["state"] == "implementing":
            plan = PlanOutput(**state["stage_outputs"]["plan"])
            branch_name = state.get("branch_name") or f"ai/implement-{ISSUE_NUMBER}"

            while state["attempt"] <= retry_cap:
                log_state_transition(ISSUE_NUMBER, "testing" if state["attempt"] > 0 else "planning", "implementing")

                # Create branch on first attempt
                if state["attempt"] == 0:
                    base_sha = gh.get_default_branch_sha()
                    gh.create_branch(branch_name, base_sha)
                    state["branch_name"] = branch_name
                    save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)

                # Load previous outputs if retry
                prev_implement: ImplementOutput | None = None
                prev_test: TestOutput | None = None
                if state["attempt"] > 0:
                    if "implement" in state["stage_outputs"]:
                        prev_implement = ImplementOutput(**state["stage_outputs"]["implement"])
                    if "test" in state["stage_outputs"]:
                        prev_test = TestOutput(**state["stage_outputs"]["test"])

                # Implement
                impl = implement_agent.run(
                    gh=gh,
                    plan=plan,
                    issue_number=ISSUE_NUMBER,
                    branch_name=branch_name,
                    model=model,
                    attempt=state["attempt"],
                    previous_implement=prev_implement,
                    previous_test=prev_test,
                )
                state = set_stage_output(state, "implement", impl.model_dump())
                state = transition(state, "testing")
                save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)

                log_state_transition(ISSUE_NUMBER, "implementing", "testing")

                # Test
                test_result = test_agent.run(
                    gh=gh,
                    implement_output=impl,
                    issue_number=ISSUE_NUMBER,
                    orchestrator_repo=ORCHESTRATOR_REPO,
                    model=model,
                    test_timeout_minutes=test_timeout,
                    attempt=state["attempt"],
                )
                state = set_stage_output(state, "test", test_result.model_dump())
                save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)

                if test_result.passed:
                    state = transition(state, "pr_open")
                    save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)
                    break
                else:
                    state["attempt"] += 1
                    if state["attempt"] > retry_cap:
                        _fail(
                            gh,
                            state,
                            f"Tests failed after {retry_cap} attempts. "
                            f"Last failure: {test_result.failure_summary or 'see log'}. "
                            f"Log: {test_result.full_log_url}",
                        )
                        return
                    state = transition(state, "implementing")
                    save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)

        # ── STAGE 5: Open PR ──────────────────────────────────────────────────
        if state["state"] == "pr_open":
            log_state_transition(ISSUE_NUMBER, "testing", "pr_open")
            plan = PlanOutput(**state["stage_outputs"]["plan"])
            impl = ImplementOutput(**state["stage_outputs"]["implement"])
            test_result = TestOutput(**state["stage_outputs"]["test"])
            analysis = AnalysisOutput(**state["stage_outputs"]["analysis"])

            pr_number = pr_agent.run(
                gh=gh,
                issue_number=ISSUE_NUMBER,
                plan=plan,
                implement_output=impl,
                test_output=test_result,
                diff_size_threshold=diff_threshold,
                sensitive_paths_touched=analysis.sensitive_paths_touched,
                senior_reviewer=senior_reviewer,
            )
            state["pr_number"] = pr_number
            state = transition(state, "done")
            save_state(TOKEN, REPO_OWNER, REPO_NAME, ISSUE_NUMBER, state)
            log_state_transition(ISSUE_NUMBER, "pr_open", "done")
            print(f"[INFO] Pipeline complete. PR #{pr_number} opened.")

    except Exception as exc:
        tb = traceback.format_exc()
        log_error(ISSUE_NUMBER, state.get("state", "unknown"), str(exc))
        _fail(
            gh,
            state,
            f"Unexpected error in stage '{state.get('state')}': {exc}\n\n"
            f"See GitHub Actions logs for full traceback.",
        )
        print(tb, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
