from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django_spire.file.exceptions import FileValidationError
from django_spire.file.utils import parse_extension

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile


@dataclass
class FileValidator:
    size_bytes_max: int = 10 * 1024 * 1024
    allowed_extensions: frozenset[str] | None = None
    blocked_extensions: frozenset[str] = field(
        default_factory=lambda: frozenset({
            'exe', 'bat', 'cmd', 'com', 'msi', 'scr', 'pif',
        })
    )

    def __post_init__(self) -> None:
        if self.size_bytes_max <= 0:
            message = 'size_bytes_max must be positive.'
            raise ValueError(message)

        if self.allowed_extensions is not None and self.blocked_extensions:
            overlap = self.allowed_extensions & self.blocked_extensions

            if overlap:
                message = f'Extensions cannot be both allowed and blocked: {overlap}'
                raise ValueError(message)

    def validate(self, file: InMemoryUploadedFile) -> None:
        self._validate_not_empty(file)
        self._validate_size(file)
        self._validate_extension(file)

    def _validate_not_empty(self, file: InMemoryUploadedFile) -> None:
        if not file or not file.name:
            message = 'No file provided.'
            raise FileValidationError(message)

    def _validate_size(self, file: InMemoryUploadedFile) -> None:
        if file.size is not None and file.size > self.size_bytes_max:
            message = (
                f'File size ({file.size} bytes) exceeds '
                f'maximum ({self.size_bytes_max} bytes).'
            )
            raise FileValidationError(message)

    def _validate_extension(self, file: InMemoryUploadedFile) -> None:
        extension = parse_extension(file.name)

        if self.blocked_extensions and extension in self.blocked_extensions:
            message = f'File extension ".{extension}" is not allowed.'
            raise FileValidationError(message)

        if self.allowed_extensions is not None and extension not in self.allowed_extensions:
            message = f'File extension ".{extension}" is not in the allowed list.'
            raise FileValidationError(message)
