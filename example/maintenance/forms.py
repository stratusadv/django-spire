from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.maintenance import models


class MaintenanceExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.MaintenanceExample
        fields: ClassVar = []
