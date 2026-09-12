"""
openai_client.py — Thin wrapper around the Gemini API (retaining the file name for compatibility)
  - Automatic retry (exponential back-off, up to 3 attempts)
  - Enforced JSON mode (response_mime_type="application/json")
  - Audit logging of token usage via logger.py
"""

from __future__ import annotations
import json
import time
import os
from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import APIError

from utils.logger import log_stage_end

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        # Automatically reads GEMINI_API_KEY from environment
        _client = genai.Client()
    return _client


def call_llm(
    *,
    stage: str,
    issue_number: int,
    attempt: int,
    model: str,
    system_prompt: str,
    user_content: str,
    max_tokens: int = 8192,
) -> dict[str, Any]:
    """
    Call the Gemini API with JSON mode.
    """
    client = _get_client()
    
    last_error: Exception | None = None
    for attempt_n in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json",
                )
            )
            
            content = response.text or "{}"
            parsed = json.loads(content)

            prompt_tokens = 0
            completion_tokens = 0
            if response.usage_metadata:
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count

            log_stage_end(
                stage=stage,
                issue_number=issue_number,
                attempt=attempt,
                outputs={"response_preview": content[:300]},
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            return parsed

        except APIError as e:
            last_error = e
            if getattr(e, 'code', None) == 429: # Rate limit
                wait = 2 ** (attempt_n + 3)
                print(f"[WARN] Rate limited. Retrying in {wait}s…")
                time.sleep(wait)
            else:
                if attempt_n < 2:
                    time.sleep(3)
                else:
                    raise

        except json.JSONDecodeError as e:
            last_error = e
            if attempt_n < 2:
                user_content += f"\n\nYour last response was not valid JSON. Please respond with valid JSON only."
            else:
                raise ValueError(f"Model returned invalid JSON after 3 attempts: {e}") from e

    raise RuntimeError(f"LLM call failed after 3 attempts: {last_error}")
