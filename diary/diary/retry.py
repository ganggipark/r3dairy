"""Transient error retry with exponential backoff for LLM calls.

Compatible with openai + anthropic exception naming (class-name based).
"""
from __future__ import annotations
import time
from typing import Callable, TypeVar

T = TypeVar("T")

_RETRYABLE_NAMES = frozenset([
    # HTTP / network transient
    "RateLimitError",
    "APITimeoutError",
    "APIConnectionError",
    "InternalServerError",
    "ServiceUnavailableError",
    "APIStatusError",
    # LLM output quality (often self-resolves on retry)
    "ContentGenerationError",
    "JSONDecodeError",
    "ValidationError",
])

_NON_RETRYABLE_NAMES = frozenset([
    "AuthenticationError",
    "BadRequestError",
    "PermissionDeniedError",
    "NotFoundError",
    "InvalidRequestError",
    "UnprocessableEntityError",
])


def is_retryable(exc: BaseException) -> bool:
    """True if exc looks like a transient error worth retrying."""
    name = type(exc).__name__

    if name in _NON_RETRYABLE_NAMES:
        return False

    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    if isinstance(status, int):
        if status == 429 or 500 <= status < 600:
            return True
        if 400 <= status < 500:
            return False

    if name in _RETRYABLE_NAMES:
        return True

    msg = str(exc).lower()
    if any(k in msg for k in (
        "timeout", "connection",
        "503", "502", "504",
        "rate limit", "rate_limit",
    )):
        return True

    return False


def with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> T:
    """Call fn() up to max_attempts times with exponential backoff on retryable errors.

    Backoff schedule: base_delay * 2**attempt sec (1s, 2s, 4s, ...).
    Non-retryable errors raise immediately.
    """
    last_exc: BaseException | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except BaseException as e:
            last_exc = e
            if not is_retryable(e):
                raise
            if attempt < max_attempts - 1:
                time.sleep(base_delay * (2 ** attempt))
    assert last_exc is not None
    raise last_exc
