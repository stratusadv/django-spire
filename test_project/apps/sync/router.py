from __future__ import annotations

from typing import Any, TYPE_CHECKING

from test_project.apps.sync.config import get_all_sync_databases
from test_project.apps.sync.context import _context

if TYPE_CHECKING:
    from django.db import models


class SyncDemoRouter:
    @staticmethod
    def _get_context_database() -> str:
        return getattr(_context, 'database_name', 'default')

    def allow_migrate(
        self,
        database: str,
        app_label: str,
        **hints: Any,
    ) -> bool | None:
        _ = hints

        if app_label == 'test_project_sync':
            return database in get_all_sync_databases()

        if database in get_all_sync_databases():
            return False

        return None

    def allow_relation(
        self,
        object_one: models.Model,
        object_two: models.Model,
        **hints: Any,
    ) -> bool | None:
        _ = hints

        if (
            object_one._meta.app_label == 'test_project_sync'
            and object_two._meta.app_label == 'test_project_sync'
        ):
            return True

        return None

    def db_for_read(
        self,
        model: type[models.Model],
        **hints: Any,
    ) -> str | None:
        _ = hints

        if model._meta.app_label == 'test_project_sync':
            return self._get_context_database()

        return None

    def db_for_write(
        self,
        model: type[models.Model],
        **hints: Any,
    ) -> str | None:
        _ = hints

        if model._meta.app_label == 'test_project_sync':
            return self._get_context_database()

        return None
