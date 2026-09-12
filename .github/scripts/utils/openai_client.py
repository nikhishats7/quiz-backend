"""
openai_client.py — Thin wrapper around the OpenAI API with:
  - Automatic retry (exponential back-off, up to 3 attempts)
  - Enforced JSON mode (response_format=json_object)
  - Audit logging of token usage via logger.py
  - Hard system prompt that resists injection from user content
"""

from __future__ import annotations
import json
import time
from typing import Any

from openai import OpenAI, APIError, RateLimitError

from utils.logger import log_stage_end

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()  # Reads OPENAI_API_KEY from env
    return _client


def call_llm(
    *,
    stage: str,
    issue_number: int,
    attempt: int,
    model: str,
    system_prompt: str,
    user_content: str,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """
    Call the OpenAI chat completions API with JSON mode.

    Parameters
    ----------
    stage : str
        Pipeline stage name (for logging).
    system_prompt : str
        Fixed system instructions. Must NOT contain raw user input.
    user_content : str
        Sanitized user-supplied context (issue body, file contents, etc.).
        Will appear only in the USER role, never SYSTEM.

    Returns
    -------
    dict
        Parsed JSON from the model's response.

    Raises
    ------
    ValueError
        If the model returns invalid JSON after all retries.
    """
    client = _get_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    last_error: Exception | None = None
    for attempt_n in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                temperature=0.2,  # Low temperature for deterministic code generation
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)

            # Audit log
            log_stage_end(
                stage=stage,
                issue_number=issue_number,
                attempt=attempt,
                outputs={"response_preview": content[:300]},
                model=model,
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
            )
            return parsed

        except RateLimitError as e:
            last_error = e
            wait = 2 ** (attempt_n + 2)  # 4s, 8s, 16s
            print(f"[WARN] Rate limited. Retrying in {wait}s…")
            time.sleep(wait)

        except APIError as e:
            last_error = e
            if attempt_n < 2:
                time.sleep(3)
            else:
                raise

        except json.JSONDecodeError as e:
            last_error = e
            if attempt_n < 2:
                # Ask the model to fix its output
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.choices[0].message.content,
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": "Your last response was not valid JSON. Please respond with valid JSON only.",
                    }
                )
            else:
                raise ValueError(f"Model returned invalid JSON after 3 attempts: {e}") from e

    raise RuntimeError(f"LLM call failed after 3 attempts: {last_error}")
