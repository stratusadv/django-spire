from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.service import BaseDjangoModelService
from django_spire.file.models import File
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock

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

            EntryVersionBlock.services.factory.create_blocks_from_file(
                file=file,
                entry_version=entry.current_version
            )

        return entries
