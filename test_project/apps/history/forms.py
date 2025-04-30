from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from test_project.apps.history import models


class HistoryExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.HistoryExample
        fields: ClassVar = []
