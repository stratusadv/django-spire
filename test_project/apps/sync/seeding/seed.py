from __future__ import annotations

import random
import time
import uuid

from faker import Faker

from test_project.apps.sync.choices import (
    LineDirectionChoices,
    PlanStatusChoices,
    SiteStatusChoices,
    StakeTypeChoices,
)
from test_project.apps.sync.config import get_active_tablet_databases
from test_project.apps.sync.context import get_tablet_count, switch_db
from test_project.apps.sync.models import Client, Site, Stake, SurveyPlan


SCENARIO_CHOICES = [
    ('land_survey', 'Land Survey'),
    ('randomized', 'Randomized'),
]

_SHARED_CLIENT_ID = uuid.UUID('aaaaaaaa-aaaa-aaaa-aaaa-000000000001')
_SHARED_PLAN_ID = uuid.UUID('cccccccc-cccc-cccc-cccc-000000000001')
_SHARED_SITE_ID = uuid.UUID('bbbbbbbb-bbbb-bbbb-bbbb-000000000001')
_SHARED_STAKE_1_ID = uuid.UUID('dddddddd-dddd-dddd-dddd-000000000001')
_SHARED_STAKE_2_ID = uuid.UUID('dddddddd-dddd-dddd-dddd-000000000002')
_SHARED_STAKE_3_ID = uuid.UUID('dddddddd-dddd-dddd-dddd-000000000003')
_SHARED_STAKE_4_ID = uuid.UUID('dddddddd-dddd-dddd-dddd-000000000004')
_SHARED_STAKE_5_ID = uuid.UUID('dddddddd-dddd-dddd-dddd-000000000005')

_TABLET_STAKE_IDS = [
    _SHARED_STAKE_3_ID,
    _SHARED_STAKE_4_ID,
    _SHARED_STAKE_5_ID,
]


def seed_sync_scenario(
    scenario: str = 'land_survey',
    seed: int | None = None,
) -> dict:
    if seed is None:
        seed = random.randint(1000, 9999)

    tablet_count = get_tablet_count()
    _clear_databases(tablet_count)

    if scenario == 'randomized':
        result = _seed_randomized(seed, tablet_count)
    else:
        result = _seed_land_survey(tablet_count)

    result['seed'] = seed

    return result


def _clear_databases(tablet_count: int) -> None:
    databases = get_active_tablet_databases(tablet_count) + ['cloud']

    for db in databases:
        switch_db(db)
        Stake.objects.all().delete()
        SurveyPlan.objects.all().delete()
        Site.objects.all().delete()
        Client.objects.all().delete()


def _create_base_data(db_name: str) -> tuple[Client, Site, SurveyPlan, Stake, Stake]:
    switch_db(db_name)

    client = Client.objects.create(
        id=_SHARED_CLIENT_ID,
        name='Riverside Land Trust',
        contact_name='Dana Morrison',
        contact_email='dana@riversidelt.ca',
    )

    site = Site.objects.create(
        id=_SHARED_SITE_ID,
        client=client,
        name='North Quarter Section 14',
        description='Boundary and control point survey',
        region='Lethbridge, AB',
        status='active',
    )

    plan = SurveyPlan.objects.create(
        id=_SHARED_PLAN_ID,
        site=site,
        plan_number='SP-0041',
        stake_spacing_m=50,
        line_direction='NS',
        headland_offset_m=0,
        office_notes='',
        baseline_a_latitude=0,
        baseline_a_longitude=0,
        baseline_b_latitude=0,
        baseline_b_longitude=0,
        heading_degrees=0,
        crew_notes='',
        status='draft',
    )

    stake_1 = Stake.objects.create(
        id=_SHARED_STAKE_1_ID,
        survey_plan=plan,
        latitude=0,
        longitude=0,
        elevation=0,
        is_placed=False,
        stake_type='boundary',
        label='BND-001',
    )

    stake_2 = Stake.objects.create(
        id=_SHARED_STAKE_2_ID,
        survey_plan=plan,
        latitude=0,
        longitude=0,
        elevation=0,
        is_placed=False,
        stake_type='boundary',
        label='BND-002',
    )

    return client, site, plan, stake_1, stake_2


