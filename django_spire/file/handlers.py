from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from django_spire.file.exceptions import FileValidationError
from django_spire.file.factory import FileFactory, BATCH_SIZE_MAX
from django_spire.file.linker import FileLinker
from django_spire.file.models import File

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.db import models

    from django_spire.file.validators import FileValidator


@dataclass
class SingleFileHandler:
    factory: FileFactory
    linker: FileLinker

    @classmethod
    def for_related_field(
        cls,
        related_field: str = '',
        validator: FileValidator | None = None,
    ) -> SingleFileHandler:
        factory_kwargs = {'related_field': related_field}

        if validator is not None:
            factory_kwargs['validator'] = validator

        return cls(
            factory=FileFactory(**factory_kwargs),
            linker=FileLinker(related_field=related_field),
        )

    def add(self, file: InMemoryUploadedFile, instance: models.Model) -> File:
        file_obj = self.factory.create(file)
        return self.linker.link(file_obj, instance)

    def replace(
        self,
        data: dict | InMemoryUploadedFile | None,
        instance: models.Model,
    ) -> File | None:
        if data is None:
            return None

        if isinstance(data, dict):
            return self._replace_from_ajax(data, instance)

        if hasattr(data, 'read'):
            return self._replace_from_upload(data, instance)

        message = f'Unsupported data type: {type(data).__name__}'
        raise TypeError(message)

    def remove(self, file_id: int, instance: models.Model) -> bool:
        content_type = ContentType.objects.get_for_model(instance)

        updated = (
            File.objects
            .active()
            .filter(
                pk=file_id,
                content_type=content_type,
                object_id=instance.pk,
            )
            .related_field(self.linker.related_field)
            .update(is_active=False, is_deleted=True)
        )

        return updated > 0

    def remove_all(self, instance: models.Model) -> int:
        return self.linker.unlink_existing(instance)

    def _replace_from_ajax(self, data: dict, instance: models.Model) -> File | None:
        file_id = data.get('id')

        if not file_id:
            return None

        try:
            file_id = int(file_id)
        except (TypeError, ValueError):
            return None

        content_type = ContentType.objects.get_for_model(instance)

        existing = File.objects.filter(
            id=file_id,
            content_type=content_type,
            object_id=instance.pk,
        ).first()

        if existing is not None:
            return existing

        file_obj = File.objects.filter(
            id=file_id,
            content_type__isnull=True,
            object_id__isnull=True,
        ).first()

        if file_obj is None:
            return None

        self.linker.unlink_existing(instance)
        return self.linker.link(file_obj, instance)

    def _replace_from_upload(self, file: InMemoryUploadedFile, instance: models.Model) -> File:
        self.linker.unlink_existing(instance)
        file_obj = self.factory.create(file)
        return self.linker.link(file_obj, instance)


@dataclass
class MultiFileHandler:
    factory: FileFactory
    linker: FileLinker

    @classmethod
    def for_related_field(
        cls,
        related_field: str = '',
        validator: FileValidator | None = None,
    ) -> MultiFileHandler:
        factory_kwargs = {'related_field': related_field}

        if validator is not None:
            factory_kwargs['validator'] = validator

        return cls(
            factory=FileFactory(**factory_kwargs),
            linker=FileLinker(related_field=related_field),
        )

    def add(self, file: InMemoryUploadedFile, instance: models.Model) -> File:
        file_obj = self.factory.create(file)
        return self.linker.link(file_obj, instance)

    def add_many(self, files: list[InMemoryUploadedFile], instance: models.Model) -> list[File]:
        if not files:
            return []

        file_objs = self.factory.create_many(files)
        self.linker.link_many(file_objs, instance)
        return file_objs

    def replace(
        self,
        data: list[dict] | list[InMemoryUploadedFile] | None,
        instance: models.Model,
    ) -> list[File]:
        if not data:
            return []

        if len(data) > BATCH_SIZE_MAX:
            message = f'Cannot process more than {BATCH_SIZE_MAX} files at once.'
            raise FileValidationError(message)

        first = data[0]

        if isinstance(first, dict):
            return self._replace_from_ajax(data, instance)

        if hasattr(first, 'read'):
            return self._replace_from_upload(data, instance)

        message = f'Unsupported data element type: {type(first).__name__}'
        raise TypeError(message)

    def remove(self, file_id: int, instance: models.Model) -> bool:
        content_type = ContentType.objects.get_for_model(instance)

        updated = (
            File.objects
            .active()
            .filter(
                pk=file_id,
                content_type=content_type,
                object_id=instance.pk,
            )
            .related_field(self.linker.related_field)
            .update(is_active=False, is_deleted=True)
        )

        return updated > 0

    def remove_all(self, instance: models.Model) -> int:
        return self.linker.unlink_existing(instance)

    def _replace_from_ajax(self, data: list[dict], instance: models.Model) -> list[File]:
        file_ids = []

        for entry in data:
            raw_id = entry.get('id')
            if raw_id:
                try:
                    file_ids.append(int(raw_id))
                except (TypeError, ValueError):
                    continue

        content_type = ContentType.objects.get_for_model(instance)

        allowed_ids = set(
            File.objects
            .filter(id__in=file_ids)
            .filter(
                Q(content_type__isnull=True, object_id__isnull=True)
                | Q(content_type=content_type, object_id=instance.pk)
            )
            .values_list('id', flat=True)
        )
        verified_ids = [file_id for file_id in file_ids if file_id in allowed_ids]

        self.linker.unlink_except(instance, keep_ids=verified_ids)

        unlinked = list(
            File.objects.filter(
                id__in=verified_ids,
                content_type__isnull=True,
                object_id__isnull=True,
            )
        )
        self.linker.link_many(unlinked, instance)

        return list(
            File.objects
            .active()
            .filter(content_type=content_type, object_id=instance.pk)
            .related_field(self.linker.related_field)
        )

    def _replace_from_upload(
        self,
        files: list[InMemoryUploadedFile],
        instance: models.Model,
    ) -> list[File]:
        self.linker.unlink_existing(instance)

        uploaded = self.factory.create_many(files)
        self.linker.link_many(uploaded, instance)

        return uploaded
