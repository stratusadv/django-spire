from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.file.factory import FileFactory
from django_spire.file.handlers import MultiFileHandler, SingleFileHandler
from django_spire.file.linker import FileLinker
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
        factory = FileFactory(related_field=ATTACHMENTS_RELATED_FIELD)
        linker = FileLinker(related_field=ATTACHMENTS_RELATED_FIELD)

        file_obj = factory.create(file)
        return linker.link(file_obj, self.obj)

    def add_attachments(self, files: list[InMemoryUploadedFile]) -> list[File]:
        factory = FileFactory(related_field=ATTACHMENTS_RELATED_FIELD)
        linker = FileLinker(related_field=ATTACHMENTS_RELATED_FIELD)

        file_objs = factory.create_many(files)
        linker.link_many(file_objs, self.obj)
        return file_objs

    def add_validated_attachment(self, file: InMemoryUploadedFile) -> File:
        validator = FileValidator(
            size_bytes_max=50 * 1024 * 1024,
            allowed_extensions=frozenset({'pdf', 'docx', 'xlsx'}),
            blocked_extensions=frozenset(),
        )

        factory = FileFactory(
            related_field=ATTACHMENTS_RELATED_FIELD,
            validator=validator,
        )

        linker = FileLinker(related_field=ATTACHMENTS_RELATED_FIELD)

        file_obj = factory.create(file)
        return linker.link(file_obj, self.obj)

    def delete_attachment(self, file_id: int) -> bool:
        file_obj = (
            self.obj.files
            .active()
            .filter(related_field=ATTACHMENTS_RELATED_FIELD, pk=file_id)
            .first()
        )

        if file_obj is None:
            return False

        file_obj.is_active = False
        file_obj.is_deleted = True
        file_obj.save()
        return True

    def delete_attachments(self) -> int:
        linker = FileLinker(related_field=ATTACHMENTS_RELATED_FIELD)
        return linker.unlink_existing(self.obj)

    def delete_profile_picture(self) -> int:
        linker = FileLinker(related_field=PROFILE_PICTURE_RELATED_FIELD)
        return linker.unlink_existing(self.obj)

    def replace_attachments(self, data: list) -> list[File]:
        handler = MultiFileHandler.for_related_field(ATTACHMENTS_RELATED_FIELD)
        return handler.save(data, self.obj)

    def replace_profile_picture(self, data) -> File | None:
        handler = SingleFileHandler.for_related_field(PROFILE_PICTURE_RELATED_FIELD)
        return handler.save(data, self.obj)
