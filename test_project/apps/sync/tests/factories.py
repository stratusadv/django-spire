from __future__ import annotations

from test_project.apps.sync import models
from test_project.apps.sync.choices import PlanStatusChoices, SiteStatusChoices


def create_test_client(**kwargs):
    defaults = {
        'name': 'Test Client',
        'contact_name': 'Test Contact',
        'contact_email': 'test@example.com',
    }
    defaults.update(kwargs)
    return models.Client.objects.create(**defaults)


def create_test_site(**kwargs):
    defaults = {
        'name': 'Test Site',
        'description': 'Test description',
        'region': 'Test Region',
        'status': SiteStatusChoices.ACTIVE,
    }
    if 'client' not in kwargs:
        defaults['client'] = create_test_client()
    defaults.update(kwargs)
    return models.Site.objects.create(**defaults)


def create_test_survey_plan(**kwargs):
    defaults = {
        'plan_number': 'SP-0001',
        'stake_spacing_m': 50,
        'line_direction': 'NS',
        'status': PlanStatusChoices.DRAFT,
    }
    if 'site' not in kwargs:
        defaults['site'] = create_test_site()
    defaults.update(kwargs)
    return models.SurveyPlan.objects.create(**defaults)


def create_test_stake(**kwargs):
    defaults = {
        'latitude': 49.0,
        'longitude': -112.0,
        'elevation': 900.0,
        'is_placed': False,
        'stake_type': 'boundary',
        'label': 'STK-0001',
    }
    if 'survey_plan' not in kwargs:
        defaults['survey_plan'] = create_test_survey_plan()
    defaults.update(kwargs)
    return models.Stake.objects.create(**defaults)
