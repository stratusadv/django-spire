from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.breadcrumb import models


class BreadcrumbExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.BreadcrumbExample
        fields: ClassVar = []
