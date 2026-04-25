from __future__ import annotations

import pytest

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
