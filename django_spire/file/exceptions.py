from __future__ import annotations


class FileError(Exception):
    """Base exception for all file module operations."""


class FileValidationError(FileError):
    """Raised when a file fails one or more validation checks."""


class FileNameError(FileValidationError):
    """Raised when a filename is missing, empty, or contains invalid bytes."""


class FileSizeError(FileValidationError):
    """Raised when a file exceeds the maximum allowed size or has unknown size."""


class FileExtensionError(FileValidationError):
    """Raised when a file has a blocked or disallowed extension."""


class FileContentError(FileValidationError):
    """Raised when file content matches a blocked binary signature."""


class FileBatchLimitError(FileError):
    """Raised when a batch operation exceeds the maximum allowed file count."""


class FileIDError(FileError):
    """Raised when a file ID is not a valid integer."""


class FileLinkError(FileError):
    """Raised when a file cannot be linked or unlinked from a model instance."""
