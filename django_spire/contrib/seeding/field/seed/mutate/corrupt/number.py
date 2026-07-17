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


def _round_number(value: Any) -> Any:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return round(value)
    return value


def _truncate_decimals(value: Any) -> Any:
    if isinstance(value, float):
        precision = random.randint(0, 3)
        return float(f'{value:.{precision}f}')
    return value


def _swap_to_wrong_type(_value: Any) -> Any:
    return random.choice([None, '', 0, [], {}])


_mild_methods: dict[str, Callable] = {'_round_number': _round_number}

_moderate_methods: dict[str, Callable] = {'_truncate_decimals': _truncate_decimals}

_chaos_methods: dict[str, Callable] = {'_swap_to_wrong_type': _swap_to_wrong_type}
