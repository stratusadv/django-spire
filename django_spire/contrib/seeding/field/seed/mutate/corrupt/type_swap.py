import random
from typing import Any, Callable


def get_methods(severity: str) -> dict[str, Callable]:
    if severity == 'mild':
        return _mild_methods
    if severity == 'moderate':
        return {**_mild_methods, **_moderate_methods}
    if severity == 'chaos':
        return {**_mild_methods, **_moderate_methods, **_chaos_methods}
    return _mild_methods


def _to_string(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ''
    return str(value)


def _to_int(value: Any) -> Any:
    try:
        return int(value)
    except (ValueError, TypeError):
        return value


def _to_float(value: Any) -> Any:
    try:
        return float(value)
    except (ValueError, TypeError):
        return value


def _to_bool(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    if isinstance(value, (int, float)):
        return bool(value)
    return value


def _to_none(_value: Any) -> None:
    return None


def _to_empty_collection(_value: Any) -> Any:
    return random.choice([[], {}, set(), ()])


_mild_methods: dict[str, Callable] = {'_to_string': _to_string}

_moderate_methods: dict[str, Callable] = {
    '_to_int': _to_int,
    '_to_float': _to_float,
    '_to_bool': _to_bool,
}

_chaos_methods: dict[str, Callable] = {
    '_to_none': _to_none,
    '_to_empty_collection': _to_empty_collection,
}
