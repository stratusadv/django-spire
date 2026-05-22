from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django_spire.contrib.sync.file.conflict import ConflictStrategy, SourceWins
from django_spire.contrib.sync.file.exceptions import FileSyncParameterError


@dataclass(frozen=True)
class FileSyncConfig:
    model_label: str
    identity_field: str
    scope_field: str
    filename: str
    fields: tuple[Any, ...]
    conflict_strategy: ConflictStrategy = field(default_factory=SourceWins)
    deactivation_threshold: float | None = None
    timestamp_field: str = 'modified_datetime'

    def __post_init__(self) -> None:
        if not self.model_label:
            message = 'model_label must not be empty'
            raise FileSyncParameterError(message)

        if not self.identity_field:
            message = 'identity_field must not be empty'
            raise FileSyncParameterError(message)

        if not self.scope_field:
            message = 'scope_field must not be empty'
            raise FileSyncParameterError(message)

        if not self.filename:
            message = 'filename must not be empty'
            raise FileSyncParameterError(message)

        if not self.fields:
            message = 'fields must not be empty'
            raise FileSyncParameterError(message)

        if self.deactivation_threshold is not None and self.deactivation_threshold < 0.0:
            message = (
                f'deactivation_threshold must be non-negative '
                f'or None, got {self.deactivation_threshold}'
            )

            raise FileSyncParameterError(message)

    @property
    def field_keys(self) -> tuple[str, ...]:
        return tuple(f.key for f in self.fields)
