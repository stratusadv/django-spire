from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.file.factory import RELATED_FIELD_LENGTH_MAX
from django_spire.file.models import File

if TYPE_CHECKING:
    from django.db import models


@dataclass
class FileLinker:
    related_field: str = ''

    def __post_init__(self) -> None:
        if len(self.related_field) > RELATED_FIELD_LENGTH_MAX:
            message = f'related_field must not exceed {RELATED_FIELD_LENGTH_MAX} characters.'
            raise ValueError(message)

    def link(self, file_obj: File, instance: models.Model) -> File:
        if instance.pk is None:
            message = 'Cannot link a file to an unsaved model instance.'
            raise ValueError(message)

        content_type = ContentType.objects.get_for_model(instance)

        file_obj.content_type = content_type
        file_obj.object_id = instance.pk
        file_obj.related_field = self.related_field
        file_obj.is_active = True
        file_obj.is_deleted = False
        file_obj.save()

        return file_obj

    def link_many(self, file_objects: list[File], instance: models.Model) -> None:
        if instance.pk is None:
            message = 'Cannot link files to an unsaved model instance.'
            raise ValueError(message)

        content_type = ContentType.objects.get_for_model(instance)

        for file_obj in file_objects:
            file_obj.content_type = content_type
            file_obj.object_id = instance.pk
            file_obj.related_field = self.related_field
            file_obj.is_active = True
            file_obj.is_deleted = False

        File.objects.bulk_update(
            file_objects,
            ['content_type', 'object_id', 'related_field', 'is_active', 'is_deleted'],
        )

    def unlink_existing(self, instance: models.Model) -> int:
        if instance.pk is None:
            message = 'Cannot unlink files from an unsaved model instance.'
            raise ValueError(message)

        content_type = ContentType.objects.get_for_model(instance)

        return (
            File.objects
            .active()
            .filter(content_type=content_type, object_id=instance.pk)
            .related_field(self.related_field)
            .update(is_active=False, is_deleted=True)
        )

    def unlink_except(self, instance: models.Model, keep_ids: list[int]) -> int:
        if instance.pk is None:
            message = 'Cannot unlink files from an unsaved model instance.'
            raise ValueError(message)

        content_type = ContentType.objects.get_for_model(instance)

        return (
            File.objects
            .active()
            .filter(content_type=content_type, object_id=instance.pk)
            .related_field(self.related_field)
            .exclude(id__in=keep_ids)
            .update(is_active=False, is_deleted=True)
        )
