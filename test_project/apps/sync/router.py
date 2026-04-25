from __future__ import annotations

from typing import Any, TYPE_CHECKING

from test_project.apps.sync.config import get_all_sync_databases
from test_project.apps.sync.context import _context

if TYPE_CHECKING:
    from django.db import models


class SyncDemoRouter:
    @staticmethod
    def _get_context_db() -> str:
        return getattr(_context, 'db', 'default')

    def allow_migrate(
        self,
        db: str,
        app_label: str,
        **hints: Any,
    ) -> bool | None:
        _ = hints

        if app_label == 'test_project_sync':
            return db in get_all_sync_databases()

        if db in get_all_sync_databases():
            return False

        return None

    def allow_relation(
        self,
        obj1: models.Model,
        obj2: models.Model,
        **hints: Any,
    ) -> bool | None:
        _ = hints

        if (
            obj1._meta.app_label == 'test_project_sync'
            and obj2._meta.app_label == 'test_project_sync'
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
            return self._get_context_db()

        return None

    def db_for_write(
        self,
        model: type[models.Model],
        **hints: Any,
    ) -> str | None:
        _ = hints

        if model._meta.app_label == 'test_project_sync':
            return self._get_context_db()

        return None
