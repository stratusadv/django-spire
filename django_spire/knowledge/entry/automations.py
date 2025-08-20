from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from django_spire.core.decorators import close_db_connections
from django_spire.file.models import File
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.tests.constants import ENTRY_IMPORT_RELATED_FIELD
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


@close_db_connections
def convert_files_to_model_objects() -> str:
    file_objects = (
        File.objects
        .related_field(field_name=ENTRY_IMPORT_RELATED_FIELD)
        .filter(content_type=ContentType.objects.get_for_model(Entry))
        .active()
        .select_related('content_type')
        .order_by('object_id')
    )

    entries = Entry.objects.id_in(
        list({file_object.object_id for file_object in file_objects})
    ).select_related('current_version')

    entry_pk_map = {entry.pk: entry for entry in entries}

    errored = []
    for file_object in file_objects:
        try:
            EntryVersionBlock.services.factory.create_blocks_from_file(
                file=file_object,
                entry_version=entry_pk_map[file_object.object_id].current_version
            )
        except Exception as e:
            errored.append({'file': file_object.name, 'error': str(e)})
            file_object.file.delete()
            file_object.delete()
        else:
            file_object.file.delete()
            file_object.delete()

    return (
        f'Files Converted: {len(file_objects) - len(errored)}\nFiles Errored: {errored}'
    )
