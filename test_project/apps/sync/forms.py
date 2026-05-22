from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from test_project.apps.sync import models

if TYPE_CHECKING:
    from typing import ClassVar


class ClientForm(forms.ModelForm):
    class Meta:
        model = models.Client
        fields: ClassVar = ['contact_email', 'contact_name', 'name']


class SiteForm(forms.ModelForm):
    class Meta:
        model = models.Site
        fields: ClassVar = ['client', 'description', 'name', 'region', 'status']


class StakeForm(forms.ModelForm):
    class Meta:
        model = models.Stake
        fields: ClassVar = [
            'elevation', 'is_placed', 'label',
            'latitude', 'longitude',
            'stake_type', 'survey_plan',
        ]


class SurveyPlanForm(forms.ModelForm):
    class Meta:
        model = models.SurveyPlan
        fields: ClassVar = [
            'baseline_a_latitude', 'baseline_a_longitude',
            'baseline_b_latitude', 'baseline_b_longitude',
            'crew_notes', 'heading_degrees', 'headland_offset_m',
            'line_direction', 'office_notes', 'plan_number',
            'site', 'stake_spacing_m', 'status',
        ]
