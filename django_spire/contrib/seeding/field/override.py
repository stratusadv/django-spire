from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Any


class FieldOverride:
    def __init__(self, seeder_class: Any) -> None:
        self.seeder_class = seeder_class
        self.overrides = {}

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute lookup to self.seeder_class if the attribute isn't found
        in this FieldOverride instance.
        """

        attr = getattr(self.seeder_class, name)

        if callable(attr):
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # TODO: Error here if fields is passed as an arg.

                # Pass the overrides field to the seed method
                if 'fields' in kwargs and isinstance(kwargs['fields'], dict):
                    kwargs['fields'] = {**kwargs['fields'], **self.overrides}
                else:
                    kwargs['fields'] = self.overrides

                return attr(*args, **kwargs)

            return wrapper

        return attr

    def filter(self, **kwargs: Any) -> FieldOverride:
        self.overrides.update(kwargs)
        return self

    def seed(self, count: int = 1) -> list:
        return self.seeder_class.seed(count=count, fields=self.overrides)
