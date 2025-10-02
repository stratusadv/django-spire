from __future__ import annotations

from typing import TYPE_CHECKING

import json

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.core.decorators import close_db_connections
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock
from django_spire.knowledge.exceptions import KnowledgeBaseConversionException

if TYPE_CHECKING:
    from django_spire.knowledge.entry.models import Entry


class EntryAutomationService(BaseDjangoModelService['Entry']):
    obj: Entry

    @close_db_connections
    def convert_files_to_model_objects(self) -> str:
        file_objects = self.obj_class.services.tool.get_files_to_convert()

        entries = self.obj_class.objects.id_in(
            list({file_object.object_id for file_object in file_objects})
        ).select_related('current_version')

        entry_pk_map = {entry.pk: entry for entry in entries}

        errored = []
        for file_object in file_objects:
            try:
                EntryVersionBlock.services.factory.create_blocks_from_file(
                    file=file_object,
                    entry_version=entry_pk_map[file_object.object_id].current_version,
                )
            except Exception as e:
                errored.append({'file': file_object.name, 'error': str(e)})

        message = f'Files Converted: {len(file_objects) - len(errored)}'
        if errored:
            raise KnowledgeBaseConversionException(
                f'\n{message}\nFiles Errored: {json.dumps(errored, indent=4)}'
            )

        return message
