from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django_spire.contrib.progress.enums import ProgressStatus

if TYPE_CHECKING:
    from typing import Any


@dataclass
class TaskState:
    message: str = 'Waiting...'
    progress: int = 0
    status: ProgressStatus = ProgressStatus.PENDING

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskState:
        return cls(
            message=data.get('message', 'Waiting...'),
            progress=data.get('progress', 0),
            status=ProgressStatus(data.get('step', ProgressStatus.PENDING)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'message': self.message,
            'progress': self.progress,
            'step': self.status.value,
        }


@dataclass
class TrackerState:
    message: str = 'Initializing...'
    progress: int = 0
    status: ProgressStatus = ProgressStatus.PENDING
    task_order: list[str] = field(default_factory=list)
    tasks: dict[str, TaskState] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrackerState:
        tasks = {
            name: TaskState.from_dict(task_data)
            for name, task_data in data.get('tasks', {}).items()
        }

        return cls(
            message=data.get('message', 'Initializing...'),
            progress=data.get('progress', 0),
            status=ProgressStatus(data.get('step', ProgressStatus.PENDING)),
            task_order=data.get('task_order', []),
            tasks=tasks,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'message': self.message,
            'progress': self.progress,
            'step': self.status.value,
            'task_order': self.task_order,
            'tasks': {name: task.to_dict() for name, task in self.tasks.items()},
        }
