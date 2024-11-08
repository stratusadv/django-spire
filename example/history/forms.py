from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.history import models


class HistoryExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.HistoryExample
        fields: ClassVar = []
