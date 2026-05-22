from __future__ import annotations

from enum import StrEnum


class ResolutionAction(StrEnum):
    USE_SOURCE = 'use_source'
    USE_TARGET = 'use_target'
    SKIP = 'skip'


class SyncAction(StrEnum):
    CREATED = 'created'
    DEACTIVATED = 'deactivated'
    UNCHANGED = 'unchanged'
    UPDATED = 'updated'


class SyncPhase(StrEnum):
    COLLECTING = 'collecting'
    COMMITTING = 'committing'
    COMPLETE = 'complete'
    EXCHANGING = 'exchanging'
    FAILED = 'failed'
    RECONCILING = 'reconciling'


class SyncStage(StrEnum):
    CLASSIFY = 'classify'
    CALLBACK = 'callback'
    MUTATE = 'mutate'
    VALIDATE = 'validate'


class SyncStatus(StrEnum):
    ABANDONED = 'abandoned'
    ERROR = 'error'
    FAILURE = 'failure'
    IN_PROGRESS = 'in_progress'
    PENDING = 'pending'
    SUCCESS = 'success'
