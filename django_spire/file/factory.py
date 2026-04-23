from __future__ import annotations

import logging

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.utils.text import get_valid_filename

from django_spire.file.exceptions import FileBatchLimitError
from django_spire.file.models import File
from django_spire.file.path import FilePathBuilder
from django_spire.file.utils import parse_extension
from django_spire.file.validators import FileValidator

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile


logger = logging.getLogger(__name__)

BATCH_SIZE_MAX = 20
EXTENSION_LENGTH_MAX = 20
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

        file_obj = self._build_file_record(file)
        file_obj.save()
        return file_obj

    def create_many(self, files: list[InMemoryUploadedFile]) -> list[File]:
        if not files:
            return []

        if len(files) > BATCH_SIZE_MAX:
            message = f'Cannot upload more than {BATCH_SIZE_MAX} files at once.'
            raise FileBatchLimitError(message)

        for file in files:
            self.validator.validate(file)

        built = [self._build_file_record(file) for file in files]

        try:
            return File.objects.bulk_create(built)
        except Exception:
            for file_obj in built:
                try:
                    file_obj.file.delete(save=False)
                except Exception:
                    logger.exception('Failed to clean up storage orphan: %s', file_obj.file.name)

            raise

    def _build_file_record(self, file: InMemoryUploadedFile) -> File:
        try:
            filename_sanitized = get_valid_filename(file.name)
        except SuspiciousFileOperation:
            filename_sanitized = None

        if filename_sanitized:
            path = PurePosixPath(filename_sanitized)
            name = path.stem
            extension = path.suffix.lstrip('.').lower()
        else:
            name = ''
            extension = ''

        if not extension:
            extension = parse_extension(file.name) or 'bin'

        if not name:
            name = 'unnamed'

        if len(name) > FILENAME_LENGTH_MAX:
            name = name[:FILENAME_LENGTH_MAX]

        if len(extension) > EXTENSION_LENGTH_MAX:
            extension = extension[:EXTENSION_LENGTH_MAX]

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
