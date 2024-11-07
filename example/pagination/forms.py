from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.pagination import models


class PaginationForm(forms.ModelForm):
    linked_recipes = forms.JSONField(required=False)

    class Meta:
        model = models.Pagination
        fields: ClassVar = []
