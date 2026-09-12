"""
sanitizer.py — Strip untrusted issue content before it touches any LLM prompt.

Rules:
  1. Remove <system>...</system> blocks (prompt-injection via XML tags).
  2. Remove common jailbreak phrases.
  3. Hard-truncate to MAX_CHARS to avoid token overflow.
  4. Never allow raw user content to appear in the SYSTEM role of a prompt.
"""

from __future__ import annotations
import re

# Maximum characters of user-supplied text allowed into any prompt
MAX_CHARS = 8_000

# Phrases that indicate prompt injection attempts
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"<\s*system\s*>.*?<\s*/\s*system\s*>", re.IGNORECASE | re.DOTALL),
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.IGNORECASE),
    re.compile(r"act\s+as\s+(a|an)\s+", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"DAN\s+mode", re.IGNORECASE),
    re.compile(r"<!-- .*? -->", re.DOTALL),  # strip HTML comments
    re.compile(r"\[INST\]|\[/INST\]"),        # Llama-style instruction tags
]

# Replacement text inserted where injection attempts were found
_REDACTION_MARKER = "[REDACTED: potential prompt injection]"


def sanitize(text: str | None) -> str:
    """
    Clean user-supplied text (issue title, body, comment) before embedding
    it in an LLM prompt.

    Returns a safe, truncated string.
    """
    if not text:
        return ""

    cleaned = text

    # 1. Remove injection patterns
    for pattern in _INJECTION_PATTERNS:
        cleaned = pattern.sub(_REDACTION_MARKER, cleaned)

    # 2. Collapse excessive whitespace (but preserve newlines for readability)
    cleaned = re.sub(r"[ \t]{4,}", "    ", cleaned)

    # 3. Hard-truncate
    if len(cleaned) > MAX_CHARS:
        cleaned = cleaned[:MAX_CHARS] + "\n\n[... truncated for safety ...]"

    return cleaned


def sanitize_list(items: list[str]) -> list[str]:
    """Sanitize a list of strings (e.g. issue comments)."""
    return [sanitize(item) for item in items]
