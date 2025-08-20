from django.contrib.contenttypes.models import ContentType
from django.db.models import F

from django_spire.core.decorators import close_db_connections
from django_spire.file.models import File
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.tests.constants import ENTRY_IMPORT_RELATED_FIELD
from django_spire.knowledge.entry.version.block.models import EntryVersionBlock


@close_db_connections
def convert_files_to_model_objects():
    file_objects = (
        File.objects
        .related_field(field_name=ENTRY_IMPORT_RELATED_FIELD)
        .filter(content_type=ContentType.objects.get_for_model(Entry))
        .active()
        .annotate(entry=Entry.objects.filter(id=F('object_id')))
        .select_related('entry__current_version')
    )

    for file in file_objects:
        try:
            EntryVersionBlock.services.factory.create_blocks_from_file(
                file=file,
                entry_version=file.entry.current_version
            )
        except Exception:
            for file_object in file_objects:
                file_object.file.delete()
                file_object.delete()
            raise
        else:
            for file_object in file_objects:
                file_object.file.delete()
                file_object.delete()
