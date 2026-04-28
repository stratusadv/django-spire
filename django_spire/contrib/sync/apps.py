from __future__ import annotations

import contextlib
import logging

from typing import TYPE_CHECKING

from django.apps import AppConfig

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


log = logging.getLogger(__name__)


class SyncableAppMixin:
    def get_m2m_models(self) -> list[type[SyncableMixin]]:
        return []

    def get_syncable_models(self) -> list[type[SyncableMixin]]:
        message = f'{type(self).__name__} must implement get_syncable_models()'
        raise NotImplementedError(message)

    def ready(self) -> None:
        super().ready()

        from django_spire.contrib.sync import HybridLogicalClock  # noqa: PLC0415
        from django_spire.contrib.sync.django import (  # noqa: PLC0415
            SyncableMixin,
            build_graph,
            register_m2m_signals,
            seed_clock,
        )

        syncable_models = self.get_syncable_models()

        clock = HybridLogicalClock()
        SyncableMixin.configure(clock)

        build_graph(syncable_models)

        with contextlib.suppress(Exception):
            seed_clock(clock, syncable_models)

        m2m_models = self.get_m2m_models()

        if m2m_models:
            register_m2m_signals(m2m_models)


class SyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'sync'
    name = 'django_spire.contrib.sync'
