from __future__ import annotations

import pytest

from django.apps import apps
from django.db import connection

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.django.mixin import SyncableMixin
from django_spire.contrib.sync.django.models.checkpoint import SyncCheckpoint
from django_spire.contrib.sync.django.models.lock import SyncNodeLock
from django_spire.contrib.sync.django.models.session import SyncSession
from django_spire.contrib.sync.tests.models import (
    SyncTestModel,
    SyncTestSimpleModel,
    SyncTestTag,
)


def pytest_runtest_setup(item: pytest.Item) -> None:
    if 'postgres_only' in item.keywords and connection.vendor == 'sqlite':
        pytest.skip('requires Postgres; SQLite does not support concurrent writers')


@pytest.fixture(autouse=True)
def _reset_clock() -> None:
    SyncableMixin.configure(HybridLogicalClock())


@pytest.fixture(autouse=True, scope='session')
def _create_test_tables(django_db_setup: None, django_db_blocker: object) -> None:
    _ = django_db_setup

    apps.clear_cache()

    all_models = [
        SyncTestTag,
        SyncTestSimpleModel,
        SyncTestModel,
        SyncCheckpoint,
        SyncNodeLock,
        SyncSession,
    ]

    with django_db_blocker.unblock():
        existing = set(connection.introspection.table_names())

        for model in all_models:
            if model._meta.db_table not in existing:
                with connection.schema_editor() as editor:
                    editor.create_model(model)
