from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.file.models import File
from django_spire.knowledge.entry.tests.constants import ENTRY_IMPORT_RELATED_FIELD

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django_spire.knowledge.entry.models import Entry


class EntryToolService(BaseDjangoModelService['Entry']):
    obj: Entry

    def get_files_to_convert(self) -> QuerySet[File]:
        return (
            File.objects.related_field(field_name=ENTRY_IMPORT_RELATED_FIELD)
            .filter(content_type=ContentType.objects.get_for_model(self.obj_class))
            .active()
            .order_by('object_id')
        )

    def get_files_to_convert_json(self) -> str:
        return json.dumps(
            [
                {
                    'id': file_object.id,
                    'name': file_object.name,
                    'type': file_object.type,
                    'size': file_object.size,
                }
                for file_object in self.get_files_to_convert()
            ]
        )
