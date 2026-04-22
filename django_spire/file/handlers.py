from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import Q

from django_spire.file.exceptions import FileBatchLimitError, FileIDError
from django_spire.file.factory import FileFactory, BATCH_SIZE_MAX
from django_spire.file.linker import FileLinker
from django_spire.file.models import File
from django_spire.file.utils import verify_file_token

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.db import models

    from django_spire.file.validators import FileValidator


@dataclass
class BaseFileHandler:
    factory: FileFactory
    linker: FileLinker

    def __post_init__(self) -> None:
        if self.factory.related_field != self.linker.related_field:
            message = 'factory.related_field and linker.related_field must match.'
            raise ValueError(message)

    def add(self, file: InMemoryUploadedFile, instance: models.Model) -> File:
        file_obj = self.factory.create(file)
        return self.linker.link(file_obj, instance)

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


@dataclass
class SingleFileHandler(BaseFileHandler):
    @classmethod
    def for_related_field(
        cls,
        related_field: str = '',
        validator: FileValidator | None = None,
        app_name: str = 'Uncategorized',
    ) -> SingleFileHandler:
        factory_kwargs = {'related_field': related_field, 'app_name': app_name}

        if validator is not None:
            factory_kwargs['validator'] = validator

        return cls(
            factory=FileFactory(**factory_kwargs),
            linker=FileLinker(related_field=related_field),
        )

    def replace(
        self,
        data: dict | InMemoryUploadedFile | None,
        instance: models.Model,
    ) -> File | None:
        if data is None:
            return None

        if isinstance(data, dict):
            return self._replace_from_ajax(data, instance)

        if isinstance(data, UploadedFile):
            return self._replace_from_upload(data, instance)

        message = f'Unsupported data type: {type(data).__name__}'
        raise TypeError(message)

    def _replace_from_ajax(self, data: dict, instance: models.Model) -> File | None:
        file_id_raw = data.get('id')

        if not file_id_raw:
            return None

        try:
            file_id = int(file_id_raw)
        except (TypeError, ValueError):
            message = f'Invalid file ID: {file_id_raw}'
            raise FileIDError(message) from None

        content_type = ContentType.objects.get_for_model(instance)

        existing = File.objects.filter(
            id=file_id,
            content_type=content_type,
            object_id=instance.pk,
        ).first()

        if existing is not None:
            return existing

        file_token = data.get('token', '')

        if not verify_file_token(file_id, file_token):
            return None

        file_obj = File.objects.filter(
            id=file_id,
            content_type__isnull=True,
            object_id__isnull=True,
        ).first()

        if file_obj is None:
            return None

        with transaction.atomic():
            self.linker.unlink_existing(instance)
            return self.linker.link(file_obj, instance)

    def _replace_from_upload(self, file: InMemoryUploadedFile, instance: models.Model) -> File:
        with transaction.atomic():
            self.linker.unlink_existing(instance)
            file_obj = self.factory.create(file)
            return self.linker.link(file_obj, instance)


@dataclass
class MultiFileHandler(BaseFileHandler):
    @classmethod
    def for_related_field(
        cls,
        related_field: str = '',
        validator: FileValidator | None = None,
        app_name: str = 'Uncategorized',
    ) -> MultiFileHandler:
        factory_kwargs = {'related_field': related_field, 'app_name': app_name}

        if validator is not None:
            factory_kwargs['validator'] = validator

        return cls(
            factory=FileFactory(**factory_kwargs),
            linker=FileLinker(related_field=related_field),
        )

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
            raise FileBatchLimitError(message)

        first = data[0]

        if isinstance(first, dict):
            if not all(isinstance(element, dict) for element in data):
                message = 'Cannot mix file uploads and existing file references in the same request.'
                raise TypeError(message)

            return self._replace_from_ajax(data, instance)

        if isinstance(first, UploadedFile):
            if not all(isinstance(element, UploadedFile) for element in data):
                message = 'Cannot mix file uploads and existing file references in the same request.'
                raise TypeError(message)

            return self._replace_from_upload(data, instance)

        message = f'Unsupported data element type: {type(first).__name__}'
        raise TypeError(message)

    def _replace_from_ajax(self, data: list[dict], instance: models.Model) -> list[File]:
        file_entries = []

        for entry in data:
            file_id_raw = entry.get('id')

            if not file_id_raw:
                continue

            try:
                file_id = int(file_id_raw)
            except (TypeError, ValueError):
                message = f'Invalid file ID: {file_id_raw}'
                raise FileIDError(message) from None

            file_entries.append({
                'id': file_id,
                'token': entry.get('token', ''),
            })

        content_type = ContentType.objects.get_for_model(instance)

        entry_ids = [entry['id'] for entry in file_entries]

        already_linked_ids = set(
            File.objects
            .filter(
                id__in=entry_ids,
                content_type=content_type,
                object_id=instance.pk,
            )
            .values_list('id', flat=True)
        )

        orphan_q = Q()

        for entry in file_entries:
            if entry['id'] not in already_linked_ids and verify_file_token(entry['id'], entry['token']):
                orphan_q |= Q(id=entry['id'])

        claimable_orphan_ids = set()

        if orphan_q:
            claimable_orphan_ids = set(
                File.objects
                .filter(orphan_q)
                .filter(content_type__isnull=True, object_id__isnull=True)
                .values_list('id', flat=True)
            )

        verified_ids = list(already_linked_ids | claimable_orphan_ids)

        with transaction.atomic():
            self.linker.unlink_except(instance, keep_ids=verified_ids)

            unlinked = list(
                File.objects.filter(
                    id__in=verified_ids,
                    content_type__isnull=True,
                    object_id__isnull=True,
                )
            )

            if unlinked:
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
        with transaction.atomic():
            self.linker.unlink_existing(instance)

            uploaded = self.factory.create_many(files)
            self.linker.link_many(uploaded, instance)

            return uploaded
