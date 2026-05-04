from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from test_project.apps.sync import forms as sync_forms, models
from test_project.apps.sync.constants import (
    DEFAULT_STRATEGY,
    TRUNCATE_LIMIT,
    SyncModelLabel,
    SyncStrategy,
)
from test_project.apps.sync.types import ModelConfig

if TYPE_CHECKING:
    from typing_extensions import Any

    from django.db import models as django_models
    from django.forms import ModelForm


MODEL_MAP: dict[str, type[django_models.Model]] = {
    'client': models.Client,
    'site': models.Site,
    'stake': models.Stake,
    'surveyplan': models.SurveyPlan,
}

MODEL_FORM_MAP: dict[str, tuple[type[django_models.Model], type[ModelForm]]] = {
    'client': (models.Client, sync_forms.ClientForm),
    'site': (models.Site, sync_forms.SiteForm),
    'stake': (models.Stake, sync_forms.StakeForm),
    'surveyplan': (models.SurveyPlan, sync_forms.SurveyPlanForm),
}

LABEL_MAP: dict[str, type[django_models.Model]] = {
    SyncModelLabel.CLIENT: models.Client,
    SyncModelLabel.SITE: models.Site,
    SyncModelLabel.STAKE: models.Stake,
    SyncModelLabel.SURVEY_PLAN: models.SurveyPlan,
}

LABEL_TO_DISPLAY: dict[str, str] = {
    SyncModelLabel.CLIENT: 'Client',
    SyncModelLabel.SITE: 'Site',
    SyncModelLabel.STAKE: 'Stake',
    SyncModelLabel.SURVEY_PLAN: 'SurveyPlan',
}

DISPLAY_FIELDS: dict[str, tuple[str, ...]] = {
    'Client': ('name', 'contact_name', 'contact_email'),
    'Site': ('name', 'description', 'region', 'status'),
    'Stake': (
        'latitude', 'longitude', 'elevation', 'is_placed',
        'stake_type', 'label',
    ),
    'SurveyPlan': (
        'plan_number',
        'stake_spacing_m', 'line_direction', 'headland_offset_m', 'office_notes',
        'baseline_a_latitude', 'baseline_a_longitude',
        'baseline_b_latitude', 'baseline_b_longitude',
        'heading_degrees', 'crew_notes',
        'status',
    ),
}

FOREIGN_KEY_DISPLAY: dict[str, list[tuple[str, Any]]] = {
    'Site': [('client', lambda instance: instance.client.name if instance.client else '')],
    'Stake': [('survey_plan', lambda instance: str(instance.survey_plan) if instance.survey_plan else '')],
    'SurveyPlan': [('site', lambda instance: instance.site.name if instance.site else '')],
}

MODEL_ORDER: list[str] = ['Client', 'Site', 'SurveyPlan', 'Stake']

MODEL_LABELS: list[str] = [
    SyncModelLabel.CLIENT,
    SyncModelLabel.SITE,
    SyncModelLabel.SURVEY_PLAN,
    SyncModelLabel.STAKE,
]

MODEL_CONFIG: dict[str, ModelConfig] = {
    SyncModelLabel.CLIENT: ModelConfig(
        fields=('name', 'contact_name', 'contact_email'),
        foreign_key_fields=(),
        model=models.Client,
    ),
    SyncModelLabel.SITE: ModelConfig(
        fields=('name', 'description', 'region', 'status'),
        foreign_key_fields=('client_id',),
        model=models.Site,
    ),
    SyncModelLabel.STAKE: ModelConfig(
        fields=(
            'latitude', 'longitude', 'elevation', 'is_placed',
            'stake_type', 'label',
        ),
        foreign_key_fields=('survey_plan_id',),
        model=models.Stake,
    ),
    SyncModelLabel.SURVEY_PLAN: ModelConfig(
        fields=(
            'plan_number',
            'stake_spacing_m', 'line_direction', 'headland_offset_m', 'office_notes',
            'baseline_a_latitude', 'baseline_a_longitude',
            'baseline_b_latitude', 'baseline_b_longitude',
            'heading_degrees', 'crew_notes',
            'status',
        ),
        foreign_key_fields=('site_id',),
        model=models.SurveyPlan,
    ),
}

CREW_FIELDS: set[str] = {
    'baseline_a_latitude',
    'baseline_a_longitude',
    'baseline_b_latitude',
    'baseline_b_longitude',
    'crew_notes',
    'elevation',
    'heading_degrees',
    'is_placed',
    'latitude',
    'longitude',
}

OFFICE_FIELDS: set[str] = {
    'headland_offset_m',
    'label',
    'line_direction',
    'office_notes',
    'stake_spacing_m',
    'stake_type',
    'status',
}

STRATEGY_CHOICES: list[tuple[str, str]] = [
    (SyncStrategy.FIELD_OWNERSHIP, 'Field Ownership'),
    (SyncStrategy.FIELD_TIMESTAMP_WINS, 'Field Timestamp Wins'),
    (SyncStrategy.LOCAL_WINS, 'Local Wins'),
    (SyncStrategy.REMOTE_WINS, 'Cloud Wins'),
]
