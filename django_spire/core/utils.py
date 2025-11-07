import inspect
from inspect import Signature
from typing import Callable, Any, Sequence


def get_object_from_module_string(module_string: str) -> Any:
    try:
        module_string, object_name = module_string.rsplit('.', 1)
        module = __import__(module_string, fromlist=[object_name])
    except ImportError:
        raise ImportError(f'Could not import module: {module_string}')

    return getattr(module, object_name)

def get_callable_from_module_string_and_validate_arguments(
        module_string: str,
        valid_args: Sequence[str],
) -> Callable:
    callable_ = get_object_from_module_string(module_string)

    if not callable(callable_):
        raise TypeError(f'Object {module_string} is not callable')

    sig = inspect.signature(callable_)
    params = sig.parameters

    for name in valid_args:
        if name not in params:
            message = f'{callable_.__qualname__} is missing required argument: {name}'
            raise TypeError(message)

    return callable_