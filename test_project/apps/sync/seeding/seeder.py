from __future__ import annotations

import random

from typing import TYPE_CHECKING

from django_spire.contrib.seeding import DjangoModelSeeder

from test_project.apps.sync import models

if TYPE_CHECKING:
    from typing import ClassVar

    from django.db.models import Model


class ClientSeeder(DjangoModelSeeder):
    model_class = models.Client
    default_to = 'faker'

    fields: ClassVar = {
        'id': 'exclude',
        'sync_field_timestamps': 'exclude',
        'sync_field_last_modified': 'exclude',
        'name': ('faker', 'company'),
        'contact_name': ('faker', 'name'),
        'contact_email': ('faker', 'email'),
    }


class SiteSeeder(DjangoModelSeeder):
    model_class = models.Site
    default_to = 'faker'

    fields: ClassVar = {
        'id': 'exclude',
        'sync_field_timestamps': 'exclude',
        'sync_field_last_modified': 'exclude',
        'client_id': 'exclude',
        'name': ('faker', 'catch_phrase'),
        'description': ('faker', 'paragraph'),
        'region': ('faker', 'city'),
        'status': 'active',
    }

    @classmethod
    def seed_database(cls, count=1, fields: dict | None = None) -> list[Model]:
        if fields is None:
            fields = {}

        clients = list(models.Client.objects.all())

        if not clients:
            return []

        sites = []

        for data in cls.seed_data(count, fields):
            data['client'] = random.choice(clients)
            sites.append(models.Site.objects.create(**data))

        return sites


class SurveyPlanSeeder(DjangoModelSeeder):
    model_class = models.SurveyPlan
    default_to = 'faker'

    fields: ClassVar = {
        'id': 'exclude',
        'sync_field_timestamps': 'exclude',
        'sync_field_last_modified': 'exclude',
        'site_id': 'exclude',
        'plan_number': ('faker', 'bothify', {'text': 'SP-####'}),
        'stake_spacing_m': 50,
        'line_direction': 'NS',
        'headland_offset_m': 0,
        'office_notes': '',
        'baseline_a_latitude': 0,
        'baseline_a_longitude': 0,
        'baseline_b_latitude': 0,
        'baseline_b_longitude': 0,
        'heading_degrees': 0,
        'crew_notes': '',
        'status': 'draft',
    }

    @classmethod
    def seed_database(cls, count=1, fields: dict | None = None) -> list[Model]:
        if fields is None:
            fields = {}

        sites = list(models.Site.objects.all())

        if not sites:
            return []

        plans = []

        for data in cls.seed_data(count, fields):
            data['site'] = random.choice(sites)
            plans.append(models.SurveyPlan.objects.create(**data))

        return plans


class StakeSeeder(DjangoModelSeeder):
    model_class = models.Stake
    default_to = 'faker'

    fields: ClassVar = {
        'id': 'exclude',
        'sync_field_timestamps': 'exclude',
        'sync_field_last_modified': 'exclude',
        'survey_plan_id': 'exclude',
        'latitude': 0,
        'longitude': 0,
        'elevation': 0,
        'is_placed': False,
        'stake_type': 'boundary',
        'label': ('faker', 'bothify', {'text': 'STK-####'}),
    }

    @classmethod
    def seed_database(cls, count=1, fields: dict | None = None) -> list[Model]:
        if fields is None:
            fields = {}

        plans = list(models.SurveyPlan.objects.all())

        if not plans:
            return []

        stakes = []

        for data in cls.seed_data(count, fields):
            data['survey_plan'] = random.choice(plans)
            stakes.append(models.Stake.objects.create(**data))

        return stakes
