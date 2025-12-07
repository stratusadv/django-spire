from __future__ import annotations

from enum import StrEnum


class ProgressStatus(StrEnum):
    COMPLETE = 'complete'
    ERROR = 'error'
    PENDING = 'pending'
    PROCESSING = 'processing'
