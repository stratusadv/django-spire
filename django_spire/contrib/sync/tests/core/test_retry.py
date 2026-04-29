from __future__ import annotations

from typing import NoReturn
from unittest.mock import patch

import pytest

from django_spire.contrib.sync.core.exceptions import (
    InvalidParameterError,
    RetryExhaustedError,
)
from django_spire.contrib.sync.core.retry import retry, _DELAY_MAX


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
    with pytest.raises(InvalidParameterError, match='must be >= 1'):
        retry(lambda: 42, attempts=0, delay=0)


def test_negative_attempts_raises() -> None:
    with pytest.raises(InvalidParameterError, match='must be >= 1'):
        retry(lambda: 42, attempts=-1, delay=0)


def test_invalid_attempts_zero_raises() -> None:
    with pytest.raises(InvalidParameterError, match='attempt'):
        retry(lambda: 42, attempts=0, delay=0)


def test_invalid_attempts_negative_raises() -> None:
    with pytest.raises(InvalidParameterError, match='attempt'):
        retry(lambda: 42, attempts=-1, delay=0)


def test_invalid_delay_negative_raises() -> None:
    with pytest.raises(InvalidParameterError, match='delay'):
        retry(lambda: 42, attempts=1, delay=-1.0)


def test_invalid_backoff_below_one_raises() -> None:
    with pytest.raises(InvalidParameterError, match='backoff'):
        retry(lambda: 42, attempts=1, delay=0, backoff=0.5)


def test_empty_exceptions_tuple_raises() -> None:
    with pytest.raises(InvalidParameterError, match='exception'):
        retry(lambda: 42, attempts=1, delay=0, exceptions=())


@patch('django_spire.contrib.sync.core.retry.time.sleep')
def test_backoff_multiplies_delay(mock_sleep: object) -> None:
    calls: list[int] = []

    def always_fail() -> NoReturn:
        calls.append(1)
        message = 'fail'
        raise OSError(message)

    with pytest.raises(RetryExhaustedError):
        retry(
            always_fail,
            attempts=4,
            delay=1.0,
            backoff=2.0,
            exceptions=(OSError,),
        )

    sleep_values = [c[0][0] for c in mock_sleep.call_args_list]

    assert len(sleep_values) == 3
    assert sleep_values[0] == pytest.approx(1.0)
    assert sleep_values[1] == pytest.approx(2.0)
    assert sleep_values[2] == pytest.approx(4.0)


@patch('django_spire.contrib.sync.core.retry.time.sleep')
def test_delay_capped_at_max(mock_sleep: object) -> None:
    calls: list[int] = []

    def always_fail() -> NoReturn:
        calls.append(1)
        message = 'fail'
        raise OSError(message)

    with pytest.raises(RetryExhaustedError):
        retry(
            always_fail,
            attempts=3,
            delay=200.0,
            backoff=2.0,
            exceptions=(OSError,),
        )

    sleep_values = [c[0][0] for c in mock_sleep.call_args_list]

    for value in sleep_values:
        assert value <= _DELAY_MAX


def test_delay_zero_is_valid() -> None:
    result = retry(lambda: 99, attempts=1, delay=0.0)

    assert result == 99


def test_backoff_exactly_one_keeps_constant_delay() -> None:
    calls: list[int] = []

    def fail_twice() -> int:
        calls.append(1)

        if len(calls) < 3:
            message = 'transient'
            raise OSError(message)

        return 42

    with patch('django_spire.contrib.sync.core.retry.time.sleep') as mock_sleep:
        result = retry(
            fail_twice,
            attempts=3,
            delay=5.0,
            backoff=1.0,
            exceptions=(OSError,),
        )

    assert result == 42

    sleep_values = [c[0][0] for c in mock_sleep.call_args_list]

    assert all(v == pytest.approx(5.0) for v in sleep_values)
