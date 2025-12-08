from __future__ import annotations

import inspect

from typing import Any, Callable, Sequence


def get_object_from_module_string(module_string: str) -> Any:
    try:
        module_string, object_name = module_string.rsplit('.', 1)
        module = __import__(module_string, fromlist=[object_name])
    except ImportError as e:
        message = f'Could not import module: {module_string}'
        raise ImportError(message) from e

    return getattr(module, object_name)

def get_callable_from_module_string_and_validate_arguments(
    module_string: str,
    valid_args: Sequence[str]
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
