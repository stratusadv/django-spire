from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.authentication.mfa import models


class AuthenticationMfaForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.AuthenticationMfaExample
        fields: ClassVar = []
