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
from test_project.apps.sync.constants import SeedScenario
from test_project.apps.sync.context import get_tablet_count, switch_database
from test_project.apps.sync.models import Client, Site, Stake, SurveyPlan


SCENARIO_CHOICES: list[tuple[str, str]] = [
    (SeedScenario.LAND_SURVEY, 'Land Survey'),
    (SeedScenario.RANDOMIZED, 'Randomized'),
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
    scenario: str = SeedScenario.LAND_SURVEY,
    seed: int | None = None,
) -> dict:
    if seed is None:
        seed = random.randint(1000, 9999)

    tablet_count = get_tablet_count()
    _clear_databases(tablet_count)

    if scenario == SeedScenario.RANDOMIZED:
        result = _seed_randomized(seed, tablet_count)
    else:
        result = _seed_land_survey(tablet_count)

    result['seed'] = seed

    return result


def _clear_databases(tablet_count: int) -> None:
    databases = [*get_active_tablet_databases(tablet_count), 'cloud']

    for database in databases:
        switch_database(database)
        Stake.objects.all().delete()
        SurveyPlan.objects.all().delete()
        Site.objects.all().delete()
        Client.objects.all().delete()


def _create_base_data(database_name: str) -> tuple[Client, Site, SurveyPlan, Stake, Stake]:
    switch_database(database_name)

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
        plan_number='SP-2024-001',
        stake_spacing_m=50,
        line_direction=LineDirectionChoices.NS,
        headland_offset_m=10,
        office_notes='Standard boundary survey',
        baseline_a_latitude=49.6935,
        baseline_a_longitude=-112.8418,
        baseline_b_latitude=49.6945,
        baseline_b_longitude=-112.8400,
        heading_degrees=15.5,
        crew_notes='',
        status=PlanStatusChoices.DRAFT,
    )

    stake_1 = Stake.objects.create(
        id=_SHARED_STAKE_1_ID,
        survey_plan=plan,
        latitude=49.6935,
        longitude=-112.8418,
        elevation=920.5,
        is_placed=True,
        stake_type=StakeTypeChoices.CONTROL,
        label='CP-001',
    )

    stake_2 = Stake.objects.create(
        id=_SHARED_STAKE_2_ID,
        survey_plan=plan,
        latitude=49.6940,
        longitude=-112.8410,
        elevation=921.0,
        is_placed=True,
        stake_type=StakeTypeChoices.BOUNDARY,
        label='BND-001',
    )

    return client, site, plan, stake_1, stake_2


def _seed_land_survey(tablet_count: int) -> dict:
    _create_base_data('cloud')

    tablet_databases = get_active_tablet_databases(tablet_count)
    tablets_seeded = []

    for index, tablet_database in enumerate(tablet_databases):
        _create_base_data(tablet_database)
        switch_database(tablet_database)
        time.sleep(0.005)

        plan = SurveyPlan.objects.get(id=_SHARED_PLAN_ID)
        plan.crew_notes = f'Crew {index + 1}: Started NW corner, windy conditions'
        plan.status = PlanStatusChoices.IN_PROGRESS
        plan.save()

        site = Site.objects.get(id=_SHARED_SITE_ID)
        site.description = f'Crew {index + 1} survey — updated on tablet'
        site.save()

        for i, stake_id in enumerate(_TABLET_STAKE_IDS):
            Stake.objects.create(
                id=stake_id,
                survey_plan=plan,
                latitude=49.6935 + (i + 1) * 0.0005,
                longitude=-112.8418 + (i + 1) * 0.0003,
                elevation=920.5 + (i + 1) * 0.3,
                is_placed=True,
                stake_type=StakeTypeChoices.BOUNDARY,
                label=f'BND-{i + 2:03d}',
            )

        tablets_seeded.append(tablet_database)

    switch_database('cloud')
    time.sleep(0.005)

    plan = SurveyPlan.objects.get(id=_SHARED_PLAN_ID)
    plan.office_notes = 'Reviewed by PM — approved for field work'
    plan.headland_offset_m = 12
    plan.status = PlanStatusChoices.REVIEWED
    plan.save()

    client = Client.objects.get(id=_SHARED_CLIENT_ID)
    client.contact_name = 'Dana Morrison-Lee'
    client.save()

    return {'tablets_seeded': tablets_seeded}


def _seed_randomized(seed: int, tablet_count: int) -> dict:
    rng = random.Random(seed)
    fake = Faker()
    Faker.seed(seed)

    num_clients = rng.randint(1, 3)
    num_sites_per_client = rng.randint(1, 2)
    num_plans_per_site = rng.randint(1, 2)
    num_stakes_per_plan = rng.randint(2, 5)

    site_statuses = [status.value for status in SiteStatusChoices]
    line_directions = [direction.value for direction in LineDirectionChoices]
    stake_types = [stake_type.value for stake_type in StakeTypeChoices]

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

    all_databases = [*get_active_tablet_databases(tablet_count), 'cloud']

    for database in all_databases:
        switch_database(database)
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

    for index, tablet_database in enumerate(tablet_databases):
        tablet_rng = random.Random(seed + index + 1)
        switch_database(tablet_database)
        time.sleep(0.005)

        stakes_to_modify = tablet_rng.sample(
            shared_stakes,
            k=min(len(shared_stakes), tablet_rng.randint(1, 3)),
        )

        for stake_data in stakes_to_modify:
            stake = Stake.objects.get(id=stake_data['id'])
            stake.latitude = tablet_rng.uniform(49.0, 50.0)
            stake.longitude = tablet_rng.uniform(-113.0, -112.0)
            stake.elevation = tablet_rng.uniform(900, 950)
            stake.is_placed = True
            stake.save()

    switch_database('cloud')
    time.sleep(0.005)

    if shared_clients:
        cloud_client = Client.objects.get(id=shared_clients[0]['id'])
        cloud_client.contact_name = fake.name()
        cloud_client.save()

    return {'tablets_seeded': tablet_databases}
