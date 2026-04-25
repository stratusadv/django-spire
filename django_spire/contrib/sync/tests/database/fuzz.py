from __future__ import annotations

import logging
import random
import time

from typing import Any

from django_spire.contrib.sync.tests.database.harness import ModelSchema
from django_spire.contrib.sync.tests.database.simulator import SyncSimulator


logger = logging.getLogger(__name__)


def parse_seed(raw: str) -> int:
    if len(raw) == 40:
        return int(raw[:16], 16)

    return int(raw)


def run_fuzz(
    seed: int,
    events_max: int = 10_000,
    tablet_count: int | None = None,
    num_fields: int | None = None,
    num_keys: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)

    tablet_count = tablet_count or rng.randint(1, 5)
    num_fields = num_fields or rng.randint(2, 15)
    num_keys = num_keys or rng.randint(2, 20)

    schemas = [
        ModelSchema(
            label='fuzz.Record',
            fields=[f'f_{i}' for i in range(num_fields)],
        ),
    ]

    sim = SyncSimulator(
        tablet_count=tablet_count,
        schemas=schemas,
        num_keys=num_keys,
        seed=seed,
    )

    logger.info(
        'seed=%d tablets=%d fields=%d keys=%d events=%d weights=%s',
        seed, tablet_count, num_fields, num_keys, events_max, sim._weights,
    )

    start = time.monotonic()
    sim.run(events_max)
    sim.assert_converged_with_oracle()
    elapsed = time.monotonic() - start

    logger.info('seed=%d PASSED in %.2fs', seed, elapsed)

    return {
        'seed': seed,
        'elapsed': elapsed,
        'tablet_count': tablet_count,
        'num_fields': num_fields,
        'num_keys': num_keys,
        'events': events_max,
        'weights': dict(sim._weights),
    }
