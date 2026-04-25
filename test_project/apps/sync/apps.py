from __future__ import annotations

import sys
import warnings

from django.apps import AppConfig
from django.core.management import call_command


class SyncDemoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'test_project_sync'
    name = 'test_project.apps.sync'

    def ready(self) -> None:
        from django.apps import apps  # noqa: PLC0415

        from django_spire.contrib.sync.core.clock import HybridLogicalClock  # noqa: PLC0415
        from django_spire.contrib.sync.django.mixin import SyncableMixin  # noqa: PLC0415
        from django_spire.contrib.sync.django.signals import register_m2m_signals  # noqa: PLC0415

        clock = HybridLogicalClock()
        SyncableMixin.configure(clock=clock)

        syncable_models = [
            model
            for model in apps.get_models()
            if issubclass(model, SyncableMixin) and not model._meta.proxy
        ]

        register_m2m_signals(syncable_models)

        self._migrate_sync_databases()

    @staticmethod
    def _migrate_sync_databases() -> None:
        from test_project.apps.sync.config import get_all_sync_databases  # noqa: PLC0415

        skip_commands = ('makemigrations', 'collectstatic', 'test', 'shell', 'check')

        if any(cmd in sys.argv for cmd in skip_commands):
            return

        with warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                message='Accessing the database during app initialization'
            )

            for db in get_all_sync_databases():
                call_command('migrate', database=db, verbosity=0, interactive=False)
