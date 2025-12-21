from __future__ import annotations

import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable

    from django_spire.contrib.progress.session import ProgressSession


class ParallelTask:
    def __init__(self, session: ProgressSession, task_id: str, future: Any) -> None:
        self._future = future
        self._session = session
        self._task_id = task_id

        self._session.start(task_id)

        thread = threading.Thread(
            target=self._wait_for_completion,
            daemon=True,
        )
        thread.start()

    def _wait_for_completion(self) -> None:
        try:
            _ = self._future.result
            self._session.complete(self._task_id)
        except Exception:
            self._session.error(self._task_id)

    @property
    def result(self) -> Any:
        return self._future.result


class SequentialTask:
    def __init__(
        self,
        session: ProgressSession,
        task_id: str,
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._exception: Exception | None = None
        self._result: Any = None
        self._session = session
        self._task_id = task_id

        self._session.start(task_id)

        try:
            self._result = func(*args, **kwargs)
            self._session.complete(task_id)
        except Exception as e:
            self._exception = e
            self._session.error(task_id)

    @property
    def result(self) -> Any:
        if self._exception is not None:
            raise self._exception

        return self._result
