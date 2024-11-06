from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from examples.gamification import models


class GamificationForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.GamificationExample
        fields: ClassVar = []
