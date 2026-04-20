from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.file.fields import MultipleFileField, SingleFileField
from django_spire.file.forms import FileModelForm
from django_spire.file.validators import FileValidator

from test_project.apps.file import models
from test_project.apps.file.constants import (
    ATTACHMENTS_RELATED_FIELD,
    PROFILE_PICTURE_RELATED_FIELD,
)

if TYPE_CHECKING:
    from typing import ClassVar


class FileExampleForm(FileModelForm):
    attachments = MultipleFileField(
        related_field=ATTACHMENTS_RELATED_FIELD,
        required=False,
        validator=FileValidator(
            size_bytes_max=50 * 1024 * 1024,
            allowed_extensions=frozenset({
                'jpg',
                'png',
                'pdf',
                'docx',
                'xlsx'
            }),
            blocked_extensions=frozenset(),
        ),
    )

    profile_picture = SingleFileField(
        related_field=PROFILE_PICTURE_RELATED_FIELD,
        required=False,
    )

    class Meta:
        model = models.FileExample
        exclude: ClassVar = []
