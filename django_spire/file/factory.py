from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.conf import settings

from django_spire.file.exceptions import FileValidationError
from django_spire.file.models import File
from django_spire.file.path import FilePathBuilder
from django_spire.file.utils import parse_extension, parse_name
from django_spire.file.validators import FileValidator

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile


BATCH_SIZE_MAX = 20
FILENAME_LENGTH_MAX = 100
RELATED_FIELD_LENGTH_MAX = 50


@dataclass
class FileFactory:
    related_field: str = ''
    app_name: str = 'Uncategorized'
    validator: FileValidator = field(default_factory=FileValidator)
    path_builder: FilePathBuilder = field(init=False)

    def __post_init__(self) -> None:
        if len(self.related_field) > RELATED_FIELD_LENGTH_MAX:
            message = f'related_field must not exceed {RELATED_FIELD_LENGTH_MAX} characters.'
            raise ValueError(message)

        self.path_builder = FilePathBuilder(
            base_folder=settings.BASE_FOLDER_NAME,
            app_name=self.app_name,
        )

    def create(self, file: InMemoryUploadedFile) -> File:
        self.validator.validate(file)

        file_obj = self._build(file)
        file_obj.save()
        return file_obj

    def create_many(self, files: list[InMemoryUploadedFile]) -> list[File]:
        if not files:
            return []

        if len(files) > BATCH_SIZE_MAX:
            message = f'Cannot upload more than {BATCH_SIZE_MAX} files at once.'
            raise FileValidationError(message)

        for file in files:
            self.validator.validate(file)

        built = [self._build(file) for file in files]

        return File.objects.bulk_create(built)

    def _build(self, file: InMemoryUploadedFile) -> File:
        name = parse_name(file.name)

        if len(name) > FILENAME_LENGTH_MAX:
            name = name[:FILENAME_LENGTH_MAX]

        extension = parse_extension(file.name)
        size = file.size if file.size is not None else 0
        path = self.path_builder.build(name, extension, self.related_field)

        file_obj = File(
            name=name,
            type=extension,
            size=size,
            related_field=self.related_field,
        )

        file.seek(0)
        file_obj.file.save(path, file, save=False)

        return file_obj
