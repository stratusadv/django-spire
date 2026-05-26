from __future__ import annotations

import pytest

from django.db import models as db_models

from django_spire.sync.core import UnknownModelError
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.database.storage import CheckpointPosition
from django_spire.contrib.sync.django.graph import DeferredForeignKey
from django_spire.contrib.sync.django.models.checkpoint import SyncCheckpoint
from django_spire.sync.django.storage import DjangoRecordWriter
from django_spire.contrib.sync.tests.models import (
    SyncTestModel,
    SyncTestSimpleModel,
    SyncTestTag,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.sync.django.storage import DjangoSyncStorage


@pytest.mark.django_db
def test_get_syncable_models(storage: DjangoSyncStorage) -> None:
    models = storage.get_syncable_models()

    assert isinstance(models, list)
    assert len(models) == 2
    assert models == sorted(models)


@pytest.mark.django_db
def test_upsert_many_creates_record(storage: DjangoSyncStorage) -> None:
    key = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'

    records = {
        key: SyncRecord(
            key=key,
            data={'id': key, 'name': 'Bob', 'value': 42},
            timestamps={'name': 200, 'value': 200},
        ),
    }

    result = storage.upsert_many('sync_tests.SyncTestModel', records, '')

    assert result.skipped == set()

    obj = SyncTestModel.objects.get(pk=key)

    assert obj.name == 'Bob'
    assert obj.value == 42
    assert obj.sync_field_timestamps == {'name': 200, 'value': 200}
    assert obj.sync_field_last_modified == 200


@pytest.mark.django_db
def test_upsert_many_updates_existing(
    storage: DjangoSyncStorage,
    model_instance: SyncTestModel,
) -> None:
    key = str(model_instance.pk)

    records = {
        key: SyncRecord(
            key=key,
            data={'id': key, 'name': 'Updated', 'value': 99},
            timestamps={'name': 300, 'value': 300},
        ),
    }

    result = storage.upsert_many('sync_tests.SyncTestModel', records, '')

    assert result.skipped == set()

    model_instance.refresh_from_db()

    assert model_instance.name == 'Updated'
    assert model_instance.value == 99
    assert model_instance.sync_field_timestamps == {'name': 300, 'value': 300}


@pytest.mark.django_db
def test_upsert_many_skips_stale_record(
    storage: DjangoSyncStorage,
    model_instance: SyncTestModel,
) -> None:
    key = str(model_instance.pk)

    records = {
        key: SyncRecord(
            key=key,
            data={'id': key, 'name': 'Stale', 'value': 0},
            timestamps={'name': 50, 'value': 50},
        ),
    }

    result = storage.upsert_many('sync_tests.SyncTestModel', records, '')

    assert key in result.skipped

    model_instance.refresh_from_db()

    assert model_instance.name == 'Alice'


@pytest.mark.django_db
def test_upsert_many_rejects_ghost_record(
    storage: DjangoSyncStorage,
) -> None:
    key = 'cccccccc-cccc-cccc-cccc-cccccccccccc'

    records = {
        key: SyncRecord(
            key=key,
            data={'id': key, 'name': 'Ghost', 'value': 0},
            timestamps={},
        ),
    }

    result = storage.upsert_many('sync_tests.SyncTestModel', records, '')

    assert any(e.key == key for e in result.errors)


@pytest.mark.django_db
def test_upsert_many_sets_many_to_many(storage: DjangoSyncStorage) -> None:
    tag = SyncTestTag.objects.create(label='urgent')
    key = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'

    records = {
        key: SyncRecord(
            key=key,
            data={'id': key, 'name': 'WithTags', 'value': 0, 'tags': [str(tag.pk)]},
            timestamps={'name': 200},
        ),
    }

    result = storage.upsert_many('sync_tests.SyncTestModel', records, '')

    assert result.skipped == set()

    obj = SyncTestModel.objects.get(pk=key)

    assert list(obj.tags.values_list('pk', flat=True)) == [tag.pk]


@pytest.mark.django_db
def test_get_records(
    storage: DjangoSyncStorage,
    model_instance: SyncTestModel,
) -> None:
    key = str(model_instance.pk)

    records = storage.get_records('sync_tests.SyncTestModel', {key})

    assert key in records
    assert records[key].data['name'] == 'Alice'
    assert records[key].timestamps == {'name': 100, 'value': 100}


@pytest.mark.django_db
def test_get_records_empty_keys(storage: DjangoSyncStorage) -> None:
    records = storage.get_records('sync_tests.SyncTestModel', set())

    assert records == {}


@pytest.mark.django_db
def test_get_records_missing_key(storage: DjangoSyncStorage) -> None:
    records = storage.get_records(
        'sync_tests.SyncTestModel',
        {'00000000-0000-0000-0000-000000000000'},
    )

    assert records == {}


@pytest.mark.django_db
def test_get_changed_since(
    storage: DjangoSyncStorage,
    model_instance: SyncTestModel,
) -> None:
    _ = model_instance

    records = storage.get_changed_since('sync_tests.SyncTestModel', 0, '')

    assert len(records) == 1

    key = next(iter(records.keys()))

    assert records[key].data['name'] == 'Alice'


@pytest.mark.django_db
def test_get_changed_since_excludes_old(
    storage: DjangoSyncStorage,
    model_instance: SyncTestModel,
) -> None:
    _ = model_instance

    records = storage.get_changed_since('sync_tests.SyncTestModel', 999999, '')

    assert len(records) == 0


@pytest.mark.django_db
def test_delete_many_soft_delete_applies_tombstone(
    storage: DjangoSyncStorage,
    model_instance: SyncTestModel,
) -> None:
    key = str(model_instance.pk)

    storage.delete_many('sync_tests.SyncTestModel', {key: 500}, '')

    model_instance.refresh_from_db()

    assert model_instance.is_deleted is True
    assert model_instance.sync_field_last_modified == 500
    assert model_instance.sync_field_timestamps['is_deleted'] == 500


@pytest.mark.django_db
def test_delete_many_soft_delete_skips_when_local_newer(
    storage: DjangoSyncStorage,
    model_instance: SyncTestModel,
) -> None:
    key = str(model_instance.pk)

    storage.delete_many('sync_tests.SyncTestModel', {key: 50}, '')

    model_instance.refresh_from_db()

    assert model_instance.is_deleted is False


@pytest.mark.django_db
def test_delete_many_hard_delete_applies_tombstone(
    simple_storage: DjangoSyncStorage,
) -> None:
    obj = SyncTestSimpleModel(name='Disposable')
    obj.sync_field_timestamps = {'name': 100}
    obj.sync_field_last_modified = 100
    db_models.Model.save(obj)

    key = str(obj.pk)

    simple_storage.delete_many('sync_tests.SyncTestSimpleModel', {key: 500}, '')

    assert not SyncTestSimpleModel.objects.filter(pk=key).exists()


@pytest.mark.django_db
def test_delete_many_hard_delete_skips_when_local_newer(
    simple_storage: DjangoSyncStorage,
) -> None:
    obj = SyncTestSimpleModel(name='Still-Here')
    obj.sync_field_timestamps = {'name': 1000}
    obj.sync_field_last_modified = 1000
    db_models.Model.save(obj)

    key = str(obj.pk)

    simple_storage.delete_many('sync_tests.SyncTestSimpleModel', {key: 500}, '')

    assert SyncTestSimpleModel.objects.filter(pk=key).exists()


@pytest.mark.django_db
def test_delete_many_empty_is_noop(storage: DjangoSyncStorage) -> None:
    storage.delete_many('sync_tests.SyncTestModel', {}, '')


@pytest.mark.django_db
def test_checkpoint_round_trip(storage: DjangoSyncStorage) -> None:
    assert storage.get_checkpoint('node-1') == CheckpointPosition(
        peer_sequence=0,
        local_sequence_pushed=0,
    )

    storage.save_checkpoint('node-1', 500, 300)

    assert storage.get_checkpoint('node-1') == CheckpointPosition(
        peer_sequence=500,
        local_sequence_pushed=300,
    )


@pytest.mark.django_db
def test_checkpoint_update(storage: DjangoSyncStorage) -> None:
    storage.save_checkpoint('node-1', 100, 50)
    storage.save_checkpoint('node-1', 200, 150)

    assert storage.get_checkpoint('node-1') == CheckpointPosition(
        peer_sequence=200,
        local_sequence_pushed=150,
    )
    assert SyncCheckpoint.objects.filter(peer_node_id='node-1').count() == 1


@pytest.mark.django_db
def test_unknown_model_raises(storage: DjangoSyncStorage) -> None:
    with pytest.raises(UnknownModelError, match='Unknown syncable model'):
        storage.get_records('nonexistent.Model', {'1'})


def test_writer_defers_syncable_target_fk() -> None:
    writer = DjangoRecordWriter(
        models=[SyncTestModel, SyncTestSimpleModel],
        deferred_foreign_keys=[
            DeferredForeignKey(
                source_label='sync_tests.SyncTestModel',
                target_label='sync_tests.SyncTestModel',
                field_name='parent',
                attribute_name='parent_id',
            ),
        ],
    )

    assert 'parent_id' in writer._deferred_attribute_names['sync_tests.SyncTestModel']
    assert 'parent_id' not in writer._external_nullable_attribute_names['sync_tests.SyncTestModel']


def test_writer_treats_non_syncable_target_fk_as_external() -> None:
    writer = DjangoRecordWriter(
        models=[SyncTestModel, SyncTestSimpleModel],
        deferred_foreign_keys=[
            DeferredForeignKey(
                source_label='sync_tests.SyncTestModel',
                target_label='auth.User',
                field_name='owner',
                attribute_name='owner_id',
            ),
        ],
    )

    assert 'owner_id' in writer._external_nullable_attribute_names['sync_tests.SyncTestModel']
    assert 'owner_id' not in writer._deferred_attribute_names['sync_tests.SyncTestModel']


def test_nullify_columns_nulls_external_without_stashing() -> None:
    writer = DjangoRecordWriter(
        models=[SyncTestModel, SyncTestSimpleModel],
        deferred_foreign_keys=[
            DeferredForeignKey(
                source_label='sync_tests.SyncTestModel',
                target_label='auth.User',
                field_name='owner',
                attribute_name='owner_id',
            ),
        ],
    )

    row = {'id': 'x', 'owner_id': 5, 'name': 'Alice'}
    stashed = writer._nullify_deferred_columns('sync_tests.SyncTestModel', row)

    assert row['owner_id'] is None
    assert 'owner_id' not in stashed


def test_nullify_columns_stashes_syncable_deferred() -> None:
    writer = DjangoRecordWriter(
        models=[SyncTestModel, SyncTestSimpleModel],
        deferred_foreign_keys=[
            DeferredForeignKey(
                source_label='sync_tests.SyncTestModel',
                target_label='sync_tests.SyncTestModel',
                field_name='parent',
                attribute_name='parent_id',
            ),
        ],
    )

    row = {'id': 'x', 'parent_id': 'y', 'name': 'Alice'}
    stashed = writer._nullify_deferred_columns('sync_tests.SyncTestModel', row)

    assert row['parent_id'] is None
    assert stashed['parent_id'] == 'y'
