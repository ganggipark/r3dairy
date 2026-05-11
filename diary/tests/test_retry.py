"""Retry logic tests (time.sleep mocked)."""
import pytest

from diary.retry import is_retryable, with_retry


class APIConnectionError(Exception): pass
class APITimeoutError(Exception): pass
class RateLimitError(Exception): pass
class AuthenticationError(Exception): pass
class BadRequestError(Exception): pass


class StatusError(Exception):
    def __init__(self, msg: str, status_code: int):
        super().__init__(msg)
        self.status_code = status_code


def test_retryable_by_class_name():
    assert is_retryable(APIConnectionError("net"))
    assert is_retryable(APITimeoutError("slow"))
    assert is_retryable(RateLimitError("too fast"))


def test_non_retryable_by_class_name():
    assert not is_retryable(AuthenticationError("bad key"))
    assert not is_retryable(BadRequestError("malformed"))


def test_retryable_by_status_5xx_and_429():
    assert is_retryable(StatusError("server fault", 500))
    assert is_retryable(StatusError("bad gateway", 502))
    assert is_retryable(StatusError("svc unavail", 503))
    assert is_retryable(StatusError("rate limit", 429))


def test_non_retryable_by_status_4xx():
    assert not is_retryable(StatusError("auth", 401))
    assert not is_retryable(StatusError("forbidden", 403))
    assert not is_retryable(StatusError("not found", 404))


def test_retryable_by_message_fallback():
    assert is_retryable(Exception("connection refused"))
    assert is_retryable(Exception("HTTP 503 service unavailable"))


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr("diary.retry.time.sleep", lambda x: None)


def test_succeeds_on_first_call():
    calls = [0]
    def fn():
        calls[0] += 1
        return "ok"
    assert with_retry(fn) == "ok"
    assert calls[0] == 1


def test_retries_then_succeeds():
    calls = [0]
    def fn():
        calls[0] += 1
        if calls[0] < 3:
            raise APIConnectionError("transient")
        return "ok"
    assert with_retry(fn, max_attempts=3) == "ok"
    assert calls[0] == 3


def test_no_retry_on_auth_error():
    calls = [0]
    def fn():
        calls[0] += 1
        raise AuthenticationError("bad key")
    with pytest.raises(AuthenticationError):
        with_retry(fn, max_attempts=3)
    assert calls[0] == 1


def test_exhausts_retries_then_raises():
    calls = [0]
    def fn():
        calls[0] += 1
        raise APIConnectionError("always fails")
    with pytest.raises(APIConnectionError):
        with_retry(fn, max_attempts=3)
    assert calls[0] == 3
