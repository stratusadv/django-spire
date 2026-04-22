from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.file.mixins import FileProcessorServiceMixin

from test_project.apps.file.constants import (
    ATTACHMENTS_RELATED_FIELD,
    PROFILE_PICTURE_RELATED_FIELD,
)

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile

    from django_spire.file.models import File

    from test_project.apps.file.models import FileExample


class FileExampleProcessorService(FileProcessorServiceMixin, BaseDjangoModelService['FileExample']):
    obj: FileExample

    def save_files(
        self,
        profile_picture: dict | InMemoryUploadedFile | None = None,
        attachments: list[dict] | list[InMemoryUploadedFile] | None = None,
        **kwargs,
    ) -> None:
        _ = kwargs

        self.replace_file(profile_picture, PROFILE_PICTURE_RELATED_FIELD)
        self.replace_files(attachments, ATTACHMENTS_RELATED_FIELD)

    def add_attachment(self, file: InMemoryUploadedFile) -> File:
        return self.add_file(file, ATTACHMENTS_RELATED_FIELD)

    def add_attachments(self, files: list[InMemoryUploadedFile]) -> list[File]:
        return self.add_files(files, ATTACHMENTS_RELATED_FIELD)

    def delete_attachment(self, file_id: int) -> bool:
        return self.delete_file(file_id, ATTACHMENTS_RELATED_FIELD)

    def delete_attachments(self) -> int:
        return self.delete_files(ATTACHMENTS_RELATED_FIELD)

    def delete_profile_picture(self) -> int:
        return self.delete_files(PROFILE_PICTURE_RELATED_FIELD)

    def replace_attachments(
        self,
        data: list[dict] | list[InMemoryUploadedFile] | None,
    ) -> list[File]:
        return self.replace_files(data, ATTACHMENTS_RELATED_FIELD)

    def replace_profile_picture(
        self,
        data: dict | InMemoryUploadedFile | None,
    ) -> File | None:
        return self.replace_file(data, PROFILE_PICTURE_RELATED_FIELD)
