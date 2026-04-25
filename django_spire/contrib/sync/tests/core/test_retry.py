from __future__ import annotations

from typing import NoReturn

import pytest

from django_spire.contrib.sync.core.exceptions import (
    InvalidParameterError,
    RetryExhaustedError,
)
from django_spire.contrib.sync.core.retry import retry


def test_succeeds_first_try() -> None:
    result = retry(lambda: 42, attempts=3, delay=0)

    assert result == 42


def test_retries_on_failure() -> None:
    calls: list[int] = []

    def flaky() -> str:
        calls.append(1)

        if len(calls) < 3:
            message = 'transient'
            raise OSError(message)

        return 'ok'

    result = retry(
        flaky,
        attempts=3,
        delay=0,
        exceptions=(OSError,),
    )

    assert result == 'ok'
    assert len(calls) == 3


def test_raises_retry_exhausted_after_all_attempts() -> None:
    def always_fail() -> NoReturn:
        message = 'permanent'
        raise OSError(message)

    with pytest.raises(RetryExhaustedError, match='exhausted 2 attempt') as exc_info:
        retry(always_fail, attempts=2, delay=0, exceptions=(OSError,))

    assert isinstance(exc_info.value.__cause__, OSError)


def test_does_not_catch_unrelated_exceptions() -> None:
    def wrong_error() -> NoReturn:
        message = 'wrong'
        raise ValueError(message)

    with pytest.raises(ValueError, match='wrong'):
        retry(wrong_error, attempts=3, delay=0, exceptions=(OSError,))


def test_default_does_not_catch_programming_errors() -> None:
    def broken() -> NoReturn:
        message = 'bug'
        raise TypeError(message)

    with pytest.raises(TypeError, match='bug'):
        retry(broken, attempts=3, delay=0)


def test_default_catches_oserror() -> None:
    calls: list[int] = []

    def flaky() -> str:
        calls.append(1)

        if len(calls) < 2:
            message = 'transient'
            raise OSError(message)

        return 'ok'

    result = retry(flaky, attempts=3, delay=0)

    assert result == 'ok'
    assert len(calls) == 2


def test_zero_attempts_raises() -> None:
    with pytest.raises(InvalidParameterError, match='attempts must be >= 1'):
        retry(lambda: 42, attempts=0, delay=0)


def test_negative_attempts_raises() -> None:
    with pytest.raises(InvalidParameterError, match='attempts must be >= 1'):
        retry(lambda: 42, attempts=-1, delay=0)
