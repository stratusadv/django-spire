from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from examples.authentication import models


class AuthenticationForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.AuthenticationExample
        fields: ClassVar = []
