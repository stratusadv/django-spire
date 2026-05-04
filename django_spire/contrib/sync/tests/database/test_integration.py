from __future__ import annotations

import pytest

from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.tests.database.helpers import (
    SURVEY,
    STAKE,
    SyncHarness,
)


@pytest.fixture
def harness() -> SyncHarness:
    return SyncHarness()


def test_worker_gps_and_office_spacing_both_survive(
    harness: SyncHarness,
) -> None:
    early = harness.ts()
    tablet_gps = harness.ts()
    office_spacing = harness.ts()

    harness.tablet_save(
        SURVEY, 'sv-1',
        {
            'id': 'sv-1',
            'stake_spacing': 40,
            'bearing': 90,
            'a_latitude': 49.6942,
            'a_longitude': -112.8134,
        },
        {
            'stake_spacing': early,
            'bearing': early,
            'a_latitude': tablet_gps,
            'a_longitude': tablet_gps,
        },
    )

    harness.server_save(
        SURVEY, 'sv-1',
        {
            'id': 'sv-1',
            'stake_spacing': 60,
            'bearing': 90,
            'a_latitude': 0.0,
            'a_longitude': 0.0,
        },
        {
            'stake_spacing': office_spacing,
            'bearing': early,
            'a_latitude': early,
            'a_longitude': early,
        },
    )

    harness.sync()

    tablet = harness.tablet_record(SURVEY, 'sv-1')
    server = harness.server_record(SURVEY, 'sv-1')

    assert tablet.data['a_latitude'] == 49.6942
    assert tablet.data['a_longitude'] == -112.8134
    assert tablet.data['stake_spacing'] == 60

    assert server.data['a_latitude'] == 49.6942
    assert server.data['a_longitude'] == -112.8134
    assert server.data['stake_spacing'] == 60


def test_server_delete_propagates_to_tablet(
    harness: SyncHarness,
) -> None:
    ts1 = harness.ts()

    harness.tablet_save(
        STAKE, 'st-3',
        {'id': 'st-3', 'latitude': 49.0},
        {'latitude': ts1},
    )

    harness.sync()

    server = harness.server_record(STAKE, 'st-3')
    assert server is not None

    ts2 = harness.ts()

    harness.server_storage._records[STAKE]['st-3'] = SyncRecord(
        key='st-3',
        data={'id': 'st-3', 'latitude': 49.0, 'is_deleted': True},
        timestamps={'latitude': ts1, 'is_deleted': ts2},
    )

    harness.sync()

    tablet = harness.tablet_record(STAKE, 'st-3')

    assert tablet is not None
    assert tablet.data['is_deleted'] is True


def test_full_day_scenario() -> None:
    harness = SyncHarness()

    early = harness.ts()
    tablet_gps = harness.ts()

    harness.tablet_save(
        SURVEY, 'sv-north',
        {
            'id': 'sv-north',
            'survey_number': 'N-42',
            'stake_spacing': 40,
            'bearing': 90,
            'a_latitude': 49.6942,
            'a_longitude': -112.8134,
            'b_latitude': 49.6950,
            'b_longitude': -112.8100,
        },
        {
            'survey_number': early,
            'stake_spacing': early,
            'bearing': early,
            'a_latitude': tablet_gps,
            'a_longitude': tablet_gps,
            'b_latitude': tablet_gps,
            'b_longitude': tablet_gps,
        },
    )

    stake_ts = harness.ts()

    for i in range(5):
        harness.tablet_save(
            STAKE, f'st-{i}',
            {
                'id': f'st-{i}',
                'survey_id': 'sv-north',
                'latitude': 49.6942 + (i * 0.001),
                'longitude': -112.8134 + (i * 0.001),
                'is_driven': True,
            },
            {
                'survey_id': stake_ts,
                'latitude': stake_ts,
                'longitude': stake_ts,
                'is_driven': stake_ts,
            },
        )

    office_spacing = harness.ts()

    harness.server_save(
        SURVEY, 'sv-north',
        {
            'id': 'sv-north',
            'survey_number': 'N-42',
            'stake_spacing': 60,
            'bearing': 90,
            'a_latitude': 0.0,
            'a_longitude': 0.0,
            'b_latitude': 0.0,
            'b_longitude': 0.0,
        },
        {
            'survey_number': early,
            'stake_spacing': office_spacing,
            'bearing': early,
            'a_latitude': early,
            'a_longitude': early,
            'b_latitude': early,
            'b_longitude': early,
        },
    )

    harness.sync()

    sv_server = harness.server_record(SURVEY, 'sv-north')
    sv_tablet = harness.tablet_record(SURVEY, 'sv-north')

    assert sv_server.data['stake_spacing'] == 60
    assert sv_server.data['a_latitude'] == 49.6942
    assert sv_server.data['a_longitude'] == -112.8134
    assert sv_server.data['b_latitude'] == 49.6950
    assert sv_server.data['b_longitude'] == -112.8100

    assert sv_tablet.data['stake_spacing'] == 60
    assert sv_tablet.data['a_latitude'] == 49.6942

    for i in range(5):
        server_stake = harness.server_record(STAKE, f'st-{i}')
        assert server_stake is not None
        assert server_stake.data['is_driven'] is True
        assert server_stake.data['latitude'] == pytest.approx(49.6942 + (i * 0.001))

    tablet_relocate = harness.ts()

    harness.tablet_save(
        STAKE, 'st-0',
        {
            'id': 'st-0',
            'survey_id': 'sv-north',
            'latitude': 49.700,
            'longitude': -112.800,
            'is_driven': True,
        },
        {
            'survey_id': stake_ts,
            'latitude': tablet_relocate,
            'longitude': tablet_relocate,
            'is_driven': stake_ts,
        },
    )

    office_reference = harness.ts()

    harness.server_save(
        STAKE, 'st-0',
        {
            'id': 'st-0',
            'survey_id': 'sv-north',
            'latitude': 49.6942,
            'longitude': -112.8134,
            'is_driven': True,
            'is_reference': True,
        },
        {
            'survey_id': stake_ts,
            'latitude': stake_ts,
            'longitude': stake_ts,
            'is_driven': stake_ts,
            'is_reference': office_reference,
        },
    )

    harness.sync()

    st0_server = harness.server_record(STAKE, 'st-0')
    st0_tablet = harness.tablet_record(STAKE, 'st-0')

    assert st0_server.data['latitude'] == 49.700
    assert st0_server.data['longitude'] == -112.800
    assert st0_server.data['is_reference'] is True

    assert st0_tablet.data['latitude'] == 49.700
    assert st0_tablet.data['is_reference'] is True
