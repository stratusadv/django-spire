from __future__ import annotations

from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from typing import Any

from django.template.loader import render_to_string
from pydantic import BaseModel

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices

if TYPE_CHECKING:
    from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


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

    def to_dict(self, version_block: EntryVersionBlock):
        return {
            'value': self.value,
            'type': self.type,
            'update_template_rendered': render_to_string(
                context={
                    'version_block': version_block,
                    'value': self.value,
                },
                template_name=self.update_template,
            )
        }


class EditorBlock(BaseModel):
    id: str
    type: BlockTypeChoices
    data: BaseEditorBlockData
    order: int | None
    tunes: dict | None

class BaseEditorBlockData(BaseModel):
    def render_to_text(self) -> str:
        raise NotImplementedError