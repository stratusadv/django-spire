from __future__ import annotations


class SyncError(Exception):
    """Base exception for all sync operations."""


class SyncAbortedError(SyncError):
    """Sync aborted due to a recoverable failure."""


class ClockDriftError(SyncAbortedError):
    """Remote node clock exceeds the allowed drift threshold."""


class ClockNotConfiguredError(SyncError):
    """SyncableMixin clock was not configured at startup."""


class ClockOverflowError(SyncError):
    """HLC counter overflowed or monotonicity was violated."""


class ConflictStateError(SyncError):
    """Conflict resolver received an invalid or incomplete conflict."""


class CircularDependencyError(SyncError):
    """Dependency graph contains a cycle."""


class DecompressionLimitError(SyncError):
    """Decompressed data exceeds the allowed size limit."""


class InvalidParameterError(SyncError):
    """Constructor or function received an invalid argument."""


class InvalidResponseError(SyncAbortedError):
    """Remote node returned a malformed or oversized response."""


class LockContentionError(SyncAbortedError):
    """Another sync session is already running for this node."""


class ManifestChecksumError(SyncAbortedError):
    """Manifest checksum verification failed."""


class ManifestFieldError(SyncError):
    """Manifest contains missing or invalid fields."""


class PayloadLimitError(SyncAbortedError):
    """Collected payload exceeds the configured size or record limit."""


class BatchLimitError(SyncError):
    """Batch size exceeds the configured maximum."""


class RecordFieldError(SyncError):
    """Record contains missing or invalid fields."""


class RecordSerializationError(SyncError):
    """Record contains a value that cannot be serialized to JSON."""


class RetryExhaustedError(SyncAbortedError):
    """Retry helper exhausted all configured attempts."""


class TransportRequiredError(SyncError):
    """Engine requires a transport for client-side sync."""


class UnknownDependencyError(SyncError):
    """Model declares a dependency on an unregistered model."""


class UnknownModelError(SyncError):
    """Model label does not match any registered syncable model."""
