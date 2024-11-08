from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.pagination import models


class PaginationExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.PaginationExample
        fields: ClassVar = []
