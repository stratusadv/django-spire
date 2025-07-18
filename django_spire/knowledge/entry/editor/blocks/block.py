from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from django_spire.knowledge.entry.block.choices import BlockTypeChoices


class BaseBlock(ABC, BaseModel):
    value: Any
    update_template: str
    display_template: str
    _type: BlockTypeChoices

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        if cls.update_template is None or cls.update_template == '':
            raise ValueError(f'{cls.__module__}.{cls.__qualname__}.update_template must be set')

    @property
    def type(self) -> BlockTypeChoices:
        return self._type

    @abstractmethod
    def render_to_text(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def render_to_html(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def update(self, **kwargs):
        raise NotImplementedError
