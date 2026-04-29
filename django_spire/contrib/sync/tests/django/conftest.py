from __future__ import annotations

import pytest

from django.db import models as db_models

from django_spire.contrib.sync.django.storage import DjangoSyncStorage
from django_spire.contrib.sync.tests.models import SyncTestModel, SyncTestSimpleModel


@pytest.fixture
def storage() -> DjangoSyncStorage:
    return DjangoSyncStorage(
        models=[SyncTestModel, SyncTestSimpleModel],
        identity_field='id',
    )


@pytest.fixture
def simple_storage() -> DjangoSyncStorage:
    return DjangoSyncStorage(
        models=[SyncTestSimpleModel],
        identity_field='id',
    )


@pytest.fixture
def model_instance() -> SyncTestModel:
    instance = SyncTestModel(name='Alice', value=10)
    instance.sync_field_timestamps = {'name': 100, 'value': 100}
    instance.sync_field_last_modified = 100
    db_models.Model.save(instance)
    instance._tracker.snapshot(instance._get_field_values())

    return instance
