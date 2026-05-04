from __future__ import annotations

import pytest

from django.db import models as db_models

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.django.queryset import _is_bypassed, sync_bypass
from django_spire.contrib.sync.tests.models import SyncTestSimpleModel, SyncTestModel


@pytest.mark.django_db
def test_bulk_create_stamps_timestamps() -> None:

    a = SyncTestSimpleModel(name='Alpha')
    b = SyncTestSimpleModel(name='Beta')

    SyncTestSimpleModel.objects.bulk_create([a, b])

    assert a.sync_field_last_modified > 0
    assert b.sync_field_last_modified > 0
    assert 'name' in a.sync_field_timestamps
    assert 'name' in b.sync_field_timestamps


@pytest.mark.django_db
def test_bulk_create_does_not_overwrite_existing_timestamps() -> None:
    instance = SyncTestSimpleModel(name='Pre-stamped')
    instance.sync_field_timestamps = {'name': 42}
    instance.sync_field_last_modified = 42

    SyncTestSimpleModel.objects.bulk_create([instance])

    assert instance.sync_field_timestamps['name'] == 42


@pytest.mark.django_db
def test_bulk_create_bypass_skips_stamping() -> None:
    instance = SyncTestSimpleModel(name='Bypassed')

    with sync_bypass():
        SyncTestSimpleModel.objects.bulk_create([instance])

    assert instance.sync_field_last_modified == 0
    assert instance.sync_field_timestamps == {}


@pytest.mark.django_db
def test_bulk_update_stamps_dirty_fields() -> None:
    instance = SyncTestSimpleModel(name='Original')
    instance.sync_field_timestamps = {'name': 100}
    instance.sync_field_last_modified = 100
    db_models.Model.save(instance)

    instance.name = 'Changed'

    SyncTestSimpleModel.objects.bulk_update([instance], ['name'])

    assert instance.sync_field_timestamps['name'] > 100
    assert instance.sync_field_last_modified > 100


@pytest.mark.django_db
def test_bulk_update_bypass_skips_stamping() -> None:
    instance = SyncTestSimpleModel(name='Original')
    instance.sync_field_timestamps = {'name': 100}
    instance.sync_field_last_modified = 100
    db_models.Model.save(instance)

    instance.name = 'Changed'

    with sync_bypass():
        SyncTestSimpleModel.objects.bulk_update([instance], ['name'])

    assert instance.sync_field_timestamps['name'] == 100
    assert instance.sync_field_last_modified == 100


@pytest.mark.django_db
def test_bulk_update_adds_meta_to_fields() -> None:
    instance = SyncTestSimpleModel(name='Original')
    instance.sync_field_timestamps = {'name': 100}
    instance.sync_field_last_modified = 100
    db_models.Model.save(instance)

    instance.name = 'Changed'

    SyncTestSimpleModel.objects.bulk_update([instance], ['name'])

    instance.refresh_from_db()

    assert instance.name == 'Changed'
    assert instance.sync_field_timestamps['name'] > 100
    assert instance.sync_field_last_modified > 100


@pytest.mark.django_db
def test_bulk_update_ignores_non_syncable_fields() -> None:
    instance = SyncTestModel(name='Alice', value=10)
    instance.sync_field_timestamps = {'name': 100, 'value': 100}
    instance.sync_field_last_modified = 100
    db_models.Model.save(instance)

    old_name_ts = instance.sync_field_timestamps['name']

    instance.value = 20

    SyncTestModel.objects.bulk_update([instance], ['value'])

    assert instance.sync_field_timestamps['name'] == old_name_ts
    assert instance.sync_field_timestamps['value'] > 100


@pytest.mark.django_db
def test_sync_bypass_restores_on_exception() -> None:
    assert not _is_bypassed()

    try:
        with sync_bypass():
            assert _is_bypassed()

            message = 'boom'
            raise RuntimeError(message)  # noqa: TRY301
    except RuntimeError:
        pass

    assert not _is_bypassed()


@pytest.mark.django_db
def test_bulk_create_each_instance_gets_unique_timestamp() -> None:
    instances = [SyncTestSimpleModel(name=f'Item-{i}') for i in range(5)]

    SyncTestSimpleModel.objects.bulk_create(instances)

    timestamps = [inst.sync_field_last_modified for inst in instances]

    assert len(set(timestamps)) == 5
    assert timestamps == sorted(timestamps)


def test_is_bypassed_false_by_default() -> None:
    assert _is_bypassed() is False


def test_sync_bypass_sets_flag() -> None:
    with sync_bypass():
        assert _is_bypassed() is True

    assert _is_bypassed() is False


def test_sync_bypass_restores_previous_state() -> None:
    assert _is_bypassed() is False

    with sync_bypass():
        assert _is_bypassed() is True

        with sync_bypass():
            assert _is_bypassed() is True

        assert _is_bypassed() is True

    assert _is_bypassed() is False


@pytest.mark.django_db
def test_save_with_bypass_skips_timestamp_update() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance = SyncTestModel(name='bypassed', value=1)

    with sync_bypass():
        instance.save()

    assert instance.sync_field_timestamps == {}
    assert instance.sync_field_last_modified == 0


@pytest.mark.django_db
def test_save_without_bypass_sets_timestamps() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instance = SyncTestModel(name='normal', value=1)
    instance.save()

    assert instance.sync_field_timestamps != {}
    assert instance.sync_field_last_modified > 0


@pytest.mark.django_db
def test_bulk_create_sets_timestamps() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instances = [
        SyncTestModel(name=f'bulk-{i}', value=i)
        for i in range(3)
    ]

    created = SyncTestModel.objects.bulk_create(instances)

    for obj in created:
        assert obj.sync_field_timestamps != {}
        assert obj.sync_field_last_modified > 0


@pytest.mark.django_db
def test_bulk_create_with_bypass_skips_timestamps() -> None:
    clock = HybridLogicalClock()
    SyncableMixin.configure(clock)

    instances = [
        SyncTestModel(name=f'bypass-bulk-{i}', value=i)
        for i in range(3)
    ]

    with sync_bypass():
        created = SyncTestModel.objects.bulk_create(instances)

    for obj in created:
        assert obj.sync_field_timestamps == {}
