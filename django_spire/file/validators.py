from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django_spire.file.exceptions import (
    FileContentError,
    FileExtensionError,
    FileNameError,
    FileSizeError
)
from django_spire.file.utils import parse_extension

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile


_EXECUTABLE_SIGNATURES = (
    b'MZ',
    b'\x7fELF',
    b'\xca\xfe\xba\xbe',
    b'\xfe\xed\xfa\xce',
    b'\xfe\xed\xfa\xcf',
    b'\xcf\xfa\xed\xfe',
    b'\xce\xfa\xed\xfe',
)

_SIGNATURE_READ_SIZE = max(
    len(signature)
    for signature in _EXECUTABLE_SIGNATURES
)


@dataclass
class FileValidator:
    size_bytes_max: int = 10 * 1024 * 1024
    allowed_extensions: frozenset[str] | None = None
    blocked_extensions: frozenset[str] = field(
        default_factory=lambda: frozenset({
            'exe',
            'bat',
            'cmd',
            'com',
            'msi',
            'scr',
            'pif',
            'htm',
            'html',
            'svg',
        })
    )
    content_validation: bool = True

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
        self._validate_filename(file)
        self._validate_size(file)
        self._validate_extension(file)

        if self.content_validation:
            self._validate_content(file)

    def _validate_not_empty(self, file: InMemoryUploadedFile) -> None:
        if not file or not file.name:
            message = 'No file provided.'
            raise FileNameError(message)

    def _validate_filename(self, file: InMemoryUploadedFile) -> None:
        if '\x00' in file.name:
            message = 'Filename contains null bytes.'
            raise FileNameError(message)

    def _validate_size(self, file: InMemoryUploadedFile) -> None:
        if file.size is None:
            message = 'File size is unknown.'
            raise FileSizeError(message)

        if file.size > self.size_bytes_max:
            message = (
                f'File size ({file.size} bytes) exceeds '
                f'maximum ({self.size_bytes_max} bytes).'
            )
            raise FileSizeError(message)

    def _validate_extension(self, file: InMemoryUploadedFile) -> None:
        extension = parse_extension(file.name)

        if not extension:
            message = 'File must have an extension.'
            raise FileExtensionError(message)

        if self.blocked_extensions and extension in self.blocked_extensions:
            message = f'File extension ".{extension}" is not allowed.'
            raise FileExtensionError(message)

        if self.allowed_extensions is not None and extension not in self.allowed_extensions:
            message = f'File extension ".{extension}" is not in the allowed list.'
            raise FileExtensionError(message)

    def _validate_content(self, file: InMemoryUploadedFile) -> None:
        position = file.tell()
        header = file.read(_SIGNATURE_READ_SIZE)
        file.seek(position)

        for signature in _EXECUTABLE_SIGNATURES:
            if header.startswith(signature):
                message = 'File content appears to be an executable binary.'
                raise FileContentError(message)
