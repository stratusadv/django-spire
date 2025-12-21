from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile

from django_spire.file.models import File

if TYPE_CHECKING:
    from django.contrib.contenttypes.models import ContentType


def create_test_file(
    content_type: ContentType | None = None,
    object_id: int | None = None,
    name: str = 'test_file',
    file_type: str = 'pdf',
    size: str = '1.5 Mb',
    related_field: str | None = None,
    is_active: bool = True,
    is_deleted: bool = False,
) -> File:
    file_content = b'test content'
    uploaded_file = SimpleUploadedFile(
        name=f'{name}.{file_type}',
        content=file_content,
        content_type='application/octet-stream'
    )

    return File.objects.create(
        content_type=content_type,
        object_id=object_id,
        file=uploaded_file,
        name=name,
        type=file_type,
        size=size,
        related_field=related_field,
        is_active=is_active,
        is_deleted=is_deleted,
    )


def create_test_in_memory_uploaded_file(
    name: str = 'test_file',
    file_type: str = 'pdf',
    content: bytes = b'test content',
) -> InMemoryUploadedFile:
    file_io = BytesIO(content)
    file_io.seek(0)

    return InMemoryUploadedFile(
        file=file_io,
        field_name='file',
        name=f'{name}.{file_type}',
        content_type='application/octet-stream',
        size=len(content),
        charset=None,
    )
