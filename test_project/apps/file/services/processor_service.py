from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.file.handlers import MultiFileHandler, SingleFileHandler
from django_spire.file.validators import FileValidator

from test_project.apps.file.constants import (
    ATTACHMENTS_RELATED_FIELD,
    PROFILE_PICTURE_RELATED_FIELD,
)

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile

    from django_spire.file.models import File

    from test_project.apps.file.models import FileExample


class FileExampleProcessorService(BaseDjangoModelService['FileExample']):
    obj: FileExample

    def add_attachment(self, file: InMemoryUploadedFile) -> File:
        handler = SingleFileHandler.for_related_field(ATTACHMENTS_RELATED_FIELD)
        return handler.add(file, self.obj)

    def add_attachments(self, files: list[InMemoryUploadedFile]) -> list[File]:
        handler = MultiFileHandler.for_related_field(ATTACHMENTS_RELATED_FIELD)
        return handler.add_many(files, self.obj)

    def add_validated_attachment(self, file: InMemoryUploadedFile) -> File:
        validator = FileValidator(
            size_bytes_max=50 * 1024 * 1024,
            allowed_extensions=frozenset({'pdf', 'docx', 'xlsx'}),
            blocked_extensions=frozenset(),
        )

        handler = SingleFileHandler.for_related_field(
            ATTACHMENTS_RELATED_FIELD,
            validator=validator
        )

        return handler.add(file, self.obj)

    def delete_attachment(self, file_id: int) -> bool:
        handler = MultiFileHandler.for_related_field(ATTACHMENTS_RELATED_FIELD)
        return handler.remove(file_id, self.obj)

    def delete_attachments(self) -> int:
        handler = MultiFileHandler.for_related_field(ATTACHMENTS_RELATED_FIELD)
        return handler.remove_all(self.obj)

    def delete_profile_picture(self) -> int:
        handler = SingleFileHandler.for_related_field(PROFILE_PICTURE_RELATED_FIELD)
        return handler.remove_all(self.obj)

    def replace_attachments(
        self,
        data: list[dict] | list[InMemoryUploadedFile] | None,
    ) -> list[File]:
        handler = MultiFileHandler.for_related_field(ATTACHMENTS_RELATED_FIELD)
        return handler.replace(data, self.obj)

    def replace_profile_picture(
        self,
        data: dict | InMemoryUploadedFile | None,
    ) -> File | None:
        handler = SingleFileHandler.for_related_field(PROFILE_PICTURE_RELATED_FIELD)
        return handler.replace(data, self.obj)
