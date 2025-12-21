from __future__ import annotations

from enum import StrEnum


class ProgressStatus(StrEnum):
    COMPLETE = 'complete'
    COMPLETING = 'completing'
    ERROR = 'error'
    PENDING = 'pending'
    RUNNING = 'running'
