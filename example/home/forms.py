from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.home import models


class HomeForm(forms.ModelForm):
    linked_recipes = forms.JSONField(required=False)

    class Meta:
        model = models.HomeExample
        fields: ClassVar = []
