from __future__ import annotations

import logging
import threading
import time

from typing import TYPE_CHECKING

from django.core.cache import cache

from django_spire.contrib.progress.enums import ProgressStatus
from django_spire.contrib.progress.runner import TaskRunner
from django_spire.contrib.progress.states import TaskState, TrackerState
from django_spire.contrib.progress.task import Task, TaskResult

if TYPE_CHECKING:
    from typing import Any, Callable


log = logging.getLogger(__name__)


class ProgressTracker:
    def __init__(self, key: str, timeout: int = 300) -> None:
        self._key = f'progress_tracker_{key}'
        self._lock = threading.Lock()
        self._tasks: list[Task] = []
        self._timeout = timeout

    def clear(self) -> None:
        cache.delete(self._key)

    def complete(self, message: str = 'Complete!') -> None:
        with self._lock:
            state = self._get_state()
            state.message = message
            state.progress = 100
            state.status = ProgressStatus.COMPLETE
            self._save_state(state)

    def error(self, message: str) -> None:
        with self._lock:
            state = self._get_state()
            state.message = message
            state.progress = 0
            state.status = ProgressStatus.ERROR
            self._save_state(state)

    def execute(self) -> dict[str, Any] | None:
        self._create_state()

        error = False
        results: dict[str, TaskResult] = {}

        try:
            error = self._execute_parallel_tasks(results)

            if not error:
                error = self._execute_sequential_tasks(results)

            if not error:
                self.complete()
                time.sleep(1)
        except BaseException:
            log.exception('Progress tracker failed')
            error = True

        if error:
            self.error('An unexpected error occurred')
            time.sleep(2)

        self.clear()

        if error:
            return None

        return {name: result.value for name, result in results.items()}

    def get(self) -> dict[str, Any] | None:
        return cache.get(self._key)

    def parallel(
        self,
        name: str,
        func: Callable[[], Any],
        label: str | None = None
    ) -> ProgressTracker:
        task = Task(
            func=func,
            label=label or self._generate_label(name),
            name=name,
            parallel=True,
        )

        self._tasks.append(task)

        return self

    def sequential(
        self,
        name: str,
        func: Callable[[dict[str, Any]], Any],
        label: str | None = None
    ) -> ProgressTracker:
        task = Task(
            func=func,
            label=label or self._generate_label(name),
            name=name,
            parallel=False,
        )

        self._tasks.append(task)

        return self

    def start(self) -> None:
        state = TrackerState()
        cache.set(self._key, state.to_dict(), timeout=self._timeout)

    def update(
        self,
        status: ProgressStatus,
        message: str,
        progress: int,
        **kwargs: Any
    ) -> None:
        with self._lock:
            state = self._get_state()
            state.message = message
            state.progress = progress
            state.status = status
            self._save_state(state, **kwargs)

    def _calculate_overall_progress(self, state: TrackerState) -> int:
        if not state.tasks:
            return 0

        total = sum(
            task.progress
            for task in state.tasks.values()
        )

        return int(total / len(state.tasks))

    def _create_state(self) -> None:
        task_names = [task.name for task in self._tasks]

        state = TrackerState(
            task_order=task_names,
            tasks={name: TaskState() for name in task_names}
        )

        cache.set(self._key, state.to_dict(), timeout=self._timeout)

    def _execute_parallel_tasks(self, results: dict[str, TaskResult]) -> bool:
        tasks = [
            task
            for task in self._tasks if task.parallel
        ]

        if not tasks:
            return False

        runners: list[TaskRunner] = []
        threads: list[threading.Thread] = []

        for task in tasks:
            runner = TaskRunner(self, task)
            runners.append(runner)

            thread = threading.Thread(target=runner.run_parallel, args=(results,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(timeout=self._timeout)

            if thread.is_alive():
                for runner in runners:
                    runner.stop()

                return True

        return any(
            results.get(task.name, TaskResult()).failed
            for task in tasks
        )

    def _execute_sequential_tasks(self, results: dict[str, TaskResult]) -> bool:
        tasks = [
            task
            for task in self._tasks
            if not task.parallel
        ]

        for task in tasks:
            runner = TaskRunner(self, task)
            runner.run_sequential(results)

            if results.get(task.name, TaskResult()).failed:
                return True

        return False

    def _generate_label(self, name: str) -> str:
        return name.replace('_', ' ').title()

    def _get_state(self) -> TrackerState:
        task_names = [task.name for task in self._tasks]
        data = cache.get(self._key)

        if data is None:
            return TrackerState(
                task_order=task_names,
                tasks={name: TaskState() for name in task_names}
            )

        return TrackerState.from_dict(data)

    def _save_state(self, state: TrackerState, **kwargs: Any) -> None:
        data = state.to_dict()
        data.update(kwargs)
        cache.set(self._key, data, timeout=self._timeout)

    def _update_task(
        self,
        name: str,
        status: ProgressStatus,
        message: str,
        progress: int
    ) -> None:
        with self._lock:
            state = self._get_state()

            state.tasks[name] = TaskState(
                message=message,
                progress=progress,
                status=status,
            )

            state.message = message
            state.progress = self._calculate_overall_progress(state)
            state.status = ProgressStatus.PROCESSING

            self._save_state(state)
