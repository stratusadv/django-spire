from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django import forms

from django_spire.file import widgets
from django_spire.file.queryset import FileQuerySet

if TYPE_CHECKING:
    from django_spire.file.models import File


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widgets.MultipleWidget()

    def prepare_value(self, value: list[File] | None):
        if value is not None:
            return json.dumps([file.to_dict() for file in value])

        return json.dumps([])

    def clean(self, data, initial = None) -> dict:
        return data


class SingleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widgets.SingleFileWidget()

    def prepare_value(self, value: File | FileQuerySet | None) -> str | None:
        if isinstance(value, FileQuerySet):
            value =  value.first()

        if value is not None:
            return value.to_json()

        return json.dumps(None)

    def clean(self, data, initial = None) -> dict:
        return data
