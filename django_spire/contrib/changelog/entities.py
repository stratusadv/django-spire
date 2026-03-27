from dataclasses import dataclass
from datetime import date
from django_spire.contrib.changelog.choices import ChangeLogTypeChoices


@dataclass
class Change:
    app: str
    description: str


@dataclass
class ChangelogEntry:
    version: str
    changes: list[Change]
    date: date
    type: ChangeLogTypeChoices
