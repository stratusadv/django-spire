from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.notification import models


class NotificationExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.NotificationExample
        fields: ClassVar = []
