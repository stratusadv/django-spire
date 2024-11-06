from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from examples.file import models


class FileForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.File
        fields: ClassVar = []
