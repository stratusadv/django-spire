from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from django_spire.file.extensions import DOCUMENT_EXTENSIONS, IMAGE_EXTENSIONS
from django_spire.file.fields import MultipleFileField, SingleFileField
from django_spire.file.validators import FileValidator

from test_project.apps.file import models
from test_project.apps.file.constants import (
    ATTACHMENTS_RELATED_FIELD,
    PROFILE_PICTURE_RELATED_FIELD,
)

if TYPE_CHECKING:
    from typing import ClassVar


class FileExampleForm(forms.ModelForm):
    profile_picture = SingleFileField(
        related_field=PROFILE_PICTURE_RELATED_FIELD,
        required=True,
        validator=FileValidator(
            allowed_extensions=IMAGE_EXTENSIONS,
        ),
    )

    attachments = MultipleFileField(
        related_field=ATTACHMENTS_RELATED_FIELD,
        required=False,
        validator=FileValidator(
            size_bytes_max=50 * 1024 * 1024,
            allowed_extensions=DOCUMENT_EXTENSIONS | IMAGE_EXTENSIONS,
        ),
    )

    class Meta:
        model = models.FileExample
        exclude: ClassVar = []
