from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices


class BaseBlock(ABC, BaseModel):
    value: Any
    type: BlockTypeChoices
    detail_template: str
    update_template: str

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)

        if cls.detail_template is None or cls.detail_template == '':
            raise ValueError(
                f'{cls.__module__}.{cls.__qualname__}.detail_template must be set'
            )

        if cls.update_template is None or cls.update_template == '':
            raise ValueError(
                f'{cls.__module__}.{cls.__qualname__}.update_template must be set'
            )

    @abstractmethod
    def render_to_text(self) -> str:
        raise NotImplementedError
