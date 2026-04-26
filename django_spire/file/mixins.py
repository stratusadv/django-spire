from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.file.models import File
from django_spire.file.handlers import MultiFileHandler, SingleFileHandler
from django_spire.file.services import copy_files_to_instance

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django.utils.datastructures import MultiValueDict

    from django_spire.file.validators import FileValidator


class FileModelMixin(models.Model):
    files = GenericRelation(File, editable=False)

    class Meta:
        abstract = True

    def copy_files_to(self, target: models.Model) -> list[File]:
        return copy_files_to_instance(self.files.active(), target)


class FileProcessorServiceMixin:
    @staticmethod
    def extract_single_file(files: MultiValueDict) -> InMemoryUploadedFile | None:
        return next(iter(files.values()), None)

    @staticmethod
    def extract_multiple_files(files: MultiValueDict) -> list[InMemoryUploadedFile]:
        result = []

        for field_name in files:
            result.extend(files.getlist(field_name))

        return result

    def _get_app_name(self) -> str:
        if not hasattr(self, 'obj') or self.obj is None:
            message = (
                f'{type(self).__name__} requires "obj" to be set '
                f'before calling file operations.'
            )

            raise AttributeError(message)

        return self.obj._meta.app_label

    def add_file(
        self,
        file: InMemoryUploadedFile,
        related_field: str = '',
        validator: FileValidator | None = None,
    ) -> File:
        handler = SingleFileHandler.for_related_field(
            related_field,
            validator=validator,
            app_name=self._get_app_name(),
        )

        return handler.add(file, self.obj)

    def replace_file(
        self,
        data: dict | InMemoryUploadedFile | None,
        related_field: str = '',
        validator: FileValidator | None = None,
    ) -> File | None:
        handler = SingleFileHandler.for_related_field(
            related_field,
            validator=validator,
            app_name=self._get_app_name(),
        )

        return handler.replace(data, self.obj)

    def add_files(
        self,
        files: list[InMemoryUploadedFile],
        related_field: str = '',
        validator: FileValidator | None = None,
    ) -> list[File]:
        handler = MultiFileHandler.for_related_field(
            related_field,
            validator=validator,
            app_name=self._get_app_name(),
        )

        return handler.add_many(files, self.obj)

    def replace_files(
        self,
        data: list[dict] | list[InMemoryUploadedFile] | None,
        related_field: str = '',
        validator: FileValidator | None = None,
    ) -> list[File]:
        handler = MultiFileHandler.for_related_field(
            related_field,
            validator=validator,
            app_name=self._get_app_name(),
        )

        return handler.replace(data, self.obj)

    def delete_file(self, file_id: int, related_field: str = '') -> bool:
        handler = SingleFileHandler.for_related_field(
            related_field,
            app_name=self._get_app_name(),
        )

        return handler.remove(file_id, self.obj)

    def delete_files(self, related_field: str = '') -> int:
        handler = MultiFileHandler.for_related_field(
            related_field,
            app_name=self._get_app_name(),
        )

        return handler.remove_all(self.obj)
