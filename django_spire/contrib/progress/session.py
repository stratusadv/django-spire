from __future__ import annotations

import json
import threading
import time
import uuid

from typing import TYPE_CHECKING

from django.core.cache import cache

from django_spire.contrib.progress.enums import ProgressStatus
from django_spire.contrib.progress.tasks import ParallelTask, SequentialTask

if TYPE_CHECKING:
    from typing import Any, Callable, Generator


SIMULATION_MESSAGES = [
    'Initializing...',
    'Processing...',
    'Analyzing...',
    'Generating...',
    'Finalizing...',
]


class ProgressSession:
    _CACHE_PREFIX = 'progress_session:'
    _CACHE_TIMEOUT = 300
    _COMPLETION_INCREMENT = 3.0
    _COMPLETION_INTERVAL = 0.03
    _MAX_SIMULATED_PERCENT = 85
    _SIMULATION_INTERVAL = 0.15

    def __init__(self, session_id: str, tasks: dict[str, str]) -> None:
        self._lock = threading.Lock()
        self._simulation_threads: dict[str, tuple[threading.Event, threading.Thread]] = {}

        self._tasks: dict[str, dict[str, Any]] = {
            task_id: {
                'complete_message': '',
                'message': 'Waiting...',
                'name': name,
                'percent': 0.0,
                'status': ProgressStatus.PENDING,
            }
            for task_id, name in tasks.items()
        }

        self.session_id = session_id

    def _calculate_increment(self, current_percent: float) -> float:
        remaining = self._MAX_SIMULATED_PERCENT - current_percent
        ratio = remaining / self._MAX_SIMULATED_PERCENT
        eased = ratio * ratio * ratio
        increment = 0.5 * eased

        return max(increment, 0.03)

    def _calculate_message_index(self, percent: float) -> int:
        message_index = int((percent / 100) * len(SIMULATION_MESSAGES))

        return min(message_index, len(SIMULATION_MESSAGES) - 1)

    def _delete(self) -> None:
        cache.delete(f'{self._CACHE_PREFIX}{self.session_id}')

    def _save(self) -> None:
        data = {
            'session_id': self.session_id,
            'tasks': {
                task_id: {
                    'complete_message': task['complete_message'],
                    'message': task['message'],
                    'name': task['name'],
                    'percent': task['percent'],
                    'status': task['status'].value,
                }
                for task_id, task in self._tasks.items()
            },
        }

        cache.set(f'{self._CACHE_PREFIX}{self.session_id}', data, timeout=self._CACHE_TIMEOUT)

    def _simulate_progress(
        self,
        task_id: str,
        stop_event: threading.Event,
    ) -> None:
        while not stop_event.is_set():
            with self._lock:
                if task_id not in self._tasks:
                    continue

                task = self._tasks[task_id]

                if task['status'] == ProgressStatus.RUNNING:
                    self._tick_running(task)

                if task['status'] == ProgressStatus.COMPLETING:
                    if self._tick_completing(task):
                        return

            interval = self._COMPLETION_INTERVAL if task['status'] == ProgressStatus.COMPLETING else self._SIMULATION_INTERVAL
            stop_event.wait(interval)

    def _tick_completing(self, task: dict[str, Any]) -> bool:
        if task['percent'] < 100.0:
            task['percent'] = min(task['percent'] + self._COMPLETION_INCREMENT, 100.0)
            self._save()
            return False

        task['status'] = ProgressStatus.COMPLETE
        task['message'] = task['complete_message']
        self._save()

        return True

    def _tick_running(self, task: dict[str, Any]) -> None:
        if task['percent'] >= self._MAX_SIMULATED_PERCENT:
            return

        increment = self._calculate_increment(task['percent'])
        task['percent'] = min(task['percent'] + increment, self._MAX_SIMULATED_PERCENT)
        task['message'] = SIMULATION_MESSAGES[self._calculate_message_index(task['percent'])]

        self._save()

    @property
    def has_error(self) -> bool:
        tasks = [
            task['status'] == ProgressStatus.ERROR
            for task in self._tasks.values()
        ]

        return any(tasks)

    @property
    def is_complete(self) -> bool:
        tasks = [
            task['status'] == ProgressStatus.COMPLETE
            for task in self._tasks.values()
        ]

        return all(tasks)

    @property
    def is_running(self) -> bool:
        tasks = [
            task['status'] in (ProgressStatus.RUNNING, ProgressStatus.COMPLETING)
            for task in self._tasks.values()
        ]

        return any(tasks)

    @property
    def overall_percent(self) -> int:
        if not self._tasks:
            return 0

        total_percent = sum(task['percent'] for task in self._tasks.values())

        return int(total_percent / len(self._tasks))

    @property
    def status(self) -> ProgressStatus:
        if self.has_error:
            return ProgressStatus.ERROR

        if self.is_complete:
            return ProgressStatus.COMPLETE

        if self.is_running:
            return ProgressStatus.RUNNING

        return ProgressStatus.PENDING

    def add_parallel(self, task_id: str, future: Any) -> ParallelTask:
        return ParallelTask(self, task_id, future)

    def add_sequential(self, task_id: str, func: Callable, *args: Any, **kwargs: Any) -> SequentialTask:
        return SequentialTask(self, task_id, func, *args, **kwargs)

    def complete(self, task_id: str, message: str | None = None) -> None:
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task['status'] = ProgressStatus.COMPLETING
                task['complete_message'] = message or f'{task["name"]} complete'
                task['message'] = 'Completing...'
                self._save()

    def error(self, task_id: str, message: str | None = None) -> None:
        if task_id in self._simulation_threads:
            stop_event, _ = self._simulation_threads[task_id]
            stop_event.set()
            del self._simulation_threads[task_id]

        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task['status'] = ProgressStatus.ERROR
                task['message'] = message or f'{task["name"]} failed'
                self._save()

    def start(self, task_id: str) -> None:
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task['percent'] = 0.0
                task['status'] = ProgressStatus.RUNNING
                task['message'] = SIMULATION_MESSAGES[0]
                self._save()

        stop_event = threading.Event()

        thread = threading.Thread(
            target=self._simulate_progress,
            args=(task_id, stop_event),
            daemon=True,
        )

        self._simulation_threads[task_id] = (stop_event, thread)
        thread.start()

    def stream(self, poll_interval: float = 0.1) -> Generator[str, None, None]:
        with self._lock:
            data = self.to_dict()

        yield f'{json.dumps(data)}\n'

        while True:
            time.sleep(poll_interval)

            with self._lock:
                data = self.to_dict()

            yield f'{json.dumps(data)}\n'

            if self.is_complete or self.has_error:
                self._delete()
                break

    def to_dict(self) -> dict[str, Any]:
        return {
            'overall_percent': self.overall_percent,
            'session_id': self.session_id,
            'status': self.status.value,
            'tasks': {
                task_id: {
                    'message': task['message'],
                    'name': task['name'],
                    'percent': int(task['percent']),
                    'status': task['status'].value if task['status'] != ProgressStatus.COMPLETING else ProgressStatus.RUNNING.value,
                }
                for task_id, task in self._tasks.items()
            },
        }

    @classmethod
    def create(cls, tasks: dict[str, str]) -> ProgressSession:
        session_id = str(uuid.uuid4())
        session = cls(session_id, tasks)
        session._save()
        return session

    @classmethod
    def get(cls, session_id: str) -> ProgressSession | None:
        data = cache.get(f'{cls._CACHE_PREFIX}{session_id}')

        if data is None:
            return None

        session = cls(data['session_id'], {})

        session._tasks = {
            task_id: {
                'complete_message': task['complete_message'],
                'message': task['message'],
                'name': task['name'],
                'percent': task['percent'],
                'status': ProgressStatus(task['status']),
            }
            for task_id, task in data['tasks'].items()
        }

        return session
