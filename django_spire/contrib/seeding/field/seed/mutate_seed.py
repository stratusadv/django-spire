from typing import Callable, Any

from django_spire.contrib.seeding.field.seed.base import BaseFieldSeed


class MutateFieldSeed(BaseFieldSeed):
    def __init__(self, seed: BaseFieldSeed, callable_: Callable, wrapper: Callable | None = None, **kwargs) -> None:
        self.seed = seed
        self.callable = callable_
        self.wrapper = wrapper
        self.kwargs = kwargs

    def generate_value(self, seed_index: int) -> Any:
        if self.wrapper:
            return self.wrapper(self.callable(**self.kwargs))

        return self.callable(**self.kwargs)
