from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from django.db.models import Max

if TYPE_CHECKING:
    from django_spire.sync.core.clock import HybridLogicalClock
    from django_spire.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)


def seed_clock(clock: HybridLogicalClock, models: list[type[SyncableMixin]]) -> None:
    water_high = 0

    for model in models:
        result = model.objects.aggregate(maximum_timestamp=Max('sync_field_last_modified'))
        timestamp = result['maximum_timestamp'] or 0

        water_high = max(water_high, timestamp)

    if water_high:
        clock.receive(water_high)
        logger.info('Seeded HLC from database: %d', water_high)
