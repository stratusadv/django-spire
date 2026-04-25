from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, TYPE_CHECKING

from django_spire.contrib.sync.core.enums import ResolutionAction

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class Conflict:
    key: str
    source_record: dict[str, Any] | None
    target_record: dict[str, Any] | None
    baseline_record: dict[str, Any] | None = None
    source_timestamp: datetime | None = None
    target_timestamp: datetime | None = None


@dataclass
class Resolution:
    action: ResolutionAction
    record: dict[str, Any] | None


class ConflictStrategy(Protocol):
    def resolve(self, conflict: Conflict) -> Resolution: ...


class SourceWins:
    def resolve(self, conflict: Conflict) -> Resolution:
        return Resolution(
            action=ResolutionAction.USE_SOURCE,
            record=conflict.source_record,
        )


class TargetWins:
    def resolve(self, conflict: Conflict) -> Resolution:
        return Resolution(
            action=ResolutionAction.USE_TARGET,
            record=conflict.target_record,
        )


class LastWriteWins:
    def resolve(self, conflict: Conflict) -> Resolution:
        if conflict.source_timestamp is None and conflict.target_timestamp is None:
            message = (
                f'Cannot resolve conflict for key {conflict.key!r}: '
                f'no timestamps available on either side'
            )
            raise ValueError(message)

        if conflict.source_timestamp is None:
            return Resolution(
                action=ResolutionAction.USE_TARGET,
                record=conflict.target_record,
            )

        if conflict.target_timestamp is None:
            return Resolution(
                action=ResolutionAction.USE_SOURCE,
                record=conflict.source_record,
            )

        if conflict.source_timestamp >= conflict.target_timestamp:
            return Resolution(
                action=ResolutionAction.USE_SOURCE,
                record=conflict.source_record,
            )

        return Resolution(
            action=ResolutionAction.USE_TARGET,
            record=conflict.target_record,
        )
