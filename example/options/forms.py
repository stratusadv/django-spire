from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.options import models


class OptionsExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.OptionsExample
        fields: ClassVar = []
