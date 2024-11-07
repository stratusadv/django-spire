from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.help import models


class HelpForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.HelpExample
        fields: ClassVar = []
