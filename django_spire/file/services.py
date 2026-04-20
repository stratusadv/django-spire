from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile

from django_spire.file.factory import FileFactory
from django_spire.file.handlers import SingleFileHandler
from django_spire.file.linker import FileLinker
from django_spire.file.models import File
from django_spire.file.validators import FileValidator

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile
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
        copy.file.save(source_file.file.name, ContentFile(source_file.file.read()), save=False)
        source_file.file.close()

        copies.append(copy)

    return File.objects.bulk_create(copies)


@dataclass
class FileService:
    related_field: str = ''
    app_name: str = 'Uncategorized'
    validator: FileValidator = field(default_factory=FileValidator)
    factory: FileFactory = field(init=False)
    linker: FileLinker = field(init=False)

    def __post_init__(self) -> None:
        self.factory = FileFactory(
            related_field=self.related_field,
            app_name=self.app_name,
            validator=self.validator,
        )
        self.linker = FileLinker(related_field=self.related_field)

    def upload(self, file: InMemoryUploadedFile) -> File:
        return self.factory.create(file)

    def upload_many(self, files: list[InMemoryUploadedFile]) -> list[File]:
        return self.factory.create_many(files)

    def attach(self, file_obj: File, instance: models.Model) -> File:
        return self.linker.link(file_obj, instance)

    def detach_existing(self, instance: models.Model) -> int:
        return self.linker.unlink_existing(instance)

    def save_from_form(
        self,
        data: dict | InMemoryUploadedFile | None,
        instance: models.Model,
    ) -> File | None:
        handler = SingleFileHandler(factory=self.factory, linker=self.linker)
        return handler.save(data, instance)

    def copy_to(self, source: models.Model, target: models.Model) -> list[File]:
        return copy_files_to_instance(source.files.active(), target)
