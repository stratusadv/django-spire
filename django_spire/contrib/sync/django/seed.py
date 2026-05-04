from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from django.db.models import Max

if TYPE_CHECKING:
    from django_spire.contrib.sync.core.clock import HybridLogicalClock
    from django_spire.contrib.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)


def seed_clock(
    clock: HybridLogicalClock,
    models: list[type[SyncableMixin]],
) -> None:
    high_water = 0

    for model in models:
        result = model.objects.aggregate(max_ts=Max('sync_field_last_modified'))
        timestamp = result['max_ts'] or 0

        high_water = max(high_water, timestamp)

    if high_water:
        clock.receive(high_water)
        logger.info('Seeded HLC from database: %d', high_water)
