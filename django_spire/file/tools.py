from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.file.models import File

if TYPE_CHECKING:
    from django.db import models


def copy_files_from_source_to_target_model_object(source: models.Model, target: models.Model) -> list[File]:
    target_class = target.__class__
    target_content_type = ContentType.objects.get_for_model(target_class)

    file_list = source.files.active()

    if not file_list.exists():
        return []

    files_to_create = []

    for file in file_list:
        new_file = File(
            content_type=target_content_type,
            object_id=target.pk,
            file=file.file,
            name=file.name,
            size=file.size,
            type=file.type,
            related_field=file.related_field,
            is_active=file.is_active,
            is_deleted=file.is_deleted
        )
        files_to_create.append(new_file)

    File.objects.bulk_create(files_to_create)

    return files_to_create
