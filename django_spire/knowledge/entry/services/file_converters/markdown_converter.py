from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.entry.services.file_converters.converter import \
    BaseFileConverter

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class MarkdownFileConverterService(BaseDjangoModelService['Entry'], BaseFileConverter):
    obj: Entry

    def convert_to_model_objs(self, file_path: str):
        a = 1
        pass
