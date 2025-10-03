from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.service import BaseDjangoModelService
from django_spire.file.models import File
from django_spire.knowledge.entry.constants import ENTRY_IMPORT_RELATED_FIELD

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry
    from django_spire.knowledge.collection.models import Collection


class EntryFactoryService(BaseDjangoModelService['Entry']):
    obj: Entry

    def create_from_files(
            self,
            author: AuthUser,
            collection: Collection,
            files: list[File],
    ) -> list[Entry]:
        entries = []
        for file in files:
            entry, _ = self.obj_class.services.save_model_obj(
                name=file.name,
                author=author,
                collection=collection
            )
            entries.append(entry)

            file.content_type = ContentType.objects.get_for_model(entry.__class__)
            file.object_id = entry.id
            file.related_field = ENTRY_IMPORT_RELATED_FIELD

            entry.ordering_services.processor.move_to_position(
                destination_objects=collection.entries.active(),
                position=0,
            )

        File.objects.bulk_update(files, ['content_type', 'object_id', 'related_field'])

        return entries
