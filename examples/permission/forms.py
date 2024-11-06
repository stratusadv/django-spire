from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from examples.permission import models


class PermissionForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.PermissionExample
        fields: ClassVar = []
