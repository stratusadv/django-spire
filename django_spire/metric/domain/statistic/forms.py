from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from django_spire.metric.domain.statistic import models

if TYPE_CHECKING:
    from typing import ClassVar


class StatisticForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Statistic
        exclude: ClassVar = []


class StatisticListFilterForm(forms.Form):
    search = forms.CharField(required=False)
