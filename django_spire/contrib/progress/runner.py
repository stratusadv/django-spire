from __future__ import annotations

import math
import random
import threading
import time

from typing import TYPE_CHECKING

from django_spire.contrib.progress.enums import ProgressStatus
from django_spire.contrib.progress.task import ProgressMessages, Task, TaskResult

if TYPE_CHECKING:
    from typing import Any, Callable

    from django_spire.contrib.progress.tracker import ProgressTracker


class TaskProgressUpdater:
    def __init__(self, tracker: ProgressTracker, task: Task) -> None:
        self._messages = ProgressMessages()
        self._task = task
        self._tracker = tracker

    def complete(self, message: str | None = None) -> None:
        self._tracker._update_task(
            self._task.name,
            ProgressStatus.COMPLETE,
            self._format(message or self._messages.complete),
            100
        )

    def error(self, message: str) -> None:
        self._tracker._update_task(
            self._task.name,
            ProgressStatus.ERROR,
            self._format(message),
            0
        )

    def start(self) -> None:
        self._tracker._update_task(
            self._task.name,
            ProgressStatus.PROCESSING,
            self._format(self._messages.starting),
            2
        )

    def update(self, message: str, progress: int) -> None:
        self._tracker._update_task(
            self._task.name,
            ProgressStatus.PROCESSING,
            self._format(message),
            progress
        )

    def _format(self, message: str) -> str:
        return f'{self._task.label}: {message}'


class ProgressSimulator:
    def __init__(
        self,
        updater: TaskProgressUpdater,
        max_progress: int = 90,
        update_interval: float = 0.15
    ) -> None:
        self._max_progress = max_progress
        self._messages = ProgressMessages()
        self._update_interval = update_interval
        self._updater = updater

    def run(self, stop_event: threading.Event) -> None:
        start_time = time.time()
        duration = random.uniform(8.0, 15.0)

        while not stop_event.is_set():
            elapsed = time.time() - start_time
            t = min(elapsed / duration, 1.0)

            progress = self._ease_out_expo(t) * self._max_progress
            progress = min(int(progress), self._max_progress)

            jitter = random.uniform(-1.5, 1.5) if progress < self._max_progress - 5 else 0
            progress = max(2, min(int(progress + jitter), self._max_progress))

            message = self._get_message_for_progress(progress)
            self._updater.update(message, progress)

            if progress >= self._max_progress:
                break

            time.sleep(self._update_interval + random.uniform(0, 0.1))

    def _ease_out_expo(self, t: float) -> float:
        if t >= 1.0:
            return 1.0

        return 1.0 - math.pow(2, -10 * t)

    def _get_message_for_progress(self, progress: int) -> str:
        steps = self._messages.steps
        index = min(int(progress / (self._max_progress / len(steps))), len(steps) - 1)

        return steps[index]


class TaskRunner:
    def __init__(self, tracker: ProgressTracker, task: Task) -> None:
        self._stop_event = threading.Event()
        self._task = task
        self._tracker = tracker
        self._updater = TaskProgressUpdater(tracker, task)

    def run_parallel(self, results: dict[str, TaskResult]) -> None:
        self._execute(results, lambda: self._task.func())

    def run_sequential(self, results: dict[str, TaskResult]) -> None:
        unwrapped = {name: result.value for name, result in results.items()}
        self._execute(results, lambda: self._task.func(unwrapped))

    def stop(self) -> None:
        self._stop_event.set()

    def _execute(self, results: dict[str, TaskResult], executor: Callable[[], Any]) -> None:
        simulator = ProgressSimulator(self._updater)
        progress_thread = threading.Thread(target=simulator.run, args=(self._stop_event,))
        progress_thread.start()

        try:
            self._updater.start()
            value = executor()
            results[self._task.name] = TaskResult(value=value)
            self._updater.complete()
        except BaseException as e:
            results[self._task.name] = TaskResult(error=e)
            self._updater.error(str(e))
        finally:
            self._stop_event.set()
            progress_thread.join(timeout=1)