def _seed_land_survey(tablet_count: int) -> dict:
    _create_base_data('cloud')
    time.sleep(0.01)

    switch_db('cloud')
    cloud_plan = SurveyPlan.objects.get(id=_SHARED_PLAN_ID)
    cloud_plan.office_notes = 'Priority survey for Q4 deadline'
    cloud_plan.headland_offset_m = 10
    cloud_plan.save()

    tablet_databases = get_active_tablet_databases(tablet_count)

    for tablet_db in tablet_databases:
        time.sleep(0.01)
        _create_base_data(tablet_db)

    time.sleep(0.01)

    _TABLET_MODIFICATIONS = [
        {
            'stake_id': _SHARED_STAKE_1_ID,
            'stake_updates': {
                'latitude': 49.6942,
                'longitude': -112.8134,
                'elevation': 915.2,
                'is_placed': True,
            },
            'plan_updates': {
                'crew_notes': 'South boundary line completed',
                'baseline_a_latitude': 49.6942,
                'baseline_a_longitude': -112.8134,
            },
        },
        {
            'stake_id': _SHARED_STAKE_2_ID,
            'stake_updates': {
                'latitude': 49.6950,
                'longitude': -112.8126,
                'elevation': 918.7,
                'is_placed': True,
            },
            'plan_updates': {
                'baseline_b_latitude': 49.6950,
                'baseline_b_longitude': -112.8126,
            },
        },
        {
            'new_stake': {
                'id': _SHARED_STAKE_3_ID,
                'latitude': 49.6960,
                'longitude': -112.8119,
                'elevation': 920.1,
                'is_placed': True,
                'stake_type': 'boundary',
                'label': 'BND-003',
            },
        },
        {
            'new_stake': {
                'id': _SHARED_STAKE_4_ID,
                'latitude': 49.6968,
                'longitude': -112.8112,
                'elevation': 919.5,
                'is_placed': True,
                'stake_type': 'boundary',
                'label': 'BND-004',
            },
        },
        {
            'new_stake': {
                'id': _SHARED_STAKE_5_ID,
                'latitude': 49.6975,
                'longitude': -112.8105,
                'elevation': 921.0,
                'is_placed': True,
                'stake_type': 'control',
                'label': 'CTL-001',
            },
            'plan_updates': {
                'status': 'in-progress',
                'heading_degrees': 175,
            },
        },
    ]

    for index, tablet_db in enumerate(tablet_databases):
        if index >= len(_TABLET_MODIFICATIONS):
            break

        modification = _TABLET_MODIFICATIONS[index]
        switch_db(tablet_db)

        if 'stake_id' in modification:
            stake = Stake.objects.get(id=modification['stake_id'])

            for attr, value in modification['stake_updates'].items():
                setattr(stake, attr, value)

            stake.save()

        if 'new_stake' in modification:
            plan = SurveyPlan.objects.get(id=_SHARED_PLAN_ID)
            Stake.objects.create(survey_plan=plan, **modification['new_stake'])

        if 'plan_updates' in modification:
            plan = SurveyPlan.objects.get(id=_SHARED_PLAN_ID)

            for attr, value in modification['plan_updates'].items():
                setattr(plan, attr, value)

            plan.save()

    return {
        'scenario': 'land_survey',
        'tablet_count': tablet_count,
    }


