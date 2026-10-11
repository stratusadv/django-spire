import logging
import threading
from typing import Any, Callable

from celery import shared_task, states
from celery.contrib.django.task import DjangoTask
from celery.exceptions import Ignore, Reject, Retry
from pydantic import BaseModel

from django_spire.celery.tracker import CeleryTaskTracker

logger = logging.getLogger(__name__)


class CeleryTaskRunner(DjangoTask):
    """Base class for the actual Celery task: runs the lifecycle, the tracker tracks it.

    Extend by overriding `execute` (class-based) or wrapping a function with
    `celery_task`. The worker writes only the result backend (no web DB); the web
    side owns the `CeleryTask` and syncs it from the backend.
    """

    runner_display_name: str | None = None
    runner_update_interval_seconds: int = 5
    data_model: type[BaseModel] | None = None

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
            return CeleryTaskTracker(self)

        tracker = CeleryTaskTracker(
            self,
            update_interval_seconds=self.runner_update_interval_seconds,
            data_model=self.data_model,
        )

        retries = getattr(self.request, 'retries', 0)
        if retries:
            tracker.meta.retries = retries

        hostname = getattr(self.request, 'hostname', None)
        if hostname:
            tracker.meta.data['worker_hostname'] = hostname

        tracker.set_started()
        self._local.tracker = tracker
        return tracker


def celery_task(
    data_model: type[BaseModel] | None = None,
    display_name: str | None = None,
    update_interval_seconds: int = 5,
    **task_opts: Any,
) -> Any:
    def decorate(fun: Callable) -> Any:
        def run(self: CeleryTaskRunner, *args: Any, **kwargs: Any) -> Any:
            def execute_fn(*execute_args: Any, **execute_kwargs: Any) -> Any:
                return fun(self, *execute_args, **execute_kwargs)

            return self._run_lifecycle(execute_fn, args, kwargs)

        run.__name__ = fun.__name__
        run.__module__ = fun.__module__
        run.__qualname__ = fun.__qualname__
        run.__wrapped__ = fun

        task = shared_task(base=CeleryTaskRunner, bind=True, **task_opts)(run)
        task.data_model = data_model
        task.runner_display_name = display_name
        task.runner_update_interval_seconds = update_interval_seconds
        return task

    return decorate
