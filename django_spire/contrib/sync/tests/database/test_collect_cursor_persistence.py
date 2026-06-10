from __future__ import annotations

from contextlib import nullcontext

from django_spire.contrib.sync.core.clock import HybridLogicalClock
from django_spire.contrib.sync.database.conflict import FieldTimestampWins
from django_spire.contrib.sync.database.engine import DatabaseEngine
from django_spire.contrib.sync.database.graph import DependencyGraph
from django_spire.contrib.sync.database.reconciler import PayloadReconciler
from django_spire.contrib.sync.tests.database.helpers import (
    ALL_MODELS,
    DirectTransport,
    InMemoryDatabaseStorage,
    STAKE,
    SURVEY,
    SURVEY_DEPS,
)


def _make_engine(
    storage: InMemoryDatabaseStorage,
    node_id: str,
    clock: HybridLogicalClock,
    transport: DirectTransport | None = None,
    batch_size: int | None = None,
) -> DatabaseEngine:
    return DatabaseEngine(
        batch_size=batch_size,
        clock=clock,
        clock_drift_max=None,
        graph=DependencyGraph(SURVEY_DEPS),
        node_id=node_id,
        peer_node_id='server' if transport is not None else None,
        reconciler=PayloadReconciler(resolver=FieldTimestampWins()),
        storage=storage,
        transaction=nullcontext,
        transport=transport,
    )


class TestCollectCursorPersistence:
    def test_low_sequence_child_survives_truncated_first_batch(self) -> None:
        clock = HybridLogicalClock()

        server_storage = InMemoryDatabaseStorage(ALL_MODELS)
        server_engine = _make_engine(server_storage, 'server', clock)

        tablet_storage = InMemoryDatabaseStorage(ALL_MODELS)
        tablet_engine = _make_engine(
            tablet_storage,
            'tablet',
            clock,
            transport=DirectTransport(server_engine),
            batch_size=3,
        )

        now = clock.now()

        tablet_storage.seed(
            STAKE,
            'stake-low',
            {'id': 'stake-low', 'x': 1},
            {'x': now},
        )

        for index in range(5):
            tablet_storage.seed(
                SURVEY,
                f'survey-{index}',
                {'id': f'survey-{index}', 'name': f'n{index}'},
                {'name': now},
            )

        tablet_engine.sync()

        surveys = server_storage._records[SURVEY]
        stakes = server_storage._records[STAKE]

        assert len(surveys) == 5

        assert 'stake-low' in stakes, (
            'stake-low (sequence 1) was skipped: the first batch filled with '
            'surveys whose max sequence exceeds it, the push high-water mark '
            'jumped past it, and its collect cursor was discarded'
        )