def _seed_randomized(seed: int, tablet_count: int) -> dict:
    rng = random.Random(seed)
    fake = Faker()
    Faker.seed(seed)

    num_clients = rng.randint(2, 4)
    num_sites_per_client = rng.randint(1, 3)
    num_plans_per_site = rng.randint(1, 2)
    num_stakes_per_plan = rng.randint(2, 5)

    line_directions = [c.value for c in LineDirectionChoices]
    plan_statuses = [c.value for c in PlanStatusChoices]
    site_statuses = [c.value for c in SiteStatusChoices]
    stake_types = [c.value for c in StakeTypeChoices]

    shared_clients = []
    shared_sites = []
    shared_plans = []
    shared_stakes = []

    for _ in range(num_clients):
        client_id = uuid.UUID(int=rng.getrandbits(128))
        shared_clients.append({
            'id': client_id,
            'contact_email': fake.email(),
            'contact_name': fake.name(),
            'name': fake.company(),
        })

        for _ in range(num_sites_per_client):
            site_id = uuid.UUID(int=rng.getrandbits(128))
            shared_sites.append({
                'id': site_id,
                'client_id': client_id,
                'description': fake.paragraph(nb_sentences=2),
                'name': fake.catch_phrase(),
                'region': fake.city(),
                'status': rng.choice(site_statuses),
            })

            for _ in range(num_plans_per_site):
                plan_id = uuid.UUID(int=rng.getrandbits(128))

                shared_plans.append({
                    'id': plan_id,
                    'site_id': site_id,
                    'baseline_a_latitude': 0,
                    'baseline_a_longitude': 0,
                    'baseline_b_latitude': 0,
                    'baseline_b_longitude': 0,
                    'crew_notes': '',
                    'heading_degrees': 0,
                    'headland_offset_m': 0,
                    'line_direction': rng.choice(line_directions),
                    'office_notes': '',
                    'plan_number': f'SP-{rng.randint(1000, 9999):04d}',
                    'stake_spacing_m': rng.choice([25, 50, 75, 100]),
                    'status': 'draft',
                })

                for j in range(num_stakes_per_plan):
                    stake_id = uuid.UUID(int=rng.getrandbits(128))
                    shared_stakes.append({
                        'id': stake_id,
                        'survey_plan_id': plan_id,
                        'elevation': 0,
                        'is_placed': False,
                        'label': f'STK-{j + 1:04d}',
                        'latitude': 0,
                        'longitude': 0,
                        'stake_type': rng.choice(stake_types),
                    })

    all_databases = get_active_tablet_databases(tablet_count) + ['cloud']

    for db in all_databases:
        switch_db(db)
        time.sleep(0.005)

        for data in shared_clients:
            Client.objects.create(**data)

        for data in shared_sites:
            Site.objects.create(**data)

        for data in shared_plans:
            SurveyPlan.objects.create(**data)

        for data in shared_stakes:
            Stake.objects.create(**data)

    tablet_databases = get_active_tablet_databases(tablet_count)

    for index, tablet_db in enumerate(tablet_databases):
        tablet_rng = random.Random(seed + index + 1)
        switch_db(tablet_db)
        time.sleep(0.005)

        stakes_to_modify = tablet_rng.sample(
            shared_stakes,
            k=min(len(shared_stakes), tablet_rng.randint(1, 3)),
        )

        for stake_data in stakes_to_modify:
            stake = Stake.objects.get(id=stake_data['id'])
            stake.latitude = round(tablet_rng.uniform(49.0, 51.0), 4)
            stake.longitude = round(tablet_rng.uniform(-114.0, -110.0), 4)
            stake.elevation = round(tablet_rng.uniform(900.0, 950.0), 1)
            stake.is_placed = True
            stake.save()

    switch_db('cloud')
    time.sleep(0.005)

    for plan_data in shared_plans:
        plan = SurveyPlan.objects.get(id=plan_data['id'])
        plan.office_notes = fake.sentence()
        plan.headland_offset_m = rng.choice([5, 10, 15, 20])
        plan.status = rng.choice(plan_statuses)
        plan.save()

    return {
        'scenario': 'randomized',
        'tablet_count': tablet_count,
    }
