from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from django_spire.metric.visual import models

if TYPE_CHECKING:
    from typing import ClassVar


class VisualForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Visual
        exclude: ClassVar = []


class VisualListFilterForm(forms.Form):
    search = forms.CharField(required=False)
