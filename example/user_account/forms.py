from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.user_account import models


class UserAccountForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.UserAccountExample
        fields: ClassVar = []
