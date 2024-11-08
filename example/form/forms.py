from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.form import models


class FormExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.FormExample
        fields: ClassVar = []
