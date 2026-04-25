from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from django_spire.contrib.sync.file.conflict import Resolution


@dataclass
class Change:
    old: dict[str, Any]
    new: dict[str, Any]

    @property
    def diff(self) -> dict[str, tuple[Any, Any]]:
        all_keys = self.old.keys() | self.new.keys()

        return {
            key: (self.old.get(key), self.new.get(key))
            for key in sorted(all_keys)
            if self.old.get(key) != self.new.get(key)
        }


@dataclass
class Error:
    key: str
    message: str
    exception: Exception | None = None


@dataclass
class Result:
    created: list[str] = field(default_factory=list)
    deactivated: list[str] = field(default_factory=list)
    errors: list[Error] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    changes: dict[str, Change] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


@dataclass
class BidirectionalResult:
    source_created: list[str] = field(default_factory=list)
    source_updated: list[str] = field(default_factory=list)
    source_deactivated: list[str] = field(default_factory=list)
    target_created: list[str] = field(default_factory=list)
    target_updated: list[str] = field(default_factory=list)
    target_deactivated: list[str] = field(default_factory=list)
    conflicts: dict[str, Resolution] = field(default_factory=dict)
    unchanged: list[str] = field(default_factory=list)
    changes: dict[str, Change] = field(default_factory=dict)
    errors: list[Error] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0
