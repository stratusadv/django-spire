from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.file import models


class FileExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.File
        fields: ClassVar = []
