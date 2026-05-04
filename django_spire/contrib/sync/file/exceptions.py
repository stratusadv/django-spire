from __future__ import annotations


class FileSyncError(Exception):
    """Base exception for all file sync operations."""


class FileSyncAbortedError(FileSyncError):
    """Sync aborted due to a safety threshold violation."""


class FileSyncArchiveError(FileSyncError):
    """Archive extraction or path validation failed."""


class FileSyncConfigError(FileSyncError):
    """Sync service mixin is missing required configuration."""


class FileSyncConflictError(FileSyncError):
    """Conflict could not be resolved with available data."""


class FileSyncParameterError(FileSyncError):
    """Constructor or function received an invalid argument."""


class FileSyncParseError(FileSyncError):
    """Source file record failed validation or type casting."""


class FileSyncSourceNotFoundError(FileSyncError):
    """Source file required for sync does not exist."""
