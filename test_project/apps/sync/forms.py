from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from test_project.apps.sync import models

if TYPE_CHECKING:
    from typing import ClassVar


class ClientForm(forms.ModelForm):
    class Meta:
        model = models.Client
        exclude: ClassVar = []


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        exclude: ClassVar = []


class SurveyPlanForm(forms.ModelForm):
    class Meta:
        model = models.SurveyPlan
        exclude: ClassVar = []


class StakeForm(forms.ModelForm):
    class Meta:
        model = models.Stake
        exclude: ClassVar = []
