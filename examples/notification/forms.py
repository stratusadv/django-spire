from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from examples.notification import models


class NotificationForm(forms.ModelForm):
    linked_recipes = forms.JSONField(required=False)

    class Meta:
        model = models.NotificationExample
        fields: ClassVar = []
