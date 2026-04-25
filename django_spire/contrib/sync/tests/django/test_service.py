from __future__ import annotations

import pytest

from django_spire.contrib.sync.core.exceptions import InvalidParameterError
from django_spire.contrib.sync.django.service import SyncableModelService
from django_spire.contrib.sync.tests.models import SyncTestModel, SyncTestTag


@pytest.fixture
def instance() -> SyncTestModel:
    return SyncTestModel(name='Alice', value=10)


@pytest.mark.django_db
def test_save_stamps_dirty_fields(instance: SyncTestModel) -> None:
    instance.save()

    assert 'name' in instance.sync_field_timestamps
    assert 'value' in instance.sync_field_timestamps
    assert instance.sync_field_last_modified > 0


@pytest.mark.django_db
def test_save_only_stamps_changed_fields(instance: SyncTestModel) -> None:
    instance.save()

    old_value_ts = instance.sync_field_timestamps.get('value')

    instance.name = 'Bob'
    instance.save()

    assert instance.sync_field_timestamps['value'] == old_value_ts
    assert instance.sync_field_timestamps['name'] >= old_value_ts


@pytest.mark.django_db
def test_save_resets_tracker(instance: SyncTestModel) -> None:
    instance.save()

    assert instance.get_dirty_fields() == set()


@pytest.mark.django_db
def test_save_no_dirty_fields_preserves_timestamps(
    instance: SyncTestModel,
) -> None:
    instance.save()

    ts_before = dict(instance.sync_field_timestamps)
    lm_before = instance.sync_field_last_modified

    instance.save()

    assert instance.sync_field_timestamps == ts_before
    assert instance.sync_field_last_modified == lm_before


@pytest.mark.django_db
def test_set_m2m(instance: SyncTestModel) -> None:
    instance.save()

    tag = SyncTestTag.objects.create(label='urgent')
    SyncableModelService.set_m2m(instance, 'tags', [tag.pk])

    assert 'tags' in instance.sync_field_timestamps
    assert instance.sync_field_timestamps['tags'] > 0
    assert list(instance.tags.values_list('pk', flat=True)) == [tag.pk]


@pytest.mark.django_db
def test_set_m2m_updates_sync_field_last_modified(instance: SyncTestModel) -> None:
    instance.save()

    old_lm = instance.sync_field_last_modified

    tag = SyncTestTag.objects.create(label='v2')
    SyncableModelService.set_m2m(instance, 'tags', [tag.pk])

    assert instance.sync_field_last_modified >= old_lm


@pytest.mark.django_db
def test_set_m2m_before_save_raises(instance: SyncTestModel) -> None:
    with pytest.raises(InvalidParameterError, match='Cannot set M2M field'):
        SyncableModelService.set_m2m(instance, 'tags', [])


@pytest.mark.django_db
def test_set_m2m_persists_to_db(instance: SyncTestModel) -> None:
    instance.save()

    tag = SyncTestTag.objects.create(label='persisted')
    SyncableModelService.set_m2m(instance, 'tags', [tag.pk])

    refreshed = SyncTestModel.objects.get(pk=instance.pk)

    assert 'tags' in refreshed.sync_field_timestamps
    assert refreshed.sync_field_last_modified == instance.sync_field_last_modified
