from __future__ import annotations


class SyncError(Exception):
    pass


class SyncAbortedError(SyncError):
    pass


class ClockDriftError(SyncAbortedError):
    pass


class ClockNotConfiguredError(SyncError):
    pass


class ClockOverflowError(SyncError):
    pass


class ConflictStateError(SyncError):
    pass


class CircularDependencyError(SyncError):
    pass


class DecompressionLimitError(SyncError):
    pass


class InvalidParameterError(SyncError):
    pass


class InvalidResponseError(SyncAbortedError):
    pass


class LockContentionError(SyncAbortedError):
    pass


class ManifestChecksumError(SyncAbortedError):
    pass


class ManifestFieldError(SyncError):
    pass


class PayloadLimitError(SyncAbortedError):
    pass


class BatchLimitError(SyncError):
    pass


class RecordFieldError(SyncError):
    pass


class RecordSerializationError(SyncError):
    pass


class RetryExhaustedError(SyncAbortedError):
    pass


class TransportRequiredError(SyncError):
    pass


class UnknownDependencyError(SyncError):
    pass


class UnknownModelError(SyncError):
    pass
