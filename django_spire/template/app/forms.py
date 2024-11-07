from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.placeholder import models


class PlaceholderForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Placeholder
        fields: ClassVar = []
