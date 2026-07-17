import random
from datetime import timedelta
from typing import Any, Callable


def get_methods(severity: str) -> dict[str, Callable]:
    if severity == 'mild':
        return _mild_methods
    if severity == 'moderate':
        return {**_mild_methods, **_moderate_methods}
    if severity == 'chaos':
        return {**_mild_methods, **_moderate_methods, **_chaos_methods}
    return _mild_methods


def _shift_days(value: Any) -> Any:
    if value is None:
        return value
    try:
        days = random.choice([-1, 1, 2, -2])
        return value + timedelta(days=days)
    except TypeError:
        return value


def _shift_hours(value: Any) -> Any:
    if value is None:
        return value
    try:
        hours = random.choice([-1, 1, 12, -12])
        return value + timedelta(hours=hours)
    except TypeError:
        return value


def _zero_time(value: Any) -> Any:
    if value is None:
        return value
    try:
        return value.replace(hour=0, minute=0, second=0, microsecond=0)
    except AttributeError:
        return value


def _end_of_day(value: Any) -> Any:
    if value is None:
        return value
    try:
        return value.replace(hour=23, minute=59, second=59, microsecond=999999)
    except AttributeError:
        return value


def _swap_date_time(value: Any) -> Any:
    if value is None:
        return value
    try:
        return value.replace(
            year=value.month, month=value.year if hasattr(value, 'year') else value.day
        )
    except (ValueError, TypeError, AttributeError):
        return value


def _to_none(_value: Any) -> None:
    return None


_mild_methods: dict[str, Callable] = {'_shift_days': _shift_days, '_shift_hours': _shift_hours}

_moderate_methods: dict[str, Callable] = {'_zero_time': _zero_time, '_end_of_day': _end_of_day}

_chaos_methods: dict[str, Callable] = {'_swap_date_time': _swap_date_time, '_to_none': _to_none}
