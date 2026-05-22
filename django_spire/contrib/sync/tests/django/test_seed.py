from __future__ import annotations

import pytest

from django.db import models as db_models

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.django.seed import seed_clock
from django_spire.contrib.sync.tests.models import SyncTestSimpleModel, SyncTestModel


@pytest.mark.django_db
def test_seed_clock_absorbs_high_water_mark() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance = SyncTestModel(name='Alice', value=10)
    instance.sync_field_timestamps = {'name': 99999}
    instance.sync_field_last_modified = 99999
    db_models.Model.save(instance)

    seed_clock(clock, [SyncTestModel])

    ts = clock.now()

    assert ts > 99999


@pytest.mark.django_db
def test_seed_clock_empty_database_is_noop() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    before = clock.now()

    seed_clock(clock, [SyncTestSimpleModel])

    after = clock.now()

    assert (after >> 16) >= (before >> 16)


@pytest.mark.django_db
def test_seed_clock_picks_max_across_models() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    low = SyncTestSimpleModel(name='Low')
    low.sync_field_timestamps = {'name': 1000}
    low.sync_field_last_modified = 1000
    db_models.Model.save(low)

    high = SyncTestModel(name='High', value=1)
    high.sync_field_timestamps = {'name': 50000}
    high.sync_field_last_modified = 50000
    db_models.Model.save(high)

    seed_clock(clock, [SyncTestModel, SyncTestSimpleModel])

    ts = clock.now()

    assert ts > 50000
