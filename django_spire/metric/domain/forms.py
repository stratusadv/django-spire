from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from django_spire.metric.domain import models

if TYPE_CHECKING:
    from typing import ClassVar


class DomainForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Domain
        exclude: ClassVar = []


class DomainListFilterForm(forms.Form):
    search = forms.CharField(required=False)
