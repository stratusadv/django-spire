from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.home import models


class HomeExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.HomeExample
        fields: ClassVar = []
