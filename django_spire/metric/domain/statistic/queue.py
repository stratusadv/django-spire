from __future__ import annotations

import logging
import queue
import threading
import traceback

from django.db import connections

from django_spire.conf import settings
from django_spire.metric.domain.statistic.services.tracking_service import StatisticTrackingService

logger = logging.getLogger(__name__)

FLUSH_BATCH_SIZE = 100

_WORKER_NAME = 'django-spire-statistic-tracking'


class StatisticTrackingQueue:
    def __init__(self, *, maxsize: int | None = None, start_worker: bool = True) -> None:
        self._queue: queue.Queue[str] = queue.Queue(
            maxsize=maxsize or getattr(settings, 'DJANGO_SPIRE_METRIC_TRACKING_QUEUE_MAXSIZE', 1000)
        )
        self._lock = threading.Lock()
        self._worker: threading.Thread | None = None
        self._start_worker = start_worker

    def enqueue(self, reference: str) -> bool:
        try:
            self._queue.put_nowait(reference)
        except queue.Full:
            logger.warning('Dropped metric tracking reference %r: queue is full', reference)
            return False

        if self._start_worker:
            self._ensure_worker()
        return True

    def flush(self) -> None:
        batch = self._drain_batch()
        while batch:
            StatisticTrackingService.track_many(batch)
            batch = self._drain_batch()

    def _ensure_worker(self) -> None:
        with self._lock:
            if self._worker is not None and self._worker.is_alive():
                return

            self._worker = threading.Thread(target=self._run, daemon=True, name=_WORKER_NAME)
            self._worker.start()

    def _run(self) -> None:
        try:
            while True:
                batch = [self._queue.get()]
                batch.extend(self._drain_batch())
                StatisticTrackingService.track_many(batch)
        except Exception:
            logger.exception('Metric tracking worker crashed with the following exception:')
            exception_string = traceback.format_exc()
            logger.exception(exception_string)
        finally:
            connections.close_all()

    def _drain_batch(self) -> list[str]:
        batch: list[str] = []
        for _ in range(FLUSH_BATCH_SIZE - 1):
            try:
                batch.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return batch


tracking_queue = StatisticTrackingQueue()
