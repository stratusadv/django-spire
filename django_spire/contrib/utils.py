from __future__ import annotations

import inspect
from typing import Any, Sequence, Callable

from django_spire.contrib.constants import TIME_UNITS_TO_SECONDS
from django_spire.exceptions import DjangoSpireInvalidClassStringError


def truncate_string(string: str, length: int) -> str:
    return string[: (length - 3)] + '...' if len(string) > length else string


def format_duration(
    amount: float,
    start_unit: str = 'second',
    min_unit: str = 'second',
    included_units: list[str] | None = None,
    is_short_form: bool = False,
) -> str:
    """
    Converts duration into a readable format. (ex. 1h 15m or 1 hour 15 minutes)
    """

    if not amount or amount == 0:
        return 'Unknown'

    if start_unit not in TIME_UNITS_TO_SECONDS.keys():
        message = (
            f'{start_unit} is not a valid start unit, choices are {TIME_UNITS_TO_SECONDS.keys()}'
        )
        raise ValueError(message)

    amount = amount * TIME_UNITS_TO_SECONDS[start_unit]

    components = []

    for unit, divisor in TIME_UNITS_TO_SECONDS.items():
        if included_units and unit not in included_units:
            continue

        converted_amount, amount = divmod(int(amount), divisor)

        if converted_amount > 0:
            if is_short_form:
                duration = f'{converted_amount}{unit[0]}'
            else:
                pluralize = '' if converted_amount == 1 else 's'
                duration = f'{converted_amount} {unit}{pluralize}'

            components.append(duration)

        # Stop if we reach the defined minimum unit
        if unit == min_unit:
            break

    separator = ' ' if is_short_form else ', '
    return separator.join(components)


def get_object_from_module_string(module_string: str) -> Any:
    try:
        module_string, object_name = module_string.rsplit('.', 1)
        module = __import__(module_string, fromlist=[object_name])
    except ImportError as e:
        message = f'Could not import module: {module_string}'
        raise ImportError(message) from e

    return getattr(module, object_name)


def get_callable_from_module_string_and_validate_arguments(
    module_string: str, valid_args: Sequence[str]
) -> Callable:
    callable_ = get_object_from_module_string(module_string)

    if not callable(callable_):
        message = f'Object {module_string} is not callable'
        raise TypeError(message)

    sig = inspect.signature(callable_)
    params = sig.parameters

    for name in valid_args:
        if name not in params:
            message = f'{callable_.__qualname__} is missing required argument: {name}'
            raise TypeError(message)

    return callable_


def get_class_from_string(class_string: str) -> type:
    class_parts = class_string.split('.')

    if len(class_parts) < 2:
        message = f'Class string {class_string} is not a valid class string.'
        raise DjangoSpireInvalidClassStringError(message)

    module_path = '.'.join(class_parts[:-1])
    class_name = class_parts[-1]

    module = __import__(module_path, fromlist=[class_name])

    return getattr(module, class_name)


def get_class_name_from_class(cls: type) -> str:
    return cls.__module__ + '.' + cls.__qualname__
