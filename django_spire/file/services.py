from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile

from django_spire.file.models import File

if TYPE_CHECKING:
    from django.db import models


def copy_files_to_instance(
    source_files: models.QuerySet,
    target: models.Model,
) -> list[File]:
    if target.pk is None:
        message = 'Cannot copy files to an unsaved model instance.'
        raise ValueError(message)

    if not source_files.exists():
        return []

    target_content_type = ContentType.objects.get_for_model(target)
    copies = []

    for source_file in source_files:
        copy = File(
            content_type=target_content_type,
            object_id=target.pk,
            name=source_file.name,
            size=source_file.size,
            type=source_file.type,
            related_field=source_file.related_field,
        )

        source_file.file.open('rb')

        copy.file.save(
            source_file.file.name,
            ContentFile(source_file.file.read()),
            save=False
        )

        source_file.file.close()

        copies.append(copy)

    return File.objects.bulk_create(copies)
