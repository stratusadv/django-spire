from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from django_spire.knowledge.entry.block.choices import BlockTypeChoices


class BaseBlock(ABC, BaseModel):
    value: Any
    _type: BlockTypeChoices

    @property
    def type(self) -> BlockTypeChoices:
        return self._type

    @abstractmethod
    def render_to_text(self) -> str:
        raise NotImplementedError
