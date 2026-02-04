from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from django_spire.metric.visual.signage import models

if TYPE_CHECKING:
    from typing import ClassVar


class SignageForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Signage
        exclude: ClassVar = []


class SignageListFilterForm(forms.Form):
    search = forms.CharField(required=False)
