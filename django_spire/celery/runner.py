import logging
import threading
from typing import Any, Callable

from celery import states
from celery.contrib.django.task import DjangoTask
from celery.exceptions import Ignore, Reject, Retry

from django_spire.celery.meta import TaskDataModel
from django_spire.celery.tracker import CeleryTaskTracker

logger = logging.getLogger(__name__)


class CeleryTaskRunner(DjangoTask):
    """Base class for the actual Celery task: runs the lifecycle, the tracker tracks it.

    Extend by overriding `execute` (class-based) or wrapping a function with
    `celery_task`. The worker writes only the result backend (no web DB); the web
    side owns the `CeleryTask` and syncs it from the backend.
    """

    runner_update_interval_seconds: int = 5
    meta_data_model: type[TaskDataModel] | None = None

    # threads pool shares one task instance across worker threads
    _local = threading.local()

    @property
    def tracker(self) -> CeleryTaskTracker | None:
        return getattr(self._local, 'tracker', None)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        return self._run_lifecycle(self.execute, args, kwargs)

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    # ================= LIFECYCLE =================
    def _run_lifecycle(self, execute_fn: Callable[..., Any], args: tuple, kwargs: dict) -> Any:
        tracker = self._start_execution()

        try:
            result = execute_fn(*args, **kwargs)
        except (Reject, Ignore):
            raise
        except Retry:
            tracker.set_retries(self.request.retries + 1)
            tracker.finish(states.RETRY)
            raise
        except Exception as exc:
            tracker.finish(states.FAILURE, exc=exc)
            raise

        tracker.finish(states.SUCCESS)
        return result

    def _start_execution(self) -> CeleryTaskTracker:
        if not self.request.id or self.request.called_directly:
            return CeleryTaskTracker(self, meta_data_model=self.meta_data_model)

        tracker = CeleryTaskTracker(
            self,
            update_interval_seconds=self.runner_update_interval_seconds,
            meta_data_model=self.meta_data_model,
        )

        retries = getattr(self.request, 'retries', 0)
        if retries:
            tracker.meta.retries = retries

        hostname = getattr(self.request, 'hostname', None)
        if hostname:
            if isinstance(tracker.meta.data, TaskDataModel):
                tracker.meta.data.worker_hostname = hostname
            else:
                tracker.meta.data['worker_hostname'] = hostname

        tracker.set_started()
        self._local.tracker = tracker
        return tracker
