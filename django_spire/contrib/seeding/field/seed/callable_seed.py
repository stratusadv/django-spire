from typing import Callable, Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class CallableFieldSeed(BaseFieldSeed):
    def __init__(self, callable_: Callable, wrapper: Callable | None = None, **kwargs) -> None:
        self.callable = callable_
        self.wrapper = wrapper
        self.kwargs = kwargs

    def generate_cache_key(self) -> str:
        callable_key = f'{self.callable.__module__}.{self.callable.__qualname__}'
        wrapper_key = (
            f'{self.wrapper.__module__}.{self.wrapper.__qualname__}' if self.wrapper else None
        )
        return f'{callable_key}:{wrapper_key}:{self.kwargs}'

    def generate_value(self, seed_index: int) -> Any:
        _ = seed_index

        if self.wrapper:
            return self.wrapper(self.callable(**self.kwargs))

        return self.callable(**self.kwargs)
