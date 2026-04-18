from __future__ import annotations

from typing import NoReturn

import pytest

from django_spire.contrib.sync.retry import retry


def test_succeeds_first_try() -> None:
    result = retry(lambda: 42, attempts=3, delay=0)

    assert result == 42


def test_retries_on_failure() -> None:
    calls: list[int] = []

    def flaky() -> str:
        calls.append(1)

        if len(calls) < 3:
            msg = 'transient'
            raise OSError(msg)

        return 'ok'

    result = retry(
        flaky,
        attempts=3,
        delay=0,
        exceptions=(OSError,),
    )

    assert result == 'ok'
    assert len(calls) == 3


def test_raises_after_exhausted() -> None:
    def always_fail() -> NoReturn:
        msg = 'permanent'
        raise OSError(msg)

    with pytest.raises(OSError, match='permanent'):
        retry(always_fail, attempts=2, delay=0, exceptions=(OSError,))


def test_does_not_catch_unrelated_exceptions() -> None:
    def wrong_error() -> NoReturn:
        msg = 'wrong'
        raise ValueError(msg)

    with pytest.raises(ValueError, match='wrong'):
        retry(wrong_error, attempts=3, delay=0, exceptions=(OSError,))


def test_zero_attempts_raises() -> None:
    with pytest.raises(ValueError, match='attempts must be >= 1'):
        retry(lambda: 42, attempts=0, delay=0)


def test_negative_attempts_raises() -> None:
    with pytest.raises(ValueError, match='attempts must be >= 1'):
        retry(lambda: 42, attempts=-1, delay=0)
