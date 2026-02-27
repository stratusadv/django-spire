from dataclasses import dataclass
from datetime import date
from django_spire.contrib.changelog.enums import ChangeLogTypeEnum


@dataclass
class Change:
    app: str
    description: str


@dataclass
class ChangelogEntry:
    version: str
    changes: list[Change]
    date: date
    type: ChangeLogTypeEnum
