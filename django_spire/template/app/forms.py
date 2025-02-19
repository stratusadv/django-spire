from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from module import models


class SpireChildAppForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.SpireChildApp
        fields: ClassVar = []
