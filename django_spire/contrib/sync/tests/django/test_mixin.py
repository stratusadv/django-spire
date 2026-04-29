from __future__ import annotations

import pytest

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.core.exceptions import ClockNotConfiguredError
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.tests.models import SyncTestModel


@pytest.fixture
def instance() -> SyncTestModel:
    return SyncTestModel(name='Alice', value=10)


@pytest.mark.django_db
def test_get_syncable_field_names() -> None:
    names = SyncTestModel.get_syncable_field_names()

    assert 'name' in names
    assert 'value' in names
    assert 'id' in names
    assert 'sync_field_timestamps' not in names
    assert 'sync_field_last_modified' not in names
    assert names == sorted(names)


@pytest.mark.django_db
def test_get_syncable_m2m_names() -> None:
    names = SyncTestModel.get_syncable_m2m_names()

    assert 'tags' in names


@pytest.mark.django_db
def test_new_instance_all_fields_dirty(instance: SyncTestModel) -> None:
    dirty = instance.get_dirty_fields()

    assert 'name' in dirty
    assert 'value' in dirty


@pytest.mark.django_db
def test_saved_instance_no_dirty_fields(instance: SyncTestModel) -> None:
    instance.sync_field_timestamps = {'name': 100, 'value': 100}
    instance.sync_field_last_modified = 100
    instance.save()

    assert instance.get_dirty_fields() == set()


@pytest.mark.django_db
def test_mutation_detected_as_dirty(instance: SyncTestModel) -> None:
    instance.sync_field_timestamps = {'name': 100, 'value': 100}
    instance.sync_field_last_modified = 100
    instance.save()

    instance.name = 'Bob'

    dirty = instance.get_dirty_fields()

    assert dirty == {'name'}


@pytest.mark.django_db
def test_refresh_from_db_resets_tracker(instance: SyncTestModel) -> None:
    instance.sync_field_timestamps = {'name': 100, 'value': 100}
    instance.sync_field_last_modified = 100
    instance.save()

    instance.name = 'Bob'

    assert 'name' in instance.get_dirty_fields()

    instance.refresh_from_db()

    assert instance.get_dirty_fields() == set()


def test_configure_sets_clock() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    assert SyncableMixin.get_clock() is clock


def test_get_clock_raises_when_not_configured() -> None:
    SyncableMixin._clock = None

    with pytest.raises(ClockNotConfiguredError, match='not configured'):
        SyncableMixin.get_clock()


def test_get_clock_after_configure() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    result = SyncableMixin.get_clock()

    assert result is clock


def test_get_syncable_field_names_excludes_meta() -> None:
    names = SyncTestModel.get_syncable_field_names()

    assert 'sync_field_timestamps' not in names
    assert 'sync_field_last_modified' not in names


def test_get_syncable_field_names_includes_regular_fields() -> None:
    names = SyncTestModel.get_syncable_field_names()

    assert 'name' in names
    assert 'value' in names


def test_get_syncable_field_names_sorted() -> None:
    names = SyncTestModel.get_syncable_field_names()

    assert names == sorted(names)


@pytest.mark.django_db
def test_save_sets_timestamps(instance: SyncTestModel) -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance.save()

    assert instance.sync_field_timestamps != {}
    assert instance.sync_field_last_modified > 0


@pytest.mark.django_db
def test_save_updates_dirty_field_timestamp() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance = SyncTestModel(name='original', value=1)
    instance.save()

    ts_before = instance.sync_field_timestamps.get('name', 0)

    instance.name = 'changed'
    instance.save()

    ts_after = instance.sync_field_timestamps.get('name', 0)

    assert ts_after > ts_before


@pytest.mark.django_db
def test_save_does_not_update_clean_field_timestamp() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance = SyncTestModel(name='stable', value=1)
    instance.save()

    ts_name = instance.sync_field_timestamps.get('name', 0)

    instance.value = 999
    instance.save()

    assert instance.sync_field_timestamps.get('name', 0) == ts_name


@pytest.mark.django_db
def test_dirty_fields_on_new_instance() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance = SyncTestModel(name='new', value=5)

    dirty = instance.get_dirty_fields()

    assert 'name' in dirty
    assert 'value' in dirty


@pytest.mark.django_db
def test_dirty_fields_after_save_is_empty() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance = SyncTestModel(name='saved', value=5)
    instance.save()

    dirty = instance.get_dirty_fields()

    assert len(dirty) == 0
