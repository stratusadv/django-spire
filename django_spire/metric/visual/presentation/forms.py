from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from django_spire.metric.visual.presentation import models

if TYPE_CHECKING:
    from typing import ClassVar


class PresentationForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Presentation
        exclude: ClassVar = []


class PresentationListFilterForm(forms.Form):
    search = forms.CharField(required=False)
