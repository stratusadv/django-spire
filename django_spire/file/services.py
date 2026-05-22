from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from django_spire.file.models import File
from django_spire.file.path import FilePathBuilder

if TYPE_CHECKING:
    from django.db import models


logger = logging.getLogger(__name__)

COPY_BATCH_SIZE_MAX = 200


def copy_files_to_instance(
    source_files: models.QuerySet,
    target: models.Model,
) -> list[File]:
    if target.pk is None:
        message = 'Cannot copy files to an unsaved model instance.'
        raise ValueError(message)

    if not source_files.exists():
        return []

    source_count = source_files.count()

    if source_count > COPY_BATCH_SIZE_MAX:
        message = (
            f'Cannot copy more than {COPY_BATCH_SIZE_MAX} '
            f'files at once ({source_count} requested).'
        )
        raise ValueError(message)

    target_content_type = ContentType.objects.get_for_model(target)

    path_builder = FilePathBuilder(
        base_folder=settings.BASE_FOLDER_NAME,
        app_name=target._meta.app_label,
    )

    copies = []

    for source_file in source_files:
        target_file = File(
            content_type=target_content_type,
            object_id=target.pk,
            name=source_file.name,
            size=source_file.size,
            type=source_file.type,
            related_field=source_file.related_field,
        )

        path = path_builder.build(
            source_file.name or 'unnamed',
            source_file.type or 'bin',
            source_file.related_field,
        )

        source_file.file.open('rb')

        try:
            target_file.file.save(path, source_file.file, save=False)
        finally:
            source_file.file.close()

        copies.append(target_file)

    return File.objects.bulk_create(copies)
