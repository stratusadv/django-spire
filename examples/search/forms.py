from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from examples.search import models


class SearchForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Search
        fields: ClassVar = []
