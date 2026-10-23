from typing import Any, Callable

from celery import shared_task

from django_spire.celery.meta import TaskDataModel
from django_spire.celery.runner import CeleryTaskRunner


def celery_task(
    name: str | None = None,
    meta_data_model: type[TaskDataModel] | None = None,
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

        task = shared_task(base=CeleryTaskRunner, bind=True, name=name, **task_opts)(run)
        task.meta_data_model = meta_data_model
        task.runner_update_interval_seconds = update_interval_seconds

        return task

    return decorate
