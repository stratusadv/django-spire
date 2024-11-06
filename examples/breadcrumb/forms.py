from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from examples.breadcrumb import models


class BreadcrumbForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.BreadcrumbExample
        fields: ClassVar = []
