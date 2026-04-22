from __future__ import annotations

from typing import ClassVar

from django import forms

from test_project.app.ordering import models


class DuckForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Duck
        exclude: ClassVar = []
