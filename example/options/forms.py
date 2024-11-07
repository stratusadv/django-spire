from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.options import models


class OptionsForm(forms.ModelForm):
    linked_recipes = forms.JSONField(required=False)

    class Meta:
        model = models.OptionsExample
        fields: ClassVar = []
