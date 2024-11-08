from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.authentication import models


class AuthenticationExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.AuthenticationExample
        fields: ClassVar = []
