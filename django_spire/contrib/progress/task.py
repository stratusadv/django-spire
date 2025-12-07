from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable


@dataclass
class ProgressMessages:
    complete: str = 'Complete'
    error: str = 'Error'
    starting: str = 'Starting...'
    steps: list[str] = field(default_factory=lambda: [
        'Initializing...',
        'Processing...',
        'Analyzing...',
        'Working...',
        'Almost there...',
        'Finalizing...',
    ])


@dataclass
class Task:
    func: Callable
    label: str
    name: str
    parallel: bool = False


@dataclass
class TaskResult:
    error: BaseException | None = None
    value: Any = None

    @property
    def failed(self) -> bool:
        return self.error is not None
