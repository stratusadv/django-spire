from __future__ import annotations

from typing import ClassVar

from django import forms

from test_project.apps.home import models


class HomeExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.HomeExample
        fields: ClassVar = []
