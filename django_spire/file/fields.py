from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django import forms
from django.core.files.uploadedfile import UploadedFile

from django_spire.file import widgets
from django_spire.file.exceptions import FileValidationError
from django_spire.file.queryset import FileQuerySet

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile

    from django_spire.file.models import File
    from django_spire.file.validators import FileValidator


class MultipleFileField(forms.FileField):
    def __init__(
        self,
        *args,
        related_field: str = '',
        validator: FileValidator | None = None,
        **kwargs
    ) -> None:
        self.related_field = related_field
        self.validator = validator
        super().__init__(*args, **kwargs)

        self.widget = widgets.MultipleFileWidget()

    def prepare_value(self, value: list[File] | None) -> str:
        if value is not None:
            return json.dumps([file.to_dict() for file in value])

        return json.dumps([])

    def clean(
        self,
        data: list[dict] | list[InMemoryUploadedFile],
        _initial: list[dict] | None = None,
    ) -> list[dict] | list[InMemoryUploadedFile]:
        if self.validator is not None and data:
            for file in data:
                if isinstance(file, UploadedFile):
                    try:
                        self.validator.validate(file)
                    except FileValidationError as exception:
                        raise forms.ValidationError(str(exception)) from exception

        return data


class SingleFileField(forms.FileField):
    def __init__(self, *args, related_field: str = '', validator: FileValidator | None = None, **kwargs) -> None:
        self.related_field = related_field
        self.validator = validator
        super().__init__(*args, **kwargs)

        self.widget = widgets.SingleFileWidget()

    def prepare_value(self, value: File | FileQuerySet | None) -> str:
        if isinstance(value, FileQuerySet):
            value = value.first()

        if value is not None:
            return value.to_json()

        return json.dumps(None)

    def clean(
        self,
        data: dict | InMemoryUploadedFile | None,
        _initial: dict | None = None,
    ) -> dict | InMemoryUploadedFile | None:
        if self.validator is not None and data is not None and isinstance(data, UploadedFile):
            try:
                self.validator.validate(data)
            except FileValidationError as exception:
                message = str(exception)
                raise forms.ValidationError(message) from exception

        return data
